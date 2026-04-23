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

# --- CONFIGURAZIONE ---
load_dotenv()
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Monete con maggiore volatilità intraday
SHADOW_LIST = ["AVAXBTC", "SOLBTC", "ETHBTC", "LINKBTC", "DOTBTC", "NEARBTC", "ARBBTC"]
TIMEFRAME = '1m' # Precisione estrema (1 minuto)
TREND_PERIOD = 20
RISK_BTC = 0.0012 # Circa 70€ per colpo

STATUS_FILE = '/home/sergio/.openclaw/workspace/denaro/shadow_status.json'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.FileHandler('shadow_trend.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    client = Client(API_KEY, API_SECRET)
    logger.info("🌑 SHADOW TREND TRACER ACTIVATED - 1M ULTRA-SCALPING")
    
    positions = {}

    while True:
        try:
            for symbol in SHADOW_LIST:
                klines = client.get_klines(symbol=symbol, interval=TIMEFRAME, limit=50)
                df = pd.DataFrame(klines, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qv', 'nt', 'tb', 'tq', 'i'])
                df['c'] = pd.to_numeric(df['c'])
                
                # Calcola SuperTrend o EMA Cross veloce
                df['ema_fast'] = ta.ema(df['c'], length=9)
                df['ema_slow'] = ta.ema(df['c'], length=21)
                
                price = df['c'].iloc[-1]
                prev_fast = df['ema_fast'].iloc[-2]
                prev_slow = df['ema_slow'].iloc[-2]
                curr_fast = df['ema_fast'].iloc[-1]
                curr_slow = df['ema_slow'].iloc[-1]

                # Rilevamento Cambio Trend (Incrocio EMA)
                if curr_fast > curr_slow and prev_fast <= prev_slow and symbol not in positions:
                    logger.info(f"⚡ SHADOW SIGNAL: Trend rialzista su {symbol}")
                    try:
                        order = client.create_order(
                            symbol=symbol, side='BUY', type='MARKET', quoteOrderQty=round(RISK_BTC, 6)
                        )
                        logger.info(f"🟢 SHADOW BUY: {symbol} @ {price} BTC")
                        positions[symbol] = {'entry': price, 'high': price}
                    except Exception as e: logger.error(f"❌ SHADOW FAILED BUY {symbol}: {e}")

                # Gestione "Shadow Exit" (Trailing Stop aggressivo)
                if symbol in positions:
                    if price > positions[symbol]['high']:
                        positions[symbol]['high'] = price
                    
                    entry = positions[symbol]['entry']
                    high = positions[symbol]['high']
                    pnl = (price - entry) / entry
                    drop_from_high = (high - price) / high
                    
                    # Esce se guadagna l'1% o se storna dello 0.5% dal massimo
                    if pnl >= 0.012 or (drop_from_high >= 0.005 and pnl > 0.004):
                        try:
                            asset_name = symbol.replace('BTC', '')
                            bal = float(client.get_asset_balance(asset=asset_name)['free'])
                            client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=bal)
                            logger.info(f"✅ SHADOW PROFIT: {symbol} | PnL: {pnl:.2%}")
                            del positions[symbol]
                            with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                                f.write(f"{(RISK_BTC * pnl * 1.0):.2f}")
                        except Exception as e: logger.error(f"❌ SHADOW FAILED SELL {symbol}: {e}")
            
            gc.collect()
            time.sleep(30)
        except Exception as e:
            logger.error(f"Shadow Loop Error: {e}")
            gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()
