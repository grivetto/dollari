import asyncio
import websockets
import json
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [WEBSOCKET ⚡] - %(message)s',
                    handlers=[logging.FileHandler("WEBSOCKET.log"), logging.StreamHandler()])

WS_URL = "wss://stream.binance.com:9443/ws/!miniTicker@arr"
SHM_FILE = "/dev/shm/binance_prices.json"
TMP_FILE = "/dev/shm/binance_prices_tmp.json"

prices_cache = {}

async def listen_binance():
    logging.info("⚡ Inizializzazione Connessione WebSocket a Binance (All MiniTickers)...")
    while True:
        try:
            async with websockets.connect(WS_URL) as ws:
                logging.info("✅ Connesso al WebSocket di Binance. Flusso dati in ricezione.")
                while True:
                    message = await ws.recv()
                    data = json.loads(message)
                    
                    # data è un array
                    updated = False
                    for item in data:
                        symbol = item['s']
                        prices_cache[symbol] = float(item['c'])
                        updated = True
                    
                    if updated:
                        # Scrittura atomica su RAM-Disk (velocissima)
                        with open(TMP_FILE, 'w') as f:
                            json.dump(prices_cache, f)
                        os.rename(TMP_FILE, SHM_FILE)
                        
        except Exception as e:
            logging.error(f"Errore WebSocket o disconnessione: {e}. Riconnessione tra 3s...")
            await asyncio.sleep(3)

if __name__ == "__main__":
    # Assicuriamoci che /dev/shm sia scrivibile
    if not os.path.exists("/dev/shm"):
        logging.error("La directory /dev/shm (RAM-Disk) non esiste! Uso /tmp come fallback.")
        SHM_FILE = "/tmp/binance_prices.json"
        TMP_FILE = "/tmp/binance_prices_tmp.json"
    
    asyncio.run(listen_binance())
