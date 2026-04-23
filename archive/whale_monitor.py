import gc
import gc
import gc
import os
import time
import requests
import json
import logging
from binance.client import Client
from dotenv import load_dotenv

# --- CONFIGURAZIONE ---
load_dotenv()
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Strategia: Monitoraggio Balene (Whale Alert)
# Questo bot non scambia direttamente (visto il capitale esaurito), 
# ma monitora grandi movimenti su BTC/EUR e invia alert su file se rileva anomalie.

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.FileHandler('whale_monitor.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    client = Client(API_KEY, API_SECRET)
    symbol = "BTCEUR"
    threshold_qty = 0.01 # Ridotta soglia per popolare la dashboard
    
    logger.info(f"🚀 Whale Monitor Attivo su {symbol} (Soglia: {threshold_qty} BTC)")

    while True:
        try:
            # Recupera gli ultimi trade eseguiti sul mercato
            trades = client.get_recent_trades(symbol=symbol, limit=10)
            for trade in trades:
                qty = float(trade['qty'])
                price = float(trade['price'])
                
                if qty >= threshold_qty:
                    side = "BUY" if not trade.get('isBuyerMaker') else "SELL"
                    logger.info(f"🐋 WHALE ALERT: {side} di {qty:.4f} BTC a {price:.2f} EUR")
                    
                    # Salva l'evento per la consultazione
                    with open('whale_events.json', 'a') as f:
                        event = {
                            "time": time.strftime('%Y-%m-%d %H:%M:%S'),
                            "qty": qty,
                            "price": price,
                            "side": side
                        }
                        f.write(json.dumps(event) + "\n")
            
            gc.collect()
            time.sleep(30)
        except Exception as e:
            logger.error(f"Errore monitoraggio: {e}")
            gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()
