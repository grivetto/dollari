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
    free_balances = {k: v for k, v in balance['free'].items() if k in ['SHIB', 'ELON'] and v > 0}
    print("Remaining balances:", free_balances)
    
    markets = exchange.load_markets()
    
    for coin in ['SHIB', 'ELON']:
        if coin in free_balances and free_balances[coin] > 0:
            qty = free_balances[coin]
            symbol = f"{coin}/USDT"
            if symbol in markets:
                try:
                    print(f"Selling {qty} {coin} for USDT...")
                    res = exchange.create_market_sell_order(symbol, qty)
                    print(f"Sold {coin}:", res['id'])
                except Exception as ex:
                    print(f"Failed to sell {coin}: {ex}")
            else:
                print(f"Market {symbol} not found")
                
except Exception as e:
    print(f"Error: {e}")
