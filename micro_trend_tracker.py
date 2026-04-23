import gc
import time
import logging
import os
import math
import pandas as pd
from dotenv import load_dotenv
from binance.client import Client

# --- CONFIGURATION ---
CONFIG = {
    "SYMBOLS": ["SOLEUR", "DOGEEUR", "BNBEUR", "AVAXEUR", "LINKEUR", "ETHEUR"],
    "MIN_MOMENTUM": 0.5, # Percent change in 1h to consider as trend
    "TRADE_AMOUNT_EUR": 20.0,
    "INTERVAL": '1h',
    "LOG_FILE": "/home/sergio/denaro/MICRO_TREND.log",
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - MICRO-TREND - %(message)s',
                    handlers=[logging.FileHandler(CONFIG["LOG_FILE"]), logging.StreamHandler()])
logger = logging.getLogger(__name__)

load_dotenv('/home/sergio/denaro/.env')
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

client = Client(API_KEY, API_SECRET)

def get_step_size(symbol):
    try:
        info = client.get_symbol_info(symbol)
        for f in info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                return float(f['stepSize'])
    except Exception as e:
        logger.error(f"Error getting step size for {symbol}: {e}")
    return 1.0

def round_step(quantity, step_size):
    if step_size == 0: return quantity
    precision = int(round(-math.log10(step_size), 0))
    return round(quantity - (quantity % step_size), precision)

def get_momentum(symbol):
    try:
        klines = client.get_klines(symbol=symbol, interval=CONFIG["INTERVAL"], limit=2)
        if len(klines) < 2: return 0.0
        open_price = float(klines[0][1])
        close_price = float(klines[-1][4])
        momentum = ((close_price - open_price) / open_price) * 100
        return momentum
    except Exception as e:
        logger.error(f"Error calculating momentum for {symbol}: {e}")
        return 0.0

def execute_scalp(symbol, side):
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        price = float(ticker['price'])
        
        step = get_step_size(symbol)
        raw_qty = CONFIG["TRADE_AMOUNT_EUR"] / price
        qty = round_step(raw_qty, step)
        
        if side == 'BUY':
            client.create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
            logger.info(f"🚀 REAL TRADE: Long {symbol} @ {price} (Qty: {qty})")
        else:
            asset = symbol.replace('EUR', '')
            bal = float(client.get_asset_balance(asset=asset)['free'])
            if bal > 0:
                sell_qty = round_step(bal, step)
                client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=sell_qty)
                logger.info(f"🔻 REAL TRADE: Short {symbol} @ {price} (Qty: {sell_qty})")
    except Exception as e:
        logger.error(f"Execution error for {symbol}: {e}")

def main():
    logger.info("Avviato Micro-Trend Tracker REAL (v2) - Fixed LOT_SIZE.")
    while True:
        gc.collect()
        try:
            for symbol in CONFIG["SYMBOLS"]:
                momentum = get_momentum(symbol)
                logger.info(f"Analisi {symbol}: Momentum {momentum:.2f}%")
                
                if momentum > CONFIG["MIN_MOMENTUM"]:
                    logger.info(f"Forte mini-trend rialzista rilevato su {symbol}. Apro long scalping.")
                    execute_scalp(symbol, 'BUY')
                elif momentum < -CONFIG["MIN_MOMENTUM"]:
                    logger.info(f"Forte mini-trend ribassista rilevato su {symbol}. Apro short scalping.")
                    execute_scalp(symbol, 'SELL')
            
            with open("micro_trend_status.json", "w") as f:
                f.write(f'{{\"status\": \"RUNNING\", \"timestamp\": {time.time()}}}')
            
            time.sleep(300) 
        except Exception as e:
            logger.error(f"Errore loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
