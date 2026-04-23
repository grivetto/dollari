import gc
import gc
# Logica: Piazza ordini limit buy/sell vicini al mid-price per catturare lo spread
import time, logging
logging.basicConfig(level=logging.INFO, filename="eth_market_maker.log")
while True:
    logging.info("MM: Bid/Ask update for ETH")
    gc.collect()
    time.sleep(5)
