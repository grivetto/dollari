cat << 'HEREDOC' > /home/sergio/autonomous_bot/kill_zombies.py
import ccxt, os, time
from dotenv import load_dotenv

load_dotenv('/home/sergio/autonomous_bot/.env')
exchange = ccxt.bitget({
    'apiKey': os.getenv('BINANCE_API_KEY'), # Wait, BITGET keys!
    'secret': os.getenv('BINANCE_API_SECRET'),
})
# Let's just use what's already on MC2:
# brain.py imports ccxt and does it!
HEREDOC
