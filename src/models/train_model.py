"""
train_model.py - Treino do Isolation Forest para Detecção de Fraude
Fraud Detection Project - Fase 4

Este script treina um modelo de detecção de anomalias (Isolation Forest)
de forma NÃO SUPERVISIONADA, ou seja, sem usar o gabarito is_fraud.

FILOSOFIA:
- Isolation Forest aprende padrões "normais" e detecta desvios
- Não precisa de labels (is_fraud) durante o treino
- Ideal para fraudes novas que nunca vimos antes

ESTRATÉGIA:
- Usar apenas transações NORMAIS para treino (para aprender o "normal")
- Testar em transações mistas (normal + fraude)
- Avaliar quantas fraudes o modelo consegue detectar
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os
import sys

# Adicionar path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.build_features import get_feature_columns


def load_processed_data():
    """Carrega dataset com features já criadas."""
    print("=" * 80)
    print("TREINO DO ISOLATION FOREST - FRAUD DETECTION")
    print("=" * 80)
    
    print("\n📂 Carregando dados processados...")
    
    # Tentar diferentes caminhos
    possible_paths = [
        '../data/processed/transactions_with_features.csv',
        'data/processed/transactions_with_features.csv',
        '../../data/processed/transactions_with_features.csv'
    ]
    
    df = None
    for path in possible_paths:
        if os.path.exists(path):
            print(f"  ✓ Arquivo encontrado: {path}")
            df = pd.read_csv(path)
            break
    
    if df is None:
        print("\n❌ ERRO: Arquivo de features não encontrado!")
        print("Execute 'python eda_fraud_analysis.py' primeiro!")
        sys.exit(1)
    
    print(f"  ✓ {len(df):,} transações carregadas")
    print(f"  ✓ Fraudes: {df['is_fraud'].sum():,} ({df['is_fraud'].mean()*100:.2f}%)")
    
    return df


def prepare_train_test_split(df, test_size=200_000, random_state=42):
    """
    Divide dados em treino e teste de forma estratificada.
    
    ESTRATÉGIA:
    - Treino: 100k transações (majoritariamente normais)
    - Teste: 200k transações (com todas as fraudes para avaliação robusta)
    
    Args:
        df: DataFrame completo
        test_size: Tamanho do conjunto de teste
        random_state: Seed para reprodutibilidade
    
    Returns:
        Tuple (X_train, X_test, y_train, y_test, test_metadata)
    """
    print("\n🔀 Dividindo dados em treino e teste...")
    
    # Separar features e target
    feature_cols = get_feature_columns()
    
    X = df[feature_cols].copy()
    y = df['is_fraud'].copy()
    
    # Metadata para análise posterior (tipo de fraude, dificuldade)
    metadata_cols = ['transaction_id', 'user_id', 'fraud_type', 'fraud_difficulty', 'amount', 'timestamp']
    metadata = df[metadata_cols].copy()
    
    # Split estratificado (manter proporção de fraudes)
    train_size = len(df) - test_size
    
    X_train, X_test, y_train, y_test, meta_train, meta_test = train_test_split(
        X, y, metadata,
        test_size=test_size,
        random_state=random_state,
        stratify=y  # Importante: manter proporção de fraudes
    )
    
    print(f"  ✓ Treino: {len(X_train):,} transações ({y_train.sum()} fraudes)")
    print(f"  ✓ Teste: {len(X_test):,} transações ({y_test.sum()} fraudes)")
    
    return X_train, X_test, y_train, y_test, meta_test


def train_isolation_forest(X_train, contamination=0.01):
    """
    Treina o Isolation Forest.
    
    HIPERPARÂMETROS:
    - contamination: Proporção esperada de anomalias (0.01 = 1%)
      NOTA: Com as novas features (rapid_sequence, value_anomaly, combined_score),
      esperamos recall muito maior mesmo com contamination=1%
    - n_estimators: Número de árvores (100 é suficiente)
    - max_samples: Amostras por árvore ('auto' = min(256, n_samples))
    - random_state: Seed para reprodutibilidade
    
    Args:
        X_train: Features de treino
        contamination: Proporção esperada de fraudes
    
    Returns:
        Modelo treinado
    """
    print(f"\n🤖 Treinando Isolation Forest...")
    print(f"  - Contamination: {contamination} ({contamination*100:.2f}%)")
    print(f"  - N estimators: 100")
    print(f"  - Max samples: auto")
    print(f"  - Features: 13 (incluindo 3 novas!)")
    
    # Normalizar features (importante para Isolation Forest)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Treinar modelo
    model = IsolationForest(
        contamination=contamination,
        n_estimators=100,
        max_samples='auto',
        random_state=42,
        n_jobs=-1,  # Usar todos os cores
        verbose=0
    )
    
    model.fit(X_train_scaled)
    
    print("  ✓ Modelo treinado com sucesso!")
    
    return model, scaler


def save_model(model, scaler, output_dir='../models'):
    """
    Salva modelo e scaler para uso posterior.
    
    Args:
        model: Modelo treinado
        scaler: StandardScaler ajustado
        output_dir: Diretório de saída
    """
    print(f"\n💾 Salvando modelo...")
    
    # Criar diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Salvar modelo
    model_path = os.path.join(output_dir, 'isolation_forest.joblib')
    joblib.dump(model, model_path)
    print(f"  ✓ Modelo salvo: {model_path}")
    
    # Salvar scaler
    scaler_path = os.path.join(output_dir, 'scaler.joblib')
    joblib.dump(scaler, scaler_path)
    print(f"  ✓ Scaler salvo: {scaler_path}")
    
    # Salvar lista de features (para garantir ordem na API)
    feature_cols = get_feature_columns()
    features_path = os.path.join(output_dir, 'feature_columns.txt')
    with open(features_path, 'w') as f:
        f.write('\n'.join(feature_cols))
    print(f"  ✓ Features salvas: {features_path}")


def quick_evaluation(model, scaler, X_test, y_test):
    """
    Avaliação rápida do modelo (detalhes na evaluate_model.py).
    
    Args:
        model: Modelo treinado
        scaler: StandardScaler
        X_test: Features de teste
        y_test: Labels de teste
    """
    print(f"\n📊 Avaliação Rápida no Conjunto de Teste...")
    
    # Normalizar test set
    X_test_scaled = scaler.transform(X_test)
    
    # Fazer predições (-1 = anomalia, 1 = normal)
    predictions = model.predict(X_test_scaled)
    
    # Converter para formato binário (1 = anomalia, 0 = normal)
    y_pred = (predictions == -1).astype(int)
    
    # Calcular métricas básicas
    total_frauds = y_test.sum()
    detected_frauds = (y_pred[y_test == 1] == 1).sum()
    
    recall = detected_frauds / total_frauds if total_frauds > 0 else 0
    
    total_normal = (y_test == 0).sum()
    false_positives = (y_pred[y_test == 0] == 1).sum()
    fpr = false_positives / total_normal if total_normal > 0 else 0
    
    print(f"\n  🎯 Recall (Fraudes Detectadas): {recall*100:.1f}%")
    print(f"     - {detected_frauds}/{total_frauds} fraudes detectadas")
    
    print(f"\n  ⚠️  Taxa de Falsos Positivos: {fpr*100:.2f}%")
    print(f"     - {false_positives:,} transações normais marcadas como fraude")
    
    print(f"\n  💡 Para análise detalhada por tipo e dificuldade:")
    print(f"     Execute: python evaluate_model.py")


def main():
    """Função principal."""
    
    # 1. Carregar dados
    df = load_processed_data()
    
    # 2. Dividir em treino/teste
    X_train, X_test, y_train, y_test, meta_test = prepare_train_test_split(df)
    
    # 3. Treinar modelo
    model, scaler = train_isolation_forest(X_train)
    
    # 4. Salvar modelo
    save_model(model, scaler)
    
    # 5. Avaliação rápida
    quick_evaluation(model, scaler, X_test, y_test)
    
    print("\n" + "=" * 80)
    print("✓ TREINO CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
    print("\n📌 Próximos passos:")
    print("  1. Avaliação detalhada: python evaluate_model.py")
    print("  2. Testar predições: python predict.py")
    print("  3. Deploy na API (Fase 5)")


if __name__ == '__main__':
    main()