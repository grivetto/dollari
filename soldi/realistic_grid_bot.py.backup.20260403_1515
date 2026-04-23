#!/usr/bin/env python3
"""
REALISTIC GRID BOT — Target €3-5/giorno su €425 capitale
Strategia: Grid BTC/EUR con range calcolato su volatilità 7gg
"""

import ccxt
import os
import time
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')

logging.basicConfig(
    filename='REALISTIC_GRID.log',
    level=logging.INFO,
    format='%(asctime)s - [GRID REALISTICO] - %(message)s'
)

class RealisticGridBot:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_API_SECRET'),
            'enableRateLimit': True,
        })
        
        # Configurazione REALISTICA
        self.pair = 'BTC/EUR'
        self.investment = 90  # €90 in EUR
        self.grid_levels = 6  # 6 livelli = 3 sopra, 3 sotto
        self.profit_target = 0.003  # 0.3% per trade (realistico)
        
        self.daily_profit = 0
        self.trades_today = 0
        self.last_day = datetime.now().day
        
    def calculate_grid_range(self):
        """Calcola range basato su volatilità 24h"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.pair, '1h', limit=24)
            prices = [x[4] for x in ohlcv]
            
            current = prices[-1]
            high = max(prices)
            low = min(prices)
            volatility = (high - low) / current
            
            # Grid su ±1.5x la volatilità
            grid_span = volatility * 1.5
            lower = current * (1 - grid_span)
            upper = current * (1 + grid_span)
            
            return lower, upper, current
        except Exception as e:
            logging.error(f"Errore calcolo range: {e}")
            return None, None, None
    
    def get_balance(self):
        """Bilancio disponibile"""
        try:
            bal = self.exchange.fetch_balance()
            eur = bal['EUR']['free'] if 'EUR' in bal else 0
            btc = bal['BTC']['free'] if 'BTC' in bal else 0
            
            ticker = self.exchange.fetch_ticker(self.pair)
            btc_in_eur = btc * ticker['last']
            
            return eur, btc, btc_in_eur
        except Exception as e:
            logging.error(f"Errore bilancio: {e}")
            return 0, 0, 0
    
    def place_grid_orders(self, lower, upper, current):
        """Piazza ordini grid"""
        try:
            # Verifica bilancio prima
            bal = self.exchange.fetch_balance()
            eur_available = bal.get('EUR', {}).get('free', 0)
            
            if eur_available < self.investment:
                logging.error(f"Fondi insufficienti: €{eur_available:.2f} < €{self.investment}")
                return 0
            
            # Cancella ordini precedenti
            try:
                self.exchange.cancel_all_orders(self.pair)
                logging.info("Ordini precedenti cancellati")
            except Exception as e:
                logging.warning(f"Nessun ordine da cancellare: {e}")
            
            step = (upper - lower) / self.grid_levels
            eur_per_order = self.investment / (self.grid_levels / 2)
            
            orders_placed = 0
            
            # Buy orders sotto prezzo attuale
            for i in range(int(self.grid_levels/2)):
                price = current - (step * (i + 1))
                if price > 0:
                    amount = (eur_per_order / price) * 0.995  # -0.5% fee
                    try:
                        order = self.exchange.create_order(
                            symbol=self.pair,
                            type='limit',
                            side='buy',
                            amount=round(amount, 6),
                            price=round(price, 2)
                        )
                        logging.info(f"Ordine BUY piazzato: {self.pair} @ {price:.2f} EUR, amount: {amount:.6f}")
                        orders_placed += 1
                    except Exception as e:
                        logging.error(f"Errore ordine BUY {self.pair} @ {price}: {e}")
            
            # Sell orders sopra prezzo attuale
            for i in range(int(self.grid_levels/2)):
                price = current + (step * (i + 1))
                amount = (eur_per_order / current) * 0.995
                try:
                    order = self.exchange.create_order(
                        symbol=self.pair,
                        type='limit',
                        side='sell',
                        amount=round(amount, 6),
                        price=round(price, 2)
                    )
                    logging.info(f"Ordine SELL piazzato: {self.pair} @ {price:.2f} EUR, amount: {amount:.6f}")
                    orders_placed += 1
                except Exception as e:
                    logging.error(f"Errore ordine SELL {self.pair} @ {price}: {e}")
            
            logging.info(f"📊 Grid piazzato: {orders_placed} ordini | Range: €{lower:,.0f} - €{upper:,.0f}")
            return orders_placed
            
        except Exception as e:
            logging.error(f"Errore piazzamento grid: {e}")
            return 0
            return 0
    
    def check_and_rebalance(self):
        """Controlla se serve ribilanciare il grid"""
        try:
            current = self.exchange.fetch_ticker(self.pair)['last']
            lower, upper, _ = self.calculate_grid_range()
            
            if lower is None:
                return
            
            # Se il prezzo è fuori dal 70% del range, ribilancia
            range_70 = lower + (upper - lower) * 0.15, lower + (upper - lower) * 0.85
            
            if current < range_70[0] or current > range_70[1]:
                logging.info(f"🔄 Ribilanciamento: prezzo €{current:,.0f} fuori range")
                self.place_grid_orders(lower, upper, current)
            
        except Exception as e:
            logging.error(f"Errore check: {e}")
    
    def daily_report(self):
        """Report giornaliero"""
        now = datetime.now()
        
        if now.day != self.last_day:
            eur, btc, btc_eur = self.get_balance()
            total = eur + btc_eur
            
            logging.info(f"📈 GIORNO COMPLETATO: Profit €{self.daily_profit:.2f} | "
                        f"Trades: {self.trades_today} | "
                        f"Totale: €{total:.2f}")
            
            self.daily_profit = 0
            self.trades_today = 0
            self.last_day = now.day
    
    def run(self):
        """Loop principale"""
        logging.info("🚀 REALISTIC GRID BOT — Avviato")
        logging.info(f"💰 Investimento: €{self.investment}")
        logging.info(f"🎯 Target: €3-5/giorno (1.5-2.5% su €200)")
        
        # Setup iniziale
        lower, upper, current = self.calculate_grid_range()
        if lower:
            self.place_grid_orders(lower, upper, current)
        
        while True:
            try:
                # Check ogni 5 minuti
                time.sleep(300)
                
                # Verifica se ribilanciare
                self.check_and_rebalance()
                
                # Report giornaliero
                self.daily_report()
                
            except Exception as e:
                logging.error(f"Errore loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = RealisticGridBot()
    bot.run()
