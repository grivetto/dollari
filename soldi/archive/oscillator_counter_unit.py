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

# --- CONFIGURAZIONE ---
load_dotenv()
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Coppie con spread elevato o ciclicità oscillatoria
PAIRS = ["ADABTC", "LTCBTC", "ETHBTC", "DOTBTC"]
RISK_BTC = 0.001 # 60€ per colpo

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [OSCILLATOR] - %(message)s',
    handlers=[logging.FileHandler('oscillator_unit.log'), logging.StreamHandler()]
)
logger = logging.getLogger("Oscillator")

def main():
    client = Client(API_KEY, API_SECRET)
    logger.info("📡 OSCILLATOR UNIT ACTIVATED - COUNTER-TREND SCALPING")
    
    positions = {}

    while True:
        try:
            for s in PAIRS:
                # Recupero dati Stocastico (15m) per identificare stanchezza trend
                klines = client.get_klines(symbol=s, interval='15m', limit=50)
                df = pd.DataFrame(klines, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qv', 'nt', 'tb', 'tq', 'i'])
                df['c'] = pd.to_numeric(df['c'])
                df['h'] = pd.to_numeric(df['h'])
                df['l'] = pd.to_numeric(df['l'])
                
                stoch = ta.stoch(df['h'], df['l'], df['c'])
                k = stoch['STOCHk_14_3_3'].iloc[-1]
                d = stoch['STOCHd_14_3_3'].iloc[-1]
                
                price = df['c'].iloc[-1]

                # Segnale Oscillator: Iper-venduto con incrocio rialzista (Svolta del mercato)
                if k < 20 and k > d and s not in positions:
                    logger.info(f"📡 OSCILLATOR SIGNAL on {s}: k={k:.1f} (Oversold Cross)")
                    try:
                        order = client.create_order(symbol=s, side='BUY', type='MARKET', quoteOrderQty=round(RISK_BTC, 6))
                        positions[s] = {'entry': price, 'qty': float(order['executedQty'])}
                        logger.info(f"🟢 OSCILLATOR BUY: {s}")
                    except: pass

                if s in positions:
                    pnl = (price - positions[s]['entry']) / positions[s]['entry']
                    # Uscita a 1.2% o Iper-comprato (k > 80)
                    if pnl >= 0.012 or k > 80 or pnl <= -0.02:
                        try:
                            client.create_order(symbol=s, side='SELL', type='MARKET', quantity=positions[s]['qty'])
                            logger.info(f"✅ OSCILLATOR SELL: {s} PnL: {pnl:.2%}")
                            del positions[s]
                            with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                                f.write(f"{(RISK_BTC * pnl * 1.0):.2f}")
                        except: pass
            
            gc.collect()
            time.sleep(45)
        except Exception as e:
            gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()
