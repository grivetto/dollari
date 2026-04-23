import ccxt
import os
from dotenv import load_dotenv
import json

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
tot_investito = b + bg + m

try:
    with open('/home/sergio/.openclaw/workspace/denaro/vault.json', 'r') as f:
        vault = json.load(f)
        cassaforte = vault.get('LOCKED_EUR', 0)
except:
    cassaforte = 222.0

CAPITALE_START_GIOCO = 500.0

drawdown_gioco = tot_investito - CAPITALE_START_GIOCO

print(f"=========================================")
print(f"💰 RESOCONTO ASSOLUTO (In Euro/Dollari Equivalenti)")
print(f"=========================================")
print(f"I tuoi '500' iniziali da giocare si trovano ora sparsi su:")
print(f" - BINANCE: {b:.2f}")
print(f" - BITGET: {bg:.2f}")
print(f" - MEXC: {m:.2f}")
print(f"-----------------------------------------")
print(f"🎯 TOTALE IN GIOCO OGGI: {tot_investito:.2f}")
print(f"🔻 DRAWDOWN REALE SUI 500: {drawdown_gioco:+.2f}")
print(f"=========================================")
print(f"🔐 CASSAFORTE (Intatta): {cassaforte:.2f}")
print(f"=========================================")

