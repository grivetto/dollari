# MC2
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/tp = exchange.price_to_precision(symbol, current_price \* 1.008)/tp = exchange.price_to_precision(symbol, current_price * 1.003)/g' /home/sergio/autonomous_bot/*.py"
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/tp = exchange.price_to_precision(symbol, current_price \* 0.992)/tp = exchange.price_to_precision(symbol, current_price * 0.997)/g' /home/sergio/autonomous_bot/*.py"
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sudo systemctl restart bot-snipers bot-predators bot-ghosts bot-darkarts"
