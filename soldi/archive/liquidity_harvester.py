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

# Monete con volume altissimo (Liquidity Hunting)
SYMBOLS = ["SOLBTC", "AVAXBTC", "ETHBTC", "FETBTC", "PEPEBTC", "DOGEBTC"]
TIMEFRAME = '1m'
# Ingressi basati su anomalie di volume improvvise (Big Money tracking)
VOL_SENSITIVITY = 3.5  # Volume > 350% media
PROFIT_TARGET = 0.002
RISK_BTC = 0.0018      # Circa 100€ per operazione

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [LIQUIDITY] - %(message)s',
    handlers=[logging.FileHandler('liquidity_harvester.log'), logging.StreamHandler()]
)
logger = logging.getLogger("Harvester")

def main():
    client = Client(API_KEY, API_SECRET)
    logger.info("🌊 LIQUIDITY HARVESTER ACTIVATED - HUNTING BIG MONEY FLOWS")
    
    positions = {}

    while True:
        try:
            for s in SYMBOLS:
                klines = client.get_klines(symbol=s, interval=TIMEFRAME, limit=30)
                df = pd.DataFrame(klines, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qv', 'nt', 'tb', 'tq', 'i'])
                df['c'] = pd.to_numeric(df['c'])
                df['v'] = pd.to_numeric(df['v'])
                
                avg_vol = df['v'].iloc[:-1].mean()
                curr_vol = df['v'].iloc[-1]
                price = df['c'].iloc[-1]
                
                # Se entra un volume anomalo mentre il prezzo sale (Shark Attack)
                if curr_vol > (avg_vol * VOL_SENSITIVITY) and df['c'].iloc[-1] > df['c'].iloc[-2] and s not in positions:
                    logger.info(f"🦈 SHARK DETECTED on {s}: Vol {curr_vol:.2f} (Avg {avg_vol:.2f})")
                    try:
                        order = client.create_order(symbol=s, side='BUY', type='MARKET', quoteOrderQty=round(RISK_BTC, 6))
                        logger.info(f"🟢 HARVESTER BUY: {s} @ {price} BTC")
                        positions[s] = {'entry': price, 'qty': float(order['executedQty'])}
                    except Exception as e: logger.error(f"❌ FAILED BUY: {e}")

                if s in positions:
                    entry = positions[s]['entry']
                    pnl = (price - entry) / entry
                    # Esce appena vede un accenno di rallentamento del volume o target
                    if pnl >= PROFIT_TARGET or pnl <= -0.015:
                        try:
                            client.create_order(symbol=s, side='SELL', type='MARKET', quantity=positions[s]['qty'])
                            logger.info(f"✅ HARVESTER PROFIT: {s} PnL: {pnl:.2%}")
                            del positions[s]
                            with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                                f.write(f"{(RISK_BTC * pnl * 1.0):.2f}")
                        except: pass
            
            gc.collect()
            time.sleep(10)
        except Exception as e:
            gc.collect()
            time.sleep(30)

if __name__ == "__main__":
    main()
