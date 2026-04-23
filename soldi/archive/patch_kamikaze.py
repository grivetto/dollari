import ccxt
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv('.env.bitget')
bitget = ccxt.bitget({
    'apiKey': os.getenv('BITGET_API_KEY'),
    'secret': os.getenv('BITGET_API_SECRET'),
    'password': os.getenv('BITGET_PASSWORD'),
    'enableRateLimit': True,
    'options': {'defaultType': 'swap'}
})

try:
    pos = bitget.fetch_positions(['SOL/USDT:USDT'])
    for p in pos:
        if float(p['contracts']) > 0:
            print(f"OPEN POSITION: {p['contracts']} at {p['entryPrice']}")
except Exception as e:
    print(f"Error: {e}")
