import gc
import gc
import gc
import gc
import gc
import gc
import gc
# -*- coding: utf-8 -*-
"""
Binance Trading Bot - RSI + EMA Strategy
Author: OpenClaw Assistant
Version: 1.0
"""

import os
import time
import logging
import pandas as pd
import pandas_ta as ta
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
from dotenv import load_dotenv
from datetime import datetime, timedelta
import sys

# --- Configuration ---
load_dotenv()

# API Credentials
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Trading Parameters
SYMBOL = 'BTCUSDT'
BASE_ASSET = SYMBOL[:-4]
QUOTE_ASSET = 'USDT'

# Strategy Settings
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
EMA_SHORT = 20
EMA_LONG = 50

# Risk Management
RISK_PER_TRADE = 0.10  # 10% of available balance
STOP_LOSS_PCT = 0.02   # 2%
TAKE_PROFIT_PCT = 0.04 # 4%

# Bot Mode
PAPER_TRADING = True   # True = test, False = trading reale
INTERVAL = '15m'       # Candlestick interval
SLEEP_TIME = 60        # Check every minute (adjust as needed)

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global State
client = None
in_position = False
entry_price = 0.0
position_quantity = 0.0
last_order_id = None

# --- Functions ---

def init_client():
    """Initialize Binance client with proper testnet/live configuration."""
    global client
    
    if not API_KEY or not API_SECRET:
        logger.error("API credentials not found in .env file")
        sys.exit(1)
    
    if PAPER_TRADING:
        logger.info("Initializing client in PAPER TRADING mode (testnet)")
        client = Client(API_KEY, API_SECRET, testnet=True)
        # Verify testnet connection
        try:
            client.ping()
            logger.info("Testnet connection successful")
        except Exception as e:
            logger.error(f"Failed to connect to testnet: {e}")
            sys.exit(1)
    else:
        logger.info("Initializing client in LIVE TRADING mode")
        client = Client(API_KEY, API_SECRET)
        try:
            account = client.get_account()
            if account['accountType'] != 'SPOT':
                logger.warning("Account type is not SPOT. Some functions may fail.")
        except Exception as e:
            logger.error(f"Failed to connect to live API: {e}")
            sys.exit(1)

