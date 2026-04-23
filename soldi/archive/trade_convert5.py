import gc
import os
import hmac
import hashlib
import time
import requests
import json
from dotenv import load_dotenv

def convert_usd_to_usdt():
    load_dotenv()
    api_key = os.getenv('CRYPTOCOM_API_KEY')
    api_secret = os.getenv('CRYPTOCOM_API_SECRET')
    
    if not api_key or not api_secret:
        print("Missing API keys")
        return

    # 1. Get current USD balance
    nonce = int(time.time() * 1000)
    req_bal = {
        "id": 60,
        "method": "private/get-account-summary",
        "api_key": api_key,
        "params": {},
        "nonce": nonce
    }
    
    sig_payload = req_bal['method'] + str(req_bal['id']) + req_bal['api_key'] + str(req_bal['nonce'])
    req_bal['sig'] = hmac.new(api_secret.encode('utf-8'), sig_payload.encode('utf-8'), hashlib.sha256).hexdigest()
    
    resp = requests.post('https://api.crypto.com/v2/private/get-account-summary', json=req_bal)
    data = resp.json()
    
    usd_balance = 0
    if data.get('result') and data['result'].get('accounts'):
        for acc in data['result']['accounts']:
            if acc['currency'] == 'USD':
                usd_balance = acc['available']
                break
    
    if usd_balance < 1.0:
        print(f"USD Balance too low: {usd_balance}")
        return

    # 2. Create Market Buy order for USDT using USD (instrument USDT_USD)
    nonce = int(time.time() * 1000)
    # We use 'notional' to specify how many USD to spend
    req_order = {
        "id": 61,
        "method": "private/create-order",
        "api_key": api_key,
        "params": {
            "instrument_name": "USDT_USD",
            "side": "BUY",
            "type": "MARKET",
            "notional": float(usd_balance)
        },
        "nonce": nonce
    }
    
    # Signature: method + id + api_key + sorted_params + nonce
    # Params: instrument_name, notional, side, type
    param_str = "instrument_nameUSDT_USDnotional" + str(req_order['params']['notional']) + "sideBUYtypeMARKET"
    sig_payload = req_order['method'] + str(req_order['id']) + req_order['api_key'] + param_str + str(req_order['nonce'])
    req_order['sig'] = hmac.new(api_secret.encode('utf-8'), sig_payload.encode('utf-8'), hashlib.sha256).hexdigest()
    
    resp = requests.post('https://api.crypto.com/v2/private/create-order', json=req_order)
    print(json.dumps(resp.json(), indent=2))

if __name__ == "__main__":
    convert_usd_to_usdt()
