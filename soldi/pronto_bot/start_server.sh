#!/bin/bash
source /home/sergio/.openclaw/workspace/denaro/trading_bot_env/bin/activate
pip install flask python-dotenv requests
nohup python3 /home/sergio/.openclaw/workspace/denaro/pronto_bot/app.py > /home/sergio/.openclaw/workspace/denaro/pronto_bot/bot.log 2>&1 &
echo $! > /home/sergio/.openclaw/workspace/denaro/pronto_bot/bot.pid
