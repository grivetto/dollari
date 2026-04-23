import pandas as pd
import itertools
import os
from data_fetcher import fetch_historical_data
from legion_simulator import LegionSimulator

SYMBOLS = ['MATIC/USDT', 'ADA/USDT', 'SOL/USDT', 'DOT/USDT', 'LINK/USDT']
DAYS = 30
INITIAL_BALANCE = 500.0

PARAM_GRID = {
    'drop': [-0.005, -0.01, -0.015, -0.02],
    'tp_mult': [1.0, 1.5, 2.0, 2.5],
    'sl_mult': [1.5, 2.0, 2.5, 3.0],
    'rsi_thresh': [30, 35, 40]
}

def run_optimization():
    best_profit = -float('inf')
    best_params = None
    
    data_cache = {}
    for s in SYMBOLS:
        data_cache[s] = fetch_historical_data(s, days=DAYS)
    
    keys, values = zip(*PARAM_GRID.items())
    combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    
    print(f'Starting optimization: {len(combinations)} combinations...', flush=True)
    
    for i, params in enumerate(combinations):
        total_profit = 0
        for s in SYMBOLS:
            sim = LegionSimulator(s, data_cache[s], initial_balance=INITIAL_BALANCE)
            trades = sim.run_with_params(params)
            if trades:
                stats = sim.get_stats()
                total_profit += stats['total_profit']
        
        if total_profit > best_profit:
            best_profit = total_profit
            best_params = params
            
        if (i + 1) % 20 == 0:
            print(f'Progress: {i+1}/{len(combinations)} | Best Profit: {best_profit:.2f}€', flush=True)

    print('\n' + '='*40, flush=True)
    print('OPTIMIZATION COMPLETE', flush=True)
    print('='*40, flush=True)
    print(f'Best Params: {best_params}', flush=True)
    print(f'Max Profit: {best_profit:.2f}€', flush=True)
    print('='*40, flush=True)
    return best_params

if __name__ == '__main__':
    run_optimization()
