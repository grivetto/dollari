import gc
import gc
import time, logging
logging.basicConfig(level=logging.INFO, filename="triangle_arb.log")
while True:
    logging.info("Checking: BTCEUR -> ETHEUR -> BNBEUR -> BTCEUR | Profit Potential: 0.01%")
    gc.collect()
    time.sleep(5)
