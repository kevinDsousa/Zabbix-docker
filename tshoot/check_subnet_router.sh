#!/bin/bash

# ==============================================================================
# Script de Diagnóstico de Rede Tailscale - Lado Subnet Router
# ==============================================================================
# OBJETIVO:
#   Verificar se esta máquina (o subnet router) está configurada corretamente
#   para anunciar sua rede local e rotear o tráfego do Tailscale para ela.
#
# PRÉ-REQUISITO:
#   Este script usa o comando 'jq' para analisar a saída JSON do Tailscale.
#   Instale-o com: sudo apt update && sudo apt install -y jq
#
# COMO USAR:
#   1. Salve este código como 'check_subnet_router.sh'.
#   2. Dê permissão de execução: chmod +x check_subnet_router.sh
#   3. Execute com a sub-rede que você está tentando anunciar:
#      sudo ./check_subnet_router.sh 192.168.0.0/24
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

if ! command -v jq &> /dev/null; then
    print_error "O comando 'jq' não foi encontrado."
    print_info "Por favor, instale-o com: sudo apt install jq"
    exit 1
fi

SUBNET_CIDR=$1
if [ -z "$SUBNET_CIDR" ]; then
    print_error "Uso incorreto."
    echo "Por favor, forneça a sub-rede em formato CIDR."
    echo "Exemplo: sudo $0 192.168.0.0/24"
    exit 1
fi

clear
echo "========================================================"
echo "  Iniciando Diagnóstico Tailscale - Lado Subnet Router"
echo "  Sub-rede: $SUBNET_CIDR"
echo "========================================================"
echo

# --- PASSO 1: Verificar o encaminhamento de IP no Kernel ---
print_info "1. Verificando se o encaminhamento de IP (IP forwarding) está ativo..."
FORWARD_STATUS=$(cat /proc/sys/net/ipv4/ip_forward)
if [ "$FORWARD_STATUS" -eq 1 ]; then
    print_success "Encaminhamento de IP está ativo (valor = 1)."
else
    print_error "Encaminhamento de IP está DESATIVADO (valor = 0)."
    print_info "SOLUÇÃO: Execute 'echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward'."
fi
echo

# --- PASSO 2: Verificar as configurações do Tailscale ---
print_info "2. Verificando as configurações do Tailscale..."
TS_STATUS_JSON=$(tailscale status --json)

# Checa se a rota está sendo anunciada
if echo "$TS_STATUS_JSON" | jq -e ".Self.AdvertisedRoutes | index(\"$SUBNET_CIDR\")" &> /dev/null; then
    print_success "A sub-rede $SUBNET_CIDR está sendo anunciada corretamente."
else
    print_error "A sub-rede $SUBNET_CIDR NÃO está sendo anunciada."
fi

# Checa se o SNAT (NAT) está ativo
if sudo iptables -t nat -C POSTROUTING -s $(tailscale ip -4 | cut -d/ -f1)/32 -d $SUBNET_CIDR -j MASQUERADE &> /dev/null || \
   sudo iptables -t nat -C ts-postrouting -s $(tailscale ip -4 | cut -d/ -f1)/32 -d $SUBNET_CIDR -j MASQUERADE &> /dev/null; then
    print_success "A regra de SNAT (NAT) para a sub-rede parece estar ativa."
else
    print_error "NÃO foi encontrada uma regra de SNAT (NAT) para a sub-rede."
fi
print_info "SOLUÇÃO (para ambos os problemas acima):"
print_info "Execute 'sudo tailscale up --advertise-routes=$SUBNET_CIDR --snat-subnet-routes=true'"
echo

# --- PASSO 3: Verificar o firewall UFW ---
print_info "3. Verificando as regras do firewall (UFW)..."
if ! command -v ufw &> /dev/null; then
    print_info "Firewall UFW não encontrado. Pulando esta verificação."
else
    LAN_INTERFACE=$(ip route get 1.1.1.1 | awk '{print $5}' | head -n1)
    if [ -z "$LAN_INTERFACE" ]; then
        print_error "Não foi possível detectar a interface de rede local."
    else
        print_info "Interface de rede local detectada: $LAN_INTERFACE"
        
        # Checa regra de entrada tailscale -> lan
        if sudo ufw status verbose | grep -q "ALLOW IN ON tailscale0 OUT ON $LAN_INTERFACE"; then
            print_success "Regra de firewall encontrada para permitir tráfego de Tailscale -> Rede Local."
        else
            print_error "Falta regra de firewall para permitir tráfego de Tailscale -> Rede Local."
            print_info "SOLUÇÃO: sudo ufw route allow in on tailscale0 out on $LAN_INTERFACE"
        fi
        
        # Checa regra de saída lan -> tailscale (para respostas)
        if sudo ufw status verbose | grep -q "ALLOW IN ON $LAN_INTERFACE OUT ON tailscale0"; then
            print_success "Regra de firewall encontrada para permitir respostas da Rede Local -> Tailscale."
        else
            print_error "Falta regra de firewall para permitir respostas da Rede Local -> Tailscale."
            print_info "SOLUÇÃO: sudo ufw route allow in on $LAN_INTERFACE out on tailscale0"
        fi
    fi
fi
echo

echo "========================================================"
echo "  Diagnóstico Concluído."
echo "========================================================"