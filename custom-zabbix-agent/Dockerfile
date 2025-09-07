# A versão alpine é leve e consistente com seu zabbix-server.
FROM zabbix/zabbix-agent:alpine-6.4-latest

# Mudar para usuário root para instalar pacotes
USER root

# Instalar Python3, pip e o git (necessário para clonar o repositório)
RUN apk add --no-cache python3 py3-pip git

# --- CORREÇÃO DEFINITIVA (MÉTODO ROBUSTO) ---
# 1. Clona manualmente o repositório para garantir que temos o código mais recente.
RUN git clone https://github.com/python-kasa/python-kasa.git /tmp/python-kasa

# 2. Instala a biblioteca a partir da cópia local clonada.
RUN pip3 install --no-cache-dir --break-system-packages /tmp/python-kasa

# 3. Limpa os ficheiros de instalação para manter a imagem pequena.
RUN rm -rf /tmp/python-kasa

# Criar o diretório para os scripts dentro do container
RUN mkdir -p /etc/zabbix/scripts/

# Copiar nosso script local para dentro da imagem do container
COPY scripts/get_p110_power.py /etc/zabbix/scripts/get_p110_power.py

# Copiar nosso ficheiro de configuração do UserParameter para o local correto
COPY conf/kasa.conf /etc/zabbix/zabbix_agentd.d/kasa.conf

# Garantir as permissões corretas
RUN chown -R zabbix:zabbix /etc/zabbix/scripts && \
    chmod +x /etc/zabbix/scripts/get_p110_power.py

# Voltar para o usuário padrão do Zabbix por segurança
USER zabbix


