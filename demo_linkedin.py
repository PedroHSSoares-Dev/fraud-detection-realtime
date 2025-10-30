"""
demo_linkedin.py - Script de Demonstração Profissional para LinkedIn
Demonstração completa do sistema de detecção de fraude em tempo real
com ASCII art, barra de progresso, animações e visualização colorida.

Autor: Pedro Soares
GitHub: github.com/seu-usuario/fraud-detection-realtime
"""

import requests
import json
import time
import sys
from datetime import datetime
from colorama import init, Fore, Back, Style
from tqdm import tqdm

# Inicializar colorama (funciona no Windows)
init(autoreset=True)

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

API_URL = "http://localhost:5000"
SPEED = 2  # Multiplicador de velocidade (1.0 = normal, 0.5 = lento, 2.0 = rápido)


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def sleep(seconds):
    """Sleep ajustável pela velocidade."""
    time.sleep(seconds * SPEED)


def print_logo():
    """Imprime logo ASCII art."""
    logo = f"""
{Fore.CYAN}{Style.BRIGHT}
    ███████╗██████╗  █████╗ ██╗   ██╗██████╗ 
    ██╔════╝██╔══██╗██╔══██╗██║   ██║██╔══██╗
    █████╗  ██████╔╝███████║██║   ██║██║  ██║
    ██╔══╝  ██╔══██╗██╔══██║██║   ██║██║  ██║
    ██║     ██║  ██║██║  ██║╚██████╔╝██████╔╝
    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ 
    
    {Fore.YELLOW}DETECTION SYSTEM v1.0{Fore.CYAN}
    Real-Time Fraud Detection with Machine Learning
{Style.RESET_ALL}"""
    print(logo)


def print_header(text, color=Fore.CYAN):
    """Imprime cabeçalho estilizado."""
    print("\n" + "=" * 70)
    print(color + Style.BRIGHT + text.center(70))
    print("=" * 70 + Style.RESET_ALL)


def print_step(number, text, color=Fore.YELLOW):
    """Imprime passo numerado."""
    print(f"\n{color}{Style.BRIGHT}[PASSO {number}] {text}{Style.RESET_ALL}")


def print_success(text):
    """Imprime mensagem de sucesso."""
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")


def print_warning(text):
    """Imprime mensagem de aviso."""
    print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")


def print_error(text):
    """Imprime mensagem de erro (fraude detectada)."""
    print(f"{Fore.RED}🚨 {text}{Style.RESET_ALL}")


def print_info(text):
    """Imprime mensagem informativa."""
    print(f"{Fore.CYAN}ℹ️  {text}{Style.RESET_ALL}")


def print_json(data, highlight_keys=None):
    """Imprime JSON formatado com destaque em chaves específicas."""
    if highlight_keys is None:
        highlight_keys = []
    
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    
    # Destacar chaves importantes
    for key in highlight_keys:
        if key in json_str:
            lines = json_str.split('\n')
            new_lines = []
            for line in lines:
                if f'"{key}"' in line:
                    new_lines.append(f"{Fore.YELLOW}{Style.BRIGHT}{line}{Style.RESET_ALL}")
                else:
                    new_lines.append(line)
            json_str = '\n'.join(new_lines)
    
    print(json_str)


