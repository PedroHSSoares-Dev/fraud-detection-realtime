"""
build_features.py - Feature Engineering para Detecção de Anomalias
Fraud Detection Project - Fase 3

Este módulo contém funções para criar features que capturam mudanças de comportamento.
Essas features transformam dados brutos em sinais detectáveis de anomalia.

FILOSOFIA:
- Anomalias são DESVIOS DE PADRÃO, não valores absolutos
- Features devem comparar transação atual com histórico do usuário
- Quanto mais contextual a feature, mais poderosa
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
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(['user_id', 'timestamp'])
    
    df['prev_timestamp'] = df.groupby('user_id')['timestamp'].shift(1)
    df['time_since_last_tx'] = (df['timestamp'] - df['prev_timestamp']).dt.total_seconds()
    df['time_since_last_tx'] = df['time_since_last_tx'].fillna(86400)
    
    return df['time_since_last_tx']


def calculate_user_spending_stats(df: pd.DataFrame, window_days: int = 7) -> Tuple[pd.Series, pd.Series]:
    """
    Calcula média e desvio padrão de gasto do usuário nos últimos N dias.
    DETECTA: Gasto súbito (valor muito acima da média do usuário)
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(['user_id', 'timestamp'])
    
    df['user_avg_amount_7d'] = df.groupby('user_id')['amount'].transform(
        lambda x: x.rolling(window=window_days, min_periods=1).mean()
    )
    
    df['user_std_amount_7d'] = df.groupby('user_id')['amount'].transform(
        lambda x: x.rolling(window=window_days, min_periods=1).std()
    )
    
    df['user_avg_amount_7d'] = df['user_avg_amount_7d'].fillna(df['amount'].mean())
    df['user_std_amount_7d'] = df['user_std_amount_7d'].fillna(df['amount'].std())
    
    return df['user_avg_amount_7d'], df['user_std_amount_7d']


def calculate_distance_from_home(df: pd.DataFrame) -> pd.Series:
    """
    Calcula distância (em km) entre localização da transação e localização "home" do usuário.
    DETECTA: Teleporte geográfico (transação longe de casa)
    """
    df = df.copy()
    
    home_locations = df.groupby('user_id').first()[['latitude', 'longitude']]
    home_locations.columns = ['home_lat', 'home_lon']
    
    df = df.merge(home_locations, left_on='user_id', right_index=True, how='left')
    
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
    DETECTA: Teleporte (velocidade humanamente impossível)
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(['user_id', 'timestamp'])
    
    df['prev_lat'] = df.groupby('user_id')['latitude'].shift(1)
    df['prev_lon'] = df.groupby('user_id')['longitude'].shift(1)
    df['prev_timestamp'] = df.groupby('user_id')['timestamp'].shift(1)
    
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
    
    df['time_between_txs_hours'] = (df['timestamp'] - df['prev_timestamp']).dt.total_seconds() / 3600
    
    df['velocity_kmh'] = np.where(
        df['time_between_txs_hours'] > 0,
        df['distance_between_txs'] / df['time_between_txs_hours'],
        0
    )
    
    df['velocity_kmh'] = df['velocity_kmh'].clip(upper=10000)
    df['velocity_kmh'] = df['velocity_kmh'].fillna(0)
    
    return df['velocity_kmh']


