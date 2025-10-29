# 🛡️ Real-Time Fraud Detection System

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5.2-orange.svg)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Sistema completo de detecção de fraude em tempo real usando Isolation Forest e feature engineering avançado. Detecta teleporte geográfico, card testing, gastos súbitos e padrões anômalos com 71.6% de recall.**

---

## 🎯 **Destaques do Projeto**

- ✅ **300.135 transações sintéticas** realistas geradas com Faker
- ✅ **5 tipos de fraude** injetados com 3 níveis de dificuldade (easy/medium/hard)
- ✅ **17 features contextuais** (velocity, distance, spending patterns, temporal patterns)
- ✅ **71.6% recall** no modelo (358/500 fraudes detectadas)
- ✅ **API REST Flask** com PostgreSQL para histórico de transações
- ✅ **Docker Compose** para orquestração completa
- ✅ **100% dos testes passando** (7/7 testes end-to-end)

---

## 📊 **Performance do Modelo**

### **Métricas Gerais**

| Métrica | Valor |
|---------|-------|
| **Recall** | **71.6%** (358/500 fraudes detectadas) |
| **Falsos Positivos** | 0.89% (1.781/200.000 transações normais) |
| **Precision** | 16.8% |
| **F1-Score** | 0.27 |

### **Detecção por Tipo de Fraude**

| Tipo de Fraude | Recall | Status |
|----------------|--------|--------|
| **Card Testing** 🔥 | 83.8% (145/173) | ✅ Excelente |
| **Teleporte** 🔥 | 83.5% (66/79) | ✅ Excelente |
| **Risky Merchant** 🔥 | 80.7% (67/83) | ✅ Excelente |
| **Sudden Spending** | 70.7% (58/82) | ⚠️ Bom |
| **Unusual Time** | 26.5% (22/83) | ❌ Requer melhoria |

### **Detecção por Dificuldade**

- **Easy:** 87.1% (210/241) ✅
- **Medium:** 66.7% (122/183) ⚠️
- **Hard:** 34.2% (26/76) ❌

---

## 🚀 **Como Executar o Projeto**

### **Pré-requisitos**

