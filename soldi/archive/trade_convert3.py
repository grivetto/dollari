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
    
    for symbol in ['ELON/USD', 'ELON/EUR']:
        if symbol in markets:
            print(f"market available {symbol}")
            
    try:
        if 'ELON/USD' in markets:
           res = exchange.create_market_sell_order('ELON/USD', 118000000)
           print(f"Sold ELON:", res['id'])
    except Exception as ex:
        print(f"Failed to sell ELON: {ex}")
        
except Exception as e:
    print(f"Error: {e}")
