FROM zabbix/zabbix-agent:alpine-6.4-latest

USER root

RUN apk add --no-cache python3 py3-pip git

RUN git clone https://github.com/python-kasa/python-kasa.git /tmp/python-kasa

RUN pip3 install --no-cache-dir --break-system-packages /tmp/python-kasa

RUN rm -rf /tmp/python-kasa

RUN mkdir -p /etc/zabbix/scripts/

COPY scripts/get_p110_power.py /etc/zabbix/scripts/get_p110_power.py

COPY conf/kasa.conf /etc/zabbix/zabbix_agentd.d/kasa.conf

RUN chown -R zabbix:zabbix /etc/zabbix/scripts && \
    chmod +x /etc/zabbix/scripts/get_p110_power.py

USER zabbix


