import asyncio
import ccxt.async_support as ccxt
import os, time, logging, json, fcntl
import pandas as pd
import pandas_ta as ta
import websockets
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/home/sergio/denaro/.env')

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [LEGION-V2] - %(message)s',
    handlers=[logging.FileHandler('/home/sergio/denaro/legion_manager_v2.log'), logging.StreamHandler()]
)
logger = logging.getLogger('LegionV2')

VAULT_FILE = '/home/sergio/denaro/vault.json'
SYMBOLS_WS = [
    'maticusdt', 'mkrusdt', 'uniusdt', 'algousdt', 'chzusdt', 'ftmusdt',
    'galausdt', 'bchusdt', 'adausdt', 'linkusdt', 'etcusdt', 'avaxusdt',
    'nearusdt', 'xtzusdt', 'vetusdt', 'aaveusdt', 'dotusdt', 'sandusdt',
    'manausdt', 'filusdt', 'xlmusdt', 'enjusdt', 'zilusdt', 'batusdt',
    'eosusdt', 'ltcusdt', 'axsusdt', 'atomusdt'
]
SYMBOLS_CCXT = [s.upper().replace('USDT', '/USDT') for s in SYMBOLS_WS]

# Strategy Constants
RISK_PER_TRADE_PCT = 0.01  # Risk 1% of balance per trade
MAX_TRADE_USDT = 50.0      # Cap per trade
MIN_TRADE_USDT = 5.0       # Min per trade
ATR_PERIOD = 14
TP_ATR_MULT = 1.5          # TP = Price + (ATR * 1.5)
SL_ATR_MULT = 2.0          # SL = Price - (ATR * 2.0)

class PriceFeed:
    def __init__(self):
        self.prices = {}
        self.volumes = {}
        self.active = True

    async def start(self):
        url = "wss://stream.binance.com:9443/ws/!ticker@arr"
        while self.active:
            try:
                async with websockets.connect(url) as ws:
                    logger.info("📡 WebSocket connected to Binance !ticker@arr")
                    while self.active:
                        data = await ws.recv()
                        tickers = json.loads(data)
                        for t in tickers:
                            s = t['s'].lower()
                            if s in SYMBOLS_WS:
                                self.prices[s] = float(t['c'])
                                self.volumes[s] = float(t['v'])
            except Exception as e:
                logger.error(f"WebSocket Error: {e}. Reconnecting in 5s...")
                await asyncio.sleep(5)

