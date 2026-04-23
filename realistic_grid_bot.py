#!/usr/bin/env python3
"""
REALISTIC GRID BOT — Target €2-5/giorno
Strategia: Grid ETH/EUR con range calcolato su volatilità 7gg
"""

import ccxt
import os
import time
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/home/sergio/denaro/.env')

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
        
        self.config = self.load_optimizer_config()
        self.pair = self.config.get('pair', 'ETH/EUR')
        self.investment = self.config.get('investment', 80)
        self.grid_levels = self.config.get('grid_levels', 6)
        self.profit_target = self.config.get('profit_target', 0.005)
        self.stop_loss = self.config.get('stop_loss', 0.04)
        self.mode = self.config.get('mode', 'LEARNING')
        
        self.daily_profit = 0
        self.trades_today = 0
        self.last_day = datetime.now().day

    def load_optimizer_config(self):
        """Legge la strategia dal Cervello (Optimizer). Se non esiste, usa default."""
        config_file = '/home/sergio/.openclaw/workspace/denaro/strategy.json'
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    cfg = json.load(f)
                    logging.info(f"🧠 Strategia caricata: Modalità {cfg.get('mode', 'MANUAL')}")
                    return cfg
        except Exception as e:
            logging.error(f"⚠️ Errore lettura strategy.json: {e}. Uso default.")
        # Fallback default
        return {
            'pair': 'ETH/EUR',
            'investment': 80,
            'grid_levels': 6,
            'profit_target': 0.005,
            'stop_loss': 0.04,
            'mode': 'LEARNING'
        }
        
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
            # Verifica bilancio una sola volta
            bal = self.exchange.fetch_balance()
            eur_available = bal.get('EUR', {}).get('free', 0)
            eth_available = bal.get('ETH', {}).get('free', 0)
            
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
            # MODALITÀ CRESCENDO: Usa il 90% del capitale disponibile, riserva 20€
            budget = max(0, eur_available - 20) 
            eur_per_order = budget / (self.grid_levels / 2)
            logging.info(f"📈 Budget Dinamico aggiornato: €{budget:.2f}")
            
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
                    # Controlla se abbiamo davvero ETH per vendere
                    bal_sell = self.exchange.fetch_balance()
                    eth_bal = bal_sell.get('ETH', {}).get('free', 0)
                    
                    if eth_bal < amount:
                        logging.info(f"⏳ Salto SELL @ {price:.2f}: ETH insufficiente (ne ho {eth_bal:.5f}, servono {amount:.5f})")
                        continue

                    order = self.exchange.create_order(
                        symbol=self.pair,
                        type='limit',
                        side='sell',
                        amount=round(amount, 6),
                        price=round(price, 2)
                    )
                    logging.info(f"✅ Ordine SELL piazzato: {self.pair} @ {price:.2f} EUR")
                    orders_placed += 1
                except Exception as e:
                    # Log silenzioso per errori noti
                    pass
            
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
                time.sleep(30)  # Check ogni 30s (prima era 300s)
            except Exception as e:
                logging.error(f"Loop error: {e}")
                time.sleep(15)

if __name__ == "__main__":
    bot = RealisticGridBot()
    bot.run()
