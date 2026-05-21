"""
Hermes Alpha Engine — Risk Manager V2
Professional risk: Kelly sizing, dynamic stops, circuit breakers, real drawdown
"""
import json
import os
import time
import logging
from collections import deque
from pathlib import Path

logger = logging.getLogger("AlphaEngine.RiskManager")


class RiskManager:
    def __init__(self, config: dict):
        self.config = config["risk"]
        self.capital_config = config["capital"]
        self.trade_history = deque(maxlen=100)
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.daily_start_balance = None
        self.peak_balance = None
        self.initial_capital = None
        self.current_balance = 0.0
        self.circuit_breaker_active = False
        self.circuit_breaker_until = 0
        self.consecutive_losses = 0
        self.stats_file = Path(config["logging"]["stats_file"])
        self.csv_file = Path(config["logging"].get("csv_file", "logs/trades.csv"))
        self.load_stats()

    def load_stats(self):
        """Load persisted stats. On fresh start, peak_balance stays None."""
        if self.stats_file.exists():
            try:
                data = json.loads(self.stats_file.read_text())
                self.trade_history = deque(data.get("trades", []), maxlen=100)
                self.peak_balance = data.get("peak_balance", None)
                self.initial_capital = data.get("initial_capital", None)
                self.daily_pnl = data.get("daily_pnl", 0.0)
                logger.info(f"Loaded stats: {len(self.trade_history)} trades, "
                            f"peak={self.peak_balance}, initial={self.initial_capital}")
            except Exception as e:
                logger.warning(f"Stats load failed (fresh start): {e}")

    def save_stats(self):
        try:
            data = {
                "trades": list(self.trade_history),
                "daily_pnl": self.daily_pnl,
                "peak_balance": self.peak_balance,
                "initial_capital": self.initial_capital,
            }
            self.stats_file.parent.mkdir(parents=True, exist_ok=True)
            self.stats_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.warning(f"Stats save failed: {e}")

    def initialize_capital(self, total_portfolio: float):
        """Set initial capital and peak balance ONCE at engine start."""
        if self.initial_capital is None:
            self.initial_capital = total_portfolio
            self.peak_balance = total_portfolio
            self.daily_start_balance = total_portfolio
            self.current_balance = total_portfolio
            self.daily_pnl = 0.0
            self.daily_trades = 0
            logger.info(f"💰 Capital initialized: {total_portfolio:.2f}€ "
                        f"(peak={self.peak_balance:.2f}€)")
            self.save_stats()

    def update_balance(self, balance: float):
        """Update current balance and track peak."""
        self.current_balance = balance
        if self.peak_balance is None or balance > self.peak_balance:
            self.peak_balance = balance
            logger.debug(f"New peak balance: {balance:.2f}€")

        if self.daily_start_balance is None:
            self.daily_start_balance = balance
            self.daily_pnl = 0.0
            self.daily_trades = 0
        else:
            self.daily_pnl = balance - self.daily_start_balance

    def record_trade(self, trade_result: dict):
        trade_result["timestamp"] = time.time()
        self.trade_history.append(trade_result)
        self.daily_trades += 1

        if trade_result.get("pnl", 0) < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

        self._append_csv(trade_result)
        self.save_stats()

    def _append_csv(self, trade: dict):
        """Append trade to CSV log. Creates header on first write."""
        try:
            self.csv_file.parent.mkdir(parents=True, exist_ok=True)
            exists = self.csv_file.exists()
            with open(self.csv_file, "a") as f:
                if not exists:
                    f.write("timestamp,pair,strategy,side,entry_price,amount,"
                            "pnl,win,hold_time_sec,confidence\n")
                ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(trade.get("timestamp", 0)))
                f.write(f"{ts},{trade.get('pair','?')},{trade.get('strategy','?')},"
                        f"{trade.get('side','?')},{trade.get('entry_price',0):.6f},"
                        f"{trade.get('amount',0):.6f},{trade.get('pnl',0):.2f},"
                        f"{1 if trade.get('win',False) else 0},"
                        f"{trade.get('hold_time',0):.0f},"
                        f"{trade.get('confidence',0):.2f}\n")
        except Exception as e:
            logger.warning(f"CSV append failed: {e}")

    def get_monthly_summary(self) -> dict:
        """Generate monthly performance summary from CSV."""
        try:
            if not self.csv_file.exists():
                return {}
            with open(self.csv_file) as f:
                lines = f.readlines()
            if len(lines) < 2:
                return {}

            trades = []
            for line in lines[1:]:
                parts = line.strip().split(",")
                if len(parts) >= 7:
                    trades.append({
                        "ts": parts[0][:7],  # YYYY-MM
                        "pair": parts[1],
                        "strategy": parts[2],
                        "pnl": float(parts[6]),
                        "win": parts[7] == "1",
                    })

            months = {}
            for t in trades:
                m = t["ts"]
                if m not in months:
                    months[m] = {"trades": 0, "wins": 0, "losses": 0,
                                 "total_pnl": 0.0}
                months[m]["trades"] += 1
                months[m]["total_pnl"] += t["pnl"]
                if t["win"]:
                    months[m]["wins"] += 1
                else:
                    months[m]["losses"] += 1

            result = {}
            for m, data in sorted(months.items()):
                wr = data["wins"] / data["trades"] * 100 if data["trades"] else 0
                result[m] = {
                    "trades": data["trades"],
                    "wins": data["wins"],
                    "losses": data["losses"],
                    "win_rate_pct": round(wr, 1),
                    "total_pnl": round(data["total_pnl"], 2),
                }
            return result
        except Exception as e:
            logger.warning(f"Monthly summary failed: {e}")
            return {}

    def compute_kelly_size(self, available_capital: float) -> float:
        """Compute optimal position size using fractional Kelly."""
        if len(self.trade_history) < 5:
            # Conservative default: 10% of available
            return min(available_capital * 0.10, self.capital_config["max_alloc_per_trade"])
        wins = [t for t in self.trade_history if t.get("pnl", 0) > 0]
        losses = [t for t in self.trade_history if t.get("pnl", 0) <= 0]
        if not losses:
            return min(available_capital * 0.20, self.capital_config["max_alloc_per_trade"])
        win_rate = len(wins) / len(self.trade_history) if self.trade_history else 0.5
        avg_win = sum(abs(t["pnl"]) for t in wins) / len(wins) if wins else 0
        avg_loss = sum(abs(t["pnl"]) for t in losses) / len(losses) if losses else 1
        if avg_loss == 0:
            avg_loss = 1
        win_loss_ratio = avg_win / avg_loss
        kelly_pct = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        kelly_pct = max(0.02, min(kelly_pct, 0.30))
        fraction = self.config["kelly_fraction"]
        alloc_pct = kelly_pct * fraction
        raw_size = available_capital * alloc_pct
        return max(
            self.capital_config["min_alloc_per_trade"],
            min(raw_size, self.capital_config["max_alloc_per_trade"]),
        )

    def compute_dynamic_stop(self, entry_price: float, atr: float, pair: str) -> dict:
        """Compute stop loss and take profit levels per pair volatility."""
        atr_pct = atr / entry_price if entry_price else 0.005
        atr_based_stop = atr * 1.5
        price_based_stop = entry_price * 0.004  # 0.4% minimum

        stop_price = entry_price - max(atr_based_stop, price_based_stop)
        take_profit = entry_price + max(atr_based_stop * 2.0, price_based_stop * 3)
        trailing_activation = entry_price + (entry_price - stop_price) * 0.5

        return {
            "stop_loss": round(stop_price, 6),
            "take_profit": round(take_profit, 6),
            "trailing_activation": round(trailing_activation, 6),
            "atr_stop_distance": round(atr_based_stop, 6),
            "atr_pct": round(atr_pct * 100, 3),
        }

    def check_circuit_breaker(self) -> bool:
        if self.circuit_breaker_active:
            if time.time() < self.circuit_breaker_until:
                return True
            else:
                self.circuit_breaker_active = False
                logger.info("🔌 Circuit breaker reset after cooldown")

        if self.consecutive_losses >= 5:
            self.circuit_breaker_active = True
            self.circuit_breaker_until = time.time() + 1800  # 30 min
            logger.warning(f"🚨 CIRCUIT BREAKER: {self.consecutive_losses} consecutive losses")
            return True

        recent_trades = list(self.trade_history)[-self.config["circuit_breaker_trades"]:]
        if len(recent_trades) < self.config["circuit_breaker_trades"]:
            return False
        losses = [t for t in recent_trades if t.get("pnl", 0) < 0]
        if len(losses) >= self.config["circuit_breaker_trades"] * 0.75:
            loss_pct = abs(sum(t["pnl"] for t in losses)) / (self.current_balance or 1)
            if loss_pct >= self.config["circuit_breaker_loss_pct"] / 100:
                self.circuit_breaker_active = True
                self.circuit_breaker_until = time.time() + self.config["circuit_breaker_cooldown_min"] * 60
                logger.warning(f"🚨 CIRCUIT BREAKER: {len(losses)} losses in last "
                              f"{self.config['circuit_breaker_trades']} trades")
                return True
        return False

    def check_daily_limit(self) -> bool:
        if self.daily_start_balance is None or self.daily_pnl >= 0:
            return False
        loss_pct = abs(self.daily_pnl) / self.daily_start_balance
        if loss_pct >= self.config["max_daily_loss_pct"] / 100:
            logger.warning(f"⛔ Daily loss limit: {loss_pct:.1%} >= {self.config['max_daily_loss_pct']}%")
            return True
        return False

    def check_drawdown(self) -> bool:
        if self.peak_balance is None or self.peak_balance == 0:
            return False
        drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
        if drawdown >= self.config["max_drawdown_pct"] / 100:
            logger.warning(f"⛔ Max drawdown: {drawdown:.1%} >= {self.config['max_drawdown_pct']}%")
            return True
        return False

    def check_all(self, available_capital: float, total_portfolio: float = None) -> dict:
        """Check all risk limits.
        Args:
            available_capital: Free EUR for position sizing
            total_portfolio: Total portfolio value for drawdown tracking.
                If None/0, uses current peak_balance (no false drawdown from
                rate-limited API calls).
        """
        if total_portfolio is not None and total_portfolio > 0:
            self.update_balance(total_portfolio)
        return {
            "can_trade": (
                not self.check_circuit_breaker()
                and not self.check_daily_limit()
                and not self.check_drawdown()
            ),
            "circuit_breaker": self.circuit_breaker_active,
            "daily_loss": abs(self.daily_pnl / self.daily_start_balance) if self.daily_start_balance else 0,
            "drawdown": (self.peak_balance - self.current_balance) / self.peak_balance if self.peak_balance else 0,
            "kelly_size": self.compute_kelly_size(available_capital),
        }

    def _get_open_position_value(self) -> float:
        """Estimate value locked in open positions (from last trades)."""
        return 0.0

    def get_summary(self) -> dict:
        wins = [t for t in self.trade_history if t.get("pnl", 0) > 0]
        losses = [t for t in self.trade_history if t.get("pnl", 0) <= 0]
        return {
            "total_trades": len(self.trade_history),
            "win_rate": len(wins) / len(self.trade_history) * 100 if self.trade_history else 0,
            "total_pnl": sum(t.get("pnl", 0) for t in self.trade_history),
            "daily_pnl": self.daily_pnl,
            "daily_trades": self.daily_trades,
            "circuit_breaker": self.circuit_breaker_active,
            "peak_balance": self.peak_balance,
            "initial_capital": self.initial_capital,
            "consecutive_losses": self.consecutive_losses,
            "monthly_summary": self.get_monthly_summary(),
        }
