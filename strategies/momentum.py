"""
Hermes Alpha Engine — Momentum Strategy
Detects trend momentum using EMA crossovers, MACD, and volume confirmation
"""

import numpy as np
from .base import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """Momentum-following strategy with multi-timeframe confirmation."""

    def __init__(self, config: dict):
        super().__init__("momentum", config, config["strategies"]["momentum"]["weight"])
        self.conf = config["strategies"]["momentum"]
        self.min_vol = self.conf["min_volume_eur"]
        self.timeframes = self.conf["timeframes"]

    def analyze(self, pair: str, data: dict) -> dict:
        candles_5m = data.get("ohlcv", {}).get("5m", [])
        candles_1m = data.get("ohlcv", {}).get("1m", [])
        price = data.get("current_price", 0)
        volume = data.get("volume_eur", 0)

        if len(candles_5m) < 30:
            return {"signal": "HOLD", "confidence": 0, "price": price, "reason": "Insufficient data"}

        # Volume filter
        if volume < self.min_vol:
            return {"signal": "HOLD", "confidence": 0, "price": price, "reason": f"Volume {volume:.0f} < {self.min_vol}"}

        # Adapt lookback to available data
        n_candles = min(len(candles_5m), 60)
        closes_5m = np.array([c[4] for c in candles_5m[-n_candles:]])
        volumes_5m = np.array([c[5] for c in candles_5m[-n_candles:]])
        highs_5m = np.array([c[2] for c in candles_5m[-n_candles:]])
        lows_5m = np.array([c[3] for c in candles_5m[-n_candles:]])
        # EMA calculations — adapt slow EMA period to available data
        slow_period = min(50, max(21, len(closes_5m) - 5))
        ema_fast = self._ema(closes_5m, 8)
        ema_mid = self._ema(closes_5m, 21)
        ema_slow = self._ema(closes_5m, slow_period)

        # MACD
        macd_line, signal_line, macd_hist = self._macd(closes_5m)

        # Current values
        fast_now = ema_fast[-1]
        mid_now = ema_mid[-1]
        slow_now = ema_slow[-1]
        fast_prev = ema_fast[-2] if len(ema_fast) > 1 else fast_now
        mid_prev = ema_mid[-2] if len(ema_mid) > 1 else mid_now

        # RSI
        rsi = self._rsi(closes_5m, 14)

        # Volume surge
        avg_vol = np.mean(volumes_5m[-20:-5])
        vol_ratio = volumes_5m[-1] / avg_vol if avg_vol > 0 else 1

        # Bollinger Band position
        sma = np.mean(closes_5m[-20:])
        std = np.std(closes_5m[-20:])
        bb_upper = sma + 2 * std
        bb_position = (price - sma) / std if std > 0 else 0

        # ——— BUY SIGNAL LOGIC ———
        score = 0
        reasons = []

        # Trend alignment (fast > mid > slow = strong uptrend)
        if fast_now > mid_now > slow_now:
            score += 30
            reasons.append("uptrend_3ema")
        elif fast_now > mid_now:
            score += 15
            reasons.append("uptrend_2ema")

        # Golden cross (fast crosses above mid)
        if fast_prev <= mid_prev and fast_now > mid_now:
            score += 25
            reasons.append("golden_cross")
        elif fast_now > mid_now and fast_prev <= mid_prev * 0.995:
            score += 10

        # MACD confirmation
        if macd_hist[-1] > 0 and macd_hist[-2] <= 0:
            score += 20  # MACD crossover
            reasons.append("macd_cross")
        elif macd_hist[-1] > 0 and macd_line[-1] > signal_line[-1]:
            score += 10

        # Volume confirmation
        if vol_ratio >= self.conf["volume_surge_threshold"]:
            score += 15
            reasons.append("volume_surge")

        # RSI not overbought
        if rsi < 65:
            score += 10
        if rsi > 75:
            score -= 15  # Overextended

        # Price above BB middle = bullish
        if bb_position > 0:
            score += 5

        # ——— SELL SIGNAL (bearish momentum, short opportunity) ———
        sell_score = 0
        sell_reasons = []
        if slow_now > mid_now > fast_now:
            sell_score += 30
            sell_reasons.append("downtrend")
        if mid_prev <= fast_prev and mid_now > fast_now:
            sell_score += 25
            sell_reasons.append("death_cross")
        if rsi > 70:
            sell_score += 15
            sell_reasons.append("overbought")
        if vol_ratio > 1.5 and price < sma:
            sell_score += 10

        # 1m timeframe confirmation
        if len(candles_1m) > 15:
            closes_1m = np.array([c[4] for c in candles_1m[-15:]])
            ema8_1m = self._ema(closes_1m, 8)[-1]
            if price > ema8_1m:
                score += 10
            else:
                sell_score += 10

        # ——— DECISION ———
        if score >= 40 and score > sell_score:
            confidence = min(1.0, score / 85)
            sl = price * (1 - self.conf["stop_loss_pct"] / 100)
            tp = price * (1 + self.conf["profit_target_pct"] / 100)
            return {
                "signal": "BUY",
                "confidence": round(confidence, 2),
                "price": price,
                "target": round(tp, 6),
                "stop_loss": round(sl, 6),
                "reason": f"Momentum BUY: {', '.join(reasons[:3])} (score={score})",
            }
        elif sell_score >= 40:
            confidence = min(1.0, sell_score / 80)
            sl = price * (1 + self.conf["stop_loss_pct"] / 100)
            tp = price * (1 - self.conf["profit_target_pct"] / 100)
            return {
                "signal": "SELL",
                "confidence": round(confidence, 2),
                "price": price,
                "target": round(tp, 6),
                "stop_loss": round(sl, 6),
                "reason": f"Momentum SELL: {', '.join(sell_reasons[:3])} (score={sell_score})",
            }

        return {"signal": "HOLD", "confidence": 0, "price": price, "reason": f"No clear momentum (score={score}/{sell_score})"}

    @staticmethod
    def _ema(data: np.ndarray, period: int) -> np.ndarray:
        result = np.zeros_like(data)
        result[:period] = data[:period]
        multiplier = 2 / (period + 1)
        result[period - 1] = np.mean(data[:period])
        for i in range(period, len(data)):
            result[i] = (data[i] - result[i - 1]) * multiplier + result[i - 1]
        return result

    @staticmethod
    def _macd(data: np.ndarray) -> tuple:
        ema12 = MomentumStrategy._ema(data, 12)
        ema26 = MomentumStrategy._ema(data, 26)
        macd_line = ema12 - ema26
        signal_line = MomentumStrategy._ema(macd_line, 9)
        macd_hist = macd_line - signal_line
        return macd_line, signal_line, macd_hist

    @staticmethod
    def _rsi(data: np.ndarray, period: int = 14) -> float:
        if len(data) < period + 1:
            return 50.0
        deltas = np.diff(data)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))
