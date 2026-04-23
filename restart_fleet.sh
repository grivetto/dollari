#!/bin/bash
# restart_fleet.sh - Utility for restarting the trading fleet

# Detect workspace path
if [ -d "/home/sergio/denaro" ]; then
    WORKSPACE="/home/sergio/denaro"
elif [ -d "/home/marco/denaro" ]; then
    WORKSPACE="/home/marco/denaro"
else
    echo "❌ Workspace not found!"
    exit 1
fi

echo "🚀 Restarting fleet in $WORKSPACE..."

# Kill any existing trading bots to avoid duplicates
pkill -f "python3 $WORKSPACE"

# Find bot files using a set of patterns
# We look for: legion_*.py, *bot*.py, *scalper*.py, *hunter*.py, *sniper*.py, *grid*.py
BOTS=$(find "$WORKSPACE" -maxdepth 1 -name "*.py" | grep -E "legion_|bot|scalper|hunter|sniper|grid")

if [ -z "$BOTS" ]; then
    echo "❌ No bot files found!"
    exit 1
fi

for bot in $BOTS; do
    echo "Starting $bot..."
    nohup python3 "$bot" > /dev/null 2>&1 &
done

echo "✅ All bots launched. Verifying..."
sleep 2
ps aux | grep python3 | grep "$WORKSPACE" | grep -v grep
