import asyncio
import ccxt.async_support as ccxt
import os, time, logging, json, fcntl
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/home/sergio/denaro/.env')

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [LEGION-MANAGER] - %(message)s',
    handlers=[logging.FileHandler('/home/sergio/denaro/legion_manager.log'), logging.StreamHandler()]
)
logger = logging.getLogger('LegionManager')

VAULT_FILE = '/home/sergio/denaro/vault.json'
SYMBOLS = [
    'MATIC/USDT', 'MKR/USDT', 'UNI/USDT', 'ALGO/USDT', 'CHZ/USDT', 'FTM/USDT',
    'GALA/USDT', 'BCH/USDT', 'ADA/USDT', 'LINK/USDT', 'ETC/USDT', 'AVAX/USDT',
    'NEAR/USDT', 'XTZ/USDT', 'VET/USDT', 'AAVE/USDT', 'DOT/USDT', 'SAND/USDT',
    'MANA/USDT', 'FIL/USDT', 'XLM/USDT', 'ENJ/USDT', 'ZIL/USDT', 'BAT/USDT',
    'EOS/USDT', 'LTC/USDT', 'AXS/USDT', 'ATOM/USDT'
]

TRADE_AMOUNT_USDT = 11.0

class LegionBot:
    def __init__(self, exchange, symbol):
        self.exchange = exchange
        self.symbol = symbol
        self.position = False
        self.buy_price = 0.0
        self.history = []

    async def update(self):
        try:
            ticker = await self.exchange.fetch_ticker(self.symbol)
            price = float(ticker['last'])
            self.history.append(price)
            if len(self.history) > 10: self.history.pop(0)

            if self.position:
                pnl = (price - self.buy_price) / self.buy_price
                if pnl >= 0.01 or pnl <= -0.06:
                    logger.info(f'⚔️ {self.symbol} CHIUDE OPERAZIONE! PNL: {pnl*100:.2f}%')
                    if pnl > 0:
                        await self.add_to_vault(TRADE_AMOUNT_USDT * pnl * 0.33)
                    self.position = False
            else:
                if len(self.history) == 10:
                    drop = (self.history[-1] - self.history[0]) / self.history[0]
                    if drop <= -0.01:
                        bal = await self.exchange.fetch_balance()
                        usdt_free = bal.get('USDT', {}).get('free', 0)
                        if usdt_free >= TRADE_AMOUNT_USDT:
                            logger.info(f'⚔️ {self.symbol} ATTACCA IL DROP! Prezzo: {price}')
                            self.buy_price = price
                            self.position = True
        except Exception as e:
            logger.error(f'Errore update {self.symbol}: {e}')

    async def add_to_vault(self, amount):
        try:
            # Using a separate thread for blocking file I/O in async
            def _write():
                with open(VAULT_FILE, 'r+') as f:
                    fcntl.flock(f, fcntl.LOCK_EX)
                    data = json.load(f)
                    locked = data.get('LOCKED_EUR', 0.0) + amount
                    data['LOCKED_EUR'] = locked
                    f.seek(0)
                    json.dump(data, f)
                    f.truncate()
                    fcntl.flock(f, fcntl.LOCK_UN)
            
            await asyncio.to_thread(_write)
            logger.info(f'⚖️ {self.symbol} HA VERSATO: +{amount:.2f}€ IN CASSAFORTE!')
        except Exception as e:
            logger.error(f'Errore vault {self.symbol}: {e}')

async def main():
    exchange = ccxt.binance({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_API_SECRET'),
        'enableRateLimit': True,
    })
    
    bots = [LegionBot(exchange, s) for s in SYMBOLS]
    logger.info(f'🚀 LegionManager avviato con {len(bots)} bot asincroni.')

    try:
        while True:
            # Execute all bot updates concurrently
            await asyncio.gather(*(bot.update() for bot in bots))
            await asyncio.sleep(60)
    except Exception as e:
        logger.error(f'Errore critico manager: {e}')
    finally:
        await exchange.close()

if __name__ == '__main__':
    asyncio.run(main())
