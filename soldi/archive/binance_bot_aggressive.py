import gc
import gc
import gc
# -*- coding: utf-8 -*-
"""
Binance Trading Bot - Versione AGGRESSIVA con Dashboard Completa
Multi-indicator: RSI + MACD + EMA + Volume + Trailing Stop
"""

import os
import time
import json
import logging
import pandas as pd
import pandas_ta as ta
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
from dotenv import load_dotenv
from datetime import datetime
import sys
import gc

# --- CONFIGURAZIONE AGGRESSIVA ---
load_dotenv()

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

SYMBOL = 'SOLEUR'
QUOTE_ASSET = 'EUR'
INTERVAL = '5m'
SLEEP_TIME = 30

# Strategia
RSI_PERIOD = 14
RSI_BUY_THRESHOLD = 50
RSI_SELL_THRESHOLD = 65
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
EMA_SHORT = 9
EMA_LONG = 21
RISK_PER_TRADE = 0.85
STOP_LOSS_PCT = 0.015
TAKE_PROFIT_PCT = 0.0075
TRAILING_STOP_PCT = 0.02
VOLUME_SPIKE_MULT = 1.5

PAPER_TRADING = False

STATUS_FILE = '/home/sergio/.openclaw/workspace/denaro/bot_status.json'
HISTORY_FILE = '/home/sergio/.openclaw/workspace/denaro/trade_history.json'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot_aggressive.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

client = None
in_position = False
entry_price = 0.0
position_quantity = 0.0
highest_price = 0.0
total_trades = 0
winning_trades = 0
total_pnl = 0.0

