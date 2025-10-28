"""
build_features.py - Feature Engineering para Detecção de Anomalias
Fraud Detection Project - Fase 3

Este módulo contém funções para criar features que capturam mudanças de comportamento.
Essas features transformam dados brutos em sinais detectáveis de anomalia.

FILOSOFIA:
- Anomalias são DESVIOS DE PADRÃO, não valores absolutos
- Features devem comparar transação atual com histórico do usuário
- Quanto mais contextual a feature, mais poderosa

Features Implementadas:
1. tempo_desde_ultima_tx_usuario (s)
2. media_gasto_7d_usuario (R$)
3. std_gasto_7d_usuario (R$)
4. distancia_tx_home_location (km)
5. tx_fora_horario_comum (0/1)
6. velocidade_entre_txs (km/h) - DETECTA TELEPORTE!
7. desvio_valor_do_padrao (z-score)
8. hora_do_dia (0-23)
9. dia_da_semana (0-6)
10. is_weekend (0/1)
"""

import pandas as pd
import numpy as np
from typing import Tuple
from datetime import timedelta
from geopy.distance import geodesic


def calculate_time_since_last_transaction(df: pd.DataFrame) -> pd.Series:
    """
    Calcula o tempo (em segundos) desde a última transação do mesmo usuário.
    
    DETECTA: Sondagem de cartão (múltiplas transações em segundos)
    
    Args:
        df: DataFrame com colunas 'user_id' e 'timestamp'
    
    Returns:
        Series com tempo em segundos (NaN para primeira transação do usuário)
    """
    # Garantir que timestamp seja datetime
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Ordenar por usuário e timestamp
    df = df.sort_values(['user_id', 'timestamp'])
    
    # Calcular diferença de tempo dentro de cada usuário
    df['prev_timestamp'] = df.groupby('user_id')['timestamp'].shift(1)
    df['time_since_last_tx'] = (df['timestamp'] - df['prev_timestamp']).dt.total_seconds()
    
    # Primeira transação de cada usuário = NaN (substituir por valor alto, ex: 1 dia)
    df['time_since_last_tx'] = df['time_since_last_tx'].fillna(86400)  # 24h em segundos
    
    return df['time_since_last_tx']


