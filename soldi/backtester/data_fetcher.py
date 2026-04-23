import ccxt
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv('/home/sergio/denaro/.env')

def fetch_historical_data(symbol, timeframe='1m', days=30):
    exchange = ccxt.binance()
    print(f'Fetching {days} days of {timeframe} data for {symbol}...')
    
    all_ohlcv = []
    since = exchange.milliseconds() - (days * 24 * 60 * 60 * 1000)
    
    while since < exchange.milliseconds():
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)
        if not ohlcv:
            break
        all_ohlcv.extend(ohlcv)
        since = ohlcv[-1][0] + 1
        
    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Save to CSV for caching
    os.makedirs('data', exist_ok=True)
    filename = f'data/{symbol.replace("/", "_")}_{timeframe}.csv'
    df.to_csv(filename, index=False)
    print(f'Saved to {filename}')
    return df

if __name__ == '__main__':
    # Test fetch
    fetch_historical_data('MATIC/USDT', days=7)
