import os
from binance.client import Client
from dotenv import load_dotenv

load_dotenv("/home/sergio/.openclaw/workspace/denaro/.env")
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')
client = Client(api_key, api_secret)

orders = client.get_open_orders()
for o in orders:
    print(f"Cancelling {o['symbol']} order {o['orderId']} for {o['origQty']} @ {o['price']}")
    client.cancel_order(symbol=o['symbol'], orderId=o['orderId'])

print("Cancellations complete. Free capital retrieved.")
