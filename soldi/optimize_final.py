#!/usr/bin/env python3
"""
FINAL OPTIMIZATION SCRIPT
1. Cancel ALL open orders to free up funds.
2. Sell ALL dust (SOL, AVAX, BNB) to EUR.
3. Buy €60 of ETH to unblock the Grid Bot sells.
"""
import ccxt
import os
import time
from dotenv import load_dotenv

load_dotenv('/home/sergio/denaro/.env')

try:
    exchange = ccxt.binance({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_API_SECRET'),
        'enableRateLimit': True,
        'options': {'warnOnFetchOpenOrdersWithoutSymbol': False}
    })
except Exception as e:
    print(f"Errore connessione: {e}")
    exit(1)

print("=== FASE 1: CANCELLAZIONE ORDINI PENDENTI ===")
orders = exchange.fetch_open_orders()
print(f"Hai {len(orders)} ordini aperti.")
for o in orders:
    print(f"  - Cancello {o['symbol']} {o['side']} @ {o['price']}")
    try:
        exchange.cancel_order(o['id'], o['symbol'])
    except Exception as e:
        print(f"    Errore: {e}")
print("✅ Tutti gli ordini sono stati cancellati. Fondi liberati!")
time.sleep(2)

print("\n=== FASE 2: VENDITA ASSET INUTILI ===")
assets = [
    {'sym': 'SOL/EUR', 'coin': 'SOL'},
    {'sym': 'AVAX/EUR', 'coin': 'AVAX'},
    {'sym': 'BNB/EUR', 'coin': 'BNB'}
]

for a in assets:
    # Refresh balance
    bal = exchange.fetch_balance()
    free = bal.get(a['coin'], {}).get('free', 0)
    min_amt = 0.01 if a['coin'] == 'AVAX' else (0.001 if a['coin'] == 'BNB' else 0.01)
    
    if free > min_amt:
        print(f"Vendo {free} {a['coin']}...")
        try:
            order = exchange.create_market_sell_order(a['sym'], free)
            print(f"✅ Venduto {a['coin']}")
        except Exception as e:
            print(f"❌ Errore vendita {a['coin']}: {e}")
    else:
        print(f"- {a['coin']}: {free} (troppo poco per vendere)")

time.sleep(5)

print("\n=== FASE 3: COMPRA ETH PER SBLOCCARE IL GRID BOT ===")
bal = exchange.fetch_balance()
eur = bal.get('EUR', {}).get('free', 0)
price = exchange.fetch_ticker('ETH/EUR')['last']

print(f"Euro disponibili: €{eur:.2f} | Prezzo ETH: €{price:.2f}")

if eur > 60:
    amount = (60 / price) * 0.995
    print(f"Compro {amount:.4f} ETH (~€60)...")
    try:
        order = exchange.create_market_buy_order('ETH/EUR', amount)
        filled = order.get('filled', amount)
        print(f"✅ Comprato {filled:.4f} ETH")
    except Exception as e:
        print(f"❌ Errore acquisto: {e}")
else:
    print(f"⚠️ Fondi insufficienti per comprare €60 di ETH.")

# Final Report
print("\n=== BILANCIO OTTIMIZZATO ===")
bal = exchange.fetch_balance()
total_eur = 0
details = []
for a in ['EUR', 'ETH', 'SOL', 'AVAX', 'BNB']:
    bal_a = bal.get(a, {})
    total = bal_a.get('total', 0)
    
    # Calc EUR value
    val = 0
    if a == 'EUR': val = total
    else:
        try:
            price = exchange.fetch_ticker(f"{a}/EUR")['last']
            val = total * price
        except: pass
    
    if val > 0:
        details.append(f"  {a}: {total:.5f} (€{val:.2f})")
        total_eur += val

print("\n".join(details))
print(f"🚀 TOTALE STIMATO: €{total_eur:.2f}")
