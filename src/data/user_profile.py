"""
user_profile.py - Modelagem de perfis de usuário para geração de transações realistas
Fraud Detection Project - Fase 2
"""

from faker import Faker
import numpy as np
from datetime import time


class UserProfile:
    """
    Representa um perfil de usuário com padrões de comportamento realistas.
    
    Esta classe é o segredo para gerar transações 'normais' convincentes.
    Cada usuário tem:
    - Localização home (cidade/país)
    - Faixa salarial (que define padrão de gastos)
    - Horários preferenciais de compra
    - Categorias favoritas de merchant
    """
    
    def __init__(self, user_id, faker_instance):
        """
        Inicializa um perfil de usuário com características aleatórias mas consistentes.
        
        Args:
            user_id (int): Identificador único do usuário
            faker_instance (Faker): Instância do Faker para gerar dados
        """
        self.faker = faker_instance
        self.user_id = user_id
        
        # Localização home (85% Brasil, 15% outros países)
        if np.random.rand() < 0.85:
            self.home_country = 'BR'
            self.home_city = self.faker.city()
            self.home_lat = float(self.faker.latitude())  # Converter Decimal para float
            self.home_lon = float(self.faker.longitude())  # Converter Decimal para float
        else:
            # Usuários internacionais (expatriados, turistas frequentes)
            countries = ['US', 'UK', 'DE', 'FR', 'ES', 'IT', 'JP', 'CN']
            self.home_country = np.random.choice(countries)
            self.home_city = self.faker.city()
            self.home_lat = float(self.faker.latitude())  # Converter Decimal para float
            self.home_lon = float(self.faker.longitude())  # Converter Decimal para float
        
        # Faixa salarial (define padrão de gastos)
        # Distribuição realista: 60% classe média, 30% média-alta, 10% alta
        salary_tier = np.random.choice(['low', 'medium', 'high'], p=[0.6, 0.3, 0.1])
        
        if salary_tier == 'low':
            self.avg_transaction = np.random.uniform(50, 200)
            self.std_transaction = self.avg_transaction * 0.5
        elif salary_tier == 'medium':
            self.avg_transaction = np.random.uniform(200, 800)
            self.std_transaction = self.avg_transaction * 0.6
        else:  # high
            self.avg_transaction = np.random.uniform(800, 3000)
            self.std_transaction = self.avg_transaction * 0.7
        
        # Horários preferenciais (padrões humanos)
        # Pico 1: Horário de almoço (12h-14h) - peso 0.3
        # Pico 2: Após o trabalho (18h-21h) - peso 0.4
        # Normal: Horário comercial (9h-18h) - peso 0.2
        # Baixo: Madrugada (0h-6h) - peso 0.1
        self.peak_hours = {
            'lunch': (12, 14),      # Almoço
            'evening': (18, 21),    # Noite
            'business': (9, 18),    # Comercial
            'night': (0, 6)         # Madrugada (suspeito!)
        }
        
        # Categorias favoritas de merchant (cada usuário tem preferências)
        all_categories = [
            'grocery', 'restaurant', 'gas_station', 'pharmacy', 
            'clothing', 'electronics', 'entertainment', 'travel',
            'online_shopping', 'utilities', 'health', 'education'
        ]
        
        # Cada usuário tem 3-5 categorias favoritas (80% das transações)
        n_favorites = np.random.randint(3, 6)
        self.favorite_categories = np.random.choice(all_categories, n_favorites, replace=False).tolist()
        self.all_categories = all_categories
        
        # Frequência de transações (transações/mês)
        # Distribuição: 40% baixa, 40% média, 20% alta
        freq_tier = np.random.choice(['low', 'medium', 'high'], p=[0.4, 0.4, 0.2])
        
        if freq_tier == 'low':
            self.transactions_per_month = np.random.randint(5, 15)
        elif freq_tier == 'medium':
            self.transactions_per_month = np.random.randint(15, 40)
        else:  # high
            self.transactions_per_month = np.random.randint(40, 100)
    
    def sample_transaction_amount(self):
        """
        Amostra um valor de transação realista para este usuário.
        Usa distribuição log-normal (valores pequenos são mais comuns).
        
        Returns:
            float: Valor da transação em R$
        """
        amount = np.random.lognormal(
            mean=np.log(self.avg_transaction),
            sigma=0.5
        )
        
        # Clamp entre R$ 5 e R$ 10.000 (evitar valores irrealistas)
        return np.clip(amount, 5, 10000)
    
    def sample_transaction_hour(self):
        """
        Amostra um horário de transação baseado nos padrões do usuário.
        
        Returns:
            int: Hora do dia (0-23)
        """
        # Probabilidades de cada período
        period = np.random.choice(
            ['lunch', 'evening', 'business', 'night'],
            p=[0.3, 0.4, 0.2, 0.1]
        )
        
        start_hour, end_hour = self.peak_hours[period]
        
        # Se o período cruza meia-noite (ex: 22h-2h)
        if start_hour > end_hour:
            if np.random.rand() < 0.5:
                return np.random.randint(start_hour, 24)
            else:
                return np.random.randint(0, end_hour + 1)
        else:
            return np.random.randint(start_hour, end_hour + 1)
    
    def sample_merchant_category(self):
        """
        Amostra uma categoria de merchant baseada nas preferências do usuário.
        
        Returns:
            str: Categoria do merchant
        """
        # 80% das vezes, escolhe das categorias favoritas
        if np.random.rand() < 0.8:
            return np.random.choice(self.favorite_categories)
        else:
            # 20% das vezes, explora outras categorias
            other_categories = [cat for cat in self.all_categories 
                              if cat not in self.favorite_categories]
            return np.random.choice(other_categories) if other_categories else np.random.choice(self.all_categories)
    
    def sample_location(self, distance_from_home_km=0):
        """
        Amostra uma localização geográfica.
        
        Args:
            distance_from_home_km (float): Distância aproximada da localização home (0 = em casa)
        
        Returns:
            tuple: (latitude, longitude, city, country)
        """
        if distance_from_home_km == 0:
            # Transação perto de casa (95% das transações normais)
            # Adiciona ruído de ~5km (variação dentro da cidade)
            lat_noise = np.random.normal(0, 0.05)
            lon_noise = np.random.normal(0, 0.05)
            
            return (
                self.home_lat + lat_noise,
                self.home_lon + lon_noise,
                self.home_city,
                self.home_country
            )
        else:
            # Transação em viagem (5% das transações normais)
            # Gera uma localização aleatória
            return (
                float(self.faker.latitude()),  # Converter Decimal para float
                float(self.faker.longitude()),  # Converter Decimal para float
                self.faker.city(),
                np.random.choice(['BR', 'US', 'UK', 'DE', 'FR', 'ES', 'AR', 'UY', 'CL'])
            )
    
    def __repr__(self):
        return (f"UserProfile(id={self.user_id}, home={self.home_city}/{self.home_country}, "
                f"avg_tx=${self.avg_transaction:.2f}, freq={self.transactions_per_month}/month)")