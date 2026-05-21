"""
Hermes Alpha Engine — Main Engine
Orchestrates multi-pair analysis, strategy execution, risk management, and self-learning
"""

import json
import os
import sys
import time
import logging
import logging.handlers
import signal
from pathlib import Path
from dotenv import load_dotenv

# Load .env from denaro directory (shared API keys)
dotenv_path = Path("/home/sergio/denaro/.env")
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    load_dotenv()

from connector import ExchangeConnector
from risk_manager import RiskManager
from opportunity_scorer import OpportunityScorer
from performance_tracker import PerformanceTracker
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.volatility_scalp import VolatilityScalpStrategy
from strategies.breakout import BreakoutStrategy
from strategies.scalping import ScalpingStrategy


# ── Logging Setup ─────────────────────────────────────────────────────
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)


class AlphaEngine:
    """Main orchestration engine for Hermes Alpha trading system."""

    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = json.load(f)

        self.name = "Hermes Alpha Engine"
        self.version = self.config["version"]
        self.running = False
        self.paused = False
        self.scanning = False
        self.loop_interval = 60  # seconds between full scans
        self.last_scan_time = 0
        self.active_positions = {}
        self.max_positions = self.config["capital"]["max_open_positions"]
        self.max_correlation = self.config["capital"]["max_correlation"]
        self.reserve_ratio = self.config["capital"]["reserve_ratio"]

        # Setup logging
        self._setup_logging()

        # Initialize components
        logger = logging.getLogger("AlphaEngine")
        logger.info(f"{'='*60}")
        logger.info(f"🚀 {self.name} v{self.version} — Initializing")
        logger.info(f"{'='*60}")

        self.connector = ExchangeConnector(self.config)
        self.risk_manager = RiskManager(self.config)
        self.scorer = OpportunityScorer(self.config)
        self.learner = PerformanceTracker(self.config)

        # Initialize strategies
        self.strategies = {}
        if self.config["strategies"]["momentum"]["enabled"]:
            self.strategies["momentum"] = MomentumStrategy(self.config)
        if self.config["strategies"]["mean_reversion"]["enabled"]:
            self.strategies["mean_reversion"] = MeanReversionStrategy(self.config)
        if self.config["strategies"]["volatility_scalp"]["enabled"]:
            self.strategies["volatility_scalp"] = VolatilityScalpStrategy(self.config)
        self.strategies["breakout"] = BreakoutStrategy(self.config)
        self.strategies["scalping"] = ScalpingStrategy(self.config)

        # Grid bot coexistence
        self.grid_levels = {}
        self.coex_config = self.config.get("coexistence", {})

        logger.info(f"Loaded {len(self.strategies)} strategies: {', '.join(self.strategies.keys())}")
        logger.info(f"Monitoring {len(self.config['pairs'])} pairs: {', '.join(self.config['pairs'])}")

        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_logging(self):
        """Configure rotating file + console logging."""
        log_level = getattr(logging, self.config["logging"].get("level", "INFO"))
        log_file = log_dir / "alpha_engine.log"

        formatter = logging.Formatter(
            "%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        fh = logging.handlers.RotatingFileHandler(
            str(log_file),
            maxBytes=self.config["logging"]["max_bytes"],
            backupCount=self.config["logging"]["backup_count"],
        )
        fh.setFormatter(formatter)
        fh.setLevel(log_level)

        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S"))
        ch.setLevel(log_level)

        root_logger = logging.getLogger("AlphaEngine")
        root_logger.setLevel(log_level)
        root_logger.addHandler(fh)
        root_logger.addHandler(ch)

        self.logger = root_logger

    def _signal_handler(self, sig, frame):
        """Handle shutdown signals gracefully."""
        sig_name = signal.Signals(sig).name
        self.logger.warning(f"Received {sig_name}. Shutting down gracefully...")
        self.running = False

    def _load_grid_levels(self):
        """Load grid bot levels to avoid trading at their prices."""
        if not self.coex_config.get("respect_grid_bots", False):
            return
        levels_file = self.coex_config.get("avoid_levels_file", "logs/grid_levels.json")
        levels_path = Path(__file__).parent / levels_file
        if levels_path.exists():
            try:
                self.grid_levels = json.loads(levels_path.read_text())
                self.logger.debug(f"Loaded grid levels for {list(self.grid_levels.keys())}")
            except Exception as e:
                self.logger.warning(f"Grid levels load failed: {e}")

    def _check_grid_proximity(self, pair: str, price: float) -> bool:
        """Check if price is too close to a grid bot level."""
        if not self.coex_config.get("respect_grid_bots", False):
            return False
        levels = self.grid_levels.get(pair, [])
        min_dist = self.coex_config.get("min_distance_from_grid_pct", 3.0)
        for level in levels:
            dist = abs(price - level) / level * 100
            if dist < min_dist:
                return True
        return False

    def _fetch_all_data(self, pair: str) -> dict:
        """Fetch all market data needed for analysis."""
        result = {"pair": pair}

        try:
            # Ticker
            ticker = self.connector.fetch_ticker(pair)
            result["current_price"] = ticker.get("last", 0)
            result["volume_eur"] = ticker.get("quoteVolume", 0) or 0
            result["change_pct"] = ticker.get("percentage", 0)
        except Exception as e:
            self.logger.warning(f"Ticker failed for {pair}: {e}")
            return result

        if result["current_price"] == 0:
            return result

        # OHLCV multi-timeframe
        result["ohlcv"] = {}
        timeframes = set()
        for s in self.strategies.values():
            conf = getattr(s, "conf", {})
            for tf in conf.get("timeframes", ["5m"]):
                timeframes.add(tf)

        for tf in timeframes:
            try:
                candles = self.connector.fetch_ohlcv(pair, timeframe=tf, limit=100)
                if candles:
                    result["ohlcv"][tf] = candles
            except Exception as e:
                self.logger.debug(f"OHLCV {tf} failed for {pair}: {e}")

        # Order book
        try:
            result["orderbook"] = self.connector.fetch_order_book(pair, limit=20)
        except Exception as e:
            result["orderbook"] = {"bid_volume": 0, "ask_volume": 0, "spread_pct": 0.1}

        return result

    def _get_available_capital(self) -> float:
        """Get free EUR available for trading."""
        try:
            free_eur = self.connector.fetch_free_eur()
            self.logger.debug(f"Available capital: {free_eur:.2f}€ free EUR")
            return free_eur
        except Exception as e:
            self.logger.error(f"Failed to get available capital: {e}")
            return 0.0

    def _get_total_portfolio(self) -> float:
        """Get total portfolio value (EUR + all crypto at market prices).
        Returns 0.0 to signal 'unable to calculate' — caller should use
        last known good value."""
        try:
            free_eur = self.connector.fetch_free_eur()
            balance = self.connector.fetch_balance()
            STABLECOINS = {"USDC", "USDT", "BUSD", "DAI", "FDUSD", "TUSD", "USDP"}
            crypto_value = 0.0
            for asset, data in balance.items():
                if isinstance(data, (int, float)):
                    continue
                if asset in STABLECOINS or asset in ("EUR", "info", "free", "total", "used"):
                    continue
                total = data.get("total", 0) if isinstance(data, dict) else 0
                if total and float(total) > 0:
                    try:
                        ticker = self.connector.fetch_ticker(f"{asset}/EUR")
                        price = ticker.get("last", 0)
                        if price > 0:
                            crypto_value += float(total) * price
                    except Exception:
                        pass
            total = free_eur + crypto_value
            # Sanity check: total must be >= free_eur, otherwise API failed
            if total < free_eur * 0.95:
                self.logger.warning(f"Total portfolio {total:.2f}€ < free EUR {free_eur:.2f}€ — likely rate limited, returning last known")
                return 0.0
            self.logger.debug(f"Total portfolio: EUR={free_eur:.2f} + crypto={crypto_value:.2f} = {total:.2f}€")
            return total
        except Exception as e:
            self.logger.warning(f"Total portfolio calc failed: {e}")
            return 0.0

    def _check_pair_correlation(self, pair: str) -> bool:
        """Check if a pair is too correlated with an active position."""
        if not self.active_positions:
            return True  # No active positions = no correlation issue

        # Simple check: same base asset
        base = pair.split("/")[0]
        for pos_pair in self.active_positions:
            pos_base = pos_pair.split("/")[0]
            # Check known correlations
            high_corr_pairs = {
                "BTC": ["ETH"],
                "ETH": ["BTC"],
                "SOL": ["NEAR"],
                "NEAR": ["SOL"],
                "ADA": ["DOT"],
                "DOT": ["ADA"],
            }
            corr_group = high_corr_pairs.get(base, [])
            if pos_base in corr_group:
                self.logger.debug(f"Correlation: {pair} vs {pos_pair} — skipping")
                return False

        return True

    def _analyze_pair(self, pair: str, data: dict, strategy_weights: dict) -> list:
        """Run all strategies on a pair and collect signals."""
        signals = []

        if not data.get("current_price", 0):
            return signals

        for s_name, strategy in self.strategies.items():
            weight = strategy_weights.get(s_name, 0)
            if weight <= 0 or not strategy.enabled:
                continue

            try:
                signal = strategy.analyze(pair, data)
                if signal["signal"] != "HOLD" and signal["confidence"] >= 0.3:
                    signal["strategy"] = s_name
                    signal["strategy_weight"] = weight
                    signal["pair"] = pair
                    signals.append(signal)
                    self.logger.debug(f"{s_name} on {pair}: {signal['signal']} "
                                      f"(conf={signal['confidence']:.2f}, w={weight:.2f})")
            except Exception as e:
                self.logger.warning(f"Strategy {s_name} failed on {pair}: {e}")

        return signals

    def _select_best_opportunity(self, all_signals: list) -> list:
        """
        Score and rank all signals, select the best ones.
        Returns list of (pair, signal) ordered by quality.
        """
        scored_signals = []
        for signal in all_signals:
            score = signal["confidence"] * 0.5 + signal.get("strategy_weight", 0) * 0.3

            # Bonus for higher timeframes (more reliable)
            strat_name = signal.get("strategy", "")
            if strat_name in ("momentum", "mean_reversion"):
                score += 0.1
            elif strat_name == "breakout":
                score += 0.05

            scored_signals.append((score, signal))

        # Sort by score descending
        scored_signals.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored_signals[:self.max_positions]]

    def _check_grid_bot_conflict(self, pair: str, signal: dict) -> bool:
        """
        Check if signal conflicts with grid bot position or active orders.
        Reuse existing grid bot pairs rather than fighting them.
        """
        grid_bot_pairs = self.coex_config.get("grid_bot_pairs", [])
        if pair not in grid_bot_pairs:
            return False  # No grid bot on this pair

        return self._check_grid_proximity(pair, signal["price"])

    def _execute_signal(self, pair: str, signal: dict):
        """Execute a trading signal."""
        s_type = signal["signal"]
        price = signal["price"]
        strategy = signal["strategy"]
        confidence = signal["confidence"]

        # Check risk limits
        available = self._get_available_capital()
        total_portfolio = self._get_total_portfolio()
        if total_portfolio > 0:
            risk_check = self.risk_manager.check_all(available, total_portfolio=total_portfolio)
        else:
            risk_check = self.risk_manager.check_all(available)

        if not risk_check["can_trade"]:
            self.logger.warning(f"Risk block: circuit={risk_check['circuit_breaker']}, "
                                f"drawdown={risk_check['drawdown']:.1%}")
            return

        # Compute position size
        kelly_size = self.risk_manager.compute_kelly_size(available)
        position_eur = min(kelly_size, available * 0.9)
        min_trade = self.config["capital"]["min_alloc_per_trade"]
        max_trade = self.config["capital"]["max_alloc_per_trade"]

        if position_eur < min_trade:
            self.logger.info(f"Position size {position_eur:.2f}€ < min {min_trade}€ — skipping")
            return

        position_eur = min(position_eur, max_trade, available * 0.9)

        # Compute stop/target
        sl_pct = self.config["strategies"][strategy]["stop_loss_pct"] / 100 if strategy in self.config["strategies"] else 0.008
        tp_pct = self.config["strategies"][strategy]["profit_target_pct"] / 100 if strategy in self.config["strategies"] else 0.015

        if s_type == "BUY":
            amount = position_eur / price
            try:
                order = self.connector.create_limit_buy_order(pair, amount, price)
                if order:
                    self.active_positions[pair] = {
                        "entry_price": price,
                        "amount": amount,
                        "stop_loss": signal.get("stop_loss", price * (1 - sl_pct)),
                        "take_profit": signal.get("target", price * (1 + tp_pct)),
                        "strategy": strategy,
                        "confidence": confidence,
                        "entered_at": time.time(),
                        "order_id": order.get("id"),
                        "side": "BUY",
                    }
                    self.logger.info(f"📈 ENTRY {pair}: {amount:.6f} @ {price:.6f} ({position_eur:.2f}€) [{strategy}]")
            except Exception as e:
                self.logger.error(f"BUY execution failed on {pair}: {e}")

        elif s_type == "SELL":
            base = pair.split("/")[0]
            free_amount = self.connector.get_free_amount(base)
            if free_amount <= 0:
                self.logger.debug(f"No {base} to sell for {pair}")
                return
            # Size based on actual crypto holding, not EUR
            crypto_value = free_amount * price
            sell_kelly = self.risk_manager.compute_kelly_size(crypto_value)
            sell_eur = min(sell_kelly, crypto_value * 0.9)
            if sell_eur < min_trade:
                self.logger.info(f"Sell size {sell_eur:.2f}€ < min {min_trade}€ for {pair} ({base}: {free_amount:.6f})")
                return
            sell_eur = min(sell_eur, max_trade, crypto_value * 0.95)
            sell_amount = sell_eur / price
            try:
                order = self.connector.create_limit_sell_order(pair, sell_amount, price)
                if order:
                    self.active_positions[pair] = {
                        "entry_price": price,
                        "amount": sell_amount,
                        "stop_loss": signal.get("stop_loss", price * (1 + sl_pct)),
                        "take_profit": signal.get("target", price * (1 - tp_pct)),
                        "strategy": strategy,
                        "confidence": confidence,
                        "entered_at": time.time(),
                        "order_id": order.get("id"),
                        "side": "SELL",
                    }
                    self.logger.info(f"📉 ENTRY {pair}: {sell_amount:.6f} @ {price:.6f} ({sell_eur:.2f}€) [{strategy}]")
            except Exception as e:
                self.logger.error(f"SELL execution failed on {pair}: {e}")

    def _get_active_value(self) -> float:
        """Get total value locked in active positions."""
        total = 0.0
        for pair, pos in list(self.active_positions.items()):
            if pos["side"] == "BUY":
                total += pos["amount"] * pos["entry_price"]
            else:
                total += pos["amount"] * pos["entry_price"]
        return total

    def _monitor_positions(self):
        """Check open positions for stop loss / take profit."""
        for pair, pos in list(self.active_positions.items()):
            try:
                ticker = self.connector.fetch_ticker(pair)
                current_price = ticker.get("last", 0)
                if current_price == 0:
                    continue

                entry = pos["entry_price"]
                sl = pos["stop_loss"]
                tp = pos["take_profit"]

                if pos["side"] == "BUY":
                    # Stop loss
                    if current_price <= sl:
                        self.logger.info(f"🛑 STOP LOSS {pair}: {current_price:.6f} <= {sl:.6f}")
                        try:
                            self.connector.create_market_sell_order(pair, pos["amount"])
                            pnl = (current_price - entry) * pos["amount"]
                            self._close_position(pair, pnl, False)
                        except Exception as e:
                            self.logger.error(f"Stop loss failed: {e}")
                        continue

                    # Take profit
                    if current_price >= tp:
                        self.logger.info(f"🎯 TAKE PROFIT {pair}: {current_price:.6f} >= {tp:.6f}")
                        try:
                            self.connector.create_market_sell_order(pair, pos["amount"])
                            pnl = (current_price - entry) * pos["amount"]
                            self._close_position(pair, pnl, True)
                        except Exception as e:
                            self.logger.error(f"Take profit failed: {e}")
                        continue

                    # Trailing stop
                    trail_activation = entry * 1.005  # 0.5% above entry
                    if current_price > trail_activation:
                        new_sl = max(sl, current_price * 0.997)  # trail 0.3% below
                        if new_sl > sl:
                            pos["stop_loss"] = new_sl
                            self.logger.debug(f"Trailing stop {pair}: {sl:.6f} → {new_sl:.6f}")

                elif pos["side"] == "SELL":
                    if current_price >= sl:
                        self.logger.info(f"🛑 STOP LOSS {pair} (short): {current_price:.6f} >= {sl:.6f}")
                        try:
                            self.connector.create_market_buy_order(pair, pos["amount"])
                            pnl = (entry - current_price) * pos["amount"]
                            self._close_position(pair, pnl, False)
                        except Exception as e:
                            self.logger.error(f"Stop loss failed: {e}")
                        continue

                    if current_price <= tp:
                        self.logger.info(f"🎯 TAKE PROFIT {pair} (short): {current_price:.6f} <= {tp:.6f}")
                        try:
                            self.connector.create_market_buy_order(pair, pos["amount"])
                            pnl = (entry - current_price) * pos["amount"]
                            self._close_position(pair, pnl, True)
                        except Exception as e:
                            self.logger.error(f"Take profit failed: {e}")
                        continue

            except Exception as e:
                self.logger.warning(f"Position monitor failed for {pair}: {e}")

    def _close_position(self, pair: str, pnl: float, win: bool):
        """Close a position and record results."""
        pos = self.active_positions.pop(pair, None)
        if not pos:
            return

        strategy_name = pos.get("strategy", "unknown")

        # Record trade
        trade_record = {
            "pair": pair,
            "strategy": strategy_name,
            "side": pos.get("side", "BUY"),
            "entry_price": pos.get("entry_price", 0),
            "amount": pos.get("amount", 0),
            "pnl": round(pnl, 2),
            "win": win,
            "hold_time": time.time() - pos.get("entered_at", time.time()),
            "confidence": pos.get("confidence", 0),
        }

        self.risk_manager.record_trade({"pnl": pnl, "win": win, "pair": pair, "strategy": strategy_name})
        self.learner.record_trade(trade_record)

        if win:
            self.logger.info(f"✅ WIN {pair}: +{pnl:.2f}€ [{strategy_name}]")
        else:
            self.logger.info(f"❌ LOSS {pair}: {pnl:.2f}€ [{strategy_name}]")

    def _check_grid_conflicts(self, pair: str) -> bool:
        """Check if pair has grid bot orders at conflicting levels."""
        if not self.coex_config.get("respect_grid_bots", False):
            return False
        return pair in self.coex_config.get("grid_bot_pairs", [])

    def scan_cycle(self):
        """Complete scan cycle: analyze all pairs, find opportunities, execute."""
        if self.scanning:
            self.logger.debug("Scan already in progress, skipping")
            return
        self.scanning = True
        self.logger.info("🔍 Starting scan cycle...")
        self._load_grid_levels()

        # Get strategy weights
        strategy_weights = self.learner.get_adjusted_weights(self.strategies)

        # Get available capital
        available = self._get_available_capital()
        if available < self.config["capital"]["min_alloc_per_trade"]:
            self.logger.info(f"Only {available:.2f}€ available — waiting for funds")
            return

        # Scan all pairs
        all_signals = []
        for pair in self.config["pairs"]:
            if pair in self.active_positions:
                continue  # Already have position on this pair

            try:
                data = self._fetch_all_data(pair)
                if not data.get("current_price", 0):
                    continue

                # Grid bot conflict check
                if self._check_grid_conflicts(pair):
                    continue

                # Correlation check
                if not self._check_pair_correlation(pair):
                    continue

                # Analyze with all strategies
                signals = self._analyze_pair(pair, data, strategy_weights)
                all_signals.extend(signals)

            except Exception as e:
                self.logger.warning(f"Scan failed for {pair}: {e}")

        self.logger.info(f"Found {len(all_signals)} signals across {len(self.config['pairs'])} pairs")
        for s in all_signals:
            self.logger.info(f"  📌 Signal: {s['pair']} {s['signal']} conf={s['confidence']:.2f} strat={s.get('strategy','?')}")

        # Score and select best opportunities
        best = self._select_best_opportunity(all_signals)

        # Execute top signals
        executed = 0
        for signal in best:
            if executed >= self.max_positions - len(self.active_positions):
                break
            self._execute_signal(signal["pair"], signal)
            executed += 1

        # Monitor existing positions
        self._monitor_positions()

        # Report
        self._print_status()
        self.scanning = False

    def _print_status(self):
        """Print current status summary."""
        total_positions = len(self.active_positions)
        available = self._get_available_capital()
        summary = f"\n{'─'*50}\n"
        summary += f"📊 STATUS: {total_positions} positions | {available:.2f}€ available\n"

        # Strategy performance
        for s_name, strategy in self.strategies.items():
            perf = strategy.get_performance()
            if perf["trades"] > 0:
                summary += f"  {s_name:20s}: {perf['trades']} trades, {perf['win_rate_pct']:.0f}% WR, {perf['total_pnl']:+.2f}€\n"

        # Active positions
        for pair, pos in self.active_positions.items():
            entry = pos["entry_price"]
            sl = pos["stop_loss"]
            tp = pos["take_profit"]
            summary += f"  ⚡ {pair:10s}: {pos['side']:4s} @ {entry:.6f} | SL={sl:.6f} TP={tp:.6f}\n"

        summary += f"{'─'*50}"
        self.logger.info(summary)

    def run(self):
        """Main engine loop."""
        self.running = True
        self.logger.info("🏁 Engine started. Press Ctrl+C to stop.")

        # Initialize risk manager with total portfolio value
        try:
            total_portfolio = self._get_total_portfolio()
            self.risk_manager.initialize_capital(total_portfolio)
            self.logger.info(f"💰 Total portfolio: {total_portfolio:.2f}€")
        except Exception as e:
            self.logger.warning(f"Could not initialize capital: {e}")

        while self.running:
            try:
                now = time.time()
                if now - self.last_scan_time >= self.loop_interval:
                    self.scan_cycle()
                    self.last_scan_time = now

                time.sleep(10)  # Check every 10s

            except KeyboardInterrupt:
                self.logger.info("Shutdown requested.")
                break
            except Exception as e:
                self.logger.error(f"Engine error: {e}", exc_info=True)
                time.sleep(30)

        self.shutdown()

    def shutdown(self):
        """Graceful shutdown."""
        self.logger.info("Shutting down...")
        if self.active_positions:
            self.logger.warning(f"{len(self.active_positions)} positions still open!")

        # Save final state
        self.learner.save()
        try:
            self.connector.close()
        except Exception:
            pass
        self.logger.info("Engine stopped.")


# ── Entry Point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    config_path = os.environ.get("ALPHA_CONFIG", "config/alpha_config.json")
    if not os.path.exists(config_path):
        config_path = os.path.join(os.path.dirname(__file__), config_path)

    if not os.path.exists(config_path):
        print(f"Config not found: {config_path}")
        sys.exit(1)

    engine = AlphaEngine(config_path)
    engine.run()