class LegionBot:
    def __init__(self, exchange, symbol_ws, symbol_ccxt):
        self.exchange = exchange
        self.symbol_ws = symbol_ws
        self.symbol_ccxt = symbol_ccxt
        self.position = False
        self.buy_price = 0.0
        self.current_tp = 0.0
        self.current_sl = 0.0
        self.trade_amount = 0.0
        self.price_history = []
        self.vol_history = []
        self.ohlcv_data = None

    async def init_indicators(self):
        try:
            # Seed ATR with 1m candles
            ohlcv = await self.exchange.fetch_ohlcv(self.symbol_ccxt, timeframe='1m', limit=100)
            self.ohlcv_data = pd.DataFrame(ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
            logger.info(f'Initialized OHLCV for {self.symbol_ccxt}')
        except Exception as e:
            logger.error(f'Error seeding {self.symbol_ccxt}: {e}')

    def calculate_atr(self):
        if self.ohlcv_data is None or len(self.ohlcv_data) < ATR_PERIOD: return 0
        atr = ta.atr(self.ohlcv_data['high'], self.ohlcv_data['low'], self.ohlcv_data['close'], length=ATR_PERIOD)
        return atr.iloc[-1] if not atr.empty else 0

    def calculate_indicators(self):
        if len(self.price_history) < 50: return None, None
        df = pd.DataFrame({'close': self.price_history})
        rsi = ta.rsi(df['close'], length=14)
        ema = ta.ema(df['close'], length=50)
        return rsi.iloc[-1] if not rsi.empty else 50, ema.iloc[-1] if not ema.empty else 0

    async def calculate_position_size(self, price, atr):
        try:
            bal = await self.exchange.fetch_balance()
            usdt_free = bal.get('USDT', {}).get('free', 0)
            
            # Stop distance in %
            sl_dist = (atr * SL_ATR_MULT) / price if atr > 0 else 0.06 # Default 6%
            
            # Risk = (Balance * Risk%) / SL_Dist
            risk_amount = usdt_free * RISK_PER_TRADE_PCT
            size = risk_amount / sl_dist if sl_dist > 0 else 11.0
            
            return max(MIN_TRADE_USDT, min(MAX_TRADE_USDT, size))
        except Exception as e:
            logger.error(f'Sizing error {self.symbol_ccxt}: {e}')
            return 11.0

    async def update(self, price_feed):
        try:
            price = price_feed.prices.get(self.symbol_ws)
            vol = price_feed.volumes.get(self.symbol_ws)
            if price is None or vol is None: return

            self.price_history.append(price)
            self.vol_history.append(vol)
            if len(self.price_history) > 100: 
                self.price_history.pop(0)
                self.vol_history.pop(0)

            if self.position:
                # Dynamic Exit: TP or SL
                if price >= self.current_tp or price <= self.current_sl:
                    pnl = (price - self.buy_price) / self.buy_price
                    logger.info(f'⚔️ {self.symbol_ccxt} EXIT! Price: {price} | TP: {self.current_tp:.2f} | SL: {self.current_sl:.2f} | PNL: {pnl*100:.2f}%')
                    if pnl > 0:
                        await self.add_to_vault(self.trade_amount * pnl * 0.33)
                    self.position = False
            else:
                if len(self.price_history) >= 10:
                    drop = (self.price_history[-1] - self.price_history[-10]) / self.price_history[-10]
                    rsi, ema = self.calculate_indicators()
                    avg_vol = sum(self.vol_history[-20:]) / 20 if len(self.vol_history) >= 20 else vol
                    vol_spike = vol > avg_vol * 1.5
                    
                    if drop <= -0.01 and rsi and rsi < 35 and vol_spike:
                        if (ema and price > ema) or (rsi < 20):
                            atr = self.calculate_atr()
                            size = await self.calculate_position_size(price, atr)
                            
                            # Set Dynamic TP/SL
                            self.current_tp = price + (atr * TP_ATR_MULT) if atr > 0 else price * 1.01
                            self.current_sl = price - (atr * SL_ATR_MULT) if atr > 0 else price * 0.94
                            self.trade_amount = size
                            
                            bal = await self.exchange.fetch_balance()
                            if bal.get('USDT', {}).get('free', 0) >= size:
                                logger.info(f'⚔️ {self.symbol_ccxt} ATTACCA! Price: {price} | Size: {size:.2f} | TP: {self.current_tp:.2f} | SL: {self.current_sl:.2f}')
                                self.buy_price = price
                                self.position = True
        except Exception as e:
            logger.error(f'Errore update {self.symbol_ccxt}: {e}')

    async def add_to_vault(self, amount):
        try:
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
            logger.info(f'⚖️ {self.symbol_ccxt} HA VERSATO: +{amount:.2f}€ IN CASSAFORTE!')
        except Exception as e:
            logger.error(f'Errore vault {self.symbol_ccxt}: {e}')

async def main():
    exchange = ccxt.binance({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_API_SECRET'),
        'enableRateLimit': True,
    })
    
    feed = PriceFeed()
    bots = [LegionBot(exchange, s, SYMBOLS_CCXT[i]) for i, s in enumerate(SYMBOLS_WS)]
    
    # Init indicators (ATR)
    for bot in bots:
        await bot.init_indicators()
    
    asyncio.create_task(feed.start())
    logger.info(f'🚀 LegionManager V2 (Dynamic) avviato. {len(bots)} bot in ascolto.')

    try:
        while True:
            await asyncio.gather(*(bot.update(feed) for bot in bots))
            await asyncio.sleep(1) 
    except Exception as e:
        logger.error(f'Errore critico manager V2: {e}')
    finally:
        await exchange.close()

if __name__ == '__main__':
    asyncio.run(main())
