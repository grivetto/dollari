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

load_dotenv()

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Focus sulle coppie EUR per evitare conversioni inutili e massimizzare il fiat
TRADING_PAIRS = ['SOLEUR', 'ETHEUR', 'BNBEUR', 'BTCEUR'] # Focus solo sui Big
INTERVAL = '1m'
SLEEP_TIME = 15 # Ridotto per evitare ban API (era 2)

# Parametri Scalping Ultra-Aggressivo
RSI_PERIOD = 7
RSI_BUY_THRESHOLD = 45 # Più selettivo (era 50)
RSI_SELL_THRESHOLD = 55 # Più respiro (era 51) 

RISK_PER_TRADE_EUR = 100.0 # Posizioni pesanti da 100 EUR per colpire duro
STOP_LOSS_PCT = 0.008      # 0.8% Stop stretto
TAKE_PROFIT_PCT = 0.0015   # 0.15% Take profit lampo

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                   handlers=[logging.FileHandler('war_machine.log'), logging.StreamHandler()])
logger = logging.getLogger("WarMachine")

client = Client(API_KEY, API_SECRET)

def get_data(symbol):
    try:
        klines = client.get_klines(symbol=symbol, interval=INTERVAL, limit=50)
        df = pd.DataFrame(klines, columns=['ts', 'open', 'high', 'low', 'close', 'volume', 'ct', 'qv', 'nt', 'tb', 'tq', 'i'])
        df['close'] = pd.to_numeric(df['close'])
        return df
    except: return None

def main():
    logger.info("⚔️ WAR MACHINE ACTIVATED - ZERO PRISONERS MODE")
    positions = {} # {symbol: {'qty': 0, 'price': 0}}

    while True:
        try:
            eur_free = float(client.get_asset_balance(asset='EUR')['free'])
            
            for symbol in TRADING_PAIRS:
                df = get_data(symbol)
                if df is None: continue
                
                df['rsi'] = ta.rsi(df['close'], length=RSI_PERIOD)
                current_price = df['close'].iloc[-1]
                rsi = df['rsi'].iloc[-1]

                # Logica SELL
                if symbol in positions:
                    pos = positions[symbol]
                    pnl = (current_price - pos['price']) / pos['price']
                    
                    if pnl >= TAKE_PROFIT_PCT or pnl <= -STOP_LOSS_PCT:
                        try:
                            client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=pos['qty'])
                            logger.info(f"💰 PROFIT/EXIT {symbol} | PnL: {pnl:.2%} | Price: {current_price}")
                            del positions[symbol]
                            # Segnala il guadagno per il monitor
                            with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                                f.write(f"{pnl * RISK_PER_TRADE_EUR:.2f}")
                        except Exception as e: logger.error(f"❌ SELL ERR {symbol}: {e}")

                # Logica BUY
                elif rsi < RSI_BUY_THRESHOLD and eur_free >= RISK_PER_TRADE_EUR:
                    try:
                        order = client.create_order(symbol=symbol, side='BUY', type='MARKET', quoteOrderQty=RISK_PER_TRADE_EUR)
                        positions[symbol] = {
                            'qty': float(order['executedQty']),
                            'price': float(order['fills'][0]['price'])
                        }
                        eur_free -= RISK_PER_TRADE_EUR
                        logger.info(f"🚀 STRIKE BUY {symbol} @ {positions[symbol]['price']} EUR")
                    except Exception as e: logger.error(f"❌ BUY ERR {symbol}: {e}")

            gc.collect()
            time.sleep(SLEEP_TIME)
        except Exception as e:
            logger.error(f"War Loop Error: {e}")
            gc.collect()
            time.sleep(10)

if __name__ == "__main__":
    main()
