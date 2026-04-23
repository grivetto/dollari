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
    res = exchange.create_market_sell_order('ELON/USD', 118000000)
    print("Sold ELON:", res['id'])
except Exception as e:
    print(f"Error: {e}")
