import gc
import gc
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
from binance.enums import *
from dotenv import load_dotenv
from datetime import datetime
import sys

# --- CONFIGURAZIONE ---
load_dotenv()

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

SYMBOL = 'SOLEUR'
QUANTITY = 0.20  # Lotti raddoppiati a 0.20 SOL (~16 EUR)
PROFIT_TARGET_PCT = 0.003  # 0.3% profit (Rapid-fire scalp)
STOP_LOSS_PCT = 0.01      # 1.0% loss protection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.FileHandler('sol_scalper.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    client = Client(API_KEY, API_SECRET)
    logger.info(f"🚀 Sol Scalper Attivo su {SYMBOL}")
    
    in_position = False
    entry_price = 0.0
    
    # Check if we already have SOL
    sol_balance = float(client.get_asset_balance(asset='SOL')['free'])
    if sol_balance >= QUANTITY:
        # Assume existing position
        avg_price = float(client.get_symbol_ticker(symbol=SYMBOL)['price'])
        entry_price = avg_price
        in_position = True
        logger.info(f"📍 Posizione rilevata: {sol_balance} SOL @ ~{entry_price}")

    while True:
        try:
            ticker = client.get_symbol_ticker(symbol=SYMBOL)
            current_price = float(ticker['price'])
            
            if not in_position:
                # Semplice logica di entrata su rintracciamento o segnale base
                # Per ora compriamo se non siamo in posizione (avvio forzato)
                # dato che Sergio vuole azione
                order = client.create_order(symbol=SYMBOL, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=QUANTITY)
                entry_price = float(order['fills'][0]['price'])
                in_position = True
                logger.info(f"🟢 BUY {QUANTITY} SOL @ {entry_price}")
            
            else:
                pnl_pct = (current_price - entry_price) / entry_price
                
                if pnl_pct >= PROFIT_TARGET_PCT:
                    client.create_order(symbol=SYMBOL, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=QUANTITY)
                    logger.info(f"🔴 SELL {QUANTITY} SOL @ {current_price} | PROFIT: {pnl_pct:.2%}")
                    in_position = False
                    gc.collect()
            time.sleep(300) # Pausa dopo profitto
                
                elif pnl_pct <= -STOP_LOSS_PCT:
                    client.create_order(symbol=SYMBOL, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=QUANTITY)
                    logger.info(f"💀 STOP LOSS @ {current_price} | LOSS: {pnl_pct:.2%}")
                    in_position = False
                    gc.collect()
            time.sleep(600) # Pausa dopo loss
            
            gc.collect()
            time.sleep(10)
            
        except Exception as e:
            logger.error(f"Errore: {e}")
            gc.collect()
            time.sleep(30)

if __name__ == "__main__":
    main()
