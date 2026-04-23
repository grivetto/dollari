#!/usr/bin/env python3
"""
INFRASTRUCTURE AUDIT — Verifica completa ogni 6 ore
Controlla: risorse, sicurezza, backup, log
"""

import os
import subprocess
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/home/sergio/denaro/.env')

TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TG_CHAT = os.getenv('TELEGRAM_CHAT_ID', '277954993')

def send_report(title, message):
    """Invia report Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {
            'chat_id': TG_CHAT,
            'text': f"📊 <b>{title}</b>\n<pre>{message}</pre>",
            'parse_mode': 'HTML'
        }
        requests.post(url, payload, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def audit_resources():
    """Controlla risorse sistema"""
    report = []
    
    # CPU e RAM
    try:
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        report.append("=== MEMORIA ===")
        report.append(result.stdout)
    except:
        report.append("❌ Errore lettura memoria")
    
    # Disk
    try:
        result = subprocess.run(['df', '-h'], capture_output=True, text=True)
        report.append("\n=== DISCO ===")
        report.append(result.stdout)
    except:
        report.append("❌ Errore lettura disco")
    
    # Load average
    try:
        with open('/proc/loadavg', 'r') as f:
            load = f.read().strip()
            report.append(f"\n=== LOAD ===")
            report.append(f"Load avg: {load}")
    except:
        pass
    
    return "\n".join(report)

def audit_services():
    """Controlla servizi attivi"""
    report = ["\n=== SERVIZI ==="]
    
    services = ['denaro-realistic-grid', 'denaro-target-tracker']
    
    for svc in services:
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', svc],
                capture_output=True,
                text=True
            )
            status = "✅ UP" if result.returncode == 0 else "❌ DOWN"
            report.append(f"{svc}: {status}")
        except:
            report.append(f"{svc}: ❌ ERROR")
    
    return "\n".join(report)

def audit_logs():
    """Controlla errori recenti nei log"""
    report = ["\n=== ERRORI RECENTI (ultime 24h) ==="]
    
    log_files = [
        '/home/sergio/.openclaw/workspace/denaro/REALISTIC_GRID.log',
        '/home/sergio/.openclaw/workspace/denaro/logs/health.log'
    ]
    
    for log_file in log_files:
        try:
            if os.path.exists(log_file):
                result = subprocess.run(
                    ['grep', '-i', 'error\\|❌', log_file],
                    capture_output=True,
                    text=True
                )
                errors = result.stdout.strip().split('\n')[-5:]  # Ultime 5
                if errors[0]:
                    report.append(f"\n{log_file}:")
                    for e in errors:
                        report.append(f"  {e[:100]}")
            else:
                report.append(f"\n{log_file}: non trovato")
        except:
            pass
    
    return "\n".join(report)

def audit_security():
    """Controlli base sicurezza"""
    report = ["\n=== SICUREZZA ==="]
    
    # Check file .env permessi
    try:
        env_file = '/home/sergio/.openclaw/workspace/denaro/.env'
        stat = os.stat(env_file)
        perms = oct(stat.st_mode)[-3:]
        if perms == '600':
            report.append(f"✅ .env permissions: {perms}")
        else:
            report.append(f"⚠️ .env permissions: {perms} (dovrebbe essere 600)")
    except:
        report.append("❌ Errore check .env")
    
    # Check utenti loggati
    try:
        result = subprocess.run(['who'], capture_output=True, text=True)
        users = result.stdout.strip()
        if users:
            report.append(f"\nUtenti loggati:\n{users}")
        else:
            report.append("\n✅ Nessun utente loggato")
    except:
        pass
    
    return "\n".join(report)

def main():
    print(f"🔍 Audit infrastructure: {datetime.now()}")
    
    # Esegui audit
    resources = audit_resources()
    services = audit_services()
    logs = audit_logs()
    security = audit_security()
    
    # Compila report
    full_report = f"{resources}\n{services}\n{logs}\n{security}"
    
    # Invia Telegram (tronca se troppo lungo)
    if len(full_report) > 4000:
        full_report = full_report[:3900] + "\n... [troncato]"
    
    send_report(f"INFRASTRUCTURE AUDIT — {datetime.now().strftime('%H:%M')}", full_report)
    
    # Salva su file
    report_file = '/home/sergio/.openclaw/workspace/denaro/logs/audit.log'
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'a') as f:
        f.write(f"\n{'='*50}\nAudit: {datetime.now()}\n{'='*50}\n")
        f.write(full_report)
    
    print("✅ Audit completato")

if __name__ == "__main__":
    main()
