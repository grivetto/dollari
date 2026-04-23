import gc
import os, time, logging, gc, json, math
from datetime import datetime
from dotenv import load_dotenv
from binance.client import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/DCA_ACCUMULATOR.log"), logging.StreamHandler()])
logger = logging.getLogger("DCA_Accumulator")

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

STATE_FILE = "/home/sergio/.openclaw/workspace/denaro/dca_state.json"
VAULT_FILE = "/home/sergio/.openclaw/workspace/denaro/vault.json"

# Compriamo 6 EUR di BTC e 6 EUR di ETH ogni 24 ore (il minimo su Binance è 5 EUR per ordine)
ASSETS_TO_BUY = {
    "BTCEUR": 6.0,
    "ETHEUR": 6.0
}

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
    return 0.00001

def round_step(quantity, step_size):
    precision = int(round(-math.log10(step_size), 0))
    return round(quantity - (quantity % step_size), precision)

def main():
    logger.info("🧱 DCA ACCUMULATOR AVVIATO. Acquisto inesorabile e cieco di BTC ed ETH a lungo termine.")
    
    while True:
        try:
            today_str = datetime.now().strftime("%Y-%m-%d")
            state = {}
            if os.path.exists(STATE_FILE):
                try:
                    with open(STATE_FILE, 'r') as f:
                        state = json.load(f)
                except: pass
                
            last_buy = state.get("last_buy_date", "")
            
            if last_buy != today_str:
                logger.info(f"📅 Nuovo giorno rilevato ({today_str}). Eseguo il DCA settimanale/giornaliero.")
                
                # Assicuriamoci di avere USDT (vendendo un po' di EUR se necessario, visto che il pair è USDT)
                total_usdt_needed = sum(ASSETS_TO_BUY.values())
                # Non serve convertire, compriamo in EUR

                # Compra gli asset
                all_success = True
                for symbol, amount_usdt in ASSETS_TO_BUY.items():
                    try:
                        ticker = client.get_symbol_ticker(symbol=symbol)
                        price = float(ticker['price'])
                        step = get_step_size(symbol)
                        qty = round_step(amount_usdt / price, step)
                        
                        if qty > 0:
                            qty_str = f"{qty:.8f}"
                            if qty_str.endswith('.'): qty_str = qty_str[:-1]
                            if '.' in qty_str:
                                qty_str = qty_str.rstrip('0').rstrip('.')
                            if qty_str == "": qty_str = "0"
                            order = client.create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty_str)
                            logger.info(f"✅ DCA ESEGUITO: Comprati {qty_str} {symbol.replace('USDT','')} a ~{price} USDT.")
                    except Exception as e:
                        logger.error(f"Errore acquisto DCA {symbol}: {e}")
                        all_success = False
                
                if all_success:
                    state["last_buy_date"] = today_str
                    with open(STATE_FILE, 'w') as f:
                        json.dump(state, f)
            
            logger.info("💗 Heartbeat OK. DCA in attesa.")
            time.sleep(60)
            gc.collect()
            
        except Exception as e:
            logger.error(f"Errore generale DCA: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
