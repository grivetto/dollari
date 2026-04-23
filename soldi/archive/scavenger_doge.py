import gc
import os, time, logging, gc, json
from dotenv import load_dotenv
from binance.client import Client
from binance import ThreadedWebsocketManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/SCAVENGER.log"), logging.StreamHandler()])
logger = logging.getLogger("Scavenger")

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
VAULT_FILE = "/home/sergio/.openclaw/workspace/denaro/vault.json"

# Lo Scavenger (lo Sciacallo) gira sui MemeCoin minori (Pepe e Floki)
# Funziona su Websocket e ha come unica metrica il "Panic Selling" globale

def add_to_vault(amount):
    try:
        if os.path.exists(VAULT_FILE):
            with open(VAULT_FILE, 'r') as f:
                locked = float(json.load(f).get("LOCKED_EUR", 0.0))
        else: locked = 0.0
        
        locked += amount
        with open(VAULT_FILE, 'w') as f:
            json.dump({"LOCKED_EUR": locked}, f)
        logger.info(f"🦴 SCIACALLO HA NASCOSTO L'OSSO: {amount:.2f}€ in Cassaforte! [Tot: {locked:.2f}€]")
    except: pass

def get_step_size(symbol):
    try:
        info = client.get_symbol_info(symbol)
        for f in info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                return float(f['stepSize'])
    except: pass
    return 1.0

def process_socket_msg(msg):
    if 'data' not in msg or 'e' not in msg['data']: return
    event = msg['data']
    if event['e'] == 'kline':
        price = float(event['k']['c'])
        is_closed = event['k']['x']
        volume = float(event['k']['v'])
        symbol = event['s']
        
        # Scavenger non compra quasi mai, aspetta che ci sia un volume enorme e anomalo in un minuto con crollo prezzo
        # ... logic semplificata per minimizzare memoria (nessun array storico, solo il volume del tick)
        
        if is_closed:
            # Volume altissimo (spike di vendite)
            if volume > 500000000: # 500 milioni per PEPE in un minuto è alto
                # Compra 5 euro fittizi a bassissimo rischio e rivende su un tick di +0.2%
                logger.info(f"🦴 {symbol} SPIKE VOLUME: {volume} - SCIACALLO IN AZIONE!")
                
def main():
    logger.info("🦴 SCAVENGER (Lo Sciacallo) AVVIATO. Cercherà ossi tra i crolli delle meme coin a consumo RAM 0.")
    
    twm = ThreadedWebsocketManager(api_key=os.getenv('BINANCE_API_KEY'), api_secret=os.getenv('BINANCE_API_SECRET'))
    twm.start()
    
    twm.start_multiplex_socket(callback=process_socket_msg, streams=[f"pepeeur@kline_1m", f"flokieur@kline_1m"])
    
    try:
        while True:
            time.sleep(60)
            logger.info("💗 Heartbeat OK. Memoria pulita.")
            gc.collect()
    except KeyboardInterrupt:
        twm.stop()

if __name__ == "__main__":
    main()
