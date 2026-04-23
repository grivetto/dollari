import gc
import gc
import gc
import ccxt
import os
import time
import logging
from dotenv import load_dotenv
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [GAMMA ⚖️] - %(message)s',
                    handlers=[logging.FileHandler("GAMMA_PAIRS.log"), logging.StreamHandler()])
logger = logging.getLogger("GammaPairs")

load_dotenv('/home/sergio/denaro/.env.bitget')
bitget = ccxt.bitget({
    'apiKey': os.getenv('BITGET_API_KEY'),
    'secret': os.getenv('BITGET_API_SECRET'),
    'password': os.getenv('BITGET_PASSWORD'),
    'enableRateLimit': True,
    'options': {'defaultType': 'swap', 'adjustForTimeDifference': True}
})

SYMBOLS = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'ADA/USDT:USDT', 'XRP/USDT:USDT', 'DOT/USDT:USDT', 'AVAX/USDT:USDT']
LEVERAGE = 10
TRADE_USDT_PER_LEG = 2.0  # 7.5$ sul LONG, 7.5$ sullo SHORT
TAKE_PROFIT_PCT = 0.01     # +1% di spread tra le due (ROI totale 10%)

def get_momentum(symbol):
    try:
        ohlcv = bitget.fetch_ohlcv(symbol, '15m', limit=20)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        return (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0] * 100
    except: return 0.0

def run_gamma_pairs():
    logger.info("⚖️ SQUADRA GAMMA (Pairs Trading) ONLINE - Arbitraggio di Forza Relativa")
    
    in_position = False
    long_sym = None
    short_sym = None
    entry_spread = 0.0
    
    # Pulizia posizione precedente
    try:
        pos = bitget.fetch_positions(SYMBOLS)
        active_pos = [p for p in pos if float(p.get('contracts', 0)) > 0]
        if len(active_pos) == 2:
            in_position = True
            for p in active_pos:
                if p['side'] == 'long': long_sym = p['symbol']
                else: short_sym = p['symbol']
            logger.info(f"🔄 Recuperato Pairs Trading: LONG {long_sym} / SHORT {short_sym}")
    except: pass

    import gc
    while True:
        gc.collect()
        try:
            bal = bitget.fetch_balance({'type': 'swap'})
            usdt_balance = float(bal.get('USDT', {}).get('free', 0.0))

            if not in_position:
                if usdt_balance < (TRADE_USDT_PER_LEG * 2):
                    logger.warning(f"Fondi insufficienti per Pairs Trading (Liberi: {usdt_balance:.2f} USDT). Servono {TRADE_USDT_PER_LEG*2} USDT liberi.")
                    time.sleep(60)
                    continue
                
                # Analisi forza
                momenta = {s: get_momentum(s) for s in SYMBOLS}
                sorted_m = sorted(momenta.items(), key=lambda x: x[1])
                weakest = sorted_m[0][0]
                strongest = sorted_m[-1][0]
                
                logger.info(f"🔍 Analisi in corso... Max Spread {momenta[strongest]-momenta[weakest]:.2f}%")
                if momenta[strongest] - momenta[weakest] > 1.0: # Differenza dell'1%
                    logger.info(f"🔥 SPREAD TROVATO! Forte: {strongest} ({momenta[strongest]:+.2f}%) | Debole: {weakest} ({momenta[weakest]:+.2f}%)")
                    
                    try:
                        bitget.set_leverage(LEVERAGE, strongest)
                    except Exception:
                        pass
                    try:
                        bitget.set_leverage(LEVERAGE, weakest)
                    except Exception:
                        pass
                    try:
                        bitget.set_margin_mode('isolated', strongest)
                    except Exception:
                        pass
                    try:
                        bitget.set_margin_mode('isolated', weakest)
                    except Exception:
                        pass
                    
                    try:
                        p_strong = bitget.fetch_ticker(strongest)['last']
                        p_weak = bitget.fetch_ticker(weakest)['last']
                        
                        qty_long = bitget.amount_to_precision(strongest, (TRADE_USDT_PER_LEG * LEVERAGE) / p_strong)
                        qty_short = bitget.amount_to_precision(weakest, (TRADE_USDT_PER_LEG * LEVERAGE) / p_weak)
                        
                        bitget.create_market_buy_order(strongest, float(qty_long))
                        bitget.create_market_sell_order(weakest, float(qty_short))
                        
                        logger.info(f"⚖️ PAIR ESEGUITO: LONG {strongest} | SHORT {weakest}")
                        long_sym = strongest
                        short_sym = weakest
                        in_position = True
                        entry_spread = (p_strong / p_weak)
                    except Exception as e:
                        logger.error(f"Errore esecuzione pair: {e}")
            
            else:
                p_long = bitget.fetch_ticker(long_sym)['last']
                p_short = bitget.fetch_ticker(short_sym)['last']
                current_spread = (p_long / p_short)
                
                profit_pct = (current_spread - entry_spread) / entry_spread
                roi = profit_pct * LEVERAGE * 100
                logger.info(f"⚖️ PAIRS ATTIVO: LONG {long_sym} / SHORT {short_sym} | ROI Spread: {roi:+.2f}%")
                
                if roi >= (TAKE_PROFIT_PCT * LEVERAGE * 100):
                    logger.info("💰 TARGET SPREAD RAGGIUNTO! Chiusura simultanea delle due gambe.")
                    bitget.create_market_sell_order(long_sym, float(active_pos[0]['contracts']), params={'reduceOnly': True})
                    bitget.create_market_buy_order(short_sym, float(active_pos[1]['contracts']), params={'reduceOnly': True})
                    in_position = False
                    time.sleep(300)
                    
            time.sleep(15)

        except Exception as e:
            logger.error(f"Errore ciclo Gamma: {e}")
            time.sleep(30)

if __name__ == '__main__':
    run_gamma_pairs()
