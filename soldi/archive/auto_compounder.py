import os
import json
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [COMPOUNDER 📈] - %(message)s',
                    handlers=[logging.FileHandler("COMPOUNDER.log"), logging.StreamHandler()])

# Target Risk: max 2.5% del capitale libero per bot
RISK_FACTOR = 0.025
MIN_TRADE_EUR = 5.5

def calculate_new_sizes():
    try:
        from telegram_bot_interactive import get_full_status, CAPITALE_VERSATO_TOTALE
        import re
        
        # Estrarre capitale totale (inclusi bloccati)
        status_lines = get_full_status().split('\n')
        total_eur = 650.0
        for line in status_lines:
            if "Valore Attuale" in line:
                try: total_eur = float(re.sub(r'[^\d.]', '', line))
                except: pass
                
        # Calcolo del rischio per bot
        new_size = total_eur * RISK_FACTOR
        if new_size < MIN_TRADE_EUR: new_size = MIN_TRADE_EUR
        
        return round(new_size, 1)
    except Exception as e:
        logging.error(f"Errore compounder: {e}")
        return MIN_TRADE_EUR

def run_compounder():
    logging.info("📈 AUTO-COMPOUNDER ATTIVATO. Ciclo di aggiustamento Size ogni 12 ore.")
    while True:
        try:
            new_size = calculate_new_sizes()
            logging.info(f"🔄 Calcolata nuova Size ottimale per trade: {new_size} € (Risk: {RISK_FACTOR*100}%)")
            
            # Qui andrebbe l'aggiornamento automatico dei bot, per ora lo segnaliamo nel file config
            config_path = "/home/sergio/.openclaw/workspace/denaro/trade_config.json"
            config_data = {}
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r") as f:
                        config_data = json.load(f)
                except: pass
            
            config_data["current_trade_size"] = new_size
            with open(config_path, "w") as f:
                json.dump(config_data, f, indent=4)
                
            logging.info(f"✅ Configurazione Trade aggiornata. I bot leggeranno la nuova size al prossimo ciclo.")
            time.sleep(43200) # 12 ore
            
        except Exception as e:
            logging.error(f"Errore Loop: {e}")
            time.sleep(3600)

if __name__ == '__main__':
    run_compounder()
