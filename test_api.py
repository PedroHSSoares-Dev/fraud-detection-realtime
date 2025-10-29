"""
test_api.py - Script de Teste Completo da API
Testa todas as funcionalidades end-to-end
"""

import requests
import json
from datetime import datetime
from typing import Dict
import time


class APITester:
    """Classe para testar a API de forma organizada."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.tests_passed = 0
        self.tests_failed = 0
    
    def print_header(self, title: str):
        """Imprime cabeçalho bonito."""
        print("\n" + "="*80)
        print(f"🧪 {title}")
        print("="*80)
    
    def print_result(self, test_name: str, passed: bool, details: str = ""):
        """Imprime resultado do teste."""
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"\n{status} - {test_name}")
        if details:
            print(f"   Detalhes: {details}")
        
        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
    
    def print_response(self, response: Dict):
        """Imprime resposta formatada."""
        print("\n📤 Resposta:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
    
    
    # ========================================================================
    # TESTE 1: HEALTH CHECK
    # ========================================================================
    
    def test_health_check(self):
        """Testa se API está rodando."""
        self.print_header("TESTE 1: Health Check")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.print_response(data)
                
                # Validar estrutura
                assert data['status'] == 'healthy'
                assert 'model' in data
                assert data['features'] == 17  # 16 features + amount
                
                self.print_result("Health Check", True, "API está saudável")
            else:
                self.print_result("Health Check", False, f"Status code: {response.status_code}")
        
        except Exception as e:
            self.print_result("Health Check", False, str(e))
    
    
    # ========================================================================
    # TESTE 2: TRANSAÇÃO NORMAL (BAIXO RISCO)
    # ========================================================================
    
    def test_normal_transaction(self):
        """Testa transação normal (deve ser aprovada)."""
        self.print_header("TESTE 2: Transação Normal (Baixo Risco)")
        
        transaction = {
            "user_id": "user_normal_001",
            "amount": 150.00,
            "merchant_name": "Supermercado Pão de Açúcar",
            "merchant_category": "grocery",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n📥 Transação enviada:")
        print(json.dumps(transaction, indent=2, ensure_ascii=False))
        
        try:
            response = requests.post(
                f"{self.base_url}/predict",
                json=transaction,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_response(data)
                
                # EXPECTATIVA: Risco BAIXO ou MÉDIO
                expected_risk = data['risk_level'] in ['BAIXO', 'MÉDIO']
                expected_recommendation = 'APROVAR' in data['recommendation']
                
                if expected_risk and expected_recommendation:
                    self.print_result(
                        "Transação Normal",
                        True,
                        f"Classificada como {data['risk_level']} (correto!)"
                    )
                else:
                    self.print_result(
                        "Transação Normal",
                        False,
                        f"Classificada como {data['risk_level']} (esperado: BAIXO/MÉDIO)"
                    )
            else:
                self.print_result("Transação Normal", False, f"Status: {response.status_code}")
        
        except Exception as e:
            self.print_result("Transação Normal", False, str(e))
    
    
    # ========================================================================
    # TESTE 3: CARD TESTING (ALTO RISCO)
    # ========================================================================
    
    def test_card_testing(self):
        """Testa fraude tipo Card Testing (múltiplas transações pequenas)."""
        self.print_header("TESTE 3: Card Testing (Alto Risco)")
        
        print("\n🔄 Simulando 3 transações consecutivas em merchants diferentes...")
        
        # Transação 1
        tx1 = {
            "user_id": "user_fraudster_001",
            "amount": 5.00,
            "merchant_name": "Loja A",
            "merchant_category": "retail",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "timestamp": datetime.now().isoformat()
        }
        
        # Transação 2 (10 segundos depois, merchant diferente)
        time.sleep(0.5)  # Simular delay curto
        tx2 = {
            "user_id": "user_fraudster_001",
            "amount": 10.00,
            "merchant_name": "Loja B",
            "merchant_category": "electronics",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "timestamp": datetime.now().isoformat()
        }
        
        # Transação 3 (10 segundos depois, merchant diferente)
        time.sleep(0.5)
        tx3 = {
            "user_id": "user_fraudster_001",
            "amount": 15.00,
            "merchant_name": "Loja C",
            "merchant_category": "food",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Enviar transações
            r1 = requests.post(f"{self.base_url}/predict", json=tx1, timeout=10)
            r2 = requests.post(f"{self.base_url}/predict", json=tx2, timeout=10)
            r3 = requests.post(f"{self.base_url}/predict", json=tx3, timeout=10)
            
            print("\n📤 Resultado da 3ª transação (a mais suspeita):")
            data = r3.json()
            self.print_response(data)
            
            # EXPECTATIVA: Risco ALTO ou CRÍTICO
            # Features: distinct_merchants_1h > 1, tx_count_1h > 2
            expected_risk = data['risk_level'] in ['ALTO', 'CRÍTICO']
            has_multiple_merchants = data['features']['distinct_merchants_1h'] >= 2
            
            if expected_risk and has_multiple_merchants:
                self.print_result(
                    "Card Testing",
                    True,
                    f"Classificado como {data['risk_level']} com {data['features']['distinct_merchants_1h']} merchants"
                )
            else:
                self.print_result(
                    "Card Testing",
                    False,
                    f"Classificado como {data['risk_level']} (esperado: ALTO/CRÍTICO)"
                )
        
        except Exception as e:
            self.print_result("Card Testing", False, str(e))
    
    
    # ========================================================================
    # TESTE 4: TELEPORTE (CRÍTICO)
    # ========================================================================
    
    def test_teleport(self):
        """Testa fraude tipo Teleporte (localização impossível)."""
        self.print_header("TESTE 4: Teleporte (Crítico)")
        
        print("\n🌍 Simulando transação em São Paulo seguida de transação em Tóquio...")
        
        # Transação 1: São Paulo
        tx1 = {
            "user_id": "user_traveler_001",
            "amount": 200.00,
            "merchant_name": "Restaurante SP",
            "merchant_category": "food",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "timestamp": datetime.now().isoformat()
        }
        
        # Transação 2: Tóquio (30 minutos depois - IMPOSSÍVEL!)
        time.sleep(0.5)
        tx2 = {
            "user_id": "user_traveler_001",
            "amount": 300.00,
            "merchant_name": "Restaurante Tokyo",
            "merchant_category": "food",
            "latitude": 35.6762,
            "longitude": 139.6503,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Enviar transações
            r1 = requests.post(f"{self.base_url}/predict", json=tx1, timeout=10)
            r2 = requests.post(f"{self.base_url}/predict", json=tx2, timeout=10)
            
            print("\n📤 Resultado da transação em Tóquio:")
            data = r2.json()
            self.print_response(data)
            
            # EXPECTATIVA: Risco CRÍTICO
            # Features: velocity_kmh > 800, distance > 5000 km
            expected_risk = data['risk_level'] == 'CRÍTICO'
            high_velocity = data['features']['velocity_kmh'] > 800
            long_distance = data['features']['distance_from_home_km'] > 5000
            
            if expected_risk and high_velocity:
                self.print_result(
                    "Teleporte",
                    True,
                    f"Classificado como CRÍTICO com velocidade de {data['features']['velocity_kmh']:.0f} km/h"
                )
            else:
                self.print_result(
                    "Teleporte",
                    False,
                    f"Classificado como {data['risk_level']} (esperado: CRÍTICO)"
                )
        
        except Exception as e:
            self.print_result("Teleporte", False, str(e))
    
    
    # ========================================================================
    # TESTE 5: GASTO SÚBITO (ALTO RISCO)
    # ========================================================================
    
    def test_sudden_spending(self):
        """Testa fraude tipo Gasto Súbito (valor muito alto)."""
        self.print_header("TESTE 5: Gasto Súbito (Alto Risco)")
        
        transaction = {
            "user_id": "user_bigspender_001",
            "amount": 8500.00,  # Valor muito alto
            "merchant_name": "Joalheria Luxo",
            "merchant_category": "jewelry",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n📥 Transação enviada:")
        print(json.dumps(transaction, indent=2, ensure_ascii=False))
        
        try:
            response = requests.post(
                f"{self.base_url}/predict",
                json=transaction,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_response(data)
                
                # EXPECTATIVA: Risco MÉDIO ou ALTO
                # Features: spending_zscore > 2
                expected_risk = data['risk_level'] in ['MÉDIO', 'ALTO', 'CRÍTICO']
                high_zscore = abs(data['features']['spending_zscore']) > 1.5
                
                if expected_risk:
                    self.print_result(
                        "Gasto Súbito",
                        True,
                        f"Classificado como {data['risk_level']} (z-score: {data['features']['spending_zscore']:.2f})"
                    )
                else:
                    self.print_result(
                        "Gasto Súbito",
                        False,
                        f"Classificado como {data['risk_level']} (esperado: MÉDIO/ALTO)"
                    )
            else:
                self.print_result("Gasto Súbito", False, f"Status: {response.status_code}")
        
        except Exception as e:
            self.print_result("Gasto Súbito", False, str(e))
    
    
    # ========================================================================
    # TESTE 6: VALIDAÇÃO DE ENTRADA (ERRO ESPERADO)
    # ========================================================================
    
    def test_invalid_input(self):
        """Testa validação de entrada (deve retornar erro 400)."""
        self.print_header("TESTE 6: Validação de Entrada (Erro Esperado)")
        
        # Transação inválida (amount negativo)
        invalid_transaction = {
            "user_id": "user_test",
            "amount": -100.00,  # ❌ Valor negativo
            "merchant_name": "Loja X",
            "merchant_category": "retail",
            "latitude": -23.5505,
            "longitude": -46.6333
        }
        
        print("\n📥 Transação inválida enviada:")
        print(json.dumps(invalid_transaction, indent=2, ensure_ascii=False))
        
        try:
            response = requests.post(
                f"{self.base_url}/predict",
                json=invalid_transaction,
                timeout=10
            )
            
            # EXPECTATIVA: Status 400 (Bad Request)
            if response.status_code == 400:
                data = response.json()
                self.print_response(data)
                self.print_result(
                    "Validação de Entrada",
                    True,
                    "API rejeitou entrada inválida corretamente (400)"
                )
            else:
                self.print_result(
                    "Validação de Entrada",
                    False,
                    f"Status {response.status_code} (esperado: 400)"
                )
        
        except Exception as e:
            self.print_result("Validação de Entrada", False, str(e))
    
    
    # ========================================================================
    # TESTE 7: BATCH PREDICTION
    # ========================================================================
    
    def test_batch_prediction(self):
        """Testa predição em lote."""
        self.print_header("TESTE 7: Predição em Lote")
        
        batch_request = {
            "transactions": [
                {
                    "user_id": "user_batch_001",
                    "amount": 100.00,
                    "merchant_name": "Loja 1",
                    "merchant_category": "retail",
                    "latitude": -23.5505,
                    "longitude": -46.6333,
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "user_id": "user_batch_002",
                    "amount": 200.00,
                    "merchant_name": "Loja 2",
                    "merchant_category": "food",
                    "latitude": -23.5505,
                    "longitude": -46.6333,
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        print(f"\n📥 Enviando {len(batch_request['transactions'])} transações em lote...")
        
        try:
            response = requests.post(
                f"{self.base_url}/predict/batch",
                json=batch_request,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                predictions = data['predictions']
                
                print(f"\n📤 Recebido {len(predictions)} predições:")
                for i, pred in enumerate(predictions, 1):
                    print(f"\n   Transação {i}: Risco {pred['risk_level']}")
                
                # EXPECTATIVA: Mesmo número de predições que transações
                if len(predictions) == len(batch_request['transactions']):
                    self.print_result(
                        "Predição em Lote",
                        True,
                        f"{len(predictions)} predições retornadas"
                    )
                else:
                    self.print_result(
                        "Predição em Lote",
                        False,
                        f"Retornou {len(predictions)} predições (esperado: {len(batch_request['transactions'])})"
                    )
            else:
                self.print_result("Predição em Lote", False, f"Status: {response.status_code}")
        
        except Exception as e:
            self.print_result("Predição em Lote", False, str(e))
    
    
    # ========================================================================
    # RESUMO FINAL
    # ========================================================================
    
    def print_summary(self):
        """Imprime resumo dos testes."""
        self.print_header("RESUMO DOS TESTES")
        
        total = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total * 100) if total > 0 else 0
        
        print(f"\n✅ Testes Passaram: {self.tests_passed}/{total}")
        print(f"❌ Testes Falharam: {self.tests_failed}/{total}")
        print(f"📊 Taxa de Sucesso: {success_rate:.1f}%")
        
        if self.tests_failed == 0:
            print("\n🎉 TODOS OS TESTES PASSARAM! API está funcionando perfeitamente!")
        else:
            print(f"\n⚠️  {self.tests_failed} teste(s) falharam. Verifique os logs acima.")
        
        print("\n" + "="*80)
    
    
    def run_all_tests(self):
        """Executa todos os testes."""
        print("\n" + "="*80)
        print("🚀 INICIANDO BATERIA DE TESTES DA API")
        print("="*80)
        
        self.test_health_check()
        self.test_normal_transaction()
        self.test_card_testing()
        self.test_teleport()
        self.test_sudden_spending()
        self.test_invalid_input()
        self.test_batch_prediction()
        
        self.print_summary()


# ==============================================================================
# EXECUTAR TESTES
# ==============================================================================

if __name__ == "__main__":
    # Verificar se API está rodando
    print("\n🔍 Verificando se API está rodando em http://localhost:5000...")
    
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print("✅ API está rodando!\n")
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: API não está rodando!")
        print("\nPara iniciar a API, execute:")
        print("  docker run -p 5000:5000 fraud-detection-api")
        print("\nOu localmente:")
        print("  cd api && python app.py")
        exit(1)
    
    # Executar testes
    tester = APITester()
    tester.run_all_tests()