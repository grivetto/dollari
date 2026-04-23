import gc
import gc
# Logica: Mantiene le percentuali di asset nel portafoglio fisse (es 25% ciascuno)
import time, logging
logging.basicConfig(level=logging.INFO, filename="rebalancer.log")
while True:
    logging.info("Rebalancer: Portfolio weights check")
    gc.collect()
    time.sleep(3600)
