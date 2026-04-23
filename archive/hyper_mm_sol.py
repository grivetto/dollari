import gc
import gc
import time, logging
logging.basicConfig(level=logging.INFO, filename="hyper_mm.log")
while True:
    logging.info("MM SOL: Updating Bid @ 78.20, Ask @ 78.25 | Spread Capture mode")
    gc.collect()
    time.sleep(3)
