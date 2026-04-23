import gc
import os
import hmac
import hashlib
import time
import requests
import json
from dotenv import load_dotenv

def sign(req, secret):
    param_str = ""
    if "params" in req:
        sorted_keys = sorted(req["params"].keys())
        for key in sorted_keys:
            val = req["params"][key]
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
    
    # Sell USD for USDT means Buying USDT with USD
    # Let's try 8.0 USD to be safe
    nonce = int(time.time() * 1000)
    req_order = {
        "id": 81,
        "method": "private/create-order",
        "api_key": api_key,
        "params": {
            "instrument_name": "USDT_USD",
            "side": "BUY",
            "type": "MARKET",
            "notional": 8.0
        },
        "nonce": nonce
    }
    req_order['sig'] = sign(req_order, api_secret)
    
    resp = requests.post('https://api.crypto.com/v2/private/create-order', json=req_order)
    print(f"Order Attempt: {json.dumps(resp.json(), indent=2)}")

if __name__ == "__main__":
    convert_usd_to_usdt()
