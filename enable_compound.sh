# Remove hardcoded 20.0 and restore compound calculation
for file in /home/sergio/.openclaw/workspace/denaro/sniper_squad.py /home/sergio/.openclaw/workspace/denaro/hunter_swarm.py /home/sergio/.openclaw/workspace/denaro/archive/omega_protocol.py; do
    sed -i 's/target_eur = 20.0  # OBIETTIVO FISSO A 100€ DA MEZZANOTTE/target_eur = usable_eur * TARGET_PERCENT if TARGET_FIXED_EUR <= 0 else TARGET_FIXED_EUR/g' "$file"
    sed -i 's/TARGET_FIXED_EUR = 10.0/TARGET_FIXED_EUR = 0.0/g' "$file"
    sed -i 's/TARGET_PERCENT = 0.04/TARGET_PERCENT = 0.022/g' "$file"
done
