import gc
import os, time, logging, gc, json
from collections import deque
from dotenv import load_dotenv
from binance.client import Client
from binance import ThreadedWebsocketManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/VAMPIRE.log"), logging.StreamHandler()])
logger = logging.getLogger("Vampire")

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
VAULT_FILE = "/home/sergio/.openclaw/workspace/denaro/vault.json"

# Il Vampiro succhia liquidità continua lateralizzando sul Bitcoin
SYMBOL = "BTCEUR"
GRID_STEP_PERCENT = 0.0005 # 0.15% di distanza tra i livelli
MAX_BUDGET = 300.0  # Massima esposizione totale del vampiro
TRADE_SIZE = 11.0   # 15 euro a livello

# Memoria ultraleggera: tiene traccia solo del prezzo corrente e delle "zanne" (ordini aperti fittizi)
# Fittizi per non intasare l'order book di Binance, il vampiro colpisce a mercato.

def get_vault_locked():
    try:
        if os.path.exists(VAULT_FILE):
            with open(VAULT_FILE, 'r') as f:
                return float(json.load(f).get("LOCKED_EUR", 0.0))
    except: pass
    return 0.0

def add_to_vault(amount):
    locked = get_vault_locked() + amount
    try:
        with open(VAULT_FILE, 'w') as f:
            json.dump({"LOCKED_EUR": locked}, f)
        logger.info(f"🧛 VAMPIRO HA PRESO SANGUE: {amount:.2f}€ dritti in Cassaforte! [Tot: {locked:.2f}€]")
    except: pass

def get_step_size():
    try:
        info = client.get_symbol_info(SYMBOL)
        for f in info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                return float(f['stepSize'])
    except: pass
    return 0.00001

def round_step(quantity, step_size):
    import math
    precision = int(round(-math.log10(step_size), 0))
    return round(quantity - (quantity % step_size), precision)

fangs = [] # list of dicts: {'entry': price, 'qty': amount}
last_price = 0.0

def process_socket_msg(msg):
    global last_price, fangs
    if 'data' not in msg or 'e' not in msg['data']: return
    
    event = msg['data']
    if event['e'] == 'kline':
        price = float(event['k']['c'])
        is_closed = event['k']['x']
        
        # Morde il mercato in chiusura di candela se scende abbastanza
        if is_closed:
            if not fangs:
                # Primo morso
                last_price = price
                execute_bite(price)
            else:
                # Se è sceso del GRID_STEP rispetto all'ultimo morso (o all'entry più basso)
                lowest_entry = min([f['entry'] for f in fangs])
                if price <= lowest_entry * (1 - GRID_STEP_PERCENT):
                    # Controllo budget
                    if len(fangs) * TRADE_SIZE < MAX_BUDGET:
                        execute_bite(price)
                        
        # Ad ogni tick, controlla se una zanna è in profitto per "succhiare" (vendere)
        for fang in list(fangs):
            if price >= fang['entry'] * (1 + GRID_STEP_PERCENT):
                try:
                    order = client.create_order(symbol=SYMBOL, side='SELL', type='MARKET', quantity=fang['qty'])
                    executed_qty = sum([float(f['qty']) for f in order['fills']])
                    avg_price = sum([float(f['price']) * float(f['qty']) for f in order['fills']]) / executed_qty if executed_qty > 0 else price
                    
                    real_pnl = (avg_price - fang['entry']) * executed_qty
                    if real_pnl > 0:
                        add_to_vault(real_pnl * 0.33) # 33% in cassaforte, il resto nel compound
                        logger.info(f"🧛 MORSO DRENATO! +{real_pnl:.2f}€ (Target Raggiunto da {fang['entry']})")
                    
                    fangs.remove(fang)
                except Exception as e:
                    pass

def execute_bite(price):
    global fangs
    try:
        available_eur = float(client.get_asset_balance(asset='EUR')['free'])
        if available_eur < TRADE_SIZE + get_vault_locked():
            return
            
        step = get_step_size()
        qty = round_step(TRADE_SIZE / price, step)
        
        if qty > 0:
            order = client.create_order(symbol=SYMBOL, side='BUY', type='MARKET', quantity=qty)
            executed_qty = sum([float(f['qty']) for f in order['fills']])
            avg_price = sum([float(f['price']) * float(f['qty']) for f in order['fills']]) / executed_qty if executed_qty > 0 else price
            
            fangs.append({'entry': avg_price, 'qty': executed_qty})
            logger.info(f"🧛 VAMPIRO HA MORSO {SYMBOL}: {executed_qty} @ {avg_price}€")
    except Exception as e:
        pass

def main():
    logger.info("🧛 VAMPIRE GRID AVVIATO. Succhierà volatilità laterale dal Bitcoin a costo RAM zero.")
    
    # Recupera fangs dal saldo BTC per non ripartire da zero
    try:
        btc_qty = float(client.get_asset_balance(asset='BTC')['free'])
        ticker = client.get_symbol_ticker(symbol=SYMBOL)
        price = float(ticker['price'])
        # Se ha più di 10 euro in BTC
        if btc_qty * price > 10.0:
            # Suddivide il bag in "zanne" da 15 euro fittizie a prezzo di mercato attuale per gestirle
            num_fangs = int((btc_qty * price) / TRADE_SIZE)
            if num_fangs > 0:
                qty_per_fang = btc_qty / num_fangs
                for _ in range(num_fangs):
                    fangs.append({'entry': price, 'qty': round_step(qty_per_fang, get_step_size())})
                logger.info(f"🔄 Recuperate {num_fangs} zanne dal saldo BTC esistente.")
    except: pass
    
    twm = ThreadedWebsocketManager(api_key=os.getenv('BINANCE_API_KEY'), api_secret=os.getenv('BINANCE_API_SECRET'))
    twm.start()
    
    twm.start_multiplex_socket(callback=process_socket_msg, streams=[f"btceur@kline_1m"])
    
    try:
        while True:
            time.sleep(60)
            logger.info("💗 Heartbeat OK.")
            gc.collect()
    except KeyboardInterrupt:
        twm.stop()

if __name__ == "__main__":
    main()
