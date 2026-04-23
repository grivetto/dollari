import gc
import os, time, logging, gc, json
from dotenv import load_dotenv
from binance.client import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/GARIBAN.log"), logging.StreamHandler()])
logger = logging.getLogger("Gariban")

load_dotenv('/home/sergio/denaro/.env')
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
client = Client(API_KEY, API_SECRET)

VAULT_FILE = "/home/sergio/.openclaw/workspace/denaro/vault.json"

def get_vault_locked():
    try:
        if os.path.exists(VAULT_FILE):
            with open(VAULT_FILE, 'r') as f:
                return float(json.load(f).get("LOCKED_EUR", 0.0))
    except Exception: pass
    return 0.0

def add_to_vault(amount):
    try:
        data = {}
        with open(VAULT_FILE, 'r') as f:
            data = json.load(f)
            
        locked = data.get("LOCKED_EUR", 0.0) + amount
        gariban_tracker = data.get("GARIBAN_TRACKER", 0.0) + amount
        
        data["LOCKED_EUR"] = locked
        data["GARIBAN_TRACKER"] = gariban_tracker
        
        with open(VAULT_FILE, 'w') as f:
            json.dump(data, f)
        logger.info(f"🤲 ELEMOSINA ACQUISITA! {amount:.2f}€ portati in Cassaforte! [Tot. Sicurezza: {locked:.2f}€ | Di cui Elemosina: {gariban_tracker:.2f}€]")
    except Exception as e:
        logger.error(f"Errore vault gariban: {e}")

def round_down_step(quantity, step_size):
    import math
    precision = int(round(-math.log10(step_size), 0))
    return round(quantity - (quantity % step_size), precision)

def get_step_size(symbol):
    try:
        info = client.get_symbol_info(symbol)
        for f in info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                return float(f['stepSize'])
    except: pass
    return 1.0

# Ampliamo le monete "povere" (meme coins, monetine ultra-volatili)
SYMBOLS = ["SHIBEUR", "DOGEEUR", "PEPEEUR"]

def recover_gariban_positions():
    positions = {}
    for sym in SYMBOLS:
        asset = sym.replace('EUR', '')
        try:
            qty = float(client.get_asset_balance(asset=asset)['free'])
            ticker = client.get_symbol_ticker(symbol=sym)
            price = float(ticker['price'])
            if qty * price > 2.0:
                positions[sym] = {'entry': price, 'qty': qty}
                logger.info(f"🔄 Spiccioli recuperati dal saldo: {sym} (Qty: {qty}, Val: ~{qty*price:.2f}€)")
        except Exception: pass
    return positions

def get_price_history(symbol):
    try:
        # Prende le ultime 5 candeline da 1 minuto per vedere se c'è un crollo rapido (la trappola)
        klines = client.get_klines(symbol=symbol, interval='1m', limit=5)
        prices = [float(k[4]) for k in klines]
        return prices
    except:
        return []

def main():
    logger.info("🕸️ ALGORITMO GARIBAN (MOD. TRAPPOLE) AVVIATO. Cerca spazzatura (drop improvvisi) e cede al +0.10%.")
    positions = recover_gariban_positions()
    
    while True:
        try:
            for symbol in SYMBOLS:
                # Recupera l'ultimo prezzo
                ticker = client.get_symbol_ticker(symbol=symbol)
                price = float(ticker['price'])
                
                # 1. CERCA LE TRAPPOLE (Drop Improvvisi)
                if symbol not in positions:
                    prices = get_price_history(symbol)
                    if len(prices) >= 5:
                        max_recent = max(prices)
                        drop = (price - max_recent) / max_recent
                        
                        # TRAPPOLA: Se negli ultimi 5 minuti la moneta è crollata di oltre l'1% di colpo (spike rosso),
                        # qualcuno l'ha buttata per strada, il Gariban la raccoglie.
                        if drop < -0.01:
                            try:
                                trade_amount = 10.0 # Usa ancora meno budget (10 euro a colpo per minimizzare i rischi)
                                step = get_step_size(symbol)
                                qty = round_down_step(trade_amount / price, step)
                                
                                # Verifica disponibilità base
                                available_eur = float(client.get_asset_balance(asset='EUR')['free'])
                                if available_eur < trade_amount + get_vault_locked():
                                    continue
                                    
                                if qty > 0:
                                    order = client.create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
                                    executed_qty = sum([float(f['qty']) for f in order['fills']])
                                    avg_price = sum([float(f['price']) * float(f['qty']) for f in order['fills']]) / executed_qty if executed_qty > 0 else price
                                    
                                    positions[symbol] = {'entry': avg_price, 'qty': executed_qty}
                                    logger.info(f"🕸️ TRAPPOLA SCATTATA! Il Gariban ha raccolto {executed_qty} {symbol} a {avg_price} dopo un crollo del {drop:.2%}.")
                            except Exception as e:
                                pass
                        
                # 2. SVUOTA LA TASCA (Micro-vendite veloci)
                elif symbol in positions:
                    entry = positions[symbol]['entry']
                    qty = positions[symbol]['qty']
                    
                    pnl = (price - entry) / entry
                    
                    # Elemosina estrema: Appena vede uno 0.10% (micro rimbalzo post-trappola), vende subito.
                    if pnl >= 0.0010 or pnl <= -0.02: # Se invece perde più del 2% post-trappola, molla per paura.
                        try:
                            asset = symbol.replace('EUR', '')
                            actual_qty = float(client.get_asset_balance(asset=asset)['free'])
                            step = get_step_size(symbol)
                            sell_qty = round_down_step(actual_qty, step)
                            
                            order = client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=sell_qty)
                            executed_qty = sum([float(f['qty']) for f in order['fills']])
                            avg_price = sum([float(f['price']) * float(f['qty']) for f in order['fills']]) / executed_qty if executed_qty > 0 else price
                            
                            real_pnl = (avg_price - entry) * executed_qty
                            
                            if real_pnl > 0:
                                add_to_vault(real_pnl)
                            else:
                                logger.info(f"💨 Gariban si è spaventato su {symbol}. Briciole perse: {real_pnl:.2f}€")
                                
                            del positions[symbol]
                        except Exception as e:
                            pass
                            
            time.sleep(20) # Aumentata la frequenza a 20s per cercare le trappole più in fretta
            logger.info("💗 Heartbeat OK. Memoria pulita.")
            gc.collect()
            
        except Exception as e:
            logger.error(f"Errore loop principale: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
