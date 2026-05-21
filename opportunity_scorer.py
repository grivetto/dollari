"""
Hermes Alpha Engine — Multi-Pair Opportunity Scorer
"""

import numpy as np


class OpportunityScorer:
    """
    Scores trading pairs on multiple dimensions to find the best opportunities.
    Composite score = weighted sum of individual factor scores.
    """

    def __init__(self, config: dict):
        self.config = config

    def compute_score(self, pair: str, data: dict) -> dict:
        """
        Compute composite opportunity score for a pair.

        data must contain:
          - 'ohlcv': { timeframe: [[timestamp, open, high, low, close, volume], ...] }
          - 'orderbook': { 'bid_volume', 'ask_volume', 'spread_pct' }
          - 'current_price': float
        """
        scores = {}
        weights = {"momentum": 0.35, "mean_reversion": 0.25, "volume": 0.20, "orderbook": 0.20}

        scores["momentum"] = self._score_momentum(data)
        scores["mean_reversion"] = self._score_mean_reversion(data)
        scores["volume"] = self._score_volume(data)
        scores["orderbook"] = self._score_orderbook(data)

        composite = sum(scores[k] * weights[k] for k in weights)
        direction = self._determine_direction(scores)

        return {
            "pair": pair,
            "composite_score": round(composite, 2),
            "direction": direction,
            "components": scores,
            "current_price": data.get("current_price", 0),
            "confidence": self._compute_confidence(scores, data),
        }

    def _score_momentum(self, data: dict) -> float:
        """Score momentum using MACD and RSI on 5m."""
        ohlcv = data.get("ohlcv", {})
        candles_5m = ohlcv.get("5m", [])
        candles_1m = ohlcv.get("1m", [])

        if len(candles_5m) < 26:
            return 0.0

        closes = np.array([c[4] for c in candles_5m[-50:]])
        volumes = np.array([c[5] for c in candles_5m[-50:]])

        # MACD
        ema12 = self._ema(closes, 12)
        ema26 = self._ema(closes, 26)
        macd = ema12[-1] - ema26[-1]
        signal = self._ema(np.array([self._ema(closes[:i+1], 12)[-1] - self._ema(closes[:i+1], 26)[-1]
                                     for i in range(25, len(closes))]), 9)

        macd_hist = macd - (signal[-1] if len(signal) > 0 else 0)

        # RSI
        rsi = self._rsi(closes, 14)

        # Price position relative to short EMA
        ema8 = self._ema(closes, 8)[-1]
        price_position = (closes[-1] - ema8) / ema8

        score = 0.0
        # MACD histogram positive = bullish momentum
        if macd_hist > 0:
            score += 30.0
        score += max(-15, min(15, macd_hist / (closes[-1] * 0.001)))  # normalize

        # RSI-based
        if 40 <= rsi <= 60:
            score += 10  # Neutral zone = potential
        elif 30 <= rsi < 40:
            score += 20  # Oversold bounce potential
        elif 60 < rsi <= 70:
            score += 15  # Bullish momentum
        elif rsi > 75:
            score -= 10  # Overextended

        # Price above EMA8 = bullish
        if price_position > 0:
            score += 15
        else:
            score -= 5

        # Volume confirmation
        avg_vol = np.mean(volumes[-20:-5]) if len(volumes) > 20 else np.mean(volumes)
        if avg_vol > 0 and volumes[-1] > avg_vol * 1.5:
            score += 15

        return max(0, min(100, score))

    def _score_mean_reversion(self, data: dict) -> float:
        """Score mean reversion potential using Bollinger Bands and RSI."""
        ohlcv = data.get("ohlcv", {})
        candles = ohlcv.get("5m", [])
        if len(candles) < 20:
            return 0.0

        closes = np.array([c[4] for c in candles[-30:]])
        price = closes[-1]

        sma = np.mean(closes)
        std = np.std(closes)
        bb_upper = sma + 2.2 * std
        bb_lower = sma - 2.2 * std

        rsi = self._rsi(closes, 14)

        score = 0.0
        if price <= bb_lower:
            score = 60 + (bb_lower - price) / std * 20  # Deep oversold
        elif price >= bb_upper:
            score = 40 + (price - bb_upper) / std * 20  # Overbought
        elif price <= bb_lower + 0.5 * std:
            score = 30  # Approaching lower band

        if rsi < 30:
            score += 20  # Strong RSI oversold
        elif rsi > 70:
            score += 10  # RSI overbought

        return max(0, min(100, score))

    def _score_volume(self, data: dict) -> float:
        """Score volume anomaly."""
        candles = data.get("ohlcv", {}).get("5m", [])
        if len(candles) < 24:
            return 0.0

        volumes = np.array([c[5] for c in candles[-24:]])
        current_vol = volumes[-1]
        avg_vol = np.mean(volumes[:-1]) if len(volumes) > 1 else current_vol

        if avg_vol < 1:
            return 0.0

        vol_ratio = current_vol / avg_vol
        min_vol_eur = self.config["strategies"]["momentum"]["min_volume_eur"]

        score = 0.0
        if vol_ratio >= 2.0 and current_vol * data.get("current_price", 1) >= min_vol_eur:
            score = 50 + min(50, (vol_ratio - 2.0) * 25)
        elif vol_ratio >= 1.5:
            score = 30 + min(30, (vol_ratio - 1.5) * 40)

        return max(0, min(100, score))

    def _score_orderbook(self, data: dict) -> float:
        """Score order book imbalance."""
        ob = data.get("orderbook", {})
        bid_vol = ob.get("bid_volume", 0)
        ask_vol = ob.get("ask_volume", 0)
        spread = ob.get("spread_pct", 0.1)

        total_vol = bid_vol + ask_vol
        if total_vol == 0:
            return 0.0

        imbalance = (bid_vol - ask_vol) / total_vol
        score = 50 + imbalance * 50  # 0-100, >50 = bullish

        # Penalize wide spreads
        if spread > 0.05:
            score -= 20

        return max(0, min(100, score))

    def _determine_direction(self, scores: dict) -> str:
        """Determine trade direction from component scores."""
        momentum = scores.get("momentum", 0)
        reversion = scores.get("mean_reversion", 0)
        volume = scores.get("volume", 0)

        # Long bias: momentum > 50 + volume confirmation
        # Short bias: strong reversion overbought
        if momentum > 50 and volume > 40:
            return "LONG"
        elif reversion > 60 and scores.get("orderbook", 50) < 40:
            return "LONG"  # Oversold bounce
        elif reversion > 70 and momentum < 30:
            return "SHORT"  # Overbought reversal
        return "NEUTRAL"

    def _compute_confidence(self, scores: dict, data: dict) -> float:
        """Compute confidence level (0-1)."""
        composite = sum(scores.values()) / max(len(scores), 1)
        volume_conf = min(1.0, self._score_volume(data) / 60)
        return min(1.0, (composite / 65) * 0.7 + volume_conf * 0.3)

    @staticmethod
    def _ema(data: np.ndarray, period: int) -> np.ndarray:
        """Exponential Moving Average."""
        if len(data) < period:
            return data
        result = np.zeros_like(data)
        result[:period] = data[:period]
        multiplier = 2 / (period + 1)
        result[period - 1] = np.mean(data[:period])
        for i in range(period, len(data)):
            result[i] = (data[i] - result[i - 1]) * multiplier + result[i - 1]
        return result

    @staticmethod
    def _rsi(data: np.ndarray, period: int = 14) -> float:
        """Relative Strength Index."""
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
