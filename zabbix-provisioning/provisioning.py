import os
import time
import yaml
from pyzabbix import ZabbixAPI, ZabbixAPIException

# --- Configurações ---
ZABBIX_URL = os.environ.get("ZABBIX_URL", "http://zabbix-server/api_jsonrpc.php")
ZABBIX_USER = os.environ.get("ZABBIX_USER", "Admin")
ZABBIX_PASSWORD = os.environ.get("ZABBIX_PASSWORD", "zabbix")
TEMPLATES_DIR = "/templates"
HOSTS_FILE = "/app/hosts.yaml" # Caminho para o arquivo de hosts dentro do container

def wait_for_zabbix_api(zapi):
    # (Esta função permanece a mesma)
    print("Aguardando a API do Zabbix ficar disponível...")
    for _ in range(30):
        try:
            zapi.is_available()
            print("API do Zabbix está pronta.")
            return True
        except Exception:
            time.sleep(10)
    print("Erro: A API do Zabbix não ficou disponível a tempo.")
    return False

def import_templates(zapi):
    # (Esta função permanece a mesma)
    print("\n--- Iniciando importação de Templates ---")
    import_rules = {
        'templates': {'createMissing': True, 'updateExisting': True},
        'templateLinkage': {'createMissing': True},
        'items': {'createMissing': True, 'updateExisting': True},
        'triggers': {'createMissing': True, 'updateExisting': True},
        'discoveryRules': {'createMissing': True, 'updateExisting': True}
    }
    template_path = os.path.join(TEMPLATES_DIR, "template_kasa.yaml")
    try:
        with open(template_path, 'r') as f:
            template_content = f.read()
            zapi.configuration.import_(format='yaml', source=template_content, rules=import_rules)
            print(f"Template '{template_path}' importado com sucesso.")
    except Exception as e:
        print(f"Erro ao importar o template '{template_path}': {e}")

def provision_hosts(zapi):
    """Lê o arquivo hosts.yaml e cria os hosts que não existem."""
    print("\n--- Iniciando provisionamento de Hosts ---")
    try:
        with open(HOSTS_FILE, 'r') as f:
            config = yaml.safe_load(f)
            hosts_to_create = config.get('hosts', [])
    except FileNotFoundError:
        print(f"Arquivo de hosts '{HOSTS_FILE}' não encontrado. Pulando criação de hosts.")
        return

    for host_data in hosts_to_create:
        host_name = host_data['host']
        print(f"Verificando host: '{host_name}'...")

        # Verifica se o host já existe
        if zapi.host.get(filter={'host': host_name}):
            print(f"Host '{host_name}' já existe. Pulando.")
            continue

        # Se não existe, vamos criá-lo
        try:
            # Pega os IDs dos grupos
            group_names = host_data['groups']
            group_ids = [g['groupid'] for g in zapi.hostgroup.get(filter={'name': group_names})]
            if not group_ids:
                print(f"AVISO: Nenhum grupo encontrado para '{host_name}'. Verifique os nomes dos grupos.")
                continue

            # Pega os IDs dos templates
            template_names = host_data['templates']
            template_ids = [t['templateid'] for t in zapi.template.get(filter={'name': template_names})]
            if not template_ids:
                print(f"AVISO: Nenhum template encontrado para '{host_name}'. Verifique os nomes dos templates.")
                continue

            # Cria o host
            zapi.host.create(
                host=host_name,
                name=host_data['name'],
                interfaces=[{
                    'type': 1, # 1 = Zabbix Agent
                    'main': 1,
                    'useip': 1,
                    'ip': host_data['ip'],
                    'dns': '',
                    'port': '10050'
                }],
                groups=[{'groupid': gid} for gid in group_ids],
                templates=[{'templateid': tid} for tid in template_ids]
            )
            print(f"Host '{host_name}' criado com sucesso!")

        except Exception as e:
            print(f"Erro ao criar o host '{host_name}': {e}")

def main():
    zapi = ZabbixAPI(ZABBIX_URL)
    if not wait_for_zabbix_api(zapi):
        return

    try:
        zapi.login(ZABBIX_USER, ZABBIX_PASSWORD)
        print(f"Login na API do Zabbix ({ZABBIX_URL}) realizado com sucesso.")
    except ZabbixAPIException as e:
        print(f"Falha no login da API do Zabbix: {e}")
        return

    # Executa as tarefas
    import_templates(zapi)
    provision_hosts(zapi)
    
    zapi.user.logout()
    print("\nLogout da API realizado. Provisionamento concluído.")

if __name__ == "__main__":
    main()
