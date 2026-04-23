import gc
import gc
import time, json, logging, ccxt, os

logging.basicConfig(filename="NANO_RSI.log", level=logging.INFO, format='%(asctime)s - %(message)s')
SYMBOL = "EUR/USDT"

def fetch_rsi():
    try:
        exchange = ccxt.binance()
        ohlcv = exchange.fetch_ohlcv(SYMBOL, '5m', limit=15)
        closes = [x[4] for x in ohlcv]
        if len(closes) < 14: return 50
        gains = []
        losses = []
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0: gains.append(change)
            else: losses.append(abs(change))
        avg_gain = sum(gains) / 14 if gains else 0
        avg_loss = sum(losses) / 14 if losses else 0
        if avg_loss == 0: return 100
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    except:
        return 50

def run():
    logging.info("Nano RSI Scalper started.")
    import gc
    while True:
        gc.collect()
        try:
            rsi = fetch_rsi()
            status = "Waiting"
            if rsi < 30: status = "Oversold - Buy Signal"
            elif rsi > 70: status = "Overbought - Sell Signal"
            
            with open("nano_rsi_status.json", "w") as f:
                json.dump({"bot": "Nano RSI Scalper", "status": status, "rsi": round(rsi, 2), "timestamp": time.time()}, f)
            logging.info(f"RSI: {rsi:.2f} | Status: {status}")
            time.sleep(60)
        except Exception as e:
            time.sleep(60)

if __name__ == "__main__":
    run()
