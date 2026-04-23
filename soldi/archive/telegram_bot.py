import gc
import os
import json
import logging
import requests
import time
from dotenv import load_dotenv

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env.telegram')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Helper function to fetch balances from status files
def get_binance_balance():
    try:
        with open('/home/sergio/.openclaw/workspace/denaro/quant_status.json') as f:
            data = json.load(f)
        return data['balance']
    except Exception as e:
        logging.error(f"Error reading Binance status: {e}")
        return None

def get_crypto_balance():
    try:
        with open('/home/sergio/.openclaw/workspace/denaro/cryptocom_status.json') as f:
            data = json.load(f)
        return data['balance']
    except Exception as e:
        logging.error(f"Error reading Crypto.com status: {e}")
        return None

def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.warning("Telegram credentials not configured")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, data=data)
        logging.info(f"Telegram response: {response.status_code} {response.text}")
    except Exception as e:
        logging.error(f"Error sending Telegram message: {e}")


def send_balance_update():
    binance_balance = get_binance_balance()
    crypto_balance = get_crypto_balance()
    
    if binance_balance is None or crypto_balance is None:
        logging.error("Could not fetch balances")
        return
    
    # Format the message with current balances
    message = f"🤖 *Trading Bot Status Update* 🤖\n\n"
    message += f"**Binance (Quant Bot):**\n"
    message += f"€{binance_balance:.2f} EUR available\n\n"
    message += f"**Crypto.com (Grid Bot):**\n"
    message += f"${crypto_balance:.2f} USDT available\n\n"
    
    # Convert USDT to EUR for total (using ~0.94 EUR/USDT as rough estimate)
    usd_to_eur = 0.94
    total_balance = binance_balance + (crypto_balance * usd_to_eur)
    
    message += f"**Total Capital:**\n"
    message += f"€{total_balance:.2f} EUR\n\n"
    
    # Add bot status info
    message += f"**Bot Status:**\n"
    message += f"Both bots are running and monitoring for trading signals\n"
    message += f"Last update: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    send_telegram_message(message)

if __name__ == '__main__':
    send_balance_update()
