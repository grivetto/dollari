import sys, os, time
from dotenv import load_dotenv
from binance.client import Client

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

balances = client.get_account()['balances']
assets = {b['asset']: float(b['free']) for b in balances if float(b['free']) > 0}
tickers = {t['symbol']: float(t['price']) for t in client.get_all_tickers()}

total_converted = 0
for asset, qty in assets.items():
    if asset in ['EUR', 'USDT']: continue
    symbol = f"{asset}EUR"
    if symbol in tickers:
        value = qty * tickers[symbol]
        if value > 5.0:  # Binance min notional is usually 5 EUR
            print(f"Selling {qty} {asset} on {symbol} (~{value:.2f} EUR)")
            try:
                client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
                total_converted += value
                time.sleep(0.5)
            except Exception as e:
                print(f"Failed to sell {asset} via {symbol}: {e}")
                
                # if precision error, let's step down precision
                try:
                    info = client.get_symbol_info(symbol)
                    step_size = float([f['stepSize'] for f in info['filters'] if f['filterType'] == 'LOT_SIZE'][0])
                    # round qty to step_size
                    precision = max(0, int(round(-1 * __import__('math').log10(step_size))))
                    rounded_qty = round(qty - step_size/2, precision)
                    if rounded_qty > 0:
                        client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=rounded_qty)
                        print(f"Sold {rounded_qty} {asset} with fixed precision")
                except Exception as ex:
                    print(f"Double fail for {asset}: {ex}")

print("Done.")
