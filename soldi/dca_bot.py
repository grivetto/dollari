#!/usr/bin/env python3
"""
DENARO DCA BOT — MC2
Strategia: Dollar Cost Averaging su BTC
- Compra €X ogni N ore
- Vendi quando BTC fa +1.5%
- Stop loss se scende del 3%
Budget: €40 | Target: €0.50-1/giorno
"""

import ccxt
import os
import time
import json
import logging
from datetime import datetime, timedelta

ENV_PATH = '/home/sergio/denaro/.env'
os.makedirs('/home/sergio/denaro/logs', exist_ok=True)
os.makedirs('/home/sergio/denaro/status', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [DCA] - %(message)s',
    handlers=[
        logging.FileHandler('/home/sergio/denaro/logs/dca_bot.log'),
    ]
)
logger = logging.getLogger(__name__)

CONFIG = {
    'symbol': 'BTC/EUR',
    'buy_amount_eur': 5,       # €5 per buy
    'buy_interval_hours': 2,   # Compra ogni 2 ore
    'sell_target': 0.015,      # Vendi a +1.5%
    'stop_loss': 0.03,         # Stop loss a -3%
    'max_position_eur': 30,     # Max €30 in BTC totale
    'min_trade_size': 0.0001,  # Min BTC per ordine
}

