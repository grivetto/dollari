#!/usr/bin/env python3
"""
SMART GRID BOT v2 — Con auto-SELL dopo BUY fill
"""
import ccxt, os, time, json, logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')

logging.basicConfig(filename='REALISTIC_GRID.log', level=logging.INFO,
    format='%(asctime)s - [GRID SMART] - %(message)s')

class SmartGridBot:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_API_SECRET'),
            'enableRateLimit': True,
        })
        self.pair = 'BTC/EUR'
        self.investment = 35
        self.grid_levels = 6
        self.active_buys = {}  # buy_order_id -> {'price': X, 'amount': Y}
        
    def get_balance(self):
        try:
            bal = self.exchange.fetch_balance()
            eur = bal['EUR']['free'] if 'EUR' in bal else 0
            btc = bal['BTC']['free'] if 'BTC' in bal else 0
            return eur, btc
        except Exception as e:
            logging.error(f'Balance error: {e}')
            return 0, 0
    
    def check_filled_buys(self):
        """Controlla BUY fillati e piazza SELL"""
        for buy_id, info in list(self.active_buys.items()):
            try:
                order = self.exchange.fetch_order(buy_id, self.pair)
                if order['status'] == 'closed':
                    # BUY fillato! Piazza SELL immediatamente
                    sell_price = info['target_sell']
                    amount = info['amount'] * 0.995  # meno fees
                    
                    sell_order = self.exchange.create_order(
                        self.pair, 'limit', 'sell',
                        round(amount, 6), round(sell_price, 2)
                    )
                    logging.info(f'✅ PROFIT SETUP: BUY @ {info["price"]:.0f} -> SELL @ {sell_price:.0f} (+{((sell_price/info["price"]-1)*100):.2f}%)')
                    del self.active_buys[buy_id]
            except Exception as e:
                logging.warning(f'Check filled error: {e}')
    
    def place_grid(self):
        """Piazza solo BUY iniziali""\'
        try:
            eur, btc = self.get_balance()
            if eur < self.investment:
                logging.error(f'Fondi insufficienti: €{eur:.2f} < €{self.investment}')
                return
            
            # Calcola range
            ohlcv = self.exchange.fetch_ohlcv(self.pair, '1h', limit=24)
            prices = [x[4] for x in ohlcv]
            current = prices[-1]
            volatility = (max(prices) - min(prices)) / current
            lower = current * (1 - volatility * 1.5)
            upper = current * (1 + volatility * 1.5)
            step = (upper - lower) / self.grid_levels
            eur_per_order = self.investment / (self.grid_levels / 2)
            
            # Cancella vecchi ordini
            try:
                self.exchange.cancel_all_orders(self.pair)
                logging.info('Vecchi ordini cancellati')
            except:
                pass
            
            # Solo BUY orders
            for i in range(int(self.grid_levels/2)):
                price = current - (step * (i + 1))
                amount = (eur_per_order / price) * 0.995
                target_sell = current + (step * (i + 1))  # Prezzo di vendita target
                
                try:
                    order = self.exchange.create_order(
                        self.pair, 'limit', 'buy',
                        round(amount, 6), round(price, 2)
                    )
                    self.active_buys[order['id']] = {'price': price, 'amount': amount, 'target_sell': target_sell}
                    logging.info(f'BUY piazzato: €{price:.0f} -> vendita a €{target_sell:.0f}')
                except Exception as e:
                    logging.error(f'Errore BUY: {e}')
                    
        except Exception as e:
            logging.error(f'Place grid error: {e}')
    
    def run(self):
        logging.info('🚀 SMART GRID BOT — Avviato con €35')
        self.place_grid()
        
        while True:
            time.sleep(30)  # Controlla ogni 30 secondi
            self.check_filled_buys()
            
            # Ribilancia se necessario (ogni 5 min controlla)
            # ... semplificato per ora

if __name__ == '__main__':
    bot = SmartGridBot()
    bot.run()
