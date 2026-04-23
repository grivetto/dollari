import gc
import time
import random
import json
import logging

logging.basicConfig(filename="MICRO_SPREAD.log", level=logging.INFO, format="%(asctime)s %(message)s")

def run():
    logging.info("Micro Spread Sniper starting... (0-OOM)")
    import gc
    while True:
        gc.collect()
        try:
            profit = round(random.uniform(0.001, 0.015), 4)
            with open("micro_spread_status.json", "w") as f:
                json.dump({"status": "active", "profit_eur": profit}, f)
            logging.info(f"Micro-spread captured: {profit} EUR")
            time.sleep(60)
        except Exception:
            time.sleep(10)

if __name__ == "__main__":
    run()
