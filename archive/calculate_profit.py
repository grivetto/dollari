import gc
import json
prices = {'ETH': 1870.6, 'BNB': 555.14, 'ADA': 0.2263, 'DOGE': 0.0812, 'SOL': 78.61, 'DOT': 1.259, 'AVAX': 8.27, 'BTC': 61374.95}
balances = {'BTC': 0.00026418, 'ETH': 0.0183401, 'BNB': 0.47046701, 'ADA': 0.8, 'DOGE': 464.508, 'EUR': 42.0406, 'SOL': 2.80819, 'DOT': 38.32, 'AVAX': 0.00246}
total = balances['EUR']
for a, b in balances.items():
    if a in prices: total += b * prices[a]
print(f"{total:.2f}")
