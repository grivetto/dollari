"""
Hermes Alpha Engine — Base Strategy
Abstract base class for all trading strategies
"""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger("AlphaEngine.Strategies")


class BaseStrategy(ABC):
    """Base class for all trading strategies."""

    def __init__(self, name: str, config: dict, weight: float):
        self.name = name
        self.config = config
        self.weight = weight
        self.trades_taken = 0
        self.wins = 0
        self.losses = 0
        self.total_pnl = 0.0
        self.consecutive_losses = 0
        self.max_consecutive_losses = 5
        self.enabled = True

    @abstractmethod
    def analyze(self, pair: str, data: dict) -> dict:
        """
        Analyze market data and return a signal.

        Returns:
            dict with keys:
              - 'signal': 'BUY', 'SELL', or 'HOLD'
              - 'confidence': 0.0 to 1.0
              - 'price': current price
              - 'target': target price (optional)
              - 'stop_loss': stop loss price (optional)
              - 'reason': string explanation
        """
        pass

    def record_result(self, pnl: float, win: bool):
        """Record trade result for learning."""
        self.trades_taken += 1
        self.total_pnl += pnl
        if win:
            self.wins += 1
            self.consecutive_losses = 0
        else:
            self.losses += 1
            self.consecutive_losses += 1
            if self.consecutive_losses >= self.max_consecutive_losses:
                self.enabled = False
                logger.warning(f"⛔ Strategy '{self.name}' disabled: {self.consecutive_losses} consecutive losses")

    def get_win_rate(self) -> float:
        """Get win rate."""
        if self.trades_taken == 0:
            return 0.0
        return self.wins / self.trades_taken

    def get_performance(self) -> dict:
        """Get strategy performance summary."""
        return {
            "name": self.name,
            "trades": self.trades_taken,
            "wins": self.wins,
            "losses": self.losses,
            "win_rate_pct": round(self.get_win_rate() * 100, 1),
            "total_pnl": round(self.total_pnl, 2),
            "enabled": self.enabled,
            "weight": self.weight,
        }
