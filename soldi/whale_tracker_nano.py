import gc
import time, json, logging, ccxt

logging.basicConfig(filename="WHALE_TRACKER.log", level=logging.INFO, format='%(asctime)s - %(message)s')

def get_order_book(symbol="BTC/EUR"):
    try:
        exchange = ccxt.binance()
        ob = exchange.fetch_order_book(symbol, limit=20)
        bids = sum([x[1] for x in ob['bids']])
        asks = sum([x[1] for x in ob['asks']])
        return bids, asks
    except:
        return 0, 0

def run():
    logging.info("Whale Tracker Nano started.")
    import gc
    while True:
        gc.collect()
        try:
            bids, asks = get_order_book("BTC/EUR")
            imbalance = bids / (asks + 0.001)
            status = "Neutral"
            if imbalance > 3: status = "Whale Accumulation (Buy Wall)"
            elif imbalance < 0.33: status = "Whale Distribution (Sell Wall)"
            
            with open("whale_tracker_status.json", "w") as f:
                json.dump({"bot": "Whale Tracker", "status": status, "bids_vol": round(bids, 2), "asks_vol": round(asks, 2), "imbalance": round(imbalance, 2), "timestamp": time.time()}, f)
            logging.info(f"BTC Imbalance: {imbalance:.2f} | Status: {status}")
            time.sleep(30)
        except Exception as e:
            time.sleep(30)

if __name__ == "__main__":
    run()
