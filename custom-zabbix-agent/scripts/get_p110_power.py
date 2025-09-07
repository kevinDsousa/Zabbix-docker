#!/usr/bin/env python3
import sys
import asyncio
import os  # MUDANÇA 1: Importamos o módulo 'os' para acessar as variáveis de ambiente
from kasa import Discover
from kasa.credentials import Credentials

async def get_power(device_ip, email, password):
    # A lógica de conexão permanece a mesma
    try:
        creds = Credentials(email, password)
        dev = await asyncio.wait_for(
            Discover.discover_single(device_ip, credentials=creds), 
            timeout=15
        )
        await dev.update()

        if dev.has_emeter:
            power_watts = dev.emeter_realtime["power"]
            print(power_watts)
        else:
            print(f"ERRO: O dispositivo em {device_ip} não suporta medição de energia.", file=sys.stderr)

    except Exception as e:
        print(f"ERRO: Ocorreu uma exceção ao conectar com {device_ip}: {type(e).__name__}: {e}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERRO: O endereço IP do dispositivo é necessário como argumento.", file=sys.stderr)
        sys.exit(1)

    # MUDANÇA 2: Lemos o e-mail e a senha das variáveis de ambiente
    # Os nomes ("KASA_USERNAME", "KASA_PASSWORD") devem ser os mesmos do seu docker-compose.yml
    email = os.environ.get("KASA_USERNAME")
    password = os.environ.get("KASA_PASSWORD")

    if not email or not password:
        print("ERRO: As variáveis de ambiente KASA_USERNAME e KASA_PASSWORD não estão definidas.", file=sys.stderr)
        sys.exit(1)

    DEVICE_IP = sys.argv[1]
    asyncio.run(get_power(DEVICE_IP, email, password))
