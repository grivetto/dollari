#!/bin/bash
# Git Auto Push — Esegue push automatico con timestamp

REPO="/home/sergio/.openclaw/workspace/denaro"
cd "$REPO" || exit 1

# Verifica modifiche
if git diff --quiet && git diff --cached --quiet; then
    echo "$(date): Nessuna modifica da pushare"
    exit 0
fi

# Add, commit, push
git add -A
git commit -m "auto: update $(date '+%Y-%m-%d %H:%M')"
git push origin refactoring

echo "$(date): Push completato su refactoring"
