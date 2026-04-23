with open('/home/sergio/.openclaw/workspace/denaro/telegram_bot_interactive.py', 'r') as f:
    content = f.read()

content = content.replace('payload = {"chat_id": chat_id, "text": resp_text, "reply_markup": markup}', 'payload = {"chat_id": chat_id, "text": resp_text, "reply_markup": markup, "disable_notification": True}')

with open('/home/sergio/.openclaw/workspace/denaro/telegram_bot_interactive.py', 'w') as f:
    f.write(content)
