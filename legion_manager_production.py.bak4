import asyncio
import ccxt.async_support as ccxt
import os, time, logging, json, fcntl, sqlite3
import pandas as pd
import pandas_ta as ta
import websockets
from datetime import datetime
from dotenv import load_dotenv
from trade_db import TradeDB

load_dotenv('/app/.env')

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [LEGION-PROD] - %(message)s',
    handlers=[logging.FileHandler('/app/legion_production.log'), logging.StreamHandler()]
)
logger = logging.getLogger('LegionProd')

VAULT_FILE = '/app/vault.json'
POSITION_DIR = '/app/positions'
EXPOSURE_FILE = '/app/global_exposure.json'
FEE_RATE = 0.001 
MAX_GLOBAL_EXPOSURE = 200.0 
MAX_CONCURRENT_POSITIONS = 6
DAILY_LOSS_LIMIT_PCT = -5.0 # Circuit Breaker at -5% daily loss
INITIAL_CAPITAL = 500.0

SYMBOLS_WS = [
    'maticusdt', 'mkrusdt', 'uniusdt', 'algousdt', 'chzusdt', 'ftmusdt',
    'galausdt', 'bchusdt', 'adausdt', 'linkusdt', 'etcusdt', 'avaxusdt',
    'nearusdt', 'xtzusdt', 'vetusdt', 'aaveusdt', 'dotusdt', 'sandusdt',
    'manausdt', 'filusdt', 'xlmusdt', 'enjusdt', 'zilusdt', 'batusdt',
    'eosusdt', 'ltcusdt', 'axsusdt', 'atomusdt'
]
SYMBOLS_CCXT = [s.upper().replace('USDT', '/USDT') for s in SYMBOLS_WS]

