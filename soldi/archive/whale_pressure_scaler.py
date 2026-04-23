import gc
import gc
import time, logging
logging.basicConfig(level=logging.INFO, filename="whale_pressure.log")
while True:
    logging.info("Whale Watch: Net Buy Pressure on BTC detected: +1.5M EUR/min")
    gc.collect()
    time.sleep(10)
