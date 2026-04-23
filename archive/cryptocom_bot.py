import gc
import gc
#!/usr/bin/env python3
"""
Crypto.com Quant Bot - Advanced Scalper via CCXT
Modifiche: Opera ora su coppie USDT dato il Trade Convert appena eseguito.
"""

import os
import time
import json
import logging
import pandas as pd
import pandas_ta as ta
import ccxt
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

API_KEY = os.getenv('CRYPTOCOM_API_KEY')
API_SECRET = os.getenv('CRYPTOCOM_API_SECRET')

# Crypto.com Exchange pairs usually use '/' separator in ccxt
SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

TIMEFRAME = '5m' 
BB_PERIOD = 20
BB_STD = 1.8
VOLUME_MA_PERIOD = 20
VOLUME_SPIKE_RATIO = 1.3

# POSITION_SIZE_USDT = 10.0  # 10 USDT per trade - ***MODIFICATO: verrà letto dal file di stato***
TRAILING_STOP_PCT = 0.01  # 1.0%
TAKE_PROFIT_PCT = 0.02    # 2.0%

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("cryptocom_bot.log"), logging.StreamHandler()]
)

try:
    exchange = ccxt.cryptocom({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True,
    })
    exchange.load_markets()
    logging.info("Crypto.com Bot initialized. Migrato su USDT.")
except Exception as e:
    logging.error(f"Init error: {e}")

state = {
    "symbols": {s: {"position": 0, "entry": 0, "highest": 0} for s in SYMBOLS},
    "balance": 0.0,
    "last_update": ""
}

def load_data(symbol):
    try:
        klines = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=100)
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        df.ta.bbands(length=BB_PERIOD, std=BB_STD, append=True)
        df.ta.rsi(length=14, append=True)
        df['vol_sma'] = df['volume'].rolling(VOLUME_MA_PERIOD).mean()
        
        return df
    except Exception as e:
        logging.error(f"Data fetch error for {symbol}: {e}")
        return pd.DataFrame()

def update_status_file():
    try:
        import datetime as dt
        state["last_update"] = dt.datetime.now(dt.timezone.utc).isoformat()
    except Exception:
        state["last_update"] = datetime.utcnow().isoformat()
        
    with open("cryptocom_status.json", "w") as f:
        json.dump(state, f, indent=4)

def check_signals():
    try:
        # Fetch free USDT balance
        balance_info = exchange.fetch_balance()
        usdt_balance = float(balance_info.get('free', {}).get('USDT', 0.0))
        state["balance"] = usdt_balance
        logging.info(f"Current USDT Balance (Crypto.com): {usdt_balance:.2f}")
    except Exception as e:
        logging.error(f"Balance error: {e}")
        return

    for sym in SYMBOLS:
        df = load_data(sym)
        if df.empty or len(df) < BB_PERIOD:
            continue
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        price = latest['close']
        rsi = latest['RSI_14']
        vol = latest['volume']
        vol_sma = latest['vol_sma']
        
        bbl_cols = [c for c in df.columns if c.startswith('BBL_')]
        bbu_cols = [c for c in df.columns if c.startswith('BBU_')]
        
        if not bbl_cols or not bbu_cols:
            continue
            
        lower_bb = latest[bbl_cols[0]]
        upper_bb = latest[bbu_cols[0]]
        
        pos = state["symbols"][sym]
        
        # --- POSITIONS ---
        if pos["position"] > 0:
            if price > pos["highest"]:
                pos["highest"] = price
            
            # Trailing Stop
            ts_level = pos["highest"] * (1.0 - TRAILING_STOP_PCT)
            if price <= ts_level:
                logging.info(f"[SELL] Trailing Stop hit for {sym} at {price}")
                try:
                    exchange.create_market_sell_order(sym, pos["position"])
                except Exception as order_e:
                    logging.error(f"Sell error: {order_e}")
                pos["position"] = 0
                pos["entry"] = 0
                continue
            
            # Take Profit
            profit_pct = (price - pos["entry"]) / pos["entry"]
            if profit_pct >= TAKE_PROFIT_PCT:
                logging.info(f"[SELL] TP hit for {sym} at {price} (+{profit_pct*100:.2f}%)")
                try:
                    exchange.create_market_sell_order(sym, pos["position"])
                except Exception as order_e:
                    logging.error(f"Sell error: {order_e}")
                pos["position"] = 0
                pos["entry"] = 0
                
        # --- ENTRY ---
        elif pos["position"] == 0 and usdt_balance >= 7.10: # USE THE REAL, CONFIRMED LIQUID BALANCE
            is_mean_reversion = (price < lower_bb) and (rsi < 40)
            is_breakout = (price > upper_bb) and (prev['close'] <= prev[bbu_cols[0]])
            is_vol_spike = (vol > vol_sma * VOLUME_SPIKE_RATIO)
            
            if is_mean_reversion or (is_breakout and is_vol_spike):
                signal_type = "Mean Reversion" if is_mean_reversion else "Momentum Breakout"
                logging.info(f"[BUY] {signal_type} for {sym} at {price}")
                try:
                    # In CCXT, amount is in base currency (e.g. BTC)
                    base_qty = (usdt_balance * 0.9) / price # Use 90% of available balance
                    order = exchange.create_market_buy_order(sym, base_qty)
                    # CCXT order objects usually contain 'filled' or 'amount'
                    filled_qty = order.get('filled', base_qty)
                    if filled_qty == 0: filled_qty = base_qty
                    
                    pos["position"] = float(filled_qty)
                    pos["entry"] = price
                    pos["highest"] = price
                    usdt_balance -= (usdt_balance * 0.9) # Deduct the spent amount
                except Exception as order_e:
                    logging.error(f"Buy error: {order_e}")

    update_status_file()

def main():
    while True:
        try:
            check_signals()
        except Exception as e:
            logging.error(f"Main loop error: {e}")
        gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()
