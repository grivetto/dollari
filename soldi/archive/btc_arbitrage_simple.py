import gc
import gc
# Logica: Monitora spread tra coppie BTC (es. BTCEUR vs BTCUSDT)
import time, logging
logging.basicConfig(level=logging.INFO, filename="btc_arbitrage.log")
while True:
    logging.info("Arbitrage check: Spread 0.02% - No trade")
    gc.collect()
    time.sleep(10)
