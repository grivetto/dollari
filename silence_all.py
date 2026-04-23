import os
import glob

# Modifichiamo TUTTI i file python di Nuvola per iniettare disable_notification: True in qualsiasi requests.post
files = glob.glob("/home/sergio/.openclaw/workspace/denaro/*.py")
for file in files:
    with open(file, 'r') as f:
        content = f.read()
    
    if "api.telegram.org" in content and "requests" in content:
        # Aggiungi disable_notification=True in stringhe JSON manuali e payload dict
        content = content.replace('json={"chat_id": chat_id, "text": msg, "disable_notification": True}', 'json={"chat_id": chat_id, "text": msg, "disable_notification": True}')
        content = content.replace('json={"chat_id": chat_id, "text": msg, "reply_markup": guest_kb, "disable_notification": True}', 'json={"chat_id": chat_id, "text": msg, "reply_markup": guest_kb, "disable_notification": True}')
        content = content.replace('json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown", "reply_markup": guest_kb, "disable_notification": True}', 'json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown", "reply_markup": guest_kb, "disable_notification": True}')
        content = content.replace('json={"chat_id": chat_id, "text": arch, "parse_mode": "Markdown", "reply_markup": guest_kb, "disable_notification": True}', 'json={"chat_id": chat_id, "text": arch, "parse_mode": "Markdown", "reply_markup": guest_kb, "disable_notification": True}')
        
        # Per i dict 'payload'
        if "payload = {" in content and "disable_notification" not in content:
            content = content.replace('payload = {', 'payload = {"disable_notification": True, ')
            
        with open(file, 'w') as f:
            f.write(content)
            
print("Tutti i bot Telegram su Nuvola sono stati silenziati alla radice.")
