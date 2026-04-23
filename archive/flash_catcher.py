import gc
import os, time, logging, gc, json, math
from dotenv import load_dotenv
from binance.client import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/FLASH_CATCHER.log"), logging.StreamHandler()])
logger = logging.getLogger("FlashCatcher")

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

VAULT_FILE = "/home/sergio/.openclaw/workspace/denaro/vault.json"

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
        logger.info(f"⚖️ FLASH CATCHER HA VERSATO: +{amount:.2f}€ IN CASSAFORTE!")
    except: pass

# SIMBOLI AD ALTA VOLATILITA' / FLASH CRASH
SYMBOLS = ["SOLEUR", "ADAEUR", "DOGEEUR", "LINKEUR"]
TRADE_EUR_AMOUNT = 15.0

def round_step(quantity, step_size):
    precision = int(round(-math.log10(step_size), 0))
    return round(quantity - (quantity % step_size), precision)

def round_price(price, tick_size):
    precision = int(round(-math.log10(tick_size), 0))
    return round(price - (price % tick_size), precision)

def get_filters(symbol):
    try:
        info = client.get_symbol_info(symbol)
        step = 1.0
        tick = 0.01
        for f in info['filters']:
            if f['filterType'] == 'LOT_SIZE': step = float(f['stepSize'])
            if f['filterType'] == 'PRICE_FILTER': tick = float(f['tickSize'])
        return step, tick
    except: return 1.0, 0.01

def main():
    logger.info("⚡ FLASH CATCHER AVVIATO. Pesca a strascico su crolli invisibili (-4%).")
    # Questa tecnica non compra a mercato. Piazza limit order ESTREMAMENTE in basso.
    # Se un bot istituzionale scarica a mercato, noi raccogliamo l'ombra della candela e rivendiamo al rimbalzo.
    
    active_orders = {} # symbol: order_id
    
    while True:
        try:
            # 1. Recupera EUR disponibili (visto che trada in EUR)
            eur_bal = float(client.get_asset_balance(asset='EUR')['free']) - get_vault_locked()

            # 2. Cancella vecchi ordini che non sono stati presi
            for sym, order_id in list(active_orders.items()):
                try:
                    status = client.get_order(symbol=sym, orderId=order_id)
                    if status['status'] == 'FILLED':
                        # Se è stato riempito, abbiamo pescato! Dobbiamo vendere subito in profitto.
                        qty = float(status['executedQty'])
                        buy_price = float(status['cummulativeQuoteQty']) / qty
                        
                        step, tick = get_filters(sym)
                        sell_price = round_price(buy_price * 1.02, tick) # +2% di rimbalzo istantaneo
                        sell_qty = round_step(qty, step)
                        
                        logger.info(f"🐟 PESCA RIUSCITA SU {sym}! Comprato a {buy_price}. Piazzo Sell a {sell_price} (+2%).")
                        client.create_order(symbol=sym, side='SELL', type='LIMIT', timeInForce='GTC', quantity=sell_qty, price=str(sell_price))
                        
                        # Stimiamo il profitto per il vault
                        add_to_vault((sell_qty * sell_price - qty * buy_price) * 0.33)
                        del active_orders[sym]
                        
                    elif status['status'] in ['CANCELED', 'REJECTED']:
                        del active_orders[sym]
                    else:
                        # Se è ancora aperto e vecchio, cancellalo per ricalcolare
                        client.cancel_order(symbol=sym, orderId=order_id)
                        del active_orders[sym]
                except Exception as e:
                    pass

            # 3. Piazza nuovi ordini esca (-4% sotto il prezzo attuale)
            if eur_bal > 10.0:
                for sym in SYMBOLS:
                    if sym in active_orders: continue
                    try:
                        ticker = client.get_symbol_ticker(symbol=sym)
                        current_price = float(ticker['price'])
                        
                        step, tick = get_filters(sym)
                        target_price = round_price(current_price * 0.96, tick) # -4%
                        qty = round_step(10.0 / target_price, step) # order di 10 EUR
                        
                        if qty > 0 and eur_bal >= 10.0:
                            order = client.create_order(symbol=sym, side='BUY', type='LIMIT', timeInForce='GTC', quantity=qty, price=str(target_price))
                            active_orders[sym] = order['orderId']
                            eur_bal -= 10.0
                            logger.info(f"🎣 Pescata impostata su {sym} a {target_price} EUR (-4%).")
                    except Exception as e:
                        pass
            
            logger.info("💗 Heartbeat OK. Reti gettate.")
            time.sleep(300) # Ricalcola ogni 5 minuti
            gc.collect()
            
        except Exception as e:
            logger.error(f"Errore Flash Catcher: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
