#!/usr/bin/env python3
"""
DENARO OPTIMIZER (IL CERVELLO)
Analizza le performance passate e aggiorna la strategia in autonomia.
"""
import json
import os
import logging
from datetime import datetime

STRATEGY_FILE = '/home/sergio/.openclaw/workspace/denaro/strategy.json'
TRADES_FILE = '/home/sergio/.openclaw/workspace/denaro/trades_history.json'

logger = logging.getLogger('Optimizer')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [OPTIMIZER] - %(message)s')

# Strategia di default (se non esiste ancora il file)
DEFAULT_STRATEGY = {
    "mode": "LEARNING",
    "pair": "ETH/EUR",
    "investment": 100,
    "grid_levels": 8,
    "profit_target": 0.004,
    "stop_loss": 0.04,
    "dca_amount": 5.0,
    "last_update": datetime.now().isoformat(),
    "notes": "Initial baseline."
}

class DenaroOptimizer:
    def __init__(self):
        self.strategy = self.load_strategy()
        self.trades = self.load_trades()
        
    def load_strategy(self):
        if os.path.exists(STRATEGY_FILE):
            with open(STRATEGY_FILE) as f:
                return json.load(f)
        return DEFAULT_STRATEGY

    def load_trades(self):
        if os.path.exists(TRADES_FILE):
            with open(TRADES_FILE) as f:
                return json.load(f)
        return []

    def save_strategy(self):
        self.strategy['last_update'] = datetime.now().isoformat()
        with open(STRATEGY_FILE, 'w') as f:
            json.dump(self.strategy, f, indent=2)
        logger.info(f"✅ Strategia aggiornata: Modalità {self.strategy['mode']}")

    def analyze(self):
        """Analizza i trade e decide se modificare i parametri"""
        
        # FASE 1: Se pochi dati, mantieni la rotta ma impara
        if len(self.trades) < 10:
            logger.info(f"📊 Dati insufficienti ({len(self.trades)} trade). Mantengo strategia attuale.")
            return

        # Calcolo metriche
        wins = len([t for t in self.trades if t.get('result', 0) > 0])
        losses = len(self.trades) - wins
        total_trades = len(self.trades)
        win_rate = wins / total_trades if total_trades > 0 else 0
        avg_profit = sum(t.get('result', 0) for t in self.trades) / total_trades

        logger.info(f"📈 Analisi: WinRate {win_rate*100:.1f}% | Avg Profit: {avg_profit:.4f}€")

        # FASE 2: Logica decisionale ADATTIVA
        
        # CASO A: Win Rate basso (< 40%) -> La strategia è troppo aggressiva
        if win_rate < 0.40:
            logger.warning("⚠️ Win Rate basso. Allargo la griglia per trade più sicuri.")
            self.strategy['grid_levels'] = max(4, self.strategy['grid_levels'] - 2) # Meno ordini
            self.strategy['profit_target'] = round(self.strategy['profit_target'] * 1.5, 4) # Target più alto
            self.strategy['mode'] = "DEFENSIVE"
        
        # CASO B: Win Rate alto (> 70%) ma profitto basso -> Troppo pochi trade
        elif win_rate > 0.70 and avg_profit < 0.50:
            logger.info("🎯 Win Rate alto ma pochi trade. Stringo la griglia per scalping.")
            self.strategy['grid_levels'] = min(12, self.strategy['grid_levels'] + 2) # Più ordini
            self.strategy['profit_target'] = round(self.strategy['profit_target'] * 0.8, 4) # Target più basso
            self.strategy['mode'] = "AGGRESSIVE"

        # CASO C: Perdita massiccia -> Stop emergency
        if any(t.get('result', 0) < -10 for t in self.trades[-5:]):
             logger.error("🚨 Rilevata perdita anomala. Attivo modalità sicurezza.")
             self.strategy['investment'] = max(20, self.strategy['investment'] * 0.8)
             self.strategy['mode'] = "CRISIS"

        self.save_strategy()

    def report(self):
        """Report breve dello stato del cervello"""
        print(f"--- CERVELLO DENARO ---")
        print(f"Modalità: {self.strategy['mode']}")
        print(f"Investimento: €{self.strategy['investment']}")
        print(f"Livelli Grid: {self.strategy['grid_levels']}")
        print(f"Profit Target: {self.strategy['profit_target']*100}%")

if __name__ == "__main__":
    brain = DenaroOptimizer()
    brain.analyze()
    brain.report()
