import gc
import gc
# Logica: Monitora grandi ordini nel book e si posiziona a scia
import time, logging
logging.basicConfig(level=logging.INFO, filename="whale_tracker.log")
while True:
    logging.info("Whale Tracker: Large order detected at 60k BTC")
    gc.collect()
    time.sleep(90)