def get_historical_data(symbol, interval, limit=100):
    """Fetch OHLCV data from Binance."""
    try:
        klines = client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit
        )
        
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        
        # Convert types
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        return df
    
    except BinanceAPIException as e:
        logger.error(f"API error fetching data: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return None

def calculate_indicators(df):
    """Add RSI and EMA indicators to dataframe."""
    if df is None or len(df) < max(RSI_PERIOD, EMA_LONG):
        logger.warning("Not enough data for indicators")
        return None
    
    # Calculate RSI
    df['rsi'] = ta.rsi(df['close'], length=RSI_PERIOD)
    
    # Calculate EMAs
    df[f'ema{EMA_SHORT}'] = ta.ema(df['close'], length=EMA_SHORT)
    df[f'ema{EMA_LONG}'] = ta.ema(df['close'], length=EMA_LONG)
    
    # Price crosses EMA20 for buy signal detection
    df['price_above_ema20'] = df['close'] > df[f'ema{EMA_SHORT}']
    df['ema_cross_up'] = (df['price_above_ema20']) & (~df['price_above_ema20'].shift(1).fillna(False))
    
    return df

def get_current_price(symbol):
    """Get current price for symbol."""
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except Exception as e:
        logger.error(f"Error getting price: {e}")
        return None

def get_available_balance(asset):
    """Get available balance for asset."""
    try:
        balance = client.get_asset_balance(asset=asset)
        return float(balance['free'])
    except Exception as e:
        logger.error(f"Error getting balance for {asset}: {e}")
        return 0.0

def get_symbol_filters(symbol):
    """Get trading filters for symbol."""
    try:
        info = client.get_symbol_info(symbol)
        filters = {}
        for f in info['filters']:
            filters[f['filterType']] = f
        return filters
    except Exception as e:
        logger.error(f"Error getting symbol info: {e}")
        return None

def round_quantity(quantity, step_size):
    """Round quantity to valid step size."""
    if step_size == 0:
        return quantity
    precision = int(round(-1 * (step_size).log10(), 0))
    return round(quantity - (quantity % step_size), precision)

def calculate_position_size(price, available_balance):
    """Calculate position size based on risk percentage."""
    position_value = available_balance * RISK_PER_TRADE
    quantity = position_value / price
    return quantity

def check_buy_signal(df, current_price):
    """Check if buy conditions are met."""
    latest = df.iloc[-1]
    
    # Condition 1: RSI oversold
    rsi_oversold = latest['rsi'] < RSI_OVERSOLD
    
    # Condition 2: Price crossed above EMA20
    ema_cross = latest['ema_cross_up']
    
    if rsi_oversold and ema_cross:
        logger.info(f"BUY SIGNAL: RSI={latest['rsi']:.2f}, Price crossed above EMA{EMA_SHORT}")
        return True
    return False

def check_sell_signal(current_price, entry_price):
    """Check if sell conditions are met."""
    # Take profit
    if current_price >= entry_price * (1 + TAKE_PROFIT_PCT):
        logger.info(f"SELL SIGNAL: Take profit hit. Current: {current_price}, Entry: {entry_price}")
        return True, "TP"
    
    # Stop loss
    if current_price <= entry_price * (1 - STOP_LOSS_PCT):
        logger.info(f"SELL SIGNAL: Stop loss hit. Current: {current_price}, Entry: {entry_price}")
        return True, "SL"
    
    # RSI overbought exit (optional)
    # Could fetch fresh data to check current RSI
    
    return False, None

def place_order(symbol, side, quantity, price=None, order_type=ORDER_TYPE_LIMIT):
    """Place an order on Binance."""
    try:
        filters = get_symbol_filters(symbol)
        if not filters:
            logger.error("Cannot place order: no filters available")
            return None
        
        # Round quantity to step size
        step_size = float(filters['LOT_SIZE']['stepSize'])
        quantity = round_quantity(quantity, step_size)
        
        # Check minimum notional
        min_notional = float(filters['MIN_NOTIONAL']['minNotional'])
        if quantity * price < min_notional:
            logger.error(f"Order too small: {quantity * price} < {min_notional}")
            return None
        
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': f"{quantity:.8f}"
        }
        
        if order_type == ORDER_TYPE_LIMIT:
            params['timeInForce'] = TIME_IN_FORCE_GTC
            params['price'] = f"{price:.8f}"
        
        logger.info(f"Placing {side} order: {quantity:.8f} at {price}")
        
        if PAPER_TRADING:
            # Simulate order in paper trading
            logger.info(f"[PAPER] Order would be placed: {params}")
            order = {
                'orderId': int(time.time() * 1000),
                'status': 'FILLED',
                'side': side,
                'quantity': quantity,
                'price': price
            }
            return order
        else:
            order = client.create_order(**params)
            logger.info(f"Order placed successfully: {order['orderId']}")
            return order
    
    except BinanceAPIException as e:
        logger.error(f"API error placing order: {e}")
        return None
    except BinanceOrderException as e:
        logger.error(f"Order error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

def main():
    """Main trading loop."""
    global in_position, entry_price, position_quantity, last_order_id
    
    logger.info("=" * 50)
    logger.info("BINANCE TRADING BOT STARTED")
    logger.info(f"Symbol: {SYMBOL}")
    logger.info(f"Mode: {'PAPER TRADING' if PAPER_TRADING else 'LIVE TRADING'}")
    logger.info(f"Strategy: RSI({RSI_PERIOD}) + EMA{EMA_SHORT}/{EMA_LONG}")
    logger.info(f"Risk: {RISK_PER_TRADE*100}% per trade, SL: {STOP_LOSS_PCT*100}%, TP: {TAKE_PROFIT_PCT*100}%")
    logger.info("=" * 50)
    
    init_client()
    
    while True:
        try:
            # 1. Get latest data
            df = get_historical_data(SYMBOL, INTERVAL, limit=100)
            if df is None:
                gc.collect()
            time.sleep(SLEEP_TIME)
                continue
            
            df = calculate_indicators(df)
            if df is None:
                gc.collect()
            time.sleep(SLEEP_TIME)
                continue
            
            current_price = get_current_price(SYMBOL)
            if current_price is None:
                gc.collect()
            time.sleep(SLEEP_TIME)
                continue
            
            latest = df.iloc[-1]
            logger.info(f"Price: {current_price:.2f} | RSI: {latest['rsi']:.2f} | "
                       f"EMA{EMA_SHORT}: {latest[f'ema{EMA_SHORT}']:.2f} | "
                       f"EMA{EMA_LONG}: {latest[f'ema{EMA_LONG}']:.2f}")
            
            # 2. Trading Logic
            if not in_position:
                # Check for buy signal
                if check_buy_signal(df, current_price):
                    # Calculate position size
                    available_usdt = get_available_balance(QUOTE_ASSET)
                    if available_usdt <= 10:  # Minimum $10
                        logger.warning(f"Insufficient balance: {available_usdt} USDT")
                        gc.collect()
            time.sleep(SLEEP_TIME)
                        continue
                    
                    position_qty = calculate_position_size(current_price, available_usdt)
                    
                    # Place buy order
                    order = place_order(
                        symbol=SYMBOL,
                        side=SIDE_BUY,
                        quantity=position_qty,
                        price=current_price
                    )
                    
                    if order:
                        in_position = True
                        entry_price = current_price
                        position_quantity = float(order['quantity'])
                        last_order_id = order['orderId']
                        logger.info(f"ENTERED POSITION: Qty={position_quantity:.8f}, Price={entry_price:.2f}")
            
            else:
                # We're in a position, check sell conditions
                sell_signal, reason = check_sell_signal(current_price, entry_price)
                if sell_signal:
                    # Sell the position
                    order = place_order(
                        symbol=SYMBOL,
                        side=SIDE_SELL,
                        quantity=position_quantity,
                        price=current_price
                    )
                    
                    if order:
                        logger.info(f"EXITED POSITION ({reason}): Qty={position_quantity:.8f}, Price={current_price:.2f}")
                        # Reset position state
                        in_position = False
                        entry_price = 0.0
                        position_quantity = 0.0
                        last_order_id = None
            
            gc.collect()
            time.sleep(SLEEP_TIME)
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            gc.collect()
            time.sleep(SLEEP_TIME)

if __name__ == "__main__":
    main()