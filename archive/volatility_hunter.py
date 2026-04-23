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

# Altcoin ad alta volatilità (Coppie BTC per usare il capitale appena arrivato)
WATCHLIST = ["ETHEUR", "SOLEUR", "BNBEUR", "ADAEUR", "DOGEEUR", "LINKEUR", "DOTEUR"]
TIMEFRAME = '5m'
VOL_SPIKE_THRESHOLD = 2.0  # Sensibilità aumentata
PROFIT_TARGET = 0.015      # 2.2% rapido
STOP_LOSS = 0.03          # 4% sicurezza
RISK_BTC = 5.5           # 60€ per trade

STATUS_FILE = '/home/sergio/.openclaw/workspace/denaro/hunter_status.json'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.FileHandler('volatility_hunter.log'), logging.StreamHandler()]
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
    logger.info("🚀 VOLATILITY HUNTER LIVE - BTC PAIRS MODE")
    
    positions = {}

    while True:
        try:
            for symbol in WATCHLIST:
                try:
                    klines = client.get_klines(symbol=symbol, interval=TIMEFRAME, limit=50)
                except Exception as e:
                    if "-2010" in str(e) or "-1121" in str(e):
                        logger.error(f"Skipping {symbol}: API Error {e}")
                        continue
                    if "NameResolutionError" in str(e) or "Read timed out" in str(e) or "HTTPSConnectionPool" in str(e):
                        logger.error(f"Connection error for {symbol}: {e}")
                        time.sleep(10)
                        continue
                    raise e

                df = pd.DataFrame(klines, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qv', 'nt', 'tb', 'tq', 'i'])
                df['c'] = pd.to_numeric(df['c'])
                df['v'] = pd.to_numeric(df['v'])
                
                avg_vol = df['v'].iloc[:-1].mean()
                current_vol = df['v'].iloc[-1]
                price = df['c'].iloc[-1]
                
                # BREAKOUT DETECTION (LIVE ORDERS ENABLED)
                if current_vol > avg_vol * VOL_SPIKE_THRESHOLD and symbol not in positions:
                    logger.info(f"🔥 BREAKOUT RILEVATO: {symbol} | Vol: {current_vol:.2f} (Avg: {avg_vol:.2f})")
                    try:
                        eur_bal = float(client.get_asset_balance(asset="EUR")["free"])
                    except Exception:
                        eur_bal = 0.0
                    
                    try:
                        with open("/home/sergio/.openclaw/workspace/denaro/vault.json", "r") as f:
                            locked = float(__import__("json").load(f).get("LOCKED_EUR", 0))
                        eur_bal = max(0, eur_bal - locked)
                    except Exception:
                        pass
                        
                    if eur_bal < RISK_BTC + 1.0:
                        logger.debug(f"⚠️ Fondo insufficiente ({eur_bal}€ disponibili netti, {RISK_BTC}€ richiesti). Skipping {symbol}")
                        continue
                        
                    qty_to_buy = RISK_BTC / price
                    try:
                        order = client.create_order(
                            symbol=symbol,
                            side='BUY',
                            type='MARKET',
                            quoteOrderQty=round(RISK_BTC, 2)
                        )
                        logger.info(f"🟢 LIVE BUY EXECUTED: {symbol} @ {price} EUR")
                        positions[symbol] = {'entry': price, 'qty': RISK_BTC / price}
                    except Exception as e:
                        if "-2010" in str(e):
                            logger.warning(f"Fondi insufficienti su acquisto mercato per {symbol}. Salto.")
                            time.sleep(10)
                            continue
                        logger.error(f"❌ FAILED BUY {symbol}: {e}")

                # GESTIONE POSIZIONI ESISTENTI
                if symbol in positions:
                    entry = positions[symbol]['entry']
                    pnl = (price - entry) / entry
                    if pnl >= PROFIT_TARGET or pnl <= -STOP_LOSS:
                        reason = "TAKE PROFIT" if pnl >= PROFIT_TARGET else "STOP LOSS"
                        try:
                            asset_name = symbol.replace('EUR', '').replace('BTC', '')
                            bal = float(client.get_asset_balance(asset=asset_name)['free'])
                            if bal > 0:
                                try:
                                    import math
                                    info = client.get_symbol_info(symbol)
                                    step_size_str = [f['stepSize'] for f in info['filters'] if f['filterType'] == 'LOT_SIZE'][0]
                                    step_size = float(step_size_str)
                                    precision = int(round(-math.log(step_size, 10), 0))
                                    bal = math.floor(bal / step_size) * step_size
                                    if precision > 0:
                                        bal = round(bal, precision)
                                    else:
                                        bal = int(bal)
                                    client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=bal)
                                except Exception as e_lot:
                                    logger.error(f"Error rounding LOT_SIZE for {symbol}: {e_lot}")
                                    client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=bal)

                            logger.info(f"✅ {reason} {symbol} @ {price} | PnL: {pnl:.2%}")
                            del positions[symbol]
                            with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                                f.write(f"{(RISK_BTC * pnl * 1.0):.2f}")
                        except Exception as e:
                            if "-2010" in str(e):
                                logger.warning(f"Fondi insufficienti (bilancio < MIN_NOTIONAL) per {symbol} su VENDITA.")
                                del positions[symbol]
                                continue
                            logger.error(f"❌ FAILED SELL {symbol}: {e}")
            
            update_status({
                "time": datetime.now().isoformat(),
                "active_hunters": len(positions),
                "watchlist": WATCHLIST,
                "status": "LIVE SCANNING"
            })
            gc.collect()
            time.sleep(30)
        except Exception as e:
            logger.error(f"Hunter Loop Error: {e}")
            gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()