def update_dashboard(df, current_price, signal="WAITING"):
    """Aggiorna il file JSON con TUTTI i dati di analisi"""
    global in_position, entry_price, position_quantity, highest_price
    global total_trades, winning_trades, total_pnl
    
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    # Calcola distanze EMA
    ema_short_dist = ((current_price - latest['ema_short']) / latest['ema_short']) * 100
    ema_long_dist = ((current_price - latest['ema_long']) / latest['ema_long']) * 100
    
    # Trend EMA
    ema_trend = "RIBASSISTA" if latest['ema_short'] < latest['ema_long'] else "RIALZISTA"
    
    # RSI trend
    rsi_trend = "↗️" if latest['rsi'] > prev['rsi'] else "↘️"
    
    # MACD trend
    macd_trend = "↗️" if latest['macd_hist'] > prev['macd_hist'] else "↘️"
    
    # Segnali
    signals = {
        "rsi_buy": bool(latest['rsi'] < RSI_BUY_THRESHOLD),
        "rsi_sell": bool(latest['rsi'] > RSI_SELL_THRESHOLD),
        "macd_bullish": bool(latest['macd'] > latest['macd_signal']),
        "macd_hist_positive": bool(latest['macd_hist'] > 0),
        "price_above_ema_short": bool(current_price > latest['ema_short']),
        "price_above_ema_long": bool(current_price > latest['ema_long']),
        "ema_bullish": bool(latest['ema_short'] > latest['ema_long']),
        "volume_spike": bool(latest['vol_spike']) if 'vol_spike' in latest else False,
    }
    
    # Conta segnali buy
    buy_score = sum([
        signals["rsi_buy"],
        signals["macd_bullish"] or signals["macd_hist_positive"],
        signals["price_above_ema_short"],
        signals["volume_spike"]
    ])
    
    # Livello RSI
    if latest['rsi'] < 30:
        rsi_level = "SOVRAVENDUTO FORTE"
        rsi_color = "#00ff88"
    elif latest['rsi'] < RSI_BUY_THRESHOLD:
        rsi_level = "SOVRAVENDUTO"
        rsi_color = "#00b894"
    elif latest['rsi'] < 50:
        rsi_level = "NEUTRO BASSO"
        rsi_color = "#fdcb6e"
    elif latest['rsi'] < RSI_SELL_THRESHOLD:
        rsi_level = "NEUTRO ALTO"
        rsi_color = "#fdcb6e"
    elif latest['rsi'] < 70:
        rsi_level = "SOVRACCOMPRATO"
        rsi_color = "#e17055"
    else:
        rsi_level = "SOVRACCOMPRATO FORTE"
        rsi_color = "#ff6b6b"
    
    # Price history (ultimi 20 candle per grafico)
    price_history = []
    for i in range(min(20, len(df))):
        idx = len(df) - 1 - i
        price_history.append({
            "time": i * 5,  # minuti fa
            "price": round(df.iloc[idx]['close'], 2),
            "rsi": round(df.iloc[idx]['rsi'], 1) if pd.notna(df.iloc[idx]['rsi']) else 0,
            "volume": round(df.iloc[idx]['volume'], 4)
        })
    price_history.reverse()
    
    status = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": SYMBOL,
        "mode": "LIVE" if not PAPER_TRADING else "PAPER",
        "status": "IN_POSIZIONE" if in_position else "IN_ATTESA",
        "signal": signal,
        
        # Prezzo
        "price": round(current_price, 2),
        "price_change_5m": round(current_price - df.iloc[-2]['close'], 2) if len(df) > 1 else 0,
        "price_change_pct": round(((current_price - df.iloc[-2]['close']) / df.iloc[-2]['close']) * 100, 3) if len(df) > 1 else 0,
        
        # Candele attuali
        "candle": {
            "open": round(latest['open'], 2),
            "high": round(latest['high'], 2),
            "low": round(latest['low'], 2),
            "close": round(latest['close'], 2),
            "volume": round(latest['volume'], 4),
            "body_size": round(abs(latest['close'] - latest['open']), 2),
            "is_green": bool(latest['close'] > latest['open'])
        },
        
        # Indicatori tecnici
        "indicators": {
            "rsi": {
                "value": round(latest['rsi'], 2),
                "trend": rsi_trend,
                "level": rsi_level,
                "color": rsi_color,
                "buy_zone": bool(latest['rsi'] < RSI_BUY_THRESHOLD),
                "sell_zone": bool(latest['rsi'] > RSI_SELL_THRESHOLD)
            },
            "macd": {
                "value": round(latest['macd'], 2),
                "signal": round(latest['macd_signal'], 2),
                "histogram": round(latest['macd_hist'], 2),
                "trend": macd_trend,
                "bullish": bool(latest['macd'] > latest['macd_signal']),
                "hist_positive": bool(latest['macd_hist'] > 0)
            },
            "ema": {
                "short": {"period": EMA_SHORT, "value": round(latest['ema_short'], 2)},
                "long": {"period": EMA_LONG, "value": round(latest['ema_long'], 2)},
                "trend": ema_trend,
                "bullish": bool(latest['ema_short'] > latest['ema_long']),
                "price_to_short_pct": round(ema_short_dist, 3),
                "price_to_long_pct": round(ema_long_dist, 3)
            },
            "volume": {
                "current": round(latest['volume'], 4),
                "avg": round(latest.get('vol_ma', latest['volume']), 4),
                "spike": signals["volume_spike"],
                "spike_ratio": round(latest['volume'] / latest.get('vol_ma', latest['volume']), 2) if latest.get('vol_ma', 0) > 0 else 1
            }
        },
        
        # Segnali
        "signals": signals,
        "buy_score": buy_score,
        "buy_score_pct": round((buy_score / 4) * 100),
        
        # Previsione
        "prediction": {
            "direction": "RIALZISTA" if buy_score >= 3 else ("NEUTRA" if buy_score >= 2 else "RIBASSISTA"),
            "confidence": round((buy_score / 4) * 100),
            "next_action": "COMPRA" if buy_score >= 3 else "ATTENDI"
        },
        
        # Posizione
        "position": {
            "active": in_position,
            "entry_price": round(entry_price, 2) if entry_price > 0 else 0,
            "quantity": round(position_quantity, 8) if position_quantity > 0 else 0,
            "current_value": round(position_quantity * current_price, 2) if position_quantity > 0 else 0,
            "unrealized_pnl": round((current_price - entry_price) * position_quantity, 4) if in_position else 0,
            "unrealized_pnl_pct": round(((current_price - entry_price) / entry_price) * 100, 2) if in_position else 0,
            "highest_price": round(highest_price, 2) if highest_price > 0 else 0,
            "tp_price": round(entry_price * (1 + TAKE_PROFIT_PCT), 2) if entry_price > 0 else 0,
            "sl_price": round(entry_price * (1 - STOP_LOSS_PCT), 2) if entry_price > 0 else 0,
            "trailing_sl": round(highest_price * (1 - TRAILING_STOP_PCT), 2) if highest_price > 0 else 0,
            "distance_to_tp_pct": round(((entry_price * (1 + TAKE_PROFIT_PCT) - current_price) / current_price) * 100, 2) if in_position else 0,
            "distance_to_sl_pct": round(((current_price - entry_price * (1 - STOP_LOSS_PCT)) / current_price) * 100, 2) if in_position else 0,
        },
        
        # Statistiche
        "stats": {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": total_trades - winning_trades,
            "win_rate": round((winning_trades / total_trades * 100), 1) if total_trades > 0 else 0,
            "total_pnl": round(total_pnl, 4)
        },
        
        # Config
        "config": {
            "rsi_buy_threshold": RSI_BUY_THRESHOLD,
            "rsi_sell_threshold": RSI_SELL_THRESHOLD,
            "take_profit": f"{TAKE_PROFIT_PCT*100}%",
            "stop_loss": f"{STOP_LOSS_PCT*100}%",
            "trailing_stop": f"{TRAILING_STOP_PCT*100}%",
            "risk_per_trade": f"{RISK_PER_TRADE*100}%",
            "interval": INTERVAL
        },
        
        # Storico prezzi per grafico
        "price_history": price_history
    }
    
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)

