import gc
import ccxt
import time
import os
import logging
from dotenv import load_dotenv
import pandas as pd
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [MEXC NANO] - %(message)s',
                    handlers=[logging.FileHandler("MEXC_NANO.log"), logging.StreamHandler()])
logger = logging.getLogger("MexcNano")

load_dotenv('/home/sergio/denaro/.env.mexc')
mexc = ccxt.mexc({
    'apiKey': os.getenv('MEXC_API_KEY'),
    'secret': os.getenv('MEXC_API_SECRET'),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot', 'adjustForTimeDifference': True, 'recvWindow': 60000}
})

PAIRS = ['SOL/USDT', 'DOGE/USDT', 'PEPE/USDT', 'WIF/USDT', 'SUI/USDT', 'XRP/USDT']
TRADE_AMOUNT_USDT = 5.2  # 5.2 USDT a botta (ordine minimo su MEXC di solito è 5 USDT)
TAKE_PROFIT_PCT = 1.0015  # +0.15% (High Freq)
RSI_BUY_THRESHOLD = 45   # Molto più aggressivo

LIVE_TRADING = True     # <-- SAFETY SWITCH

def get_rsi(symbol, timeframe='1m', period=14):
    try:
        ohlcv = mexc.fetch_ohlcv(symbol, timeframe, limit=period + 10)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df['rsi'].iloc[-1]
    except Exception as e:
        return 50

def run_nano_squad():
    mode = "LIVE TRADING" if LIVE_TRADING else "PAPER TRADING (Simulazione)"
    logger.info(f"🚀 Avvio MEXC Nano Squad - Modalità: {mode}")
    logger.info("📡 Connessione a MEXC in corso...")
    
    active_trades = {}
    import re
    try:
        bal = mexc.fetch_balance()
        tck = mexc.fetch_tickers()
        for k, v in bal['total'].items():
            if k == 'USDT': continue
            pair = f"{k}/USDT"
            if pair in tck and pair in PAIRS:
                val = v * tck[pair]['last']
                if val > 2.0:
                    active_trades[pair] = {'qty': v, 'price': tck[pair]['last']}
        
        with open('MEXC_NANO.log', 'r') as f:
            for line in f.readlines():
                match = re.search(r'COMPRATO ([\d\.]+) (\w+/USDT) al prezzo di ([\d\.e\-]+)', line)
                if match:
                    q, p, pr = match.groups()
                    if p in active_trades:
                        active_trades[p]['price'] = float(pr)
        logger.info(f"♻️ Ripristinato stato di {len(active_trades)} trade aperti dal saldo MEXC.")
    except Exception as e:
        logger.error(f"Errore recupero stato iniziale: {e}")
    
    import gc
    while True:
        gc.collect()
        gc.collect()
        try:
            balance = mexc.fetch_balance()
            free_usdt = float(balance.get('USDT', {}).get('free', 0))
            
            for symbol in PAIRS:
                # 1. Controlla posizioni aperte (per vendere)
                if symbol in active_trades:
                    entry_price = active_trades[symbol]['price']
                    qty = active_trades[symbol]['qty']
                    ticker = mexc.fetch_ticker(symbol)
                    current_price = float(ticker['last'])
                    
                    if current_price >= entry_price * TAKE_PROFIT_PCT:
                        logger.info(f"🎯 TAKE PROFIT SUI MICRO-MARGINI! {symbol} ha raggiunto {current_price}")
                        if LIVE_TRADING:
                            try:
                                base_asset = symbol.split('/')[0]
                                actual_qty = float(mexc.fetch_balance().get(base_asset, {}).get('free', 0.0))
                                safe_qty = min(qty, actual_qty)
                                safe_qty = float(mexc.amount_to_precision(symbol, safe_qty))
                                mexc.create_market_sell_order(symbol, safe_qty)
                                logger.info(f"✅ [LIVE] VENDUTO {symbol} ({safe_qty}). Profitto netto incassato in USDT!")
                                
                                # Calcolo Elemosina
                                profit = (current_price - entry_price) * safe_qty
                                elemosina = profit * 0.33
                                try:
                                    vault_file = '/home/sergio/.openclaw/workspace/denaro/vault.json'
                                    with open(vault_file, 'r') as f: v_data = json.load(f)
                                    v_data['GARIBAN_TRACKER'] = v_data.get('GARIBAN_TRACKER', 0.0) + elemosina
                                    v_data['LOCKED_EUR'] = v_data.get('LOCKED_EUR', 0.0) + elemosina
                                    with open(vault_file, 'w') as f: json.dump(v_data, f)
                                    logger.info(f"🤲 [GARIBAN MEXC] Prelevati {elemosina:.4f} USDT di profitto per l'Elemosina!")
                                except Exception as ve:
                                    logger.error(f"Errore aggiornamento Elemosina: {ve}")

                                del active_trades[symbol]
                            except Exception as e:

                                logger.error(f"Errore vendita LIVE {symbol}: {e}")
                        else:
                            logger.info(f"✅ [SIMULAZIONE] Chiusura posizione su {symbol} completata con successo.")
                            profit = (current_price - entry_price) * qty
                            elemosina = profit * 0.33
                            try:
                                vault_file = '/home/sergio/.openclaw/workspace/denaro/vault.json'
                                with open(vault_file, 'r') as f: v_data = json.load(f)
                                v_data['GARIBAN_TRACKER'] = v_data.get('GARIBAN_TRACKER', 0.0) + elemosina
                                v_data['LOCKED_EUR'] = v_data.get('LOCKED_EUR', 0.0) + elemosina
                                with open(vault_file, 'w') as f: json.dump(v_data, f)
                                logger.info(f"🤲 [GARIBAN MEXC] (Simulato) Aggiunti {elemosina:.4f} USDT all'Elemosina/Vault!")
                            except: pass
                            del active_trades[symbol]

                            
                # 2. Cerca nuovi ingressi (per comprare)
                else:
                    # Abbiamo abbastanza fondi per aprire un trade?
                    if free_usdt > TRADE_AMOUNT_USDT:
                        rsi = get_rsi(symbol)
                        if rsi < RSI_BUY_THRESHOLD:
                            logger.info(f"🔥 SEGNALE BUY SUL DIP: {symbol} | RSI: {rsi:.1f}")
                            ticker = mexc.fetch_ticker(symbol)
                            price = float(ticker['last'])
                            qty_raw = TRADE_AMOUNT_USDT / price
                            try:
                                mexc.load_markets()
                                qty = float(mexc.amount_to_precision(symbol, qty_raw))
                            except:
                                qty = round(qty_raw, 4)
                            
                            
                            if LIVE_TRADING:
                                try:
                                    mexc.create_market_buy_order(symbol, qty)
                                    logger.info(f"🛍️ [LIVE] COMPRATO {qty:.4f} {symbol} al prezzo di {price}")
                                    active_trades[symbol] = {'price': price, 'qty': qty}
                                    free_usdt -= TRADE_AMOUNT_USDT
                                except Exception as e:
                                    logger.error(f"Errore acquisto LIVE {symbol}: {e}")
                            else:
                                logger.info(f"🛍️ [SIMULAZIONE] Ingresso simulato su {symbol} a {price}")
                                active_trades[symbol] = {'price': price, 'qty': qty}
                                free_usdt -= TRADE_AMOUNT_USDT
            
            time.sleep(15)
            
        except Exception as e:
            logger.error(f"Errore di rete o API: {e}")
            time.sleep(15)

if __name__ == '__main__':
    run_nano_squad()
