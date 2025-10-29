"""
app.py - API Flask para Detecção de Fraude
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from api.predictor import FraudPredictor
from api.schemas import TransactionInput, PredictionOutput
from pydantic import ValidationError
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
CORS(app)

# Inicializar preditor (carrega modelo na inicialização)
try:
    predictor = FraudPredictor()
    logger.info("Preditor inicializado com sucesso")
except Exception as e:
    logger.error(f"Erro ao inicializar preditor: {e}")
    predictor = None


@app.route('/', methods=['GET'])
def home():
    """Endpoint de health check."""
    return jsonify({
        'service': 'Fraud Detection API',
        'version': '1.0.0',
        'status': 'running',
        'model_loaded': predictor is not None
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check detalhado."""
    if predictor is None:
        return jsonify({'status': 'unhealthy', 'reason': 'Model not loaded'}), 503
    
    return jsonify({
        'status': 'healthy',
        'model': 'Isolation Forest',
        'features': len(predictor.feature_columns)
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint principal: predição de fraude.
    """
    if predictor is None:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        # Validar entrada
        data = request.get_json()
        transaction = TransactionInput(**data)
        
        # Fazer predição
        result = predictor.predict(transaction.dict())
        
        # Validar saída
        output = PredictionOutput(**result)
        
        logger.info(f"Predição realizada - User: {transaction.user_id}, Risk: {output.risk_level}")
        
        return jsonify(output.dict()), 200
    
    except ValidationError as e:
        logger.warning(f"Erro de validação: {e}")
        return jsonify({'error': 'Invalid input', 'details': e.errors()}), 400
    
    except Exception as e:
        logger.error(f"Erro na predição: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """
    Predição em lote (múltiplas transações).
    """
    if predictor is None:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        data = request.get_json()
        transactions = data.get('transactions', [])
        
        if not transactions:
            return jsonify({'error': 'No transactions provided'}), 400
        
        # Validar todas as transações
        validated_txs = []
        for tx in transactions:
            validated_txs.append(TransactionInput(**tx).dict())
        
        # Fazer predições
        results = predictor.predict_batch(validated_txs)
        
        logger.info(f"Predição em lote realizada - {len(results)} transações")
        
        return jsonify({'predictions': results}), 200
    
    except ValidationError as e:
        return jsonify({'error': 'Invalid input', 'details': e.errors()}), 400
    
    except Exception as e:
        logger.error(f"Erro na predição em lote: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)