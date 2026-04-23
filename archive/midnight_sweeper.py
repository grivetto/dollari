import os, json, logging
from dotenv import load_dotenv
from binance.client import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/SWEEPER.log"), logging.StreamHandler()])
logger = logging.getLogger("Sweeper")

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

WORKSPACE = "/home/sergio/.openclaw/workspace/denaro"
VAULT_FILE = os.path.join(WORKSPACE, "vault.json")
MIDNIGHT_STATE = os.path.join(WORKSPACE, "midnight_state.json")

def get_total_eur():
    balances = client.get_account()['balances']
    assets = {b['asset']: float(b['free']) + float(b['locked']) for b in balances if float(b['free']) > 0 or float(b['locked']) > 0}
    tickers = client.get_all_tickers()
    prices = {t['symbol']: float(t['price']) for t in tickers}
    
    total_eur = assets.get('EUR', 0) + assets.get('USDT', 0)
    for asset, qty in assets.items():
        if asset in ['EUR', 'USDT']: continue
        symbol = f"{asset}EUR"
        if symbol in prices: total_eur += qty * prices[symbol]
        elif f"{asset}BTC" in prices and "BTCEUR" in prices: total_eur += qty * prices[f"{asset}BTC"] * prices["BTCEUR"]
    return total_eur

def add_to_vault(amount):
    try:
        data = {}
        if os.path.exists(VAULT_FILE):
            with open(VAULT_FILE, 'r') as f:
                data = json.load(f)
        
        locked = data.get("LOCKED_EUR", 0.0) + amount
        data["LOCKED_EUR"] = locked
        data["SWEEPER_TRACKER"] = data.get("SWEEPER_TRACKER", 0.0) + amount
        
        with open(VAULT_FILE, 'w') as f:
            json.dump(data, f)
        return locked
    except Exception as e:
        logger.error(f"Errore vault sweeper: {e}")
        return 0

def main():
    logger.info("🧹 MIDNIGHT SWEEPER: Avvio chiusura giornaliera e calcolo incassi.")
    
    # 2. Calcolo profitti e spostamento nella cassaforte
    today_total = get_total_eur()
    yesterday_total = today_total # default if no file
    
    if os.path.exists(MIDNIGHT_STATE):
        try:
            with open(MIDNIGHT_STATE, 'r') as f:
                yesterday_total = json.load(f).get("midnight_eur", today_total)
        except: pass

    daily_profit = today_total - yesterday_total
    
    if daily_profit > 0:
        logger.info(f"💰 PROFITTO DEL GIORNO RILEVATO: +{daily_profit:.2f}€. Spostamento in cassaforte.")
        add_to_vault(daily_profit)
    else:
        logger.info(f"📉 Nessun profitto netto oggi ({daily_profit:.2f}€). Nessun versamento aggiuntivo in cassaforte.")

    # 3. Salva lo snapshot per domani
    try:
        with open(MIDNIGHT_STATE, 'w') as f:
            json.dump({"midnight_eur": today_total}, f)
        logger.info(f"📸 Snapshot portafoglio salvato: {today_total:.2f}€")
    except Exception as e:
        logger.error(f"Errore snapshot: {e}")

if __name__ == "__main__":
    main()
