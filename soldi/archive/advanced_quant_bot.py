import gc
import gc
import gc
import os
import time
import json
import logging
import pandas as pd
import pandas_ta as ta
from binance.client import Client
from dotenv import load_dotenv
from datetime import datetime
import sys

# --- CONFIGURAZIONE ---
load_dotenv()

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

SYMBOLS = ["BTCEUR", "ETHEUR", "SOLEUR", "BNBEUR"]
TIMEFRAME = Client.KLINE_INTERVAL_1MINUTE  # ULTRA-FAST 1 MINUTE

# Parametri Aggressivi
RSI_PERIOD = 7
RSI_BUY = 35
RSI_SELL = 65
POSITION_SIZE_EUR = 30.0  # Alzata dopo ricarica di emergenza (abbiamo ~64€ liberi)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('quant_bot.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

STATUS_FILE = '/home/sergio/.openclaw/workspace/denaro/quant_status.json'

def get_data(client, symbol):
    try:
        klines = client.get_klines(symbol=symbol, interval=TIMEFRAME, limit=100)
        df = pd.DataFrame(klines, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qv', 'nt', 'tb', 'tq', 'i'])
        df['c'] = pd.to_numeric(df['c'])
        return df
    except Exception as e:
        logger.error(f"Error {symbol}: {e}")
        return None

def main():
    client = Client(API_KEY, API_SECRET)
    logger.info("🚀 ULTRA-QUANT OVERDRIVE STARTED")
    
    active_positions = {}

    while True:
        try:
            for symbol in SYMBOLS:
                df = get_data(client, symbol)
                if df is None or len(df) < RSI_PERIOD: continue
                
                df['rsi'] = ta.rsi(df['c'], length=RSI_PERIOD)
                rsi = df['rsi'].iloc[-1]
                price = df['c'].iloc[-1]
                
                # Ingressi aggressivi
                if rsi <= RSI_BUY and symbol not in active_positions:
                    logger.info(f"🟢 QUANT BUY: {symbol} RSI: {rsi:.1f}")
                    try:
                        # Ordine reale Market su EUR pair
                        order = client.create_order(symbol=symbol, side='BUY', type='MARKET', quoteOrderQty=POSITION_SIZE_EUR)
                        active_positions[symbol] = {'entry': price, 'qty': float(order['executedQty'])}
                    except Exception as e: logger.error(f"❌ QUANT FAILED BUY: {e}")

                # Uscite veloci
                if symbol in active_positions:
                    entry = active_positions[symbol]['entry']
                    pnl = (price - entry) / entry
                    if pnl >= 0.015 or pnl <= -0.02: # 1.5% profit target
                        try:
                            client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=active_positions[symbol]['qty'])
                            logger.info(f"🔴 QUANT SELL: {symbol} PnL: {pnl:.2%}")
                            del active_positions[symbol]
                            with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                                f.write(f"{(POSITION_SIZE_EUR * pnl):.2f}")
                        except Exception as e: logger.error(f"❌ QUANT FAILED SELL: {e}")
            
            gc.collect()
            time.sleep(30)
        except Exception as e:
            logger.error(f"Quant Loop Error: {e}")
            gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()
