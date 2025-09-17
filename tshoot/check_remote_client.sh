#!/bin/bash

# ==============================================================================
# Script de Diagnóstico de Rede Tailscale - Lado Cliente
# ==============================================================================
# OBJETIVO:
#   Verificar se esta máquina (cliente) está configurada corretamente para
#   acessar uma sub-rede remota anunciada via Tailscale.
#
# COMO USAR:
#   1. Salve este código como 'check_remote_client.sh'.
#   2. Dê permissão de execução: chmod +x check_remote_client.sh
#   3. Execute com o IP do dispositivo que você quer alcançar na sub-rede:
#      sudo ./check_remote_client.sh 192.168.0.3
# ==============================================================================

# --- Cores para a saída ---
COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_NC='\033[0m' # No Color

print_info() {
    echo -e "${COLOR_YELLOW}[INFO] $1${COLOR_NC}"
}

print_success() {
    echo -e "${COLOR_GREEN}[SUCESSO] $1${COLOR_NC}"
}

print_error() {
    echo -e "${COLOR_RED}[FALHA] $1${COLOR_NC}"
}

# --- Verificação Inicial ---
if [[ $EUID -ne 0 ]]; then
   print_error "Este script precisa ser executado como root (use sudo)."
   exit 1
fi

TARGET_IP=$1
if [ -z "$TARGET_IP" ]; then
    print_error "Uso incorreto."
    echo "Por favor, forneça o endereço IP do dispositivo de destino."
    echo "Exemplo: sudo $0 192.168.0.3"
    exit 1
fi

clear
echo "========================================================"
echo "  Iniciando Diagnóstico Tailscale - Lado Cliente"
echo "  Alvo: $TARGET_IP"
echo "========================================================"
echo

# --- PASSO 1: Verificar status do Tailscale ---
print_info "1. Verificando o status do serviço Tailscale..."
if ! tailscale status &> /dev/null; then
    print_error "O serviço Tailscale não está rodando ou não está conectado."
    print_info "Tente executar: sudo tailscale up"
    exit 1
else
    print_success "Serviço Tailscale está ativo."
fi
echo

# --- PASSO 2: Verificar se as rotas da sub-rede são aceitas ---
print_info "2. Verificando se esta máquina aceita sub-redes remotas..."
IP_PREFIX=$(echo $TARGET_IP | cut -d. -f1-3).0
SUBNET_CIDR="${IP_PREFIX}/24" # Assume máscara /24, comum em redes domésticas

if ip route | grep -q "$SUBNET_CIDR dev tailscale0"; then
    print_success "A rota para a sub-rede $SUBNET_CIDR existe na tabela de roteamento."
else
    print_error "A rota para a sub-rede $SUBNET_CIDR NÃO foi encontrada."
    print_info "SOLUÇÃO: Execute 'sudo tailscale up --accept-routes' nesta máquina."
    # Não vamos parar o script, pois os testes de conectividade ainda podem ser úteis.
fi
echo

# --- PASSO 3: Testes de Conectividade ---
print_info "3. Executando testes de conectividade para $TARGET_IP..."
echo "   (Isso pode demorar alguns segundos)"
echo

# Teste de Ping (ICMP)
echo "   a) Testando com PING..."
if ping -c 3 -W 3 $TARGET_IP &> /dev/null; then
    print_success "O dispositivo $TARGET_IP respondeu ao ping."
else
    print_error "O dispositivo $TARGET_IP NÃO respondeu ao ping."
    print_info "  Isso pode ser normal se o dispositivo ou um firewall bloqueia pings (ICMP)."
fi

# Teste de Rota (tracepath)
echo "   b) Rastreando a rota com TRACEPATH..."
tracepath $TARGET_IP

# Teste de Serviço (HTTP com curl)
echo "   c) Testando conexão na porta 80 (HTTP) com cURL..."
if curl --connect-timeout 5 -sI http://$TARGET_IP | grep -q "200 OK"; then
    print_success "O dispositivo $TARGET_IP respondeu com '200 OK' na porta 80."
    print_info "  A comunicação está funcionando!"
else
    print_error "O dispositivo $TARGET_IP não respondeu na porta 80 (HTTP) ou não retornou '200 OK'."
fi
echo

echo "========================================================"
echo "  Diagnóstico Concluído."
echo "========================================================"