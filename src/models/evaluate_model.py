"""
evaluate_model.py - Avaliação Detalhada do Isolation Forest
Fraud Detection Project - Fase 4

Este script avalia o modelo em profundidade:
- Recall por tipo de fraude
- Recall por dificuldade (easy/medium/hard)
- Análise de falsos positivos
- Curva de threshold

Execute após train_model.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
import sys

# Adicionar path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.build_features import get_feature_columns


def load_model_and_data():
    """Carrega modelo treinado e dados de teste."""
    print("=" * 80)
    print("AVALIAÇÃO DETALHADA - ISOLATION FOREST")
    print("=" * 80)
    
    # Carregar modelo
    print("\n📦 Carregando modelo treinado...")
    
    # Tentar diferentes caminhos para o modelo
    model_paths = [
        '../models/isolation_forest.joblib',
        '../../models/isolation_forest.joblib',
        'models/isolation_forest.joblib'
    ]
    
    model = None
    scaler = None
    for model_path in model_paths:
        scaler_path = model_path.replace('isolation_forest.joblib', 'scaler.joblib')
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            print(f"  ✓ Modelo carregado de: {model_path}")
            break
    
    if model is None:
        print("\n❌ ERRO: Modelo não encontrado!")
        print("Execute 'python train_model.py' primeiro!")
        sys.exit(1)
    
    # Carregar dados
    print("\n📂 Carregando dados de teste...")
    
    data_paths = [
        '../data/processed/transactions_with_features.csv',
        '../../data/processed/transactions_with_features.csv',
        'data/processed/transactions_with_features.csv'
    ]
    
    df = None
    for path in data_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            print(f"  ✓ Dados carregados de: {path}")
            break
    
    if df is None:
        print("\n❌ ERRO: Dados não encontrados!")
        print("Execute 'python eda_fraud_analysis.py' primeiro!")
        sys.exit(1)
    
    # Usar apenas conjunto de teste (últimas 200k transações)
    df_test = df.tail(200000).copy()
    
    # CRÍTICO: Resetar índices para alinhar com predições
    df_test = df_test.reset_index(drop=True)
    
    print(f"  ✓ {len(df_test):,} transações de teste")
    print(f"  ✓ Fraudes: {df_test['is_fraud'].sum():,}")
    
    return model, scaler, df_test


def evaluate_by_fraud_type(model, scaler, df_test):
    """Avalia recall por tipo de fraude."""
    print("\n" + "=" * 80)
    print("📊 RECALL POR TIPO DE FRAUDE")
    print("=" * 80)
    
    feature_cols = get_feature_columns()
    X_test = df_test[feature_cols]
    X_test_scaled = scaler.transform(X_test)
    
    # Predições
    predictions = model.predict(X_test_scaled)
    y_pred = (predictions == -1).astype(int)
    
    # IMPORTANTE: Adicionar predições ao dataframe para facilitar análise
    df_test_copy = df_test.copy()
    df_test_copy['predicted_fraud'] = y_pred
    
    # Filtrar apenas fraudes
    frauds = df_test_copy[df_test_copy['is_fraud'] == 1].copy()
    
    results = []
    for fraud_type in frauds['fraud_type'].unique():
        subset = frauds[frauds['fraud_type'] == fraud_type]
        total = len(subset)
        detected = subset['predicted_fraud'].sum()
        recall = detected / total if total > 0 else 0
        
        results.append({
            'fraud_type': fraud_type,
            'total': total,
            'detected': detected,
            'recall': recall
        })
        
        print(f"\n  {fraud_type}:")
        print(f"    Total: {total}")
        print(f"    Detectadas: {detected}")
        print(f"    Recall: {recall*100:.1f}%")
    
    return pd.DataFrame(results)


def evaluate_by_difficulty(model, scaler, df_test):
    """Avalia recall por dificuldade."""
    print("\n" + "=" * 80)
    print("📈 RECALL POR DIFICULDADE")
    print("=" * 80)
    
    feature_cols = get_feature_columns()
    X_test = df_test[feature_cols]
    X_test_scaled = scaler.transform(X_test)
    
    # Predições
    predictions = model.predict(X_test_scaled)
    y_pred = (predictions == -1).astype(int)
    
    # IMPORTANTE: Adicionar predições ao dataframe
    df_test_copy = df_test.copy()
    df_test_copy['predicted_fraud'] = y_pred
    
    # Filtrar apenas fraudes
    frauds = df_test_copy[df_test_copy['is_fraud'] == 1].copy()
    
    results = []
    difficulties = ['easy', 'medium', 'hard']
    
    for difficulty in difficulties:
        subset = frauds[frauds['fraud_difficulty'] == difficulty]
        total = len(subset)
        detected = subset['predicted_fraud'].sum()
        recall = detected / total if total > 0 else 0
        
        results.append({
            'difficulty': difficulty,
            'total': total,
            'detected': detected,
            'recall': recall
        })
        
        print(f"\n  {difficulty.upper()}:")
        print(f"    Total: {total}")
        print(f"    Detectadas: {detected}")
        print(f"    Recall: {recall*100:.1f}%")
    
    return pd.DataFrame(results)


def analyze_false_positives(model, scaler, df_test, top_n=10):
    """Analisa falsos positivos (transações normais marcadas como fraude)."""
    print("\n" + "=" * 80)
    print("⚠️  ANÁLISE DE FALSOS POSITIVOS")
    print("=" * 80)
    
    feature_cols = get_feature_columns()
    X_test = df_test[feature_cols]
    X_test_scaled = scaler.transform(X_test)
    
    # Predições e scores
    predictions = model.predict(X_test_scaled)
    scores = model.decision_function(X_test_scaled)
    
    y_pred = (predictions == -1).astype(int)
    
    # IMPORTANTE: Adicionar predições ao dataframe
    df_test_copy = df_test.copy()
    df_test_copy['predicted_fraud'] = y_pred
    df_test_copy['anomaly_score'] = scores
    
    # Filtrar falsos positivos (normais marcadas como fraude)
    false_positives = df_test_copy[
        (df_test_copy['is_fraud'] == 0) & 
        (df_test_copy['predicted_fraud'] == 1)
    ].copy()
    
    total_normal = (df_test_copy['is_fraud'] == 0).sum()
    
    print(f"\n  Total de falsos positivos: {len(false_positives):,}")
    print(f"  Taxa: {len(false_positives) / total_normal * 100:.2f}%")
    
    if len(false_positives) > 0:
        print(f"\n  Top {top_n} características de falsos positivos:")
        print(f"\n  (Transações normais que 'parecem' fraude)")
        
        fp_features = false_positives[feature_cols].describe()
        print(fp_features[['amount', 'velocity_kmh', 'distance_from_home_km', 'spending_zscore']])
    
    return false_positives


def plot_recall_by_type_and_difficulty(df_type, df_diff):
    """Gera gráfico de recall por tipo e dificuldade."""
    print("\n📊 Gerando visualizações...")
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Recall por tipo
    axes[0].bar(df_type['fraud_type'], df_type['recall'] * 100, 
                color='steelblue', alpha=0.7, edgecolor='black')
    axes[0].set_title('Recall por Tipo de Fraude', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Tipo de Fraude')
    axes[0].set_ylabel('Recall (%)')
    axes[0].set_ylim(0, 100)
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # Adicionar valores nas barras
    for i, v in enumerate(df_type['recall'] * 100):
        axes[0].text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')
    
    # Plot 2: Recall por dificuldade
    colors = {'easy': 'lightgreen', 'medium': 'orange', 'hard': 'crimson'}
    bar_colors = [colors[d] for d in df_diff['difficulty']]
    
    axes[1].bar(df_diff['difficulty'], df_diff['recall'] * 100, 
                color=bar_colors, alpha=0.7, edgecolor='black')
    axes[1].set_title('Recall por Dificuldade', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Dificuldade')
    axes[1].set_ylabel('Recall (%)')
    axes[1].set_ylim(0, 100)
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # Adicionar valores nas barras
    for i, v in enumerate(df_diff['recall'] * 100):
        axes[1].text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')
    
    plt.tight_layout()
    
    # Salvar - descobrir caminho correto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    reports_dir = os.path.join(project_root, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    save_path = os.path.join(reports_dir, '07_model_recall_analysis.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Salvo: {save_path}")
    plt.close()


def generate_evaluation_report(df_type, df_diff, false_positives):
    """Gera relatório textual da avaliação."""
    print("\n📋 Gerando relatório de avaliação...")
    
    report = []
    report.append("=" * 80)
    report.append("RELATÓRIO DE AVALIAÇÃO - ISOLATION FOREST")
    report.append("=" * 80)
    report.append("")
    
    # Recall por tipo
    report.append("🎯 RECALL POR TIPO DE FRAUDE:")
    report.append("")
    for _, row in df_type.iterrows():
        report.append(f"  {row['fraud_type']}:")
        report.append(f"    - Detectadas: {row['detected']}/{row['total']}")
        report.append(f"    - Recall: {row['recall']*100:.1f}%")
        report.append("")
    
    # Recall por dificuldade
    report.append("📈 RECALL POR DIFICULDADE:")
    report.append("")
    for _, row in df_diff.iterrows():
        report.append(f"  {row['difficulty'].upper()}:")
        report.append(f"    - Detectadas: {row['detected']}/{row['total']}")
        report.append(f"    - Recall: {row['recall']*100:.1f}%")
        report.append("")
    
    # Falsos positivos
    report.append("⚠️  FALSOS POSITIVOS:")
    report.append(f"  - Total: {len(false_positives):,}")
    report.append("")
    
    # Conclusão
    overall_recall = df_type['detected'].sum() / df_type['total'].sum()
    report.append("🏆 CONCLUSÃO:")
    report.append(f"  - Recall Geral: {overall_recall*100:.1f}%")
    report.append(f"  - Melhor Performance: Fraudes {df_type.loc[df_type['recall'].idxmax(), 'fraud_type']}")
    report.append(f"  - Desafio: Fraudes {df_diff.loc[df_diff['recall'].idxmin(), 'difficulty']}")
    report.append("")
    report.append("=" * 80)
    
    # Salvar - descobrir caminho correto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    reports_dir = os.path.join(project_root, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    report_path = os.path.join(reports_dir, '08_evaluation_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print('\n'.join(report))
    print(f"\n  ✓ Salvo: {report_path}")


def main():
    """Função principal."""
    
    # 1. Carregar modelo e dados
    model, scaler, df_test = load_model_and_data()
    
    # 2. Avaliar por tipo de fraude
    df_type = evaluate_by_fraud_type(model, scaler, df_test)
    
    # 3. Avaliar por dificuldade
    df_diff = evaluate_by_difficulty(model, scaler, df_test)
    
    # 4. Analisar falsos positivos
    false_positives = analyze_false_positives(model, scaler, df_test)
    
    # 5. Gerar visualizações
    plot_recall_by_type_and_difficulty(df_type, df_diff)
    
    # 6. Gerar relatório
    generate_evaluation_report(df_type, df_diff, false_positives)
    
    print("\n" + "=" * 80)
    print("✓ AVALIAÇÃO CONCLUÍDA!")
    print("=" * 80)


if __name__ == '__main__':
    main()