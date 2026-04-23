import logging

logger = logging.getLogger("ExitStrategy")

class ExitManager:
    def __init__(self, trailing_stop_pct=1.5, activation_threshold=2.0, partial_exit_pct=50, tp1_percent=3.0):
        """
        Sistema di exit migliorato con trailing stop e uscite parziali.
        
        :param trailing_stop_pct: Distanza % dallo stop rispetto al picco
        :param activation_threshold: Profitto minimo % per attivare trailing
        :param partial_exit_pct: % da chiudere al primo TP
        :param tp1_percent: Primo target di profitto %
        """
        self.trailing_stop_pct = trailing_stop_pct
        self.activation_threshold = activation_threshold
        self.partial_exit_pct = partial_exit_pct
        self.tp1_percent = tp1_percent
        self.positions = {}  # {symbol: {'entry': x, 'peak': x, 'partial_done': bool}}

    def update_position(self, symbol, entry_price, current_price):
        """
        Gestisce la posizione e ritorna l'azione da fare.
        
        Returns:
            dict: {'action': 'HOLD'|'PARTIAL_EXIT'|'FULL_EXIT', 'profit_pct': float}
        """
        profit_pct = ((current_price - entry_price) / entry_price) * 100
        
        if symbol not in self.positions:
            self.positions[symbol] = {'entry': entry_price, 'peak': entry_price, 'partial_done': False}
        
        pos = self.positions[symbol]
        pos['peak'] = max(pos['peak'], current_price)
        
        # FASE 1: Take Profit Parziale (50%)
        if profit_pct >= self.tp1_percent and not pos['partial_done']:
            pos['partial_done'] = True
            return {
                'action': 'PARTIAL_EXIT',
                'percentage': self.partial_exit_pct,
                'profit_pct': round(profit_pct, 2),
                'reason': f'TP1 reached ({self.tp1_percent}%)'
            }
        
        # FASE 2: Trailing Stop
        if profit_pct >= self.activation_threshold:
            stop_price = pos['peak'] * (1 - self.trailing_stop_pct / 100)
            if current_price < stop_price:
                del self.positions[symbol]
                return {
                    'action': 'FULL_EXIT',
                    'profit_pct': round(profit_pct, 2),
                    'reason': 'Trailing stop triggered'
                }
        
        return {
            'action': 'HOLD',
            'profit_pct': round(profit_pct, 2),
            'peak': pos['peak'],
            'stop': round(pos['peak'] * (1 - self.trailing_stop_pct / 100), 8)
        }

    def force_exit(self, symbol):
        """Forza uscita immediata"""
        if symbol in self.positions:
            del self.positions[symbol]
            return {'action': 'FORCED_EXIT'}
        return {'action': 'NO_POSITION'}

    def get_status(self):
        """Status di tutte le posizioni"""
        return {
            sym: {
                'entry': data['entry'],
                'peak': data['peak'],
                'unrealized_pnl_pct': round(((data['peak'] - data['entry']) / data['entry']) * 100, 2)
            }
            for sym, data in self.positions.items()
        }

