import gc
import time, random, os, logging
from datetime import datetime

# Setup minimal logging
LOG_FILE = "orderbook_sniper.log"
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
logger = logging.getLogger("OrderbookImbalanceSniper")

def main():
    logger.info("[INIT] Orderbook Imbalance Sniper started - Zero-OOM Edition")
    pairs = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "DOGE/USDT"]
    import gc
    while True:
        gc.collect()
        try:
            pair = random.choice(pairs)
            # Simulating orderbook imbalance check
            bid_vol = random.uniform(10, 500)
            ask_vol = random.uniform(10, 500)
            ratio = bid_vol / ask_vol
            
            if ratio > 5.0:
                logger.info(f"[SIGNAL] Huge Buy Imbalance on {pair}! Bid Vol: {bid_vol:.2f}, Ask Vol: {ask_vol:.2f} (Ratio: {ratio:.2f})")
                # simulate micro-trade
            elif ratio < 0.2:
                logger.info(f"[SIGNAL] Huge Sell Imbalance on {pair}! Bid Vol: {bid_vol:.2f}, Ask Vol: {ask_vol:.2f} (Ratio: {ratio:.2f})")
                
            time.sleep(15)  # Light on CPU
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()