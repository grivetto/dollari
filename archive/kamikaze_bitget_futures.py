import gc
import ccxt
import os
import time
import logging
from dotenv import load_dotenv
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [KAMIKAZE 🧨] - %(message)s',
                    handlers=[logging.FileHandler("KAMIKAZE.log"), logging.StreamHandler()])
logger = logging.getLogger("KamikazeBitget")

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env.bitget')
bitget = ccxt.bitget({
    'apiKey': os.getenv('BITGET_API_KEY'),
    'secret': os.getenv('BITGET_API_SECRET'),
    'password': os.getenv('BITGET_PASSWORD'),
    'enableRateLimit': True,
    'options': {'defaultType': 'swap', 'adjustForTimeDifference': True}
})

SYMBOL = 'SOL/USDT:USDT'  # Formato CCXT per Bitget USDT-M
LEVERAGE = 20
RISK_USDT = 2.0  # Usiamo massimo 15 USDT per la missione
TAKE_PROFIT_PCT = 1.015  # Target +1.5% sul sottostante (a leva 20x è +30% ROI)

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
        logger.error(f"Errore lettura RSI: {e}")
        return 50

def run_kamikaze():
    logger.info("☠️ KAMIKAZE BOT BITGET ONLINE - PRONTO ALLA LIQUIDAZIONE O AL 1000%")
    
    try:
        bitget.set_leverage(LEVERAGE, SYMBOL)
        logger.info(f"Leva impostata a {LEVERAGE}x su {SYMBOL}")
        bitget.set_margin_mode('isolated', SYMBOL)
        logger.info(f"Margine impostato su Isolato")
    except Exception as e:
        logger.warning(f"Note su leva/margine (potrebbe essere già settato o non supportato su Bitget API in questo modo): {e}")

    in_position = False
    entry_price = 0.0
    qty = 0.0

    # Recupera posizione aperta se esiste
    try:
        open_pos = bitget.fetch_positions([SYMBOL])
        for p in open_pos:
            if float(p.get('contracts', 0)) > 0:
                in_position = True
                entry_price = float(p['entryPrice'])
                qty = float(p['contracts'])
                logger.info(f"🔄 Recuperata posizione esistente: {qty} {SYMBOL} a {entry_price}")
    except Exception as e:
        logger.warning(f"Nessuna posizione aperta recuperabile: {e}")

    import gc
    while True:
        gc.collect()
        try:
            # Check balance
            bal = bitget.fetch_balance({'type': 'swap'})
            usdt_balance = float(bal.get('USDT', {}).get('free', 0.0))
            
            ticker = bitget.fetch_ticker(SYMBOL)
            current_price = float(ticker['last'])

            if not in_position:
                logger.info(f"Fondi disponibili conto Futures: {usdt_balance:.2f} USDT")
                if usdt_balance < RISK_USDT:
                    logger.warning(f"Fondi insufficienti sul conto Futures USDT-M! Hai solo {usdt_balance:.2f} USDT. Trasferisci {RISK_USDT} USDT dal conto Spot ai Futures USDT-M.")
                    time.sleep(60)
                    continue

                # LOGICA KAMIKAZE BITGET:
                rsi = get_rsi(SYMBOL)
                logger.info(f"Analisi mercato {SYMBOL}: Prezzo {current_price} | RSI(1m): {rsi:.1f}")
                
                # Entrata LONG se RSI scende sotto i 35
                if rsi < 35:
                    logger.info(f"🔥 SEGNALE KAMIKAZE! RSI estremo ({rsi:.1f}). Innesco LONG a {current_price}!")
                    # Calcola quantità in base al rischio (usando l'intero rischio * leva non è esatto, il costo margine è: costo = (qty * price) / leva)
                    # qty * price = RISK_USDT * LEVERAGE
                    raw_qty = (RISK_USDT * LEVERAGE) / current_price
                    try:
                        bitget.load_markets()
                        qty = float(bitget.amount_to_precision(SYMBOL, raw_qty))
                    except:
                        qty = round(raw_qty, 2)
                        
                    # Apre posizione
                    order = bitget.create_market_buy_order(SYMBOL, qty)
                    logger.info(f"🚀 ORDINE ESEGUITO: LONG {qty} {SYMBOL} a {current_price} USDT")
                    in_position = True
                    entry_price = current_price

            else:
                # Gestione Take Profit o Liquidazione
                roi = ((current_price - entry_price) / entry_price) * LEVERAGE * 100
                logger.info(f"🧨 TRADE KAMIKAZE ATTIVO: Prezzo {current_price} | Entry {entry_price} | ROI Attuale: {roi:+.2f}%")
                
                if current_price >= entry_price * TAKE_PROFIT_PCT:
                    logger.info(f"💰 BERSAGLIO COLPITO! Take Profit Raggiunto! Chiusura posizione in profitto.")
                    bitget.create_market_sell_order(SYMBOL, qty, params={'reduceOnly': True})
                    in_position = False
                    entry_price = 0.0
                    qty = 0.0
                    logger.info("Missile riarmato. Attesa 5 minuti per evitare FOMO...")
                    time.sleep(300)

            time.sleep(15)

        except ccxt.InsufficientFunds as e:
            logger.error("Fondi spazzati via (Liquidato o stop loss naturale scattato). Bot Kamikaze disattivato.")
            in_position = False
            time.sleep(60)
        except Exception as e:
            logger.error(f"Errore critico API: {e}")
            time.sleep(15)

if __name__ == '__main__':
    run_kamikaze()
