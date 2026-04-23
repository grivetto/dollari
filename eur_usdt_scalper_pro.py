import gc
import time
import logging
from binance.client import Client
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger("EUR_USDT_SCALPER")

load_dotenv(os.path.join('/home/sergio/.openclaw/workspace/denaro', '.env'))
try:
    client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
except Exception as e:
    logger.error(f"Binance client error: {e}")
    client = None

def run_scalper():
    logger.info("Starting EUR/USDT Micro Scalper Pro...")
    import gc
    while True:
        gc.collect()
        try:
            if client:
                ticker = client.get_ticker(symbol='EURUSDT')
                bid = float(ticker['bidPrice'])
                ask = float(ticker['askPrice'])
                spread = ask - bid
                logger.info(f"EUR/USDT Spread: {spread:.6f} (Bid: {bid}, Ask: {ask})")
                if spread > 0.0005:
                    logger.info("Micro-spread opportunity found. Executing virtual scalp...")
        except Exception as e:
            logger.error(f"Error: {e}")
        time.sleep(10)

if __name__ == "__main__":
    run_scalper()
