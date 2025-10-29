"""
predictor.py - Preditor de Fraude em Tempo Real com PostgreSQL
"""

import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import json

# Adicionar src ao path para importar build_features
sys.path.append(str(Path(__file__).parent.parent / 'src'))
from features.build_features import build_all_features, get_feature_columns


class FraudPredictor:
    """
    Classe responsável por carregar modelo e fazer predições.
    Com suporte a PostgreSQL para histórico de transações.
    """
    
    def __init__(self, model_path: str = None, scaler_path: str = None):
        """
        Inicializa o preditor carregando modelo, scaler e conexões de banco.
        """
        if model_path is None:
            model_path = Path(__file__).parent.parent / 'models' / 'isolation_forest.joblib'
        
        if scaler_path is None:
            scaler_path = Path(__file__).parent.parent / 'models' / 'scaler.joblib'
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.feature_columns = get_feature_columns()
        
        # Conectar ao PostgreSQL
        try:
            database_url = os.getenv('DATABASE_URL', 'postgresql://fraud_user:fraud_pass_2025@localhost:5432/fraud_db')
            self.db = psycopg2.connect(database_url)
            print(f"✅ PostgreSQL conectado: {database_url.split('@')[1]}")
        except Exception as e:
            print(f"⚠️  PostgreSQL não disponível: {e}")
            self.db = None
        
        # Conectar ao Redis (opcional - para cache)
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            self.redis = redis.from_url(redis_url)
            self.redis.ping()
            print(f"✅ Redis conectado: {redis_url}")
        except Exception as e:
            print(f"⚠️  Redis não disponível: {e}")
            self.redis = None
        
        print(f"Modelo carregado: {model_path}")
        print(f"Features esperadas: {len(self.feature_columns)}")
    
    
    def _get_user_history(self, user_id: str, limit: int = 100) -> pd.DataFrame:
        """
        Busca histórico de transações do usuário no PostgreSQL.

        Args:
            user_id: ID do usuário
            limit: Número máximo de transações a retornar

        Returns:
            DataFrame com histórico ou None se não encontrar
        """
        if self.db is None:
            return None

        try:
            cursor = self.db.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT 
                    user_id,
                    amount,
                    merchant_name,
                    merchant_category,
                    latitude,
                    longitude,
                    timestamp
                FROM transactions 
                WHERE user_id = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
            """, [user_id, limit])

            rows = cursor.fetchall()
            cursor.close()

            if rows:
                df = pd.DataFrame(rows)

                # ============================================================
                # CONVERTER TIPOS (PostgreSQL Decimal → Python float)
                # ============================================================
                df['amount'] = df['amount'].astype(float)
                df['latitude'] = df['latitude'].astype(float)
                df['longitude'] = df['longitude'].astype(float)

                # Garantir que timestamp é datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'])

                return df
            return None
    
        except Exception as e:
            print(f"❌ Erro ao buscar histórico: {e}")
            return None
    
    
    def _save_transaction(self, transaction_data: dict):
        """
        Salva transação no PostgreSQL.
        """
        if self.db is None:
            return
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO transactions 
                (user_id, amount, merchant_name, merchant_category, 
                 latitude, longitude, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [
                transaction_data['user_id'],
                transaction_data['amount'],
                transaction_data['merchant_name'],
                transaction_data['merchant_category'],
                transaction_data['latitude'],
                transaction_data['longitude'],
                transaction_data['timestamp']
            ])
            self.db.commit()
            cursor.close()
            print(f"✅ Transação salva: {transaction_data['user_id']}")
        
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erro ao salvar transação: {e}")
    
    
    def predict(self, transaction_data: dict, user_history: pd.DataFrame = None) -> dict:
        """
        Faz predição de fraude para uma transação.
        Busca histórico automaticamente se não fornecido.
        """
        user_id = transaction_data['user_id']
        
        # Buscar histórico do PostgreSQL se não fornecido
        if user_history is None and self.db is not None:
            user_history = self._get_user_history(user_id)
            if user_history is not None:
                print(f"📊 Histórico encontrado: {len(user_history)} transações")
        
        # Converter transação atual para DataFrame
        df = pd.DataFrame([transaction_data])
        
        # Se tiver histórico, concatenar
        if user_history is not None and not user_history.empty:
            # Inverter ordem (mais antigas primeiro)
            user_history = user_history.sort_values('timestamp')
            df = pd.concat([user_history, df], ignore_index=True)
        
        # Aplicar feature engineering
        df_features = build_all_features(df)
        
        # Pegar apenas a última linha
        current_tx = df_features.iloc[[-1]].copy()
        
        # Selecionar features do modelo
        X = current_tx[self.feature_columns].copy()
        
        # Preencher NaN com valores padrão
        X = X.fillna({
            'time_since_last_tx_sec': 86400,
            'user_avg_amount_7d': X['amount'].iloc[0] if 'amount' in X.columns else 0,
            'user_std_amount_7d': 0,
            'distance_from_home_km': 0,
            'velocity_kmh': 0,
            'spending_zscore': 0,
            'tx_count_rolling_1h_user': 0,
            'distinct_merchants_rolling_1h_user': 0,
            'is_new_merchant_category_user': 1,
            'rapid_sequence_flag': 0,
            'value_anomaly_flag': 0,
            'combined_anomaly_score': 0
        })
        
        # Garantir que não há mais NaN
        X = X.fillna(0)
        
        # Normalizar
        X_scaled = self.scaler.transform(X)
        
        # Predição
        prediction = self.model.predict(X_scaled)[0]
        anomaly_score = self.model.score_samples(X_scaled)[0]
        
        # Classificar risco
        risk_level, recommendation = self._classify_risk(
            anomaly_score, 
            prediction,
            current_tx
        )
        
        # Salvar transação no banco
        self._save_transaction(transaction_data)
        
        # Funções auxiliares para conversão segura
        def safe_float(value):
            try:
                val = float(value)
                return 0.0 if pd.isna(val) else val
            except:
                return 0.0
        
        def safe_int(value):
            try:
                val = float(value)
                return 0 if pd.isna(val) else int(val)
            except:
                return 0
        
        return {
            'anomaly_score': float(anomaly_score),
            'is_anomaly': bool(prediction == -1),
            'risk_level': risk_level,
            'recommendation': recommendation,
            'features': {
                'velocity_kmh': safe_float(current_tx['velocity_kmh'].iloc[0]),
                'distance_from_home_km': safe_float(current_tx['distance_from_home_km'].iloc[0]),
                'spending_zscore': safe_float(current_tx['spending_zscore'].iloc[0]),
                'tx_count_1h': safe_int(current_tx['tx_count_rolling_1h_user'].iloc[0]),
                'distinct_merchants_1h': safe_int(current_tx['distinct_merchants_rolling_1h_user'].iloc[0])
            }
        }
    
    
    def _classify_risk(self, anomaly_score: float, prediction: int, features: pd.DataFrame) -> tuple:
        """
        Classifica nível de risco baseado em score e features.
        """
        # Extrair features críticas com tratamento de NaN
        velocity = float(features['velocity_kmh'].iloc[0]) if not pd.isna(features['velocity_kmh'].iloc[0]) else 0
        distance = float(features['distance_from_home_km'].iloc[0]) if not pd.isna(features['distance_from_home_km'].iloc[0]) else 0
        tx_count = int(features['tx_count_rolling_1h_user'].iloc[0]) if not pd.isna(features['tx_count_rolling_1h_user'].iloc[0]) else 0
        distinct_merchants = int(features['distinct_merchants_rolling_1h_user'].iloc[0]) if not pd.isna(features['distinct_merchants_rolling_1h_user'].iloc[0]) else 0
        
        # CRÍTICO: Múltiplos sinais fortes
        critical_signals = 0
        if velocity > 800:
            critical_signals += 1
        if distance > 5000:
            critical_signals += 1
        if tx_count > 5 and distinct_merchants > 3:
            critical_signals += 1
        
        if critical_signals >= 2:
            return "CRÍTICO", "BLOQUEAR transação e LIGAR para cliente imediatamente"
        
        # ALTO: Anomalia detectada
        if prediction == -1:
            if anomaly_score < -0.2:
                return "ALTO", "Enviar para FILA DE ANÁLISE HUMANA (prioridade alta)"
            else:
                return "MÉDIO", "Enviar para FILA DE ANÁLISE HUMANA (prioridade normal)"
        
        # BAIXO: Normal
        return "BAIXO", "APROVAR automaticamente"


    def predict_batch(self, transactions: list) -> list:
        """
        Predição em lote.
        """
        results = []
        for tx in transactions:
            result = self.predict(tx)
            results.append(result)
        
        return results