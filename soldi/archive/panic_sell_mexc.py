import ccxt
import os
from dotenv import load_dotenv
import time

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env.mexc')
mexc = ccxt.mexc({'apiKey': os.getenv('MEXC_API_KEY'), 'secret': os.getenv('MEXC_API_SECRET'), 'enableRateLimit': True, 'options': {'defaultType': 'spot'}})

balance = mexc.fetch_balance()
for asset, amount in balance['free'].items():
    if asset != 'USDT' and amount > 0:
        symbol = f"{asset}/USDT"
        try:
            mexc.load_markets()
            ticker = mexc.fetch_ticker(symbol)
            if ticker['last'] * amount > 5: # Only sell if > 5 USDT
                mexc.create_market_sell_order(symbol, amount)
                print(f"Sold {amount} of {symbol}")
        except Exception as e:
            print(f"Could not sell {symbol}: {e}")
print("Cleaned up orphans.")
