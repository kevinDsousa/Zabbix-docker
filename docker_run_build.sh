#!/bin/bash
# SCRIPT FINAL PARA GARANTIR UMA RECONSTRUÇÃO COMPLETA E SEM CACHE (V2)

# 'set -e' faz com que o script pare imediatamente se algum comando falhar.
set -e

# Configurações
CONFIG_FILE="docker-compose.yml"
IMAGE_NAME="custom-zabbix-agent:latest"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}--- INICIANDO PROCESSO DE BUILD FINAL E DEFINITIVO ---${NC}"

# --- PASSO 1: LIMPEZA COMPLETA ---
echo -e "\n${YELLOW}[1/4] Parando e removendo containers, volumes e redes antigas...${NC}"
docker-compose -f "$CONFIG_FILE" down --volumes

# --- PASSO 2: REMOÇÃO FORÇADA DA IMAGEM ANTIGA ---
echo -e "\n${YELLOW}[2/4] Removendo a imagem antiga '$IMAGE_NAME' para evitar cache...${NC}"
docker rmi $IMAGE_NAME || true

# Removendo a imagem do provisionador para garantir que as mudanças no Dockerfile sejam aplicadas
docker rmi zabbix-docker-zabbix-provisioner || true

# --- PASSO 3: RECONSTRUÇÃO FORÇADA SEM CACHE ---
# Separamos o 'build' do 'up' para compatibilidade com a sua versão do docker-compose.
echo -e "\n${YELLOW}[3/4] Reconstruindo a imagem do agente SEM CACHE...${NC}"
echo -e "${YELLOW}Este passo PODE DEMORAR VÁRIOS MINUTOS. Por favor, aguarde...${NC}"
docker-compose -f "$CONFIG_FILE" build --no-cache zabbix-agent

# --- PASSO 4: INICIAR O AMBIENTE COMPLETO ---
echo -e "\n${YELLOW}[4/4] Iniciando todos os containers com a nova imagem...${NC}"
docker-compose -f "$CONFIG_FILE" up -d --force-recreate

echo -e "\n${GREEN}--- PROCESSO CONCLUÍDO COM SUCESSO! ---${NC}"
echo -e "${YELLOW}Verificando status final dos containers:${NC}"
docker-compose -f "$CONFIG_FILE" ps
echo -e "\n${GREEN}Acesse a interface do Zabbix em http://localhost:8051${NC}"