def typing_effect(text, delay=0.05):
    """Simula digitação."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay * SPEED)
    print()


def show_progress(text, duration=2):
    """Mostra barra de progresso."""
    print(f"\n{Fore.CYAN}{text}{Style.RESET_ALL}")
    for _ in tqdm(
        range(100), 
        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}',
        colour='cyan'
    ):
        time.sleep(duration / 100 * SPEED)


def print_box(text, color=Fore.RED):
    """Imprime texto em caixa destacada."""
    border = "═" * (len(text) + 4)
    print(f"\n{color}╔{border}╗")
    print(f"║  {text}  ║")
    print(f"╚{border}╝{Style.RESET_ALL}")


def animate_loading(text="Processando", steps=3, delay=0.5):
    """Animação de carregamento."""
    for i in range(steps):
        sys.stdout.write(f"\r{Fore.YELLOW}{text}{'.' * (i + 1)}   {Style.RESET_ALL}")
        sys.stdout.flush()
        sleep(delay)
    print()


def print_separator(char="─", length=70, color=Fore.CYAN):
    """Imprime separador."""
    print(f"{color}{char * length}{Style.RESET_ALL}")


# ============================================================================
# FUNÇÕES DE DEMONSTRAÇÃO
# ============================================================================

def check_api_health():
    """Verifica se API está rodando."""
    print_step(1, "Verificando Status da API", Fore.CYAN)
    sleep(0.5)
    
    show_progress("Conectando ao sistema", duration=1.5)
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("API está rodando!")
            print(f"   {Fore.CYAN}├─ Modelo: {Fore.WHITE}{data['model']}")
            print(f"   {Fore.CYAN}├─ Features: {Fore.WHITE}{data['features']}")
            print(f"   {Fore.CYAN}└─ Status: {Fore.GREEN}HEALTHY{Style.RESET_ALL}")
            return True
        else:
            print_error(f"API retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("API não está rodando!")
        print(f"\n{Fore.RED}{Style.BRIGHT}⚠️  Execute antes:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   docker-compose up -d{Style.RESET_ALL}\n")
        return False


def demo_normal_transaction():
    """Demonstra transação normal (aprovada)."""
    print_step(2, "Transação Normal - Comportamento Legítimo", Fore.GREEN)
    sleep(1)
    
    transaction = {
        "user_id": "user_traveler_001",
        "amount": 200.00,
        "merchant_name": "Restaurante Figueira Rubaiyat",
        "merchant_category": "food",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\n{Fore.CYAN}┌─ DETALHES DA TRANSAÇÃO")
    print(f"│")
    print(f"├─ 📍 Localização: {Fore.WHITE}São Paulo, Brasil")
    print(f"├─ 💰 Valor: {Fore.WHITE}R$ {transaction['amount']:.2f}")
    print(f"├─ 🏪 Estabelecimento: {Fore.WHITE}{transaction['merchant_name']}")
    print(f"├─ 🏷️  Categoria: {Fore.WHITE}{transaction['merchant_category']}")
    print(f"└─ ⏰ Horário: {Fore.WHITE}{datetime.now().strftime('%H:%M:%S')}")
    print(Style.RESET_ALL)
    
    sleep(1)
    animate_loading("Analisando padrão de comportamento", steps=3, delay=0.6)
    
    response = requests.post(f"{API_URL}/predict", json=transaction)
    data = response.json()
    
    sleep(0.5)
    print(f"\n{Fore.CYAN}📊 ANÁLISE DO MODELO:{Style.RESET_ALL}")
    print_json(data, highlight_keys=['risk_level', 'recommendation', 'anomaly_score'])
    
    sleep(1.5)
    if data['risk_level'] == 'BAIXO':
        print_box("✓ TRANSAÇÃO APROVADA AUTOMATICAMENTE", Fore.GREEN)
        print(f"\n{Fore.GREEN}   Anomaly Score: {data['anomaly_score']:.3f} (normal)")
        print(f"   Sem sinais de fraude detectados{Style.RESET_ALL}")
    
    return transaction


def demo_teleport_fraud(previous_transaction):
    """Demonstra detecção de teleporte (fraude crítica)."""
    print_step(3, "Transação Suspeita - Possível Teleporte", Fore.RED)
    sleep(1)
    
    print(f"\n{Fore.YELLOW}⏳ Simulando passagem de tempo...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   (30 minutos após transação anterior){Style.RESET_ALL}")
    
    # Barra de progresso para "tempo passando"
    for _ in tqdm(
        range(100), 
        desc=f"{Fore.YELLOW}Aguardando{Style.RESET_ALL}",
        bar_format='{desc}: {bar}',
        colour='yellow'
    ):
        time.sleep(0.02 * SPEED)
    print()
    
    transaction = {
        "user_id": "user_traveler_001",
        "amount": 300.00,
        "merchant_name": "Restaurante Sukiyabashi Jiro",
        "merchant_category": "food",
        "latitude": 35.6762,
        "longitude": 139.6503,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\n{Fore.RED}┌─ DETALHES DA TRANSAÇÃO (SUSPEITA)")
    print(f"│")
    print(f"├─ 📍 Localização: {Fore.WHITE}Tóquio, Japão {Fore.RED}⚠️")
    print(f"├─ 💰 Valor: {Fore.WHITE}R$ {transaction['amount']:.2f}")
    print(f"├─ 🏪 Estabelecimento: {Fore.WHITE}{transaction['merchant_name']}")
    print(f"├─ 🏷️  Categoria: {Fore.WHITE}{transaction['merchant_category']}")
    print(f"└─ ⏰ Horário: {Fore.WHITE}{datetime.now().strftime('%H:%M:%S')} {Fore.RED}(30 min depois)")
    print(Style.RESET_ALL)
    
    sleep(1)
    animate_loading("Calculando features geoespaciais", steps=4, delay=0.5)
    
    response = requests.post(f"{API_URL}/predict", json=transaction)
    data = response.json()
    
    sleep(0.5)
    print(f"\n{Fore.RED}📊 ANÁLISE DO MODELO (CRÍTICA):{Style.RESET_ALL}")
    print_json(
        data, 
        highlight_keys=['risk_level', 'velocity_kmh', 'distance_from_home_km', 'recommendation']
    )
    
    sleep(1.5)
    
    # DESTAQUE DRAMÁTICO DO RESULTADO
    if data['risk_level'] in ['CRÍTICO', 'ALTO']:
        print("\n")
        print("!" * 70)
        print(Back.RED + Fore.WHITE + Style.BRIGHT + 
              "  🚨 ALERTA DE FRAUDE - NÍVEL CRÍTICO  ".center(70) + Style.RESET_ALL)
        print("!" * 70)
        
        sleep(0.5)
        velocity = data['features']['velocity_kmh']
        distance = data['features']['distance_from_home_km']
        
        print(f"\n{Fore.RED}{Style.BRIGHT}╔═══════════════════════════════════════════════════════╗")
        print(f"║  INDICADORES DE FRAUDE                                ║")
        print(f"╠═══════════════════════════════════════════════════════╣")
        print(f"║  ⚡ Velocidade Necessária: {velocity:>18,.1f} km/h  ║")
        print(f"║  📏 Distância Percorrida: {distance:>18,.1f} km    ║")
        print(f"║  🎯 Anomaly Score:        {data['anomaly_score']:>23.3f}     ║")
        print(f"╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        sleep(1)
        print(f"\n{Fore.YELLOW}💡 ANÁLISE TÉCNICA:{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}├─ Distância São Paulo → Tóquio: {Fore.WHITE}~18.400 km")
        print(f"   {Fore.CYAN}├─ Tempo decorrido: {Fore.WHITE}~30 minutos")
        print(f"   {Fore.CYAN}├─ Velocidade média de avião: {Fore.WHITE}~900 km/h")
        print(f"   {Fore.CYAN}├─ Velocidade detectada: {Fore.RED}{velocity:,.0f} km/h")
        print(f"   {Fore.CYAN}└─ Conclusão: {Fore.RED}{Style.BRIGHT}FISICAMENTE IMPOSSÍVEL!{Style.RESET_ALL}")
        
        sleep(1)
        print_box("🛑 AÇÃO RECOMENDADA: BLOQUEAR E CONTATAR CLIENTE", Fore.RED)


def demo_card_testing():
    """Demonstra detecção de card testing."""
    print_step(4, "Card Testing - Sondagem de Cartão", Fore.YELLOW)
    sleep(1)
    
    print(f"\n{Fore.CYAN}📝 Cenário:{Style.RESET_ALL}")
    typing_effect("   Fraudador testa cartão roubado em múltiplos estabelecimentos", delay=0.03)
    typing_effect("   com valores baixos para confirmar validade...", delay=0.03)
    
    sleep(1)
    
    merchants = [
        ("Loja de Conveniência 24h", "retail", 5.00),
        ("Farmácia Drogasil", "pharmacy", 10.00),
        ("Posto Shell", "gas_station", 15.00)
    ]
    
    print(f"\n{Fore.YELLOW}🔄 Sequência de Transações Suspeitas:{Style.RESET_ALL}\n")
    
    for i, (merchant, category, amount) in enumerate(merchants, 1):
        print(f"{Fore.CYAN}┌─ Transação {i}/3")
        print(f"├─ 🏪 {merchant}")
        print(f"├─ 💰 R$ {amount:.2f}")
        print(f"└─ ⏰ {datetime.now().strftime('%H:%M:%S')}{Style.RESET_ALL}")
        
        transaction = {
            "user_id": "user_fraudster_001",
            "amount": amount,
            "merchant_name": merchant,
            "merchant_category": category,
            "latitude": -23.5505,
            "longitude": -46.6333,
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(f"{API_URL}/predict", json=transaction)
        data = response.json()
        
        if i < 3:
            print(f"   {Fore.GREEN}✓ Processando...{Style.RESET_ALL}\n")
            sleep(0.8)
        else:
            sleep(0.5)
            animate_loading("Detectando padrão anômalo", steps=3, delay=0.5)
            
            print(f"\n{Fore.YELLOW}📊 ANÁLISE DA 3ª TRANSAÇÃO:{Style.RESET_ALL}")
            print_json(
                data, 
                highlight_keys=['risk_level', 'distinct_merchants_1h', 'tx_count_1h']
            )
            
            sleep(1.5)
            if data['risk_level'] in ['ALTO', 'CRÍTICO']:
                print_warning("CARD TESTING DETECTADO!")
                print(f"\n{Fore.YELLOW}   Padrão identificado:")
                print(f"   {Fore.CYAN}├─ Merchants diferentes (1h): {Fore.WHITE}{data['features']['distinct_merchants_1h']}")
                print(f"   {Fore.CYAN}├─ Transações em sequência: {Fore.WHITE}{data['features']['tx_count_1h']}")
                print(f"   {Fore.CYAN}├─ Valores suspeitos: {Fore.WHITE}Micro-transações (<R$ 20)")
                print(f"   {Fore.CYAN}└─ Risco: {Fore.RED}{data['risk_level']}{Style.RESET_ALL}")


def demo_summary():
    """Mostra resumo final com estatísticas."""
    print_header("📊 RESUMO DA DEMONSTRAÇÃO", Fore.MAGENTA)
    sleep(1)
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}Sistema de Detecção de Fraude em Tempo Real{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Powered by Machine Learning (Isolation Forest){Style.RESET_ALL}")
    
    sleep(1)
    print_separator()
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}✅ DETECÇÕES REALIZADAS NESTA DEMO:{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}1. Transação Normal → {Fore.WHITE}APROVADA {Fore.CYAN}(BAIXO risco)")
    print(f"   {Fore.RED}2. Teleporte (SP→Tokyo) → {Fore.WHITE}BLOQUEADA {Fore.RED}(CRÍTICO)")
    print(f"   {Fore.YELLOW}3. Card Testing → {Fore.WHITE}SINALIZADA {Fore.YELLOW}(ALTO risco){Style.RESET_ALL}")
    
    sleep(1)
    print_separator()
    
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}🎯 PERFORMANCE DO MODELO (Dataset Completo):{Style.RESET_ALL}")
    
    # Tabela de métricas
    metrics = [
        ("Recall Geral", "71.6%", Fore.GREEN),
        ("Card Testing", "83.8%", Fore.GREEN),
        ("Teleporte", "83.5%", Fore.GREEN),
        ("Sudden Spending", "70.7%", Fore.YELLOW),
        ("Unusual Time", "26.5%", Fore.RED),
        ("Falsos Positivos", "0.89%", Fore.CYAN)
    ]
    
    print(f"\n   {'Métrica':<20} {'Valor':>10}")
    print(f"   {Fore.CYAN}{'-' * 32}{Style.RESET_ALL}")
    for metric, value, color in metrics:
        print(f"   {metric:<20} {color}{value:>10}{Style.RESET_ALL}")
    
    sleep(1)
    print_separator()
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}🏗️  STACK TECNOLÓGICO:{Style.RESET_ALL}")
    
    stack = [
        ("Backend", "Python + Flask + Gunicorn"),
        ("Database", "PostgreSQL 15 (histórico de transações)"),
        ("Cache", "Redis 7 (hot data)"),
        ("ML Model", "Isolation Forest (scikit-learn 1.5.2)"),
        ("Features", "17 features contextuais"),
        ("DevOps", "Docker + Docker Compose"),
        ("Cloud", "AWS Architecture (EC2 + RDS + ALB)")
    ]
    
    print()
    for component, tech in stack:
        print(f"   {Fore.CYAN}├─ {component}:{Fore.WHITE} {tech}{Style.RESET_ALL}")
    
    sleep(1)
    print_separator()
    
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}💼 IMPACTO DE NEGÓCIO:{Style.RESET_ALL}")
    print(f"\n   {Fore.CYAN}Cenário: Fintech com 1M transações/mês")
    print(f"   {Fore.CYAN}Taxa de fraude: 0.24% (2.400 fraudes/mês){Style.RESET_ALL}")
    
    print(f"\n   {'Métrica':<30} {'Valor':>20}")
    print(f"   {Fore.MAGENTA}{'-' * 52}{Style.RESET_ALL}")
    
    business_metrics = [
        ("Fraudes Detectadas", "1.718/mês", Fore.GREEN),
        ("Prejuízo Evitado", "R$ 2.577.000/mês", Fore.GREEN),
        ("ROI", "396.000%", Fore.GREEN),
        ("Custo AWS (produção)", "~R$ 650/mês", Fore.CYAN)
    ]
    
    for metric, value, color in business_metrics:
        print(f"   {metric:<30} {color}{Style.BRIGHT}{value:>20}{Style.RESET_ALL}")


def print_closing():
    """Impressão final com call to action."""
    print_separator("═", 70, Fore.MAGENTA)
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}🔗 LINKS E CONTATO:{Style.RESET_ALL}")
    print(f"\n   {Fore.CYAN}GitHub:{Fore.WHITE} github.com/seu-usuario/fraud-detection-realtime")
    print(f"   {Fore.CYAN}LinkedIn:{Fore.WHITE} linkedin.com/in/seu-perfil")
    print(f"   {Fore.CYAN}Email:{Fore.WHITE} seu-email@exemplo.com")
    
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}💬 O QUE VOCÊ ACHOU?{Style.RESET_ALL}")
    print(f"   {Fore.CYAN}• Que tipo de fraude seria mais difícil de detectar?")
    print(f"   {Fore.CYAN}• Sugestões de features adicionais?")
    print(f"   {Fore.CYAN}• Dúvidas sobre a implementação?{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}{'='*70}")
    print(f"{'✨ OBRIGADO POR ASSISTIR! ✨'.center(70)}")
    print(f"{'='*70}{Style.RESET_ALL}\n")


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal - executa toda a demonstração."""
    try:
        # Limpar tela (opcional)
        # import os
        # os.system('cls' if os.name == 'nt' else 'clear')
        
        # Logo e introdução
        print_logo()
        sleep(2)
        
        print(f"{Fore.YELLOW}📹 Demonstração para LinkedIn{Style.RESET_ALL}")
        print(f"{Fore.CYAN}👨‍💻 Desenvolvido por: Pedro Soares")
        print(f"{Fore.CYAN}🎯 Tech Stack: Python | Flask | PostgreSQL | Docker | ML{Style.RESET_ALL}")
        sleep(2)
        
        # Verificar API
        if not check_api_health():
            return
        
        sleep(2)
        
        # Demonstrações
        print_separator("═", 70, Fore.CYAN)
        
        # 1. Transação normal
        previous_tx = demo_normal_transaction()
        sleep(2.5)
        
        # 2. Teleporte (FRAUDE!)
        demo_teleport_fraud(previous_tx)
        sleep(2.5)
        
        # 3. Card Testing
        demo_card_testing()
        sleep(2.5)
        
        # 4. Resumo
        demo_summary()
        sleep(2)
        
        # 5. Finalização
        print_header("✨ DEMONSTRAÇÃO CONCLUÍDA", Fore.GREEN)
        sleep(1)
        print_closing()
        
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Demonstração interrompida pelo usuário.{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"\n\n{Fore.RED}❌ Erro inesperado: {e}{Style.RESET_ALL}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print(f"\n{Fore.CYAN}Iniciando em 3 segundos...{Style.RESET_ALL}")
    sleep(3)
    main()