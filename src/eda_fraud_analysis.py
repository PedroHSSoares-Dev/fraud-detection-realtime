"""
eda_fraud_analysis.py - Análise Exploratória e Visualização de Fraudes
Fraud Detection Project - Fase 3

Este script cria visualizações profissionais que provam que fraudes são anomalias.
Executa automaticamente e salva gráficos em alta resolução.

Execute: python eda_fraud_analysis.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

# Adicionar path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.build_features import build_all_features, get_feature_columns

# Configurar estilo dos gráficos
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 11

def load_and_prepare_data():
    """Carrega dados e aplica feature engineering."""
    print("=" * 80)
    print("ANÁLISE EXPLORATÓRIA DE FRAUDES")
    print("=" * 80)
    
    print("\n📂 Carregando dados...")
    
    # Tentar diferentes caminhos possíveis
    possible_paths = [
        '../../data/raw/transactions_with_fraud.csv',
        '../data/raw/transactions_with_fraud.csv',
        'data/raw/transactions_with_fraud.csv'
    ]
    
    df = None
    for path in possible_paths:
        if os.path.exists(path):
            print(f"  ✓ Arquivo encontrado em: {path}")
            df = pd.read_csv(path)
            break
    
    if df is None:
        print("\n❌ ERRO: Arquivo não encontrado!")
        print("Tentativas:")
        for path in possible_paths:
            print(f"  - {path}")
        print("\n💡 Verifique se você executou 'python inject_frauds.py' primeiro!")
        sys.exit(1)
    
    print(f"  ✓ {len(df):,} transações carregadas")
    print(f"  ✓ Fraudes: {df['is_fraud'].sum():,} ({df['is_fraud'].mean()*100:.2f}%)")
    
    # Aplicar feature engineering
    df = build_all_features(df)
    
    return df


def plot_fraud_distribution(df):
    """Plot 1: Distribuição de fraudes por tipo e dificuldade."""
    print("\n📊 Gerando gráfico: Distribuição de Fraudes...")
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # Por tipo
    fraud_types = df[df['is_fraud'] == 1]['fraud_type'].value_counts()
    axes[0].bar(fraud_types.index, fraud_types.values, color='crimson', alpha=0.7, edgecolor='black')
    axes[0].set_title('Distribuição de Fraudes por Tipo', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Tipo de Fraude')
    axes[0].set_ylabel('Quantidade')
    axes[0].tick_params(axis='x', rotation=45)
    
    for i, v in enumerate(fraud_types.values):
        axes[0].text(i, v + 5, str(v), ha='center', fontweight='bold')
    
    # Por dificuldade
    fraud_diff = df[df['is_fraud'] == 1]['fraud_difficulty'].value_counts()
    colors = {'easy': 'lightcoral', 'medium': 'orange', 'hard': 'darkred'}
    axes[1].bar(
        fraud_diff.index, 
        fraud_diff.values, 
        color=[colors[x] for x in fraud_diff.index],
        alpha=0.7,
        edgecolor='black'
    )
    axes[1].set_title('Distribuição de Fraudes por Dificuldade', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Nível de Dificuldade')
    axes[1].set_ylabel('Quantidade')
    
    for i, v in enumerate(fraud_diff.values):
        axes[1].text(i, v + 5, str(v), ha='center', fontweight='bold')
    
    plt.tight_layout()
    save_path = os.path.join(REPORTS_DIR, '01_fraud_distribution.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Salvo: {save_path}")
    plt.close()


def plot_velocity_scatter(df):
    """Plot 2: Velocidade vs Distância (DETECTA TELEPORTE)."""
    print("\n📊 Gerando gráfico: Velocidade vs Distância (Teleporte)...")
    
    # Filtrar apenas transações com velocidade > 0
    df_velocity = df[df['velocity_kmh'] > 0].copy()
    
    plt.figure(figsize=(14, 8))
    
    # Scatter plot normal vs fraude
    normal = df_velocity[df_velocity['is_fraud'] == 0]
    fraud = df_velocity[df_velocity['is_fraud'] == 1]
    
    plt.scatter(
        normal['distance_from_home_km'], 
        normal['velocity_kmh'], 
        alpha=0.3, 
        s=10, 
        label='Normal', 
        color='blue'
    )
    
    plt.scatter(
        fraud['distance_from_home_km'], 
        fraud['velocity_kmh'], 
        alpha=0.8, 
        s=50, 
        label='Fraude', 
        color='red',
        edgecolors='black',
        linewidths=0.5
    )
    
    # Linha de "velocidade humanamente impossível" (800 km/h = velocidade de avião)
    plt.axhline(y=800, color='orange', linestyle='--', linewidth=2, label='Velocidade de Avião (800 km/h)')
    
    plt.title('Velocidade Entre Transações vs Distância de Casa\n(DETECTA TELEPORTE GEOGRÁFICO)', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Distância de Casa (km)', fontsize=12)
    plt.ylabel('Velocidade Entre Transações (km/h)', fontsize=12)
    plt.legend(fontsize=11)
    plt.yscale('log')  # Escala logarítmica para ver todos os pontos
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, '02_velocity_vs_distance.png'), dpi=300, bbox_inches='tight')
    print("  ✓ Salvo: reports/02_velocity_vs_distance.png")
    plt.close()


def plot_spending_deviation(df):
    """Plot 3: Z-score de Gasto por Tipo de Fraude (DETECTA GASTO SÚBITO)."""
    print("\n📊 Gerando gráfico: Desvio de Gasto (Gasto Súbito)...")
    
    plt.figure(figsize=(14, 8))
    
    # Preparar dados
    fraud_data = df[df['is_fraud'] == 1].copy()
    fraud_data = fraud_data[fraud_data['spending_zscore'] < 50]  # Remover outliers extremos
    
    # Boxplot por tipo de fraude
    fraud_types = fraud_data['fraud_type'].unique()
    data_to_plot = [fraud_data[fraud_data['fraud_type'] == ft]['spending_zscore'].values 
                    for ft in fraud_types]
    
    bp = plt.boxplot(data_to_plot, labels=fraud_types, patch_artist=True)
    
    # Colorir boxes
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    # Linha de referência (z-score = 3 = muito acima da média)
    plt.axhline(y=3, color='red', linestyle='--', linewidth=2, label='Z-score = 3 (Suspeito)')
    
    plt.title('Desvio de Gasto (Z-score) por Tipo de Fraude\n(DETECTA GASTO SÚBITO)', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Tipo de Fraude', fontsize=12)
    plt.ylabel('Z-score do Valor (desvios padrão da média do usuário)', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, '03_spending_deviation_by_type.png'), dpi=300, bbox_inches='tight')
    print("  ✓ Salvo: reports/03_spending_deviation_by_type.png")
    plt.close()


def plot_time_between_transactions(df):
    """Plot 4: Tempo Entre Transações (DETECTA SONDAGEM)."""
    print("\n📊 Gerando gráfico: Tempo Entre Transações (Sondagem)...")
    
    plt.figure(figsize=(14, 8))
    
    # Filtrar transações com tempo < 1 hora (3600s)
    df_fast = df[df['time_since_last_tx_sec'] < 3600].copy()
    
    normal = df_fast[df_fast['is_fraud'] == 0]
    fraud = df_fast[df_fast['is_fraud'] == 1]
    
    # Histograma
    bins = np.logspace(0, np.log10(3600), 50)
    
    plt.hist(normal['time_since_last_tx_sec'], bins=bins, alpha=0.5, 
             label='Normal', color='blue', edgecolor='black')
    plt.hist(fraud['time_since_last_tx_sec'], bins=bins, alpha=0.7, 
             label='Fraude', color='red', edgecolor='black')
    
    # Linha de "suspeito" (< 60 segundos)
    plt.axvline(x=60, color='orange', linestyle='--', linewidth=2, 
                label='< 60 segundos (Suspeito)')
    
    plt.title('Tempo Desde Última Transação do Usuário\n(DETECTA SONDAGEM DE CARTÃO)', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Tempo Desde Última Transação (segundos)', fontsize=12)
    plt.ylabel('Frequência', fontsize=12)
    plt.xscale('log')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, '04_time_between_transactions.png'), dpi=300, bbox_inches='tight')
    print("  ✓ Salvo: reports/04_time_between_transactions.png")
    plt.close()


def plot_hour_heatmap(df):
    """Plot 5: Heatmap de Fraudes por Hora (DETECTA HORÁRIO ATÍPICO)."""
    print("\n📊 Gerando gráfico: Heatmap de Horários (Horário Atípico)...")
    
    # Contar fraudes por hora e tipo
    fraud_df = df[df['is_fraud'] == 1].copy()
    
    pivot = fraud_df.groupby(['fraud_type', 'hour_of_day']).size().reset_index(name='count')
    pivot_table = pivot.pivot(index='fraud_type', columns='hour_of_day', values='count').fillna(0)
    
    plt.figure(figsize=(16, 6))
    sns.heatmap(pivot_table, annot=False, cmap='YlOrRd', cbar_kws={'label': 'Número de Fraudes'})
    
    plt.title('Distribuição de Fraudes por Hora do Dia\n(DETECTA HORÁRIO ATÍPICO)', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Hora do Dia', fontsize=12)
    plt.ylabel('Tipo de Fraude', fontsize=12)
    
    # Destacar madrugada (0-5h)
    plt.axvline(x=5, color='blue', linestyle='--', linewidth=2, alpha=0.7)
    plt.text(2.5, -0.5, 'MADRUGADA\n(0h-5h)', ha='center', fontsize=10, 
             color='blue', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, '05_hour_heatmap.png'), dpi=300, bbox_inches='tight')
    print("  ✓ Salvo: reports/05_hour_heatmap.png")
    plt.close()


def plot_feature_correlation(df):
    """Plot 6: Matriz de Correlação de Features."""
    print("\n📊 Gerando gráfico: Correlação de Features...")
    
    feature_cols = get_feature_columns()
    
    # Calcular correlação
    corr = df[feature_cols].corr()
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8})
    
    plt.title('Matriz de Correlação Entre Features\n(Features Independentes = Bom para ML)', 
              fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, '06_feature_correlation.png'), dpi=300, bbox_inches='tight')
    print("  ✓ Salvo: reports/06_feature_correlation.png")
    plt.close()


def generate_summary_report(df):
    """Gera relatório textual com estatísticas."""
    print("\n📋 Gerando relatório de estatísticas...")
    
    report = []
    report.append("=" * 80)
    report.append("RELATÓRIO DE ANÁLISE EXPLORATÓRIA - FRAUD DETECTION")
    report.append("=" * 80)
    report.append("")
    
    # Estatísticas gerais
    report.append("📊 ESTATÍSTICAS GERAIS:")
    report.append(f"  - Total de transações: {len(df):,}")
    report.append(f"  - Transações normais: {(df['is_fraud'] == 0).sum():,} ({(df['is_fraud'] == 0).mean()*100:.2f}%)")
    report.append(f"  - Transações fraudulentas: {df['is_fraud'].sum():,} ({df['is_fraud'].mean()*100:.2f}%)")
    report.append("")
    
    # Distribuição por tipo
    report.append("🎯 DISTRIBUIÇÃO POR TIPO DE FRAUDE:")
    fraud_types = df[df['is_fraud'] == 1]['fraud_type'].value_counts()
    for fraud_type, count in fraud_types.items():
        report.append(f"  - {fraud_type}: {count} fraudes")
    report.append("")
    
    # Distribuição por dificuldade
    report.append("📈 DISTRIBUIÇÃO POR DIFICULDADE:")
    fraud_diff = df[df['is_fraud'] == 1]['fraud_difficulty'].value_counts()
    for difficulty, count in fraud_diff.items():
        report.append(f"  - {difficulty}: {count} fraudes")
    report.append("")
    
    # Estatísticas de features (fraude vs normal)
    report.append("🔍 COMPARAÇÃO FRAUDE VS NORMAL (Features Médias):")
    feature_cols = get_feature_columns()
    
    for feature in feature_cols:
        normal_mean = df[df['is_fraud'] == 0][feature].mean()
        fraud_mean = df[df['is_fraud'] == 1][feature].mean()
        diff_pct = ((fraud_mean - normal_mean) / normal_mean * 100) if normal_mean != 0 else 0
        
        report.append(f"  - {feature}:")
        report.append(f"      Normal: {normal_mean:.2f} | Fraude: {fraud_mean:.2f} | Diferença: {diff_pct:+.1f}%")
    
    report.append("")
    report.append("=" * 80)
    report.append("✓ ANÁLISE CONCLUÍDA!")
    report.append("=" * 80)
    
    # Salvar relatório
    with open(os.path.join(REPORTS_DIR, '00_summary_report.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print('\n'.join(report))
    print(f"\n  ✓ Salvo: {os.path.join(REPORTS_DIR, '00_summary_report.txt')}")


def main():
    """Função principal."""
    # Determinar diretório base do projeto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Criar diretório de reports se não existir
    reports_dir = os.path.join(project_root, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Atualizar caminhos globalmente (hack rápido para os plots)
    global REPORTS_DIR, PROCESSED_DIR
    REPORTS_DIR = reports_dir
    PROCESSED_DIR = os.path.join(project_root, 'data', 'processed')
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # Carregar e preparar dados
    df = load_and_prepare_data()
    
    # Salvar dataset com features
    print("\n💾 Salvando dataset com features...")
    output_path = os.path.join(PROCESSED_DIR, 'transactions_with_features.csv')
    df.to_csv(output_path, index=False)
    print(f"  ✓ Salvo: {output_path}")
    
    # Gerar todas as visualizações
    print("\n🎨 Gerando visualizações...")
    plot_fraud_distribution(df)
    plot_velocity_scatter(df)
    plot_spending_deviation(df)
    plot_time_between_transactions(df)
    plot_hour_heatmap(df)
    plot_feature_correlation(df)
    
    # Gerar relatório textual
    generate_summary_report(df)
    
    print("\n" + "=" * 80)
    print("✓ ANÁLISE EXPLORATÓRIA CONCLUÍDA COM SUCESSO!")
    print("=" * 80)
    print(f"\n📁 Arquivos gerados em: {reports_dir}")
    print("  - 00_summary_report.txt")
    print("  - 01_fraud_distribution.png")
    print("  - 02_velocity_vs_distance.png")
    print("  - 03_spending_deviation_by_type.png")
    print("  - 04_time_between_transactions.png")
    print("  - 05_hour_heatmap.png")
    print("  - 06_feature_correlation.png")
    print("\n💡 Use essas visualizações no seu README e apresentações!")


# Variáveis globais para caminhos (serão definidas no main)
REPORTS_DIR = '../../reports'
PROCESSED_DIR = '../../data/processed'


if __name__ == '__main__':
    main()