import gc
import os
from dotenv import load_dotenv
import time, hmac, hashlib, requests, json

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
BASE_URL = "https://api.binance.com"

def sign(query):
    return hmac.new(API_SECRET.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()

def get_balances():
    ts = int(time.time() * 1000)
    query = f"timestamp={ts}"
    signature = sign(query)
    url = f"{BASE_URL}/api/v3/account?{query}&signature={signature}"
    r = requests.get(url, headers={"X-MBX-APIKEY": API_KEY})
    return r.json()

def get_prices(symbols):
    r = requests.get(f"{BASE_URL}/api/v3/ticker/price")
    prices_list = r.json()
    return {item['symbol']: float(item['price']) for item in prices_list if item['symbol'] in symbols}

try:
    balances_data = get_balances()
    relevant = ['EUR', 'USDT', 'SOL', 'BTC', 'ETH', 'BNB']
    assets = {b['asset']: float(b['free']) for b in balances_data.get('balances', []) if b['asset'] in relevant}
    
    symbols = ['BTCEUR', 'ETHEUR', 'SOLEUR', 'BNBEUR']
    prices = get_prices(symbols)
    
    total_eur = assets.get('EUR', 0)
    for asset, qty in assets.items():
        if asset == 'EUR' or asset == 'USDT': continue # Simplification
        pair = f"{asset}EUR"
        if pair in prices:
            total_eur += qty * prices[pair]
            
    print(json.dumps({"assets": assets, "total_eur": round(total_eur, 2), "prices": prices}))
except Exception as e:
    import traceback
    print(json.dumps({"error": str(e), "trace": traceback.format_exc()}))
