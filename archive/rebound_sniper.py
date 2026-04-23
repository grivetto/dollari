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

# Monete solide (Coppie BTC per usare i fondi appena arrivati)
SNIPE_LIST = ["ETHBTC", "SOLBTC", "BNBBTC", "LINKBTC", "AVAXBTC"]
TIMEFRAME = '5m'
RSI_BUY = 28.0          # Iper-venduto estremo
RSI_PERIOD = 14
TARGET_REBOUND = 0.0025
STOP_LOSS = 0.04       # 4% sicurezza
RISK_BTC = 0.0015       # Circa 90€ per trade

STATUS_FILE = '/home/sergio/.openclaw/workspace/denaro/sniper_status.json'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.FileHandler('rebound_sniper.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def update_status(data):
    try:
        with open(STATUS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error status: {e}")

def main():
    client = Client(API_KEY, API_SECRET)
    logger.info("🎯 REBOUND SNIPER LIVE - BTC PAIRS MODE")
    
    positions = {}

    while True:
        try:
            for symbol in SNIPE_LIST:
                klines = client.get_klines(symbol=symbol, interval=TIMEFRAME, limit=100)
                df = pd.DataFrame(klines, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qv', 'nt', 'tb', 'tq', 'i'])
                df['c'] = pd.to_numeric(df['c'])
                
                rsi = ta.rsi(df['c'], length=RSI_PERIOD).iloc[-1]
                price = df['c'].iloc[-1]
                
                # SNIPE DETECTION (LIVE ORDERS ENABLED)
                if rsi <= RSI_BUY and symbol not in positions:
                    logger.info(f"🎯 SNIPE! {symbol} RSI: {rsi:.1f} (Iper-venduto)")
                    try:
                        order = client.create_order(
                            symbol=symbol,
                            side='BUY',
                            type='MARKET',
                            quoteOrderQty=round(RISK_BTC, 6)
                        )
                        logger.info(f"🟢 LIVE SNIPE BUY: {symbol} @ {price} BTC")
                        positions[symbol] = {'entry': price, 'qty': RISK_BTC / price}
                    except Exception as e:
                        logger.error(f"❌ FAILED SNIPE {symbol}: {e}")
                        if "insufficient balance" in str(e).lower():
                            logger.info(f"⏸️ Pausing {symbol} for 15 minutes due to insufficient balance.")
                            positions[symbol] = {'entry': price, 'qty': 0, 'paused': True, 'resume_time': time.time() + 900}

                # GESTIONE POSIZIONI ESISTENTI
                if symbol in positions:
                    if positions[symbol].get('paused'):
                        if time.time() > positions[symbol]['resume_time']:
                            del positions[symbol]
                            logger.info(f"▶️ Resumed {symbol} after cooldown.")
                        continue
                    
                    entry = positions[symbol]['entry']
                    pnl = (price - entry) / entry
                    if pnl >= TARGET_REBOUND or pnl <= -STOP_LOSS:
                        reason = "TAKE PROFIT" if pnl >= TARGET_REBOUND else "STOP LOSS"
                        try:
                            asset_name = symbol.replace('BTC', '')
                            bal = float(client.get_asset_balance(asset=asset_name)['free'])
                            client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=bal)
                            logger.info(f"✅ {reason} {symbol} @ {price} | PnL: {pnl:.2%}")
                            del positions[symbol]
                            with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                                f.write(f"{(RISK_BTC * pnl * 1.0):.2f}")
                        except Exception as e:
                            logger.error(f"❌ FAILED SNIPE SELL {symbol}: {e}")
            
            update_status({
                "time": datetime.now().isoformat(),
                "active_snipes": len(positions),
                "targets": SNIPE_LIST,
                "status": "LIVE SNIPING (BTC PAIRS)"
            })
            gc.collect()
            time.sleep(20)
        except Exception as e:
            logger.error(f"Sniper Loop Error: {e}")
            gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()
