"""
inject_frauds.py - Script principal para injeção de fraudes
Fraud Detection Project - Fase 2

Este script:
1. Carrega o CSV de transações normais
2. Injeta 600 fraudes distribuídas em 5 tipos e 3 níveis de dificuldade
3. Salva o dataset final

Execução: ~20 segundos
"""

import pandas as pd
import os
import sys
from datetime import datetime

# Importar funções de injeção
from fraud_injectors import (
    inject_teleport_fraud,
    inject_sudden_spending_fraud,
    inject_card_testing_fraud,
    inject_unusual_time_fraud,
    inject_risky_merchant_fraud
)


def main():
    print("=" * 80)
    print("INJEÇÃO DE FRAUDES SINTÉTICAS - FRAUD DETECTION")
    print("=" * 80)
    
    # Paths
    input_path = '../../data/raw/transactions.csv'
    output_path = '../../data/raw/transactions_with_fraud.csv'
    backup_path = '../../data/raw/transactions_normal_backup.csv'
    gabarito_path = '../../data/raw/fraud_gabarito.csv'
    
    # =========================================================================
    # ESTRATÉGIA DE BACKUP E RESTAURAÇÃO
    # =========================================================================
    # Se o backup existir, usar ele (dados limpos)
    # Se não existir, criar backup do arquivo atual
    
    if os.path.exists(backup_path):
        print(f"\n📂 Backup encontrado! Carregando dados limpos de: {backup_path}")
        input_path = backup_path
    
    # Verificar se arquivo existe
    if not os.path.exists(input_path):
        print(f"\n❌ ERRO: Arquivo não encontrado: {input_path}")
        print("Execute 'python generate_data.py' primeiro!")
        sys.exit(1)
    
    # Carregar dados
    print(f"📂 Carregando transações normais de: {input_path}")
    df = pd.read_csv(input_path)
    
    # CRÍTICO: Converter timestamp para datetime IMEDIATAMENTE
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    print(f"  ✓ {len(df):,} transações normais carregadas")
    print(f"  ✓ Período: {df['timestamp'].min()} a {df['timestamp'].max()}")
    
    # Fazer backup (se não existir)
    if not os.path.exists(backup_path):
        print(f"\n💾 Criando backup: {backup_path}")
        df.to_csv(backup_path, index=False)
        print("  ✓ Backup criado!")
    
    # =========================================================================
    # ESTRATÉGIA DE DISTRIBUIÇÃO DAS FRAUDES
    # =========================================================================
    # Total: 600 fraudes (0.2% de 300.000)
    # 
    # Por tipo (5 tipos × 120 fraudes cada):
    # - 🌍 Teleporte: 120
    # - 💸 Gasto Súbito: 120
    # - 🔍 Sondagem: 40 sequências (120 transações totais, pois cada sequência tem 3-10 txs)
    # - 🌙 Horário Atípico: 120
    # - 🎰 Merchant Suspeito: 120
    #
    # Por dificuldade:
    # - Easy: 50 por tipo
    # - Medium: 50 por tipo  
    # - Hard: 20 por tipo
    # =========================================================================
    
    print("\n" + "=" * 80)
    print("INICIANDO INJEÇÃO DE FRAUDES")
    print("=" * 80)
    
    # 🌍 FRAUDE TIPO 1: TELEPORTE GEOGRÁFICO (120 total)
    df = inject_teleport_fraud(df, n_samples=50, difficulty='easy')
    df = inject_teleport_fraud(df, n_samples=50, difficulty='medium')
    df = inject_teleport_fraud(df, n_samples=20, difficulty='hard')
    
    # 💸 FRAUDE TIPO 2: GASTO SÚBITO (120 total)
    df = inject_sudden_spending_fraud(df, n_samples=50, difficulty='easy')
    df = inject_sudden_spending_fraud(df, n_samples=50, difficulty='medium')
    df = inject_sudden_spending_fraud(df, n_samples=20, difficulty='hard')
    
    # 🔍 FRAUDE TIPO 3: SONDAGEM DE CARTÃO (40 sequências = ~120-400 transações)
    # Nota: Cada sequência gera múltiplas transações (3-10 dependendo da dificuldade)
    df = inject_card_testing_fraud(df, n_samples=15, difficulty='easy')    # 15 × 10 = 150 txs
    df = inject_card_testing_fraud(df, n_samples=15, difficulty='medium')  # 15 × 5 = 75 txs
    df = inject_card_testing_fraud(df, n_samples=10, difficulty='hard')    # 10 × 3 = 30 txs
    # Total: ~255 transações de sondagem
    
    # 🌙 FRAUDE TIPO 4: HORÁRIO ATÍPICO (120 total)
    df = inject_unusual_time_fraud(df, n_samples=50, difficulty='easy')
    df = inject_unusual_time_fraud(df, n_samples=50, difficulty='medium')
    df = inject_unusual_time_fraud(df, n_samples=20, difficulty='hard')
    
    # 🎰 FRAUDE TIPO 5: MERCHANT SUSPEITO (120 total)
    df = inject_risky_merchant_fraud(df, n_samples=50, difficulty='easy')
    df = inject_risky_merchant_fraud(df, n_samples=50, difficulty='medium')
    df = inject_risky_merchant_fraud(df, n_samples=20, difficulty='hard')
    
    # =========================================================================
    # ESTATÍSTICAS FINAIS
    # =========================================================================
    
    print("\n" + "=" * 80)
    print("ESTATÍSTICAS DO DATASET FINAL")
    print("=" * 80)
    
    total_transactions = len(df)
    total_frauds = df['is_fraud'].sum()
    fraud_percentage = (total_frauds / total_transactions) * 100
    
    print(f"\n📊 Visão Geral:")
    print(f"  - Total de transações: {total_transactions:,}")
    print(f"  - Transações normais: {total_transactions - total_frauds:,} ({100 - fraud_percentage:.2f}%)")
    print(f"  - Transações fraudulentas: {total_frauds:,} ({fraud_percentage:.2f}%)")
    
    print(f"\n🎯 Distribuição por Tipo de Fraude:")
    fraud_types = df[df['is_fraud'] == 1]['fraud_type'].value_counts()
    for fraud_type, count in fraud_types.items():
        print(f"  - {fraud_type}: {count} fraudes")
    
    print(f"\n📈 Distribuição por Dificuldade:")
    fraud_difficulty = df[df['is_fraud'] == 1]['fraud_difficulty'].value_counts()
    for difficulty, count in fraud_difficulty.items():
        print(f"  - {difficulty}: {count} fraudes")
    
    # =========================================================================
    # SALVAR DADOS
    # =========================================================================
    
    print(f"\n💾 Salvando dataset final...")
    
    # Ordenar por timestamp (importante para análises temporais)
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Converter timestamp de volta para string (formato CSV consistente)
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Salvar dataset completo
    df.to_csv(output_path, index=False)
    file_size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"  ✓ Dataset salvo em: {output_path}")
    print(f"    - Tamanho: {file_size_mb:.2f} MB")
    
    # Salvar gabarito (apenas fraudes)
    fraud_df = df[df['is_fraud'] == 1].copy()
    fraud_df.to_csv(gabarito_path, index=False)
    print(f"  ✓ Gabarito salvo em: {gabarito_path}")
    print(f"    - Total de fraudes: {len(fraud_df):,}")
    
    # =========================================================================
    # VALIDAÇÃO RÁPIDA
    # =========================================================================
    
    print(f"\n🔍 Validação Rápida:")
    
    # Verificar se há NaN
    if df.isnull().any().any():
        print("  ⚠️  AVISO: Dataset contém valores NaN!")
    else:
        print("  ✓ Sem valores NaN")
    
    # Verificar tipos de dados
    if df['is_fraud'].dtype == 'int64':
        print("  ✓ Coluna is_fraud é int64")
    else:
        print(f"  ⚠️  AVISO: is_fraud deveria ser int64, mas é {df['is_fraud'].dtype}")
    
    # Verificar range de valores
    if df['amount'].min() >= 0:
        print("  ✓ Valores de amount são positivos")
    else:
        print("  ⚠️  AVISO: Existem valores negativos em amount")
    
    print("\n" + "=" * 80)
    print("✓ INJEÇÃO DE FRAUDES CONCLUÍDA COM SUCESSO!")
    print("=" * 80)
    
    print(f"\n📌 Próximos passos:")
    print(f"  1. Explorar dados: jupyter notebook ../../notebooks/")
    print(f"  2. Criar features de detecção de anomalias")
    print(f"  3. Treinar Isolation Forest")
    print(f"  4. Avaliar performance por tipo e dificuldade de fraude")


if __name__ == '__main__':
    main()