class ExposureGuard:
    @staticmethod
    def get_exposure():
        if not os.path.exists(EXPOSURE_FILE):
            return {'total': 0.0, 'positions': {}}
        try:
            with open(EXPOSURE_FILE, 'r') as f:
                return json.load(f)
        except: return {'total': 0.0, 'positions': {}}

    @staticmethod
    async def update_exposure(symbol, amount, action):
        def _write():
            with open(EXPOSURE_FILE, 'r+') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                data = ExposureGuard.get_exposure()
                if action == 'open':
                    data['total'] += amount
                    data['positions'][symbol] = amount
                elif action == 'close':
                    val = data['positions'].pop(symbol, 0)
                    data['total'] -= val
                json.dump(data, f)
                f.seek(0)
                f.truncate()
                fcntl.flock(f, fcntl.LOCK_UN)
        await asyncio.to_thread(_write)

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
    def __init__(self, exchange, symbol_ws, symbol_ccxt, db):
        self.exchange = exchange
        self.symbol_ws = symbol_ws
        self.symbol_ccxt = symbol_ccxt
        self.db = db
        self.position = False
        self.buy_price = 0.0
        self.qty = 0.0
        self.current_tp = 0.0
        self.current_sl = 0.0
        self.entry_time = None
        self.price_history = []
        self.vol_history = []
        self.ohlcv_data = None
        self.load_state()

    def load_state(self):
        path = os.path.join(POSITION_DIR, f'{self.symbol_ws}.json')
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    self.position = True
                    self.buy_price = data['price']
                    self.qty = data['qty']
                    self.current_tp = data['tp']
                    self.current_sl = data['sl']
                    self.entry_time = data.get('ts', time.time())
                    logger.info(f'Restored position for {self.symbol_ccxt}: {self.qty} @ {self.buy_price}')
            except Exception as e:
                logger.error(f'Error loading state {self.symbol_ws}: {e}')

    def save_state(self):
        path = os.path.join(POSITION_DIR, f'{self.symbol_ws}.json')
        data = {'price': self.buy_price, 'qty': self.qty, 'tp': self.current_tp, 'sl': self.current_sl, 'ts': self.entry_time}
        try:
            with open(path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f'Error saving state {self.symbol_ws}: {e}')

    async def init_indicators(self):
        try:
            ohlcv = await self.exchange.fetch_ohlcv(self.symbol_ccxt, timeframe='1m', limit=100)
            self.ohlcv_data = pd.DataFrame(ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
        except Exception as e:
            logger.error(f'Error seeding {self.symbol_ccxt}: {e}')

    def calculate_atr(self):
        if self.ohlcv_data is None or len(self.ohlcv_data) < 14: return 0
        atr = ta.atr(self.ohlcv_data['high'], self.ohlcv_data['low'], self.ohlcv_data['close'], length=14)
        return atr.iloc[-1] if not atr.empty else 0

    async def update(self, price_feed, risk_manager):
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
                if price >= self.current_tp or price <= self.current_sl:
                    try:
                        order = await self.exchange.create_market_sell_order(self.symbol_ccxt, self.qty)
                        sell_price = float(order['price']) if 'price' in order else price
                        
                        gross_pnl = (sell_price - self.buy_price) * self.qty
                        fees = (self.buy_price + sell_price) * self.qty * FEE_RATE
                        net_pnl = gross_pnl - fees
                        pnl_pct = (sell_price - self.buy_price) / self.buy_price - (FEE_RATE * 2)
                        
                        reason = 'take_profit' if price >= self.current_tp else 'stop_loss'
                        
                        # Save to DB
                        self.db.save_trade(
                            bot_name='Legion', symbol=self.symbol_ccxt, side='BUY',
                            entry_price=self.buy_price, exit_price=sell_price, quantity=self.qty,
                            entry_time=datetime.fromtimestamp(self.entry_time).isoformat(),
                            exit_time=datetime.now().isoformat(),
                            gross_pnl=gross_pnl, fees=fees, net_pnl=net_pnl, reason=reason
                        )

                        if net_pnl > 0:
                            await self.add_to_vault(net_pnl * 0.33)
                        
                        logger.info(f'⚔️ {self.symbol_ccxt} CLOSED! Exit: {sell_price} | Net PnL: {pnl_pct*100:.2f}% | Net Profit: {net_pnl:.2f}€')
                        
                        await ExposureGuard.update_exposure(self.symbol_ws, 0, 'close')
                        self.position = False
                        pos_path = os.path.join(POSITION_DIR, f'{self.symbol_ws}.json')
                        if os.path.exists(pos_path):
                            os.remove(pos_path)
                    except Exception as e:
                        logger.error(f'Sell Error {self.symbol_ccxt}: {e}')
            else:
                # Risk Manager Checks
                if not risk_manager.authorize_trade(self.symbol_ws, 11.0):
                    return

                if len(self.price_history) >= 10:
                    drop = (self.price_history[-1] - self.price_history[-10]) / self.price_history[-10]
                    df_temp = pd.DataFrame({'close': self.price_history})
                    rsi = ta.rsi(df_temp['close'], length=14).iloc[-1] if len(self.price_history) >= 14 else 50
                    ema = ta.ema(df_temp['close'], length=50).iloc[-1] if len(self.price_history) >= 50 else price
                    avg_vol = sum(self.vol_history[-20:]) / 20 if len(self.vol_history) >= 20 else vol
                    vol_spike = vol > avg_vol * 1.5
                    
                    if drop <= -0.01 and rsi < 35 and vol_spike and ((price > ema) or (rsi < 20)):
                        atr = self.calculate_atr()
                        if pd.isna(atr) or atr == 0: return
                        
                        sl_dist = (atr * 2.0) / price
                        risk_amount = INITIAL_CAPITAL * 0.01 
                        size_usdt = risk_amount / sl_dist if sl_dist > 0 else 11.0
                        size_usdt = max(5.0, min(50.0, size_usdt))
                        
                        try:
                            order = await self.exchange.create_market_buy_order(self.symbol_ccxt, size_usdt, params={'quoteOrderQty': size_usdt})
                            self.qty = float(order['filled']) if 'filled' in order else size_usdt / price
                            self.buy_price = float(order['price']) if 'price' in order else price
                            self.current_tp = self.buy_price + (atr * 1.5)
                            self.current_sl = self.buy_price - (atr * 2.0)
                            self.entry_time = time.time()
                            self.position = True
                            self.save_state()
                            await ExposureGuard.update_exposure(self.symbol_ws, size_usdt, 'open')
                            logger.info(f'⚔️ {self.symbol_ccxt} OPEN! Entry: {self.buy_price} | Size: {size_usdt:.2f} | TP: {self.current_tp:.2f} | SL: {self.current_sl:.2f}')
                        except Exception as e:
                            logger.error(f'Buy Error {self.symbol_ccxt}: {e}')
        except Exception as e:
            logger.error(f'Update Error {self.symbol_ccxt}: {e}')

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

class RiskManager:
    def __init__(self, db):
        self.db = db
        self.max_exposure = MAX_GLOBAL_EXPOSURE
        self.max_positions = MAX_CONCURRENT_POSITIONS
        self.daily_loss_limit = DAILY_LOSS_LIMIT_PCT

    def authorize_trade(self, symbol, amount, side='BUY'):
        # 1. Global Exposure Check
        exp = ExposureGuard.get_exposure()
        if exp['total'] + amount > self.max_exposure:
            return False
        
        # 2. Max Concurrent Positions Check
        if len(exp['positions']) >= self.max_positions:
            return False
            
        # 3. Daily PnL Circuit Breaker
        daily_pnl = self.db.get_daily_pnl()
        daily_pnl_pct = (daily_pnl / INITIAL_CAPITAL) * 100
        if daily_pnl_pct <= self.daily_loss_limit:
            logger.warning(f'⚠️ CIRCUIT BREAKER ACTIVE! Daily PnL {daily_pnl_pct:.2f}% <= {self.daily_loss_limit}%')
            return False
            
        return True

async def main():
    exchange = ccxt.binance({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_API_SECRET'),
        'enableRateLimit': True,
    })
    
    db = TradeDB('/app/trades.db')
    risk_manager = RiskManager(db)
    feed = PriceFeed()
    bots = [LegionBot(exchange, s, SYMBOLS_CCXT[i], db) for i, s in enumerate(SYMBOLS_WS)]
    
    for bot in bots:
        await bot.init_indicators()
    
    asyncio.create_task(feed.start())
    logger.info(f'🚀 LegionManager PROD (V-Brain) avviato. {len(bots)} bot in ascolto.')

    try:
        while True:
            await asyncio.gather(*(bot.update(feed, risk_manager) for bot in bots))
            await asyncio.sleep(1) 
    except Exception as e:
        logger.error(f'Errore critico manager PROD: {e}')
    finally:
        await exchange.close()

if __name__ == '__main__':
    asyncio.run(main())