def calculate_unusual_hour_flag(df: pd.DataFrame) -> pd.Series:
    """
    Flag (0/1) indicando se transação ocorreu fora do horário comum (madrugada).
    DETECTA: Horário atípico (transações às 2-4 AM)
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    df['hour'] = df['timestamp'].dt.hour
    df['is_unusual_hour'] = ((df['hour'] >= 0) & (df['hour'] < 5)).astype(int)
    
    return df['is_unusual_hour']


def calculate_rapid_sequence_flag(df: pd.DataFrame, threshold_seconds: int = 60) -> pd.Series:
    """
    Flag (0/1) indicando se transação ocorreu muito rápido após a anterior.
    DETECTA: Sondagem de cartão (múltiplas transações em segundos)
    """
    rapid_sequence = (df['time_since_last_tx_sec'] < threshold_seconds).astype(int)
    return rapid_sequence


def calculate_tx_count_rolling_window(df: pd.DataFrame, window_minutes: int = 60) -> pd.Series:
    """
    Conta quantas transações o usuário fez na última N minutos.
    DETECTA: Card testing (múltiplas transações em janela curta)
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(['user_id', 'timestamp'])
    
    def count_recent_txs(group):
        timestamps = group['timestamp']
        counts = []
        
        for idx, current_time in enumerate(timestamps):
            time_threshold = current_time - timedelta(minutes=window_minutes)
            recent_txs = timestamps[(timestamps < current_time) & (timestamps >= time_threshold)]
            counts.append(len(recent_txs))
        
        return pd.Series(counts, index=group.index)
    
    tx_counts = df.groupby('user_id').apply(count_recent_txs, include_groups=False)
    
    if isinstance(tx_counts.index, pd.MultiIndex):
        tx_counts = tx_counts.droplevel(0)
    
    return tx_counts


def calculate_distinct_merchants_rolling_window(df: pd.DataFrame, window_minutes: int = 60) -> pd.Series:
    """
    Conta quantas lojas diferentes o usuário usou na última N minutos.
    DETECTA: Card testing (fraudador testa em múltiplas lojas)
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(['user_id', 'timestamp'])
    
    def count_distinct_merchants(group):
        timestamps = group['timestamp']
        merchants = group['merchant_name']
        counts = []
        
        for idx, current_time in enumerate(timestamps):
            time_threshold = current_time - timedelta(minutes=window_minutes)
            recent_mask = (timestamps < current_time) & (timestamps >= time_threshold)
            recent_merchants = merchants[recent_mask]
            counts.append(recent_merchants.nunique())
        
        return pd.Series(counts, index=group.index)
    
    distinct_counts = df.groupby('user_id').apply(count_distinct_merchants, include_groups=False)
    
    if isinstance(distinct_counts.index, pd.MultiIndex):
        distinct_counts = distinct_counts.droplevel(0)
    
    return distinct_counts


def calculate_new_merchant_category_flag(df: pd.DataFrame) -> pd.Series:
    """
    Flag (0/1) indicando se esta é a primeira vez que o usuário usa esta categoria de merchant.
    DETECTA: Padrão de compra incomum
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(['user_id', 'timestamp'])
    
    def check_new_category(group):
        categories = group['merchant_category']
        flags = []
        seen_categories = set()
        
        for category in categories:
            if category not in seen_categories:
                flags.append(1)
                seen_categories.add(category)
            else:
                flags.append(0)
        
        return pd.Series(flags, index=group.index)
    
    new_category_flags = df.groupby('user_id').apply(check_new_category, include_groups=False)
    
    if isinstance(new_category_flags.index, pd.MultiIndex):
        new_category_flags = new_category_flags.droplevel(0)
    
    return new_category_flags


def calculate_value_anomaly_flag(df: pd.DataFrame) -> pd.Series:
    """
    Flag (0/1) indicando se valor é anômalo (muito baixo ou muito alto).
    DETECTA: Card testing (valores baixos) e gasto súbito (valores altos)
    """
    is_micro = df['amount'] < 30
    is_huge = df['amount'] > (df['user_avg_amount_7d'] * 3)
    value_anomaly = (is_micro | is_huge).astype(int)
    
    return value_anomaly


def calculate_combined_anomaly_score(df: pd.DataFrame) -> pd.Series:
    """
    Score combinado de anomalia (0-15) baseado em múltiplos sinais.
    DETECTA: Fraudes sutis com múltiplos sinais fracos
    """
    score = pd.Series(0, index=df.index)
    
    score += (df['velocity_kmh'] > 100).astype(int) * 3
    score += (df['distance_from_home_km'] > 1000).astype(int) * 2
    score += (df['spending_zscore'] > 2).astype(int) * 2
    score += (df['is_unusual_hour'] == 1).astype(int) * 1
    score += (df['time_since_last_tx_sec'] < 60).astype(int) * 2
    
    if 'tx_count_rolling_1h_user' in df.columns:
        score += (df['tx_count_rolling_1h_user'] > 3).astype(int) * 3
    
    if 'distinct_merchants_rolling_1h_user' in df.columns:
        score += (df['distinct_merchants_rolling_1h_user'] > 1).astype(int) * 2
    
    return score


