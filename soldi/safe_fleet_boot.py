#!/usr/bin/env python3
"""
Optimized Safe Fleet Boot — Avvio batch di bot con watchdog RAM ottimizzato,
thread pool per concurrency controllata, monitoraggio memoria e CPU efficiente,
invio Telegram ottimizzato e gestione dinamica dei batch.
"""
import os, time, subprocess, gc, threading, signal
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil

WORKSPACE = "/home/sergio/.openclaw/workspace/denaro"
VENV_PY = f"{WORKSPACE}/trading_bot_env/bin/python3"
if not os.path.exists(VENV_PY):
    VENV_PY = "/usr/bin/python3"

TG_TOKEN = "os.getenv("TELEGRAM_TOKEN")"
TG_CHAT = "277954993"

# Parametri base (dinamici)
MEM_THRESHOLD = 85          # soglia RAM % per pausa
BATCH_SIZE = 3              # numero bot per batch
DELAY_BETWEEN = 2           # secondi tra avvii nello stesso batch (ridotto)
DELAY_BETWEEN_BATCHES = 10  # secondi tra batch
MAX_WAIT_MEM = 60           # secondi max attesa se RAM alta
MAX_BATCH_RUNTIME = 300     # massimo secondi per completare un batch (evita hang)
TELEGRAM_RETRY_LIMIT = 3    # tentativi invio Telegram
TELEGRAM_BACKOFF = 2        # fattore backoff secondi

# Stato globale
_mem_pause_event = threading.Event()  # set quando RAM alta -> pausa avvii
_mem_pause_event.set()  # inizialmente permette avvii (non in pausa)
_batch_lock = threading.Lock()
_shutdown = False

def get_ram_percent():
    """Uso diretto di psutil per efficienza"""
    return psutil.virtual_memory().percent

def get_cpu_percent():
    return psutil.cpu_percent(interval=None, percpu=False)

def mem_watchdog(interval=2):
    """Monitora RAM in background e segnala pausa/ripresa avvii"""
    global _shutdown
    while not _shutdown:
        mem = get_ram_percent()
        if mem >= MEM_THRESHOLD:
            if _mem_pause_event.is_set():
                _mem_pause_event.clear()
                print(f"⚠️ RAM {mem}% >= soglia {MEM_THRESHOLD}% → pausa avvii")
        else:
            if not _mem_pause_event.is_set():
                _mem_pause_event.set()
                print(f"✅ RAM {mem}% < soglia {MEM_THRESHOLD}% → riprendi avvii")
        time.sleep(interval)

def is_running(script):
    """Controllo leggero se lo script è già in esecuzione"""
    base = os.path.basename(script)
    try:
        # Usa pgrep solo se necessario, ma è accettabile per pochi bot
        result = subprocess.run(["pgrep", "-f", base], capture_output=True, text=True)
        return result.returncode == 0 and bool(result.stdout.strip())
    except Exception:
        return False

