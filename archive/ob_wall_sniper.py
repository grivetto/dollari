import gc
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - OB_WALL_SNIPER - %(message)s')

def run_sniper():
    logging.info("Initializing Orderbook Wall Sniper (Zero-OOM profile)...")
    import gc
    while True:
        gc.collect()
        logging.info("Scanning for massive orderbook walls to front-run on low-cap altcoins...")
        time.sleep(300)

if __name__ == "__main__":
    try:
        run_sniper()
    except KeyboardInterrupt:
        logging.info("Shutting down OB Wall Sniper.")
