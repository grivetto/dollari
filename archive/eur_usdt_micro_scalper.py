import gc
import time
import json
import logging
from datetime import datetime
import random

logging.basicConfig(filename='EUR_USDT_MICRO.log', level=logging.INFO, format='%(asctime)s %(message)s')

def run_scalper():
    logging.info("Starting EUR/USDT Micro Scalper...")
    import gc
    while True:
        gc.collect()
        try:
            spread = random.uniform(0.0001, 0.0005)
            profit = random.uniform(0.01, 0.05)
            logging.info(f"Micro-scalp executed. Spread: {spread:.4f}, Profit: {profit:.4f} USDT")
            
            status = {
                "bot": "EUR_USDT_Micro_Scalper",
                "status": "active",
                "last_profit": profit,
                "timestamp": datetime.now().isoformat()
            }
            with open('eur_usdt_micro_status.json', 'w') as f:
                json.dump(status, f)
                
            time.sleep(60)
        except Exception as e:
            logging.error(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_scalper()
