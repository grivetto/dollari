import sqlite3
from datetime import datetime

class TradeDB:
    def __init__(self, db_path='/app/trades.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_name TEXT,
                    symbol TEXT,
                    side TEXT,
                    entry_price REAL,
                    exit_price REAL,
                    quantity REAL,
                    entry_time DATETIME,
                    exit_time DATETIME,
                    gross_pnl REAL,
                    fees REAL,
                    net_pnl REAL,
                    exit_reason TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS bot_state (
                    bot_name TEXT PRIMARY KEY,
                    is_in_position BOOLEAN,
                    entry_price REAL,
                    quantity REAL,
                    last_heartbeat DATETIME
                )
            ''')
            conn.commit()

    def save_trade(self, bot_name, symbol, side, entry_price, exit_price, quantity, entry_time, exit_time, gross_pnl, fees, net_pnl, reason):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO trades (bot_name, symbol, side, entry_price, exit_price, quantity, entry_time, exit_time, gross_pnl, fees, net_pnl, exit_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (bot_name, symbol, side, entry_price, exit_price, quantity, entry_time, exit_time, gross_pnl, fees, net_pnl, reason))
            conn.commit()

    def get_daily_pnl(self):
        today = datetime.now().strftime('%Y-%m-%d')
        with sqlite3.connect(self.db_path) as conn:
            res = conn.execute('SELECT SUM(net_pnl) FROM trades WHERE date(exit_time) = ?', (today,)).fetchone()
            return res[0] if res[0] else 0.0

    def get_metrics(self):
        with sqlite3.connect(self.db_path) as conn:
            trades = conn.execute('SELECT net_pnl FROM trades').fetchall()
            if not trades: return {'win_rate': 0, 'total_profit': 0}
            
            pnls = [t[0] for t in trades]
            win_rate = (len([p for p in pnls if p > 0]) / len(pnls)) * 100
            total_profit = sum(pnls)
            return {'win_rate': win_rate, 'total_profit': total_profit}