class DCABot:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_API_SECRET'),
            'enableRateLimit': True,
        })
        self.symbol = CONFIG['symbol']
        self.dca_entries = []  # List of {price, amount, time, buy_id}
        self.state_file = '/home/sergio/denaro/status/dca_state.json'
        self.total_pnl = 0
        self.last_buy = None
        self.load_state()

        logger.info("=" * 50)
        logger.info("DCA BOT — MC2 Avviato")
        logger.info(f"Pair: {self.symbol}")
        logger.info(f"Buy: EUR {CONFIG['buy_amount_eur']} ogni {CONFIG['buy_interval_hours']}h")
        logger.info(f"Sell target: +{CONFIG['sell_target']*100:.1f}%")
        logger.info(f"Stop loss: -{CONFIG['stop_loss']*100:.1f}%")
        logger.info(f"Max position: EUR {CONFIG['max_position_eur']}")
        logger.info("=" * 50)

    def load_state(self):
        try:
            with open(self.state_file) as f:
                data = json.load(f)
                self.dca_entries = data.get('dca_entries', [])
                self.last_buy = data.get('last_buy')
                self.total_pnl = data.get('total_pnl', 0)
                
                if self.dca_entries:
                    logger.info(f"Caricati {len(self.dca_entries)} entry DCA esistenti")
        except:
            self.dca_entries = []
            self.last_buy = None
            self.total_pnl = 0

    def save_state(self):
        data = {
            'dca_entries': self.dca_entries,
            'last_buy': self.last_buy,
            'total_pnl': self.total_pnl,
            'updated': datetime.now().isoformat(),
        }
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_btc_balance(self):
        try:
            bal = self.exchange.fetch_balance()
            return bal.get('BTC', {}).get('free', 0)
        except:
            return 0

    def get_eur_balance(self):
        try:
            bal = self.exchange.fetch_balance()
            return bal.get('EUR', {}).get('free', 0)
        except:
            return 0

    def get_avg_entry_price(self):
        if not self.dca_entries:
            return 0
        total_cost = sum(e['price'] * e['amount'] for e in self.dca_entries)
        total_amount = sum(e['amount'] for e in self.dca_entries)
        return total_cost / total_amount if total_amount > 0 else 0

    def should_buy(self):
        """Check if it's time to buy."""
        # Check if already at max position
        btc_balance = self.get_btc_balance()
        ticker = self.exchange.fetch_ticker(self.symbol)
        current_value = btc_balance * ticker['last']
        
        if current_value >= CONFIG['max_position_eur']:
            logger.info(f"MAX position reached: EUR {current_value:.2f} >= EUR {CONFIG['max_position_eur']}")
            return False
        
        # Check if enough time passed since last buy
        if self.last_buy:
            last_buy_time = datetime.fromisoformat(self.last_buy)
            if (datetime.now() - last_buy_time).total_seconds() < CONFIG['buy_interval_hours'] * 3600:
                return False
        
        # Check EUR balance
        eur_balance = self.get_eur_balance()
        if eur_balance < CONFIG['buy_amount_eur'] + 2:
            logger.info(f"EUR insufficienti: {eur_balance:.2f} < {CONFIG['buy_amount_eur'] + 2}")
            return False
        
        return True

    def buy(self):
        """Buy BTC with configured amount."""
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            price = ticker['last']
            
            amount = CONFIG['buy_amount_eur'] / price * 0.995  # -0.5% for fee
            
            if amount < CONFIG['min_trade_size']:
                logger.info(f"Importo troppo piccolo: {amount:.6f} BTC")
                return
            
            order = self.exchange.create_order(
                symbol=self.symbol,
                type='market',
                side='buy',
                amount=round(amount, 6),
            )
            
            filled_amount = order.get('filled', amount)
            filled_price = order.get('average', price)
            
            entry = {
                'price': filled_price,
                'amount': filled_amount,
                'time': datetime.now().isoformat(),
                'buy_id': order.get('id', ''),
            }
            self.dca_entries.append(entry)
            self.last_buy = datetime.now().isoformat()
            self.save_state()
            
            logger.info(f"BUY {filled_amount:.6f} BTC @ EUR {filled_price:.2f} (EUR {CONFIG['buy_amount_eur']})")
            logger.info(f"Posizione totale: {sum(e['amount'] for e in self.dca_entries):.6f} BTC | Avg entry: {self.get_avg_entry_price():.2f}")
            
        except Exception as e:
            logger.error(f"Errore BUY: {e}")

    def try_sell(self):
        """Check if we should take profit or stop loss."""
        if not self.dca_entries:
            return
        
        avg_price = self.get_avg_entry_price()
        if avg_price == 0:
            return
        
        btc_balance = self.get_btc_balance()
        if btc_balance <= 0:
            return
        
        ticker = self.exchange.fetch_ticker(self.symbol)
        current_price = ticker['last']
        pnl = (current_price - avg_price) / avg_price
        
        should_sell = False
        reason = ''
        
        if pnl >= CONFIG['sell_target']:
            should_sell = True
            reason = f"TP +{pnl*100:.1f}% (avg entry: EUR {avg_price:.2f})"
        elif pnl <= -CONFIG['stop_loss']:
            should_sell = True
            reason = f"SL {pnl*100:.1f}% (avg entry: EUR {avg_price:.2f})"
        
        if should_sell:
            try:
                sell_amount = btc_balance
                if sell_amount < CONFIG['min_trade_size']:
                    logger.info(f"Troppi pochi BTC da vendere: {sell_amount:.6f}")
                    return
                
                order = self.exchange.create_order(
                    symbol=self.symbol,
                    type='market',
                    side='sell',
                    amount=round(sell_amount, 6),
                )
                
                sell_price = order.get('average', current_price)
                sold_amount = order.get('filled', sell_amount)
                actual_pnl = (sell_price - avg_price) * sold_amount
                self.total_pnl += actual_pnl
                
                logger.info(f"SELL {sold_amount:.6f} BTC @ EUR {sell_price:.2f}")
                logger.info(f"PnL: EUR {actual_pnl:+.2f} | Motivo: {reason}")
                
                # Clear entries after sell
                old_entries = self.dca_entries
                self.dca_entries = []
                self.save_state()
                
            except Exception as e:
                logger.error(f"Errore SELL: {e}")

    def run(self):
        logger.info("Avvio loop principale...")
        
        cycle = 0
        while True:
            try:
                time.sleep(120)  # Check every 2 minutes
                cycle += 1
                
                # Always try to sell first (check TP/SL)
                self.try_sell()
                
                # Try to buy when needed
                if self.should_buy():
                    self.buy()
                
                # Status every 30 min
                if cycle % 15 == 0:
                    ticker = self.exchange.fetch_ticker(self.symbol)
                    avg = self.get_avg_entry_price()
                    pnl = (ticker['last'] - avg) / avg if avg > 0 else 0
                    entries = len(self.dca_entries)
                    btc = self.get_btc_balance()
                    eur = self.get_eur_balance()
                    logger.info(f"TICK #{cycle}: {entries} entry | PnL: {pnl:+.2%} | BTC: {btc:.6f} | EUR: {eur:.2f} | PnL totale: EUR {self.total_pnl:+.2f}")

            except KeyboardInterrupt:
                logger.info("Interruzione richiesta.")
                break
            except Exception as e:
                logger.error(f"Loop error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = DCABot()
    bot.run()
