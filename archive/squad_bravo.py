import gc
import gc
import gc
import os
import time
import json
import logging
import requests
from binance.client import Client
from binance.enums import *
from dotenv import load_dotenv
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[logging.FileHandler('squad_bravo.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    load_dotenv()
    client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
    
    symbol = 'ETHEUR'
    logger.info(f"⚔️ SQUADRA BRAVO (ETH) - ATTIVA IN MODALITÀ SUPPORTO")

    while True:
        try:
            ticker = client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            
            # Squadra Bravo monitora Ethereum. Se abbiamo già ETH, cerca il profitto.
            # Se siamo liquidi, aspetta il segnale dal Commander.
            eth_bal = float(client.get_asset_balance(asset='ETH')['free'])
            
            status = {
                "last_update": datetime.now().isoformat(),
                "squad": "BRAVO",
                "asset": symbol,
                "price": price,
                "balance": eth_bal,
                "status": "PATROLLING"
            }
            with open('/home/sergio/.openclaw/workspace/denaro/dashboard/squad_bravo_data.json', 'w') as f:
                json.dump(status, f)
                
            gc.collect()
            time.sleep(30)
        except Exception as e:
            logger.error(f"Errore Bravo: {e}")
            gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()
