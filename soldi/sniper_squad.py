import gc
import os
import time
import math
import logging
import json
from collections import deque
from datetime import datetime
from dotenv import load_dotenv
from binance.client import Client
from binance import ThreadedWebsocketManager
from binance.enums import *

# --- CONFIGURATION ---
CONFIG = {
    "SYMBOLS": ["SOLEUR", "DOGEEUR", "BNBEUR", "AVAXEUR", "LINKEUR", "PEPEEUR", "ETHEUR", "DOTEUR"],
    "MAX_TRADE_EUR": 1000.0,
    "MAX_CONCURRENT_TRADES": 6,
    "TARGET_PERCENT": 0.04,
    "TARGET_FIXED_EUR": 100.0,
    "RSI_BUY_MIN": 30,
    "RSI_BUY_MAX": 85,
    "RSI_OVERSOLD": 30,
    "ATR_TP_MULT": 2.0,           # Take Profit at 2x ATR
    "ATR_SL_MULT": 3.0,           # Stop Loss at 3x ATR
    "TP_TRAILING_FACTOR": 0.999,    # 0.1% drop from peak
    "VAULT_PERCENT": 0.33,          # 33% to vault
    "MIN_TRADE_EUR": 15.0,
    "LOG_FILE": "/home/sergio/denaro/sniper_squad.log",
    "VAULT_FILE": "/home/sergio/denaro/vault.json",
    "MISSION_FILE": "/home/sergio/denaro/daily_mission.json",
}

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(CONFIG["LOG_FILE"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Sniper")

# --- INITIALIZATION ---
load_dotenv('/home/sergio/denaro/.env')
API_KEY=os.getenv('BINANCE_API_KEY')
API_SECRET=os.getenv('BINANCE_API_SECRET')

if not API_KEY or not API_SECRET:
    logger.critical("API Credentials missing in .env!")
    exit(1)

try:
    client = Client(API_KEY, API_SECRET)
except Exception as e:
    logger.critical(f"Failed to connect to Binance: {e}")
    exit(1)

klines = {s: deque(maxlen=100) for s in CONFIG["SYMBOLS"]}
positions = {}

# --- UTILITY FUNCTIONS ---

def get_vault_locked():
    try:
        if os.path.exists(CONFIG["VAULT_FILE"]):
            with open(CONFIG["VAULT_FILE"], 'r') as f:
                return float(json.load(f).get("LOCKED_EUR", 0.0))
    except Exception as e:
        logger.error(f"Error reading vault: {e}")
    return 0.0

def add_to_vault(amount):
    locked = get_vault_locked() + amount
    try:
        with open(CONFIG["VAULT_FILE"], 'w') as f:
            json.dump({"LOCKED_EUR": locked}, f)
        logger.info(f"🔐 Added {amount:.2f}€ to Vault. Total Protected: {locked:.2f}€")
    except Exception as e:
        logger.error(f"Error writing to vault: {e}")

def get_daily_mission():
    today_str = datetime.now().strftime("%Y-%m-%d")
    try:
        if os.path.exists(CONFIG["MISSION_FILE"]):
            with open(CONFIG["MISSION_FILE"], 'r') as f:
                mission = json.load(f)
            if mission.get("date") == today_str:
                return mission
    except Exception as e:
        logger.error(f"Error reading mission: {e}")
    
    try:
        available_eur = float(client.get_asset_balance(asset='EUR')['free'])
    except Exception as e:
        logger.error(f"Error getting EUR balance for mission: {e}")
        available_eur = 0.0
        
    usable_eur = max(0, available_eur - get_vault_locked())
    target_eur = CONFIG["TARGET_FIXED_EUR"]
    
    new_mission = {
        "date": today_str,
        "start_capital": usable_eur,
        "target_eur": target_eur,
        "profit_today": 0.0,
        "achieved": False
    }
    
    try:
        with open(CONFIG["MISSION_FILE"], 'w') as f:
            json.dump(new_mission, f)
        logger.info(f"🕛 Midnight Reset. New Target: {target_eur:.2f}€")
    except Exception as e:
        logger.error(f"Error saving new mission: {e}")
    
    return new_mission

def update_daily_mission(pnl_amount):
    mission = get_daily_mission()
    mission["profit_today"] += pnl_amount
    
    if mission["profit_today"] >= mission["target_eur"] and not mission["achieved"]:
        mission["achieved"] = True
        logger.info(f"🎉 Daily Goal Reached! ({mission['target_eur']:.2f}€). Squad resting until midnight.")
        
    try:
        with open(CONFIG["MISSION_FILE"], 'w') as f:
            json.dump(mission, f)
    except Exception as e:
        logger.error(f"Error updating mission: {e}")
    return mission

def calc_ema(prices, period=9):
    if len(prices) < period: return prices[-1] if prices else 0
    k = 2 / (period + 1)
    ema = prices[0]
    for p in list(prices)[1:]:
        ema = (p * k) + (ema * (1 - k))
    return ema

def calc_rsi(prices, period=14):
    prices = list(prices)
    if len(prices) <= period: return 50.0
    gains, losses = 0.0, 0.0
    for i in range(1, period + 1):
        change = prices[i] - prices[i - 1]
        if change > 0: gains += change
        else: losses -= change
    if losses == 0: return 100.0
    rs = (gains / period) / (losses / period)
    return 100.0 - (100.0 / (1.0 + rs))

def calc_atr(prices, period=14):
    if len(prices) < period + 1: return 0.0
    tr_sum = 0.0
    prices = list(prices)
    for i in range(1, period + 1):
        # Approximate ATR using simple range as we only have closes in klines deque
        # For a real ATR we need High/Low, but we can use a volatility proxy:
        # (Current Close - Previous Close) absolute
        tr_sum += abs(prices[-i] - prices[-i-1])
    return tr_sum / period

def get_step_size(symbol):
    try:
        info = client.get_symbol_info(symbol)
        for f in info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                return float(f['stepSize'])
    except Exception as e:
        logger.error(f"Error getting step size for {symbol}: {e}")
    return 1.0

def round_step(quantity, step_size):
    if step_size == 0: return quantity
    precision = int(round(-math.log10(step_size), 0))
    return round(quantity - (quantity % step_size), precision)

def init_historical_data():
    for sym in CONFIG["SYMBOLS"]:
        try:
            hist = client.get_klines(symbol=sym, interval='1m', limit=100)
            for k in hist: klines[sym].append(float(k[4]))
        except Exception as e:
            logger.error(f"Error loading history for {sym}: {e}")
    logger.info("✅ Historical data loaded.")

def recover_positions():
    for sym in CONFIG["SYMBOLS"]:
        asset = sym.replace('EUR', '')
        try:
            bal = client.get_asset_balance(asset=asset)
            qty = float(bal['free'])
            ticker = client.get_symbol_ticker(symbol=sym)
            price = float(ticker['price'])
            if qty * price > 10.0:
                # For recovered positions, we use a default ATR estimate (1%)
                positions[sym] = {
                    'entry': price, 
                    'qty': qty, 
                    'highest': price, 
                    'tp': price * 1.01, 
                    'sl': price * 0.95
                }
                logger.info(f"🔄 Recovered position: {sym} (Qty: {qty}, Val: ~{qty*price:.2f}€)")
        except Exception as e:
            logger.debug(f"No active position for {sym} during recovery: {e}")

# --- MAIN LOOP ---

def process_socket_msg(msg):
    if 'data' not in msg or 'e' not in msg['data']: return
    event = msg['data']
    
    mission = get_daily_mission()
    
    if event['e'] == 'kline':
        k, symbol = event['k'], event['s']
        price, is_closed = float(k['c']), k['x']
        
        if symbol in positions:
            pos = positions[symbol]
            entry = pos['entry']
            qty = pos['qty']
            tp = pos.get('tp', entry * 1.01)
            sl = pos.get('sl', entry * 0.90)
            highest = max(pos.get('highest', entry), price)
            pos['highest'] = highest
            
            pnl = (price - entry) / entry
            
            # ATR-BASED EXIT LOGIC
            take_profit = price >= tp or (pnl > 0.005 and price < highest * CONFIG["TP_TRAILING_FACTOR"])
            stop_loss = price <= sl
            
            if take_profit or stop_loss:
                reason = "PROFIT" if take_profit else "STOP"
                try:
                    asset = symbol.replace('EUR', '')
                    actual_bal = client.get_asset_balance(asset=asset)
                    actual_qty = float(actual_bal['free'])
                    
                    step = get_step_size(symbol)
                    sell_qty = round_step(actual_qty, step)
                    
                    if sell_qty > 0:
                        client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=sell_qty)
                        real_pnl = (price - entry) * qty
                        mission = update_daily_mission(real_pnl)
                        
                        logger.info(f"⚡ {reason} {symbol} | Gain: {real_pnl:+.2f}€ | Progress: {mission['profit_today']:.2f}€ / {mission['target_eur']:.2f}€")
                        
                        if real_pnl > 0:
                            add_to_vault(real_pnl * CONFIG["VAULT_PERCENT"])
                    
                    del positions[symbol]
                except Exception as e:
                    logger.error(f"Error exiting position {symbol}: {e}")

        if is_closed:
            klines[symbol].append(price)
            if len(klines[symbol]) >= 15:
                rsi = calc_rsi(klines[symbol], 14)
                ema = calc_ema(klines[symbol], 9)
                atr = calc_atr(klines[symbol], 14)
                
                # Trading conditions
                momentum_buy = price > ema * 0.999 and CONFIG["RSI_BUY_MIN"] < rsi < CONFIG["RSI_BUY_MAX"]
                oversold_bounce = rsi < CONFIG["RSI_OVERSOLD"]
                
                if mission["achieved"]: 
                    return
                
                if (momentum_buy or oversold_bounce) and symbol not in positions and len(positions) < CONFIG["MAX_CONCURRENT_TRADES"]:
                    try:
                        available_eur = float(client.get_asset_balance(asset='EUR')['free'])
                        usable_eur = available_eur - get_vault_locked()
                        trade_amount = min(CONFIG["MAX_TRADE_EUR"], usable_eur)
                        
                        if trade_amount < CONFIG["MIN_TRADE_EUR"]: 
                            return
                        
                        step = get_step_size(symbol)
                        qty = round_step(trade_amount / price, step)
                        
                        if qty <= 0: return

                        # CALCULATE ATR-BASED TP/SL
                        tp_price = price + (atr * CONFIG["ATR_TP_MULT"])
                        sl_price = price - (atr * CONFIG["ATR_SL_MULT"])

                        logger.info(f"🚀 BUY {symbol} | Price: {price} | RSI: {rsi:.1f} | ATR: {atr:.4f} | TP: {tp_price:.4f} | SL: {sl_price:.4f}")
                        order = client.create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
                        
                        fills = order.get('fills', [])
                        if fills:
                            executed_qty = sum([float(f['qty']) for f in fills])
                            avg_price = sum([float(f['price']) * float(f['qty']) for f in fills]) / executed_qty
                        else:
                            avg_price = price
                            executed_qty = qty
                        
                        # Recalculate TP/SL based on actual execution price
                        final_tp = avg_price + (atr * CONFIG["ATR_TP_MULT"])
                        final_sl = avg_price - (atr * CONFIG["ATR_SL_MULT"])
                        
                        positions[symbol] = {
                            'entry': avg_price, 
                            'qty': executed_qty, 
                            'highest': avg_price, 
                            'tp': final_tp, 
                            'sl': final_sl
                        }
                    except Exception as e:
                        logger.error(f"Error entering position {symbol}: {e}")

def main():
    logger.info("⚡ SNIPER SQUAD (ATR-Dynamic) avviata")
    
    m = get_daily_mission()
    logger.info(f"📅 Target di oggi: {m['target_eur']:.2f}€. Profitto attuale: {m['profit_today']:.2f}€")
    
    init_historical_data()
    recover_positions()
    
    twm = ThreadedWebsocketManager(api_key=API_KEY, api_secret=API_SECRET)
    twm.start()
    
    streams = [f"{s.lower()}@kline_1m" for s in CONFIG["SYMBOLS"]]
    twm.start_multiplex_socket(callback=process_socket_msg, streams=streams)
    
    try:
        while True:
            get_daily_mission()
            time.sleep(60)
            logger.info("💗 Heartbeat OK. Memoria pulita.")
            gc.collect()
    except KeyboardInterrupt:
        logger.info("Stopping Sniper Squad...")
        twm.stop()
    except Exception as e:
        logger.critical(f"Unexpected main loop error: {e}")
        twm.stop()

if __name__ == "__main__":
    main()