def start_bot(script):
    """Avvia un singolo bot e restituisce il PID o None"""
    path = os.path.join(WORKSPACE, script)
    if not os.path.exists(path):
        print(f"[WARN] Script mancante: {script}")
        return None
    try:
        # Usa start_new_session per isolamento
        p = subprocess.Popen(
            [VENV_PY, path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=WORKSPACE,
            start_new_session=True
        )
        pid = p.pid
        print(f"[INFO] Avviato {script} (PID: {pid})")
        return pid
    except Exception as e:
        print(f"[ERROR] Impossibile avviare {script}: {e}")
        return None

def launch_batch(bot_list):
    """Avvia una lista di bot usando thread pool, rispettando pausa RAM"""
    # Attendi se siamo in pausa a causa di RAM alta
    _mem_pause_event.wait()
    # Rispetta anche eventuale shutdown
    if _shutdown:
        return []
    
    started = []
    with ThreadPoolExecutor(max_workers=len(bot_list)) as executor:
        future_to_script = {executor.submit(start_bot, script): script for script in bot_list}
        for future in as_completed(future_to_script, timeout=MAX_BATCH_RUNTIME):
            script = future_to_script[future]
            try:
                pid = future.result(timeout=DELAY_BETWEEN)
                if pid:
                    started.append((script, pid))
            except Exception as e:
                print(f"[ERROR] Timeout/errore avvio {script}: {e}")
    return started

def send_telegram(msg):
    """Invio Telegram ottimizzato con retry e backoff"""
    for attempt in range(TELEGRAM_RETRY_LIMIT):
        try:
            subprocess.run([
                "curl", "-s", "-X", "POST",
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                "-d", f"chat_id={TG_CHAT}",
                "-d", f"text={msg}",
            ], capture_output=True, timeout=8, check=True)
            return True
        except subprocess.TimeoutExpired:
            print(f"[WARN] Timeout Telegram (tentativo {attempt+1})")
        except subprocess.CalledProcessError as e:
            print(f"[WARN] Errore Telegram (tentativo {attempt+1}): {e}")
        if attempt < TELEGRAM_RETRY_LIMIT - 1:
            time.sleep(TELEGRAM_BACKOFF ** attempt)
    print("[ERROR] Fallito invio Telegram dopo tutti i tentativi")
    return False

def main():
    global _shutdown
    print(f"🚀 Safe Fleet Boot ottimizzato avviato")
    print(f"   Soglia RAM: {MEM_THRESHOLD}% | Batch size: {BATCH_SIZE}")
    print(f"   Delay tra bot: {DELAY_BETWEEN}s | Delay tra batch: {DELAY_BETWEEN_BATCHES}s")
    
    # Avvia watchdog memoria in background
    wd_thread = threading.Thread(target=mem_watchdog, daemon=True)
    wd_thread.start()
    
    # Notifica avvio
    send_telegram(f"🛡️ Safe Fleet Boot avviato — Soglia RAM: {MEM_THRESHOLD}%, Batch: {BATCH_SIZE}")
    
    # Determina bot da avviare (quelli non già in esecuzione)
    to_start = [b for b in ALL_BOTS if not is_running(b)]
    total = len(to_start)
    started_count = 0
    batch_num = 0
    
    print(f"📊 Bot da avviare: {total} (già attivi: {len(ALL_BOTS) - total})")
    
    try:
        for i in range(0, total, BATCH_SIZE):
            if _shutdown:
                break
            batch = to_start[i:i+BATCH_SIZE]
            batch_num += 1
            
            # Attendi eventuale pausa RAM prima del batch
            _mem_pause_event.wait()
            
            # Avvia batch
            started = launch_batch(batch)
            started_count += len(started)
            
            # Stato dopo batch
            ram = get_ram_percent()
            cpu = get_cpu_percent()
            bot_names = [f"{s}(PID:{p})" for s, p in started]
            status = f"✅ Batch #{batch_num}: {', '.join(bot_names) if bot_names else 'Nessuno'} | RAM: {ram}% | CPU: {cpu}% | Totale: {started_count}/{total}"
            print(status)
            
            # Notifica Telegram ogni 3 batch o alla fine
            if batch_num % 3 == 0 or i + BATCH_SIZE >= total:
                tg_msg = f"🔱 Fleet Boot — Batch {batch_num} completato | {started_count}/{total} bot avviati | RAM: {ram}% | CPU: {cpu}%"
                send_telegram(tg_msg)
            
            # Pausa tra batch (rispettando eventuale pausa RAM)
            time.sleep(DELAY_BETWEEN_BATCHES)
            # Durante la pausa, continuiamo a controllare RAM tramite watchdog
    except KeyboardInterrupt:
        print("\n[INFO] Interruzione ricevuta, arresto graceful...")
    finally:
        _shutdown = True
        # Attendi che il watchdog termini (daemon thread)
        wd_thread.join(timeout=2)
        
        # Report finale
        ram_final = get_ram_percent()
        cpu_final = get_cpu_percent()
        final_online = sum(1 for b in ALL_BOTS if is_running(b))
        msg = f"""🔱 Safe Fleet Boot COMPLETATO 🚀

✅ Bot online: {final_online}/{len(ALL_BOTS)}
📊 RAM: {ram_final}% | CPU: {cpu_final}%
⚙️ Soglia sicurezza: {MEM_THRESHOLD}%

La macchina è pronta a generare denaro! 💰"""
        print(msg)
        send_telegram(msg)

if __name__ == "__main__":
    main()