import ccxt
import os
from dotenv import load_dotenv

def get_binance():
    load_dotenv('/home/sergio/denaro/.env')
    exchange = ccxt.binance({'apiKey': os.getenv('BINANCE_API_KEY'), 'secret': os.getenv('BINANCE_API_SECRET')})
    bal = exchange.fetch_balance()
    t = 0
    for c, a in bal.get('total', {}).items():
        if a > 0:
            if c in ['USDT','EUR','USDC']: t += a
            else:
                try: t += a * exchange.fetch_ticker(f"{c}/USDT")['last']
                except: pass
    return t

def get_bitget():
 load_dotenv('/home/sergio/denaro/.env.bitget')
    exchange = ccxt.bitget({'apiKey': os.getenv('BITGET_API_KEY'), 'secret': os.getenv('BITGET_API_SECRET'), 'password': os.getenv('BITGET_PASSWORD'), 'options': {'defaultType': 'swap'}})
    return exchange.fetch_balance()['USDT']['total']

def get_mexc():
 load_dotenv('/home/sergio/denaro/.env.mexc')
    exchange = ccxt.mexc({'apiKey': os.getenv('MEXC_API_KEY'), 'secret': os.getenv('MEXC_API_SECRET')})
    bal = exchange.fetch_balance()
    t = 0
    for c, a in bal.get('total', {}).items():
        if float(a) > 0:
            if c in ['USDT']: t += float(a)
            else:
                try: t += float(a) * float(exchange.fetch_ticker(f"{c}/USDT")['last'])
                except: pass
    return t

b = get_binance()
bg = get_bitget()
m = get_mexc()
print(f"BINANCE SPOT (EUR+Crypto equivalenti in USDT): {b:.2f} $")
print(f"BITGET FUTURES (USDT): {bg:.2f} $")
print(f"MEXC SPOT (Crypto equivalenti in USDT): {m:.2f} $")
print(f"TOTALE GLOBALE (PER NOI AMICI): {b+bg+m:.2f} $")
