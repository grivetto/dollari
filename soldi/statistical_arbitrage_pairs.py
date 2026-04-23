import ccxt
import time
import os
import sys
import logging
import numpy as np
from collections import deque
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [PAIRS TRADER ⚖️] - %(message)s',
                    handlers=[logging.FileHandler("PAIRS_TRADER.log"), logging.StreamHandler()])

sys.path.insert(0, '/home/sergio/.openclaw/workspace/denaro')
import local_price

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
    logging.error(f"Errore connessione: {e}")
    exit()

def run_pairs_trading():
    # Settaggi Strategici
    SYM_A = 'BTC/USDT:USDT'  # Leader
    SYM_B = 'ETH/USDT:USDT'  # Follower
    MARGIN_PER_LEG_USDT = 15.0 # Rischio 15$ per lato (Totale 30$)
    LEVERAGE = 10
    
    # Parametri Statistici (Z-Score)
    WINDOW_SIZE = 120 # Quanti prezzi storici tenere (es. 120 * 5s = 10 minuti di storico per la cointegrazione veloce)
    Z_SCORE_ENTRY = 2.0  # Deviazioni standard per ENTRARE (L'elastico e' teso)
    Z_SCORE_EXIT = 0.5   # Deviazioni standard per USCIRE (L'elastico si e' rilassato)
    
    try:
        bitget.set_leverage(LEVERAGE, SYM_A)
        bitget.set_leverage(LEVERAGE, SYM_B)
    except: pass

    logging.info(f"⚖️ STATISTICAL ARBITRAGE (Pairs Trading) INIZIALIZZATO.")
    logging.info(f"Coppia Cointegrata: {SYM_A} <-> {SYM_B} | Leva {LEVERAGE}x | Z-Score Entry: {Z_SCORE_ENTRY}")
    
    history_A = deque(maxlen=WINDOW_SIZE)
    history_B = deque(maxlen=WINDOW_SIZE)
    ratios = deque(maxlen=WINDOW_SIZE)
    
    position_open = False
    trade_side_A = None # 'short' o 'long'
    
    while True:
        try:
            # Usa il websocket locale per azzerare la latenza
            ticker_A = local_price.get_ticker('BTC/USDT')
            ticker_B = local_price.get_ticker('ETH/USDT')
            
            if not ticker_A or not ticker_B:
                ticker_A = bitget.fetch_ticker(SYM_A)
                ticker_B = bitget.fetch_ticker(SYM_B)
                
            price_A = ticker_A['last']
            price_B = ticker_B['last']
            
            if not price_A or not price_B: continue
            
            history_A.append(price_A)
            history_B.append(price_B)
            
            ratio = price_A / price_B
            ratios.append(ratio)
            
            if len(ratios) == WINDOW_SIZE:
                # Calcolo Statistico: Z-Score
                mean_ratio = np.mean(ratios)
                std_ratio = np.std(ratios)
                
                if std_ratio > 0:
                    z_score = (ratio - mean_ratio) / std_ratio
                else:
                    z_score = 0
                
                # logging.info(f"Z-Score: {z_score:.2f} (Ratio: {ratio:.4f} | Mean: {mean_ratio:.4f})")
                
                # --- LOGICA DI ENTRATA ---
                if not position_open:
                    if z_score > Z_SCORE_ENTRY:
                        # Il Ratio e' troppo alto: A e' sopravvalutato rispetto a B.
                        # -> SHORT A, LONG B
                        logging.warning(f"🚨 [ELASTICO TESO] Z-Score {z_score:.2f} > {Z_SCORE_ENTRY}. BTC Sopravvalutato su ETH.")
                        logging.warning(f"⚖️ Esecuzione Pairs Trade: SHORT {SYM_A} & LONG {SYM_B}")
                        
                        qty_A = (MARGIN_PER_LEG_USDT * LEVERAGE) / price_A
                        qty_B = (MARGIN_PER_LEG_USDT * LEVERAGE) / price_B
                        
                        try:
                            # Esecuzione Atomica (o quasi)
                            bitget.create_market_sell_order(SYM_A, float(bitget.amount_to_precision(SYM_A, qty_A)))
                            bitget.create_market_buy_order(SYM_B, float(bitget.amount_to_precision(SYM_B, qty_B)))
                            
                            position_open = True
                            trade_side_A = 'short'
                            logging.info("✅ Trade di Cointegrazione APERTO con successo a Rischio Zero.")
                            
                            # Notifica Telegram
                            try:
                                import requests
                                load_dotenv('/home/sergio/denaro/.env.telegram')
                                tk = os.getenv('TELEGRAM_BOT_TOKEN')
                                cid = os.getenv('TELEGRAM_CHAT_ID')
                                msg = f"⚖️ *STATISTICAL ARBITRAGE (Pairs Trader)* ⚖️\n\nHo rilevato una divergenza matematica estrema (Z-Score: {z_score:.2f}) tra Bitcoin ed Ethereum.\nL'elastico si è spezzato.\n\n*Azione Simultanea:* SHORT {SYM_A} 🔴 + LONG {SYM_B} 🟢 (Leva {LEVERAGE}x)\n*Rischio Mercato:* ZERO ASSOLUTO (Market Neutral).\n\nAttendo il ritorno alla media (Snapback) per chiudere in profitto. 🕸️"
                                requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", data={"chat_id": cid, "text": msg, "parse_mode": "Markdown"})
                            except: pass
                            
                        except Exception as e_trade:
                            logging.error(f"Errore apertura Pairs Trade: {e_trade}")
                            
                    elif z_score < -Z_SCORE_ENTRY:
                        # Il Ratio e' troppo basso: A e' sottovalutato rispetto a B.
                        # -> LONG A, SHORT B
                        logging.warning(f"🚨 [ELASTICO TESO] Z-Score {z_score:.2f} < {-Z_SCORE_ENTRY}. BTC Sottovalutato su ETH.")
                        logging.warning(f"⚖️ Esecuzione Pairs Trade: LONG {SYM_A} & SHORT {SYM_B}")
                        
                        qty_A = (MARGIN_PER_LEG_USDT * LEVERAGE) / price_A
                        qty_B = (MARGIN_PER_LEG_USDT * LEVERAGE) / price_B
                        
                        try:
                            # Esecuzione
                            bitget.create_market_buy_order(SYM_A, float(bitget.amount_to_precision(SYM_A, qty_A)))
                            bitget.create_market_sell_order(SYM_B, float(bitget.amount_to_precision(SYM_B, qty_B)))
                            
                            position_open = True
                            trade_side_A = 'long'
                            logging.info("✅ Trade di Cointegrazione APERTO con successo a Rischio Zero.")
                            
                            # Notifica Telegram
                            try:
                                import requests
                                load_dotenv('/home/sergio/denaro/.env.telegram')
                                tk = os.getenv('TELEGRAM_BOT_TOKEN')
                                cid = os.getenv('TELEGRAM_CHAT_ID')
                                msg = f"⚖️ *STATISTICAL ARBITRAGE (Pairs Trader)* ⚖️\n\nHo rilevato una divergenza matematica estrema (Z-Score: {z_score:.2f}) tra Bitcoin ed Ethereum.\nL'elastico si è spezzato.\n\n*Azione Simultanea:* LONG {SYM_A} 🟢 + SHORT {SYM_B} 🔴 (Leva {LEVERAGE}x)\n*Rischio Mercato:* ZERO ASSOLUTO (Market Neutral).\n\nAttendo il ritorno alla media (Snapback) per chiudere in profitto. 🕸️"
                                requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", data={"chat_id": cid, "text": msg, "parse_mode": "Markdown"})
                            except: pass
                            
                        except Exception as e_trade:
                            logging.error(f"Errore apertura Pairs Trade: {e_trade}")

                # --- LOGICA DI USCITA ---
                else:
                    # Abbiamo una posizione aperta. Aspettiamo che lo Z-Score torni verso lo zero (Mean Reversion)
                    if trade_side_A == 'short' and z_score <= Z_SCORE_EXIT:
                        logging.info(f"🎯 [RITORNO ALLA MEDIA] Z-Score {z_score:.2f} <= {Z_SCORE_EXIT}. Chiusura Profitto!")
                        try:
                            # Chiudi Posizioni
                            pos = bitget.fetch_positions([SYM_A, SYM_B])
                            for p in pos:
                                if float(p['contracts']) > 0:
                                    sym = p['symbol']
                                    c_side = p['side']
                                    if c_side == 'long':
                                        bitget.create_market_sell_order(sym, float(p['contracts']), params={'reduceOnly': True})
                                    else:
                                        bitget.create_market_buy_order(sym, float(p['contracts']), params={'reduceOnly': True})
                            
                            position_open = False
                            trade_side_A = None
                            logging.info("✅ Trade Chiuso. Profitto (Spread) Incassato.")
                        except Exception as e_close:
                            logging.error(f"Errore chiusura posizioni: {e_close}")
                            
                    elif trade_side_A == 'long' and z_score >= -Z_SCORE_EXIT:
                        logging.info(f"🎯 [RITORNO ALLA MEDIA] Z-Score {z_score:.2f} >= {-Z_SCORE_EXIT}. Chiusura Profitto!")
                        try:
                            # Chiudi Posizioni
                            pos = bitget.fetch_positions([SYM_A, SYM_B])
                            for p in pos:
                                if float(p['contracts']) > 0:
                                    sym = p['symbol']
                                    c_side = p['side']
                                    if c_side == 'long':
                                        bitget.create_market_sell_order(sym, float(p['contracts']), params={'reduceOnly': True})
                                    else:
                                        bitget.create_market_buy_order(sym, float(p['contracts']), params={'reduceOnly': True})
                            
                            position_open = False
                            trade_side_A = None
                            logging.info("✅ Trade Chiuso. Profitto (Spread) Incassato.")
                        except Exception as e_close:
                            logging.error(f"Errore chiusura posizioni: {e_close}")

            time.sleep(5)
            
        except Exception as e:
            logging.error(f"Errore Loop: {e}")
            time.sleep(5)

if __name__ == '__main__':
    run_pairs_trading()
