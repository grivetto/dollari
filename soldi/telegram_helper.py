def send_alert(msg):
    try:
        import os, requests
        from dotenv import load_dotenv
        load_dotenv()
        t = os.getenv('TELEGRAM_BOT_TOKEN')
        c = os.getenv('TELEGRAM_CHAT_ID', '277954993')
        requests.post(f'https://api.telegram.org/bot{t}/sendMessage', 
                      json={'chat_id': c, 'text': f'🤖 Grid Bot V2\n{msg}'})
    except: pass
