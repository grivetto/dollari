import gc
import time, json, os, logging
from datetime import datetime

STATUS_FILE = "micro_funding_status.json"
logging.basicConfig(filename="MICRO_FUNDING.log", level=logging.INFO, format="%(asctime)s %(message)s")

def get_mock_profit():
    return round((time.time() % 3600) / 3600 * 0.5, 4) # Up to 0.5 EUR per hour

def main():
    logging.info("Micro Funding Sniffer avviato - Zero OOM.")
    print("Micro Funding Sniffer avviato.")
    import gc
    while True:
        gc.collect()
        try:
            profit = get_mock_profit()
            trades = int((time.time() % 100) / 10)
            data = {
                "bot_name": "Micro Funding Sniffer",
                "status": "running",
                "profit_eur": profit,
                "trades": trades,
                "timestamp": datetime.now().isoformat()
            }
            with open(STATUS_FILE, "w") as f:
                json.dump(data, f)
            time.sleep(15)
        except Exception as e:
            logging.error(f"Errore: {e}")
            time.sleep(15)

if __name__ == "__main__":
    main()
