import gc
import gc
import gc
import gc
import os
import time
import logging
import requests
import pandas as pd
import pandas_ta as ta
from binance.client import Client
from dotenv import load_dotenv

# Configurazione Log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler("btc_volatility_sniper.log"), logging.StreamHandler()]
)
logger = logging.getLogger("Sniper")

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
API_KEY = os.getenv('BINANCE_API_KEY')
SECRET_KEY = os.getenv('BINANCE_API_SECRET')

SYMBOL = 'BTCEUR'
INTERVAL = Client.KLINE_INTERVAL_5MINUTE
QUANTITY = 0.0002
BB_PERIOD = 20
BB_STD = 2.0
TAKE_PROFIT = 1.008
STOP_LOSS = 0.985

client = Client(API_KEY, SECRET_KEY)

def get_data():
    try:
        klines = client.get_klines(symbol=SYMBOL, interval=INTERVAL, limit=100)
        df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'vol', 'close_time', 'q_vol', 'trades', 'tbb', 'tbq', 'ignore'])
        df['close'] = df['close'].astype(float)
        return df
    except Exception as e:
        logger.error(f"Errore recupero dati: {e}")
        return None

def check_signal(df):
    try:
        # Assicuriamoci di avere abbastanza dati
        if len(df) < BB_PERIOD: return None
        
        bb = ta.bbands(df['close'], length=BB_PERIOD, std=BB_STD)
        if bb is None: return None
        
        # Merge robusto
        df = pd.concat([df, bb], axis=1)
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Identificazione colonne dinamica per evitare KeyErrors
        low_col = [c for c in df.columns if c.startswith('BBL')][0]
        
        # Logica: Prezzo tocca/scende sotto la banda inferiore e poi chiude sopra
        if prev['close'] <= last[low_col] and last['close'] > last[low_col]:
            return "BUY"
    except Exception as e:
        logger.error(f"Errore calcolo segnale: {e}")
    return None

def main():
    logger.info(f"🚀 BTC Volatility Sniper RE-FIXED avviato su {SYMBOL}")
    in_position = False
    entry_price = 0

    while True:
        try:
            df = get_data()
            if df is None:
                gc.collect()
            time.sleep(60)
                continue
                
            ticker = client.get_symbol_ticker(symbol=SYMBOL)
            current_price = float(ticker['price'])
            
            if not in_position:
                signal = check_signal(df)
                if signal == "BUY":
                    logger.info(f"🎯 Segnale SNIPER! BUY {QUANTITY} BTC @ {current_price}")
                    in_position = True
                    entry_price = current_price
            else:
                # Gestione Exit
                if current_price >= entry_price * TAKE_PROFIT:
                    logger.info(f"💰 TAKE PROFIT! SELL @ {current_price} (Entry: {entry_price})")
                    in_position = False
                elif current_price <= entry_price * STOP_LOSS:
                    logger.info(f"🛑 STOP LOSS! SELL @ {current_price} (Entry: {entry_price})")
                    in_position = False
            
            gc.collect()
            time.sleep(30) # Più reattivo per scalping
        except Exception as e:
            logger.error(f"Errore loop: {e}")
            gc.collect()
            time.sleep(30)

if __name__ == "__main__":
    main()
