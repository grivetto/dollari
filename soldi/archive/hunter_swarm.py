import gc
import os, time, math, logging, gc, json
from collections import deque
from dotenv import load_dotenv
from binance.client import Client
from binance import ThreadedWebsocketManager
from binance.enums import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/HUNTER_SWARM.log"), logging.StreamHandler()])
logger = logging.getLogger("Swarm")

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

# Lo Swarm (Sciame) si divide in 5 mini-bot autonomi su socket, ognuno con 20€,
# per colpire simultaneamente più monete quando il mercato scende a candela rossa piena.
SYMBOLS = ["SOLEUR", "AVAXEUR", "DOTEUR", "BNBEUR", "ETHEUR", "LINKEUR", "PEPEEUR", "DOGEEUR", "ADAEUR", "XRPBTC"]
TRADE_AMOUNT = 11.0  
MAX_SWARM_SIZE = 10

VAULT_FILE = "/home/sergio/.openclaw/workspace/denaro/vault.json"
MISSION_FILE = "/home/sergio/.openclaw/workspace/denaro/daily_mission.json"

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
        logger.info(f"🍯 LO SCIAME HA VERSATO MIELE NEL VAULT! +{amount:.2f}€")
    except: pass

def update_daily_mission(pnl_amount):
    try:
        with open(MISSION_FILE, 'r') as f:
            mission = json.load(f)
        mission["profit_today"] += pnl_amount
        
        if mission["profit_today"] >= mission["target_eur"] and not mission["achieved"]:
            mission["achieved"] = True
            
        with open(MISSION_FILE, 'w') as f:
            json.dump(mission, f)
        return mission
    except: pass
    return None

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

# Stato memoria leggerissimo
positions = {}
klines_o = {s: 0.0 for s in SYMBOLS} # open price of current minute

def process_socket_msg(msg):
    if 'data' not in msg or 'e' not in msg['data']: return
    event = msg['data']
    
    if event['e'] == 'kline':
        symbol = event['s']
        k = event['k']
        price = float(k['c'])
        open_p = float(k['o'])
        is_closed = k['x']
        
        # Gestione Uscite
        if symbol in positions:
            entry = positions[symbol]['entry']
            qty = positions[symbol]['qty']
            
            pnl = (price - entry) / entry
            
            # Lo sciame prende morsi veloci e scappa (+0.3%)
            take_profit = pnl > 0.001 
            stop_loss = pnl <= -0.05 # Se perde il 5% taglia
            
            if take_profit or stop_loss:
                reason = "PROFIT" if take_profit else "STOP"
                try:
                    asset = symbol.replace('EUR', '').replace('BTC', '')
                    actual_qty = float(client.get_asset_balance(asset=asset)['free'])
                    step = get_step_size(symbol)
                    sell_qty = round_step(actual_qty, step)
                    
                    client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=sell_qty)
                    
                    real_pnl = (price - entry) * qty
                    if "BTC" in symbol:
                        ebtc = float(client.get_symbol_ticker(symbol="BTCEUR")['price'])
                        real_pnl *= ebtc
                        
                    m = update_daily_mission(real_pnl)
                    logger.info(f"🐝 {reason} {symbol} | Gain: {real_pnl:+.2f}€ | Progresso: {m['profit_today']:.2f}€")
                    
                    if real_pnl > 0: add_to_vault(real_pnl * 0.33)
                        
                    del positions[symbol]
                except Exception as e:
                    pass

        # Gestione Ingressi
        if not is_closed and symbol not in positions and len(positions) < MAX_SWARM_SIZE:
            # Drop violento all'interno della stessa candela (-0.5% in un minuto)
            drop = (price - open_p) / open_p
            if drop <= -0.002:
                try:
                    trade_amt = TRADE_AMOUNT
                    if "BTC" in symbol:
                        ebtc = float(client.get_symbol_ticker(symbol="BTCEUR")['price'])
                        trade_amt = trade_amt / ebtc
                        
                    # Verifica liquidità base
                    eur_bal = float(client.get_asset_balance(asset='EUR')['free'])
                    if eur_bal < TRADE_AMOUNT + get_vault_locked():
                        return
                        
                    step = get_step_size(symbol)
                    qty = round_step(trade_amt / price, step)
                    
                    if qty > 0:
                        order = client.create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
                        executed_qty = sum([float(f['qty']) for f in order['fills']])
                        avg_price = sum([float(f['price']) * float(f['qty']) for f in order['fills']]) / executed_qty if executed_qty > 0 else price
                        
                        positions[symbol] = {'entry': avg_price, 'qty': executed_qty}
                        logger.info(f"🐝 LO SCIAME HA ATTACCATO {symbol} al ribasso ({drop:.2%})! {executed_qty} @ {avg_price}€")
                except: pass

def main():
    logger.info("🐝 HUNTER SWARM (Lo Sciame) AVVIATO. Aggredisce le candele rosse in tempo reale con micro-squadre da 20€.")
    
    twm = ThreadedWebsocketManager(api_key=os.getenv('BINANCE_API_KEY'), api_secret=os.getenv('BINANCE_API_SECRET'))
    twm.start()
    
    streams = [f"{s.lower()}@kline_1m" for s in SYMBOLS]
    twm.start_multiplex_socket(callback=process_socket_msg, streams=streams)
    
    try:
        while True:
            time.sleep(60)
            logger.info("💗 Heartbeat OK.")
            gc.collect()
    except KeyboardInterrupt:
        twm.stop()

if __name__ == "__main__":
    main()
