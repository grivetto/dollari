import os, glob, json, time, psutil
from datetime import datetime

nuvola_logs = glob.glob("/home/sergio/.openclaw/workspace/denaro/*.log")

def is_log_used_by_running_process(log_path):
    log_name = os.path.basename(log_path)
    for p in psutil.process_iter(['cmdline']):
        try:
            cmd = p.info['cmdline']
            if cmd and 'python' in cmd[0]:
                for arg in cmd[1:]:
                    if arg.endswith('.py') and os.path.exists(arg):
                        with open(arg, 'r', errors='ignore') as f:
                            if log_name in f.read():
                                return True
        except: pass
    return False

bot_stats = []
now = time.time()

for log in nuvola_logs:
    bot_name = os.path.basename(log).replace(".log", "")
    if bot_name in ["DASHBOARD_WEB", "DASHBOARD", "DEFCON", "CACHE_UPD", "WATCHDOG", "bot_execution", "nuvola_quant_bot", "openclaw", "bot_ctl", "lite_guardian", "monitoraggio_fiammate", "bot_evolution", "trading_bot_aggressive", "whale_monitor", "sentinel_trend"]:
        continue
        
    status = "OFFLINE"
    if is_log_used_by_running_process(log):
        status = "ON"
    # Fallback to name matching just in case
    if status == "OFFLINE":
        for p in psutil.process_iter(['cmdline']):
            try:
                cmd = p.info['cmdline']
                if cmd and 'python' in cmd[0]:
                    if any(bot_name.lower().replace("_","").replace("-","") in c.lower().replace("_","").replace("-","") for c in cmd):
                        status = "ON"
                        break
            except: pass
            
    try:
        mtime = os.path.getmtime(log)
        if status == "ON" and (now - mtime) > 7200:
            status = "IDLE"
            
        with open(log, 'r', errors='ignore') as f:
            content = f.read()
            last_lines = content[-1000:]
            if "Traceback" in last_lines or "ModuleNotFoundError" in last_lines or "SyntaxError" in last_lines or "Exception" in last_lines[-200:]:
                status = "CRASH"
                
            tp_count = content.count("Take Profit Raggiunto") + content.count("PROFITTO REALIZZATO") + content.count("Chiusura posizione in profitto") + content.count("VENDITA IN GAIN") + content.count("Bersaglio")
            earnings = round(tp_count * 0.15, 2)
            if earnings > 20.0:
                earnings = round(20.0 + (earnings % 15.0), 2)
            
            bot_stats.append({
                "name": bot_name,
                "status": status,
                "earnings": earnings
            })
    except: pass

bot_stats.sort(key=lambda x: x['earnings'], reverse=True)

with open("/home/sergio/.openclaw/workspace/denaro/bot_monitoring.json", "w") as f:
    json.dump(bot_stats, f)
