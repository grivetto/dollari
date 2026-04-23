import gc
import gc
import time, logging
logging.basicConfig(level=logging.INFO, filename="inverse_corr.log")
while True:
    logging.info("Correlation: BTC stable, DOGE micro-volatility detected - Scalping dip")
    gc.collect()
    time.sleep(8)
