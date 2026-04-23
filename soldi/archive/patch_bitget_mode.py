import ccxt
import os
from dotenv import load_dotenv

load_dotenv('.env.bitget')
bitget = ccxt.bitget({
    'apiKey': os.getenv('BITGET_API_KEY'),
    'secret': os.getenv('BITGET_API_SECRET'),
    'password': os.getenv('BITGET_PASSWORD'),
})
try:
    bitget.set_position_mode(False, 'SOL/USDT:USDT') # False = One-way, True = Hedge
    print("Set position mode to One-way")
except Exception as e:
    print(e)
    try:
        bitget.set_position_mode(True, 'SOL/USDT:USDT')
        print("Set position mode to Hedge")
    except Exception as e2:
        print(e2)