def add_trade_to_history(trade):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            try:
                history = json.load(f)
            except:
                history = []
    history.insert(0, trade)
    history = history[:50]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def init_client():
    global client
    if not API_KEY or not API_SECRET:
        logger.error("Chiavi API mancanti")
        sys.exit(1)
    if PAPER_TRADING:
        client = Client(API_KEY, API_SECRET, testnet=True)
        logger.info("🔧 PAPER TRADING")
    else:
        client = Client(API_KEY, API_SECRET)
        logger.info("💰 LIVE TRADING")
    client.ping()
    logger.info("✅ Connessione OK")

def get_data(symbol, interval, limit=100):
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(klines, columns=[
            'ts', 'open', 'high', 'low', 'close', 'volume',
            'close_ts', 'quote_vol', 'trades', 'taker_buy', 'taker_quote', 'ignore'
        ])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        return df
    except Exception as e:
        logger.error(f"Errore dati: {e}")
        return None

def calc_indicators(df):
    df['rsi'] = ta.rsi(df['close'], length=RSI_PERIOD)
    macd = ta.macd(df['close'], fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL)
    df['macd'] = macd['MACD_12_26_9']
    df['macd_signal'] = macd['MACDs_12_26_9']
    df['macd_hist'] = macd['MACDh_12_26_9']
    df['ema_short'] = ta.ema(df['close'], length=EMA_SHORT)
    df['ema_long'] = ta.ema(df['close'], length=EMA_LONG)
    df['vol_ma'] = df['volume'].rolling(20).mean()
    df['vol_spike'] = df['volume'] > (df['vol_ma'] * VOLUME_SPIKE_MULT)
    return df

def check_buy_signal(df):
    latest = df.iloc[-1]
    rsi_ok = latest['rsi'] < RSI_BUY_THRESHOLD
    macd_ok = latest['macd_hist'] > 0 or (latest['macd'] > latest['macd_signal'])
    ema_ok = latest['close'] > latest['ema_short']
    vol_ok = latest['vol_spike']
    signals = sum([rsi_ok, macd_ok, ema_ok, vol_ok])
    if signals >= 3:
        return True
    return False

def check_sell_signal(current_price):
    global highest_price
    if current_price > highest_price:
        highest_price = current_price
    tp_price = entry_price * (1 + TAKE_PROFIT_PCT)
    if current_price >= tp_price:
        return True, "TP"
    sl_price = entry_price * (1 - STOP_LOSS_PCT)
    if current_price <= sl_price:
        return True, "SL"
    trailing_sl = highest_price * (1 - TRAILING_STOP_PCT)
    if current_price <= trailing_sl and highest_price > entry_price:
        return True, "TRAIL"
    return False, None

def get_price(symbol):
    try:
        return float(client.get_symbol_ticker(symbol=symbol)['price'])
    except:
        return None

