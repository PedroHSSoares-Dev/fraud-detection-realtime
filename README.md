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
- ✅ **Script de demonstração profissional** (`demo_linkedin.py`) com animações
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
- [Python 3.11+](https://www.python.org/downloads/) instalado
- [Git](https://git-scm.com/) instalado

---

### **Execução Rápida (Demonstração Completa)**
```bash
# 1. Clone o repositório (inclui modelos pré-treinados)
git clone https://github.com/seu-usuario/fraud-detection-realtime.git
cd fraud-detection-realtime

# 2. Inicie os serviços (API + PostgreSQL + Redis)
docker-compose up -d

# Aguardar ~10 segundos para inicialização
# Verificar logs: docker-compose logs -f

# 3. Instale dependências da demo
pip install colorama requests tqdm

# 4. Execute a demonstração profissional
python demo_linkedin.py
```

**Resultado esperado (~90 segundos):**
```
    ███████╗██████╗  █████╗ ██╗   ██╗██████╗ 
    ██╔════╝██╔══██╗██╔══██╗██║   ██║██╔══██╗
    █████╗  ██████╔╝███████║██║   ██║██║  ██║
    
[PASSO 1] ✅ API está rodando!

[PASSO 2] Transação Normal → BAIXO (APROVADA)

[PASSO 3] Teleporte (SP→Tokyo) → CRÍTICO (BLOQUEADA)
🚨 Velocidade: 10.000 km/h - FISICAMENTE IMPOSSÍVEL!

[PASSO 4] Card Testing → ALTO (ANÁLISE HUMANA)
⚠️  3 merchants diferentes detectados

📊 RESUMO: 71.6% recall | ROI: 22x | R$ 515k/mês economizados
```

A demo executa **3 cenários** de detecção de fraude em tempo real:
1. **Transação normal** (usuário `user_demo_normal`) → Aprovada automaticamente
2. **Teleporte** (usuário `user_demo_teleport`: SP → Tokyo em 30 min) → Bloqueada
3. **Card testing** (usuário `user_demo_fraudster`: 3 micro-transações) → Análise humana

**Nota:** Os usuários de demonstração estão pré-cadastrados no banco (`init.sql`) com histórico de transações consistente.

---

### **Retreinar o Modelo (Opcional)**

Se você quiser treinar o modelo do zero com seus próprios dados:
```bash
# 1. Criar ambiente virtual (recomendado)
python -m venv fraud-env
source fraud-env/bin/activate  # Linux/Mac
fraud-env\Scripts\activate     # Windows

# 2. Instalar dependências completas
pip install -r requirements.txt

# 3. Executar pipeline completo
python src/data/generate_data.py           # Gera 300k transações (~2 min)
python src/features/build_features.py      # Feature engineering (~3 min)
cd models
python train_model.py                      # Treina modelo (~2 min)
python evaluate_model.py                   # Avalia performance (~1 min)
cd ..

# 4. Reiniciar API com novo modelo
docker-compose restart api
```

**Tempo total:** ~8-10 minutos

**Resultado:**
- `data/raw/transactions_with_fraud.csv` (300.135 transações)
- `data/processed/transactions_with_features.csv` (com 17 features)
- `models/isolation_forest.joblib` (modelo retreinado)
- `models/scaler.joblib` (StandardScaler atualizado)
- `reports/figures/` (novos gráficos de performance)

---

### **Testes Automatizados (Opcional)**
```bash
# Executar bateria completa de testes
pip install requests
python test_api.py
```

**Resultado esperado:**
```
✅ Testes Passaram: 7/7
📊 Taxa de Sucesso: 100.0%

Testes executados:
1. ✅ Health Check
2. ✅ Transação Normal (BAIXO risco)
3. ✅ Card Testing (ALTO risco)
4. ✅ Teleporte (CRÍTICO)
5. ✅ Gasto Súbito (MÉDIO/ALTO risco)
6. ✅ Validação de Entrada (erro 400)
7. ✅ Predição em Lote
```

---

### **Testes Manuais (API via curl)**

#### **Health Check:**
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "model": "Isolation Forest",
  "features": 17
}
```

---

#### **Predição de Fraude (Normal):**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_demo_normal",
    "amount": 150.00,
    "merchant_name": "Supermercado Extra",
    "merchant_category": "grocery",
    "latitude": -23.5505,
    "longitude": -46.6333
  }'
```

**Response:**
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

#### **Predição de Fraude (Teleporte):**
```bash
# Primeira transação em São Paulo
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_demo_teleport",
    "amount": 200.00,
    "merchant_name": "Restaurante SP",
    "merchant_category": "food",
    "latitude": -23.5505,
    "longitude": -46.6333
  }'

# Aguardar 2 segundos
sleep 2

# Segunda transação em Tóquio (impossível!)
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_demo_teleport",
    "amount": 300.00,
    "merchant_name": "Restaurante Tokyo",
    "merchant_category": "food",
    "latitude": 35.6762,
    "longitude": 139.6503
  }'
```

**Response (FRAUDE DETECTADA):**
```json
{
  "anomaly_score": -0.45,
  "is_anomaly": true,
  "risk_level": "CRÍTICO",
  "recommendation": "BLOQUEAR transação e LIGAR para cliente imediatamente",
  "features": {
    "velocity_kmh": 18500.5,
    "distance_from_home_km": 18400.2,
    "spending_zscore": 1.2,
    "tx_count_1h": 2,
    "distinct_merchants_1h": 1
  }
}
```

---

### **Explorar o Banco de Dados (Opcional)**
```bash
# Conectar ao PostgreSQL
docker exec -it fraud-postgres psql -U fraud_user -d fraud_db

# Dentro do PostgreSQL:

# Ver total de transações
SELECT COUNT(*) FROM transactions;

# Ver transações por usuário (top 10)
SELECT user_id, COUNT(*) as total 
FROM transactions 
GROUP BY user_id 
ORDER BY total DESC 
LIMIT 10;

# Ver últimas 5 transações de um usuário
SELECT * FROM transactions 
WHERE user_id = 'user_demo_normal'
ORDER BY timestamp DESC 
LIMIT 5;

# Ver usuários de demonstração
SELECT user_id, COUNT(*) as total_transactions
FROM transactions 
WHERE user_id LIKE 'user_demo_%'
GROUP BY user_id;

# Sair
\q
```

---

### **Comandos Úteis do Docker**
```bash
# Ver status dos containers
docker-compose ps

# Ver logs em tempo real (todos os serviços)
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f redis

# Parar todos os serviços
docker-compose down

# Parar e remover volumes (limpa banco de dados)
docker-compose down -v

# Reiniciar serviços
docker-compose restart

# Reiniciar serviço específico
docker-compose restart api

# Rebuild após modificar código
docker-compose up --build -d

# Ver uso de recursos (CPU, RAM)
docker stats

# Executar comando dentro do container
docker exec -it fraud-api bash
```

---

### **Gravação de Vídeo da Demo (Para LinkedIn/Portfólio)**

**Preparação:**

1. **Terminal:**
   - Usar **Windows Terminal** (melhor suporte a cores)
   - Modo tela cheia: `F11`
   - Aumentar fonte: `Ctrl + +` (até 16-18pt)

2. **OBS Studio (recomendado):**
   - Download: [obsproject.com](https://obsproject.com/)
   - Fonte: "Captura de Janela" → Windows Terminal
   - Resolução: 1920x1080, 30fps

3. **Ajustar velocidade (opcional):**
```python
   # Editar linha 24 de demo_linkedin.py
   SPEED = 1.0   # Normal (~90 segundos)
   SPEED = 0.7   # Lento (melhor para narração)
   SPEED = 1.5   # Rápido (dinâmico para LinkedIn)
```

4. **Executar:**
```bash
   python demo_linkedin.py
```

5. **Edição (opcional):**
   - **CapCut** (grátis): Adicionar música, textos, cortes
   - **DaVinci Resolve** (grátis): Edição profissional

---

## 🏗️ **Arquitetura do Sistema**

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

**Componentes AWS:**

| Serviço | Tipo | Função |
|---------|------|--------|
| **EC2 + Auto Scaling** | t2.micro → c5.large | Rodar containers da API (2-10 instâncias) |
| **Application Load Balancer** | ALB | Distribuir tráfego entre instâncias |
| **RDS PostgreSQL** | db.t3.small | Banco de dados gerenciado (histórico de transações) |
| **ElastiCache Redis** | cache.t3.micro | Cache distribuído (hot data) |
| **ECR** | Container Registry | Armazenar imagens Docker |
| **CloudWatch** | Monitoring | Logs, métricas, alertas |

**Custo Estimado AWS:**

| Cenário | Custo Mensal |
|---------|--------------|
| **Free Tier (12 meses)** | R$ 0/mês |
| **Mínimo Viável (1M tx/mês)** | ~R$ 785/mês (~$157) |
| **Produção Séria (10M tx/mês)** | ~R$ 3.170/mês (~$634) |

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
├── init.sql                          # Schema + dados de exemplo + users demo
├── requirements.txt                  # Dependências completas (dev)
├── requirements-api.txt              # Dependências da API (produção)
├── demo_linkedin.py                  # Script de demonstração profissional
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

**Response:**
```json
{
  "service": "Fraud Detection API",
  "version": "1.0.0",
  "status": "running",
  "model_loaded": true
}
```

---

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
- Prejuízo médio por fraude: R$ 500
- Recall do modelo: 71.6% (1.718 fraudes detectadas)
- Taxa de prevenção pós-análise humana: 60%
- Custo mensal total: R$ 22.650 (AWS + analistas + overhead)

**Resultados:**

| Métrica | Valor |
|---------|-------|
| **Fraudes detectadas** | 1.718/mês |
| **Fraudes efetivamente prevenidas** | 1.031/mês (60% das detectadas) |
| **Prejuízo evitado** | **R$ 515.500/mês** |
| **Custo AWS (Mínimo viável)** | R$ 785/mês |
| **Custo AWS (10M tx/mês)** | R$ 3.170/mês |
| **Custo analistas (2 FTE)** | R$ 20.000/mês |
| **Custo total (operacional)** | R$ 22.650/mês |
| **ROI** | **2.176%** (22x retorno) |

**Interpretação:** Para cada R$ 1 investido no sistema, a empresa economiza R$ 22 em fraudes evitadas.

---

## ⚖️ **Trade-offs do Modelo**

O modelo foi otimizado para **maximizar recall** (detectar fraudes) em vez de precision (minimizar falsos positivos).

**Por quê?**

Em detecção de fraude, o custo de **deixar passar uma fraude** (R$ 500) é **250x maior** que o custo de **analisar um falso positivo** (R$ 2).

**Métricas:**
- **Recall: 71.6%** ✅ Detecta 358/500 fraudes
- **Precision: 16.8%** ⚠️ 1.781 falsos positivos (0.89% das transações)
- **F1-Score: 0.27** (balanceamento recall/precision)

**Interpretação:**
Para cada 100 alertas do sistema:
- 17 são fraudes reais (devem ser bloqueadas)
- 83 são clientes legítimos (devem ser aprovados após análise)

**Trade-off aceitável:** Preferimos analisar 8.900 transações/mês (falsos positivos) do que deixar passar 142 fraudes/mês adicionais (R$ 71k em prejuízo).

**Melhorias possíveis:**
- Modelo supervisionado (XGBoost) → Precision ~60-70%
- Ensemble com regras de negócio → Precision crítica ~90%
- Ajuste de threshold → Balancear precision/recall conforme negócio

---

## 🛠️ **Tecnologias Utilizadas**

| Categoria | Tecnologias |
|-----------|-------------|
| **Backend** | Flask 3.0.0, Gunicorn 21.2.0, Pydantic 2.9.0 |
| **Machine Learning** | scikit-learn 1.5.2, pandas 2.1.4, numpy 1.26.2 |
| **Database** | PostgreSQL 15, Redis 7, psycopg2 2.9.9 |
| **DevOps** | Docker, Docker Compose, Git |
| **Data Generation** | Faker 37.12.0, geopy 2.4.1 |
| **Visualization** | colorama, tqdm (demo script) |

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