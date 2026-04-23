import gc
import time
import json
import os
import logging
from datetime import datetime
from binance.client import Client
from dotenv import load_dotenv
import sys

# Aggiungo la root al path per importare i file se necessario, o metto le funzioni qui.
sys.path.append('/home/sergio/.openclaw/workspace')
try:
    from flash_crash_arbitrageur import check_flash_crash
except ImportError:
    def check_flash_crash(): pass

try:
    from rsi_divergence_hunter import check_divergence
except ImportError:
    def check_divergence(data): return False

SYMBOL = "BTCEUR"
DEV_THRESHOLD = 0.02 # 2% deviation
POLL_INTERVAL = 30
STATUS_FILE = "vwap_status.json"

BASE_DIR = '/home/sergio/.openclaw/workspace/denaro'
load_dotenv(os.path.join(BASE_DIR, '.env'))
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

logging.basicConfig(level=logging.INFO, format='%(message)s')

def get_vwap_and_price():
    try:
        klines = client.get_klines(symbol=SYMBOL, interval=Client.KLINE_INTERVAL_1MINUTE, limit=100)
        if not klines: return None, None
        
        cumulative_vp = 0
        cumulative_v = 0
        current_price = float(klines[-1][4])
        prices = []
        
        for candle in klines:
            high = float(candle[2])
            low = float(candle[3])
            close = float(candle[4])
            volume = float(candle[5])
            prices.append(close)
            typical_price = (high + low + close) / 3
            cumulative_vp += typical_price * volume
            cumulative_v += volume
            
        vwap = cumulative_vp / cumulative_v if cumulative_v > 0 else current_price
        return vwap, current_price, prices
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, None, None

def main():
    print(f"[{datetime.now()}] Starting VWAP Reversion Sniper on {SYMBOL} with Enhancements")
    import gc
    while True:
        gc.collect()
        vwap, price, prices = get_vwap_and_price()
        if vwap and price:
            deviation = (price - vwap) / vwap
            signal = "NEUTRAL"
            if deviation > DEV_THRESHOLD:
                signal = "SHORT_SIGNAL"
            elif deviation < -DEV_THRESHOLD:
                signal = "LONG_SIGNAL"
                
            # Enhancements
            check_flash_crash()
            if check_divergence(prices):
                signal = "RSI_DIVERGENCE_" + signal
                
            status = {
                "symbol": SYMBOL,
                "price": price,
                "vwap": round(vwap, 2),
                "deviation_pct": round(deviation * 100, 2),
                "signal": signal,
                "timestamp": str(datetime.now())
            }
            with open(os.path.join(BASE_DIR, STATUS_FILE), "w") as f:
                json.dump(status, f)
            print(f"[{datetime.now()}] {SYMBOL} Price: {price}, VWAP: {round(vwap,2)}, Dev: {round(deviation*100,2)}% -> {signal}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
