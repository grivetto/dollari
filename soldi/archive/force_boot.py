import os, time, subprocess

WORKSPACE = "/home/sergio/.openclaw/workspace/denaro"
VENV_PYTHON = f"{WORKSPACE}/trading_bot_env/bin/python3"

BOTS = [
    "triangle_arbitrage_v1.py", "hyper_mm_sol.py", "whale_pressure_scaler.py",
    "inverse_corr_bot.py", "ema_cross_scalper.py", "btc_arbitrage_simple.py",
    "eth_market_maker.py", "bnb_mean_reversion.py", "sol_momentum_hunter.py",
    "whale_order_tracker.py", "sentiment_analyzer_bot.py", "multi_coin_rebalancer.py",
    "flash_crash_buyer.py", "breakout_volatility_unit.py", "eth_gas_price_trader.py"
]

for script in BOTS:
    path = os.path.join(WORKSPACE, script)
    try:
        subprocess.Popen([VENV_PYTHON, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Force Started {script}")
        time.sleep(1)
    except: pass
