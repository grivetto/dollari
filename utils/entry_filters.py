
import logging
from utils import indicators as ind

logger = logging.getLogger("EntryFilters")

class EntryFilters:
    @staticmethod
    def should_enter(symbol, price, klines, volume_data):
        """
        Analizza le condizioni di ingresso basandosi su RSI, Volume e Trend.
        """
        # 1. RSI Filter
        rsi = ind.calculate_rsi(klines, 14)
        rsi_ok = 30 < rsi < 70  # Evita zone di estremo esaurimento
        
        # 2. Volume Filter (Volume > 1.5x MA20)
        volumes = [v for v in volume_data]
        if len(volumes) < 20: return False, "Insufficent volume data"
        
        ma20_vol = sum(volumes[-20:]) / 20
        current_vol = volumes[-1]
        vol_ok = current_vol > (ma20_vol * 1.5)
        
        # 3. Trend Filter (EMA 50 > EMA 200)
        # We need more data for EMA 200
        if len(klines) < 200: return False, "Insufficent data for trend"
        
        ema50 = ind.calculate_ema(klines, 50)
        ema200 = ind.calculate_ema(klines, 200)
        trend_up = ema50 > ema200
        
        # Decision Logic
        if rsi_ok and vol_ok and trend_up:
            return True, "STRONG_BUY"
        if rsi < 30 and vol_ok:
            return True, "OVERSOLD_BOUNCE"
            
        return False, f"RSI:{rsi:.1f}, Vol:{vol_ok}, Trend:{trend_up}"
