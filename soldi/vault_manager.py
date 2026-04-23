import gc
import os, json, time, logging
from binance.client import Client
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - VAULT - %(message)s')
load_dotenv("/home/sergio/.openclaw/workspace/denaro/.env")
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

# Capitale EUR di partenza
INITIAL_EUR = 346.54
VAULT_FILE = "/home/sergio/.openclaw/workspace/denaro/vault.json"

def get_eur_balance():
    try:
        acc = client.get_account()
        for b in acc['balances']:
            if b['asset'] == 'EUR':
                return float(b['free'])
        return 0.0
    except Exception as e:
        logging.error(f"Error checking balance: {e}")
        return 0.0

def update_vault():
    eur_now = get_eur_balance()
    if eur_now <= INITIAL_EUR:
        logging.info(f"Liquidità corrente (€{eur_now:.2f}) sotto o pari all'investimento iniziale (€{INITIAL_EUR:.2f}). Nessun prelievo.")
        return
    
    profit = eur_now - INITIAL_EUR
    saved_amount = round(profit * 0.33, 2)
    
    # Update vault.json
    try:
        with open(VAULT_FILE, 'w') as f:
            json.dump({"LOCKED_EUR": saved_amount}, f)
        logging.info(f"✅ PROFITTO REALIZZATO: +€{profit:.2f} | 🔐 33% IN CASSAFORTE: €{saved_amount:.2f} (I Bot non potranno toccarlo!)")
    except Exception as e:
        logging.error(f"Failed to write vault: {e}")

if __name__ == "__main__":
    logging.info("🏦 SISTEMA DI RISERVA FRAZIONARIA (33%) AVVIATO.")
    import gc
    while True:
        gc.collect()
        update_vault()
        time.sleep(30)
