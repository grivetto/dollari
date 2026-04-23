import gc
import ccxt
import os
import time
import logging
from dotenv import load_dotenv
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [KAMIKAZE 🧨] - %(message)s',
                    handlers=[logging.FileHandler("KAMIKAZE.log"), logging.StreamHandler()])
logger = logging.getLogger("KamikazeMexc")

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env.mexc')
mexc = ccxt.mexc({
    'apiKey': os.getenv('MEXC_API_KEY'),
    'secret': os.getenv('MEXC_API_SECRET'),
    'enableRateLimit': True,
    'options': {'defaultType': 'swap'}  # Swap = Perpetual Futures
})

SYMBOL = 'SOL/USDT:USDT'  # Formato futures per CCXT su MEXC
LEVERAGE = 20
RISK_USDT = 5.0
TAKE_PROFIT_PCT = 1.02  # Target: se SOL fa +2%, noi facciamo +40% di ROI

def get_rsi(symbol, timeframe='1m', period=14):
    try:
        ohlcv = mexc.fetch_ohlcv(symbol, timeframe, limit=period + 10)
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
    logger.info("☠️ MISSIONE KAMIKAZE AVVIATA SU MEXC FUTURES (LEVA 20x) ☠️")
    try:
        mexc.load_markets()
        
        # Check balance
        balance = mexc.fetch_balance()
        usdt_free = float(balance.get('USDT', {}).get('free', 0))
        logger.info(f"Fondi Tattici (Futures): {usdt_free:.2f} USDT")
        
        if usdt_free < 4.5:
            logger.error("Fondi insufficienti sul conto Futures! Trasferisci almeno 5 USDT.")
            return

        try:
            mexc.set_leverage(LEVERAGE, SYMBOL)
            logger.info(f"Leva impostata con successo a {LEVERAGE}x su {SYMBOL}")
        except Exception as e:
            logger.warning(f"Nota Leva: {e} (Assicurati che sia 20x nell'app)")
            
        logger.info("Il cecchino è in posizione. In attesa del momento perfetto (RSI estremo < 30) per premere il grilletto...")
        
        position_open = False
        entry_price = 0.0
        qty = 0.0
        
        import gc
        while True:
            gc.collect()
            try:
                ticker = mexc.fetch_ticker(SYMBOL)
                current_price = float(ticker['last'])
                
                if not position_open:
                    rsi = get_rsi(SYMBOL)
                    if rsi < 30: # Condizione estrema di ipervenduto per fare l'ingresso Kamikaze LONG
                        logger.info(f"💥 BERSAGLIO AGGANCIATO! RSI a {rsi:.1f}. Innesco missile LONG su {SYMBOL} a {current_price}...")
                        
                        # Calcola Qty con la leva
                        # Il costo nominale è RISK_USDT, quindi la dimensione della posizione è RISK_USDT * LEVERAGE
                        position_size_usdt = usdt_free * LEVERAGE * 0.95 # Usa il 95% per le fee
                        raw_qty = position_size_usdt / current_price
                        qty = float(mexc.amount_to_precision(SYMBOL, raw_qty))
                        
                        try:
                            # order = mexc.create_market_buy_order(SYMBOL, qty) # Messo al sicuro per test API
                            mexc.create_market_buy_order(SYMBOL, qty)
                            logger.info(f"✅ MISSILATA PARTITA! Aperto LONG di {qty} {SYMBOL} (Valore nominale: {position_size_usdt:.2f} USDT)")
                            position_open = True
                            entry_price = current_price
                        except Exception as oe:
                            logger.error(f"Errore lancio ordine: {oe}")
                    else:
                        logger.info(f"Attesa del momento giusto... Prezzo: {current_price} | RSI: {rsi:.1f} (Target < 30)")
                        
                else:
                    # Monitoraggio TP/SL
                    roi_pct = ((current_price - entry_price) / entry_price) * LEVERAGE * 100
                    logger.info(f"💣 TRADE ATTIVO | Prezzo: {current_price} | Entry: {entry_price} | ROI Attuale: {roi_pct:+.2f}%")
                    
                    if current_price >= entry_price * TAKE_PROFIT_PCT:
                        logger.info(f"🎯 BERSAGLIO COLPITO! Profitto esplosivo raggiunto (+{roi_pct:.2f}% ROI). Chiusura posizione!")
                        try:
                            mexc.create_market_sell_order(SYMBOL, qty)
                            logger.info("✅ POSIZIONE KAMIKAZE CHIUSA CON SUCCESSO. Missione compiuta.")
                            break # Termina il bot dopo il primo attacco
                        except Exception as ce:
                            logger.error(f"Errore chiusura: {ce}")
                            
            except Exception as e:
                logger.error(f"Errore di loop: {e}")
                
            time.sleep(10)
            
    except Exception as base_e:
        logger.error(f"Errore critico: {base_e}")
        import time
        time.sleep(60)

if __name__ == "__main__":
    run_kamikaze()
