sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/sl = exchange.price_to_precision(symbol, price \* 0.985)/sl = exchange.price_to_precision(symbol, price * 0.996)/g' /home/sergio/autonomous_bot/dark_arts.py"
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/sl = exchange.price_to_precision(symbol, price \* 1.015)/sl = exchange.price_to_precision(symbol, price * 1.004)/g' /home/sergio/autonomous_bot/dark_arts.py"

sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/sl = exchange.price_to_precision(symbol, price \* 0.992)/sl = exchange.price_to_precision(symbol, price * 0.996)/g' /home/sergio/autonomous_bot/ghosts.py"
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/sl = exchange.price_to_precision(symbol, price \* 1.008)/sl = exchange.price_to_precision(symbol, price * 1.004)/g' /home/sergio/autonomous_bot/ghosts.py"

sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/sl = exchange.price_to_precision(symbol, price \* 0.99)/sl = exchange.price_to_precision(symbol, price * 0.996)/g' /home/sergio/autonomous_bot/predators.py"
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/sl = exchange.price_to_precision(symbol, price \* 1.01)/sl = exchange.price_to_precision(symbol, price * 1.004)/g' /home/sergio/autonomous_bot/predators.py"

sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/sl = exchange.price_to_precision(symbol, current_price \* 0.99)/sl = exchange.price_to_precision(symbol, current_price * 0.996)/g' /home/sergio/autonomous_bot/snipers.py"
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/sl = exchange.price_to_precision(symbol, current_price \* 1.01)/sl = exchange.price_to_precision(symbol, current_price * 1.004)/g' /home/sergio/autonomous_bot/snipers.py"

sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sudo systemctl restart bot-snipers bot-predators bot-ghosts bot-darkarts"
