"""
Hermes Alpha Engine — Volatility Scalp Strategy
Captures small price moves during high volatility using 1m candles
"""

import numpy as np
from .base import BaseStrategy


class VolatilityScalpStrategy(BaseStrategy):
    """High-frequency scalping on volatility spikes with tight stops."""

    def __init__(self, config: dict):
        super().__init__("volatility_scalp", config, config["strategies"]["volatility_scalp"]["weight"])
        self.conf = config["strategies"]["volatility_scalp"]

    def analyze(self, pair: str, data: dict) -> dict:
        candles_1m = data.get("ohlcv", {}).get("1m", [])
        candles_5m = data.get("ohlcv", {}).get("5m", [])
        price = data.get("current_price", 0)
        spread = data.get("orderbook", {}).get("spread_pct", 0.1)

        if len(candles_1m) < 10:
            return {"signal": "HOLD", "confidence": 0, "price": price, "reason": "Insufficient 1m data"}

        # Spread filter
        if spread > self.conf["spread_max_bps"] / 10000:
            return {"signal": "HOLD", "confidence": 0, "price": price,
                    "reason": f"Spread {spread*10000:.0f}bps > {self.conf['spread_max_bps']}bps"}

        closes_1m = np.array([c[4] for c in candles_1m[-20:]])
        highs_1m = np.array([c[2] for c in candles_1m[-20:]])
        lows_1m = np.array([c[3] for c in candles_1m[-20:]])
        volumes_1m = np.array([c[5] for c in candles_1m[-20:]])

        # ATR on 1m
        atr_1m = self._atr(highs_1m, lows_1m, closes_1m, 14)
        atr_pct = atr_1m / price * 100

        # ATR filter
        if atr_pct < self.conf["min_atr_pct"]:
            return {"signal": "HOLD", "confidence": 0, "price": price,
                    "reason": f"ATR {atr_pct:.2f}% < {self.conf['min_atr_pct']}%"}
        if atr_pct > self.conf["max_atr_pct"]:
            return {"signal": "HOLD", "confidence": 0, "price": price,
                    "reason": f"ATR {atr_pct:.2f}% > {self.conf['max_atr_pct']}%"}

        # Volume spike detection
        avg_vol_1m = np.mean(volumes_1m[:-5]) if len(volumes_1m) > 5 else np.mean(volumes_1m)
        vol_ratio = volumes_1m[-1] / avg_vol_1m if avg_vol_1m > 0 else 1
        recent_vol_ratio = np.mean(volumes_1m[-3:]) / avg_vol_1m if avg_vol_1m > 0 else 1

        # Price direction: last 3 candles
        price_change_3 = (closes_1m[-1] - closes_1m[-4]) / closes_1m[-4] * 100 if len(closes_1m) > 4 else 0
        price_change_1 = (closes_1m[-1] - closes_1m[-2]) / closes_1m[-2] * 100 if len(closes_1m) > 2 else 0

        # Short-term EMAs
        ema_fast = self._ema(closes_1m, 5)
        ema_slow = self._ema(closes_1m, 10)
        ema_cross = ema_fast[-1] - ema_slow[-1]

        # ——— BUY SCALP ———
        buy_score = 0
        buy_reasons = []

        # Volume confirmation
        if vol_ratio >= self.conf["volume_spike_multiplier"]:
            buy_score += 30
            buy_reasons.append(f"vol_spike_{vol_ratio:.1f}x")
        elif recent_vol_ratio >= 1.5:
            buy_score += 15
            buy_reasons.append("vol_surge")

        # Momentum on 1m
        if price_change_3 > 0.3:
            buy_score += 20
            buy_reasons.append("3m_up")
        elif price_change_1 > 0.15:
            buy_score += 10

        # EMA alignment
        if ema_cross > 0:
            buy_score += 15

        # Pullback in uptrend
        if ema_cross > 0 and price_change_1 < 0:
            buy_score += 20  # Pullback buy
            buy_reasons.append("pullback")

        # ——— SELL SCALP ———
        sell_score = 0
        sell_reasons = []

        if vol_ratio >= self.conf["volume_spike_multiplier"]:
            sell_score += 25
            sell_reasons.append("vol_spike_sell")

        if price_change_3 < -0.3:
            sell_score += 25
            sell_reasons.append("3m_down")
        elif price_change_1 < -0.15:
            sell_score += 15

        if ema_cross < 0:
            sell_score += 20

        if ema_cross < 0 and price_change_1 > 0:
            sell_score += 20  # Bounce sell
            sell_reasons.append("bounce_sell")

        # 5m context filter
        if len(candles_5m) > 5:
            closes_5m = np.array([c[4] for c in candles_5m[-10:]])
            rsi_5m = self._rsi(closes_5m, 14)
            if buy_score > 0 and rsi_5m > 70:
                buy_score -= 15  # Don't buy into 5m overbought
            if sell_score > 0 and rsi_5m < 30:
                sell_score -= 15  # Don't sell into 5m oversold

        # ——— DECISION ———
        if buy_score >= 35 and buy_score > sell_score:
            confidence = min(1.0, buy_score / 80)
            sl = price * (1 - self.conf["stop_loss_pct"] / 100)
            tp = price * (1 + self.conf["profit_target_pct"] / 100)
            return {
                "signal": "BUY",
                "confidence": round(confidence, 2),
                "price": price,
                "target": round(tp, 6),
                "stop_loss": round(sl, 6),
                "reason": f"Scalp BUY: {', '.join(buy_reasons[:2])} (score={buy_score})",
            }
        elif sell_score >= 35:
            confidence = min(1.0, sell_score / 75)
            sl = price * (1 + self.conf["stop_loss_pct"] / 100)
            tp = price * (1 - self.conf["profit_target_pct"] / 100)
            return {
                "signal": "SELL",
                "confidence": round(confidence, 2),
                "price": price,
                "target": round(tp, 6),
                "stop_loss": round(sl, 6),
                "reason": f"Scalp SELL: {', '.join(sell_reasons[:2])} (score={sell_score})",
            }

        return {"signal": "HOLD", "confidence": 0, "price": price,
                "reason": f"No setup (atr={atr_pct:.2f}%, vol={vol_ratio:.1f}x)"}

    @staticmethod
    def _atr(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, period: int = 14) -> float:
        if len(highs) < period + 1:
            return highs[-1] - lows[-1] if len(highs) > 0 else 0
        trs = np.zeros(len(highs) - 1)
        for i in range(1, len(highs)):
            trs[i - 1] = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        return np.mean(trs[-period:])

    @staticmethod
    def _ema(data: np.ndarray, period: int) -> np.ndarray:
        result = np.zeros_like(data)
        multiplier = 2 / (period + 1)
        result[period - 1] = np.mean(data[:period])
        for i in range(period, len(data)):
            result[i] = (data[i] - result[i - 1]) * multiplier + result[i - 1]
        return result

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
