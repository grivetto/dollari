import gc
import gc
import gc
import os
import time
import json
import logging
from binance.client import Client
from binance.enums import *
from dotenv import load_dotenv
from datetime import datetime

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('smart_grid_v3.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    load_dotenv()
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    client = Client(api_key, api_secret)
    
    symbol = 'BTCEUR'
    grid_levels = 20
    
    # Tracking dello strike per evitare spam
    last_strike_time = 0
    cooldown_period = 3600 # 1 ora di silenzio tra uno strike e l'altro
    
    logger.info(f"🚀 ALPHA-FLEET: Smart Grid Engine v3.1 ONLINE (Anti-Spam fix)")
    
    while True:
        try:
            ticker = client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            
            balances = client.get_account()['balances']
            btc_free = float(next(a['free'] for a in balances if a['asset'] == 'BTC'))
            eur_free = float(next(a['free'] for a in balances if a['asset'] == 'EUR'))
            
            total_val = eur_free + (btc_free * price)
            
            logger.info(f"📊 LIVE: {price} EUR | Valore Portafoglio: {total_val:.2f}€")
            
            status = {
                "last_update": datetime.now().isoformat(),
                "symbol": symbol,
                "price": price,
                "total_eur": round(total_val, 2),
                "grid_levels": grid_levels,
                "status": "PROFIT_MODE_ACTIVE"
            }
            with open('/home/sergio/.openclaw/workspace/denaro/grid_status.json', 'w') as f:
                json.dump(status, f)
            
            # Logica Strike con cooldown
            current_time = time.time()
            baseline = 722.00  # Capitale iniziale totale aggiornato (Fiat + Crypto)
            profit_today = total_val - baseline
            
            if total_val >= baseline + 0.50: # Strike ogni volta che guadagniamo almeno 0.50€
                if current_time - last_strike_time > cooldown_period:
                    with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                        f.write(f"{profit_today:.2f}")
                    last_strike_time = current_time
                    logger.info(f"🎯 STRIKE ALERT GENERATED: +{profit_today:.2f}€")
                else:
                    logger.info(f"🎯 Threshold reached (+{profit_today:.2f}€) but cooldown is active.")
            
            gc.collect()
            time.sleep(30)
        except Exception as e:
            logger.error(f"Errore: {e}")
            gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()
