import ccxt
import time
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [FUNDING ARBITRAGE 🏦] - %(message)s',
                    handlers=[logging.FileHandler("FUNDING_ARBITRAGE.log"), logging.StreamHandler()])

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
    logging.error(f"Errore connessione Bitget: {e}")
    exit()

def run_funding_arbitrage():
    MARGIN_USDT = 10.0
    LEVERAGE = 20
    
    logging.info("🏦 FUNDING ARBITRAGE ESTREMO ATTIVATO.")
    logging.info(f"Ricerca del Tasso di Interesse più alto sul mercato (Shorting the Pump). Rischio: {MARGIN_USDT} USDT.")
    
    while True:
        try:
            # 1. Recupera tutti i funding rates da Bitget
            funding_rates = bitget.fetch_funding_rates()
            
            highest_rate = 0.0
            target_symbol = None
            
            for symbol, data in funding_rates.items():
                # Filtra solo i contratti in USDT e ignora BTC/ETH per cercare le memecoin
                if symbol.endswith(':USDT') and symbol not in ['BTC/USDT:USDT', 'ETH/USDT:USDT']:
                    rate = float(data['fundingRate'])
                    if rate > highest_rate:
                        highest_rate = rate
                        target_symbol = symbol
                        
            # Se troviamo una coin con un tasso > 0.05% ogni 8 ore (che è altissimo)
            # o se vogliamo solo prendere la più alta in assoluto, mettiamo una soglia
            # Ad esempio: 0.0003 = 0.03% ogni 8h = 32% APR
            # Vogliamo una moneta speculativa
            
            if target_symbol and highest_rate > 0.0003:
                logging.info(f"🚨 Trovata anomalia sui Tassi: {target_symbol} paga il +{highest_rate * 100:.3f}% ogni 8 ore ai venditori allo scoperto!")
                
                # Controlla se abbiamo già posizioni aperte su questo simbolo
                positions = bitget.fetch_positions([target_symbol])
                has_position = any(float(p['contracts']) > 0 for p in positions)
                
                if not has_position:
                    logging.warning(f"🏦 Apro posizione SHORT speculativa su {target_symbol} per incassare gli interessi dai LONGers in leva.")
                    
                    try:
                        # Imposta Leva (ignora errori se già settata)
                        try:
                            bitget.set_leverage(LEVERAGE, target_symbol)
                        except: pass
                        
                        ticker = bitget.fetch_ticker(target_symbol)
                        current_price = ticker['last']
                        
                        qty = (MARGIN_USDT * LEVERAGE) / current_price
                        qty_str = bitget.amount_to_precision(target_symbol, qty)
                        
                        # Ordine Market SHORT
                        bitget.create_market_sell_order(target_symbol, float(qty_str))
                        logging.info(f"✅ Ordine SHORT Eseguito: {qty_str} {target_symbol} a ~{current_price} USDT")
                        
                        # Stop Loss per sicurezza: se la coin pompa del +3% ci stoppiamo (-60% ROE)
                        sl_price = current_price * 1.03
                        # Take Profit: se i longers vengono liquidati (crollo del -5%) = +100% ROE
                        tp_price = current_price * 0.95
                        
                        try:
                            # Take Profit
                            bitget.create_order(target_symbol, 'limit', 'buy', float(qty_str), float(bitget.price_to_precision(target_symbol, tp_price)), params={'reduceOnly': True})
                            # Stop Loss
                            bitget.create_order(target_symbol, 'stopMarket', 'buy', float(qty_str), float(bitget.price_to_precision(target_symbol, sl_price)), params={'reduceOnly': True})
                        except Exception as e_sl:
                            logging.error(f"Errore SL/TP su Arbitraggio: {e_sl}")
                            
                        # Manda notifica
                        try:
                            import requests
                            load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env.telegram')
                            tk = os.getenv('TELEGRAM_BOT_TOKEN')
                            cid = os.getenv('TELEGRAM_CHAT_ID')
                            msg = f"🏦 *FUNDING ARBITRAGE ESTREMO* 🏦\n\nHo scansionato i tassi d'interesse globali e ho trovato un'anomalia esplosiva su *{target_symbol.replace(':USDT', '')}*.\n\nI trader in Leva LONG sono così disperati che pagano il **+{highest_rate * 100:.3f}% ogni 8 ore** a chiunque apra uno SHORT.\n\n*Azione:* Entrata SHORT (Leva {LEVERAGE}x)\n*Rischio:* {MARGIN_USDT} USDT\n\nOra ci faremo pagare letteralmente una rendita passiva dai fanatici, e se la moneta crolla sotto il suo stesso peso... incassiamo il Take Profit del +100%. Il banco vince sempre! 🎰"
                            requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", data={"chat_id": cid, "text": msg, "parse_mode": "Markdown"})
                        except: pass
                        
                        # Pausa lunghissima perché abbiamo aperto il trade (12 ore)
                        time.sleep(43200)
                        
                    except Exception as e_sell:
                        logging.error(f"Errore apertura SHORT arbitraggio: {e_sell}")
                else:
                    logging.info(f"Abbiamo già una posizione aperta su {target_symbol}. Manteniamo la rendita passiva.")
                    time.sleep(3600) # Controlla tra un'ora
            else:
                logging.info(f"Nessuna coin in eccesso di FOMO trovata (Max rate attuale: {highest_rate*100:.3f}%). Aspetto la prossima ondata speculativa.")
            
            # Controlla i tassi ogni ora (il funding rate si aggiorna lentamente)
            time.sleep(3600)
            
        except Exception as e:
            logging.error(f"Errore Loop Arbitraggio Funding: {e}")
            time.sleep(60)

if __name__ == '__main__':
    run_funding_arbitrage()
