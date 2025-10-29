# Imagem base Python 3.11 slim (menor tamanho)
FROM python:3.11-slim

# Metadados
LABEL maintainer="pedro@frauddetection.com"
LABEL description="Fraud Detection API - Real-time anomaly detection"

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements DA API e instalar dependências
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Copiar código da aplicação
COPY api/ ./api/
COPY src/ ./src/
COPY models/ ./models/

# Criar usuário não-root (segurança)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 5000

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=api.app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Comando de inicialização (usar gunicorn para produção)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "api.app:app"]