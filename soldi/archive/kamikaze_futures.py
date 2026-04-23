import os
import time
import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [KAMIKAZE 🧨] - %(message)s')
logger = logging.getLogger("Kamikaze")

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

client = Client(api_key, api_secret)

SYMBOL = 'SOLUSDT'
LEVERAGE = 20
MARGIN_TYPE = 'ISOLATED'
RISK_USDT = 15.0  # Quanti USDT usare dal conto Futures

def setup_kamikaze():
    try:
        # Imposta leva
        client.futures_change_leverage(symbol=SYMBOL, leverage=LEVERAGE)
        logger.info(f"Leva impostata a {LEVERAGE}x su {SYMBOL}")
        
        # Imposta margine isolato (evita di bruciare l'intero conto)
        client.futures_change_margin_type(symbol=SYMBOL, marginType=MARGIN_TYPE)
        logger.info(f"Margine impostato su {MARGIN_TYPE}")
    except BinanceAPIException as e:
        if e.code == -4046:  # No need to change margin type
            pass
        else:
            logger.error(f"Errore configurazione margine: {e}")

def run_kamikaze():
    logger.info("☠️ KAMIKAZE BOT ONLINE - PRONTO ALLA LIQUIDAZIONE O AL 1000%")
    setup_kamikaze()
    
    try:
        # Check balance
        account = client.futures_account()
        usdt_balance = float([b['availableBalance'] for b in account['assets'] if b['asset'] == 'USDT'][0])
        logger.info(f"Fondi disponibili conto Futures: {usdt_balance:.2f} USDT")
        
        if usdt_balance < RISK_USDT:
            logger.warning(f"Fondi insufficienti sul conto Futures! Hai solo {usdt_balance:.2f} USDT. Trasferisci {RISK_USDT} USDT dal conto Spot ai Futures.")
            return

        # LOGICA KAMIKAZE:
        # Analisi momentum su 1 minuto (se sta pompando forte, entra LONG a leva 20x)
        klines = client.futures_klines(symbol=SYMBOL, interval=Client.KLINE_INTERVAL_1MINUTE, limit=5)
        current_price = float(klines[-1][4])
        logger.info(f"Prezzo attuale {SYMBOL}: {current_price}")
        
        logger.info("ATTENZIONE: Il bot è in modalità STANDBY. Sposta i fondi su Futures tramite l'app Binance e dimmi 'GO' per fargli aprire il trade a leva 20x.")

    except BinanceAPIException as e:
        logger.error(f"Errore critico Binance API: {e}")

if __name__ == '__main__':
    run_kamikaze()
