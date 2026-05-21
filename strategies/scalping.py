"""
Hermes Alpha Engine — Scalping Strategy
Ultra-fast 1m scalping: order flow + tape reading + micro-structure
"""

import numpy as np
from .base import BaseStrategy


class ScalpingStrategy(BaseStrategy):
    """Tape-reading micro-scalping: 1m candle wicks, bid/ask imbalance, micro-structure."""

    def __init__(self, config: dict):
        super().__init__("scalping", config, 0.0)
        scalp_conf = config["strategies"]["volatility_scalp"]
        self.spread_max = scalp_conf["spread_max_bps"]
        self.vol_mult = scalp_conf["volume_spike_multiplier"]

    def analyze(self, pair: str, data: dict) -> dict:
        candles_1m = data.get("ohlcv", {}).get("1m", [])
        ob = data.get("orderbook", {})
        spread = ob.get("spread_pct", 0.1)
        price = data.get("current_price", 0)
        bid_vol = ob.get("bid_volume", 0)
        ask_vol = ob.get("ask_volume", 0)

        if len(candles_1m) < 5 or spread > self.spread_max / 10000:
            return {"signal": "HOLD", "confidence": 0, "price": price,
                    "reason": f"Spread {spread*10000:.0f}bps > {self.spread_max}bps" if spread > self.spread_max / 10000 else "No data"}

        closes = np.array([c[4] for c in candles_1m[-10:]])
        highs = np.array([c[2] for c in candles_1m[-10:]])
        lows = np.array([c[3] for c in candles_1m[-10:]])
        volumes = np.array([c[5] for c in candles_1m[-10:]])
        opens = np.array([c[1] for c in candles_1m[-10:]])

        # Candlestick analysis
        bodies = np.abs(closes - opens)
        upper_wicks = highs - np.maximum(closes, opens)
        lower_wicks = np.minimum(closes, opens) - lows
        total_range = highs - lows

        # Detect wick patterns
        last_body = bodies[-1]
        last_upper_wick = upper_wicks[-1]
        last_lower_wick = lower_wicks[-1]
        last_range = total_range[-1]

        # Order book imbalance
        total_ob_vol = bid_vol + ask_vol
        ob_imbalance = (bid_vol - ask_vol) / total_ob_vol if total_ob_vol > 0 else 0

        # Volume
        avg_vol = np.mean(volumes[:-1]) if len(volumes) > 1 else volumes[0]
        vol_ratio = volumes[-1] / avg_vol if avg_vol > 0 else 1

        # Price micro-momentum
        micro_trend = (closes[-1] - closes[-3]) / closes[-3] * 100 if len(closes) > 3 else 0

        # ——— BUY SETUP ———
        buy_score = 0
        buy_reasons = []

        # Long lower wick = rejection of lows
        if last_range > 0 and last_lower_wick / last_range > 0.6:
            buy_score += 25
            buy_reasons.append("hammer")
        elif last_lower_wick > last_body * 2 and last_body > 0:
            buy_score += 20
            buy_reasons.append("long_lower_wick")

        # Order book: more bids than asks = buying pressure
        if ob_imbalance > 0.3:
            buy_score += 20
            buy_reasons.append("bid_heavy")
        elif ob_imbalance > 0.15:
            buy_score += 10

        # Micro uptrend
        if 0.1 < micro_trend < 1.0:
            buy_score += 15
            buy_reasons.append("micro_up")
        elif micro_trend > 1.0:
            buy_score += 5

        # Volume on green candle
        if closes[-1] > opens[-1] and vol_ratio > 1.5:
            buy_score += 15
            buy_reasons.append("vol_green")

        # ——— SELL SETUP ———
        sell_score = 0
        sell_reasons = []

        # Long upper wick = rejection of highs
        if last_range > 0 and last_upper_wick / last_range > 0.6:
            sell_score += 25
            sell_reasons.append("shooting_star")
        elif last_upper_wick > last_body * 2 and last_body > 0:
            sell_score += 20
            sell_reasons.append("long_upper_wick")

        # Order book: more asks than bids = selling pressure
        if ob_imbalance < -0.3:
            sell_score += 20
            sell_reasons.append("ask_heavy")
        elif ob_imbalance < -0.15:
            sell_score += 10

        # Micro downtrend
        if -1.0 < micro_trend < -0.1:
            sell_score += 15
            sell_reasons.append("micro_down")
        elif micro_trend < -1.0:
            sell_score += 5

        # Volume on red candle
        if closes[-1] < opens[-1] and vol_ratio > 1.5:
            sell_score += 15
            sell_reasons.append("vol_red")

        # ——— DECISION ———
        if buy_score >= 35 and buy_score > sell_score:
            confidence = min(1.0, buy_score / 75)
            sl = price * 0.996  # 0.4% stop
            tp = price * 1.004  # 0.4% target
            return {
                "signal": "BUY",
                "confidence": round(confidence, 2),
                "price": price,
                "target": round(tp, 6),
                "stop_loss": round(sl, 6),
                "reason": f"Scalp BUY: {', '.join(buy_reasons[:2])} (imbalance={ob_imbalance:.2f})",
            }
        elif sell_score >= 35:
            confidence = min(1.0, sell_score / 70)
            sl = price * 1.004
            tp = price * 0.996
            return {
                "signal": "SELL",
                "confidence": round(confidence, 2),
                "price": price,
                "target": round(tp, 6),
                "stop_loss": round(sl, 6),
                "reason": f"Scalp SELL: {', '.join(sell_reasons[:2])} (imbalance={ob_imbalance:.2f})",
            }

        return {"signal": "HOLD", "confidence": 0, "price": price,
                "reason": f"Micro={micro_trend:.2f}%, imb={ob_imbalance:.2f}"}
