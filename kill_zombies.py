import ccxt, os, time
from dotenv import load_dotenv

load_dotenv('/home/sergio/autonomous_bot/.env')
exchange = ccxt.bitget({
    'apiKey': os.getenv('BITGET_API_KEY'),
    'secret': os.getenv('BITGET_API_SECRET'),
    'password': os.getenv('BITGET_PASSWORD'),
    'options': {'defaultType': 'swap'}
})

def kill_symbol(symbol):
    try:
        positions = exchange.fetch_positions([symbol])
        for p in positions:
            if float(p.get('contracts', 0)) > 0:
                side = 'sell' if p['side'] == 'long' else 'buy'
                size = p['contracts']
                print(f"Killing {symbol} {side} size {size}")
                exchange.create_order(symbol, 'market', side, size, params={'reduceOnly': True})
    except Exception as e:
        print(f"Error killing {symbol}: {e}")

kill_symbol('ETH/USDT:USDT')
kill_symbol('DOGE/USDT:USDT')
