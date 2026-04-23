
import datetime

# Percorso del file di coda
LOG_FILE = '/home/sergio/.openclaw/workspace/denaro/whatsapp_queue.log' # Default Nuvola

def send_whatsapp_alert(message):
    """Aggiunge un messaggio alla coda per Stella"""
    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_FILE, 'a') as f:
            f.write(f'[{timestamp}] {message}\n')
        return True
    except Exception as e:
        print(f"Errore scrittura coda: {e}")
        return False
