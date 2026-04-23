import gc
import os
import hmac
import hashlib
import time
import requests
import json
from dotenv import load_dotenv

def get_signature(query_string, secret_key):
    return hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def buy_btc_with_eur():
    load_dotenv()
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    base_url = "https://api.binance.com"
    
    # Check EUR balance first
    timestamp = int(time.time() * 1000)
    query = f"timestamp={timestamp}"
    signature = get_signature(query, api_secret)
    headers = {'X-MBX-APIKEY': api_key}
    
    acc_resp = requests.get(f"{base_url}/api/v3/account?{query}&signature={signature}", headers=headers)
    balances = acc_resp.json().get('balances', [])
    eur_balance = next((float(b['free']) for b in balances if b['asset'] == 'EUR'), 0)
    
    print(f"Current EUR Balance: {eur_balance}")
    
    if eur_balance < 10:
        print("EUR balance too low for a safe market buy (Binance min is ~10 EUR).")
        return

    # Use 95% of available EUR to account for fees
    buy_amount_eur = round(eur_balance * 0.95, 2)
    print(f"Attempting to buy BTC with {buy_amount_eur} EUR...")
    
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": "BTCEUR",
        "side": "BUY",
        "type": "MARKET",
        "quoteOrderQty": buy_amount_eur,
        "timestamp": timestamp,
        "newClientOrderId": f"agent-btc-buy-{int(time.time())}"
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    signature = get_signature(query_string, api_secret)
    
    order_resp = requests.post(f"{base_url}/api/v3/order?{query_string}&signature={signature}", headers=headers)
    print(f"Order Response: {json.dumps(order_resp.json(), indent=2)}")

if __name__ == "__main__":
    buy_btc_with_eur()
