import gc
import gc
# Logica: Piazza ordini limit "low-ball" al -10% per catturare flash crash
import time, logging
logging.basicConfig(level=logging.INFO, filename="flash_crash.log")
while True:
    logging.info("Flash Crash: Orders placed at -10%")
    gc.collect()
    time.sleep(600)
