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

def sell_sol_for_eur():
    load_dotenv()
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    base_url = "https://api.binance.com"
    
    # Sell 0.5 SOL to replenish liquidity
    sell_qty = 0.5
    timestamp = int(time.time() * 1000)
    
    params = {
        "symbol": "SOLEUR",
        "side": "SELL",
        "type": "MARKET",
        "quantity": sell_qty,
        "timestamp": timestamp,
        "newClientOrderId": f"agent-sol-sell-{int(time.time())}"
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    signature = get_signature(query_string, api_secret)
    headers = {'X-MBX-APIKEY': api_key}
    
    order_resp = requests.post(f"{base_url}/api/v3/order?{query_string}&signature={signature}", headers=headers)
    print(f"Order Response: {json.dumps(order_resp.json(), indent=2)}")

if __name__ == "__main__":
    sell_sol_for_eur()
