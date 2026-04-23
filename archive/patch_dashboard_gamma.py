import os, sys

with open('/home/sergio/.openclaw/workspace/denaro/dashboard/dashboard_server.py', 'r') as f:
    content = f.read()

new_imports = """
bitget_client = None
try:
    load_dotenv(os.path.join(BASE_DIR, '.env.bitget'))
    if os.getenv('BITGET_API_KEY'):
        bitget_client = ccxt.bitget({'apiKey': os.getenv('BITGET_API_KEY'), 'secret': os.getenv('BITGET_API_SECRET'), 'password': os.getenv('BITGET_PASSWORD')})
except: pass
"""
content = content.replace("mexc_client = ccxt.mexc({'apiKey': os.getenv('MEXC_API_KEY'), 'secret': os.getenv('MEXC_API_SECRET'), 'options': {'defaultType': 'spot'}})\nexcept: pass", "mexc_client = ccxt.mexc({'apiKey': os.getenv('MEXC_API_KEY'), 'secret': os.getenv('MEXC_API_SECRET'), 'options': {'defaultType': 'spot'}})\nexcept: pass\n" + new_imports)

logic = """
        bitget_free = 0.0
        bitget_pnl = 0.0
        if bitget_client:
            try:
                bal = bitget_client.fetch_balance({'type': 'swap'})
                bitget_free = float(bal.get('USDT', {}).get('total', 0.0))
                # Approximate PNL from unrealized
                positions = bitget_client.fetch_positions()
                for p in positions:
                    if float(p.get('contracts', 0)) > 0:
                        bitget_pnl += float(p.get('unrealizedPnl', 0.0))
            except: pass

        return {
            "vault": f"{vault:.2f}",
            "liquid": f"{liquid:.2f}",
            "target": f"{target:.2f}",
            "profit_today": f"{profit_today:.2f}",
            "mexc_liquid": f"{mexc_free:.2f}",
            "bitget_liquid": f"{bitget_free:.2f}",
            "bitget_pnl": f"{bitget_pnl:.2f}"
        }
"""
import re
content = re.sub(r'return \{[\s\S]*?\}', logic.strip(), content, count=1)

with open('/home/sergio/.openclaw/workspace/denaro/dashboard/dashboard_server.py', 'w') as f:
    f.write(content)
