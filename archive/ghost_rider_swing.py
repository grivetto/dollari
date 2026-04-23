import gc
import gc
import gc
import os
import time
import json
import logging
from binance.client import Client
from dotenv import load_dotenv

# --- CONFIGURAZIONE ---
load_dotenv()
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Monete "Heavy" per swing trading
SWING_LIST = ["SOLBTC", "ETHBTC", "BNBBTC"]
RISK_BTC = 0.0018 # Circa 110€ per colpo

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.FileHandler('ghost_rider.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    client = Client(API_KEY, API_SECRET)
    logger.info("👻 GHOST RIDER SWING BOT ACTIVATED - LONG TREND")
    
    while True:
        try:
            for symbol in SWING_LIST:
                # Analisi Candele 1 ora (Swing)
                klines = client.get_klines(symbol=symbol, interval='1h', limit=5)
                # Semplice logica Ghost: 3 candele verdi consecutive = INGRESSO
                is_bullish = all(float(k[4]) > float(k[1]) for k in klines[-3:])
                
                if is_bullish:
                    # Inserisce ordine se non già in posizione (controllo balance)
                    asset_name = symbol.replace('BTC', '')
                    bal = float(client.get_asset_balance(asset=asset_name)['free'])
                    if bal * float(klines[-1][4]) < 5: # Posizione trascurabile
                        logger.info(f"👻 GHOST RIDER: Rilevato trend solido su {symbol}")
                        try:
                            client.create_order(
                                symbol=symbol, side='BUY', type='MARKET', quoteOrderQty=round(RISK_BTC, 6)
                            )
                            logger.info(f"🟢 GHOST BUY: {symbol} (Ride the trend)")
                        except Exception as e: logger.error(f"❌ GHOST FAILED BUY: {e}")
            
            gc.collect()
            time.sleep(300) # Check ogni 5 minuti
        except Exception as e:
            logger.error(f"Ghost Loop Error: {e}")
            gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()
