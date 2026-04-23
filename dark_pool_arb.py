import gc
import os, time, logging, gc, json
from collections import deque
from dotenv import load_dotenv
from binance.client import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/DARKPOOL.log"), logging.StreamHandler()])
logger = logging.getLogger("DarkPool")

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
        logger.info(f"🌑 DARK POOL ARBITRAGE: SOTTRATTI {amount:.2f}€ AL MERCATO! [Vault: {locked:.2f}€]")
    except: pass

# Triangolazioni di base: EUR -> CRYPTO -> BTC -> EUR
TRIANGLES = [
    ("SOLEUR", "SOLBTC", "BTCEUR"),
    ("ETHEUR", "ETHBTC", "BTCEUR"),
    ("BNBEUR", "BNBBTC", "BTCEUR"),
    ("ADAEUR", "ADABTC", "BTCEUR"),
    ("DOGEEUR", "DOGEBTC", "BTCEUR"),
    ("AVAXEUR", "AVAXBTC", "BTCEUR"),
    ("LINKEUR", "LINKBTC", "BTCEUR"),
    ("DOTEUR", "DOTBTC", "BTCEUR")
]

TRADE_AMOUNT = 11.0  # 50 euro per tentativo
MIN_PROFIT = 0.003   # 0.3% di disallineamento netto richiesto per colpire (copre le fees 3x0.1%)

def main():
    logger.info("🌑 DARK POOL ARBITRAGE AVVIATO. Cercherà inefficienze matematiche (Triangolazioni) ogni 5 secondi.")
    
    while True:
        try:
            available_eur = float(client.get_asset_balance(asset='EUR')['free'])
            if available_eur < TRADE_AMOUNT + get_vault_locked():
                logger.info("💗 Heartbeat OK. Memoria pulita. (Attesa liquidità)")
                time.sleep(10)
                continue
                
            # Recupera tutti i ticker in una sola chiamata (bassissimo impatto API/CPU)
            tickers = {t['symbol']: float(t['price']) for t in client.get_all_tickers()}
            
            for t1, t2, t3 in TRIANGLES:
                if t1 in tickers and t2 in tickers and t3 in tickers:
                    p1 = tickers[t1] # EUR per 1 Crypto
                    p2 = tickers[t2] # BTC per 1 Crypto
                    p3 = tickers[t3] # EUR per 1 BTC
                    
                    if p1 == 0 or p2 == 0 or p3 == 0: continue
                    
                    # Costo in EUR passando per BTC
                    # 1 Crypto = p2 BTC. 1 BTC = p3 EUR. Quindi 1 Crypto = p2 * p3 EUR
                    cost_via_btc = p2 * p3
                    
                    # Direzione 1: Compra Crypto con EUR, vendi per BTC, vendi BTC per EUR
                    profit_dir1 = (cost_via_btc - p1) / p1
                    
                    # Direzione 2: Compra BTC con EUR, compra Crypto con BTC, vendi Crypto per EUR
                    profit_dir2 = (p1 - cost_via_btc) / cost_via_btc
                    
                    # Se c'è un gap del >0.3% (copre le fee 0.1% * 3 = 0.3%) colpisci!
                    if profit_dir1 > MIN_PROFIT:
                        # Logica fittizia di trade qui. In realtà le fee Binance base sono 0.1%.
                        # Questa è un'operazione quasi priva di rischio di mercato (solo rischio esecuzione)
                        logger.info(f"🌑 GAP TROVATO: {t1}->{t2}->{t3} | Spread: {profit_dir1:.2%}")
                        # Simulazione o logica reale:
                        # client.create_order(symbol=t1, side='BUY', type='MARKET', quoteOrderQty=TRADE_AMOUNT)
                        # client.create_order(symbol=t2, side='SELL', type='MARKET', ...)
                        # client.create_order(symbol=t3, side='SELL', type='MARKET', ...)
                        # Per ora lo teniamo come Radar, non esegue tri-arb live perché rischia slippage senza BNB per le fee
                        pass
                        
            time.sleep(5) # Ciclo velocissimo ma leggero (1 sola API call)
            logger.info("💗 Heartbeat OK. Memoria pulita.")
            gc.collect()
        except Exception as e:
            logger.error(f"Errore: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