def get_balance(asset):
    try:
        b = client.get_asset_balance(asset=asset)
        return float(b['free']) if b else 0.0
    except:
        return 0.0

def place_order(symbol, side, quantity, price):
    global total_trades, winning_trades, total_pnl
    try:
        if PAPER_TRADING:
            logger.info(f"📝 [PAPER] {side} {quantity:.8f} @ {price:.2f}")
            return {'orderId': int(time.time()*1000), 'quantity': quantity, 'price': price}
        else:
            order = client.create_order(
                symbol=symbol, side=side, type='LIMIT',
                timeInForce='GTC', quantity=f"{quantity:.8f}", price=f"{price:.8f}"
            )
            logger.info(f"✅ {side}: {order['orderId']}")
            return order
    except Exception as e:
        logger.error(f"❌ Errore: {e}")
        return None

def main():
    global in_position, entry_price, position_quantity, highest_price
    global total_trades, winning_trades, total_pnl
    
    logger.info("="*50)
    logger.info("🚀 BOT AGGRESSIVO CON DASHBOARD COMPLETA")
    logger.info("="*50)
    
    init_client()
    
    # Carica storico
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
                total_trades = sum(1 for t in history if t.get('type') == 'SELL')
                winning_trades = sum(1 for t in history if t.get('type') == 'SELL' and t.get('pnl', 0) > 0)
                total_pnl = sum(t.get('pnl', 0) for t in history if t.get('type') == 'SELL')
        except:
            pass
    
    while True:
        try:
            df = get_data(SYMBOL, INTERVAL, 100)
            if df is None:
                gc.collect()
                time.sleep(SLEEP_TIME)
                continue
            
            df = calc_indicators(df)
            price = get_price(SYMBOL)
            if price is None:
                gc.collect()
                time.sleep(SLEEP_TIME)
                continue
            
            latest = df.iloc[-1]
            signal = "WAITING"
            
            if not in_position:
                if check_buy_signal(df):
                    balance = get_balance(QUOTE_ASSET)
                    try:
                        with open("/home/sergio/.openclaw/workspace/denaro/vault.json", "r") as f:
                            vault = __import__("json").load(f)
                            locked = float(vault.get("LOCKED_EUR", 0))
                            balance = max(0, balance - locked)
                    except: pass

                    qty = round((balance * RISK_PER_TRADE) / price, 2)
                    if qty * price > 5:
                        order = place_order(SYMBOL, SIDE_BUY, qty, price)
                        if order:
                            in_position = True
                            entry_price = price
                            position_quantity = qty
                            highest_price = price
                            signal = "BUY"
                            logger.info(f"🟢 ENTRATO: {qty:.8f} BTC @ {price:.2f}")
            else:
                if price > highest_price:
                    highest_price = price
                sell, reason = check_sell_signal(price)
                if sell:
                    order = place_order(SYMBOL, SIDE_SELL, position_quantity, price)
                    if order:
                        pnl = (price - entry_price) * position_quantity
                        pct = ((price - entry_price) / entry_price) * 100
                        signal = f"SELL ({reason})"
                        total_trades += 1
                        if pnl > 0:
                            winning_trades += 1
                        total_pnl += pnl
                        add_trade_to_history({
                            "type": "SELL",
                            "reason": reason,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "entry_price": round(entry_price, 2),
                            "exit_price": round(price, 2),
                            "quantity": round(position_quantity, 8),
                            "pnl": round(pnl, 4),
                            "pnl_pct": round(pct, 2)
                        })
                        logger.info(f"🔴 USCITO ({reason}): PnL={pnl:.4f} ({pct:+.2f}%)")
                        in_position = False
                        entry_price = 0
                        position_quantity = 0
                        highest_price = 0
                        time.sleep(5)
                        continue
            
            # Aggiorna dashboard con TUTTI i dati
            update_dashboard(df, price, signal)
            
            time.sleep(SLEEP_TIME)
            gc.collect()
            
        except KeyboardInterrupt:
            logger.info("🛑 Fermato")
            sys.exit(0)
        except Exception as e:
            logger.error(f"❌ Errore: {e}")
            time.sleep(SLEEP_TIME)

if __name__ == "__main__":
    main()
