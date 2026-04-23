import gc
import gc
import gc
import ccxt
import os
import time
import logging
import json
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [DELTA 🌊] - %(message)s',
                    handlers=[logging.FileHandler("SQUADRA_DELTA.log"), logging.StreamHandler()])
logger = logging.getLogger("SquadraDelta")

load_dotenv('/home/sergio/denaro/.env')
# Usiamo CCXT per Binance per comodità e velocità asincrona
binance = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_API_SECRET'),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

SYMBOLS = ['BTC/EUR', 'ETH/EUR', 'SOL/EUR', 'DOGE/EUR', 'XRP/EUR']
TRADE_EUR = 11.0
IMBALANCE_RATIO = 3.5  # Bids devono essere 3.5x gli Asks nei primi 10 livelli
TAKE_PROFIT = 1.002    # +0.2%
STOP_LOSS = 0.995      # -0.5% (Se il muro sparisce, tagliamo le perdite)

VAULT_FILE = "/home/sergio/.openclaw/workspace/denaro/vault.json"

def get_vault_locked():
    try:
        with open(VAULT_FILE, 'r') as f:
            return float(json.load(f).get("LOCKED_EUR", 0.0))
    except: return 0.0

def run_delta():
    logger.info("🌊 SQUADRA DELTA (Order Flow Frontrunner) ONLINE - Analisi Level 2 in corso")
    
    active_trade = None

    import gc
    while True:
        gc.collect()
        try:
            # Controllo fondi
            bal = binance.fetch_balance()
            free_eur = float(bal.get('EUR', {}).get('free', 0.0))
            usable_eur = free_eur - get_vault_locked()

            if active_trade:
                # Gestione Trade Aperto
                sym = active_trade['symbol']
                entry = active_trade['entry']
                qty = active_trade['qty']
                
                ticker = binance.fetch_ticker(sym)
                current_price = float(ticker['last'])
                
                if current_price >= entry * TAKE_PROFIT:
                    logger.info(f"💰 [TAKE PROFIT] Muro sfruttato con successo su {sym}! Venduto a {current_price}€")
                    try:
                        binance.create_market_sell_order(sym, qty)
                        profit = (current_price - entry) * qty
                        elemosina = profit * 0.33
                        
                        # Aggiorna Vault
                        try:
                            with open(VAULT_FILE, 'r') as f: v_data = json.load(f)
                            v_data['LOCKED_EUR'] = v_data.get('LOCKED_EUR', 0.0) + elemosina
                            with open(VAULT_FILE, 'w') as f: json.dump(v_data, f)
                            logger.info(f"🔐 Aggiunti {elemosina:.4f}€ al Vault.")
                        except: pass
                        active_trade = None
                        time.sleep(60) # Pausa post-trade
                    except Exception as e:
                        logger.error(f"Errore TP: {e}")
                        
                elif current_price <= entry * STOP_LOSS:
                    logger.warning(f"🛑 [STOP LOSS] Il Muro su {sym} è crollato (Fake Wall). Vendita d'emergenza a {current_price}€")
                    try:
                        binance.create_market_sell_order(sym, qty)
                        active_trade = None
                        time.sleep(300) # Pausa punitiva
                    except Exception as e:
                        logger.error(f"Errore SL: {e}")

            else:
                # Ricerca Imbalance
                if usable_eur < TRADE_EUR:
                    logger.debug("Fondi insufficienti o bloccati nel Vault. Pausa.")
                    time.sleep(30)
                    continue

                best_sym = None
                best_ratio = 0.0
                
                for sym in SYMBOLS:
                    try:
                        ob = binance.fetch_order_book(sym, limit=10)
                        bids = ob['bids']
                        asks = ob['asks']
                        
                        if not bids or not asks: continue
                        
                        # Calcola volume totale nei primi 10 livelli
                        total_bid_vol = sum([b[0] * b[1] for b in bids]) # Prezzo * Qty
                        total_ask_vol = sum([a[0] * a[1] for a in asks])
                        
                        if total_ask_vol > 0:
                            ratio = total_bid_vol / total_ask_vol
                            if ratio > best_ratio:
                                best_ratio = ratio
                                best_sym = sym
                    except: pass
                
                if best_sym and best_ratio >= IMBALANCE_RATIO:
                    logger.info(f"🐋 WHALE ALERT SU {best_sym}! Muro in Acquisto rilevato. Rapporto Bids/Asks: {best_ratio:.1f}x")
                    try:
                        price = binance.fetch_ticker(best_sym)['last']
                        
                        # Calcola quantità esatta
                        binance.load_markets()
                        qty = float(binance.amount_to_precision(best_sym, TRADE_EUR / price))
                        
                        binance.create_market_buy_order(best_sym, qty)
                        logger.info(f"🚀 ENTRATA TATTICA (Front-Run) su {best_sym}: Comprati {qty} a {price}€")
                        active_trade = {'symbol': best_sym, 'entry': price, 'qty': qty}
                    except Exception as e:
                        logger.error(f"Errore entrata Front-Run: {e}")
                        
            time.sleep(5) # Ciclo veloce per Order Flow

        except Exception as e:
            logger.error(f"Errore ciclo Delta: {e}")
            time.sleep(15)

if __name__ == '__main__':
    run_delta()
