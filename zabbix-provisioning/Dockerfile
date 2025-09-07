FROM python:3.9-slim

WORKDIR /app

# Instala as dependências
RUN pip install pyzabbix pyyaml

# Copia os arquivos
COPY ./templates /templates
COPY ./hosts.yaml .
COPY ./provisioning.py .

CMD ["python", "provisioning.py"]
