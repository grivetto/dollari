import gc
import gc
import gc
#!/usr/bin/env python3
"""
Binance Spot Grid Trading Bot
Strategia Grid: ordini buy/sell su N livelli di prezzo
"""

import os
import time
import json
import logging
from datetime import datetime
from decimal import Decimal, ROUND_DOWN

from binance.client import Client
from binance.enums import *
from dotenv import load_dotenv

# --- CONFIGURAZIONE GRID ---
load_dotenv()

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Parametri Grid
SYMBOL = 'SOLEUR'
LOWER_BOUND = 70.0    # Prezzo minimo griglia
UPPER_BOUND = 84.0    # Prezzo massimo griglia
GRID_LEVELS = 4         # Numero di livelli griglia

# Capital allocation
INVESTMENT_PER_GRID = 0.23  # 10% del balance per grid level
TOTAL_INVESTMENT_PCT = 0.80 # 80% del balance totale

# Commissioni Binance
MAKER_FEE = 0.001   # 0.1%
TAKER_FEE = 0.001   # 0.1%

# Stop Loss
STOP_LOSS_ENABLED = True
STOP_LOSS_PCT = 0.02  # 2% sotto il lower bound

# Modalità
PAPER_TRADING = False
PAPER_BALANCE_EUR = 1000.0  # Balance test paper trading

