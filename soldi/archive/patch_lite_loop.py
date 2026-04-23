with open("/home/sergio/.openclaw/workspace/denaro/lite_guardian.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "if __name__ == \"__main__\":" in line:
        new_lines.append("    while True:\n")
        new_lines.append("        for name, script in BOT_REGISTRY.items():\n")
        new_lines.append("            if not is_running(script):\n")
        new_lines.append("                logger.info(f\"{name} is not running, starting...\")\n")
        new_lines.append("                start_bot(name, script)\n")
        new_lines.append("                time.sleep(2)\n")
        new_lines.append("        time.sleep(15)\n\n")
    new_lines.append(line)

with open("/home/sergio/.openclaw/workspace/denaro/lite_guardian.py", "w") as f:
    f.writelines(new_lines)
