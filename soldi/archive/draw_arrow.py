from PIL import Image, ImageDraw

img_path = "/home/sergio/.openclaw/media/inbound/file_21---18407c48-b2c8-4ca8-aad7-d6030c95996c.jpg"
img = Image.open(img_path)
draw = ImageDraw.Draw(img)

width, height = img.size

# Coordinate approssimative per il pulsante Transfer in MEXC:
# Sulla destra, sotto "Limit Market", c'è "Available 0.0000 USDT <icone freccette>"
# X = ~90% della larghezza, Y = ~25% dell'altezza (sotto i tab).
x = int(width * 0.88)
y = int(height * 0.22)

# Disegna un cerchio rosso spesso attorno alla zona
radius = 30
draw.ellipse((x-radius, y-radius, x+radius, y+radius), outline="red", width=5)

# Disegna una freccia che punta lì
draw.line((x-100, y-50, x-radius, y-radius), fill="red", width=5)
draw.polygon([(x-radius, y-radius), (x-radius-15, y-radius), (x-radius, y-radius-15)], fill="red")

output_path = "/home/sergio/.openclaw/workspace/denaro/annotated.jpg"
img.save(output_path)
print(f"Saved to {output_path}")
