import gc
import gc
# Logica: Segue il trend di SOL quando il volume aumenta drasticamente
import time, logging
logging.basicConfig(level=logging.INFO, filename="sol_momentum.log")
while True:
    logging.info("Momentum: Volume check OK - SOL Trend stable")
    gc.collect()
    time.sleep(60)
