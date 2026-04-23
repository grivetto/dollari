sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sed -i 's/TRADE_SIZE_USDT = 6.0/TRADE_SIZE_USDT = 9.0/g' /home/sergio/autonomous_bot/*.py"
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sudo systemctl restart bot-snipers bot-predators bot-ghosts bot-darkarts"
