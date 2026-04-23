import gc
import gc
import gc
import gc
import os
import time
import json
import logging
import random
from binance.client import Client
from dotenv import load_dotenv

# --- CONFIGURAZIONE ---
load_dotenv()
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Monete a bassa capitalizzazione o alta sensibilità ai micro-ordini (Meme/Alt liquide)
BAIT_LIST = ["PEPEBTC", "SHIBBTC", "DOGEBTC", "FLOKIBTC", "WIFBTC"]
BAIT_SIZE_BTC = 0.00015  # Micro-ordini da ~9€ per non rischiare, ma attirare attenzione

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [BAIT-ALGO] - %(message)s',
    handlers=[logging.FileHandler('bait_engine.log'), logging.StreamHandler()]
)
logger = logging.getLogger("Bait")

def main():
    client = Client(API_KEY, API_SECRET)
    logger.info("🎣 BAIT & TRAP ENGINE ACTIVATED - STUZZICANDO IL MERCATO")
    
    while True:
        try:
            # 1. SCEGLI UN BERSAGLIO
            target = random.choice(BAIT_LIST)
            
            # 2. PIAZZA UN "ESCA" (Micro-ordine Market)
            # Questo ordine appare nei grafici e nei log della Flash Unit per attirare altri bot
            logger.info(f"🪱 Lancio esca su {target}...")
            try:
                # Compro una micro-quantità
                order = client.create_order(symbol=target, side='BUY', type='MARKET', quoteOrderQty=round(BAIT_SIZE_BTC, 6))
                qty = float(order['executedQty'])
                
                # 3. ATTENDI IL REACTION SPIKE (30-60 secondi)
                # Scommettiamo che altri bot algoritmici vedano il nostro BUY e spingano il prezzo
                gc.collect()
            time.sleep(random.randint(30, 60))
                
                # 4. CHIUDI LA TRAPPOLA
                logger.info(f"🧨 Chiudo la trappola su {target}...")
                client.create_order(symbol=target, side='SELL', type='MARKET', quantity=qty)
                
            except Exception as e:
                logger.error(f"❌ Errore esca: {e}")
            
            # Attendi tra una provocazione e l'altra
            gc.collect()
            time.sleep(random.randint(300, 900)) 
            
        except Exception as e:
            logger.error(f"Bait Loop Error: {e}")
            gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()
