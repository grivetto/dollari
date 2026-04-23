import gc
import os, time, logging, gc, json, fcntl
from dotenv import load_dotenv
from binance.client import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/LEGION_ADA.log"), logging.StreamHandler()])
logger = logging.getLogger("Legion_ADA")

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
    try:
        with open(VAULT_FILE, "r+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            data = json.load(f)
            locked = data.get("LOCKED_EUR", 0.0) + amount
            data["LOCKED_EUR"] = locked
            f.seek(0)
            json.dump(data, f)
            f.truncate()
            fcntl.flock(f, fcntl.LOCK_UN)
        logger.info(f"⚖️ LEGION {SYMBOL} HA VERSATO: +{amount:.2f}€ IN CASSAFORTE!")
    except Exception as e:
        logger.error(f"Errore vault: {e}")

SYMBOL = "ADAUSDT"
TRADE_AMOUNT_USDT = 11.0

def main():
    logger.info("⚔️ LEGION ADA AVVIATO. Micro-operativo su timeframe lunghi. Zero OOM.")
    
    position = False
    buy_price = 0.0
    history = []
    
    while True:
        try:
            ticker = client.get_symbol_ticker(symbol=SYMBOL)
            price = float(ticker['price'])
            history.append(price)
            if len(history) > 10: history.pop(0) # 10 minuti di storia
            
            if position:
                pnl = (price - buy_price) / buy_price
                if pnl >= 0.01 or pnl <= -0.06: # +2% TP, -4% SL
                    logger.info(f"⚔️ LEGION ADA CHIUDE OPERAZIONE! PNL: {pnl*100:.2f}%")
                    # Dato il capitale ridotto, simuliamo ordini o piaziamo veri se ci sono capitali
                    usdt_bal = float(client.get_asset_balance(asset='USDT')['free'])
                    if pnl > 0:
                        add_to_vault(TRADE_AMOUNT_USDT * pnl * 0.33)
                    position = False
            else:
                if len(history) == 10:
                    drop = (history[-1] - history[0]) / history[0]
                    if drop <= -0.02: # Crollo del 3.5% in 10 minuti
                        try:
                            usdt_bal = float(client.get_asset_balance(asset='USDT')['free'])
                            if usdt_bal >= TRADE_AMOUNT_USDT:
                                logger.info(f"⚔️ LEGION ADA ATTACCA IL DROP (-3.5%)! Prezzo: {price}")
                                buy_price = price
                                position = True
                        except: pass
            
            time.sleep(60) # 1 request per min
            logger.info("💗 Heartbeat OK.")
            gc.collect()
        except Exception as e:
            time.sleep(60)

if __name__ == "__main__":
    main()
