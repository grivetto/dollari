import subprocess
import re

def ping(host):
    try:
        # ping -c 4 -W 2 host
        result = subprocess.run(['ping', '-c', '4', '-W', '2', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            # Estrai avg rtt
            match = re.search(r'min/avg/max/mdev = [\d\.]+/([\d\.]+)/', result.stdout)
            if match:
                return float(match.group(1))
    except Exception:
        pass
    return None

exchanges = {
    'Binance (Global)': 'api.binance.com',
    'Binance (EU/US/Asia CDN)': 'api1.binance.com',
    'Bitget': 'api.bitget.com',
    'Bybit': 'api.bybit.com',
    'OKX': 'aws.okx.com',
    'MEXC': 'api.mexc.com',
    'Coinbase': 'api.coinbase.com',
    'Kraken': 'api.kraken.com'
}

print("Analisi latenza Centro Stella attuale (Francoforte - Nuvola):")
for name, host in exchanges.items():
    avg_ping = ping(host)
    status = f"{avg_ping:.2f} ms" if avg_ping is not None else "TIMEOUT"
    print(f"- {name:<25}: {status:>10}")
