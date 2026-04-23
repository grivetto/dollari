import pandas as pd
import pandas_ta as ta
import numpy as np

class LegionSimulator:
    def __init__(self, symbol, df, initial_balance=500.0):
        self.symbol = symbol
        self.df = df if df is not None else pd.DataFrame()
        self.balance = initial_balance
        self.initial_balance = initial_balance
        
        self.drop_trigger = -0.01
        self.TP_ATR_MULT = 1.5
        self.SL_ATR_MULT = 2.0
        self.rsi_threshold = 35
        
        self.RISK_PER_TRADE_PCT = 0.01
        self.MAX_TRADE_USDT = 50.0
        self.MIN_TRADE_USDT = 5.0
        self.ATR_PERIOD = 14
        
        self.position = False
        self.buy_price = 0.0
        self.current_tp = 0.0
        self.current_sl = 0.0
        self.trade_amount = 0.0
        self.trades = []

    def calculate_atr(self):
        if self.df is None or len(self.df) < self.ATR_PERIOD: return 0
        atr = ta.atr(self.df['high'], self.df['low'], self.df['close'], length=self.ATR_PERIOD)
        return atr.iloc[-1] if not atr.empty else 0

    def run_with_params(self, params):
        if self.df is None or len(self.df) < 100: return []
        
        self.drop_trigger = params.get('drop', self.drop_trigger)
        self.TP_ATR_MULT = params.get('tp_mult', self.TP_ATR_MULT)
        self.SL_ATR_MULT = params.get('sl_mult', self.SL_ATR_MULT)
        self.rsi_threshold = params.get('rsi_thresh', self.rsi_threshold)
        
        self.position = False
        self.balance = self.initial_balance
        self.trades = []
        
        df = self.df.copy()
        df['rsi'] = ta.rsi(df['close'], length=14)
        df['ema'] = ta.ema(df['close'], length=50)
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=self.ATR_PERIOD)
        df['vol_avg'] = df['volume'].rolling(window=20).mean()

        for i in range(50, len(df)):
            row = df.iloc[i]
            price = row['close']
            
            if self.position:
                if price >= self.current_tp or price <= self.current_sl:
                    pnl = (price - self.buy_price) / self.buy_price
                    profit_usdt = self.trade_amount * pnl
                    self.balance += profit_usdt
                    self.trades.append({
                        'symbol': self.symbol,
                        'entry_time': self.entry_time,
                        'exit_time': row['timestamp'],
                        'entry_price': self.buy_price,
                        'exit_price': price,
                        'pnl_pct': pnl * 100,
                        'profit_usdt': profit_usdt,
                        'balance': self.balance,
                        'type': 'TP' if price >= self.current_tp else 'SL'
                    })
                    self.position = False
            else:
                price_10_ago = df['close'].iloc[i-10]
                drop = (price - price_10_ago) / price_10_ago
                vol_spike = row['volume'] > row['vol_avg'] * 1.5
                rsi_ok = row['rsi'] < self.rsi_threshold if not pd.isna(row['rsi']) else False
                trend_ok = (price > row['ema']) or (row['rsi'] < 20) if not pd.isna(row['ema']) else False
                
                if drop <= self.drop_trigger and rsi_ok and vol_spike and trend_ok:
                    atr = row['atr']
                    if pd.isna(atr) or atr == 0: continue
                    sl_dist = (atr * self.SL_ATR_MULT) / price
                    risk_amount = self.balance * self.RISK_PER_TRADE_PCT
                    size = risk_amount / sl_dist if sl_dist > 0 else 11.0
                    size = max(self.MIN_TRADE_USDT, min(self.MAX_TRADE_USDT, size))
                    self.buy_price = price
                    self.current_tp = price + (atr * self.TP_ATR_MULT)
                    self.current_sl = price - (atr * self.SL_ATR_MULT)
                    self.trade_amount = size
                    self.entry_time = row['timestamp']
                    self.position = True
        return self.trades

    def get_stats(self):
        if not self.trades: return None
        df_trades = pd.DataFrame(self.trades)
        win_rate = (df_trades['profit_usdt'] > 0).mean() * 100
        total_profit = self.balance - self.initial_balance
        return {
            'symbol': self.symbol,
            'total_trades': len(self.trades),
            'win_rate': win_rate,
            'total_profit': total_profit,
            'final_balance': self.balance,
            'max_drawdown': self.calculate_max_drawdown()
        }

    def calculate_max_drawdown(self):
        balances = [t['balance'] for t in self.trades]
        if not balances: return 0
        peak = balances[0]
        max_dd = 0
        for b in balances:
            if b > peak: peak = b
            dd = (peak - b) / peak
            if dd > max_dd: max_dd = dd
        return max_dd * 100
