import re
import ccxt
import os
from dotenv import load_dotenv

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env.mexc')
mexc = ccxt.mexc({
    'apiKey': os.getenv('MEXC_API_KEY'),
    'secret': os.getenv('MEXC_API_SECRET'),
    'options': {'defaultType': 'spot'}
})

def recover_state():
    bal = mexc.fetch_balance()
    tck = mexc.fetch_tickers()
    active = {}
    
    for k, v in bal['total'].items():
        if k == 'USDT': continue
        pair = f"{k}/USDT"
        if pair in tck:
            val = v * tck[pair]['last']
            if val > 1.0: # More than 1 USDT
                active[pair] = {'qty': v, 'price': tck[pair]['last']}
                
    # Now try to refine price from log
    try:
        with open('/home/sergio/.openclaw/workspace/denaro/MEXC_NANO.log', 'r') as f:
            lines = f.readlines()
            for line in reversed(lines):
                if "COMPRATO" in line:
                    match = re.search(r'COMPRATO ([\d\.]+) (\w+/USDT) al prezzo di ([\d\.e\-]+)', line)
                    if match:
                        q, p, pr = match.groups()
                        if p in active:
                            active[p]['price'] = float(pr)
    except: pass
    
    print(active)

recover_state()
