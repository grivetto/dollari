import gc
import os, json, time, subprocess
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
TG_TOKEN = "os.getenv("TELEGRAM_TOKEN")"
TG_CHAT_ID = "277954993"

def get_total_balance():
    try:
        balances = client.get_account()['balances']
        total = 0
        prices = {t['symbol']: float(t['price']) for t in client.get_all_tickers() if t['symbol'].endswith('EUR')}
        for b in balances:
            qty = float(b['free']) + float(b['locked'])
            if qty <= 0: continue
            if b['asset'] == 'EUR': total += qty
            elif f"{b['asset']}EUR" in prices: total += qty * prices[f"{b['asset']}EUR"]
        return total
    except: return None

def main():
    last_bal = get_total_balance()
    import gc
    while True:
        gc.collect()
        time.sleep(300) # 5 minuti
        current_bal = get_total_balance()
        if current_bal and last_bal:
            profit = current_bal - last_bal
            if profit < 10.0:
                msg = f"⚡️ **TARGET ALERT**: {profit:.2f}€/5min (Target: 10€). Forzatura frequenza flotta in corso... 🔥"
                subprocess.run(["curl", "-s", "-X", "POST", f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", "-d", f"chat_id={TG_CHAT_ID}", "-d", f"text={msg}", "-d", "parse_mode=Markdown"])
            else:
                msg = f"🏆 **TARGET 10€ SUPERATO**: +{profit:.2f}€ in 5 minuti! 🚀💰"
                subprocess.run(["curl", "-s", "-X", "POST", f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", "-d", f"chat_id={TG_CHAT_ID}", "-d", f"text={msg}", "-d", "parse_mode=Markdown"])
            last_bal = current_bal

if __name__ == "__main__":
    main()
