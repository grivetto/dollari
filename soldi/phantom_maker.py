import gc
import os, time, logging, gc, json, math
from dotenv import load_dotenv
from binance.client import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/PHANTOM.log"), logging.StreamHandler()])
logger = logging.getLogger("Phantom")

load_dotenv('/home/sergio/denaro/.env')
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
VAULT_FILE = "/home/sergio/.openclaw/workspace/denaro/vault.json"

def get_vault_locked():
    try:
        if os.path.exists(VAULT_FILE):
            with open(VAULT_FILE, 'r') as f:
                return float(json.load(f).get("LOCKED_EUR", 0.0))
    except: pass
    return 0.0

def get_step_size(symbol):
    try:
        info = client.get_symbol_info(symbol)
        for f in info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                return float(f['stepSize'])
    except: pass
    return 1.0

def get_tick_size(symbol):
    try:
        info = client.get_symbol_info(symbol)
        for f in info['filters']:
            if f['filterType'] == 'PRICE_FILTER':
                return float(f['tickSize'])
    except: pass
    return 0.01

def round_step(quantity, step_size):
    precision = int(round(-math.log10(step_size), 0))
    return round(quantity - (quantity % step_size), precision)

SYMBOLS = ["SOLEUR", "BNBEUR", "AVAXEUR", "DOTEUR", "ETHEUR", "ADAEUR", "LINKEUR", "DOGEEUR"]
TRADE_AMOUNT = 11.0  # 20 euro per limit order
BUY_DROP = 0.02      # Compra se crolla del 2%
SELL_PUMP = 0.02     # Vende con profitto del 2%

def main():
    logger.info("👻 PHANTOM MAKER AVVIATO. Piazza reti invisibili (Limit Orders) nel book per catturare crolli. Zero RAM/CPU.")
    
    while True:
        try:
            available_eur = float(client.get_asset_balance(asset='EUR')['free'])
            usable_eur = available_eur - get_vault_locked()
            
            for symbol in SYMBOLS:
                try:
                    open_orders = client.get_open_orders(symbol=symbol)
                    asset = symbol.replace('EUR', '')
                    asset_bal = float(client.get_asset_balance(asset=asset)['free'])
                    
                    ticker = client.get_symbol_ticker(symbol=symbol)
                    current_price = float(ticker['price'])
                    
                    step = get_step_size(symbol)
                    tick = get_tick_size(symbol)
                    
                    # Se abbiamo monete comprate dalla rete, piazziamo ordine di vendita LIMIT
                    if asset_bal * current_price > 10.0:
                        sell_orders = [o for o in open_orders if o['side'] == 'SELL']
                        if not sell_orders:
                            sell_price = round_step(current_price * (1 + SELL_PUMP), tick)
                            sell_qty = round_step(asset_bal, step)
                            if sell_qty > 0:
                                client.create_order(symbol=symbol, side='SELL', type='LIMIT', timeInForce='GTC', quantity=sell_qty, price=sell_price)
                                logger.info(f"👻 PHANTOM ha piazzato VENDITA per {sell_qty} {symbol} a {sell_price}€")
                    
                    # Se NON abbiamo monete, piazziamo rete di ACQUISTO LIMIT in basso
                    elif asset_bal * current_price <= 10.0:
                        buy_orders = [o for o in open_orders if o['side'] == 'BUY']
                        if not buy_orders and usable_eur >= TRADE_AMOUNT:
                            buy_price = round_step(current_price * (1 - BUY_DROP), tick)
                            buy_qty = round_step(TRADE_AMOUNT / buy_price, step)
                            if buy_qty > 0:
                                client.create_order(symbol=symbol, side='BUY', type='LIMIT', timeInForce='GTC', quantity=buy_qty, price=buy_price)
                                logger.info(f"👻 PHANTOM ha piazzato ACQUISTO (Rete) per {buy_qty} {symbol} a {buy_price}€ (-2%)")
                                usable_eur -= TRADE_AMOUNT
                        elif buy_orders:
                            # Cancella ordini troppo distanti (mercato salito oltre il 5% dalla rete)
                            for o in buy_orders:
                                order_price = float(o['price'])
                                if (current_price - order_price) / order_price > 0.05:
                                    client.cancel_order(symbol=symbol, orderId=o['orderId'])
                                    logger.info(f"👻 PHANTOM ha rimosso rete obsoleta su {symbol}")
                except Exception as e:
                    pass
                                
            # Riposa 2 minuti (consumo zero)
            time.sleep(120)
            logger.info("💗 Heartbeat OK. Memoria pulita.")
            gc.collect()
        except Exception as e:
            time.sleep(60)

if __name__ == "__main__":
    main()
