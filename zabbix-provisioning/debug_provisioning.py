#!/usr/bin/env python3
import os
import time
import yaml
import requests
from pyzabbix import ZabbixAPI, ZabbixAPIException

def test_connectivity():
    """Testa a conectividade com os serviços"""
    print("=== Teste de Conectividade ===")
    
    # Testa conexão com zabbix-web
    web_urls = [
        "http://zabbix-web:8080",
        "http://zabbix-web:8080/api_jsonrpc.php",
        "http://zabbix-server/api_jsonrpc.php"
    ]
    
    for url in web_urls:
        try:
            print(f"Testando {url}...")
            response = requests.get(url, timeout=5)
            print(f"  ✓ Status: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Erro: {e}")
    
    print()

def test_api_login():
    """Testa login na API do Zabbix"""
    print("=== Teste de Login na API ===")
    
    urls_to_try = [
        "http://zabbix-web:8080/api_jsonrpc.php",
        "http://zabbix-server/api_jsonrpc.php"
    ]
    
    for url in urls_to_try:
        try:
            print(f"Tentando login em {url}...")
            zapi = ZabbixAPI(url)
            zapi.session.verify = False
            zapi.user.login("Admin", "zabbix")
            print(f"  ✓ Login bem-sucedido!")
            
            # Testa algumas operações básicas
            version = zapi.apiinfo.version()
            print(f"  ✓ Versão do Zabbix: {version}")
            
            hosts = zapi.host.get(output=['hostid', 'host'])
            print(f"  ✓ Hosts existentes: {len(hosts)}")
            for host in hosts:
                print(f"    - {host['host']} (ID: {host['hostid']})")
            
            templates = zapi.template.get(output=['templateid', 'name'])
            print(f"  ✓ Templates existentes: {len(templates)}")
            for template in templates[:5]:  # Mostra apenas os primeiros 5
                print(f"    - {template['name']}")
            
            groups = zapi.hostgroup.get(output=['groupid', 'name'])
            print(f"  ✓ Grupos existentes: {len(groups)}")
            for group in groups:
                print(f"    - {group['name']} (ID: {group['groupid']})")
            
            zapi.user.logout()
            return True
            
        except Exception as e:
            print(f"  ✗ Erro: {e}")
    
    return False

def test_file_access():
    """Testa acesso aos arquivos necessários"""
    print("=== Teste de Acesso a Arquivos ===")
    
    files_to_check = [
        "/app/hosts.yaml",
        "/templates/template_kasa.yaml"
    ]
    
    for file_path in files_to_check:
        try:
            if os.path.exists(file_path):
                print(f"  ✓ {file_path} existe")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"    Tamanho: {len(content)} caracteres")
                    if file_path.endswith('.yaml'):
                        try:
                            data = yaml.safe_load(content)
                            print(f"    YAML válido: {type(data)}")
                            if file_path.endswith('hosts.yaml'):
                                hosts = data.get('hosts', [])
                                print(f"    Hosts definidos: {len(hosts)}")
                                for host in hosts:
                                    print(f"      - {host.get('host', 'sem nome')}")
                        except Exception as e:
                            print(f"    ✗ Erro no YAML: {e}")
            else:
                print(f"  ✗ {file_path} não existe")
        except Exception as e:
            print(f"  ✗ Erro ao acessar {file_path}: {e}")
    
    print()

def main():
    print("=== DEBUG DO PROVISIONAMENTO ZABBIX ===\n")
    
    # Variáveis de ambiente
    print("=== Variáveis de Ambiente ===")
    env_vars = ['ZABBIX_URL', 'ZABBIX_USER', 'ZABBIX_PASSWORD']
    for var in env_vars:
        value = os.environ.get(var, 'NÃO DEFINIDA')
        if 'PASSWORD' in var and value != 'NÃO DEFINIDA':
            value = '*' * len(value)
        print(f"{var}: {value}")
    print()
    
    # Testes
    test_file_access()
    test_connectivity()
    
    if test_api_login():
        print("\n=== TODOS OS TESTES BÁSICOS PASSARAM ===")
        print("Executando provisionamento real...")
        
        # Importa e executa o script original
        try:
            from provisioning import main as provision_main
            return provision_main()
        except Exception as e:
            print(f"Erro ao executar provisionamento: {e}")
            return 1
    else:
        print("\n=== FALHA NOS TESTES BÁSICOS ===")
        print("Verifique a conectividade e configuração.")
        return 1

if __name__ == "__main__":
    exit(main())