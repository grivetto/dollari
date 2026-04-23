import ccxt
import time
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ECHO SNIPER 🌏] - %(message)s',
                    handlers=[logging.FileHandler("SPATIAL_ARBITRAGE.log"), logging.StreamHandler()])

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env.mexc')

COINS = ['SOL', 'DOGE', 'AVAX', 'LINK', 'PEPE', 'WIF', 'NEAR', 'FET']

try:
    binance = ccxt.binance({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_API_SECRET'),
        'enableRateLimit': True
    })
    
    mexc = ccxt.mexc({
        'apiKey': os.getenv('MEXC_API_KEY'),
        'secret': os.getenv('MEXC_API_SECRET'),
        'enableRateLimit': True
    })
except Exception as e:
    logging.error(f"Errore connessione: {e}")
    exit()

def run_echo_sniper():
    logging.info("🌏 ASIAN ECHO SNIPER (Lead-Lag Arbitrage) ATTIVATO.")
    logging.info("Sto analizzando il differenziale di latenza tra MEXC (Asia) e Binance (Europa)...")
    
    ARBITRAGE_THRESHOLD = 1.015 
    TRADE_AMOUNT_EUR = 15.0  
    
    while True:
        try:
            mexc_tickers = mexc.fetch_tickers()
            binance_tickers = binance.fetch_tickers()
            
            for coin in COINS:
                sym_usdt = f"{coin}/USDT"
                if sym_usdt in mexc_tickers and sym_usdt in binance_tickers:
                    try:
                        mexc_price = float(mexc_tickers[sym_usdt]['last'])
                        bin_price = float(binance_tickers[sym_usdt]['last'])
                        
                        if bin_price == 0: continue
                        
                        spread = mexc_price / bin_price
                        
                        if spread > ARBITRAGE_THRESHOLD:
                            logging.warning(f"🚨 [ANOMALIA RILEVATA] {coin} sta pompando su MEXC ({mexc_price:.4f} vs BINANCE: {bin_price:.4f})! Spread: +{(spread-1)*100:.2f}%")
                            
                            sym_eur = f"{coin}/EUR"
                            
                            try:
                                bin_eur_ticker = binance.fetch_ticker(sym_eur)
                                current_eur_price = float(bin_eur_ticker['last'])
                                qty = TRADE_AMOUNT_EUR / current_eur_price
                                
                                logging.info(f"⚡ COMPRO {qty:.4f} {coin} su Binance a {current_eur_price:.4f} EUR per anticipare l'onda asiatica!")
                                
                                tp_price = current_eur_price * 1.02
                                
                                try:
                                    binance.create_market_buy_order(sym_eur, float(binance.amount_to_precision(sym_eur, qty)))
                                    logging.info(f"✅ Acquisto ESEGUITO. Posizionato Take Profit a {tp_price:.4f} EUR.")
                                    
                                    try:
                                        binance.create_limit_sell_order(sym_eur, float(binance.amount_to_precision(sym_eur, qty)), float(binance.price_to_precision(sym_eur, tp_price)))
                                    except Exception as e2:
                                        logging.error(f"Errore Take Profit: {e2}")
                                        
                                    try:
                                        import requests
                                        tk = os.getenv('TELEGRAM_BOT_TOKEN')
                                        cid = os.getenv('TELEGRAM_CHAT_ID')
                                        msg = f"🌏 *ASIAN ECHO SNIPER* 🌏\n\nHo rilevato un'esplosione di volumi su MEXC (+{(spread-1)*100:.2f}%) su *{coin}*.\n\nHo anticipato l'onda comprando su Binance Europa per {TRADE_AMOUNT_EUR}€.\nTake profit automatico impostato a +2%. Sfruttiamo il fuso orario! ⚡"
                                        requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", data={"chat_id": cid, "text": msg, "parse_mode": "Markdown"})
                                    except: pass
                                    
                                    time.sleep(300)
                                    
                                except Exception as e_buy:
                                    logging.error(f"Impossibile comprare: {e_buy}")
                                    
                            except Exception as e_eur:
                                pass
                    except: pass
                            
            time.sleep(10)
            
        except Exception as e:
            logging.error(f"Errore Loop: {e}")
            time.sleep(10)

if __name__ == '__main__':
    run_echo_sniper()
