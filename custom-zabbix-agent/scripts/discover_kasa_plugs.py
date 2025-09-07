#!/usr/bin/env python3
import asyncio
import json
from kasa import Discover

async def find_plugs():
    """
    Descobre todas as tomadas Kasa na rede e formata a saída em JSON para o LLD do Zabbix.
    """
    plugs_list = []
    try:
        # Descobre todos os dispositivos na rede em 5 segundos
        found_devices = await Discover.discover(timeout=5)

        for ip, dev in found_devices.items():
            # Apenas adiciona dispositivos que têm medidor de energia
            if dev.has_emeter:
                plugs_list.append({
                    "{#PLUGIP}": ip,
                    "{#PLUGALIAS}": dev.alias  # O nome que você deu para a tomada no app Kasa
                })

    except Exception:
        # Se ocorrer um erro, não retorna nada
        pass
    
    # O Zabbix LLD espera um JSON com uma chave "data" contendo a lista
    print(json.dumps({"data": plugs_list}))

if __name__ == "__main__":
    asyncio.run(find_plugs())
