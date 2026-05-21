"""
Hermes Alpha Engine — Mean Reversion Strategy
Detects oversold/overbought conditions using RSI, Bollinger Bands, and stochastic
"""

import numpy as np
from .base import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion strategy: buy dips, sell rips."""

    def __init__(self, config: dict):
        super().__init__("mean_reversion", config, config["strategies"]["mean_reversion"]["weight"])
        self.conf = config["strategies"]["mean_reversion"]

    def analyze(self, pair: str, data: dict) -> dict:
        candles = data.get("ohlcv", {}).get("5m", [])
        candles_15m = data.get("ohlcv", {}).get("15m", [])
        price = data.get("current_price", 0)

        if len(candles) < 25:
            return {"signal": "HOLD", "confidence": 0, "price": price, "reason": "Insufficient data"}

        closes = np.array([c[4] for c in candles[-40:]])
        highs = np.array([c[2] for c in candles[-40:]])
        lows = np.array([c[3] for c in candles[-40:]])
        volumes = np.array([c[5] for c in candles[-40:]])

        # Bollinger Bands
        sma = np.mean(closes[-20:])
        std = np.std(closes[-20:])
        bb_dev = self.conf["bollinger_deviation"]
        bb_upper = sma + bb_dev * std
        bb_lower = sma - bb_dev * std
        bb_width = (bb_upper - bb_lower) / sma

        # RSI
        rsi = self._rsi(closes, 14)

        # Stochastic
        stoch_k, stoch_d = self._stochastic(highs, lows, closes, 14)

        # Price distance from SMA
        price_distance = (price - sma) / sma * 100

        # Volume
        avg_vol = np.mean(volumes[-20:])
        vol_ratio = volumes[-1] / avg_vol if avg_vol > 0 else 1

        # ——— BUY (OVERSOLD BOUNCE) ———
        buy_score = 0
        buy_reasons = []

        # Price below lower BB
        if price <= bb_lower:
            buy_score += 40
            buy_reasons.append("below_bb_lower")
        elif price <= sma - 1.5 * std:
            buy_score += 25
            buy_reasons.append("near_bb_lower")

        # RSI oversold
        if rsi <= self.conf["rsi_oversold"]:
            buy_score += 30
            buy_reasons.append(f"rsi_oversold({rsi:.0f})")
        elif rsi < 35:
            buy_score += 20

        # Stochastic oversold
        if stoch_k < 20:
            buy_score += 20
            buy_reasons.append("stoch_oversold")
        elif stoch_k < 30:
            buy_score += 10

        # Volume confirmation on dip
        if vol_ratio > 1.3 and price < sma:
            buy_score += 10
            buy_reasons.append("volume_on_dip")

        # BB width narrow = squeeze potential
        if bb_width < 0.03:
            buy_score += 10

        # ——— SELL (OVERBOUGHT REVERSAL) ———
        sell_score = 0
        sell_reasons = []

        if price >= bb_upper:
            sell_score += 40
            sell_reasons.append("above_bb_upper")
        elif price >= sma + 1.5 * std:
            sell_score += 25
            sell_reasons.append("near_bb_upper")

        if rsi >= self.conf["rsi_overbought"]:
            sell_score += 30
            sell_reasons.append(f"rsi_overbought({rsi:.0f})")
        elif rsi > 65:
            sell_score += 20

        if stoch_k > 80:
            sell_score += 20
            sell_reasons.append("stoch_overbought")
        elif stoch_k > 70:
            sell_score += 10

        if vol_ratio > 1.3 and price > sma:
            sell_score += 10
            sell_reasons.append("volume_on_rally")

        # 15m confirmation
        if len(candles_15m) > 5:
            closes_15m = np.array([c[4] for c in candles_15m[-10:]])
            rsi_15m = self._rsi(closes_15m, 14)
            if buy_score > 0 and rsi_15m < 40:
                buy_score += 15
                buy_reasons.append("15m_rsi_confirm")
            elif sell_score > 0 and rsi_15m > 60:
                sell_score += 15
                sell_reasons.append("15m_rsi_confirm")

        # ——— DECISION ———
        if buy_score >= 45 and buy_score > sell_score:
            confidence = min(1.0, buy_score / 90)
            sl = price * (1 - self.conf["stop_loss_pct"] / 100)
            tp = price * (1 + self.conf["profit_target_pct"] / 100)
            return {
                "signal": "BUY",
                "confidence": round(confidence, 2),
                "price": price,
                "target": round(tp, 6),
                "stop_loss": round(sl, 6),
                "reason": f"MeanRev BUY: {', '.join(buy_reasons[:3])} (score={buy_score})",
            }
        elif sell_score >= 45:
            confidence = min(1.0, sell_score / 85)
            sl = price * (1 + self.conf["stop_loss_pct"] / 100)
            tp = price * (1 - self.conf["profit_target_pct"] / 100)
            return {
                "signal": "SELL",
                "confidence": round(confidence, 2),
                "price": price,
                "target": round(tp, 6),
                "stop_loss": round(sl, 6),
                "reason": f"MeanRev SELL: {', '.join(sell_reasons[:3])} (score={sell_score})",
            }

        return {"signal": "HOLD", "confidence": 0, "price": price,
                "reason": f"No reversion (rsi={rsi:.0f}, dist={price_distance:.2f}%)"}

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

    @staticmethod
    def _stochastic(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, period: int = 14) -> tuple:
        if len(highs) < period:
            return 50, 50
        recent_high = np.max(highs[-period:])
        recent_low = np.min(lows[-period:])
        if recent_high == recent_low:
            return 50, 50
        k = (closes[-1] - recent_low) / (recent_high - recent_low) * 100
        return k, k  # Simplified: %K only
