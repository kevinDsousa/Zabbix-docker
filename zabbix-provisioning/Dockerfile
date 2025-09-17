FROM python:3.9-slim

WORKDIR /app

# Instala as dependências
RUN pip install --no-cache-dir pyzabbix pyyaml requests

# Cria os diretórios necessários
RUN mkdir -p /templates

# Copia os arquivos
COPY ./templates /templates
COPY ./hosts.yaml /app/hosts.yaml
COPY ./provisioning.py /app/provisioning.py
COPY ./debug_provisioning.py /app/debug_provisioning.py

# Torna os scripts executáveis
RUN chmod +x /app/provisioning.py /app/debug_provisioning.py

# Comando padrão
CMD ["python", "/app/provisioning.py"]