def calculate_spending_deviation(df: pd.DataFrame, user_avg: pd.Series, user_std: pd.Series) -> pd.Series:
    """
    Calcula z-score do valor da transação em relação ao padrão do usuário.
    DETECTA: Gasto súbito (valor muito fora do padrão)
    """
    user_std_safe = user_std.replace(0, 1)
    z_score = (df['amount'] - user_avg) / user_std_safe
    
    return z_score


def extract_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extrai features temporais: hora, dia da semana, fim de semana.
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    df['hour_of_day'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    return df[['hour_of_day', 'day_of_week', 'is_weekend']]


def build_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica todas as transformações de features no dataset.
    
    Esta função será usada em:
    - EDA (Fase 3)
    - Treino do modelo (Fase 4)
    - API de produção (Fase 5)
    """
    print("\n" + "="*70)
    print("INICIANDO FEATURE ENGINEERING")
    print("="*70)
    
    df = df.copy()
    
    print("\nCalculando features básicas...")
    df['time_since_last_tx_sec'] = calculate_time_since_last_transaction(df)
    df['user_avg_amount_7d'], df['user_std_amount_7d'] = calculate_user_spending_stats(df)
    df['distance_from_home_km'] = calculate_distance_from_home(df)
    df['velocity_kmh'] = calculate_velocity_between_transactions(df)
    df['is_unusual_hour'] = calculate_unusual_hour_flag(df)
    df['spending_zscore'] = calculate_spending_deviation(df, df['user_avg_amount_7d'], df['user_std_amount_7d'])
    
    temporal_features = extract_temporal_features(df)
    df = pd.concat([df, temporal_features], axis=1)
    
    print("Calculando features avançadas...")
    df['tx_count_rolling_1h_user'] = calculate_tx_count_rolling_window(df, window_minutes=60)
    df['distinct_merchants_rolling_1h_user'] = calculate_distinct_merchants_rolling_window(df, window_minutes=60)
    df['is_new_merchant_category_user'] = calculate_new_merchant_category_flag(df)
    df['rapid_sequence_flag'] = calculate_rapid_sequence_flag(df)
    df['value_anomaly_flag'] = calculate_value_anomaly_flag(df)
    df['combined_anomaly_score'] = calculate_combined_anomaly_score(df)
    
    print(f"\nFeature engineering concluído: 16 features criadas")
    print("="*70)
    
    return df


def get_feature_columns() -> list:
    """
    Retorna lista de colunas de features para treino do modelo.
    
    IMPORTANTE: Não incluir colunas que podem vazar informação:
    - transaction_id, user_id, timestamp, merchant_name
    - is_fraud, fraud_type, fraud_difficulty (targets)
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
        'is_weekend',
        'tx_count_rolling_1h_user',
        'distinct_merchants_rolling_1h_user',
        'is_new_merchant_category_user',
        'rapid_sequence_flag',
        'value_anomaly_flag',
        'combined_anomaly_score'
    ]


if __name__ == '__main__':
    print("="*80)
    print("TESTE DE FEATURE ENGINEERING")
    print("="*80)
    
    print("\nCarregando dados...")
    df = pd.read_csv('../../data/raw/transactions_with_fraud.csv')
    print(f"Transações carregadas: {len(df):,}")
    
    df_features = build_all_features(df)
    
    output_path = '../../data/processed/transactions_with_features.csv'
    df_features.to_csv(output_path, index=False)
    print(f"\nDataset salvo em: {output_path}")
    
    print("\nAmostra de fraudes:")
    frauds = df_features[df_features['is_fraud'] == 1].head(5)
    feature_cols = get_feature_columns()
    print(frauds[['transaction_id', 'fraud_type', 'fraud_difficulty'] + feature_cols[:5]])
    
    print("\n" + "="*80)
    print("TESTE CONCLUÍDO")
    print("="*80)