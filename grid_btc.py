#!/usr/bin/env python3
"""
DENARO GRID BOT - BTC/EUR
Macchina: MC2
Capitale: €150
Strategia: Grid Conservativo (±2%)
"""

import os
import sys
import time
import json
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - BTC_GRID - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BTCGrid")

CONFIG = {
    "symbol": "BTC/EUR",
    "grid_levels": 5,
    "grid_range_pct": 0.02,  # ±2% (conservativo)
    "profit_per_grid": 0.003,  # 0.3%
    "base_order_eur": 15.0,
    "max_total_invested": 150.0,
    "trailing_stop_pct": 1.5,
    "trailing_activation_pct": 2.5,
    "check_interval": 30,
    "vault_pct": 0.33,
}

state = {
    "filled_orders": [],
    "total_invested": 0.0,
    "total_profit": 0.0,
    "peak_value": 0.0,
}

def get_client():
    import ccxt
    return ccxt.binance({
        'apiKey': os.getenv("BINANCE_API_KEY"),
        'secret': os.getenv("BINANCE_API_SECRET"),
        'enableRateLimit': True,
    })

def calculate_grid(current_price):
    prices = []
    step = CONFIG["grid_range_pct"] / CONFIG["grid_levels"]
    for i in range(-CONFIG["grid_levels"], CONFIG["grid_levels"] + 1):
        price = current_price * (1 + i * step)
        prices.append({
            "level": i,
            "price": round(price, 2),
            "action": "buy" if i < 0 else ("sell" if i > 0 else "hold")
        })
    return prices

def place_orders(client, prices):
    if state["total_invested"] >= CONFIG["max_total_invested"]:
        return []
    
    placed = []
    for p in prices:
        if p["action"] == "hold":
            continue
        amount = CONFIG["base_order_eur"] / p["price"]
        try:
            order = (client.create_limit_buy_order if p["action"] == "buy" else client.create_limit_sell_order)(
                symbol=CONFIG["symbol"], amount=round(amount, 8), price=p["price"]
            )
            placed.append({"id": order['id'], "price": p["price"], "action": p["action"]})
            logger.info(f"Placed {p['action']} @ {p['price']}")
        except Exception as e:
            logger.error(f"Order failed: {e}")
    return placed

def check_fills(client):
    for order in state["filled_orders"]:
        if order.get("processed"):
            continue
        try:
            status = client.fetch_order(order['id'], CONFIG["symbol"])
            if status['status'] == 'closed':
                order["processed"] = True
                if order["action"] == "buy":
                    state["total_invested"] += order["price"]
                else:
                    profit = CONFIG["profit_per_grid"] * CONFIG["base_order_eur"]
                    state["total_profit"] += profit
                    vault_contrib = profit * CONFIG["vault_pct"]
                    logger.info(f"💰 Sell @ {order['price']}, Profit: {profit:.2f}€ (Vault: {vault_contrib:.2f}€)")
        except Exception as e:
            logger.error(f"Check failed: {e}")

def trailing_check(current_price):
    if not state["filled_orders"] or current_price <= 0:
        return "HOLD"
    
    state["peak_value"] = max(state["peak_value"], current_price)
    avg_entry = sum(o["price"] for o in state["filled_orders"]) / len(state["filled_orders"])
    profit_pct = (current_price - avg_entry) / avg_entry * 100
    
    if profit_pct >= CONFIG["trailing_activation_pct"]:
        stop = state["peak_value"] * (1 - CONFIG["trailing_stop_pct"] / 100)
        if current_price < stop:
            return "EXIT"
    return "HOLD"

def main():
    logger.info("🚀 BTC GRID BOT Starting (MC2) - Capital: €150")
    
    client = get_client()
    if not client:
        logger.error("No API client")
        return
    
    try:
        ticker = client.fetch_ticker(CONFIG["symbol"])
        current_price = ticker['last']
        state["peak_value"] = current_price
        logger.info(f"BTC price: {current_price}€")
    except Exception as e:
        logger.error(f"Price fetch failed: {e}")
        return
    
    logger.info(f"Grid: {CONFIG['grid_levels']} levels, ±{CONFIG['grid_range_pct']*100}%")
    
    while True:
        try:
            ticker = client.fetch_ticker(CONFIG["symbol"])
            current_price = ticker['last']
            
            action = trailing_check(current_price)
            if action == "EXIT":
                logger.info(f"🚨 TRAILING STOP @ {current_price}€")
                break
            
            check_fills(client)
            
            if time.time() % 60 < CONFIG["check_interval"]:
                logger.info(f"Price: {current_price}€, Invested: {state['total_invested']:.2f}€, Profit: {state['total_profit']:.2f}€")
            
            time.sleep(CONFIG["check_interval"])
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
