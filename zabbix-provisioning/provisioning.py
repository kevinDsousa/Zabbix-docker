#!/usr/bin/env python3
import requests
import time
import re
from urllib.parse import urljoin

def setup_zabbix_initial_config():
    """Configura o Zabbix automaticamente via interface web"""
    
    base_url = "http://zabbix-web:8080"
    session = requests.Session()
    
    print("=== Configuração Automática do Zabbix ===")
    
    # 1. Acessa a página de setup diretamente
    print("1. Acessando página de setup...")
    setup_url = urljoin(base_url, "/setup.php")
    response = session.get(setup_url)
    
    # Check for setup page content (case-insensitive)
    if "welcome to zabbix" in response.text.lower() or "setup.php" in response.url:
        print("   ✓ Página de setup encontrada")
        return run_setup_wizard(session, base_url)
    elif "index.php" in response.url or "dashboard" in response.text:
        print("   ✓ Zabbix já está configurado!")
        return True
    else:
        print(f"   ⚠️ Resposta inesperada: {response.status_code} de {response.url}. Conteúdo inicial: {response.text[:200]}...") # Added more info
        return False

def run_setup_wizard(session, base_url):
    """Executa o wizard de configuração"""
    
    print("2. Executando wizard de configuração...")
    
    # Step 1: Welcome
    print("   → Passo 1: Welcome")
    response = session.get(f"{base_url}/setup.php")
    
    # Step 2: Check requirements
    print("   → Passo 2: Verificando requisitos")
    response = session.post(f"{base_url}/setup.php", data={
        'type': 'step2',
        'next': 'Next step'
    })
    
    # Step 3: Database configuration
    print("   → Passo 3: Configuração do banco")
    db_config = {
        'type': 'step3',
        'db_type': 'MYSQL',
        'db_server': 'zabbix-mysql',
        'db_port': '3306',
        'db_database': 'zabbix',
        'db_user': 'zabbix',
        'db_password': 'zabbix_pwd',
        'db_schema': '',
        'next': 'Next step'
    }
    response = session.post(f"{base_url}/setup.php", data=db_config)
    
    # Step 4: Zabbix server details
    print("   → Passo 4: Detalhes do servidor Zabbix")
    server_config = {
        'type': 'step4',
        'zbx_server': 'zabbix-server',
        'zbx_server_port': '10051',
        'zbx_server_name': 'Zabbix Docker',
        'next': 'Next step'
    }
    response = session.post(f"{base_url}/setup.php", data=server_config)
    
    # Step 5: Pre-installation summary
    print("   → Passo 5: Resumo da instalação")
    response = session.post(f"{base_url}/setup.php", data={
        'type': 'step5',
        'next': 'Next step'
    })
    
    # Step 6: Installation
    print("   → Passo 6: Finalizando instalação")
    response = session.post(f"{base_url}/setup.php", data={
        'type': 'step6',
        'save_config': '1',
        'download': 'Download configuration file',
        'next': 'Finish'
    })
    
    print("   ✓ Configuração inicial concluída!")
    return True

def wait_for_web_interface(base_url, max_attempts=20, delay=10):
    """Aguarda a interface web do Zabbix estar acessível."""
    print(f"Aguardando a interface web do Zabbix em {base_url} ficar disponível...")
    for i in range(max_attempts):
        try:
            response = requests.get(base_url, timeout=5)
            if response.status_code == 200:
                print("Interface web do Zabbix está acessível.")
                return True
        except requests.exceptions.ConnectionError:
            pass # Connection refused, retry
        except Exception as e:
            print(f"Erro inesperado ao verificar a interface web: {e}")
        
        print(f"   Tentativa {i + 1}/{max_attempts}: Interface web ainda não disponível. Aguardando {delay} segundos...")
        time.sleep(delay)
    print("❌ Falha: Interface web do Zabbix não ficou disponível a tempo.")
    return False

def wait_and_setup_zabbix(max_attempts=10):
    """Aguarda o Zabbix estar disponível e executa a configuração"""
    
    base_url = "http://zabbix-web:8080" # Define base_url here for wait_for_web_interface
    if not wait_for_web_interface(base_url):
        return False

    for attempt in range(max_attempts):
        print(f"\nTentativa {attempt + 1}/{max_attempts} (Configuração)")
        
        try:
            if setup_zabbix_initial_config():
                print("✅ Zabbix configurado com sucesso!")
                return True
        except Exception as e:
            print(f"   ✗ Erro durante a configuração: {e}")
        
        if attempt < max_attempts - 1:
            print("   Aguardando 30 segundos antes de re-tentar a configuração...")
            time.sleep(30)
    
    print("❌ Falha na configuração automática do Zabbix")
    return False


if __name__ == "__main__":
    if wait_and_setup_zabbix():
        print("\n🎉 Zabbix está pronto! Executando provisionamento...")
        
        # Agora executa o provisionamento
        try:
            from provisioning import main as provision_main
            exit(provision_main())
        except Exception as e:
            print(f"Erro no provisionamento: {e}")
            exit(1)
    else:
        print("\n💥 Configuração automática falhou.")
        print("Configure manualmente em: http://localhost:8051")
        exit(1)