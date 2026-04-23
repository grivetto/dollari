import json, os, time, logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [TARGET ENFORCER 🛑] - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/AUTO_HEALER.log")])

def check_target_and_enforce():
    try:
        # Get profit
        try:
            pt = float(__import__("json").load(open("/home/sergio/.openclaw/workspace/denaro/total_usdt_cache.json")).get("total_usdt", 0)) - float(__import__("json").load(open("/home/sergio/.openclaw/workspace/denaro/midnight_balance.json")).get("balance", 0))
        except: pt = 0.0

        # Get target
        try:
            with open("/home/sergio/.openclaw/workspace/denaro/daily_mission.json", "r") as f:
                target = float(json.load(f).get("target_eur", 10.0))
        except: target = 10.0

        if pt >= target:
            logging.warning(f"TARGET GLOBALE RAGGIUNTO! ({pt:.2f} >= {target:.2f}). Spengo l'artiglieria su MC2...")
            os.system("sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 'sudo systemctl stop bot-snipers bot-predators bot-ghosts bot-darkarts'")
            with open("/home/sergio/.openclaw/workspace/denaro/mc2_paused.flag", "w") as f: f.write("1")
        else:
            if os.path.exists("/home/sergio/.openclaw/workspace/denaro/mc2_paused.flag"):
                logging.info("Target non ancora raggiunto, ma MC2 era in pausa. Lo riattivo!")
                os.system("sudo ssh -p 2222 -o StrictHostKeyChecking=no sergio@93.43.252.114 'sudo systemctl start bot-snipers bot-predators bot-ghosts bot-darkarts'")
                os.remove("/home/sergio/.openclaw/workspace/denaro/mc2_paused.flag")
                
    except Exception as e:
        logging.error(f"Errore Target Enforcer: {e}")

if __name__ == "__main__":
    while True:
        check_target_and_enforce()
        time.sleep(60)
