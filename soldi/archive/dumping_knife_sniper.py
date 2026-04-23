import ccxt
import time
import os
import logging
import sys
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [KNIFE SNIPER 🔪] - %(message)s',
                    handlers=[logging.FileHandler("DUMPING_KNIFE.log"), logging.StreamHandler()])

sys.path.insert(0, '/home/sergio/.openclaw/workspace/denaro')
import local_price

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env.bitget')

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

def run_knife_sniper():
    SYMBOL = 'SOL/USDT:USDT'
    MARGIN_USDT = 10.0   # Solo 10 USDT di rischio (Il Colpo Grosso)
    LEVERAGE = 20        # Leva 20x (Esposizione 200 USDT)
    
    # Parametri del crollo (Flash Crash)
    CRASH_THRESHOLD_PERCENT = -2.5  # Se crolla di > 2.5% in pochi minuti
    REBOUND_TARGET_PERCENT = 1.5    # Vogliamo rubare un rimbalzo del +1.5% (+30% di ROE netto)
    STOP_LOSS_PERCENT = -1.0        # Se sbaglia e continua a crollare perdiamo l'1% (Liquidazione o -20% di ROE)
    
    try:
        bitget.set_leverage(LEVERAGE, SYMBOL)
    except: pass

    logging.info(f"🔪 DUMPING KNIFE SNIPER ARMATA SU {SYMBOL}.")
    logging.info(f"Rischio: {MARGIN_USDT} USDT | Leva: {LEVERAGE}x | Target Bounce: +{REBOUND_TARGET_PERCENT}%")
    
    # Raccogliamo la baseline del prezzo ogni 5 minuti per calcolare il crollo improvviso
    price_history = []
    
    while True:
        try:
            ticker = local_price.get_ticker('SOL/USDT')
            if not ticker: ticker = bitget.fetch_ticker(SYMBOL)
            
            current_price = ticker['last']
            timestamp = time.time()
            
            # Manteniamo solo gli ultimi 15 minuti di storico per il flash crash
            price_history.append({'price': current_price, 'time': timestamp})
            price_history = [p for p in price_history if timestamp - p['time'] <= 900] # 15 min = 900s
            
            if len(price_history) > 5:
                # Trova il prezzo massimo negli ultimi 15 minuti
                max_price = max(p['price'] for p in price_history)
                drop_percent = ((current_price - max_price) / max_price) * 100
                
                logging.info(f"🔪 SOL: {current_price:.2f} $ | Max 15m: {max_price:.2f} $ | Drop: {drop_percent:.2f}%")
                
                # Se il crollo supera la soglia del flash crash
                if drop_percent <= CRASH_THRESHOLD_PERCENT:
                    logging.warning(f"🚨 [FLASH CRASH RILEVATO] Solana è crollata del {drop_percent:.2f}% a {current_price} $.")
                    logging.warning("🔪 Entrata LONG Kamikaze sul sangue! (Catching the falling knife)")
                    
                    try:
                        # Calcolo Size
                        qty = (MARGIN_USDT * LEVERAGE) / current_price
                        qty_str = bitget.amount_to_precision(SYMBOL, qty)
                        
                        # Ordine Market LONG
                        order = bitget.create_market_buy_order(SYMBOL, float(qty_str))
                        logging.info(f"✅ Ordine Eseguito: {qty_str} SOL a ~{current_price} USDT")
                        
                        # Piazziamo istantaneamente Take Profit e Stop Loss
                        entry_price = current_price # Approximation
                        tp_price = entry_price * (1 + (REBOUND_TARGET_PERCENT / 100))
                        sl_price = entry_price * (1 + (STOP_LOSS_PERCENT / 100))
                        
                        try:
                            # Take Profit
                            bitget.create_order(SYMBOL, 'limit', 'sell', float(qty_str), float(bitget.price_to_precision(SYMBOL, tp_price)), params={'reduceOnly': True})
                            # Stop Loss
                            bitget.create_order(SYMBOL, 'stop_market', 'sell', float(qty_str), params={'stopPrice': float(bitget.price_to_precision(SYMBOL, sl_price)), 'reduceOnly': True})
                        except Exception as o_err:
                            logging.error(f"Errore impostazione SL/TP: {o_err}")
                            
                        # Manda notifica Telegram
                        try:
                            import requests
                            load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env.telegram')
                            tk = os.getenv('TELEGRAM_BOT_TOKEN')
                            cid = os.getenv('TELEGRAM_CHAT_ID')
                            msg = f"🔪 *DUMPING KNIFE SNIPER* 🔪\n\nHo intercettato un **Flash Crash del {drop_percent:.2f}%** su Solana.\nHo appena afferrato il coltello che cade.\n\n*Direzione:* LONG 🟢 (Leva {LEVERAGE}x)\n*Rischio:* {MARGIN_USDT} USDT\n*Prezzo Entrata:* ~{entry_price} $\n*Target Rimbalzo:* {tp_price:.2f} $\n\nOra aspettiamo il Rimbalzo del Gatto Morto. 🐈💀"
                            requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", data={"chat_id": cid, "text": msg, "parse_mode": "Markdown"})
                        except: pass
                        
                        # Mettiamo il bot in pausa profonda per evitare di comprare multipli coltelli
                        logging.info("Sospensione per 2 ore in attesa che l'operazione si chiuda (TP o SL).")
                        price_history.clear()
                        time.sleep(7200)
                        
                    except Exception as e_buy:
                        logging.error(f"Errore acquisto: {e_buy}")
                        time.sleep(60) # Riproviamo dopo 1 minuto
                        
            time.sleep(15) # Lettura rapida ogni 15 secondi
            
        except Exception as e:
            logging.error(f"Errore Loop: {e}")
            time.sleep(15)

if __name__ == '__main__':
    run_knife_sniper()
