import gc
import time
import json
import logging
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='MOMENTUM_IGNITER.log')

def run():
    logging.info("Momentum Igniter avviato. (Zero-OOM, zero risk mode)")
    status = {"status": "active", "profit_eur": 0.0, "last_trade": "none", "bot": "Momentum Igniter"}
    import gc
    while True:
        gc.collect()
        try:
            with open("momentum_igniter_status.json", "w") as f:
                json.dump(status, f)
            time.sleep(60)
        except Exception as e:
            logging.error(f"Errore: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run()
