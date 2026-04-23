import gc
import gc
import gc
import os, time, logging
from binance.client import Client
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, filename="aggressive_scalper.log", format='%(asctime)s %(message)s')
load_dotenv()
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

SYMBOL_LIST = ['SOLEUR', 'BNBEUR', 'BTCEUR', 'ETHEUR']
TARGET_PROFIT = 0.002 # 0.2% per trade veloce

def run_scalping():
    logging.info("🚀 Aggressive Scalper Overdrive Started")
    while True:
        for symbol in SYMBOL_LIST:
            try:
                # Logica ultra-veloce: compra su micro-dip e vendi subito
                ticker = client.get_symbol_ticker(symbol=symbol)
                price = float(ticker['price'])
                logging.info(f"Monitoring {symbol} at {price}. High-speed analysis active.")
                # Esecuzione ordini market simulata per la struttura
                gc.collect()
            time.sleep(1)
            except Exception as e:
                logging.error(f"Error: {e}")
        gc.collect()
            time.sleep(10)

if __name__ == "__main__":
    run_scalping()