def calculate_user_spending_stats(df: pd.DataFrame, window_days: int = 7) -> Tuple[pd.Series, pd.Series]:
    """
    Calcula média e desvio padrão de gasto do usuário nos últimos N dias.
    
    DETECTA: Gasto súbito (valor muito acima da média do usuário)
    
    Args:
        df: DataFrame com colunas 'user_id', 'timestamp', 'amount'
        window_days: Janela de tempo em dias (padrão: 7)
    
    Returns:
        Tuple (média, desvio_padrão) de gasto do usuário
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(['user_id', 'timestamp'])
    
    # Calcular média móvel por usuário (janela de tempo)
    df['user_avg_amount_7d'] = df.groupby('user_id')['amount'].transform(
        lambda x: x.rolling(window=window_days, min_periods=1).mean()
    )
    
    # Calcular desvio padrão móvel
    df['user_std_amount_7d'] = df.groupby('user_id')['amount'].transform(
        lambda x: x.rolling(window=window_days, min_periods=1).std()
    )
    
    # Preencher NaN com média geral
    df['user_avg_amount_7d'] = df['user_avg_amount_7d'].fillna(df['amount'].mean())
    df['user_std_amount_7d'] = df['user_std_amount_7d'].fillna(df['amount'].std())
    
    return df['user_avg_amount_7d'], df['user_std_amount_7d']


def calculate_distance_from_home(df: pd.DataFrame) -> pd.Series:
    """
    Calcula distância (em km) entre localização da transação e localização "home" do usuário.
    
    DETECTA: Teleporte geográfico (transação longe de casa)
    
    LÓGICA:
    - "Home" = localização da primeira transação do usuário (assumimos que é casa)
    - Usa fórmula de Haversine para distância entre coordenadas
    
    Args:
        df: DataFrame com colunas 'user_id', 'latitude', 'longitude'
    
    Returns:
        Series com distância em km
    """
    df = df.copy()
    
    # Definir localização "home" como primeira transação do usuário
    home_locations = df.groupby('user_id').first()[['latitude', 'longitude']]
    home_locations.columns = ['home_lat', 'home_lon']
    
    # Merge de volta no dataframe
    df = df.merge(home_locations, left_on='user_id', right_index=True, how='left')
    
    # Calcular distância usando Haversine
    def haversine_distance(row):
        if pd.isna(row['home_lat']) or pd.isna(row['latitude']):
            return 0
        
        try:
            home = (row['home_lat'], row['home_lon'])
            current = (row['latitude'], row['longitude'])
            return geodesic(home, current).kilometers
        except:
            return 0
    
    df['distance_from_home_km'] = df.apply(haversine_distance, axis=1)
    
    return df['distance_from_home_km']


def calculate_velocity_between_transactions(df: pd.DataFrame) -> pd.Series:
    """
    Calcula velocidade (em km/h) necessária para viajar entre duas transações consecutivas.
    
    DETECTA: Teleporte (velocidade humanamente impossível, ex: 5000 km/h)
    
    LÓGICA:
    - Velocidade = Distância / Tempo
    - Se velocidade > 800 km/h (velocidade de avião), é suspeito
    
    Args:
        df: DataFrame com colunas 'user_id', 'latitude', 'longitude', 'timestamp'
    
    Returns:
        Series com velocidade em km/h
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(['user_id', 'timestamp'])
    
    # Calcular coordenadas da transação anterior
    df['prev_lat'] = df.groupby('user_id')['latitude'].shift(1)
    df['prev_lon'] = df.groupby('user_id')['longitude'].shift(1)
    df['prev_timestamp'] = df.groupby('user_id')['timestamp'].shift(1)
    
    # Calcular distância entre transações
    def distance_between_txs(row):
        if pd.isna(row['prev_lat']):
            return 0
        
        try:
            prev = (row['prev_lat'], row['prev_lon'])
            current = (row['latitude'], row['longitude'])
            return geodesic(prev, current).kilometers
        except:
            return 0
    
    df['distance_between_txs'] = df.apply(distance_between_txs, axis=1)
    
    # Calcular tempo entre transações (em horas)
    df['time_between_txs_hours'] = (df['timestamp'] - df['prev_timestamp']).dt.total_seconds() / 3600
    
    # Calcular velocidade (evitar divisão por zero)
    df['velocity_kmh'] = np.where(
        df['time_between_txs_hours'] > 0,
        df['distance_between_txs'] / df['time_between_txs_hours'],
        0
    )
    
    # Limitar velocidades irrealistas (max: velocidade do som ~1200 km/h)
    df['velocity_kmh'] = df['velocity_kmh'].clip(upper=10000)
    
    # Primeira transação de cada usuário = 0
    df['velocity_kmh'] = df['velocity_kmh'].fillna(0)
    
    return df['velocity_kmh']


