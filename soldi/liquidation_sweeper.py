import ccxt
import time
import os
import sys
import json
import logging
from collections import deque
import asyncio
import websockets
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [LIQUIDATION SWEEPER 🧹] - %(message)s',
                    handlers=[logging.FileHandler("LIQUIDATION_SWEEPER.log"), logging.StreamHandler()])

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env.bitget')

try:
    bitget = ccxt.bitget({
        'apiKey': os.getenv('BITGET_API_KEY'),
        'secret': os.getenv('BITGET_API_SECRET'),
        'password': os.getenv('BITGET_PASSWORD'),
        'enableRateLimit': True,
        'options': {'defaultType': 'swap'}
    })
    bitget.load_markets()
except Exception as e:
    logging.error(f"Errore connessione: {e}")
    exit()

async def listen_liquidations():
    uri = "wss://fstream.binance.com/ws/!forceOrder@arr"
    
    LIQUIDATION_THRESHOLD_USD = 2_000_000 # 2 Milioni di dollari in 3 secondi
    TIME_WINDOW_SEC = 3
    MARGIN_USDT = 15.0
    LEVERAGE = 20
    
    liquidations = deque()
    
    logging.info("🧹 LO SPAZZINO (Liquidation Sweeper) INIZIALIZZATO.")
    logging.info("Connesso al nastro forceOrder di Binance Futures. In ascolto di cadaveri finanziari in leva 100x...")
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    if 'o' in data:
                        order = data['o']
                        symbol = order['s']
                        side = order['S']      # "SELL" o "BUY"
                        price = float(order['p'])
                        qty = float(order['q'])
                        usd_value = price * qty
                        
                        timestamp = time.time()
                        
                        # Solo liquidazioni SELL (trader LONG che vengono margin-called e forzati a vendere, causando un dump)
                        if side == "SELL" and usd_value > 10000: # Ignoriamo i pesciolini sotto 10k
                            liquidations.append({"sym": symbol, "val": usd_value, "time": timestamp})
                            
                        # Pulisci liquidazioni vecchie (>3 secondi)
                        while liquidations and liquidations[0]["time"] < timestamp - TIME_WINDOW_SEC:
                            liquidations.popleft()
                            
                        # Sommiamo il volume liquidato per moneta
                        sym_totals = {}
                        for liq in liquidations:
                            s = liq["sym"]
                            sym_totals[s] = sym_totals.get(s, 0) + liq["val"]
                            
                        for sym, total_val in sym_totals.items():
                            if total_val >= LIQUIDATION_THRESHOLD_USD:
                                logging.warning(f"🩸 [LIQUIDATION CASCADE] Rilevata carneficina su {sym}: {total_val/1_000_000:.2f} MILIONI di USD liquidati in {TIME_WINDOW_SEC}s!")
                                
                                # Entriamo sul Bottom della Cascata su Bitget
                                # Trasformiamo il simbolo da Binance (BTCUSDT) a Bitget (BTC/USDT:USDT)
                                bitget_sym = sym.replace('USDT', '/USDT:USDT')
                                
                                try:
                                    bitget.set_leverage(LEVERAGE, bitget_sym)
                                except: pass
                                
                                try:
                                    ticker = bitget.fetch_ticker(bitget_sym)
                                    curr_price = ticker['last']
                                    buy_qty = (MARGIN_USDT * LEVERAGE) / curr_price
                                    buy_qty_str = bitget.amount_to_precision(bitget_sym, buy_qty)
                                    
                                    logging.info(f"🧹 SPAZZINO IN AZIONE: Compro il fondo di {bitget_sym} (LONG {buy_qty_str} a ~{curr_price})")
                                    bitget.create_market_buy_order(bitget_sym, float(buy_qty_str))
                                    
                                    # Piazziamo il Take Profit rapido per il Rimbalzo del Gatto Morto (+1.5%)
                                    tp_price = curr_price * 1.015
                                    bitget.create_order(bitget_sym, 'limit', 'sell', float(buy_qty_str), float(bitget.price_to_precision(bitget_sym, tp_price)), params={'reduceOnly': True})
                                    
                                    logging.info("✅ Operazione Eseguita. Resti recuperati, in attesa del rimbalzo.")
                                    liquidations.clear() # Svuotiamo per non comprare due volte
                                    
                                    # Notifica
                                    try:
                                        import requests
                                        tk = os.getenv('TELEGRAM_BOT_TOKEN')
                                        cid = os.getenv('TELEGRAM_CHAT_ID')
                                        msg = f"🧹 *LIQUIDATION SWEEPER* 🧹\n\nHo rilevato una carneficina in diretta mondiale su *{sym}*.\nSono stati liquidati forzatamente **${total_val/1_000_000:.2f} Milioni** di dollari in soli 3 secondi.\n\nHo spazzato il fondo comprando LONG in leva {LEVERAGE}x su Bitget con {MARGIN_USDT}$. Attendo il rimbalzo fisiologico. 🩸"
                                        requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", data={"chat_id": cid, "text": msg, "parse_mode": "Markdown"})
                                    except: pass
                                    
                                    # Pausa tattica di 10 minuti per non ricomprare subito
                                    await asyncio.sleep(600)
                                    break # Esce dal for loop dei symbol
                                except Exception as e_trade:
                                    logging.error(f"Errore nello Spazzare {bitget_sym}: {e_trade}")

        except Exception as e:
            logging.error(f"Errore connessione WebSocket Liquidazioni: {e}")
            await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(listen_liquidations())
