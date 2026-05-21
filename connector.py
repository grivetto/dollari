"""
Hermes Alpha Engine — Exchange Connector
Robust ccxt wrapper with auto-reconnect, rate limiting, error classification
"""

import os
import time
import logging
import ccxt
import ccxt.pro as ccxt_pro
from dotenv import load_dotenv
from typing import Optional

logger = logging.getLogger("AlphaEngine.Connector")


class ExchangeConnector:
    """Thread-safe exchange connector with automatic reconnect and error classification."""

    EXCHANGE_ERRORS = {
        "ratelimit": "RATE_LIMIT",
        "bad_request": "BAD_REQUEST",
        "insufficient_funds": "INSUFFICIENT_FUNDS",
        "bad_symbol": "BAD_SYMBOL",
        "network": "NETWORK",
        "timeout": "TIMEOUT",
        "maintenance": "MAINTENANCE",
        "unknown": "UNKNOWN",
    }

    def __init__(self, config: dict):
        load_dotenv()
        self.config = config
        self.name = config["exchange"]["name"]
        self.sandbox = config["exchange"].get("sandbox", False)

        self.api_key = os.getenv("BINANCE_API_KEY") or os.getenv("BINANCE_SECRET_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET") or os.getenv("BINANCE_SECRET")

        if not self.api_key or not self.api_secret:
            raise ValueError("API keys not found in environment! Check .env")

        self.exchange = self._create_exchange()
        self.pro_exchange = self._create_pro_exchange()
        self.last_request = 0.0
        self.min_interval = 60.0 / config["exchange"]["rate_limit"]
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        self.reconnect_delay = 5

    def _create_exchange(self):
        exchange_class = getattr(ccxt, self.name)
        exchange = exchange_class({
            "apiKey": self.api_key,
            "secret": self.api_secret,
            "enableRateLimit": True,
            "timeout": 30000,  # 30s timeout per request
            "options": {"defaultType": "spot"},
        })
        if self.sandbox:
            exchange.set_sandbox_mode(True)
        return exchange

    def _create_pro_exchange(self):
        exchange_class = getattr(ccxt_pro, self.name)
        exchange = exchange_class({
            "apiKey": self.api_key,
            "secret": self.api_secret,
            "enableRateLimit": True,
            "timeout": 30000,  # 30s timeout per request
            "options": {"defaultType": "spot"},
        })
        if self.sandbox:
            exchange.set_sandbox_mode(True)
        return exchange

    def _rate_limit(self):
        """Ensure we don't exceed the API rate limit."""
        elapsed = time.time() - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

    def _classify_error(self, error: Exception) -> str:
        """Classify an exception into an error category."""
        err_str = str(error).lower()
        if any(w in err_str for w in ["rate limit", "too many requests", "429"]):
            return self.EXCHANGE_ERRORS["ratelimit"]
        elif any(w in err_str for w in ["insufficient balance", "insufficient funds", "account has insufficient"]):
            return self.EXCHANGE_ERRORS["insufficient_funds"]
        elif any(w in err_str for w in ["bad request", "invalid symbol", "invalid order"]):
            return self.EXCHANGE_ERRORS["bad_request"]
        elif any(w in err_str for w in ["symbol not found", "does not exist"]):
            return self.EXCHANGE_ERRORS["bad_symbol"]
        elif any(w in err_str for w in ["timeout", "timed out", "econnrefused", "econnreset", "connection"]):
            return self.EXCHANGE_ERRORS["network"]
        elif any(w in err_str for w in ["maintenance", "offline", "under maintenance"]):
            return self.EXCHANGE_ERRORS["maintenance"]
        return self.EXCHANGE_ERRORS["unknown"]

    def _handle_error(self, error: Exception, context: str = "") -> Optional[dict]:
        """Handle exchange error, return None if retryable."""
        category = self._classify_error(error)
        self.consecutive_errors += 1

        logger.warning(f"[{category}] {context}: {error}")

        if category == self.EXCHANGE_ERRORS["ratelimit"]:
            time.sleep(10)
            return None
        elif category == self.EXCHANGE_ERRORS["network"]:
            time.sleep(self.reconnect_delay)
            self.reconnect_delay = min(self.reconnect_delay * 2, 60)
            return None
        elif category == self.EXCHANGE_ERRORS["maintenance"]:
            time.sleep(120)
            return None
        elif category == self.EXCHANGE_ERRORS["insufficient_funds"]:
            logger.error(f"Insufficient funds: {error}")
            raise error  # Not retryable
        elif category == self.EXCHANGE_ERRORS["bad_request"]:
            logger.error(f"Bad request: {error}")
            raise error  # Not retryable

        # Unknown — check consecutive errors
        if self.consecutive_errors >= self.max_consecutive_errors:
            logger.critical(f"Too many consecutive errors ({self.consecutive_errors}). Raising.")
            raise error

        return None  # Retryable — caller should retry

    def reset_error_count(self):
        self.consecutive_errors = 0
        self.reconnect_delay = 5

    def fetch_ohlcv(self, pair: str, timeframe: str = "5m", limit: int = 100) -> list:
        """Fetch OHLCV data with retry."""
        for attempt in range(3):
            try:
                self._rate_limit()
                data = self.exchange.fetch_ohlcv(pair, timeframe=timeframe, limit=limit)
                self.last_request = time.time()
                self.reset_error_count()
                return data
            except Exception as e:
                result = self._handle_error(e, f"fetch_ohlcv({pair}, {timeframe})")
                if result is not None:
                    raise  # Non-retryable
                if attempt == 2:
                    raise
        return []

    def fetch_order_book(self, pair: str, limit: int = 20) -> dict:
        """Fetch order book with retry."""
        for attempt in range(3):
            try:
                self._rate_limit()
                ob = self.exchange.fetch_order_book(pair, limit=limit)
                self.last_request = time.time()
                self.reset_error_count()
                if ob and ob.get("bids") and ob.get("asks"):
                    bid_vol = sum(b[1] for b in ob["bids"][:5])
                    ask_vol = sum(a[1] for a in ob["asks"][:5])
                    spread_pct = (
                        (ob["asks"][0][0] - ob["bids"][0][0]) / ob["bids"][0][0] * 100
                        if ob["bids"] and ob["asks"]
                        else 0.1
                    )
                    return {
                        "bid_volume": bid_vol,
                        "ask_volume": ask_vol,
                        "spread_pct": spread_pct,
                        "bids": ob["bids"][:5],
                        "asks": ob["asks"][:5],
                    }
                return {"bid_volume": 0, "ask_volume": 0, "spread_pct": 0.1, "bids": [], "asks": []}
            except Exception as e:
                result = self._handle_error(e, f"orderbook({pair})")
                if result is not None:
                    raise
                if attempt == 2:
                    raise
        return {"bid_volume": 0, "ask_volume": 0, "spread_pct": 0.1, "bids": [], "asks": []}

    def fetch_ticker(self, pair: str) -> dict:
        """Fetch ticker with retry."""
        for attempt in range(3):
            try:
                self._rate_limit()
                ticker = self.exchange.fetch_ticker(pair)
                self.last_request = time.time()
                self.reset_error_count()
                return {
                    "last": ticker.get("last", 0),
                    "bid": ticker.get("bid", 0),
                    "ask": ticker.get("ask", 0),
                    "baseVolume": ticker.get("baseVolume", 0),
                    "quoteVolume": ticker.get("quoteVolume", 0),
                    "percentage": ticker.get("percentage", 0),
                    "high": ticker.get("high", 0),
                    "low": ticker.get("low", 0),
                }
            except Exception as e:
                result = self._handle_error(e, f"ticker({pair})")
                if result is not None:
                    raise
                if attempt == 2:
                    raise
        return {"last": 0, "bid": 0, "ask": 0, "baseVolume": 0, "quoteVolume": 0, "percentage": 0, "high": 0, "low": 0}

    def fetch_balance(self) -> dict:
        """Fetch full balance."""
        for attempt in range(3):
            try:
                self._rate_limit()
                balance = self.exchange.fetch_balance()
                self.last_request = time.time()
                self.reset_error_count()
                return balance
            except Exception as e:
                result = self._handle_error(e, "fetch_balance")
                if result is not None:
                    raise
                if attempt == 2:
                    raise
        return {}

    def fetch_free_eur(self) -> float:
        """Get free EUR balance."""
        balance = self.fetch_balance()
        if "EUR" in balance and "free" in balance["EUR"]:
            return float(balance["EUR"]["free"])
        return 0.0

    def get_free_amount(self, asset: str) -> float:
        """Get free amount of an asset."""
        balance = self.fetch_balance()
        if asset in balance and "free" in balance[asset]:
            return float(balance[asset]["free"])
        return 0.0

    def create_limit_buy_order(self, pair: str, amount: float, price: float) -> Optional[dict]:
        """Create limit buy order with proper rounding."""
        for attempt in range(3):
            try:
                self._rate_limit()
                market = self.exchange.market(pair)
                amount = self.exchange.amount_to_precision(pair, amount)
                price = self.exchange.price_to_precision(pair, price)
                order = self.exchange.create_limit_buy_order(pair, amount, price)
                self.last_request = time.time()
                self.reset_error_count()
                logger.info(f"✅ BUY {pair}: {amount} @ {price} — ID: {order.get('id')}")
                return order
            except Exception as e:
                category = self._classify_error(e)
                if category in ("INSUFFICIENT_FUNDS", "BAD_REQUEST"):
                    logger.error(f"[{category}] Order failed: {e}")
                    raise
                logger.warning(f"Order attempt {attempt+1}/3 failed: {e}")
                if attempt == 2:
                    raise
                time.sleep(2)
        return None

    def create_limit_sell_order(self, pair: str, amount: float, price: float) -> Optional[dict]:
        """Create limit sell order with proper rounding."""
        for attempt in range(3):
            try:
                self._rate_limit()
                market = self.exchange.market(pair)
                amount = self.exchange.amount_to_precision(pair, amount)
                price = self.exchange.price_to_precision(pair, price)
                order = self.exchange.create_limit_sell_order(pair, amount, price)
                self.last_request = time.time()
                self.reset_error_count()
                logger.info(f"✅ SELL {pair}: {amount} @ {price} — ID: {order.get('id')}")
                return order
            except Exception as e:
                category = self._classify_error(e)
                if category in ("INSUFFICIENT_FUNDS", "BAD_REQUEST"):
                    logger.error(f"[{category}] Order failed: {e}")
                    raise
                logger.warning(f"Order attempt {attempt+1}/3 failed: {e}")
                if attempt == 2:
                    raise
                time.sleep(2)
        return None

    def create_market_buy_order(self, pair: str, amount: float) -> Optional[dict]:
        """Create market buy order."""
        for attempt in range(3):
            try:
                self._rate_limit()
                order = self.exchange.create_market_buy_order(pair, amount)
                self.last_request = time.time()
                self.reset_error_count()
                logger.info(f"✅ MARKET BUY {pair}: {amount} — ID: {order.get('id')}")
                return order
            except Exception as e:
                category = self._classify_error(e)
                if category in ("INSUFFICIENT_FUNDS", "BAD_REQUEST"):
                    logger.error(f"[{category}] Order failed: {e}")
                    raise
                logger.warning(f"Market buy attempt {attempt+1}/3 failed: {e}")
                if attempt == 2:
                    raise
                time.sleep(2)
        return None

    def create_market_sell_order(self, pair: str, amount: float) -> Optional[dict]:
        """Create market sell order."""
        for attempt in range(3):
            try:
                self._rate_limit()
                order = self.exchange.create_market_sell_order(pair, amount)
                self.last_request = time.time()
                self.reset_error_count()
                logger.info(f"✅ MARKET SELL {pair}: {amount} — ID: {order.get('id')}")
                return order
            except Exception as e:
                category = self._classify_error(e)
                if category in ("INSUFFICIENT_FUNDS", "BAD_REQUEST"):
                    logger.error(f"[{category}] Order failed: {e}")
                    raise
                logger.warning(f"Market sell attempt {attempt+1}/3 failed: {e}")
                if attempt == 2:
                    raise
                time.sleep(2)
        return None

    def cancel_order(self, order_id: str, pair: str) -> bool:
        """Cancel an order."""
        try:
            self._rate_limit()
            self.exchange.cancel_order(order_id, pair)
            self.last_request = time.time()
            logger.info(f"❌ Cancelled {order_id} on {pair}")
            return True
        except Exception as e:
            logger.warning(f"Cancel failed: {e}")
            return False

    def fetch_open_orders(self, pair: Optional[str] = None) -> list:
        """Fetch open orders."""
        for attempt in range(3):
            try:
                self._rate_limit()
                orders = self.exchange.fetch_open_orders(pair)
                self.last_request = time.time()
                self.reset_error_count()
                return orders
            except Exception as e:
                result = self._handle_error(e, "fetch_open_orders")
                if result is not None:
                    raise
                if attempt == 2:
                    raise
        return []

    def fetch_my_trades(self, pair: str, limit: int = 50) -> list:
        """Fetch recent trades for a pair."""
        for attempt in range(3):
            try:
                self._rate_limit()
                trades = self.exchange.fetch_my_trades(pair, limit=limit)
                self.last_request = time.time()
                self.reset_error_count()
                return trades
            except Exception as e:
                result = self._handle_error(e, f"fetch_my_trades({pair})")
                if result is not None:
                    raise
                if attempt == 2:
                    raise
        return []

    def get_market_info(self, pair: str) -> dict:
        """Get market info (precision, limits, etc.)."""
        try:
            market = self.exchange.market(pair)
            return {
                "base": market["base"],
                "quote": market["quote"],
                "amount_precision": market["precision"]["amount"],
                "price_precision": market["precision"]["price"],
                "min_amount": market["limits"]["amount"]["min"],
                "min_cost": market["limits"]["cost"]["min"],
                "tier_based": market.get("tierBased", False),
            }
        except Exception as e:
            logger.warning(f"Market info for {pair}: {e}")
            return {}

    def close(self):
        """Close connections."""
        try:
            self.exchange.close()
        except Exception:
            pass
