# 🪐 ORBITAL COMMAND - DEPLOYMENT GUIDE (v1.0.0)

Questa guida illustra la procedura per clonare l'intera infrastruttura quantitativa "Orbital Command" su un nuovo server Linux (Ubuntu/Debian) vuoto.

## 🛠️ PREREQUISITI DI SISTEMA
- OS: Ubuntu 22.04 LTS o Debian 12
- RAM Minima: 8 GB (16 GB Consigliati per HFT/MEV)
- CPU: 4 Cores (Minimo)
- Swap: File di Swap da 10GB configurato (`fallocate -l 10G /swapfile`)
- Software: `python3`, `pip3`, `git`, `htop`, `tmux`, `curl`

---

## 🚀 FASE 1: CLONAZIONE E SETUP AMBIENTE

1. **Clona il Repository o Estrai il Backup:**
   ```bash
   mkdir -p ~/.openclaw/workspace/denaro
   cd ~/.openclaw/workspace/denaro
   tar -xzf orbital_command_backup.tar.gz
   ```

2. **Crea l'Ambiente Virtuale Python (Isolato per Sicurezza):**
   ```bash
   sudo apt update && sudo apt install -y python3-venv python3-pip
   python3 -m venv trading_bot_env
   source trading_bot_env/bin/activate
   ```

3. **Installa le Dipendenze Quantenziate:**
   ```bash
   pip install --upgrade pip
   pip install ccxt pandas numpy python-dotenv psutil websockets requests web3 eth-account
   ```
   *(Nota: Il pacchetto `web3` potrebbe richiedere compilatori C++: `sudo apt install build-essential`)*

---

## 🔑 FASE 2: INNESTO DELLE CHIAVI API E SEGRETI

Il sistema utilizza la libreria `dotenv` per isolare le chiavi. Devi creare i seguenti file nella root del progetto (`~/.openclaw/workspace/denaro/`):

1. **Crea il file `.env` (Binance Spot & Core):**
   ```env
   BINANCE_API_KEY=la_tua_chiave_binance
   BINANCE_API_SECRET=il_tuo_segreto_binance
   ```

2. **Crea il file `.env.bitget` (Bitget Futures & Hedging):**
   ```env
   BITGET_API_KEY=la_tua_chiave_bitget
   BITGET_API_SECRET=il_tuo_segreto_bitget
   BITGET_PASSWORD=la_tua_passphrase_bitget
   ```

3. **Crea il file `.env.mexc` (MEXC HFT Zero-Fee):**
   ```env
   MEXC_API_KEY=la_tua_chiave_mexc
   MEXC_API_SECRET=il_tuo_segreto_mexc
   ```

4. **Crea il file `.env.telegram` (Comando e Controllo):**
   ```env
   TELEGRAM_BOT_TOKEN=il_token_del_tuo_bot_botfather
   TELEGRAM_CHAT_ID=il_tuo_chat_id_personale
   ```

5. **Crea il file `.env.web3` (DeFi, MEV e Flash Loans):**
   ```env
   WEB3_WSS_URL=wss://arb-mainnet.g.alchemy.com/v2/LA_TUA_CHIAVE_ALCHEMY
   WEB3_PRIVATE_KEY=LA_TUA_CHIAVE_PRIVATA_METAMASK_ESADECIMALE
   ```

---

## ⚙️ FASE 3: ACCENSIONE DELL'ECOSISTEMA (BOOT-UP)

Per avviare la macchina, non devi lanciare i 50 bot manualmente. Esiste un singolo "Guardiano" che funge da Direttore d'Orchestra.

1. **Configura il Servizio di Sistema (Systemd) per l'Auto-Start:**
   Crea il file `/etc/systemd/system/denaro-lite-guardian.service`:
   ```ini
   [Unit]
   Description=Orbital Command Guardian Service
   After=network.target

   [Service]
   User=tuo_utente_linux
   WorkingDirectory=/home/tuo_utente_linux/.openclaw/workspace/denaro
   ExecStart=/home/tuo_utente_linux/.openclaw/workspace/denaro/trading_bot_env/bin/python3 lite_guardian.py
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

2. **Innesca il Guardiano:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable denaro-lite-guardian.service
   sudo systemctl start denaro-lite-guardian.service
   ```

Il Guardiano accenderà in automatico:
- Il RAM-Disk WebSocket a latenza zero (`orbital_websocket.py`).
- Lo Zabbix Watchdog per il monitoraggio hardware (`zabbix_watchdog.py`).
- La Cyberpunk Web Dashboard sulla porta 8080 (`dashboard_server.py`).
- Tutti i Bot Operativi (Sniper, Legione, Hedger, Pairs Trader, MEV Brain).

---

## 🌐 FASE 4: ESPOSIZIONE DASHBOARD E TELEMETRIA

Il server web espone nativamente l'interfaccia sulla porta locale `8080`.
Per esporla su Internet in sicurezza (HTTPS), utilizza NGINX come Reverse Proxy:

```nginx
server {
    listen 8443 ssl;
    server_name il_tuo_dominio.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

La tua infrastruttura istituzionale è ora clonata e letale. 🐺
