#!/usr/bin/env python3
"""
DCA DAILY — Dollar Cost Averaging automatico
Compra €1.50 di BTC ogni giorno alle 09:00 (se fondi sufficienti)
"""

import os
import logging
from datetime import datetime
from decimal import Decimal
import ccxt
import requests
from dotenv import load_dotenv

load_dotenv('/home/sergio/denaro/.env')

# Config
DCA_AMOUNT_EUR = 5.00  # €5.00 al giorno (Aggressivo)
MIN_EUR_BALANCE = 5.0  # Riserva minima
DCA_LOG = '/home/sergio/.openclaw/workspace/denaro/logs/dca.log'

TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TG_CHAT = os.getenv('TELEGRAM_CHAT_ID', '277954993')

logging.basicConfig(
    filename=DCA_LOG,
    level=logging.INFO,
    format='%(asctime)s - [DCA] - %(message)s'
)

def send_telegram(msg):
    """Invia notifica Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {
            'chat_id': TG_CHAT,
            'text': msg,
            'parse_mode': 'HTML'
        }
        requests.post(url, payload, timeout=10)
    except Exception as e:
        logging.error(f"Telegram error: {e}")

def dca_buy():
    """Esegue acquisto DCA"""
    try:
        # Connessione
        ex = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_API_SECRET'),
            'enableRateLimit': True,
        })
        
        # Verifica bilancio EUR
        bal = ex.fetch_balance()
        eur_free = bal.get('EUR', {}).get('free', 0)
        
        logging.info(f"Bilancio EUR: €{eur_free:.2f}")
        
        # Stop se fondi insufficienti
        if eur_free < MIN_EUR_BALANCE:
            msg = f"⚠️ <b>DCA FERMO</b>\nFondi insufficienti: €{eur_free:.2f}\nMinimo richiesto: €{MIN_EUR_BALANCE}"
            send_telegram(msg)
            logging.warning(f"DCA skipped: fondi insufficienti (€{eur_free:.2f})")
            return
        
        if eur_free < DCA_AMOUNT_EUR:
            msg = f"⚠️ <b>DCA FERMO</b>\nSolo €{eur_free:.2f} disponibili"
            send_telegram(msg)
            logging.warning(f"DCA skipped: meno di €{DCA_AMOUNT_EUR}")
            return
        
        # Calcola quantità BTC da comprare
        ticker = ex.fetch_ticker('BTC/EUR')
        price = ticker['last']
        btc_amount = DCA_AMOUNT_EUR / price
        
        logging.info(f"Prezzo BTC/EUR: €{price:,.2f}")
        logging.info(f"Quantità da comprare: {btc_amount:.8f} BTC")
        
        # Esegui market buy
        order = ex.create_market_buy_order('BTC/EUR', btc_amount)
        
        # Successo
        avg_price = order.get('average', order.get('price', price))
        total_cost = float(order['amount']) * float(avg_price)
        
        msg = f"""✅ <b>DCA ACQUISTO</b>
<b>Data:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
<b>Quantità:</b> {order['amount']:.8f} BTC
<b>Prezzo:</b> €{float(avg_price):,.2f}
<b>Totale:</b> €{total_cost:.2f}
<b>Rimanente:</b> €{eur_free - total_cost:.2f} EUR

📈 DCA continua domani!"""
        
        send_telegram(msg)
        logging.info(f"DCA completato: {order['amount']:.8f} BTC @ €{avg_price}")
        
        # Salva su file tracciamento
        dca_file = '/home/sergio/.openclaw/workspace/denaro/dca_tracking.json'
        import json
        
        data = {'acquisti': [], 'totale_btc': 0, 'totale_eur_speso': 0}
        if os.path.exists(dca_file):
            with open(dca_file, 'r') as f:
                data = json.load(f)
        
        data['acquisti'].append({
            'data': datetime.now().isoformat(),
            'eur_speso': total_cost,
            'btc_acquistato': float(order['amount']),
            'prezzo_medio': float(avg_price)
        })
        data['totale_btc'] += float(order['amount'])
        data['totale_eur_speso'] += total_cost
        
        with open(dca_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logging.info(f"Tracking aggiornato: totale BTC={data['totale_btc']:.8f}")
        
    except Exception as e:
        error_msg = f"❌ <b>DCA ERRORE</b>\n{str(e)[:200]}"
        send_telegram(error_msg)
        logging.error(f"Errore DCA: {e}")

if __name__ == "__main__":
    logging.info("DCA Daily avviato")
    dca_buy()
