import gc
import ccxt
import os
import time
import logging
from dotenv import load_dotenv
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [MICRO-SHORT 📉] - %(message)s',
                    handlers=[logging.FileHandler("MICRO_SHORT.log"), logging.StreamHandler()])
logger = logging.getLogger("MicroShort")

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env.bitget')
bitget = ccxt.bitget({
    'apiKey': os.getenv('BITGET_API_KEY'),
    'secret': os.getenv('BITGET_API_SECRET'),
    'password': os.getenv('BITGET_PASSWORD'),
    'enableRateLimit': True,
    'options': {'defaultType': 'swap', 'adjustForTimeDifference': True}
})

SYMBOL = 'DOGE/USDT:USDT'  # Scegliamo DOGE per il micro-short
LEVERAGE = 20
RISK_USDT = 2.0  # Micro-arma: rischiamo solo i 5$ rimasti liberi
TAKE_PROFIT_PCT = 0.985  # Target: se DOGE fa -1.5%, noi facciamo +30% ROI in SHORT

def get_rsi(symbol, timeframe='1m', period=14):
    try:
        ohlcv = bitget.fetch_ohlcv(symbol, timeframe, limit=period + 10)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df['rsi'].iloc[-1]
    except Exception as e:
        logger.error(f"Errore RSI: {e}")
        return 50

def run_micro_shorter():
    logger.info("📉 MICRO-SHORTER BITGET ONLINE - PRONTO A SCOMMETTERE SUL SANGUE 🩸")
    
    try:
        bitget.set_leverage(LEVERAGE, SYMBOL)
        bitget.set_margin_mode('isolated', SYMBOL)
        bitget.set_position_mode(False, SYMBOL) # One-way mode
        logger.info(f"Leva {LEVERAGE}x e Margine Isolato configurati su {SYMBOL}")
    except Exception as e:
        logger.warning(f"Note configurazione iniziale: {e}")

    in_position = False
    entry_price = 0.0
    qty = 0.0

    try:
        open_pos = bitget.fetch_positions([SYMBOL])
        for p in open_pos:
            if float(p.get('contracts', 0)) > 0:
                in_position = True
                entry_price = float(p['entryPrice'])
                qty = float(p['contracts'])
                logger.info(f"🔄 Recuperato SHORT aperto: {qty} {SYMBOL} a {entry_price}")
    except: pass

    import gc
    while True:
        gc.collect()
        try:
            bal = bitget.fetch_balance({'type': 'swap'})
            usdt_balance = float(bal.get('USDT', {}).get('free', 0.0))
            
            ticker = bitget.fetch_ticker(SYMBOL)
            current_price = float(ticker['last'])

            if not in_position:
                if usdt_balance < RISK_USDT:
                    logger.warning(f"Fondi insufficienti per il Micro-Short (Liberi: {usdt_balance:.2f} USDT). Serve {RISK_USDT} USDT.")
                    time.sleep(60)
                    continue

                rsi = get_rsi(SYMBOL)
                logger.info(f"Ricerca vittima {SYMBOL}: Prezzo {current_price} | RSI(1m): {rsi:.1f}")
                
                # Entrata SHORT se l'RSI è troppo alto (Ipercomprato) o se pompa a vuoto
                if rsi > 65:
                    logger.info(f"🎯 BERSAGLIO IN IPERCOMPRATO (RSI: {rsi:.1f}). FUOCO SHORT a {current_price}!")
                    raw_qty = (RISK_USDT * LEVERAGE) / current_price
                    try:
                        bitget.load_markets()
                        qty = float(bitget.amount_to_precision(SYMBOL, raw_qty))
                    except:
                        qty = round(raw_qty, 1)
                        
                    # Apre posizione SHORT
                    order = bitget.create_market_sell_order(SYMBOL, qty)
                    logger.info(f"🩸 ORDINE ESEGUITO: SHORT {qty} {SYMBOL} a {current_price} USDT")
                    in_position = True
                    entry_price = current_price

            else:
                # Gestione Take Profit SHORT: Il prezzo deve SCENDERE per guadagnare!
                roi = ((entry_price - current_price) / entry_price) * LEVERAGE * 100
                logger.info(f"📉 SHORT ATTIVO: Prezzo {current_price} | Entry {entry_price} | ROI Attuale: {roi:+.2f}%")
                
                if current_price <= entry_price * TAKE_PROFIT_PCT:
                    logger.info(f"💰 CROLLO INTERCETTATO! Take Profit SHORT Raggiunto! (+30% ROI). Chiudo la posizione.")
                    bitget.create_market_buy_order(SYMBOL, qty, params={'reduceOnly': True})
                    in_position = False
                    entry_price = 0.0
                    qty = 0.0
                    logger.info("Micro-Arma ricaricata. Attesa 5 minuti...")
                    time.sleep(300)

            time.sleep(15)

        except ccxt.InsufficientFunds:
            logger.error("Fondi spazzati via (Liquidato o stop loss). Micro-Shorter in pausa.")
            in_position = False
            time.sleep(60)
        except Exception as e:
            logger.error(f"Errore critico API: {e}")
            time.sleep(15)

if __name__ == '__main__':
    run_micro_shorter()
