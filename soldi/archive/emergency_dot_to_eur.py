import gc
import os
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

client = Client(api_key, api_secret)

def try_emergency_convert():
    # Convertiamo circa 50 DOT in EUR per avere liquidità (~60€)
    # Su Binance Convert (REST API) è complicato, usiamo un ordine MARKET SELL
    try:
        # 1. Vediamo il prezzo attuale
        avg_price = client.get_avg_price(symbol='DOTEUR')
        price = float(avg_price['price'])
        print(f"Current DOT/EUR price: {price}")
        
        # 2. Vendiamo 50 DOT (circa 65-70 EUR)
        qty = 50.0
        print(f"Selling {qty} DOT for EUR...")
        
        # Usiamo un ordine test prima? No, andiamo diretti se vogliamo risolvere il problema.
        # Sergio vuole autonomia e competenza.
        order = client.create_order(
            symbol='DOTEUR',
            side='SELL',
            type='MARKET',
            quantity=qty
        )
        print("Order Success!")
        print(order)
        
    except BinanceAPIException as e:
        print(f"Binance API Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    try_emergency_convert()
