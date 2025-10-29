"""
schemas.py - Schemas de validação para API
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class TransactionInput(BaseModel):
    """
    Schema para entrada de transação.
    """
    user_id: str = Field(..., description="ID do usuário")
    amount: float = Field(..., gt=0, description="Valor da transação (R$)")
    merchant_name: str = Field(..., description="Nome do estabelecimento")
    merchant_category: str = Field(..., description="Categoria do estabelecimento")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    timestamp: Optional[str] = Field(None, description="Timestamp (ISO format)")
    
    @field_validator('timestamp', mode='before')
    @classmethod
    def set_timestamp(cls, v):
        """Se timestamp não fornecido, usar timestamp atual."""
        return v or datetime.now().isoformat()
    
    class Config:
        json_schema_extra = {  # <-- Changed from schema_extra
            "example": {
                "user_id": "user_12345",
                "amount": 1500.00,
                "merchant_name": "Loja de Eletrônicos XYZ",
                "merchant_category": "electronics",
                "latitude": -23.5505,
                "longitude": -46.6333,
                "timestamp": "2025-10-28T14:30:00"
            }
        }


class PredictionOutput(BaseModel):
    """
    Schema para saída de predição.
    """
    anomaly_score: float
    is_anomaly: bool
    risk_level: str
    recommendation: str
    features: dict
    
    class Config:
        json_schema_extra = {  # <-- Changed from schema_extra
            "example": {
                "anomaly_score": -0.15,
                "is_anomaly": True,
                "risk_level": "ALTO",
                "recommendation": "Enviar para FILA DE ANÁLISE HUMANA (prioridade alta)",
                "features": {
                    "velocity_kmh": 450.5,
                    "distance_from_home_km": 1200.0,
                    "spending_zscore": 2.5,
                    "tx_count_1h": 1,
                    "distinct_merchants_1h": 0
                }
            }
        }