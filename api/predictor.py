"""
predictor.py - Preditor de Fraude em Tempo Real
"""

import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Adicionar src ao path para importar build_features
sys.path.append(str(Path(__file__).parent.parent / 'src'))
from features.build_features import build_all_features, get_feature_columns


class FraudPredictor:
    """
    Classe responsável por carregar modelo e fazer predições.
    """
    
    def __init__(self, model_path: str = None, scaler_path: str = None):
        """
        Inicializa o preditor carregando modelo e scaler.
        
        Args:
            model_path: Caminho para isolation_forest.joblib
            scaler_path: Caminho para scaler.joblib
        """
        if model_path is None:
            model_path = Path(__file__).parent.parent / 'models' / 'isolation_forest.joblib'
        
        if scaler_path is None:
            scaler_path = Path(__file__).parent.parent / 'models' / 'scaler.joblib'
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.feature_columns = get_feature_columns()
        
        print(f"Modelo carregado: {model_path}")
        print(f"Features esperadas: {len(self.feature_columns)}")
    
    
    def predict(self, transaction_data: dict, user_history: pd.DataFrame = None) -> dict:
        """
        Faz predição de fraude para uma transação.
        
        Args:
            transaction_data: Dicionário com dados da transação
            user_history: DataFrame com histórico do usuário (opcional)
        
        Returns:
            dict com:
                - anomaly_score: Score de anomalia (-1 a 1, quanto mais negativo, mais anômalo)
                - is_anomaly: Boolean (True = fraude suspeita)
                - risk_level: "BAIXO" | "MÉDIO" | "ALTO" | "CRÍTICO"
                - recommendation: Ação recomendada
                - features: Features calculadas (debug)
        """
        # Converter para DataFrame
        df = pd.DataFrame([transaction_data])
        
        # Se tiver histórico, concatenar (para calcular features temporais)
        if user_history is not None:
            df = pd.concat([user_history, df], ignore_index=True)
        
        # Aplicar feature engineering
        df_features = build_all_features(df)
        
        # Pegar apenas a última linha (transação atual)
        current_tx = df_features.iloc[[-1]]
        
        # Selecionar features do modelo
        X = current_tx[self.feature_columns]
        
        # Normalizar
        X_scaled = self.scaler.transform(X)
        
        # Predição
        prediction = self.model.predict(X_scaled)[0]  # -1 = anomalia, 1 = normal
        anomaly_score = self.model.score_samples(X_scaled)[0]  # Score contínuo
        
        # Classificar risco
        risk_level, recommendation = self._classify_risk(
            anomaly_score, 
            prediction,
            current_tx
        )
        
        return {
            'anomaly_score': float(anomaly_score),
            'is_anomaly': bool(prediction == -1),
            'risk_level': risk_level,
            'recommendation': recommendation,
            'features': {
                'velocity_kmh': float(current_tx['velocity_kmh'].iloc[0]),
                'distance_from_home_km': float(current_tx['distance_from_home_km'].iloc[0]),
                'spending_zscore': float(current_tx['spending_zscore'].iloc[0]),
                'tx_count_1h': int(current_tx['tx_count_rolling_1h_user'].iloc[0]),
                'distinct_merchants_1h': int(current_tx['distinct_merchants_rolling_1h_user'].iloc[0])
            }
        }
    
    
    def _classify_risk(self, anomaly_score: float, prediction: int, features: pd.DataFrame) -> tuple:
        """
        Classifica nível de risco baseado em score e features.
        
        LÓGICA DE NEGÓCIO:
        - CRÍTICO: Múltiplos sinais fortes (bloquear e ligar para cliente)
        - ALTO: Anomalia clara (enviar para fila de análise urgente)
        - MÉDIO: Anomalia leve (enviar para fila de análise normal)
        - BAIXO: Normal (aprovar automaticamente)
        """
        # Extrair features críticas
        velocity = features['velocity_kmh'].iloc[0]
        distance = features['distance_from_home_km'].iloc[0]
        tx_count = features['tx_count_rolling_1h_user'].iloc[0]
        distinct_merchants = features['distinct_merchants_rolling_1h_user'].iloc[0]
        
        # CRÍTICO: Múltiplos sinais fortes
        critical_signals = 0
        if velocity > 800:  # Velocidade de avião
            critical_signals += 1
        if distance > 5000:  # Outro país
            critical_signals += 1
        if tx_count > 5 and distinct_merchants > 3:  # Card testing agressivo
            critical_signals += 1
        
        if critical_signals >= 2:
            return "CRÍTICO", "BLOQUEAR transação e LIGAR para cliente imediatamente"
        
        # ALTO: Anomalia detectada pelo modelo
        if prediction == -1:
            if anomaly_score < -0.2:  # Score muito negativo
                return "ALTO", "Enviar para FILA DE ANÁLISE HUMANA (prioridade alta)"
            else:
                return "MÉDIO", "Enviar para FILA DE ANÁLISE HUMANA (prioridade normal)"
        
        # BAIXO: Normal
        return "BAIXO", "APROVAR automaticamente"


    def predict_batch(self, transactions: list) -> list:
        """
        Predição em lote (útil para processar múltiplas transações).
        """
        results = []
        for tx in transactions:
            result = self.predict(tx)
            results.append(result)
        
        return results