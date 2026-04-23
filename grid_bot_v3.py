import os, time, logging, json
from datetime import datetime
from dotenv import load_dotenv
from binance.client import Client
from core.database import log_trade, log_price, log_snapshot
from core.risk_manager import risk_manager

load_dotenv('/home/sergio/denaro/.env')
logging.basicConfig(filename='/home/sergio/denaro/grid_v3.log', level=logging.INFO, format='%(asctime)s - GRID - %(levelname)s - %(message)s')

CONFIG_PATH = '/home/sergio/denaro/grid_config_nuvola.json'

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f'Config load error: {e}')
        return None

def get_sma(client, symbol, interval='15m', limit=20):
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        closes = [float(k[4]) for k in klines]
        return sum(closes) / len(closes)
    except Exception as e:
        logging.error(f'Error calculating SMA for {symbol}: {e}')
        return None

def is_safe_to_trade(client, symbol, side, current_price):
    sma = get_sma(client, symbol)
    if sma:
        deviation = (current_price - sma) / sma
        if side == 'BUY' and deviation > 0.02:
            logging.warning(f'Mean Reversion: Price {current_price} too far above SMA. Blocking BUY.')
            return False
        if side == 'SELL' and deviation < -0.02:
            logging.warning(f'Mean Reversion: Price {current_price} too far below SMA. Blocking SELL.')
            return False
    
    if side == 'BUY':
        config = load_config()
        amount_eur = config.get('ORDER_SIZE_EUR', 15.0) if config else 15.0
        allowed, reason = risk_manager.check_exposure(symbol, amount_eur)
        if not allowed:
            logging.warning(f'Risk Manager: {reason}. Blocking trade.')
            return False
            
    return True

def run_bot():
    client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
    logging.info('🚀 DENARO GRID BOT v3.2 (Quant Risk Enabled) Starting...')
    
    last_snapshot = 0
    
    while True:
        try:
            config = load_config()
            if not config: 
                time.sleep(10)
                continue
                
            for symbol in config['SYMBOLS']:
                ticker = client.get_symbol_ticker(symbol=symbol)
                price = float(ticker['price'])
                
                log_price(symbol, price, 0)
                
                safe = is_safe_to_trade(client, symbol, 'BUY', price)
                status = 'SAFE' if safe else 'BLOCKED'
                logging.info(f'{symbol} Price: {price} | Status: {status}')
                
            if time.time() - last_snapshot > 3600:
                total_eq = risk_manager.get_total_equity()
                log_snapshot(total_eq, 0, 0, 0) 
                last_snapshot = time.time()
                logging.info(f'Equity Snapshot saved: {total_eq:.2f}€')

            time.sleep(60)
        except Exception as e:
            logging.error(f'Main loop error: {e}')
            time.sleep(10)

if __name__ == '__main__':
    run_bot()
