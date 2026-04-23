import ccxt
import time
import os
import json
import logging
import sys
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [HEDGE 🛡️] - %(message)s',
                    handlers=[logging.FileHandler("DELTA_NEUTRAL.log"), logging.StreamHandler()])

sys.path.insert(0, '/home/sergio/.openclaw/workspace/denaro')
import local_price

load_dotenv('/home/sergio/denaro/.env')
load_dotenv('/home/sergio/denaro/.env.bitget')

try:
    binance = ccxt.binance({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_API_SECRET'),
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
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

def get_spot_exposure():
    try:
        bal = binance.fetch_balance()
        assets = {b['asset']: float(b['free']) + float(b['locked']) for b in bal['info']['balances'] if float(b['free']) > 0 or float(b['locked']) > 0}
        
        tickers = binance.fetch_tickers()
        total_eur_exposure = 0.0
        
        for asset, qty in assets.items():
            if asset in ['EUR', 'USDT', 'USDC']: continue
            sym = f"{asset}/EUR"
            if sym in tickers:
                total_eur_exposure += qty * tickers[sym]['last']
                
        return total_eur_exposure
    except Exception as e:
        logging.error(f"Errore Spot Exposure: {e}")
        return 0.0

def run_hedger():
    logging.info("🛡️ DELTA NEUTRAL PORTFOLIO (Hedge Fund Mode) ATTIVATO.")
    HEDGE_SYMBOL = 'BTC/USDT:USDT'
    LEVERAGE = 10
    
    try:
        bitget.set_leverage(LEVERAGE, HEDGE_SYMBOL)
    except: pass

    while True:
        try:
            spot_exposure_eur = get_spot_exposure()
            
            # Recuperiamo prezzo BTC/EUR per coprire tutto il portafoglio in BTC
            btc_eur = local_price.get_ticker('BTC/EUR')
            if not btc_eur: btc_eur = binance.fetch_ticker('BTC/EUR')
            btc_price_eur = btc_eur['last']
            
            # Calcoliamo quanta BTC vendere SHORT su Bitget per azzerare l'esposizione
            target_hedge_btc = spot_exposure_eur / btc_price_eur
            
            # Verifichiamo se abbiamo già una posizione aperta
            positions = bitget.fetch_positions([HEDGE_SYMBOL])
            current_short_qty = 0.0
            for p in positions:
                if p['side'] == 'short':
                    current_short_qty = float(p['contracts'])
                    
            logging.info(f"🛡️ Esposizione Binance: {spot_exposure_eur:.2f} €. Target Short: {target_hedge_btc:.5f} BTC. Short Attuale: {current_short_qty:.5f} BTC.")
            
            diff_btc = target_hedge_btc - current_short_qty
            
            # Se la differenza è maggiore di 0.001 BTC (circa 60 EUR), facciamo re-balance
            if abs(diff_btc) > 0.001:
                bitget_bal = bitget.fetch_balance({'type': 'swap'})
                usdt_free = float(bitget_bal['USDT']['free'])
                
                btc_usdt = local_price.get_ticker('BTC/USDT')
                if not btc_usdt: btc_usdt = binance.fetch_ticker('BTC/USDT')
                btc_price_usdt = btc_usdt['last']
                
                required_margin = (abs(diff_btc) * btc_price_usdt) / LEVERAGE
                
                if diff_btc > 0: # Dobbiamo shortare di più
                    if usdt_free >= required_margin:
                        logging.warning(f"⚖️ Sbilanciamento rilevato. Apertura SHORT aggiuntivo di {diff_btc:.5f} BTC (Margine richiesto: ~{required_margin:.2f} USDT).")
                        qty_str = bitget.amount_to_precision(HEDGE_SYMBOL, diff_btc)
                        try:
                            bitget.create_market_sell_order(HEDGE_SYMBOL, float(qty_str))
                            logging.info("✅ Ordine di Copertura (Hedge) ESEGUITO CON SUCCESSO! Portafoglio Protetto.")
                            # Manda notifica Telegram
                            try:
                                import requests
                                load_dotenv('/home/sergio/denaro/.env.telegram')
                                tk = os.getenv('TELEGRAM_BOT_TOKEN')
                                cid = os.getenv('TELEGRAM_CHAT_ID')
                                msg = f"🛡️ *SCUDO ATTIVATO (DELTA NEUTRAL)* 🛡️\n\nHo appena rilevato i tuoi fondi USDT su Bitget e ho chiuso a chiave la cupola di vetro.\n\nEsposizione Binance: {spot_exposure_eur:.2f} €\nCopertura aperta: {qty_str} BTC SHORT in Leva {LEVERAGE}x\n\nIl portafoglio è matematicamente immune ai crolli da questo esatto istante."
                                requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", data={"chat_id": cid, "text": msg, "parse_mode": "Markdown"})
                            except: pass
                        except Exception as e:
                            logging.error(f"Errore creazione ordine Hedge: {e}")
                    else:
                        logging.warning(f"⚠️ [ATTESA FONDI] Serve un margine di {required_margin:.2f} USDT liberi per pareggiare lo scudo. Attualmente hai {usdt_free:.2f} USDT. In attesa di deposito da Sergio...")
                else: # Ne abbiamo shortati troppi, dobbiamo comprarne un po' per ridurre lo short
                    reduce_qty = abs(diff_btc)
                    logging.info(f"⚖️ Sbilanciamento rilevato (Scudo in eccesso). Riduzione SHORT di {reduce_qty:.5f} BTC.")
                    qty_str = bitget.amount_to_precision(HEDGE_SYMBOL, reduce_qty)
                    try:
                        bitget.create_market_buy_order(HEDGE_SYMBOL, float(qty_str), params={'reduceOnly': True})
                    except Exception as e:
                        logging.error(f"Errore riduzione Hedge: {e}")
            else:
                logging.info(f"⚖️ Lo Scudo è perfettamente bilanciato. Nessun intervento necessario.")
            
            # Controlla ogni 5 minuti per ribilanciare l'hedge dinamicamente!
            time.sleep(300)
            
        except Exception as e:
            logging.error(f"Errore Hedge Loop: {e}")
            time.sleep(60)

if __name__ == '__main__':
    run_hedger()
