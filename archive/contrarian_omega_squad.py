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

# Focus su monete in forte rally per "Short" o monete "Pump & Dump"
REVERSAL_LIST = ["ETHBTC", "SOLBTC", "AVAXBTC", "DOGEBTC", "LINKBTC", "BNBBTC", "MATICBTC", "NEARBTC"]
TIMEFRAME = '5m'
RSI_SELL = 68.0       # Estremo Iper-comprato (Metodo opposto: vendiamo la forza)
PROFIT_TARGET = 0.035 # 3.5% calo
STOP_LOSS = 0.05      # 5% sicurezza
RISK_BTC = 0.002      # Circa 120€ per trade - OMEGA OVERDRIVE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.FileHandler('contrarian_omega.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    client = Client(API_KEY, API_SECRET)
    logger.info("⚔️ SQUADRA OMEGA: CONTRARIAN OVERDRIVE ACTIVATED")
    
    positions = {}

    while True:
        try:
            for symbol in REVERSAL_LIST:
                klines = client.get_klines(symbol=symbol, interval=TIMEFRAME, limit=100)
                df = pd.DataFrame(klines, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qv', 'nt', 'tb', 'tq', 'i'])
                df['c'] = pd.to_numeric(df['c'])
                
                rsi = ta.rsi(df['c'], length=14).iloc[-1]
                price = df['c'].iloc[-1]
                
                # CONTRARIAN DETECTION: Vendiamo quando tutti comprano (Overbought)
                if rsi >= RSI_SELL and symbol not in positions:
                    logger.info(f"🚨 OMEGA OVERDRIVE: {symbol} Iper-comprato (RSI: {rsi:.1f}).")
                    try:
                        # Simulazione short o vendita asset esistente per riacquisto basso
                        # Per ora logghiamo l'intento aggressivo
                        logger.info(f"📉 [OMEGA-OVERDRIVE] Execution on {symbol} @ {price}")
                        positions[symbol] = {'entry': price}
                    except Exception as e: logger.error(f"❌ OMEGA FAILED: {e}")

                if symbol in positions:
                    entry = positions[symbol]['entry']
                    change = (price - entry) / entry
                    if change <= -PROFIT_TARGET:
                        logger.info(f"✅ OMEGA OVERDRIVE PROFIT: {symbol} @ {price}")
                        del positions[symbol]
                        with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                            f.write(f"{(RISK_BTC * 0.035 * 59500):.2f}")
                    elif change >= STOP_LOSS:
                        del positions[symbol]

            gc.collect()
            time.sleep(30)
        except Exception as e:
            logger.error(f"Omega Error: {e}")
            gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()
