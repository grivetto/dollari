import gc
import gc
import os
import ccxt
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('CRYPTOCOM_API_KEY')
API_SECRET = os.getenv('CRYPTOCOM_API_SECRET')

exchange = ccxt.cryptocom({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
})

try:
    balance = exchange.fetch_balance()
    free_balances = {k: v for k, v in balance['free'].items() if v > 0}
    print("Free balances before:", free_balances)
    
    markets = exchange.load_markets()
    
    for coin in ['SHIB', 'ELON']:
        if coin in free_balances and free_balances[coin] > 0:
            qty = free_balances[coin]
            symbol = f"{coin}/USDT"
            if symbol in markets:
                print(f"Selling {qty} {coin} for USDT...")
                res = exchange.create_market_sell_order(symbol, qty)
                print(f"Sold {coin}:", res['id'])
            else:
                print(f"Market {symbol} not found")
                
    gc.collect()
            time.sleep(2)
    balance_after = exchange.fetch_balance()
    free_balances_after = {k: v for k, v in balance_after['free'].items() if v > 0}
    print("Free balances after:", free_balances_after)
except Exception as e:
    print(f"Error: {e}")
