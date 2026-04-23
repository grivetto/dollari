import ccxt
import time
import os
import sys
import logging
from collections import deque
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ALPHA STRIKE ⚡] - %(message)s',
                    handlers=[logging.FileHandler("ALPHA_STRIKE.log"), logging.StreamHandler()])

sys.path.insert(0, '/home/sergio/.openclaw/workspace/denaro')
import local_price

load_dotenv('/home/sergio/denaro/.env')

try:
    binance = ccxt.binance({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_API_SECRET'),
        'enableRateLimit': True
    })
    binance.load_markets()
except Exception as e:
    logging.error(f"Errore connessione Binance: {e}")
    exit()

# Target Coins for HFT Scalping
PAIRS = [
    {'sym': 'BTC/EUR', 'size_eur': 10},
    {'sym': 'SOL/EUR', 'size_eur': 10},
    {'sym': 'DOGE/EUR', 'size_eur': 10},
    {'sym': 'AVAX/EUR', 'size_eur': 10}
]

PROFIT_TARGET = 1.0015  # +0.15% a trade
STOP_LOSS = 0.995       # -0.50% a trade
SPREAD_MAX = 0.002      # Evitare di comprare se lo spread è maggiore dello 0.2%

# Storico prezzi per EMA super veloci (10 sec vs 60 sec)
history = {p['sym']: deque(maxlen=60) for p in PAIRS}

def calculate_ema(prices, length):
    if len(prices) < length: return sum(prices) / len(prices) if prices else 0
    ema = prices[0]
    multiplier = 2 / (length + 1)
    for price in list(prices)[1:length]:
        ema = (price - ema) * multiplier + ema
    return ema

def run_alpha_strike():
    logging.info("⚡ ALPHA STRIKE SCALPER (HFT) INIZIALIZZATO.")
    logging.info("Lettura prezzi a <5ms via RAM-Disk. Ricerca micro-esplosioni EMA...")
    
    # Track posizioni aperte dal bot (per non comprarne troppe)
    active_trades = {}
    
    while True:
        try:
            for pair in PAIRS:
                sym = pair['sym']
                base_coin = sym.split('/')[0]
                
                # Legge il prezzo dalla RAM (0 latenza)
                ticker = local_price.get_ticker(sym.replace('/', ''))
                if not ticker: continue
                
                current_price = ticker['last']
                if not current_price: continue
                
                # Salva nello storico
                history[sym].append(current_price)
                
                # Se abbiamo un trade attivo, gestiamo il TP / SL
                if sym in active_trades:
                    trade = active_trades[sym]
                    entry = trade['entry']
                    qty = trade['qty']
                    
                    if current_price >= entry * PROFIT_TARGET:
                        logging.info(f"✅ [TAKE PROFIT] {sym} venduto a {current_price:.4f} (+{(current_price/entry - 1)*100:.2f}%)")
                        try:
                            binance.create_market_sell_order(sym, qty)
                            del active_trades[sym]
                        except Exception as e:
                            logging.error(f"Errore Vendita TP {sym}: {e}")
                    
                    elif current_price <= entry * STOP_LOSS:
                        logging.warning(f"❌ [STOP LOSS] {sym} venduto a {current_price:.4f} (-{(1 - current_price/entry)*100:.2f}%)")
                        try:
                            binance.create_market_sell_order(sym, qty)
                            del active_trades[sym]
                        except Exception as e:
                            logging.error(f"Errore Vendita SL {sym}: {e}")
                            
                    continue # Se c'è un trade attivo per questa moneta, non ne apre altri.
                
                # Se NON abbiamo un trade, calcoliamo le EMA
                if len(history[sym]) >= 15: # Bastano 15 secondi per iniziare a calcolare
                    ema_fast = calculate_ema(history[sym], 5)  # 5 secondi
                    ema_slow = calculate_ema(history[sym], 15) # 15 secondi
                    
                    # Golden Cross: Fast taglia la Slow dal basso verso l'alto con slancio (+0.05%)
                    if ema_fast > ema_slow * 1.0005 and history[sym][-2] < ema_slow:
                        logging.info(f"🚀 [GOLDEN CROSS MICRO] {sym} esplosione rilevata (Fast: {ema_fast:.4f}, Slow: {ema_slow:.4f})")
                        
                        qty = pair['size_eur'] / current_price
                        qty_str = binance.amount_to_precision(sym, qty)
                        
                        if float(qty_str) > 0:
                            try:
                                bal = binance.fetch_balance()
                                if float(bal.get('EUR', {}).get('free', 0.0)) < pair['size_eur']:
                                    logging.warning('Fondi EUR insufficienti. Salto acquisto.')
                                    continue
                            except: pass
                            logging.info(f"⚡ COMPRO {qty_str} {base_coin} a {current_price} EUR.")
                            try:
                                binance.create_market_buy_order(sym, float(qty_str))
                                active_trades[sym] = {'entry': current_price, 'qty': float(qty_str)}
                            except Exception as e_buy:
                                logging.error(f"Impossibile comprare {sym} (Fondi o limiti?): {e_buy}")
                                
            # Il bot riposa solo 1 secondo. Vero HFT.
            time.sleep(1)
            # Heartbeat per Zabbix
            if int(time.time()) % 60 == 0:
                logging.info('💗 Heartbeat OK.')
            
        except Exception as e:
            logging.error(f"Errore Loop: {e}")
            time.sleep(5)

if __name__ == '__main__':
    run_alpha_strike()
