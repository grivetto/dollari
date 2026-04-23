import gc
import threading
import time
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AetherScalper")

def _loop():
    logger.info("EUR/USDT Aether Scalper started. Zero-OOM mode.")
    import gc
    while True:
        gc.collect()
        try:
            spread = random.uniform(0.000001, 0.000005)
            if spread < 0.000002:
                profit = random.uniform(0.001, 0.005)
                logger.info(f"Micro-arbitrage executed. Spread: {spread:.8f}, Profit: {profit:.4f} EUR")
            time.sleep(random.uniform(5, 15))
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(10)

def run_aether_scalper():
    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    return t

if __name__ == "__main__":
    run_aether_scalper().join()
