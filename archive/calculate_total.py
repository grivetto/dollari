import gc
prices = {
    'ETH': 1871.46,
    'BNB': 557.81,
    'ADA': 0.2259,
    'DOGE': 0.0808,
    'SOL': 78.09,
    'DOT': 1.278,
    'AVAX': 8.2,
    'BTC': 61170.01
}

balances = {
    'BTC': 0.00027052,
    'ETH': 4.01e-05,
    'BNB': 0.44233032,
    'ADA': 0.8,
    'DOGE': 627.508,
    'EUR': 59.88848299, # Free + Locked
    'SOL': 3.06319,
    'DOT': 38.32,
    'AVAX': 0.00246
}

total_eur = balances['EUR']
for asset, bal in balances.items():
    if asset in prices:
        value = bal * prices[asset]
        total_eur += value
        print(f"{asset}: {bal} * {prices[asset]} = {value:.2f} EUR")

print(f"Total EUR: {total_eur:.2f}")
