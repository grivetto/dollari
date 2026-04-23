import gc
import os, time, logging, gc
from dotenv import load_dotenv
from binance.client import Client

LOG_FILE = "/home/sergio/.openclaw/workspace/denaro/LIQUIDITY_VACUUM.log"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
logger = logging.getLogger("LiquidityVacuum")

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

PAIRS = ["BTCEUR", "ETHEUR", "SOLEUR"]
SPREAD_THRESHOLD = 0.005 # 0.5% spread is huge

def run_bot():
    logger.info("Avviato Liquidity Vacuum (Zero-OOM) - Cerco vuoti nel book per catturare lo spread...")
    while True:
        try:
            for pair in PAIRS:
                depth = client.get_order_book(symbol=pair, limit=5)
                best_bid = float(depth['bids'][0][0])
                best_ask = float(depth['asks'][0][0])
                spread = (best_ask - best_bid) / best_bid
                
                if spread > SPREAD_THRESHOLD:
                    logger.warning(f"🕳️ Vuoto di liquidita su {pair}! Spread: {spread*100:.2f}%. Ask: {best_ask}, Bid: {best_bid}")
                    # Simulated action: place limit orders inside the gap
                    mid_price = (best_ask + best_bid) / 2
                    buy_price = mid_price * 0.999
                    sell_price = mid_price * 1.001
                    logger.info(f"🕸️ Piazzo ordini limite dentro lo spread: BUY @ {buy_price:.2f}, SELL @ {sell_price:.2f}")
                else:
                    logger.info(f"💧 {pair}: Spread {spread*100:.3f}% (Normale). Niente da fare.")
                    
            gc.collect()
            time.sleep(30)
            
        except Exception as e:
            logger.error(f"Errore ciclo Liquidity Vacuum: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_bot()
