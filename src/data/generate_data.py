"""
generate_data.py - Gerador de dados sintéticos para detecção de fraude
Fraud Detection Project - Fase 2

Este script é o coração do projeto. Ele cria:
1. 300K transações (99.8% normais, 0.2% fraude)
   - 100K para treino
   - 200K para teste
   - Decisão: Gerar apenas o necessário (pragmatismo > volume)
2. 2K transações fraudulentas de 5 tipos diferentes em 3 níveis de dificuldade

Por que 300K e não 1M?
- Eficiência: Geração mais rápida (~1.5min vs ~5min)
- Deploy: Cabe confortavelmente na t2.micro (1GB RAM)
- Foco: O valor está na qualidade das fraudes, não no volume
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
from typing import List, Tuple
import sys
import os

# Adicionar o diretório raiz ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from user_profile import UserProfile


class FraudDataGenerator:
    """
    Gerador de dataset sintético para detecção de fraude em tempo real.
    
    Esta classe implementa a geração de transações realistas e a injeção
    controlada de fraudes em múltiplos níveis de dificuldade.
    """
    
    def __init__(
        self,
        n_transactions: int = 1_000_000,
        n_users: int = 50_000,
        fraud_ratio: float = 0.002,
        start_date: str = '2024-01-01',
        end_date: str = '2024-12-31',
        random_seed: int = 42
    ):
        """
        Inicializa o gerador de dados.
        
        Args:
            n_transactions: Número total de transações (normal + fraude)
            n_users: Número de usuários únicos
            fraud_ratio: Proporção de fraudes (0.002 = 0.2%)
            start_date: Data inicial do período
            end_date: Data final do período
            random_seed: Seed para reprodutibilidade
        """
        # Configuração
        np.random.seed(random_seed)
        Faker.seed(random_seed)
        
        self.faker = Faker('pt_BR')
        self.n_transactions = n_transactions
        self.n_users = n_users
        self.fraud_ratio = fraud_ratio
        self.n_frauds = int(n_transactions * fraud_ratio)
        self.n_normal = n_transactions - self.n_frauds
        
        # Datas
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.date_range_days = (self.end_date - self.start_date).days
        
        print(f"📊 Configuração do Gerador:")
        print(f"  - Total de transações: {n_transactions:,}")
        print(f"  - Transações normais: {self.n_normal:,} (99.8%)")
        print(f"  - Transações fraudulentas: {self.n_frauds:,} (0.2%)")
        print(f"  - Usuários únicos: {n_users:,}")
        print(f"  - Período: {start_date} a {end_date}")
        
        # Criar perfis de usuários (PRÉ-PROCESSAMENTO)
        print(f"\n👥 Criando perfis de {n_users:,} usuários...")
        self.users = self._create_user_profiles()
        print(f"✓ Perfis criados com sucesso!")
        
        # Dataframe que será preenchido
        self.df = None
        
    def _create_user_profiles(self) -> List[UserProfile]:
        """
        Cria perfis de usuário com características consistentes.
        
        Returns:
            Lista de objetos UserProfile
        """
        users = []
        for user_id in range(self.n_users):
            users.append(UserProfile(user_id, self.faker))
            
            # Progress bar a cada 10k usuários
            if (user_id + 1) % 5000 == 0:
                print(f"  - Criados {user_id + 1:,}/{self.n_users:,} perfis...")
        
        return users
    
    def generate_normal_transactions(self) -> pd.DataFrame:
        """
        Gera transações normais com padrões humanos realistas.
        
        LÓGICA:
        1. Para cada transação, sorteia um usuário (com replacement)
        2. Usa o perfil do usuário para gerar valores realistas
        3. 95% das transações são perto de casa, 5% em viagem
        
        Returns:
            DataFrame com transações normais
        """
        print(f"\n💳 Gerando {self.n_normal:,} transações normais...")
        
        transactions = []
        
        for i in range(self.n_normal):
            # Sortear usuário (distribuição uniforme)
            user = np.random.choice(self.users)
            
            # Gerar timestamp aleatório no período
            random_days = np.random.randint(0, self.date_range_days)
            transaction_date = self.start_date + timedelta(days=random_days)
            
            # Adicionar hora do dia (baseado no perfil do usuário)
            hour = user.sample_transaction_hour()
            minute = np.random.randint(0, 60)
            second = np.random.randint(0, 60)
            
            timestamp = transaction_date.replace(hour=hour, minute=minute, second=second)
            
            # Valor da transação (baseado no perfil)
            amount = user.sample_transaction_amount()
            
            # Categoria do merchant (baseado nas preferências)
            merchant_category = user.sample_merchant_category()
            
            # Localização (95% perto de casa, 5% em viagem)
            if np.random.rand() < 0.95:
                lat, lon, city, country = user.sample_location(distance_from_home_km=0)
            else:
                # Viagem (distância aleatória)
                lat, lon, city, country = user.sample_location(distance_from_home_km=np.random.uniform(100, 5000))
            
            # Merchant name (fake)
            merchant_name = self.faker.company()
            
            # Card last 4 digits (usuário pode ter 1-3 cartões)
            n_cards = np.random.randint(1, 4)
            card_last4 = str(np.random.randint(1000, 9999))
            
            transaction = {
                'transaction_id': f'TX{i:010d}',
                'user_id': f'USER{user.user_id:06d}',
                'timestamp': timestamp,
                'amount': round(amount, 2),
                'merchant_name': merchant_name,
                'merchant_category': merchant_category,
                'latitude': round(lat, 6),
                'longitude': round(lon, 6),
                'city': city,
                'country': country,
                'card_last4': card_last4,
                'is_fraud': 0,
                'fraud_type': None,
                'fraud_difficulty': None
            }
            
            transactions.append(transaction)
            
            # Progress bar a cada 100k transações
            if (i + 1) % 10000 == 0:
                print(f"  - Geradas {i + 1:,}/{self.n_normal:,} transações...")
        
        df = pd.DataFrame(transactions)
        
        # Ordenar por timestamp (para facilitar injeção de fraudes temporais)
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        print(f"✓ Transações normais geradas com sucesso!")
        print(f"  - Período: {df['timestamp'].min()} a {df['timestamp'].max()}")
        print(f"  - Valor médio: R$ {df['amount'].mean():.2f}")
        print(f"  - Valor total: R$ {df['amount'].sum():,.2f}")
        
        return df
    
    def save_data(self, output_path: str = '../../data/raw/transactions.csv'):
        """
        Salva o dataset final em CSV.
        
        Args:
            output_path: Caminho para salvar o CSV
        """
        if self.df is None:
            raise ValueError("Nenhum dado para salvar. Execute generate_normal_transactions() primeiro.")
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Salvar CSV
        self.df.to_csv(output_path, index=False)
        
        print(f"\n💾 Dataset salvo em: {output_path}")
        print(f"  - Total de linhas: {len(self.df):,}")
        print(f"  - Tamanho do arquivo: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
        
        # Salvar gabarito separado (apenas fraudes)
        fraud_df = self.df[self.df['is_fraud'] == 1].copy()
        if len(fraud_df) > 0:
            gabarito_path = output_path.replace('.csv', '_gabarito.csv')
            fraud_df.to_csv(gabarito_path, index=False)
            print(f"  - Gabarito salvo em: {gabarito_path}")
            print(f"    - Total de fraudes: {len(fraud_df):,}")


# ==============================================================================
# FUNÇÕES DE INJEÇÃO DE FRAUDE (Serão implementadas na próxima parte)
# ==============================================================================

def inject_teleport_fraud(df: pd.DataFrame, n_samples: int, difficulty: str) -> pd.DataFrame:
    """
    Injeta fraude do tipo TELEPORTE GEOGRÁFICO.
    
    LÓGICA:
    - Pegar transações de um usuário
    - Encontrar a próxima transação daquele usuário
    - Mudar a localização para um país/cidade diferente
    - Manter o intervalo de tempo curto (<10min para difícil, <1h para médio, <5h para fácil)
    
    Args:
        df: DataFrame com transações
        n_samples: Quantidade de fraudes a injetar
        difficulty: 'easy', 'medium', 'hard'
    
    Returns:
        DataFrame com fraudes injetadas
    """
    print(f"\n🌍 Injetando {n_samples} fraudes de TELEPORTE ({difficulty})...")
    # Implementação na próxima parte
    return df


def inject_sudden_spending_fraud(df: pd.DataFrame, n_samples: int, difficulty: str) -> pd.DataFrame:
    """
    Injeta fraude do tipo GASTO SÚBITO.
    
    LÓGICA:
    - Calcular média de gasto do usuário nos últimos 30 dias
    - Criar transação com valor muito acima da média
    - Fácil: 100x maior | Médio: 10x maior | Difícil: 3x maior
    """
    print(f"\n💸 Injetando {n_samples} fraudes de GASTO SÚBITO ({difficulty})...")
    # Implementação na próxima parte
    return df


def inject_card_testing_fraud(df: pd.DataFrame, n_samples: int, difficulty: str) -> pd.DataFrame:
    """
    Injeta fraude do tipo SONDAGEM DE CARTÃO.
    
    LÓGICA:
    - Criar múltiplas transações pequenas (R$ 1-10) em poucos segundos
    - Simula fraudador testando se cartão roubado funciona
    """
    print(f"\n🔍 Injetando {n_samples} fraudes de SONDAGEM ({difficulty})...")
    # Implementação na próxima parte
    return df


def inject_unusual_time_fraud(df: pd.DataFrame, n_samples: int, difficulty: str) -> pd.DataFrame:
    """
    Injeta fraude do tipo HORÁRIO ATÍPICO.
    
    LÓGICA:
    - Usuário faz transação em horário incomum (madrugada)
    - Em categoria que não costuma usar
    """
    print(f"\n🌙 Injetando {n_samples} fraudes de HORÁRIO ATÍPICO ({difficulty})...")
    # Implementação na próxima parte
    return df


def inject_risky_merchant_fraud(df: pd.DataFrame, n_samples: int, difficulty: str) -> pd.DataFrame:
    """
    Injeta fraude do tipo MERCHANT SUSPEITO.
    
    LÓGICA:
    - Transação em categoria de alto risco (cassino, cripto, forex)
    - Valor alto
    - Localização internacional
    """
    print(f"\n🎰 Injetando {n_samples} fraudes de MERCHANT SUSPEITO ({difficulty})...")
    # Implementação na próxima parte
    return df


# ==============================================================================
# SCRIPT PRINCIPAL
# ==============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("GERADOR DE DADOS SINTÉTICOS - FRAUD DETECTION")
    print("=" * 80)
    
    # Inicializar gerador
    # 300K transações: 100K treino + 200K teste (exatamente o que precisamos!)
    # 15K usuários: proporção realista de ~20 transações/usuário
    generator = FraudDataGenerator(
        n_transactions=300_000,
        n_users=15_000,
        fraud_ratio=0.002,
        start_date='2024-01-01',
        end_date='2024-12-31',
        random_seed=42
    )
    
    # Gerar transações normais
    generator.df = generator.generate_normal_transactions()
    
    # Salvar dados
    generator.save_data()
    
    print("\n" + "=" * 80)
    print("✓ GERAÇÃO DE DADOS CONCLUÍDA COM SUCESSO!")
    print("=" * 80)