def calculate_unusual_hour_flag(df: pd.DataFrame) -> pd.Series:
    """
    Flag (0/1) indicando se transação ocorreu fora do horário comum (madrugada).
    
    DETECTA: Horário atípico (transações às 2-4 AM)
    
    Args:
        df: DataFrame com coluna 'timestamp'
    
    Returns:
        Series binária (1 = fora do horário, 0 = horário normal)
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Extrair hora
    df['hour'] = df['timestamp'].dt.hour
    
    # Horário atípico: 0h-5h (madrugada)
    df['is_unusual_hour'] = ((df['hour'] >= 0) & (df['hour'] < 5)).astype(int)
    
    return df['is_unusual_hour']


def calculate_spending_deviation(df: pd.DataFrame, user_avg: pd.Series, user_std: pd.Series) -> pd.Series:
    """
    Calcula z-score do valor da transação em relação ao padrão do usuário.
    
    DETECTA: Gasto súbito (valor muito fora do padrão)
    
    Z-score > 3 = muito acima da média (suspeito!)
    
    Args:
        df: DataFrame com coluna 'amount'
        user_avg: Média de gasto do usuário
        user_std: Desvio padrão de gasto do usuário
    
    Returns:
        Series com z-score
    """
    # Evitar divisão por zero
    user_std_safe = user_std.replace(0, 1)
    
    z_score = (df['amount'] - user_avg) / user_std_safe
    
    return z_score


def extract_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extrai features temporais: hora, dia da semana, fim de semana.
    
    Args:
        df: DataFrame com coluna 'timestamp'
    
    Returns:
        DataFrame com 3 novas colunas
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    df['hour_of_day'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    return df[['hour_of_day', 'day_of_week', 'is_weekend']]


def build_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica TODAS as transformações de features no dataset.
    
    Esta é a função principal que será usada em:
    - EDA (Fase 3)
    - Treino do modelo (Fase 4)
    - API de produção (Fase 5)
    
    Args:
        df: DataFrame bruto com transações
    
    Returns:
        DataFrame com features adicionadas
    """
    print("🔧 Iniciando Feature Engineering...")
    
    df = df.copy()
    
    # 1. Tempo desde última transação
    print("  - Calculando tempo desde última transação...")
    df['time_since_last_tx_sec'] = calculate_time_since_last_transaction(df)
    
    # 2. Estatísticas de gasto do usuário
    print("  - Calculando média e desvio padrão de gasto...")
    df['user_avg_amount_7d'], df['user_std_amount_7d'] = calculate_user_spending_stats(df)
    
    # 3. Distância de casa
    print("  - Calculando distância da localização home...")
    df['distance_from_home_km'] = calculate_distance_from_home(df)
    
    # 4. Velocidade entre transações
    print("  - Calculando velocidade entre transações...")
    df['velocity_kmh'] = calculate_velocity_between_transactions(df)
    
    # 5. Flag de horário atípico
    print("  - Detectando horários atípicos...")
    df['is_unusual_hour'] = calculate_unusual_hour_flag(df)
    
    # 6. Desvio de gasto (z-score)
    print("  - Calculando desvio de gasto...")
    df['spending_zscore'] = calculate_spending_deviation(
        df, 
        df['user_avg_amount_7d'], 
        df['user_std_amount_7d']
    )
    
    # 7. Features temporais
    print("  - Extraindo features temporais...")
    temporal_features = extract_temporal_features(df)
    df = pd.concat([df, temporal_features], axis=1)
    
    print("✓ Feature Engineering concluído!")
    print(f"  - Total de features criadas: 10")
    
    return df


def get_feature_columns() -> list:
    """
    Retorna lista de colunas de features para treino do modelo.
    
    IMPORTANTE: NÃO incluir colunas que podem vazar informação:
    - transaction_id (identificador único, sem valor preditivo)
    - user_id (identificador único, sem valor preditivo)
    - timestamp (usar apenas features derivadas: hour_of_day, day_of_week)
    - merchant_name (muitos valores únicos, usar merchant_category)
    - is_fraud (target!)
    - fraud_type (target!)
    - fraud_difficulty (target!)
    
    Esta lista será usada para:
    - Treinar o Isolation Forest
    - Fazer predições na API
    
    Returns:
        Lista de nomes de colunas
    """
    return [
        'amount',
        'time_since_last_tx_sec',
        'user_avg_amount_7d',
        'user_std_amount_7d',
        'distance_from_home_km',
        'velocity_kmh',
        'is_unusual_hour',
        'spending_zscore',
        'hour_of_day',
        'day_of_week',
        'is_weekend'
    ]


# ==============================================================================
# SCRIPT DE TESTE (Se executar este arquivo diretamente)
# ==============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("TESTE DE FEATURE ENGINEERING")
    print("=" * 80)
    
    # Carregar dados
    print("\n📂 Carregando dados...")
    df = pd.read_csv('../../data/raw/transactions_with_fraud.csv')
    print(f"  ✓ {len(df):,} transações carregadas")
    
    # Aplicar features
    df_features = build_all_features(df)
    
    # Salvar dataset com features
    output_path = '../../data/processed/transactions_with_features.csv'
    df_features.to_csv(output_path, index=False)
    print(f"\n💾 Dataset com features salvo em: {output_path}")
    
    # Mostrar amostra de fraudes
    print("\n🔍 Amostra de fraudes com features:")
    frauds = df_features[df_features['is_fraud'] == 1].head(5)
    feature_cols = get_feature_columns()
    print(frauds[['transaction_id', 'fraud_type', 'fraud_difficulty'] + feature_cols])
    
    print("\n" + "=" * 80)
    print("✓ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 80)