import json
import os

SHM_FILE = "/dev/shm/binance_prices.json"
if not os.path.exists(SHM_FILE):
    SHM_FILE = "/tmp/binance_prices.json"

def get_ticker(symbol_ccxt):
    # Converte 'SOL/EUR' in 'SOLEUR'
    raw_symbol = symbol_ccxt.replace('/', '').replace('-', '')
    try:
        with open(SHM_FILE, 'r') as f:
            prices = json.load(f)
            
        if raw_symbol in prices:
            return {'last': float(prices[raw_symbol])}
        else:
            return None
    except Exception as e:
        return None
