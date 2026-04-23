sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sudo systemctl stop tg-reporter"
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "sudo systemctl disable tg-reporter"
sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 "pkill -f tg_reporter.py"
