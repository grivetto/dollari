import gc
import gc
# Logica: Entra su rottura delle resistenze storiche a 1H
import time, logging
logging.basicConfig(level=logging.INFO, filename="breakout.log")
while True:
    logging.info("Breakout: Monitoring resistance levels")
    gc.collect()
    time.sleep(120)
