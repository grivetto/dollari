#!/usr/bin/env python3
"""Cancel stale ADA buy orders far from market price."""
import json, os, sys
sys.path.insert(0, '.')
from connector import ExchangeConnector
from dotenv import load_dotenv
load_dotenv('/home/sergio/hermes_alpha/.env')

with open('config/alpha_config.json') as f:
    config = json.load(f)

c = ExchangeConnector(config)
ex = c.exchange
ex.options['warnOnFetchOpenOrdersWithoutSymbol'] = False

orders = ex.fetch_open_orders()
cancelled = 0
freed = 0.0

for o in orders:
    sym = o.get('symbol', '')
    side = o.get('side', '')
    price = float(o.get('price', 0))
    amount = float(o.get('amount', 0))
    oid = o.get('id', '')
    cost = price * amount

    if 'ADA' in sym and side == 'buy' and price < 0.25:
        print(f'Cancelling ADA order: {oid} @ {price} x {amount} ({cost:.2f}EUR)')
        try:
            ex.cancel_order(oid, sym)
            cancelled += 1
            freed += cost
        except Exception as e:
            print(f'  Failed: {e}')

if cancelled == 0:
    print('No stale ADA orders found')
else:
    print(f'\nCancelled {cancelled} orders, freed {freed:.2f}EUR')

# Verify remaining
orders = ex.fetch_open_orders()
print(f'\nRemaining orders: {len(orders)}')
for o in sorted(orders, key=lambda x: x['symbol']):
    cost = float(o['price']) * float(o['amount'])
    print(f'{o["symbol"]:12s} {o["side"]:4s} @ {float(o["price"]):>12.6f} x {float(o["amount"]):>8.4f} | cost={cost:.2f}EUR')

c.close()
