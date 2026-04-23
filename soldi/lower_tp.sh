# Nuvola
sed -i 's/TAKE_PROFIT = 1.004/TAKE_PROFIT = 1.002/g' /home/sergio/.openclaw/workspace/denaro/squadra_delta_orderflow.py
sed -i 's/STOP_LOSS = 0.995/STOP_LOSS = 0.997/g' /home/sergio/.openclaw/workspace/denaro/squadra_delta_orderflow.py
sed -i 's/target_eur = 100.0/target_eur = 20.0/g' /home/sergio/.openclaw/workspace/denaro/sniper_squad.py

# MC2
ssh -p 2222 sergio@93.43.252.114 "sed -i 's/tp = exchange.price_to_precision(symbol, current_price \* 1.008)/tp = exchange.price_to_precision(symbol, current_price * 1.003)/g' /home/sergio/autonomous_bot/*.py"
ssh -p 2222 sergio@93.43.252.114 "sed -i 's/tp = exchange.price_to_precision(symbol, current_price \* 0.992)/tp = exchange.price_to_precision(symbol, current_price * 0.997)/g' /home/sergio/autonomous_bot/*.py"
ssh -p 2222 sergio@93.43.252.114 "sudo systemctl restart bot-snipers bot-predators bot-ghosts bot-darkarts"

# NY (MC5)
ssh -i /home/sergio/.ssh/newyork.pem -o StrictHostKeyChecking=no ubuntu@52.207.9.162 "sed -i 's/TAKE_PROFIT = 1.004/TAKE_PROFIT = 1.0015/g' /home/ubuntu/workspace/denaro/*.py"
ssh -i /home/sergio/.ssh/newyork.pem -o StrictHostKeyChecking=no ubuntu@52.207.9.162 "sudo systemctl restart newyork-guardian"

