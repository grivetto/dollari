with open("dashboard/dashboard_server.py", "r") as f:
    code = f.read()

# Add mexc parsing
new_balance_logic = """
        try:
            mexc_free = 0.0
            import ccxt
            load_dotenv(os.path.join(BASE_DIR, '.env.mexc'))
            api_key = os.getenv('MEXC_API_KEY')
            if api_key:
                mexc = ccxt.mexc({'apiKey': api_key, 'secret': os.getenv('MEXC_API_SECRET'), 'options': {'defaultType': 'spot'}})
                bal = mexc.fetch_balance()
                mexc_free = float(bal.get('USDT', {}).get('free', 0.0))
        except:
            mexc_free = 0.0

        return {
            "vault": f"{vault:.2f}",
            "liquid": f"{liquid:.2f}",
            "target": f"{target:.2f}",
            "profit_today": f"{profit_today:.2f}",
            "mexc_liquid": f"{mexc_free:.2f}"
        }
"""

import re
code = re.sub(r'return \{\n\s+"vault": f"\{vault:\.2f\}",\n\s+"liquid": f"\{liquid:\.2f\}",\n\s+"target": f"\{target:\.2f\}",\n\s+"profit_today": f"\{profit_today:\.2f\}"\n\s+\}', new_balance_logic, code)

# add MEXC_NANO.log to logs
code = code.replace('"OB_WALL_SNIPER.log"]', '"OB_WALL_SNIPER.log", "MEXC_NANO.log"]')

with open("dashboard/dashboard_server.py", "w") as f:
    f.write(code)

