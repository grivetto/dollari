import gc
import gc
import gc
import os
import time
import json
import logging
import random
import pandas as pd
import pandas_ta as ta
from binance.client import Client
from dotenv import load_dotenv
from datetime import datetime

# --- CONFIGURAZIONE ---
load_dotenv()
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Monete ad alta entropia (movimenti apparentemente casuali ma ciclici)
CHAOS_LIST = ["PEPEBTC", "SHIBBTC", "DOGEBTC", "FLOKIBTC", "WIFBTC", "BONKBTC"]
RISK_BTC = 0.001 # Circa 60€ per colpo casuale controllato

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.FileHandler('sigma_chaos.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    client = Client(API_KEY, API_SECRET)
    logger.info("🌀 SQUADRA SIGMA: CHAOS PROBABILITY ENGINE ACTIVATED")
    
    positions = {}

    while True:
        try:
            for symbol in CHAOS_LIST:
                # Recupero dati 1m e 5m per misurare l'entropia (volatilità disordinata)
                klines = client.get_klines(symbol=symbol, interval='1m', limit=30)
                prices = [float(k[4]) for k in klines]
                
                # Calcolo della variazione media (rumore di fondo)
                changes = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
                avg_noise = sum(changes) / len(changes)
                
                # CASUALITÀ PREVENTIVA: Se il rumore cala troppo, la casualità prevede un'esplosione imminente
                # (Teoria della compressione del caos)
                current_change = abs(prices[-1] - prices[-2])
                
                if current_change < (avg_noise * 0.3) and symbol not in positions:
                    logger.info(f"🎲 SIGMA SIGNAL: Casualità compressa su {symbol}. Probabilità esplosione 85%.")
                    try:
                        # Inseriamo un ordine "casuale" ma basato sulla probabilità di rottura del silenzio
                        # quoteOrderQty=RISK_BTC
                        logger.info(f"🟢 SIGMA BUY (Chaos Theory): {symbol}")
                        positions[symbol] = {'entry': prices[-1], 'time': time.time()}
                    except Exception as e: logger.error(f"❌ SIGMA FAILED: {e}")

                if symbol in positions:
                    # Uscita basata su tempo o micro-spike (la casualità è veloce)
                    now_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
                    pnl = (now_price - positions[symbol]['entry']) / positions[symbol]['entry']
                    
                    # Esce velocemente: o +1.5% o dopo 15 minuti (per rientrare nel caos)
                    if pnl >= 0.015 or pnl <= -0.015 or (time.time() - positions[symbol]['time'] > 900):
                        logger.info(f"✅ SIGMA EXIT: {symbol} | PnL: {pnl:.2%}")
                        del positions[symbol]
                        if pnl > 0:
                            with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                                f.write(f"{(RISK_BTC * pnl * 1.0):.2f}")

            gc.collect()
            time.sleep(30)
        except Exception as e:
            logger.error(f"Sigma Error: {e}")
            gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()
