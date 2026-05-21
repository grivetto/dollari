"""
Hermes Alpha Engine — Breakout Strategy
Detects breakouts from consolidation ranges with volume confirmation
"""

import numpy as np
from .base import BaseStrategy


class BreakoutStrategy(BaseStrategy):
    """Breakout trading: identifies consolidation zones and enters on breakouts."""

    def __init__(self, config: dict):
        super().__init__("breakout", config, 0.0)  # Dynamic weight
        moment_conf = config["strategies"]["momentum"]
        self.atr_multiple = moment_conf["breakout_atr_multiple"]
        self.conf_bars = moment_conf["confirmation_bars"]
        self.vol_threshold = moment_conf["volume_surge_threshold"]

    def analyze(self, pair: str, data: dict) -> dict:
        candles = data.get("ohlcv", {}).get("5m", [])
        candles_1m = data.get("ohlcv", {}).get("1m", [])
        price = data.get("current_price", 0)

        if len(candles) < 30:
            return {"signal": "HOLD", "confidence": 0, "price": price, "reason": "Insufficient data"}

        closes = np.array([c[4] for c in candles[-40:]])
        highs = np.array([c[2] for c in candles[-40:]])
        lows = np.array([c[3] for c in candles[-40:]])
        volumes = np.array([c[5] for c in candles[-40:]])

        # Identify range: last 20 candles
        range_high = np.max(highs[-20:-5])
        range_low = np.min(lows[-20:-5])
        range_width = (range_high - range_low) / range_low * 100

        # ATR
        atr = self._atr(highs, lows, closes, 14)
        atr_pct = atr / price * 100

        # Volume metrics
        avg_vol_20 = np.mean(volumes[-25:-5])
        avg_vol_5 = np.mean(volumes[-5:])
        vol_ratio = avg_vol_5 / avg_vol_20 if avg_vol_20 > 0 else 1

        # Price position relative to range
        range_position = (price - range_low) / (range_high - range_low) * 100 if range_high > range_low else 50

        # Calculate breakout threshold
        breakout_threshold = range_high + atr * self.atr_multiple
        breakdown_threshold = range_low - atr * self.atr_multiple

        # Last 3 candles behavior
        last_3_highs = highs[-3:]
        last_3_lows = lows[-3:]
        last_3_closes = closes[-3:]
        last_3_vols = volumes[-3:]

        # ——— BUY (UPTREND BREAKOUT) ———
        buy_score = 0
        buy_reasons = []

        # Price breaking above range
        if price > breakout_threshold:
            buy_score += 30
            buy_reasons.append(f"breakout_{range_width:.1f}%_range")

        # Consecutive closes above range high
        closes_above = sum(1 for c in last_3_closes if c > range_high)
        if closes_above >= self.conf_bars:
            buy_score += 20
            buy_reasons.append(f"{closes_above}_bars_confirm")

        # Volume confirmation on breakout
        if vol_ratio >= self.vol_threshold:
            buy_score += 25
            buy_reasons.append(f"vol_{vol_ratio:.1f}x")

        # Increasing volume trend
        if avg_vol_5 > avg_vol_20:
            buy_score += 10

        # Range not too wide (consolidation)
        if range_width < 8 and range_width > 1.5:
            buy_score += 10
        elif range_width >= 8:
            buy_score -= 10  # Too wide = not consolidation

        # ATR suitable
        if 0.3 < atr_pct < 3:
            buy_score += 5

        # ——— SELL (DOWNTREND BREAKDOWN) ———
        sell_score = 0
        sell_reasons = []

        if price < breakdown_threshold:
            sell_score += 30
            sell_reasons.append("breakdown")

        closes_below = sum(1 for c in last_3_closes if c < range_low)
        if closes_below >= self.conf_bars:
            sell_score += 20
            sell_reasons.append("confirm_bars")

        if vol_ratio >= self.vol_threshold:
            sell_score += 25
            sell_reasons.append("vol_breakdown")

        if avg_vol_5 > avg_vol_20:
            sell_score += 10

        # 1m acceleration check
        if len(candles_1m) > 3:
            closes_1m = np.array([c[4] for c in candles_1m[-5:]])
            vol_1m = np.array([c[5] for c in candles_1m[-5:]])
            avg_vol_1m = np.mean(vol_1m[:-1])
            if vol_1m[-1] > avg_vol_1m * 2:
                if price > breakout_threshold:
                    buy_score += 10
                    buy_reasons.append("1m_accel")
                elif price < breakdown_threshold:
                    sell_score += 10

        # ——— DECISION ———
        if buy_score >= 50 and buy_score > sell_score:
            confidence = min(1.0, buy_score / 90)
            sl = price - atr * 1.5  # Wider stop for breakouts
            tp = price + (price - range_low) * 0.5  # Target: 50% of range height
            return {
                "signal": "BUY",
                "confidence": round(confidence, 2),
                "price": price,
                "target": round(tp, 6),
                "stop_loss": round(sl, 6),
                "reason": f"Breakout BUY: {', '.join(buy_reasons[:3])} ({range_width:.1f}% range)",
            }
        elif sell_score >= 50:
            confidence = min(1.0, sell_score / 85)
            sl = price + atr * 1.5
            tp = price - (range_high - price) * 0.5
            return {
                "signal": "SELL",
                "confidence": round(confidence, 2),
                "price": price,
                "target": round(tp, 6),
                "stop_loss": round(sl, 6),
                "reason": f"Breakout SELL: {', '.join(sell_reasons[:3])}",
            }

        return {"signal": "HOLD", "confidence": 0, "price": price,
                "reason": f"No breakout (range={range_width:.1f}%, pos={range_position:.0f}%)"}

    @staticmethod
    def _atr(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, period: int = 14) -> float:
        if len(highs) < period + 1:
            return highs[-1] - lows[-1] if len(highs) > 0 else 0
        trs = np.zeros(len(highs) - 1)
        for i in range(1, len(highs)):
            trs[i - 1] = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        return np.mean(trs[-period:])
