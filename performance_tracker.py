"""
Hermes Alpha Engine — Performance Tracker + Self-Learning
Adjusts strategy weights based on real performance data
"""

import json
import time
import logging
from pathlib import Path

logger = logging.getLogger("AlphaEngine.Learning")


class PerformanceTracker:
    """
    Tracks strategy performance and dynamically adjusts weights.
    Uses exponential decay to favor recently profitable strategies.
    """

    def __init__(self, config: dict):
        self.config = config["learning"]
        self.capital_config = config["capital"]
        self.trades = []
        self.strategy_stats = {}  # name -> {wins, losses, total_pnl, avg_hold_time}
        self.pair_stats = {}  # pair -> {trades, win_rate, total_pnl}
        self.last_adjustment = 0
        self.adjustment_interval = self.config["adjustment_interval_hours"] * 3600
        self.min_trades = self.config["min_trades_for_adjustment"]
        self.weight_decay = self.config["strategy_weight_decay"]
        self.stats_file = Path(config["logging"]["stats_file"])
        self.load()

    def load(self):
        """Load persisted stats."""
        if self.stats_file.exists():
            try:
                data = json.loads(self.stats_file.read_text())
                self.strategy_stats = data.get("strategy_stats", {})
                self.pair_stats = data.get("pair_stats", {})
                logger.info(f"Loaded stats: {len(self.strategy_stats)} strategies, {len(self.pair_stats)} pairs")
            except Exception as e:
                logger.warning(f"Stats load failed: {e}")

    def save(self):
        """Persist stats to disk."""
        try:
            data = {
                "strategy_stats": self.strategy_stats,
                "pair_stats": self.pair_stats,
                "updated_at": time.time(),
            }
            self.stats_file.parent.mkdir(parents=True, exist_ok=True)
            self.stats_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.warning(f"Stats save failed: {e}")

    def record_trade(self, trade: dict):
        """Record a completed trade and update all stats."""
        strategy = trade.get("strategy", "unknown")
        pair = trade.get("pair", "unknown")
        pnl = trade.get("pnl", 0)
        win = pnl > 0

        # Strategy stats
        if strategy not in self.strategy_stats:
            self.strategy_stats[strategy] = {
                "trades": 0, "wins": 0, "losses": 0,
                "total_pnl": 0.0, "avg_win": 0.0, "avg_loss": 0.0,
                "max_win": 0.0, "max_loss": 0.0, "consecutive_losses": 0,
                "last_trade_time": time.time(),
                "weight": 0.0,
            }
        s = self.strategy_stats[strategy]
        s["trades"] += 1
        s["total_pnl"] += pnl
        s["last_trade_time"] = time.time()
        if win:
            s["wins"] += 1
            s["consecutive_losses"] = 0
            s["avg_win"] = (s["avg_win"] * (s["wins"] - 1) + pnl) / s["wins"]
            s["max_win"] = max(s["max_win"], pnl)
        else:
            s["losses"] += 1
            s["consecutive_losses"] += 1
            s["avg_loss"] = (s["avg_loss"] * (s["losses"] - 1) + abs(pnl)) / s["losses"]
            s["max_loss"] = min(s["max_loss"], pnl)

        # Pair stats
        if pair not in self.pair_stats:
            self.pair_stats[pair] = {"trades": 0, "wins": 0, "losses": 0, "total_pnl": 0.0}
        p = self.pair_stats[pair]
        p["trades"] += 1
        p["total_pnl"] += pnl
        if win:
            p["wins"] += 1
        else:
            p["losses"] += 1

        self.trades.append(trade)
        if len(self.trades) > 1000:
            self.trades = self.trades[-500:]

        self.save()

    def get_adjusted_weights(self, strategies: dict) -> dict:
        """
        Compute adjusted strategy weights based on recent performance.
        Returns {strategy_name: weight} summing to 1.0.
        """
        now = time.time()
        adjusted_weights = {}

        # Base weights from config
        base_weights = {}
        for s_name, s_obj in strategies.items():
            base_weights[s_name] = s_obj.weight

        total_base = sum(base_weights.values())
        if total_base == 0:
            return {k: 1.0 / len(strategies) for k in strategies}

        # Initial weights = normalized base
        for s_name in strategies:
            adjusted_weights[s_name] = base_weights[s_name] / total_base

        # Check if we should adjust
        elapsed = now - self.last_adjustment
        total_trades = sum(self.strategy_stats.get(s, {}).get("trades", 0) for s in strategies)

        if total_trades < self.min_trades or elapsed < self.adjustment_interval:
            return adjusted_weights

        # Calculate performance score per strategy
        scores = {}
        for s_name in strategies:
            stats = self.strategy_stats.get(s_name)
            if not stats or stats["trades"] < 2:
                scores[s_name] = 1.0  # Neutral
                continue

            win_rate = stats["wins"] / stats["trades"] if stats["trades"] > 0 else 0
            profit_factor = (
                (stats["avg_win"] * stats["wins"]) / (stats["avg_loss"] * stats["losses"])
                if stats["avg_loss"] > 0 and stats["losses"] > 0
                else 2.0 if stats["wins"] > 0 else 0.5
            )

            # Recent trades weighted more (last 10)
            recent_trades = [t for t in self.trades[-30:] if t.get("strategy") == s_name]
            recent_wins = sum(1 for t in recent_trades if t.get("pnl", 0) > 0)
            recent_win_rate = recent_wins / len(recent_trades) if recent_trades else win_rate

            # Composite score
            score = (
                win_rate * 0.3
                + min(profit_factor / 3, 1) * 0.3
                + recent_win_rate * 0.3
                + (1 - stats["consecutive_losses"] / 10) * 0.1
            )
            scores[s_name] = max(0.1, score)

        # Apply decay to weights
        for s_name in adjusted_weights:
            old_weight = adjusted_weights[s_name]
            score = scores.get(s_name, 1.0)
            # Blend old weight with score
            new_weight = old_weight * self.weight_decay + score * (1 - self.weight_decay)
            adjusted_weights[s_name] = new_weight

        # Normalize
        total = sum(adjusted_weights.values())
        if total > 0:
            for s_name in adjusted_weights:
                adjusted_weights[s_name] /= total

        # Disable strategies with too many consecutive losses
        for s_name in strategies:
            stats = self.strategy_stats.get(s_name, {})
            if stats.get("consecutive_losses", 0) >= 10:
                adjusted_weights[s_name] = 0.0
                logger.warning(f"⛔ Strategy '{s_name}' zeroed: {stats['consecutive_losses']} consecutive losses")

        # Ensure at least one strategy is active
        active = sum(1 for w in adjusted_weights.values() if w > 0)
        if active == 0:
            logger.warning("All strategies zeroed! Resetting to equal weights.")
            for s_name in adjusted_weights:
                adjusted_weights[s_name] = 1.0 / len(adjusted_weights)

        self.last_adjustment = now
        logger.info(f"Adjusted weights: {adjusted_weights}")
        return adjusted_weights

    def get_best_pair(self) -> tuple:
        """Get the best performing pair."""
        if not self.pair_stats:
            return None
        scored = []
        for pair, stats in self.pair_stats.items():
            if stats["trades"] < 3:
                continue
            wr = stats["wins"] / stats["trades"]
            avg_pnl = stats["total_pnl"] / stats["trades"]
            scored.append((wr * 0.6 + avg_pnl * 0.4, pair))
        scored.sort(reverse=True)
        return scored[0][1] if scored else None

    def get_summary(self) -> dict:
        """Get full performance summary."""
        return {
            "strategies": self.strategy_stats,
            "pairs": self.pair_stats,
            "total_trades": len(self.trades),
            "last_adjustment": self.last_adjustment,
        }
