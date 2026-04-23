import ccxt
import os
import sys
from dotenv import load_dotenv

load_dotenv('/home/sergio/denaro/.env')
exchange = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_API_SECRET'),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

try:
    bal = exchange.fetch_balance()
    eur_free = float(bal.get('EUR', {}).get('free', 0))
    if eur_free < 50:
        print(f"Non ci sono 50 EUR liberi. Trovati: {eur_free} EUR.")
        sys.exit(0)
    
    # Compra USDT usando EUR (il pair su Binance è USDT/EUR o EUR/USDT?)
    # Binance usa EUR/USDT (vendi EUR per comprare USDT) oppure USDT/EUR (compri USDT con EUR).
    # Verifichiamo prima il ticker.
    ticker = exchange.fetch_ticker('EUR/USDT')
    price = ticker['last']
    
    amount_usdt = 50.0 / price
    print(f"Compro {amount_usdt:.2f} USDT al prezzo di {price:.4f} EUR (Totale: ~50 EUR)")
    
    # Esegui ordine market
    order = exchange.create_market_buy_order('EUR/USDT', amount_usdt)
    print("Ordine eseguito con successo:", order['id'])
    
except Exception as e:
    print(f"Errore: {e}")
