import os, time
from binance.client import Client
from dotenv import load_dotenv

load_dotenv("/home/sergio/.openclaw/workspace/denaro/.env")
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

def market_sell(symbol, qty):
    try:
        order = client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
        print(f"✅ VENDUTO {qty} {symbol}")
    except Exception as e:
        print(f"❌ ERRORE {symbol}: {e}")

account = client.get_account()
for bal in account['balances']:
    asset = bal['asset']
    free = float(bal['free'])
    if asset == 'SOL' and free > 0.5:
        # Arrotonda per Binance precision
        qty = round(free * 0.5, 2)
        market_sell('SOLEUR', qty)
    elif asset == 'DOGE' and free > 100:
        qty = int(free * 0.5)
        market_sell('DOGEEUR', qty)
    elif asset == 'DOT' and free > 10:
        qty = round(free * 0.5, 2)
        market_sell('DOTEUR', qty)
    elif asset == 'LINK' and free > 2:
        qty = round(free * 0.5, 2)
        market_sell('LINKEUR', qty)
    elif asset == 'BNB' and free > 0.1:
        qty = round(free * 0.5, 3)
        market_sell('BNBEUR', qty)

time.sleep(2)
acc = client.get_account()
eur = [b['free'] for b in acc['balances'] if b['asset'] == 'EUR']
print(f"💼 NUOVO SALDO EUR DISPONIBILE: {eur[0]} €")
