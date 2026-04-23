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

# Monete con alta volatilità oraria (Intraday Cycles)
SYMBOLS = ["SOLBTC", "AVAXBTC", "ETHBTC", "BNBBTC", "LINKBTC"]
RISK_BTC = 0.002 # Circa 120€ per trade pesante

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [NEURAL] - %(message)s',
    handlers=[logging.FileHandler('neural_pulse.log'), logging.StreamHandler()]
)
logger = logging.getLogger("Neural")

def main():
    client = Client(API_KEY, API_SECRET)
    logger.info("🧠 NEURAL PULSE ACTIVATED - CYCLIC PATTERN PREDICTION")
    
    positions = {}

    while True:
        try:
            for s in SYMBOLS:
                klines = client.get_klines(symbol=s, interval='5m', limit=50)
                df = pd.DataFrame(klines, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qv', 'nt', 'tb', 'tq', 'i'])
                df['c'] = pd.to_numeric(df['c'])
                
                # Calcolo "Impulso Neurale" (Combinazione RSI + MACD Acceleration)
                rsi = ta.rsi(df['c'], length=14).iloc[-1]
                macd = ta.macd(df['c']).iloc[-1]
                macd_accel = macd['MACDh_12_26_9'] - ta.macd(df['c']).iloc[-2]['MACDh_12_26_9']
                
                price = df['c'].iloc[-1]

                # Segnale di "Battito" (RSI basso + Macd che accelera verso l'alto)
                if rsi < 42 and macd_accel > 0 and s not in positions:
                    logger.info(f"🧠 NEURAL PULSE on {s}: RSI {rsi:.1f} Accel {macd_accel:.8f}")
                    try:
                        order = client.create_order(symbol=s, side='BUY', type='MARKET', quoteOrderQty=round(RISK_BTC, 6))
                        positions[s] = {'entry': price, 'qty': float(order['executedQty']), 'max': price}
                        logger.info(f"🟢 NEURAL BUY: {s} @ {price}")
                    except Exception as e: logger.error(f"❌ NEURAL FAILED: {e}")

                if s in positions:
                    if price > positions[s]['max']: positions[s]['max'] = price
                    entry = positions[s]['entry']
                    high = positions[s]['max']
                    pnl = (price - entry) / entry
                    drawdown = (high - price) / high
                    
                    # Uscita chirurgica: 3% profit o Trailing 1% dal massimo
                    if pnl >= 0.03 or drawdown >= 0.01:
                        try:
                            client.create_order(symbol=s, side='SELL', type='MARKET', quantity=positions[s]['qty'])
                            logger.info(f"✅ NEURAL PROFIT: {s} PnL: {pnl:.2%}")
                            del positions[s]
                            with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                                f.write(f"{(RISK_BTC * pnl * 1.0):.2f}")
                        except: pass
            
            gc.collect()
            time.sleep(20)
        except Exception as e:
            gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()
