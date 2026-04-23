import gc
import gc
import time, logging
logging.basicConfig(level=logging.INFO, filename="ema_scalper.log")
while True:
    logging.info("EMA Cross: EMA5 > EMA10 on ETHEUR - Bullish Momentum")
    gc.collect()
    time.sleep(5)
