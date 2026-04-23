import pandas as pd
from data_fetcher import fetch_historical_data
from legion_simulator import LegionSimulator
import os

SYMBOLS = ['MATIC/USDT', 'ADA/USDT', 'SOL/USDT', 'DOT/USDT', 'LINK/USDT']
DAYS = 7
INITIAL_BALANCE = 500.0

def run_backtest():
    all_stats = []
    
    for symbol in SYMBOLS:
        print(f'\n--- Testing {symbol} ---')
        df = fetch_historical_data(symbol, days=DAYS)
        
        sim = LegionSimulator(symbol, df, initial_balance=INITIAL_BALANCE)
        trades = sim.run()
        stats = sim.get_stats()
        
        if stats:
            print(f'Trades: {stats["total_trades"]} | WinRate: {stats["win_rate"]:.2f}% | Profit: {stats["total_profit"]:.2f}€ | MaxDD: {stats["max_drawdown"]:.2f}%')
            all_stats.append(stats)
        else:
            print('No trades executed.')

    if all_stats:
        summary = pd.DataFrame(all_stats)
        print('\n' + '='*40)
        print('FINAL SUMMARY')
        print('='*40)
        print(summary.to_string(index=False))
        print('='*40)
        print(f'Aggregated Profit: {summary["total_profit"].sum():.2f}€')
    else:
        print('No trades found for any symbol.')

if __name__ == '__main__':
    run_backtest()