- [Docker Desktop](https://www.docker.com/products/docker-desktop) instalado e rodando
- [Git](https://git-scm.com/) instalado
- [Python 3.11+](https://www.python.org/downloads/) (apenas para executar testes locais)

---

### **Passo 1: Clone o Repositório**
```bash
git clone https://github.com/seu-usuario/fraud-detection-realtime.git
cd fraud-detection-realtime
```

---

### **Passo 2: Inicie os Serviços com Docker Compose**
```bash
# Subir todos os serviços (API + PostgreSQL + Redis)
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f
```

**Aguarde até ver esta mensagem nos logs:**
```
fraud-api | ✅ PostgreSQL conectado: postgres:5432/fraud_db
fraud-api | ✅ Redis conectado: redis://redis:6379/0
fraud-api | Modelo carregado: /app/models/isolation_forest.joblib
fraud-api | Preditor inicializado com sucesso
```

**Pressione `Ctrl+C` para sair dos logs.**

---

### **Passo 3: Teste a API**

#### **3.1. Health Check (via navegador ou curl)**
```bash
# Linux/Mac
curl http://localhost:5000/health

# Windows (PowerShell)
Invoke-WebRequest -Uri http://localhost:5000/health
```

**Ou abra no navegador:** [http://localhost:5000/health](http://localhost:5000/health)

**Resposta esperada:**
```json
{
  "status": "healthy",
  "model": "Isolation Forest",
  "features": 17
}
```

---

#### **3.2. Predição de Fraude (exemplo: transação normal)**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_normal_001",
    "amount": 150.00,
    "merchant_name": "Supermercado Pão de Açúcar",
    "merchant_category": "grocery",
    "latitude": -23.5505,
    "longitude": -46.6333
  }'
```

**Resposta esperada:**
```json
{
  "anomaly_score": 0.05,
  "is_anomaly": false,
  "risk_level": "BAIXO",
  "recommendation": "APROVAR automaticamente",
  "features": {
    "velocity_kmh": 15.3,
    "distance_from_home_km": 2.5,
    "spending_zscore": 0.2,
    "tx_count_1h": 1,
    "distinct_merchants_1h": 0
  }
}
```

---

#### **3.3. Exemplo: Detecção de Teleporte (CRÍTICO)**
```bash
# Primeira transação em São Paulo
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_traveler_001",
    "amount": 200.00,
    "merchant_name": "Restaurante SP",
    "merchant_category": "food",
    "latitude": -23.5505,
    "longitude": -46.6333
  }'

# Aguardar 2 segundos
sleep 2

# Segunda transação em Tóquio (30 minutos depois - IMPOSSÍVEL!)
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_traveler_001",
    "amount": 300.00,
    "merchant_name": "Restaurante Tokyo",
    "merchant_category": "food",
    "latitude": 35.6762,
    "longitude": 139.6503
  }'
```

**Resposta esperada (FRAUDE DETECTADA):**
```json
{
  "anomaly_score": -0.45,
  "is_anomaly": true,
  "risk_level": "CRÍTICO",
  "recommendation": "BLOQUEAR transação e LIGAR para cliente imediatamente",
  "features": {
    "velocity_kmh": 18500.5,  // ← Velocidade impossível!
    "distance_from_home_km": 18400.2,
    "spending_zscore": 1.2,
    "tx_count_1h": 2,
    "distinct_merchants_1h": 1
  }
}
```

---

### **Passo 4: Execute a Bateria de Testes Completa**
```bash
# Instalar biblioteca de requisições HTTP
pip install requests

# Executar todos os testes (7 testes)
python test_api.py
```

**Resultado esperado:**
```
================================================================================
🧪 RESUMO DOS TESTES
================================================================================

✅ Testes Passaram: 7/7
❌ Testes Falharam: 0/7
📊 Taxa de Sucesso: 100.0%

🎉 TODOS OS TESTES PASSARAM! API está funcionando perfeitamente!
```

**Testes executados:**
1. ✅ Health Check
2. ✅ Transação Normal (BAIXO risco)
3. ✅ Card Testing (ALTO risco)
4. ✅ Teleporte (CRÍTICO)
5. ✅ Gasto Súbito (MÉDIO/ALTO risco)
6. ✅ Validação de Entrada (erro 400)
7. ✅ Predição em Lote

---

### **Passo 5: Explorar o Banco de Dados (Opcional)**
```bash
# Conectar ao PostgreSQL
docker exec -it fraud-postgres psql -U fraud_user -d fraud_db

# Dentro do PostgreSQL, executar queries:

# Ver total de transações
SELECT COUNT(*) FROM transactions;

# Ver transações por usuário
SELECT user_id, COUNT(*) as total 
FROM transactions 
GROUP BY user_id 
ORDER BY total DESC;

# Ver últimas 5 transações
SELECT * FROM transactions 
ORDER BY timestamp DESC 
LIMIT 5;

# Sair
\q
```

---

### **Comandos Úteis**
```bash
# Ver status dos containers
docker-compose ps

# Parar todos os serviços
docker-compose down

# Parar e remover volumes (limpar banco de dados)
docker-compose down -v

# Ver logs de um serviço específico
docker-compose logs api
docker-compose logs postgres

# Reiniciar serviços
docker-compose restart

# Rebuild após modificar código
docker-compose up --build -d
```

---

## 🏗️ **Arquitetura do Sistema**

### **Arquitetura Local (Docker Compose)**

![Arquitetura Local](docs/architecture-local.png)

**Componentes:**
- **Flask API (Port 5000):** Endpoints REST para detecção de fraude
- **PostgreSQL (Port 5433):** Armazena histórico de transações de cada usuário
- **Redis (Port 6379):** Cache opcional para hot data
- **Isolation Forest Model:** Modelo treinado (.joblib) com 71.6% recall

**Fluxo de uma Predição:**
1. Cliente envia transação → API Flask
2. API busca histórico do usuário no PostgreSQL
3. Feature Engineering aplica 17 transformações
4. Modelo Isolation Forest detecta anomalia
5. Lógica de negócio classifica risco (BAIXO/MÉDIO/ALTO/CRÍTICO)
6. Transação é salva no PostgreSQL
7. Resposta retorna para o cliente

---

### **Arquitetura de Produção (AWS)**

![Arquitetura AWS](docs/architecture-aws.png)

**Componentes AWS:**

| Serviço | Tipo | Função |
|---------|------|--------|
| **EC2 + Auto Scaling** | t2.micro → c5.large | Rodar containers da API (2-10 instâncias) |
| **Application Load Balancer** | ALB | Distribuir tráfego entre instâncias |
| **RDS PostgreSQL** | db.t3.small | Banco de dados gerenciado (histórico de transações) |
| **ElastiCache Redis** | cache.t3.micro | Cache distribuído (hot data) |
| **ECR** | Container Registry | Armazenar imagens Docker |
| **CloudWatch** | Monitoring | Logs, métricas, alertas |

**Custo Estimado:** ~$130/mês (após Free Tier) | **Free Tier:** $0/mês (primeiros 12 meses)

---

## 📁 **Estrutura do Projeto**
```
fraud-detection-realtime/
├── api/                              # API Flask
│   ├── app.py                        # Endpoints REST (/predict, /health)
│   ├── predictor.py                  # Lógica de predição + PostgreSQL
│   ├── schemas.py                    # Validação Pydantic
│   └── utils.py
├── src/
│   ├── data/
│   │   └── generate_data.py          # Geração de 300k transações sintéticas
│   ├── features/
│   │   └── build_features.py         # Feature engineering (17 features)
│   └── models/
│       ├── train_model.py            # Treino do Isolation Forest
│       └── evaluate_model.py         # Avaliação (71.6% recall)
├── models/
│   ├── isolation_forest.joblib       # Modelo treinado
│   └── scaler.joblib                 # StandardScaler
├── data/
│   ├── raw/                          # Transações sintéticas
│   └── processed/                    # Dados com features
├── notebooks/
│   └── 01-eda-feature-eng.ipynb      # Análise exploratória
├── reports/
│   └── figures/                      # Gráficos e visualizações
├── docker-compose.yml                # Orquestração (API + PostgreSQL + Redis)
├── Dockerfile                        # Container da API
├── init.sql                          # Schema + dados de exemplo
├── requirements.txt                  # Dependências completas (dev)
├── requirements-api.txt              # Dependências da API (produção)
├── test_api.py                       # Testes end-to-end
└── README.md
```

---

## 🔬 **Feature Engineering (17 Features)**

O sistema utiliza **17 features contextuais** que capturam desvios de comportamento:

### **Features Temporais**
- `time_since_last_tx_sec`: Detecta sequências rápidas
- `tx_count_rolling_1h_user`: Detecta card testing
- `is_unusual_hour`: Flag para horário atípico (2-5 AM)
- `hour_of_day`, `day_of_week`, `is_weekend`

### **Features Geoespaciais** (Detecta Teleporte)
- `velocity_kmh`: Velocidade necessária entre transações
- `distance_from_home_km`: Distância da localização "home"

### **Features de Gasto** (Detecta Gasto Súbito)
- `amount`: Valor da transação
- `user_avg_amount_7d`: Média de gasto dos últimos 7 dias
- `user_std_amount_7d`: Desvio padrão
- `spending_zscore`: Z-score do valor atual

### **Features de Merchant** (Detecta Card Testing)
- `distinct_merchants_rolling_1h_user`: Merchants diferentes (última hora)
- `is_new_merchant_category_user`: Flag para categoria nova

### **Features Compostas**
- `rapid_sequence_flag`: Transações em <60s
- `value_anomaly_flag`: Micro-transações ou gastos altos
- `combined_anomaly_score`: Score combinado (0-15)

---

## 🌐 **API Endpoints**

### **GET /**
Informações básicas da API.

### **GET /health**
Health check detalhado.

**Response:**
```json
{
  "status": "healthy",
  "model": "Isolation Forest",
  "features": 17
}
```

---

### **POST /predict**
Predição de fraude para uma transação.

**Request Body:**
```json
{
  "user_id": "string",
  "amount": "float (>0)",
  "merchant_name": "string",
  "merchant_category": "string",
  "latitude": "float (-90 a 90)",
  "longitude": "float (-180 a 180)",
  "timestamp": "string (ISO 8601, opcional)"
}
```

**Response:**
```json
{
  "anomaly_score": "float",
  "is_anomaly": "boolean",
  "risk_level": "BAIXO | MÉDIO | ALTO | CRÍTICO",
  "recommendation": "string",
  "features": {
    "velocity_kmh": "float",
    "distance_from_home_km": "float",
    "spending_zscore": "float",
    "tx_count_1h": "int",
    "distinct_merchants_1h": "int"
  }
}
```

---

### **POST /predict/batch**
Predição em lote (múltiplas transações).

**Request Body:**
```json
{
  "transactions": [
    { "user_id": "...", "amount": 100, ... },
    { "user_id": "...", "amount": 200, ... }
  ]
}
```

**Response:**
```json
{
  "predictions": [
    { "anomaly_score": 0.1, "risk_level": "BAIXO", ... },
    { "anomaly_score": -0.3, "risk_level": "ALTO", ... }
  ]
}
```

---

## 🏢 **Classificação de Risco (Lógica de Negócio)**

| Nível | Critérios | Ação Recomendada |
|-------|-----------|------------------|
| **CRÍTICO** | ≥2 sinais fortes:<br>• velocity > 800 km/h<br>• distance > 5000 km<br>• card_testing (tx_count>5 + merchants>3) | **BLOQUEAR** transação<br>**LIGAR** para cliente imediatamente |
| **ALTO** | Anomalia detectada pelo modelo<br>(anomaly_score < -0.2) | Enviar para **FILA DE ANÁLISE HUMANA**<br>(prioridade alta) |
| **MÉDIO** | Anomalia leve<br>(anomaly_score < 0) | Enviar para **FILA DE ANÁLISE HUMANA**<br>(prioridade normal) |
| **BAIXO** | Normal<br>(anomaly_score ≥ 0) | **APROVAR** automaticamente |

---

## 📈 **Impacto de Negócio**

### **Cenário: Fintech com 1M de transações/mês**

**Premissas:**
- Taxa de fraude real: 0.24% (2.400 fraudes/mês)
- Prejuízo médio por fraude: R$ 1.500
- Recall do modelo: 71.6%

**Resultados:**

| Métrica | Valor |
|---------|-------|
| **Fraudes detectadas** | 1.718 fraudes/mês |
| **Prejuízo evitado** | **R$ 2.577.000/mês** |
| **Custo AWS (produção)** | R$ 650/mês (~$130) |
| **ROI** | **~396.000%** |
| **Falsos positivos** | 8.900 transações (0.89%) |

**Trade-off aceitável:** Para cada 1 fraude verdadeira, o sistema gera ~5 falsos positivos que vão para análise humana.

---

## 🛠️ **Tecnologias Utilizadas**

| Categoria | Tecnologias |
|-----------|-------------|
| **Backend** | Flask 3.0.0, Gunicorn 21.2.0, Pydantic 2.9.0 |
| **Machine Learning** | scikit-learn 1.5.2, pandas 2.1.4, numpy 1.26.2 |
| **Database** | PostgreSQL 15, Redis 7, psycopg2 2.9.9 |
| **DevOps** | Docker, Docker Compose, Git |
| **Data Generation** | Faker 37.12.0, geopy 2.4.1 |

---

## 🤝 **Contribuindo**

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/melhoria`)
3. Commit (`git commit -m 'feat: adiciona nova feature'`)
4. Push (`git push origin feature/melhoria`)
5. Abra um Pull Request

---

## 📄 **Licença**

Este projeto está sob a licença MIT.

---

## 📚 **Referências**

- [Isolation Forest Paper (Liu et al., 2008)](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)
- [Feature Engineering for Machine Learning (O'Reilly)](https://www.oreilly.com/library/view/feature-engineering-for/9781491953235/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

---

<div align="center">

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**

Desenvolvido como projeto de portfólio para demonstrar habilidades em:<br>
**Machine Learning | Feature Engineering | API REST | Docker | PostgreSQL | AWS Architecture**

</div>