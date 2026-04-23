import gc
import os, time, logging, gc, json
from datetime import datetime
from dotenv import load_dotenv
from binance.client import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/YIELD_FARMER.log"), logging.StreamHandler()])
logger = logging.getLogger("Yield_Farmer")

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

def get_simple_earn_product(asset):
    try:
        # Usa il nuovo endpoint Simple Earn
        res = client.get_simple_earn_flexible_product_list(asset=asset)
        if res and 'rows' in res and len(res['rows']) > 0:
            return res['rows'][0]['productId']
    except Exception as e:
        logger.warning(f"Impossibile leggere prodotti Simple Earn per {asset}: {e}")
    return None

def subscribe_earn(product_id, amount):
    try:
        res = client.subscribe_simple_earn_flexible_product(productId=product_id, amount=amount)
        return res
    except Exception as e:
        logger.error(f"Errore iscrizione Earn: {e}")
        return None

def main():
    logger.info("🌾 YIELD FARMER AVVIATO. Sweeper per interessi passivi DeFi / Simple Earn.")
    
    assets_to_farm = ['USDT', 'EUR'] # Quelli stabili che non fanno trading attivo
    
    while True:
        try:
            logger.info("💗 Heartbeat OK. Ricerca liquidità dormiente per lo Yield Farming...")
            
            for asset in assets_to_farm:
                try:
                    bal = float(client.get_asset_balance(asset=asset)['free'])
                    if bal > 10.0:
                        # Scopriamo il productId
                        p_id = get_simple_earn_product(asset)
                        if p_id:
                            # Tentiamo di mettere in stake la liquidità libera, lasciando un piccolo buffer
                            amount_to_stake = round(bal - 5.0, 2)
                            if amount_to_stake > 0:
                                res = subscribe_earn(p_id, amount_to_stake)
                                if res:
                                    logger.info(f"✅ FARMING ATTIVATO: {amount_to_stake} {asset} bloccati in Earn flessibile (interessi passivi attivati).")
                except Exception as e:
                    pass
            
            time.sleep(3600) # Controlla ogni ora
            gc.collect()
            
        except Exception as e:
            logger.error(f"Errore Farmer: {e}")
            time.sleep(3600)

if __name__ == "__main__":
    main()
