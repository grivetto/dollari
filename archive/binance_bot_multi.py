import gc
import gc
import gc
#!/usr/bin/env python3
import os
import time
import json
import logging
import pandas as pd
import pandas_ta as ta
from binance.client import Client
from dotenv import load_dotenv
from datetime import datetime, timedelta
import sys

load_dotenv()

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

TRADING_PAIRS = [
    'SOLEUR', 'ETHEUR', 'BNBEUR', 'BTCEUR', 'ADAEUR', 'DOGEEUR', 'AVAXEUR'
]

QUOTE_ASSET = 'EUR'
INTERVAL = '1m'
SLEEP_TIME = 10

# Indicatori (GOD MODE MAX - HYPER-AGGRESSIVE)
RSI_PERIOD = 7
RSI_BUY_THRESHOLD = 45 # Compra prima!
RSI_SELL_THRESHOLD = 55 # Vendi subito!

RISK_PER_TRADE = 0.50 # 50% del saldo libero per trade per essere sicuri di avere EUR
STOP_LOSS_PCT = 0.015
TAKE_PROFIT_PCT = 0.0025
TRAILING_STOP_PCT = 0.001

STATUS_FILE = '/home/sergio/.openclaw/workspace/denaro/multi_status.json'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                   handlers=[logging.FileHandler('trading_bot.log'), logging.StreamHandler()])
logger = logging.getLogger(__name__)

client = Client(API_KEY, API_SECRET)
coin_states = {}

class CoinState:
    def __init__(self, symbol):
        self.symbol = symbol
        self.in_position = False
        self.entry_price = 0.0
        self.position_quantity = 0.0
        self.highest_price = 0.0
        self.total_pnl = 0.0

for pair in TRADING_PAIRS:
    coin_states[pair] = CoinState(pair)

def get_data(symbol):
    try:
        klines = client.get_klines(symbol=symbol, interval=INTERVAL, limit=100)
        df = pd.DataFrame(klines, columns=['ts', 'open', 'high', 'low', 'close', 'volume', 'ct', 'qv', 'nt', 'tb', 'tq', 'i'])
        df['close'] = pd.to_numeric(df['close'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['volume'] = pd.to_numeric(df['volume'])
        return df
    except: return None

def main():
    logger.info("🚀 GOD MODE MAX - ALPHA SQUAD OVERDRIVE")
    while True:
        try:
            # Rimosso btc_balance riga non più necessaria
            for symbol in TRADING_PAIRS:
                df = get_data(symbol)
                if df is None: continue
                
                df['rsi'] = ta.rsi(df['close'], length=RSI_PERIOD)
                price = df['close'].iloc[-1]
                rsi = df['rsi'].iloc[-1]
                state = coin_states[symbol]

                if rsi < RSI_BUY_THRESHOLD and not state.in_position:
                    # Usa il saldo EUR per comprare
                    eur_balance = float(client.get_asset_balance(asset='EUR')['free'])
                    qty_to_buy_eur = eur_balance * RISK_PER_TRADE
                    if qty_to_buy_eur > 10.0: # Binance min 10 EUR
                        try:
                            order = client.create_order(symbol=symbol, side='BUY', type='MARKET', quoteOrderQty=round(qty_to_buy_eur, 2))
                            state.in_position = True
                            state.entry_price = price
                            state.position_quantity = float(order['executedQty'])
                            state.highest_price = price
                            logger.info(f"🟢 OVERDRIVE BUY {symbol} @ {price} EUR")
                        except Exception as e: logger.error(f"❌ BUY ERROR {symbol}: {e}")

                elif state.in_position:
                    if price > state.highest_price: state.highest_price = price
                    pnl = (price - state.entry_price) / state.entry_price
                    trail = (state.highest_price - price) / state.highest_price
                    
                    should_sell = False
                    if pnl >= TAKE_PROFIT_PCT: should_sell = True
                    elif pnl <= -STOP_LOSS_PCT: should_sell = True
                    elif trail >= TRAILING_STOP_PCT and pnl > 0.005: should_sell = True
                    
                    if should_sell:
                        try:
                            client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=state.position_quantity)
                            logger.info(f"🔴 OVERDRIVE SELL {symbol} | PnL: {pnl:.2%}")
                            state.in_position = False
                            with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                                f.write(f"{(state.position_quantity * price * pnl * 1.0):.2f}")
                        except Exception as e: logger.error(f"❌ SELL ERROR {symbol}: {e}")
            
            gc.collect()
            time.sleep(SLEEP_TIME)
        except Exception as e:
            logger.error(f"Loop Error: {e}")
            gc.collect()
            time.sleep(30)

if __name__ == "__main__":
    main()
