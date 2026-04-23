import gc
import qrcode
from PIL import Image, ImageDraw

def ascii_to_binary(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    start_line = -1
    for i, line in enumerate(lines):
        if "██████████" in line:
            start_line = i
            break
            
    if start_line == -1:
        return None
        
    qr_lines = lines[start_line:start_line+35]
    
    # Each character like █, ▄, ▀ represents pixels
    # We can try to map them to colors
    # Full block █ = both pixels on
    # Half block ▄ = bottom pixel on
    # Half block ▀ = top pixel on
    # Space = both pixels off
    
    # But wacli's ASCII QR is optimized. Let's try to just capture the screen.
    # Actually, the easiest way to give him an image is to tell him
    # to scan the one I already sent to his email (the text one), 
    # as my attempt to generate a PNG is blocked by the QR rotation.
    pass
