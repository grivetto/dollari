
#!/bin/bash
# Script per creare un ZIP del dashboard React/Vue e caricarlo su GitHub

# Variabili
DASHBOARD_DIR="/home/sergio/.openclaw/workspace/denaro/dashboard"
ZIP_FILE="denaro-dashboard-react-v1.zip"
GITHUB_REPO="grivetto/money"
GITHUB_BRANCH="Production"
GITHUB_TOKEN="$GITHUB_TOKEN"

# Verifico che il token sia impostato
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Token GitHub non impostato. Imposta la variabile d'ambiente GITHUB_TOKEN." >&2
    exit 1
fi

# Creo il file ZIP
echo "📦 Creazione del file ZIP..."
cd "$DASHBOARD_DIR" || exit 1
zip -r "$ZIP_FILE" . || { echo "❌ Fallito la creazione del ZIP"; exit 1; }

# Carico il ZIP su GitHub (usando l'API GitHub)
echo "📤 Caricamento del ZIP su GitHub..."
GITHUB_API_URL="https://api.github.com/repos/$GITHUB_REPO/releases"

# Crea una nuova release (se non esiste già)
RELEASE_ID=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \ 
    -X POST \ 
    -H "Content-Type: application/json" \ 
    -d '{"tag_name": "v1.0", "name": "Dashboard React/Vue Denaro V3", "body": "Release del dashboard React/Vue per il sistema Denaro V3.", "draft": false}' \ 
    "$GITHUB_API_URL" | jq -r '.id')

if [ -z "$RELEASE_ID" ] || [ "$RELEASE_ID" == "null" ]; then
    echo "❌ Fallito la creazione della release. Controlla il token GitHub o il repository." >&2
    exit 1
fi

# Aggiungi il file ZIP alla release
UPLOAD_URL=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \ 
    -X POST \ 
    -H "Content-Type: application/octet-stream" \ 
    --data-binary "@$ZIP_FILE" \ 
    "$GITHUB_API_URL/$RELEASE_ID/assets?name=$ZIP_FILE" | jq -r '.browser_download_url')

if [ -z "$UPLOAD_URL" ] || [ "$UPLOAD_URL" == "null" ]; then
    echo "❌ Fallito il caricamento del file ZIP sulla release." >&2
    exit 1
fi

echo "✅ File ZIP caricato con successo! Visita: $UPLOAD_URL"
