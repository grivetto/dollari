
import pandas as pd
import pandas_ta as ta

def calculate_rsi(prices, length=14):
    """Calculates RSI using pandas_ta. Returns the last value."""
    if len(prices) < length:
        return 50.0
    series = pd.Series(prices)
    rsi = ta.rsi(series, length=length)
    return float(rsi.iloc[-1]) if not rsi.empty else 50.0

def calculate_ema(prices, length=9):
    """Calculates EMA using pandas_ta. Returns the last value."""
    if len(prices) < length:
        return prices[-1] if prices else 0.0
    series = pd.Series(prices)
    ema = ta.ema(series, length=length)
    return float(ema.iloc[-1]) if not ema.empty else prices[-1]

def calculate_atr(highs, lows, closes, length=14):
    """Calculates ATR using pandas_ta. Returns the last value."""
    if len(highs) < length:
        return 0.0
    df = pd.DataFrame({
        'high': highs,
        'low': lows,
        'close': closes
    })
    atr = ta.atr(df['high'], df['low'], df['close'], length=length)
    return float(atr.iloc[-1]) if not atr.empty else 0.0
