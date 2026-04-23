import gc
import os, time, logging, gc, json, math
from collections import deque
from dotenv import load_dotenv
from binance.client import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/BLACKHOLE.log"), logging.StreamHandler()])
logger = logging.getLogger("BlackHole")

load_dotenv('/home/sergio/denaro/.env')
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
VAULT_FILE = "/home/sergio/.openclaw/workspace/denaro/vault.json"

# Black Hole (Il Buco Nero): Compra ad orari specifici e programmati, 
# intercettando i fusi orari globali (Es. apertura mercato asiatico, americano, ecc.)
# e succhia liquidità. Incredibilmente leggero perché usa solo l'orologio interno.

def add_to_vault(amount):
    try:
        if os.path.exists(VAULT_FILE):
            with open(VAULT_FILE, 'r') as f:
                locked = float(json.load(f).get("LOCKED_EUR", 0.0))
        else: locked = 0.0
        
        locked += amount
        with open(VAULT_FILE, 'w') as f:
            json.dump({"LOCKED_EUR": locked}, f)
        logger.info(f"🌌 BUCO NERO HA ASSORBITO MATERIA: {amount:.2f}€ in Cassaforte! [Tot: {locked:.2f}€]")
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

SYMBOLS = ["BTCEUR", "ETHEUR"]
TRADE_AMOUNT = 11.0

def main():
    logger.info("🌌 BLACK HOLE ABSORBER AVVIATO. Agisce sui fusi orari dei grandi mercati globali.")
    
    while True:
        try:
            # Recupera l'orario UTC
            h = time.gmtime().tm_hour
            m = time.gmtime().tm_min
            
            # Aperture indicative mercati globali in UTC:
            # 01:00 UTC (Tokyo)
            # 08:00 UTC (Londra)
            # 14:30 UTC (New York)
            
            is_market_open = (h == 1 and m == 0) or (h == 8 and m == 0) or (h == 14 and m == 30)
            
            if is_market_open:
                # Esegue un colpo per intercettare la volatilità dell'apertura
                for symbol in SYMBOLS:
                    ticker = client.get_symbol_ticker(symbol=symbol)
                    price = float(ticker['price'])
                    
                    try:
                        available_eur = float(client.get_asset_balance(asset='EUR')['free'])
                        if available_eur >= TRADE_AMOUNT:
                            step = get_step_size(symbol)
                            qty = round_step(TRADE_AMOUNT / price, step)
                            if qty > 0:
                                order = client.create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
                                logger.info(f"🌌 BLACK HOLE INGRESSO FUSO ORARIO {h}:{m} UTC su {symbol}")
                    except Exception as e:
                        pass
                
                # Attende un po' prima del prossimo controllo per non sparare più volte nello stesso minuto
                time.sleep(65)
            
            time.sleep(10)
            logger.info("💗 Heartbeat OK. Memoria pulita.")
            gc.collect()
            
        except Exception as e:
            time.sleep(60)

if __name__ == "__main__":
    main()
