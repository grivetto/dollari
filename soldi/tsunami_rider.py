import gc
import os, time, logging, gc, json
from dotenv import load_dotenv
from binance.client import Client
from binance import ThreadedWebsocketManager
import math

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/TSUNAMI.log"), logging.StreamHandler()])
logger = logging.getLogger("Tsunami")

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

def add_to_vault(amount):
    locked = get_vault_locked() + amount
    try:
        with open(VAULT_FILE, 'w') as f:
            json.dump({"LOCKED_EUR": locked}, f)
        logger.info(f"🌊 TSUNAMI HA DEPOSITATO {amount:.2f}€ IN CASSAFORTE!")
    except: pass

def get_step_size(symbol):
    try:
        info = client.get_symbol_info(symbol)
        for f in info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                return float(f['stepSize'])
    except: pass
    return 1.0

def round_step(quantity, step_size):
    precision = int(round(-math.log10(step_size), 0))
    return round(quantity - (quantity % step_size), precision)

SYMBOLS = ["SOLEUR", "DOGEEUR", "AVAXEUR", "BNBEUR", "PEPEEUR"]
TRADE_AMOUNT = 11.0  # Carico pesante, cavalca solo tsunami certi

positions = {}

def process_socket_msg(msg):
    if 'data' not in msg or 'e' not in msg['data']: return
    event = msg['data']
    if event['e'] == 'kline':
        symbol = event['s']
        k = event['k']
        price = float(k['c'])
        open_price = float(k['o'])
        is_closed = k['x']
        volume = float(k['v'])
        
        # Gestione Uscita
        if symbol in positions:
            entry = positions[symbol]['entry']
            qty = positions[symbol]['qty']
            highest = max(positions[symbol].get('highest', entry), price)
            positions[symbol]['highest'] = highest
            
            pnl = (price - entry) / entry
            
            # Esce veloce: Take Profit dinamico o Stop Loss stretto
            take_profit = pnl > 0.003 or (pnl > 0.0015 and price < highest * 0.998)
            stop_loss = pnl <= -0.01  # Massimo -1% sullo tsunami
            
            if take_profit or stop_loss:
                reason = "PROFIT" if take_profit else "STOP"
                try:
                    asset = symbol.replace('EUR', '')
                    actual_qty = float(client.get_asset_balance(asset=asset)['free'])
                    step = get_step_size(symbol)
                    sell_qty = round_step(actual_qty, step)
                    
                    if sell_qty > 0:
                        client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=sell_qty)
                        real_pnl = (price - entry) * qty
                        logger.info(f"🌊 {reason} {symbol} TSUNAMI CONCLUSO | Gain: {real_pnl:+.2f}€")
                        
                        if real_pnl > 0:
                            add_to_vault(real_pnl * 0.33)
                            
                        del positions[symbol]
                except Exception as e:
                    pass

        # Gestione Ingresso (Solo chiusura candela)
        if is_closed and symbol not in positions:
            # Candela 1m superiore allo 0.8% = Tsunami in corso (Pompa violenta)
            pump_percent = (price - open_price) / open_price
            if pump_percent >= 0.008:
                try:
                    available_eur = float(client.get_asset_balance(asset='EUR')['free'])
                    usable_eur = available_eur - get_vault_locked()
                    
                    if usable_eur >= TRADE_AMOUNT:
                        step = get_step_size(symbol)
                        qty = round_step(TRADE_AMOUNT / price, step)
                        
                        if qty > 0:
                            order = client.create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
                            executed_qty = sum([float(f['qty']) for f in order['fills']])
                            avg_price = sum([float(f['price']) * float(f['qty']) for f in order['fills']]) / executed_qty if executed_qty > 0 else price
                            
                            positions[symbol] = {'entry': avg_price, 'qty': executed_qty, 'highest': avg_price}
                            logger.info(f"🌊 TSUNAMI RIDER ENTRATO! {symbol} pompata del {pump_percent:.2%}. {executed_qty} @ {avg_price}€")
                except Exception as e:
                    pass

def main():
    logger.info("🌊 TSUNAMI RIDER AVVIATO. Cavalca le candele verdi giganti (Pumps > 0.8%/min) e le spreme (No OOM).")
    
    # Recupera posizioni
    for sym in SYMBOLS:
        asset = sym.replace('EUR', '')
        try:
            qty = float(client.get_asset_balance(asset=asset)['free'])
            ticker = client.get_symbol_ticker(symbol=sym)
            price = float(ticker['price'])
            if qty * price > 15.0:
                positions[sym] = {'entry': price, 'qty': qty, 'highest': price}
                logger.info(f"🔄 Tsunami recuperato dal saldo: {sym} (Qty: {qty}, Val: ~{qty*price:.2f}€)")
        except: pass
    
    twm = ThreadedWebsocketManager(api_key=os.getenv('BINANCE_API_KEY'), api_secret=os.getenv('BINANCE_API_SECRET'))
    twm.start()
    
    streams = [f"{s.lower()}@kline_1m" for s in SYMBOLS]
    twm.start_multiplex_socket(callback=process_socket_msg, streams=streams)
    
    try:
        while True:
            time.sleep(60)
            logger.info("💗 Heartbeat OK. Memoria pulita.")
            gc.collect()
    except KeyboardInterrupt:
        twm.stop()

if __name__ == "__main__":
    main()
