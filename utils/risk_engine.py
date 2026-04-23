import logging
from datetime import datetime

logger = logging.getLogger("RiskEngine")

class RiskManager:
    def __init__(self, 
                 max_daily_loss_pct=-2.5,
                 default_pos_size_pct=1.5,
                 max_pos_size_pct=3.0,
                 vol_multiplier_min=0.5,
                 vol_multiplier_max=1.5):
        """
        Sistema di risk management avanzato per Denaro.
        
        :param max_daily_loss_pct: Perdita massima giornaliera (% negative)
        :param default_pos_size_pct: % capitale per singolo trade
        :param max_pos_size_pct: % massima per singolo trade
        :param vol_multiplier_min: Moltiplicatore minimo in alta volatilità
        :param vol_multiplier_max: Moltiplicatore massimo in bassa volatilità
        """
        self.max_daily_loss_pct = max_daily_loss_pct
        self.default_pos_size_pct = default_pos_size_pct
        self.max_pos_size_pct = max_pos_size_pct
        self.vol_multiplier_min = vol_multiplier_min
        self.vol_multiplier_max = vol_multiplier_max
        self.daily_loss_taken = 0.0

    def calculate_size(self, total_balance, volatility=1.0, atr_price=None):
        """
        Calcola dimensione posizione con ATR adjustment.
        
        :param total_balance: Capitale totale disponibile
        :param volatility: Volatilità normalizzata (0.1 = molto volatile, 1.0 = stabile)
        :param atr_price: ATR in valore assoluto (opzionale)
        :return: Dimensione posizione in EUR
        """
        if total_balance <= 0:
            return 0.0
        
        # Base size: % del capitale
        base_size = total_balance * (self.default_pos_size_pct / 100)
        
        # ATR-based adjustment
        if atr_price and atr_price > 0:
            atr_pct = atr_price / total_balance
            atr_adj = max(0.5, min(2.0, 0.01 / atr_pct))  # Clamp 0.5x - 2x
        else:
            atr_adj = 1.0
        
        # Volatility adjustment
        vol_adj = self.vol_multiplier_max - (volatility * (self.vol_multiplier_max - self.vol_multiplier_min))
        vol_adj = max(self.vol_multiplier_min, min(self.vol_multiplier_max, vol_adj))
        
        # Calcolo finale
        adjusted_size = base_size * atr_adj * vol_adj
        
        # Limiti di sicurezza
        max_size = total_balance * (self.max_pos_size_pct / 100)
        final_size = min(adjusted_size, max_size)
        
        # Minimo Binance
        min_size = 5.0
        final_size = max(final_size, min_size)
        
        return round(final_size, 2)

    def check_daily_loss(self, current_pnl_pct):
        """
        Verifica se il trading può continuare.
        
        :param current_pnl_pct: PnL giornaliero in %
        :return: True se OK, False se bloccare
        """
        if current_pnl_pct <= self.max_daily_loss_pct:
            logger.warning(f"🚨 CIRCUIT BREAKER: Daily loss {current_pnl_pct:.2f}% >= limit {self.max_daily_loss_pct}%. Trading HALTED.")
            return False
        return True

    def get_risk_level(self, volatility):
        """Livello di rischio basato su volatilità"""
        if volatility > 0.05: return "HIGH"
        if volatility > 0.02: return "MEDIUM"
        return "LOW"

    def reset_daily(self):
        """Resetta il contatore perdite giornaliere"""
        self.daily_loss_taken = 0.0
        logger.info("✅ Daily loss counter reset")

