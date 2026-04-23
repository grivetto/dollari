import gc
prices = {'ETH': 1868.22, 'BNB': 553.8, 'ADA': 0.2279, 'DOGE': 0.08184, 'SOL': 78.66, 'DOT': 1.253, 'AVAX': 8.27, 'BTC': 61165.15}
balances = {'BTC': 0.00026304, 'ETH': 0.0183401, 'BNB': 0.47040181, 'ADA': 0.8, 'DOGE': 464.508, 'EUR': 41.9486, 'SOL': 2.80819, 'DOT': 38.32, 'AVAX': 0.00246}
total = balances['EUR']
for a, b in balances.items():
    if a in prices: total += b * prices[a]
print(total)
