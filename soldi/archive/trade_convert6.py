import gc
import os
import hmac
import hashlib
import time
import requests
import json
from dotenv import load_dotenv

def sign(req, secret):
    # Method + ID + API Key + Sorted Params + Nonce
    param_str = ""
    if "params" in req:
        # Sort keys alphabetically
        sorted_keys = sorted(req["params"].keys())
        for key in sorted_keys:
            val = req["params"][key]
            if val is None:
                val = ""
            param_str += key + str(val)
            
    sig_payload = req["method"] + str(req["id"]) + req["api_key"] + param_str + str(req["nonce"])
    return hmac.new(
        bytes(secret, 'utf-8'),
        msg=bytes(sig_payload, 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

def convert_usd_to_usdt():
    load_dotenv()
    api_key = os.getenv('CRYPTOCOM_API_KEY')
    api_secret = os.getenv('CRYPTOCOM_API_SECRET')
    
    # 1. Get current USD balance
    nonce = int(time.time() * 1000)
    req_bal = {
        "id": 70,
        "method": "private/get-account-summary",
        "api_key": api_key,
        "params": {},
        "nonce": nonce
    }
    req_bal['sig'] = sign(req_bal, api_secret)
    
    resp = requests.post('https://api.crypto.com/v2/private/get-account-summary', json=req_bal)
    data = resp.json()
    
    usd_balance = 0
    if data.get('result') and data['result'].get('accounts'):
        for acc in data['result']['accounts']:
            if acc['currency'] == 'USD':
                usd_balance = acc['available']
                break
    
    print(f"USD Balance detected: {usd_balance}")
    if usd_balance < 1.0:
        return

    # 2. Create Market Buy order for USDT using USD (instrument USDT_USD)
    nonce = int(time.time() * 1000)
    req_order = {
        "id": 71,
        "method": "private/create-order",
        "api_key": api_key,
        "params": {
            "instrument_name": "USDT_USD",
            "side": "BUY",
            "type": "MARKET",
            "notional": usd_balance
        },
        "nonce": nonce
    }
    req_order['sig'] = sign(req_order, api_secret)
    
    resp = requests.post('https://api.crypto.com/v2/private/create-order', json=req_order)
    print(json.dumps(resp.json(), indent=2))

if __name__ == "__main__":
    convert_usd_to_usdt()
