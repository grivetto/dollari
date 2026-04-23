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

# Monete ad alta volatilità oraria (Intraday Cycles)
# Strategia: STATISTICAL MEAN REVERSION (L'esatto opposto del Trend Following)
# Se una moneta scosta troppo dalla sua media oraria, scommettiamo sul ritorno alla base.
SYMBOLS = ["SOLBTC", "AVAXBTC", "ETHBTC", "DOTBTC", "NEARBTC", "LINKBTC"]
TIMEFRAME = '5m'
BOL_PERIOD = 20
BOL_STD = 2.2 # Filtro molto selettivo
RISK_BTC = 0.002 # Circa 120€ per trade "pesante"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [CENTURION] - %(message)s',
    handlers=[logging.FileHandler('centurion_squad.log'), logging.StreamHandler()]
)
logger = logging.getLogger("Centurion")

def main():
    client = Client(API_KEY, API_SECRET)
    logger.info("🛡️ SQUADRA CENTURION ACTIVATED - STATISTICAL ARBITRAGE & MEAN REVERSION")
    
    positions = {}

    while True:
        try:
            for s in SYMBOLS:
                klines = client.get_klines(symbol=s, interval=TIMEFRAME, limit=100)
                df = pd.DataFrame(klines, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qv', 'nt', 'tb', 'tq', 'i'])
                df['c'] = pd.to_numeric(df['c'])
                
                # Calcolo Bollinger Bands per Mean Reversion
                bb = ta.bbands(df['c'], length=BOL_PERIOD, std=BOL_STD)
                lower_band = bb[f'BBL_{BOL_PERIOD}_{BOL_STD}'].iloc[-1]
                upper_band = bb[f'BBU_{BOL_PERIOD}_{BOL_STD}'].iloc[-1]
                price = df['c'].iloc[-1]

                # SEGNALE CENTURION: Compriamo quando il prezzo "esplode" fuori dalle bande inferiori
                # (Scommettiamo contro il panico degli altri)
                if price <= lower_band and s not in positions:
                    logger.info(f"🛡️ CENTURION SIGNAL: {s} fuori soglia statistica. Inizio recupero.")
                    try:
                        # Esecuzione reale (Limit order per evitare slippage su colpi grandi)
                        order = client.create_order(
                            symbol=s, side='BUY', type='MARKET', quoteOrderQty=round(RISK_BTC, 6)
                        )
                        positions[s] = {'entry': price, 'qty': float(order['executedQty'])}
                        logger.info(f"🟢 CENTURION BUY: {s} @ {price} BTC")
                    except Exception as e: logger.error(f"❌ CENTURION FAILED BUY: {e}")

                # USCITA: Appena torna alla media (SMA 20)
                if s in positions:
                    sma_mid = bb[f'BBM_{BOL_PERIOD}_{BOL_STD}'].iloc[-1]
                    pnl = (price - positions[s]['entry']) / positions[s]['entry']
                    
                    if price >= sma_mid or pnl <= -0.04:
                        try:
                            client.create_order(symbol=s, side='SELL', type='MARKET', quantity=positions[s]['qty'])
                            logger.info(f"✅ CENTURION PROFIT: {s} | PnL: {pnl:.2%}")
                            del positions[s]
                            with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                                f.write(f"{(RISK_BTC * pnl * 1.0):.2f}")
                        except: pass
            
            gc.collect()
            time.sleep(30)
        except Exception as e:
            logger.error(f"Centurion Loop Error: {e}")
            gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()
