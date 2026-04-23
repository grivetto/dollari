cd /root/workspace/denaro/
cp lite_guardian.py heavy_guardian.py

# Uncomment everything first
sed -i 's/# BOT_REGISTRY/BOT_REGISTRY/g' heavy_guardian.py
sed -i 's/#     BOT_REGISTRY/    BOT_REGISTRY/g' heavy_guardian.py

# Now comment out the ones running on Nuvola or MC2:
# SQUADRA_ALPHA, SQUADRA_DELTA, SQUADRA_GAMMA, KAMIKAZE, STROZZINO, CONTABILE_DCA, MEV_BRAIN, GARIBAN
# DASHBOARD, AUTO_HEALER, AI_RISK_ENGINE, BOT_STATUS_CACHE, TG-BOT, ORBITAL_WS

sed -i '/BOT_REGISTRY\["SQUADRA_/s/^/# /' heavy_guardian.py
sed -i '/BOT_REGISTRY\["KAMIKAZE/s/^/# /' heavy_guardian.py
sed -i '/BOT_REGISTRY\["STROZZINO/s/^/# /' heavy_guardian.py
sed -i '/BOT_REGISTRY\["CONTABILE_DCA/s/^/# /' heavy_guardian.py
sed -i '/BOT_REGISTRY\["MEV_BRAIN/s/^/# /' heavy_guardian.py
sed -i '/BOT_REGISTRY\["GARIBAN/s/^/# /' heavy_guardian.py
sed -i '/BOT_REGISTRY\["DASHBOARD/s/^/# /' heavy_guardian.py
sed -i '/BOT_REGISTRY\["AUTO_HEALER/s/^/# /' heavy_guardian.py
sed -i '/BOT_REGISTRY\["AI_RISK_ENGINE/s/^/# /' heavy_guardian.py
sed -i '/BOT_REGISTRY\["BOT_STATUS_CACHE/s/^/# /' heavy_guardian.py
sed -i '/BOT_REGISTRY\["TG-BOT/s/^/# /' heavy_guardian.py
sed -i '/BOT_REGISTRY\["ORBITAL_WS/s/^/# /' heavy_guardian.py

# Ensure correct python path for the heavy server
sed -i 's|/home/sergio/.openclaw/workspace/denaro/trading_bot_env/bin/python3|/root/workspace/denaro/trading_bot_env/bin/python3|g' heavy_guardian.py
sed -i 's|/home/sergio/.openclaw/workspace/denaro|/root/workspace/denaro|g' heavy_guardian.py

