# Make PREDATORS Trend Followers (TP +3%, SL -1%)
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/tp = exchange.price_to_precision(symbol, price \* 1.003)/tp = exchange.price_to_precision(symbol, price * 1.03)/g' /home/sergio/autonomous_bot/predators.py"
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/tp = exchange.price_to_precision(symbol, price \* 0.997)/tp = exchange.price_to_precision(symbol, price * 0.97)/g' /home/sergio/autonomous_bot/predators.py"
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/sl = exchange.price_to_precision(symbol, price \* 0.996)/sl = exchange.price_to_precision(symbol, price * 0.99)/g' /home/sergio/autonomous_bot/predators.py"
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/sl = exchange.price_to_precision(symbol, price \* 1.004)/sl = exchange.price_to_precision(symbol, price * 1.01)/g' /home/sergio/autonomous_bot/predators.py"

# Make DARK ARTS High-Leverage Breakout Hunters (TP +5%, SL -1.5%)
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/tp = exchange.price_to_precision(symbol, price \* 1.003)/tp = exchange.price_to_precision(symbol, price * 1.05)/g' /home/sergio/autonomous_bot/dark_arts.py"
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/tp = exchange.price_to_precision(symbol, price \* 0.997)/tp = exchange.price_to_precision(symbol, price * 0.95)/g' /home/sergio/autonomous_bot/dark_arts.py"
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/sl = exchange.price_to_precision(symbol, price \* 0.996)/sl = exchange.price_to_precision(symbol, price * 0.985)/g' /home/sergio/autonomous_bot/dark_arts.py"
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/sl = exchange.price_to_precision(symbol, price \* 1.004)/sl = exchange.price_to_precision(symbol, price * 1.015)/g' /home/sergio/autonomous_bot/dark_arts.py"

sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sudo systemctl restart bot-predators bot-darkarts"
