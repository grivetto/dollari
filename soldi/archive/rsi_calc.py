import gc
import sys
import json

def calculate_rsi(prices, period=14):
    if len(prices) <= period:
        return None
    
    deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    if avg_loss == 0:
        return 100
        
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Simple RSI for the last point (since we only have 14 points, this is just an approx)
    return rsi

try:
    prices = [float(p) for p in sys.stdin.readlines() if p.strip()]
    print(calculate_rsi(prices))
except Exception as e:
    print(f"Error: {e}")