# File di stato
STATUS_FILE = '/home/sergio/.openclaw/workspace/denaro/grid_status.json'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('grid_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GridLevel:
    """Rappresenta un livello della griglia"""
    def __init__(self, price, level_index, direction):
        self.price = price
        self.level_index = level_index
        self.direction = direction  # 'BUY' o 'SELL'
        self.order_id = None
        self.filled = False
        self.filled_price = None
        self.filled_time = None
        self.quantity = 0.0
        self.opposite_order_id = None  # ID dell'ordine opposto

class GridTradingBot:
    def __init__(self):
        self.client = None
        self.grid_levels = []
        self.active_orders = {}
        self.filled_orders = []
        self.total_trades = 0
        self.total_profit = 0.0
        self.total_fees = 0.0
        self.current_price = 0.0
        self.starting_price = 0.0
        
        # Paper trading state
        self.paper_usdt = PAPER_BALANCE_EUR if PAPER_TRADING else 0
        self.paper_btc = 0.0
        
    def init_client(self):
        """Inizializza client Binance"""
        global PAPER_BALANCE_EUR
        
        if not API_KEY or not API_SECRET:
            logger.error("API Key mancanti!")
            return False
            
        if PAPER_TRADING:
            self.client = Client(API_KEY, API_SECRET, testnet=True)
            logger.info("📝 Modalità PAPER TRADING")
        else:
            self.client = Client(API_KEY, API_SECRET)
            logger.info("💰 Modalità LIVE TRADING")
            
        try:
            self.client.ping()
            logger.info("✅ Connessione Binance OK")
            
            if PAPER_TRADING:
                self.paper_usdt = PAPER_BALANCE_EUR
                self.paper_btc = 0.1  # Simula un po' di SOL
            else:
                # Recupera balance reale
                balance = self.get_balance('EUR')
                logger.info(f"💰 Balance EUR: {balance:.2f}")
                
            return True
        except Exception as e:
            logger.error(f"Errore connessione: {e}")
            return False
    
    def get_balance(self, asset):
        """Ottieni balance asset"""
        if PAPER_TRADING:
            if asset == 'EUR':
                return self.paper_usdt
            elif asset in ['SOL', 'SOLEUR']:
                return self.paper_btc
            return 0
        try:
            b = self.client.get_asset_balance(asset=asset)
            return float(b['free']) if b else 0
        except:
            return 0
    
    def update_paper_balance(self, asset, amount):
        """Aggiorna balance paper"""
        if asset == 'EUR':
            self.paper_usdt += amount
        elif asset in ['SOL', 'SOLEUR']:
            self.paper_btc += amount
    
    def get_price(self):
        """Ottieni prezzo corrente"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=SYMBOL)
            self.current_price = float(ticker['price'])
            return self.current_price
        except Exception as e:
            logger.error(f"Errore prezzo: {e}")
            return None
    
    def round_qty(self, qty):
        """Arrotonda quantity per Binance"""
        return round(qty, 2)
    
    def round_price(self, price):
        """Arrotonda prezzo per Binance"""
        return round(price, 2)
    
    def calculate_grid_prices(self):
        """Calcola i prezzi per ogni livello della griglia"""
        step = (UPPER_BOUND - LOWER_BOUND) / (GRID_LEVELS - 1)
        prices = []
        for i in range(GRID_LEVELS):
            price = LOWER_BOUND + (step * i)
            prices.append(round(price, 2))
        return prices
    
    def initialize_grid(self):
        """Inizializza la griglia di ordini"""
        logger.info("="*60)
        logger.info("🎯 GRID TRADING BOT")
        logger.info(f"Pair: {SYMBOL}")
        logger.info(f"Range: ${LOWER_BOUND:,.2f} - ${UPPER_BOUND:,.2f}")
        logger.info(f"Levels: {GRID_LEVELS}")
        logger.info("="*60)
        
        grid_prices = self.calculate_grid_prices()
        
        # Ottieni prezzo corrente
        current_price = self.get_price()
        if not current_price:
            logger.error("Impossibile ottenere prezzo!")
            return False
        
        self.starting_price = current_price
        logger.info(f"📊 Prezzo corrente: ${current_price:,.2f}")
        logger.info(f"📍 Prezzo iniziale: ${self.starting_price:,.2f}")
        
        # Determina livello centrale
        mid_level = GRID_LEVELS // 2
        
        # Crea livelli griglia
        self.grid_levels = []
        for i, price in enumerate(grid_prices):
            # Sotto il prezzo corrente = BUY, sopra = SELL
            if price < current_price:
                direction = 'BUY'
            elif price > current_price:
                direction = 'SELL'
            else:
                direction = 'BUY'  # Default al centro
            
            level = GridLevel(price, i, direction)
            self.grid_levels.append(level)
        
        # Calcola quantity per grid
        available_usdt = self.get_balance('EUR')
        investment_per_grid = 6.0 # Fix to avoid NOTIONAL error
        qty_per_grid = investment_per_grid / current_price
        
        logger.info(f"💵 Investment per grid: ${investment_per_grid:,.2f}")
        logger.info(f"📦 Quantity per grid: {qty_per_grid:.8f} SOL")
        
        # Piazza ordini iniziali
        for level in self.grid_levels:
            level.quantity = self.round_qty(qty_per_grid)
            
            if level.direction == 'BUY' and level.price < current_price:
                order_id = self.place_order('BUY', level.price, level.quantity)
                if order_id:
                    level.order_id = order_id
                    self.active_orders[order_id] = level
                    logger.info(f"  📗 BUY grid {level.level_index}: ${level.price:,.2f} qty={level.quantity:.6f}")
                    
            elif level.direction == 'SELL' and level.price > current_price:
                # Per SELL, prima devi avere l'asset (dal BUY precedente)
                # Inizialmente piazza solo BUY, i SELL verranno creati dopo
                pass
        
        logger.info(f"\n✅ Griglia inizializzata con {len([l for l in self.grid_levels if l.order_id])} ordini attivi")
        return True
    
    def place_order(self, side, price, quantity):
        """Piazza un ordine limit"""
        try:
            if PAPER_TRADING:
                # Simula ordine paper
                order_id = f"paper_{int(time.time()*1000)}_{side}"
                
                if side == 'BUY':
                    cost = price * quantity
                    if cost > self.paper_usdt:
                        return None  # Balance insufficiente
                    self.update_paper_balance('EUR', -cost)
                    self.update_paper_balance('SOL', quantity)
                else:  # SELL
                    if quantity > self.paper_btc:
                        return None  # Balance insufficiente
                    self.update_paper_balance('EUR', price * quantity)
                    self.update_paper_balance('SOL', -quantity)
                
                logger.info(f"📝 [PAPER] {side} {quantity:.6f} @ ${price:,.2f}")
                return order_id
            else:
                order = self.client.create_order(
                    symbol=SYMBOL,
                    side=side,
                    type='LIMIT',
                    timeInForce='GTC',
                    quantity=f"{quantity:.6f}",
                    price=f"{price:.2f}"
                )
                logger.info(f"✅ {side} order #{order['orderId']}: {quantity:.6f} @ ${price:,.2f}")
                return order['orderId']
        except Exception as e:
            logger.error(f"❌ Errore {side} order: {e}")
            return None
    
    def check_orders(self):
        """Controlla se ci sono ordini eseguiti"""
        current_price = self.get_price()
        if not current_price:
            return
        
        for order_id, level in list(self.active_orders.items()):
            # Simula check ordine eseguito
            executed = False
            
            if level.direction == 'BUY' and current_price <= level.price:
                executed = True
            elif level.direction == 'SELL' and current_price >= level.price:
                executed = True
            
            if executed:
                self.handle_order_filled(level, current_price)
    
    def handle_order_filled(self, level, fill_price):
        """Gestisce ordine eseguito"""
        logger.info(f"🎯 ORDINE ESEGUITO: {level.direction} @ ${fill_price:,.2f}")
        
        # Registra trade
        self.total_trades += 1
        self.filled_orders.append({
            'time': datetime.now().isoformat(),
            'direction': level.direction,
            'price': fill_price,
            'grid_level': level.level_index,
            'quantity': level.quantity
        })
        
        # Rimuovi ordine attivo
        if level.order_id in self.active_orders:
            del self.active_orders[level.order_id]
        
        level.filled = True
        level.filled_price = fill_price
        level.filled_time = datetime.now().isoformat()
        
        # Calcola profitto (se SELL)
        if level.direction == 'SELL':
            profit_per_unit = fill_price - level.price  # Differenza tra sell e buy price
            gross_profit = profit_per_unit * level.quantity
            fee = gross_profit * MAKER_FEE
            net_profit = gross_profit - fee
            self.total_profit += net_profit
            self.total_fees += fee
            logger.info(f"  💰 Profitto netto: ${net_profit:,.4f} (fee: ${fee:,.4f})")
        
        # Piazza ordine opposto
        if level.direction == 'BUY':
            # BUY eseguito → piazza SELL al livello sopra
            sell_level_idx = level.level_index + 1
            if sell_level_idx < GRID_LEVELS:
                sell_level = self.grid_levels[sell_level_idx]
                sell_level.quantity = level.quantity  # Stessa quantità
                order_id = self.place_order('SELL', sell_level.price, sell_level.quantity)
                if order_id:
                    sell_level.order_id = order_id
                    self.active_orders[order_id] = sell_level
                    logger.info(f"  📕 Piazzato SELL @ ${sell_level.price:,.2f}")
        else:
            # SELL eseguito → piazza BUY al livello sotto
            buy_level_idx = level.level_index - 1
            if buy_level_idx >= 0:
                buy_level = self.grid_levels[buy_level_idx]
                buy_level.quantity = level.quantity
                order_id = self.place_order('BUY', buy_level.price, buy_level.quantity)
                if order_id:
                    buy_level.order_id = order_id
                    self.active_orders[order_id] = buy_level
                    logger.info(f"  📗 Piazzato BUY @ ${buy_level.price:,.2f}")
    
    def check_stop_loss(self):
        """Controlla se prezzo è sotto stop loss"""
        if not STOP_LOSS_ENABLED:
            return False
        
        stop_price = LOWER_BOUND * (1 - STOP_LOSS_PCT)
        
        if self.current_price < stop_price:
            logger.warning(f"⚠️ STOP LOSS TRIGGERED! Prezzo: ${self.current_price:,.2f} < SL: ${stop_price:,.2f}")
            
            # Cancella tutti gli ordini e vendi tutto
            self.stop_bot("STOP_LOSS")
            return True
        return False
    
    def stop_bot(self, reason="MANUAL"):
        """Ferma il bot e chiude tutte le posizioni"""
        logger.info(f"\n🛑 FERMATA BOT: {reason}")
        
        # Cancella ordini attivi (simulato in paper)
        for order_id in list(self.active_orders.keys()):
            del self.active_orders[order_id]
        
        # Vendi tutto se SOL > 0
        btc_balance = self.get_balance('SOL')
        if btc_balance > 0:
            logger.info(f"📤 Vendita {btc_balance:.6f} SOL @ ${self.current_price:,.2f}")
            self.place_order('SELL', self.current_price, btc_balance)
    
    def update_status(self):
        """Aggiorna file status per dashboard"""
        grid_prices = self.calculate_grid_prices()
        
        # Calcola stats griglia
        filled_buys = len([f for f in self.filled_orders if f['direction'] == 'BUY'])
        filled_sells = len([f for f in self.filled_orders if f['direction'] == 'SELL'])
        
        status = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'mode': 'PAPER' if PAPER_TRADING else 'LIVE',
            'symbol': SYMBOL,
            'current_price': self.current_price,
            'starting_price': self.starting_price,
            'price_change_pct': round(((self.current_price - self.starting_price) / self.starting_price) * 100, 3) if self.starting_price else 0,
            
            # Grid config
            'grid': {
                'lower_bound': LOWER_BOUND,
                'upper_bound': UPPER_BOUND,
                'levels': GRID_LEVELS,
                'grid_prices': grid_prices,
                'step_size': round((UPPER_BOUND - LOWER_BOUND) / (GRID_LEVELS - 1), 2),
            },
            
            # Status
            'status': 'STOPPED' if self.current_price < LOWER_BOUND * (1 - STOP_LOSS_PCT) else 'RUNNING',
            'stop_loss_price': round(LOWER_BOUND * (1 - STOP_LOSS_PCT), 2),
            
            # Orders
            'active_orders': len(self.active_orders),
            'filled_buys': filled_buys,
            'filled_sells': filled_sells,
            'total_trades': self.total_trades,
            
            # Profits
            'total_profit': round(self.total_profit, 4),
            'total_fees': round(self.total_fees, 4),
            'net_profit': round(self.total_profit - self.total_fees, 4),
            
            # Balance
            'balance': {
                'usdt': round(self.get_balance('EUR'), 2),
                'btc': round(self.get_balance('SOL'), 8),
                'btc_value_usdt': round(self.get_balance('SOL') * self.current_price, 2),
                'total_usdt': round(self.get_balance('EUR') + (self.get_balance('SOL') * self.current_price), 2),
            },
            
            # Orders attivi
            'orders': [
                {
                    'order_id': oid,
                    'direction': lvl.direction,
                    'price': lvl.price,
                    'quantity': lvl.quantity,
                    'level': lvl.level_index
                }
                for oid, lvl in self.active_orders.items()
            ],
            
            # Fill history
            'fills': self.filled_orders[-20:],  # Ultimi 20
            
            # Level status
            'levels': [
                {
                    'index': i,
                    'price': lvl.price,
                    'direction': lvl.direction,
                    'has_order': lvl.order_id is not None,
                    'filled': lvl.filled,
                    'is_current': abs(lvl.price - self.current_price) < (UPPER_BOUND - LOWER_BOUND) / GRID_LEVELS
                }
                for i, lvl in enumerate(self.grid_levels)
            ]
        }
        
        with open(STATUS_FILE, 'w') as f:
            json.dump(status, f, indent=2)
        
        return status
    
    def run(self):
        """Loop principale"""
        if not self.init_client():
            return
        
        if not self.initialize_grid():
            return
        
        logger.info("\n🚀 Bot avviato! Monitoraggio in corso...\n")
        
        iteration = 0
        while True:
            try:
                iteration += 1
                current_price = self.get_price()
                
                if current_price:
                    # Check stop loss
                    if self.check_stop_loss():
                        break
                    
                    # Controlla ordini
                    self.check_orders()
                    
                    # Aggiorna status ogni iterazione
                    self.update_status()
                    
                    # Log periodico
                    if iteration % 5 == 0:
                        btc = self.get_balance('SOL')
                        usdt = self.get_balance('EUR')
                        logger.info(
                            f"📊 ${current_price:,.2f} | "
                            f"Active: {len(self.active_orders)} | "
                            f"Trades: {self.total_trades} | "
                            f"Profit: ${self.total_profit:,.4f} | "
                            f"SOL: {btc:.6f} | EUR: {usdt:,.2f}"
                        )
                
                gc.collect()
            time.sleep(15)  # Check ogni 15 secondi
                
            except KeyboardInterrupt:
                logger.info("\n🛑 Bot fermato dall'utente")
                break
            except Exception as e:
                logger.error(f"Errore: {e}")
                gc.collect()
            time.sleep(30)
        
        self.update_status()
        logger.info("👋 Bot terminated")

if __name__ == "__main__":
    bot = GridTradingBot()
    bot.run()
