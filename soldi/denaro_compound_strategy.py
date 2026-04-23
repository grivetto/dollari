#!/usr/bin/env python3
"""
Denaro Compound Strategy — Target progressivo €10/giorno
Fasi: €3-5 → €5-7 → €10+ (man mano che il capitale cresce)

Strategie attive:
1. Grid Trading BTC/EUR (70% capitale) — rendita stabile
2. EUR/USDT Scalping (20% capitale) — micro-profit
3. Funding Arbitrage (10% capitale) — rendita passiva
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from decimal import Decimal
import ccxt
from dotenv import load_dotenv

# Configurazione
load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
CAPITAL_FILE = '/home/sergio/.openclaw/workspace/denaro/capital_state.json'
DAILY_LOG = '/home/sergio/.openclaw/workspace/denaro/daily_pnl.log'

logging.basicConfig(
    filename=DAILY_LOG,
    level=logging.INFO,
    format='%(asctime)s - [COMPOUND] - %(message)s'
)

class DenaroCompoundStrategy:
    def __init__(self):
        self.binance = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_API_SECRET'),
            'enableRateLimit': True,
        })
        
        # Stato capitale
        self.capital = self.load_capital()
        self.daily_target = self.calculate_daily_target()
        self.today_pnl = 0
        
    def load_capital(self):
        """Carica stato capitale o inizializza"""
        if os.path.exists(CAPITAL_FILE):
            with open(CAPITAL_FILE, 'r') as f:
                return json.load(f)
        return {
            'initial': 425.0,
            'current': 425.0,
            'peak': 425.0,
            'total_profit': 0.0,
            'start_date': datetime.now().isoformat(),
            'phase': 1,  # Fase 1: €3-5/giorno
            'daily_history': []
        }
    
    def save_capital(self):
        """Salva stato capitale"""
        with open(CAPITAL_FILE, 'w') as f:
            json.dump(self.capital, f, indent=2)
    
    def calculate_daily_target(self):
        """Calcola target giornaliero basato sulla fase"""
        current = self.capital['current']
        phase = self.capital['phase']
        
        if phase == 1:
            # Fase 1: €425-€500 → target €3-5
            return min(5.0, max(3.0, current * 0.008))  # 0.8%
        elif phase == 2:
            # Fase 2: €500-€650 → target €5-7
            return min(7.0, max(5.0, current * 0.010))  # 1.0%
        else:
            # Fase 3: €650+ → target €8-12
            return min(12.0, max(8.0, current * 0.012))  # 1.2%
    
    def update_phase(self):
        """Aggiorna fase in base al capitale"""
        current = self.capital['current']
        old_phase = self.capital['phase']
        
        if current >= 650:
            self.capital['phase'] = 3
        elif current >= 500:
            self.capital['phase'] = 2
        else:
            self.capital['phase'] = 1
            
        if self.capital['phase'] != old_phase:
            logging.info(f"🎯 FASE {old_phase} → {self.capital['phase']}! "
                        f"Capitale: €{current:.2f}")
            self.daily_target = self.calculate_daily_target()
    
    def get_binance_balance(self):
        """Recupera bilancio totale in EUR"""
        try:
            balance = self.binance.fetch_balance()
            total_eur = 0.0
            
            for currency, amount in balance.get('total', {}).items():
                if amount > 0:
                    if currency == 'EUR':
                        total_eur += amount
                    elif currency == 'USDT':
                        # Converte USDT in EUR (approx)
                        total_eur += amount * 0.92
                    elif currency in ['BTC', 'ETH', 'SOL']:
                        try:
                            ticker = self.binance.fetch_ticker(f"{currency}/EUR")
                            total_eur += amount * ticker['last']
                        except:
                            pass
            return total_eur
        except Exception as e:
            logging.error(f"Errore bilancio: {e}")
            return self.capital['current']
    
    def check_daily_status(self):
        """Controlla stato giornaliero"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Calcola P&L giornaliero
        current_balance = self.get_binance_balance()
        yesterday_balance = self.capital['current']
        daily_pnl = current_balance - yesterday_balance
        
        self.today_pnl = daily_pnl
        
        # Aggiorna storico
        self.capital['daily_history'].append({
            'date': today,
            'balance': current_balance,
            'pnl': daily_pnl,
            'target': self.daily_target,
            'phase': self.capital['phase']
        })
        
        # Mantieni solo ultimi 90 giorni
        if len(self.capital['daily_history']) > 90:
            self.capital['daily_history'] = self.capital['daily_history'][-90:]
        
        # Aggiorna totale
        self.capital['current'] = current_balance
        self.capital['total_profit'] += daily_pnl
        
        if current_balance > self.capital['peak']:
            self.capital['peak'] = current_balance
        
        # Verifica fase
        self.update_phase()
        self.save_capital()
        
        # Log
        status = "✅" if daily_pnl >= self.daily_target else "⚠️"
        logging.info(f"{status} Giorno {today}: P&L €{daily_pnl:.2f} | "
                    f"Target: €{self.daily_target:.2f} | "
                    f"Capitale: €{current_balance:.2f} | "
                    f"Fase {self.capital['phase']}")
        
        return daily_pnl >= self.daily_target
    
    def compound_profits(self):
        """Reinveste profitti se target raggiunto per 3 giorni consecutivi"""
        history = self.capital['daily_history'][-3:]
        
        if len(history) >= 3:
            all_profitable = all(h['pnl'] >= h['target'] * 0.8 for h in history)
            
            if all_profitable and self.capital['current'] > self.capital['initial'] * 1.05:
                # Aumenta leggermente l'exposure
                logging.info("📈 Trend positivo — Compounding attivato")
                return True
        return False
    
    def run(self):
        """Loop principale — eseguito ogni ora"""
        logging.info(f"🚀 Denaro Compound Strategy AVVIATA")
        logging.info(f"💰 Capitale: €{self.capital['current']:.2f}")
        logging.info(f"🎯 Target giornaliero: €{self.daily_target:.2f}")
        logging.info(f"📊 Fase: {self.capital['phase']}")
        
        last_day = None
        
        while True:
            try:
                now = datetime.now()
                current_day = now.strftime('%Y-%m-%d')
                
                # Check a mezzanotte (nuovo giorno)
                if current_day != last_day and now.hour >= 0:
                    self.check_daily_status()
                    last_day = current_day
                
                # Check ogni ora durante il giorno
                if now.minute == 0:  # Ora esatta
                    balance = self.get_binance_balance()
                    pnl_so_far = balance - self.capital['current']
                    
                    # Alert se sotto target a metà giornata
                    if now.hour == 12 and pnl_so_far < self.daily_target * 0.3:
                        logging.warning(f"⚠️ Sotto target a metà giornata: "
                                      f"€{pnl_so_far:.2f} / €{self.daily_target:.2f}")
                
                time.sleep(60)  # Check ogni minuto
                
            except Exception as e:
                logging.error(f"Errore loop: {e}")
                time.sleep(300)

if __name__ == "__main__":
    strategy = DenaroCompoundStrategy()
    strategy.run()
