import os, re, time, datetime
from datetime import timezone, timedelta

now = time.time()
fifteen_min_ago = now - 900  # 15 minutes in seconds

def parse_log_line_timestamp(line):
    # Try to match timestamp at start: YYYY-MM-DD HH:MM:SS,mmm
    match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3}', line)
    if match:
        ts_str = match.group(1)
        try:
            dt = datetime.datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
            # Assume local time (Europe/Rome) but logs may be UTC? We'll treat as UTC for simplicity.
            # Actually logs likely in local time? We'll just parse as naive and convert to timestamp assuming UTC.
            # Better to treat as UTC.
            dt = dt.replace(tzinfo=timezone.utc)
            return dt.timestamp()
        except:
            pass
    return None

def scan_log_for_profit(log_path):
    profits = []
    try:
        with open(log_path, 'r') as f:
            for line in f:
                ts = parse_log_line_timestamp(line)
                if ts is None:
                    continue
                if ts >= fifteen_min_ago:
                    # Check for profit keywords
                    if re.search(r'profit|gain|\+[\d\.]+%?|closed.*profit', line, re.I):
                        profits.append(line.strip())
    except Exception as e:
        pass
    return profits

def scan_log_for_opportunity(log_path):
    opportunities = []
    try:
        with open(log_path, 'r') as f:
            for line in f:
                ts = parse_log_line_timestamp(line)
                if ts is None:
                    continue
                if ts >= fifteen_min_ago:
                    # Look for RSI < 25 on BTC/ETH/SOL
                    if re.search(r'RSI.*[<≤]\s*25.*(BTC|ETH|SOL)|(BTC|ETH|SOL).*RSI.*[<≤]\s*25', line, re.I):
                        opportunities.append(line.strip())
    except Exception as e:
        pass
    return opportunities

logs = [
    'sol_scalper.log',
    'quant_bot.log',
    'grid_bot.log'
]

all_profits = []
all_opps = []

for log in logs:
    path = os.path.join('/home/sergio/.openclaw/workspace/denaro', log)
    if os.path.exists(path):
        all_profits.extend(scan_log_for_profit(path))
        all_opps.extend(scan_log_for_opportunity(path))

print("PROFITS:", len(all_profits))
for p in all_profits[:5]:
    print(p)
print("OPPORTUNITIES:", len(all_opps))
for o in all_opps[:5]:
    print(o)
