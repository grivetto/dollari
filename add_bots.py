import re

with open('/home/sergio/.openclaw/workspace/denaro/dashboard_server.py', 'r') as f:
    text = f.read()

# Add Elemosiniere to Protocollo Trinity or Squadre? Let's add it to Squadre or a new section.
# Actually let's add them to the Squadre d'Assalto or Protocollo Trinity.
# L'Elemosiniere sounds like Protocollo Trinity or a special bot. Let's add to Protocollo Trinity.
# Il Kamikaze sounds like Squadre d'Assalto.

kamikaze_html = "<li><span>💣 <strong>Il Kamikaze</strong><br><small>Futures Bitget (High Risk)</small></span> <span class=\\\"status warn\\\">INNESCATO</span></li>"
elemosiniere_html = "<li><span>🤲 <strong>L'Elemosiniere</strong><br><small>Gariban Grid / Scavenger</small></span> <span class=\\\"status online\\\">RACCOGLIE</span></li>"

# Find Squadre d'Assalto list and append Kamikaze
text = text.replace("<li><span>⚖️ <strong>SQUADRA_GAMMA</strong><br><small>Pairs Trading su Bitget</small></span> <span class=\"status\">ALLINEATA</span></li>",
                    f"<li><span>⚖️ <strong>SQUADRA_GAMMA</strong><br><small>Pairs Trading su Bitget</small></span> <span class=\"status\">ALLINEATA</span></li>\\n                {kamikaze_html}")

# Find Protocollo Trinity list and append Elemosiniere
text = text.replace("<li><span>👼 <strong>L'Angelo Custode</strong><br><small>MEV Arbitrum</small></span> <span class=\"status online\">ONLINE</span></li>",
                    f"<li><span>👼 <strong>L'Angelo Custode</strong><br><small>MEV Arbitrum</small></span> <span class=\"status online\">ONLINE</span></li>\\n                {elemosiniere_html}")


with open('/home/sergio/.openclaw/workspace/denaro/dashboard_server.py', 'w') as f:
    f.write(text)

