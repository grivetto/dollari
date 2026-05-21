#!/usr/bin/env bash
set -euo pipefail

# ── Hermes Alpha Engine Deploy Script ──────────────────────────────
# Deploys the engine to mc2 server as a systemd service

SERVER="${1:-mc2}"
USER="sergio"
REMOTE_DIR="/home/${USER}/hermes_alpha"
LOCAL_DIR="/home/${USER}/hermes_alpha"
SERVICE_NAME="alpha-engine"

echo "🚀 Hermes Alpha Engine — Deploy to ${SERVER}"
echo "═══════════════════════════════════════════"

# 1. Create remote directory structure
echo "📁 Creating remote directory..."
ssh "${USER}@${SERVER}" "mkdir -p ${REMOTE_DIR}/config ${REMOTE_DIR}/strategies ${REMOTE_DIR}/logs"

# 2. Copy files (rsync or scp)
echo "📦 Copying files..."
rsync -avz --progress \
  "${LOCAL_DIR}/engine.py" \
  "${LOCAL_DIR}/connector.py" \
  "${LOCAL_DIR}/risk_manager.py" \
  "${LOCAL_DIR}/opportunity_scorer.py" \
  "${LOCAL_DIR}/performance_tracker.py" \
  "${LOCAL_DIR}/requirements.txt" \
  "${USER}@${SERVER}:${REMOTE_DIR}/"

rsync -avz --progress \
  "${LOCAL_DIR}/config/alpha_config.json" \
  "${USER}@${SERVER}:${REMOTE_DIR}/config/"

rsync -avz --progress \
  "${LOCAL_DIR}/strategies/"*.py \
  "${USER}@${SERVER}:${REMOTE_DIR}/strategies/"

# 3. Copy .env from denaro (shared API keys)
echo "🔑 Ensuring API keys..."
ssh "${USER}@${SERVER}" "cp -n /home/${USER}/denaro/.env ${REMOTE_DIR}/.env 2>/dev/null || echo 'Using existing .env'"

# 4. Install dependencies
echo "📦 Installing Python dependencies..."
ssh "${USER}@${SERVER}" "cd ${REMOTE_DIR} && python3 -m venv venv 2>/dev/null || true"
ssh "${USER}@${SERVER}" "cd ${REMOTE_DIR} && source venv/bin/activate && pip install -r requirements.txt -q"

# 5. Create systemd service
echo "⚙️ Creating systemd service..."
ssh "${USER}@${SERVER}" "sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null" << 'SERVICEFILE'
[Unit]
Description=Hermes Alpha Engine — Self-Learning Trading System
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=sergio
WorkingDirectory=/home/sergio/hermes_alpha
EnvironmentFile=/home/sergio/hermes_alpha/.env
ExecStart=/home/sergio/hermes_alpha/venv/bin/python engine.py
Restart=on-failure
RestartSec=15
StandardOutput=append:/home/sergio/hermes_alpha/logs/service.log
StandardError=append:/home/sergio/hermes_alpha/logs/service.error

[Install]
WantedBy=multi-user.target
SERVICEFILE

# 6. Enable and start service
echo "▶️ Enabling and starting service..."
ssh "${USER}@${SERVER}" "sudo systemctl daemon-reload && sudo systemctl enable ${SERVICE_NAME}.service && sudo systemctl restart ${SERVICE_NAME}.service"

# 7. Verify
sleep 2
echo ""
echo "📋 Service status:"
ssh "${USER}@${SERVER}" "sudo systemctl status ${SERVICE_NAME}.service --no-pager"

echo ""
echo "✅ Done! Check logs with:"
echo "  sudo journalctl -u ${SERVICE_NAME} -f"
echo "  tail -f ${REMOTE_DIR}/logs/alpha_engine.log"
