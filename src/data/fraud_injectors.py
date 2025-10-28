"""
fraud_injectors.py - Funções de injeção de fraudes sintéticas
Fraud Detection Project - Fase 2

Este módulo contém as 5 funções que injetam fraudes de diferentes tipos
e níveis de dificuldade no dataset de transações normais.

Estratégia:
- Cada função pega N amostras de transações normais
- Modifica características específicas para criar anomalias
- Marca is_fraud=1, fraud_type e fraud_difficulty
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from typing import Tuple


def inject_teleport_fraud(df: pd.DataFrame, n_samples: int, difficulty: str) -> pd.DataFrame:
    """
    🌍 FRAUDE TIPO 1: TELEPORTE GEOGRÁFICO
    
    Simula um fraudador que rouba dados do cartão e tenta usar em outro país
    enquanto o usuário legítimo ainda está fazendo transações no país de origem.
    
    LÓGICA:
    1. Selecionar N usuários aleatórios que tenham pelo menos 2 transações
    2. Pegar uma transação do usuário
    3. Criar uma nova transação do mesmo usuário em localização distante
    4. Intervalo de tempo curto (fisicamente impossível)
    
    NÍVEIS DE DIFICULDADE:
    - easy: Brasil → China em 5 minutos (óbvio)
    - medium: São Paulo → Rio em 30 minutos (muito suspeito)
    - hard: Mesma cidade, bairros distantes em 10 minutos (sutil)
    
    Args:
        df: DataFrame com transações
        n_samples: Número de fraudes a injetar
        difficulty: 'easy', 'medium' ou 'hard'
    
    Returns:
        DataFrame com fraudes injetadas
    """
    print(f"\n🌍 Injetando {n_samples} fraudes de TELEPORTE ({difficulty})...")
    
    # Configurar parâmetros por dificuldade
    if difficulty == 'easy':
        time_delta_minutes = np.random.randint(1, 10, n_samples)  # 1-10 min
        distance_km = np.random.uniform(5000, 15000, n_samples)  # 5.000-15.000 km
        different_country = True
    elif difficulty == 'medium':
        time_delta_minutes = np.random.randint(10, 60, n_samples)  # 10-60 min
        distance_km = np.random.uniform(500, 2000, n_samples)  # 500-2.000 km
        different_country = np.random.rand(n_samples) > 0.5  # 50% outro país
    else:  # hard
        time_delta_minutes = np.random.randint(5, 30, n_samples)  # 5-30 min
        distance_km = np.random.uniform(20, 100, n_samples)  # 20-100 km (mesma cidade)
        different_country = False
    
    # Encontrar usuários com múltiplas transações
    user_counts = df['user_id'].value_counts()
    eligible_users = user_counts[user_counts >= 2].index.tolist()
    
    if len(eligible_users) < n_samples:
        print(f"  ⚠️  Aviso: Apenas {len(eligible_users)} usuários elegíveis. Ajustando n_samples.")
        n_samples = len(eligible_users)
    
    # Selecionar usuários aleatórios
    selected_users = np.random.choice(eligible_users, n_samples, replace=False)
    
    fraud_transactions = []
    
    for i, user_id in enumerate(selected_users):
        # Pegar transações do usuário
        user_txs = df[df['user_id'] == user_id].sort_values('timestamp')
        
        # Escolher uma transação base (não a última, para ter contexto temporal)
        if len(user_txs) > 2:
            base_tx = user_txs.iloc[np.random.randint(0, len(user_txs) - 1)]
        else:
            base_tx = user_txs.iloc[0]
        
        # Criar transação fraudulenta "teleportada"
        fraud_tx = base_tx.copy()
        
        # Mudar timestamp (adicionar poucos minutos) - mantém como datetime
        fraud_tx['timestamp'] = pd.to_datetime(base_tx['timestamp']) + timedelta(minutes=int(time_delta_minutes[i]))
        
        # Mudar localização (coordenadas aleatórias distantes)
        if different_country if isinstance(different_country, bool) else different_country[i]:
            # Outro país
            fraud_tx['latitude'] = np.random.uniform(-90, 90)
            fraud_tx['longitude'] = np.random.uniform(-180, 180)
            fraud_tx['country'] = np.random.choice(['US', 'CN', 'GB', 'RU', 'IN', 'JP'])
            fraud_tx['city'] = 'Foreign City'
        else:
            # Mesma cidade, coordenadas distantes
            # Aproximação: 1 grau ≈ 111 km
            offset_degrees = distance_km[i] / 111
            fraud_tx['latitude'] = float(base_tx['latitude']) + np.random.uniform(-offset_degrees, offset_degrees)
            fraud_tx['longitude'] = float(base_tx['longitude']) + np.random.uniform(-offset_degrees, offset_degrees)
        
        # Marcar como fraude
        fraud_tx['is_fraud'] = 1
        fraud_tx['fraud_type'] = 'teleport'
        fraud_tx['fraud_difficulty'] = difficulty
        # ID sequencial normal (não vazar informação!)
        fraud_tx['transaction_id'] = f'TX{len(df) + i:010d}'
        
        fraud_transactions.append(fraud_tx)
    
    # Adicionar fraudes ao dataframe
    fraud_df = pd.DataFrame(fraud_transactions)
    df = pd.concat([df, fraud_df], ignore_index=True)
    
    print(f"  ✓ {len(fraud_transactions)} fraudes de teleporte injetadas!")
    
    return df


def inject_sudden_spending_fraud(df: pd.DataFrame, n_samples: int, difficulty: str) -> pd.DataFrame:
    """
    💸 FRAUDE TIPO 2: GASTO SÚBITO
    
    Simula um fraudador que rouba o cartão e faz uma compra de alto valor,
    muito acima do padrão de gasto do usuário legítimo.
    
    LÓGICA:
    1. Calcular o valor médio de transações do usuário
    2. Criar transação com valor muito acima da média
    3. Quanto maior o multiplicador, mais fácil de detectar
    
    NÍVEIS DE DIFICULDADE:
    - easy: 100x a média (R$ 50 → R$ 5.000)
    - medium: 10x a média (R$ 50 → R$ 500)
    - hard: 3x a média (R$ 50 → R$ 150) - pode ser compra legítima!
    
    Args:
        df: DataFrame com transações
        n_samples: Número de fraudes a injetar
        difficulty: 'easy', 'medium' ou 'hard'
    
    Returns:
        DataFrame com fraudes injetadas
    """
    print(f"\n💸 Injetando {n_samples} fraudes de GASTO SÚBITO ({difficulty})...")
    
    # Configurar multiplicador por dificuldade
    if difficulty == 'easy':
        multiplier_range = (50, 100)
    elif difficulty == 'medium':
        multiplier_range = (8, 15)
    else:  # hard
        multiplier_range = (3, 5)
    
    # Calcular média de gasto por usuário
    user_avg_spending = df.groupby('user_id')['amount'].mean()
    
    # Selecionar usuários aleatórios
    selected_users = np.random.choice(user_avg_spending.index, n_samples, replace=False)
    
    fraud_transactions = []
    
    for i, user_id in enumerate(selected_users):
        # Pegar uma transação base do usuário
        user_txs = df[df['user_id'] == user_id]
        base_tx = user_txs.sample(n=1).iloc[0]
        
        # Criar transação fraudulenta com gasto súbito
        fraud_tx = base_tx.copy()
        
        # Calcular novo valor (multiplicador aleatório no range)
        multiplier = np.random.uniform(*multiplier_range)
        avg_amount = user_avg_spending[user_id]
        fraud_tx['amount'] = round(avg_amount * multiplier, 2)
        
        # Limitar a valores realistas (máximo R$ 50.000)
        fraud_tx['amount'] = min(fraud_tx['amount'], 50000)
        
        # Ajustar timestamp (alguns dias depois) - mantém como datetime
        fraud_tx['timestamp'] = pd.to_datetime(base_tx['timestamp']) + timedelta(days=np.random.randint(1, 7))
        
        # Categoria suspeita (eletrônicos, joias, viagem)
        fraud_tx['merchant_category'] = np.random.choice(['electronics', 'jewelry', 'travel', 'luxury'])
        
        # Marcar como fraude
        fraud_tx['is_fraud'] = 1
        fraud_tx['fraud_type'] = 'sudden_spending'
        fraud_tx['fraud_difficulty'] = difficulty
        fraud_tx['transaction_id'] = f'TX{len(df) + i:010d}'
        
        fraud_transactions.append(fraud_tx)
    
    # Adicionar fraudes ao dataframe
    fraud_df = pd.DataFrame(fraud_transactions)
    df = pd.concat([df, fraud_df], ignore_index=True)
    
    print(f"  ✓ {len(fraud_transactions)} fraudes de gasto súbito injetadas!")
    
    return df


def inject_card_testing_fraud(df: pd.DataFrame, n_samples: int, difficulty: str) -> pd.DataFrame:
    """
    🔍 FRAUDE TIPO 3: SONDAGEM DE CARTÃO (Card Testing)
    
    Simula fraudador testando se cartão roubado funciona antes de fazer
    grandes compras. Faz múltiplas transações pequenas em poucos minutos.
    
    LÓGICA:
    1. Escolher um usuário
    2. Criar múltiplas transações pequenas (R$ 1-10)
    3. Intervalo de tempo muito curto entre elas
    
    NÍVEIS DE DIFICULDADE:
    - easy: 10 transações em 30 segundos
    - medium: 5 transações em 2 minutos
    - hard: 3 transações em 5 minutos (pode ser comportamento normal)
    
    Args:
        df: DataFrame com transações
        n_samples: Número de SEQUÊNCIAS de fraude a injetar
        difficulty: 'easy', 'medium' ou 'hard'
    
    Returns:
        DataFrame com fraudes injetadas
    """
    print(f"\n🔍 Injetando {n_samples} fraudes de SONDAGEM ({difficulty})...")
    
    # Configurar parâmetros por dificuldade
    if difficulty == 'easy':
        n_tests_per_sequence = 10
        time_window_seconds = 30
        amount_range = (1, 5)
    elif difficulty == 'medium':
        n_tests_per_sequence = 5
        time_window_seconds = 120
        amount_range = (5, 15)
    else:  # hard
        n_tests_per_sequence = 3
        time_window_seconds = 300
        amount_range = (10, 30)
    
    # Selecionar usuários aleatórios
    all_users = df['user_id'].unique()
    selected_users = np.random.choice(all_users, n_samples, replace=False)
    
    fraud_transactions = []
    
    for i, user_id in enumerate(selected_users):
        # Pegar uma transação base do usuário
        user_txs = df[df['user_id'] == user_id]
        base_tx = user_txs.sample(n=1).iloc[0]
        
        # Timestamp base (alguns dias depois da transação original)
        base_timestamp = pd.to_datetime(base_tx['timestamp']) + timedelta(days=np.random.randint(1, 5))
        
        # Criar sequência de testes
        for test_num in range(n_tests_per_sequence):
            fraud_tx = base_tx.copy()
            
            # Timestamp incrementado dentro da janela de tempo - mantém como datetime
            seconds_offset = np.random.randint(0, time_window_seconds)
            fraud_tx['timestamp'] = base_timestamp + timedelta(seconds=seconds_offset)
            
            # Valor pequeno (teste)
            fraud_tx['amount'] = round(np.random.uniform(*amount_range), 2)
            
            # Merchant aleatório (online)
            fraud_tx['merchant_category'] = np.random.choice(['online_shopping', 'entertainment', 'utilities'])
            fraud_tx['merchant_name'] = f'Online Merchant Test {test_num}'
            
            # Marcar como fraude
            fraud_tx['is_fraud'] = 1
            fraud_tx['fraud_type'] = 'card_testing'
            fraud_tx['fraud_difficulty'] = difficulty
            fraud_tx['transaction_id'] = f'TX{len(df) + (i * n_tests_per_sequence) + test_num:010d}'
            
            fraud_transactions.append(fraud_tx)
    
    # Adicionar fraudes ao dataframe
    fraud_df = pd.DataFrame(fraud_transactions)
    df = pd.concat([df, fraud_df], ignore_index=True)
    
    print(f"  ✓ {len(fraud_transactions)} fraudes de sondagem injetadas ({n_samples} sequências)!")
    
    return df


def inject_unusual_time_fraud(df: pd.DataFrame, n_samples: int, difficulty: str) -> pd.DataFrame:
    """
    🌙 FRAUDE TIPO 4: HORÁRIO ATÍPICO
    
    Simula transações em horários que o usuário normalmente não faria,
    combinado com categorias incomuns.
    
    LÓGICA:
    1. Identificar padrão de horário do usuário
    2. Criar transação em horário atípico (madrugada)
    3. Categoria incomum para o usuário
    
    NÍVEIS DE DIFICULDADE:
    - easy: 3h AM + categoria nunca usada + valor alto
    - medium: 2h AM + categoria rara + valor médio
    - hard: 1h AM + categoria ocasional + valor baixo
    
    Args:
        df: DataFrame com transações
        n_samples: Número de fraudes a injetar
        difficulty: 'easy', 'medium' ou 'hard'
    
    Returns:
        DataFrame com fraudes injetadas
    """
    print(f"\n🌙 Injetando {n_samples} fraudes de HORÁRIO ATÍPICO ({difficulty})...")
    
    # Configurar parâmetros por dificuldade
    if difficulty == 'easy':
        hour_range = (2, 4)  # 2h-4h da manhã
        amount_multiplier = (3, 5)
        risky_categories = ['entertainment', 'travel', 'luxury']
    elif difficulty == 'medium':
        hour_range = (1, 3)  # 1h-3h da manhã
        amount_multiplier = (2, 3)
        risky_categories = ['online_shopping', 'electronics', 'entertainment']
    else:  # hard
        hour_range = (0, 2)  # 0h-2h da manhã
        amount_multiplier = (1.5, 2.5)
        risky_categories = ['restaurant', 'gas_station', 'pharmacy']  # Podem ser 24h
    
    # Selecionar usuários aleatórios
    all_users = df['user_id'].unique()
    selected_users = np.random.choice(all_users, n_samples, replace=False)
    
    fraud_transactions = []
    
    for i, user_id in enumerate(selected_users):
        # Pegar uma transação base do usuário
        user_txs = df[df['user_id'] == user_id]
        base_tx = user_txs.sample(n=1).iloc[0]
        
        # Criar transação fraudulenta em horário atípico
        fraud_tx = base_tx.copy()
        
        # Ajustar timestamp para madrugada - mantém como datetime
        fraud_timestamp = pd.to_datetime(base_tx['timestamp']) + timedelta(days=np.random.randint(1, 7))
        unusual_hour = np.random.randint(*hour_range)
        fraud_tx['timestamp'] = fraud_timestamp.replace(hour=unusual_hour, minute=np.random.randint(0, 60))
        
        # Categoria suspeita
        fraud_tx['merchant_category'] = np.random.choice(risky_categories)
        
        # Valor elevado
        multiplier = np.random.uniform(*amount_multiplier)
        fraud_tx['amount'] = round(float(base_tx['amount']) * multiplier, 2)
        
        # Marcar como fraude
        fraud_tx['is_fraud'] = 1
        fraud_tx['fraud_type'] = 'unusual_time'
        fraud_tx['fraud_difficulty'] = difficulty
        fraud_tx['transaction_id'] = f'TX{len(df) + i:010d}'
        
        fraud_transactions.append(fraud_tx)
    
    # Adicionar fraudes ao dataframe
    fraud_df = pd.DataFrame(fraud_transactions)
    df = pd.concat([df, fraud_df], ignore_index=True)
    
    print(f"  ✓ {len(fraud_transactions)} fraudes de horário atípico injetadas!")
    
    return df


def inject_risky_merchant_fraud(df: pd.DataFrame, n_samples: int, difficulty: str) -> pd.DataFrame:
    """
    🎰 FRAUDE TIPO 5: MERCHANT SUSPEITO
    
    Simula transações em categorias de alto risco (cassinos online,
    criptomoedas, forex) que são comumente associadas a fraudes.
    
    LÓGICA:
    1. Escolher categorias de alto risco
    2. Valor alto
    3. Possivelmente localização internacional
    
    NÍVEIS DE DIFICULDADE:
    - easy: Cassino offshore + R$ 10.000 + país suspeito
    - medium: Cripto exchange + R$ 2.000 + país conhecido
    - hard: Forex legítimo + R$ 500 + Brasil (pode ser investimento)
    
    Args:
        df: DataFrame com transações
        n_samples: Número de fraudes a injetar
        difficulty: 'easy', 'medium' ou 'hard'
    
    Returns:
        DataFrame com fraudes injetadas
    """
    print(f"\n🎰 Injetando {n_samples} fraudes de MERCHANT SUSPEITO ({difficulty})...")
    
    # Configurar parâmetros por dificuldade
    if difficulty == 'easy':
        risky_categories = ['casino_online', 'gambling', 'adult_content']
        amount_range = (5000, 15000)
        foreign_location = True
        suspicious_countries = ['MT', 'CY', 'PA', 'BZ']  # Malta, Chipre, Panamá, Belize
    elif difficulty == 'medium':
        risky_categories = ['crypto_exchange', 'forex', 'binary_options']
        amount_range = (1000, 5000)
        foreign_location = np.random.rand() > 0.5
        suspicious_countries = ['US', 'GB', 'SG', 'HK']
    else:  # hard
        risky_categories = ['investment', 'forex', 'online_trading']
        amount_range = (300, 1500)
        foreign_location = False
        suspicious_countries = ['BR']
    
    # Selecionar usuários aleatórios
    all_users = df['user_id'].unique()
    selected_users = np.random.choice(all_users, n_samples, replace=False)
    
    fraud_transactions = []
    
    for i, user_id in enumerate(selected_users):
        # Pegar uma transação base do usuário
        user_txs = df[df['user_id'] == user_id]
        base_tx = user_txs.sample(n=1).iloc[0]
        
        # Criar transação fraudulenta em merchant suspeito
        fraud_tx = base_tx.copy()
        
        # Categoria de alto risco
        fraud_tx['merchant_category'] = np.random.choice(risky_categories)
        fraud_tx['merchant_name'] = f'Risky Merchant {np.random.randint(1000, 9999)}'
        
        # Valor alto
        fraud_tx['amount'] = round(np.random.uniform(*amount_range), 2)
        
        # Localização (internacional se applicable)
        if foreign_location if isinstance(foreign_location, bool) else foreign_location:
            fraud_tx['country'] = np.random.choice(suspicious_countries)
            fraud_tx['latitude'] = np.random.uniform(-90, 90)
            fraud_tx['longitude'] = np.random.uniform(-180, 180)
            fraud_tx['city'] = 'Foreign City'
        
        # Timestamp (alguns dias depois) - mantém como datetime
        fraud_tx['timestamp'] = pd.to_datetime(base_tx['timestamp']) + timedelta(days=np.random.randint(1, 10))
        
        # Marcar como fraude
        fraud_tx['is_fraud'] = 1
        fraud_tx['fraud_type'] = 'risky_merchant'
        fraud_tx['fraud_difficulty'] = difficulty
        fraud_tx['transaction_id'] = f'TX{len(df) + i:010d}'
        
        fraud_transactions.append(fraud_tx)
    
    # Adicionar fraudes ao dataframe
    fraud_df = pd.DataFrame(fraud_transactions)
    df = pd.concat([df, fraud_df], ignore_index=True)
    
    print(f"  ✓ {len(fraud_transactions)} fraudes de merchant suspeito injetadas!")
    
    return df