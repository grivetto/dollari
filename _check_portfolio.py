#!/usr/bin/env python3
"""Check portfolio state on mc2."""
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

# Open orders
orders = ex.fetch_open_orders()
print(f'=== OPEN ORDERS ({len(orders)}) ===')
eur_locked = 0
for o in sorted(orders, key=lambda x: x['symbol']):
    cost = float(o['price']) * float(o['amount'])
    if o['side'] == 'buy' and o['symbol'].endswith('/EUR'):
        eur_locked += cost
    print(f'{o["symbol"]:12s} {o["side"]:4s} {float(o["price"]):>12.6f} {float(o["amount"]):>10.4f} | cost={cost:.2f}€')
print(f'\nEUR locked in buy orders: {eur_locked:.2f}€')

# Portfolio value
bal = c.fetch_balance()
tickers = {
    'ETH/EUR': None, 'SOL/EUR': None, 'ADA/EUR': None, 'XRP/EUR': None,
    'LINK/EUR': None, 'DOGE/EUR': None, 'DOT/EUR': None, 'NEAR/EUR': None,
    'SUI/EUR': None, 'BTC/EUR': None,
}
for pair in tickers:
    try:
        t = ex.fetch_ticker(pair)
        tickers[pair] = t['last']
    except:
        pass

total = 0.0
print(f'\n=== PORTFOLIO ===')
for asset, total_val in bal.get('total', {}).items():
    fval = float(total_val)
    if fval <= 0:
        continue
    free = float(bal.get('free', {}).get(asset, 0))
    used = float(bal.get('used', {}).get(asset, 0))
    if asset == 'EUR':
        value = fval
    elif asset == 'USDC':
        value = fval
    else:
        pair = f'{asset}/EUR'
        price = tickers.get(pair, tickers.get(f'{asset}/USDT', None))
        if price:
            if asset == 'USDT':
                value = fval
            else:
                value = fval * price
        else:
            value = 0
    total += value
    print(f'{asset:8s}: {fval:>10.4f} free={free:.4f} used={used:.4f} ≈ {value:.2f}€')

print(f'\n💰 TOTAL PORTFOLIO: {total:.2f}€')
c.close()
