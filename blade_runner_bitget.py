import ccxt
import time
import os
import logging
from dotenv import load_dotenv
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [BLADE RUNNER 🗡️] - %(message)s',
                    handlers=[logging.FileHandler("BLADE_RUNNER.log"), logging.StreamHandler()])

load_dotenv('/home/sergio/denaro/.env.bitget')

try:
    bitget = ccxt.bitget({
        'apiKey': os.getenv('BITGET_API_KEY'),
        'secret': os.getenv('BITGET_API_SECRET'),
        'password': os.getenv('BITGET_PASSWORD'),
        'enableRateLimit': True,
        'options': {'defaultType': 'swap'}
    })
    bitget.load_markets()
except Exception as e:
    logging.error(f"Errore connessione Bitget: {e}")
    exit()

TRADE_USDT = 8.0  # Usiamo 15 USDT di margine
LEVERAGE = 10
TARGET_PROFIT = 0.015  # 1.5% di movimento netto sul sottostante = 15% ROE
STOP_LOSS = -0.010     # 1% stop loss

# Cerca la moneta più volatile del momento
def find_target_coin():
    try:
        tickers = bitget.fetch_tickers()
        candidates = []
        for symbol, data in tickers.items():
            if not symbol.endswith(':USDT'): continue
            if data['quoteVolume'] and data['quoteVolume'] > 5000000:  # Buona liquidità
                change = data.get('percentage', 0.0)
                if change: candidates.append((symbol, change))
        # Prende la coin che sta pompando di più nelle ultime 24h
        if not candidates: return "XRP/USDT:USDT"
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    except Exception as e:
        logging.error(f"Errore ricerca coin: {e}")
        return "XRP/USDT:USDT"

def get_trend(symbol):
    try:
        ohlcv = bitget.fetch_ohlcv(symbol, '5m', limit=10)
        if not ohlcv: return "FLAT"
        df = pd.DataFrame(ohlcv, columns=['t', 'o', 'h', 'l', 'c', 'v'])
        if df['c'].iloc[-1] > df['c'].iloc[0]: return "UP"
        else: return "DOWN"
    except: return "FLAT"

def set_leverage(symbol):
    try: bitget.set_leverage(LEVERAGE, symbol)
    except: pass

def run_blade_runner():
    logging.info("🗡️ BLADE RUNNER ATTIVATO. Caccia spietata ai breakout su Bitget Futures.")
    active_trade = False
    current_symbol = None
    side = None
    entry_price = 0.0
    qty = 0.0

    while True:
        try:
            if not active_trade:
                symbol = find_target_coin()
                trend = get_trend(symbol)
                
                if trend == "FLAT":
                    time.sleep(30)
                    continue
                
                set_leverage(symbol)
                ticker = bitget.fetch_ticker(symbol)
                price = ticker['last']
                
                
                # Check actual balance
                bal = bitget.fetch_balance()
                usdt_free = bal.get('USDT', {}).get('free', 0.0)
                actual_trade_usdt = TRADE_USDT
                if usdt_free < 2.0:
                    logging.warning(f"Fondi USDT insufficienti su Bitget: {usdt_free:.2f}. Pausa.")
                    time.sleep(60)
                    continue
                if usdt_free < TRADE_USDT:
                    actual_trade_usdt = usdt_free * 0.95
                
                raw_qty = (actual_trade_usdt * LEVERAGE) / price

                try: qty = float(bitget.amount_to_precision(symbol, raw_qty))
                except: qty = round(raw_qty, 2)
                
                side = 'buy' if trend == "UP" else 'sell'
                
                try:
                    order = bitget.create_market_order(symbol, side, qty)
                    entry_price = price
                    active_trade = True
                    current_symbol = symbol
                    logging.info(f"🚀 INGRESSO {side.upper()} SU {symbol} a {entry_price}. Margine: {actual_trade_usdt:.2f} USDT (x{LEVERAGE})")
                except Exception as e:
                    logging.error(f"Errore ingresso a mercato: {e}")
                    time.sleep(60)

            else:
                ticker = bitget.fetch_ticker(current_symbol)
                current_price = ticker['last']
                
                if side == 'buy': roi = (current_price - entry_price) / entry_price
                else: roi = (entry_price - current_price) / entry_price
                
                logging.info(f"🗡️ {current_symbol} | Posizione: {side.upper()} | Entry: {entry_price:.4f} | Attuale: {current_price:.4f} | ROI (senza leva): {roi*100:.2f}% | ROE (con leva): {roi*LEVERAGE*100:.2f}%")
                
                if roi >= TARGET_PROFIT:
                    logging.info(f"✅ TAKE PROFIT COLPITO! Chiudo posizione su {current_symbol} in profitto.")
                    close_side = 'sell' if side == 'buy' else 'buy'
                    try: bitget.create_market_order(current_symbol, close_side, qty, params={'reduceOnly': True})
                    except: pass
                    active_trade = False
                    time.sleep(10)
                    
                elif roi <= STOP_LOSS:
                    logging.warning(f"❌ STOP LOSS COLPITO! Chiudo in perdita {current_symbol} per proteggere il capitale.")
                    close_side = 'sell' if side == 'buy' else 'buy'
                    try: bitget.create_market_order(current_symbol, close_side, qty, params={'reduceOnly': True})
                    except: pass
                    active_trade = False
                    time.sleep(30)
            
            time.sleep(15)
            
        except Exception as e:
            logging.error(f"Errore Loop: {e}")
            time.sleep(60)

if __name__ == '__main__':
    run_blade_runner()
