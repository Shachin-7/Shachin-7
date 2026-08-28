import os
import sys
import math
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

input_path = "/Users/sha/Sha portfolio/sha-portfolio/public/Adobe Express - file-7.png"
output_svg_path = "/tmp/shachin-profile/assets/portrait.svg"

img = Image.open(input_path)

# Convert to RGBA
if img.mode != "RGBA":
    img = img.convert("RGBA")

# Extract alpha channel to filter background
alpha = img.split()[3]

# Convert to grayscale for brightness evaluation
gray = img.convert("L")
# Enhance contrast slightly
gray = ImageOps.autocontrast(gray, cutoff=2)

cols = 90
w, h = gray.size
cell = w / cols
rows_count = int(h / cell)

# Color ramp from deep reddish black -> dark red -> warm amber -> bright yellow/white highlight
# Exact palette sampled from reference image:
palette_ramp = [
    (0.00, (15, 3, 0)),        # dark background / shadow (#0f0300)
    (0.15, (46, 5, 0)),        # deep red-brown (#2e0500)
    (0.30, (117, 37, 7)),      # dark amber (#752507)
    (0.45, (209, 61, 17)),     # rich orange-red (#d13d11)
    (0.60, (250, 123, 22)),    # vibrant orange (#fa7b16)
    (0.75, (255, 175, 33)),    # warm gold (#ffaf21)
    (0.90, (255, 222, 95)),    # bright yellow (#ffde5f)
    (1.00, (255, 248, 180)),   # glowing highlight (#fff8b4)
]

def get_ramped_color(val):
    val = max(0.0, min(1.0, val))
    for i in range(len(palette_ramp) - 1):
        t1, c1 = palette_ramp[i]
        t2, c2 = palette_ramp[i+1]
        if t1 <= val <= t2:
            ratio = (val - t1) / (t2 - t1)
            r = int(c1[0] + ratio * (c2[0] - c1[0]))
            g = int(c1[1] + ratio * (c2[1] - c1[1]))
            b = int(c1[2] + ratio * (c2[2] - c1[2]))
            return f"#{r:02x}{g:02x}{b:02x}"
    return "#fff8b4"

px_gray = gray.load()
px_alpha = alpha.load()

bmap = []
for row in range(rows_count):
    r_cells = []
    for col in range(cols):
        x0 = int(col * cell)
        x1 = int((col + 1) * cell)
        y0 = int(row * cell)
        y1 = int((row + 1) * cell)

        tot_b = 0
        tot_a = 0
        cnt = 0
        for y in range(y0, min(y1, h)):
            for x in range(x0, min(x1, w)):
                tot_b += px_gray[x, y]
                tot_a += px_alpha[x, y]
                cnt += 1
        
        avg_b = (tot_b / cnt) / 255.0 if cnt > 0 else 0
        avg_a = (tot_a / cnt) / 255.0 if cnt > 0 else 0
        
        # If alpha is transparent (background), set brightness to 0
        if avg_a < 0.2:
            avg_b = 0

        r_cells.append(avg_b)
    bmap.append(r_cells)

# Generate animated SVG with row reveal
max_r = cell * 0.46
svg_w = cell * cols
svg_h = cell * rows_count

RT = 2.5
RF = 0.45
delay_step = (RT - RF) / max(rows_count - 1, 1)

lines = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w:.1f} {svg_h:.1f}" width="{svg_w:.1f}" height="{svg_h:.1f}" role="img" aria-label="dot-matrix portrait">',
    '<style>',
    '@keyframes rv{from{opacity:0}to{opacity:1}}',
    f'.rw{{animation:rv {RF:.2f}s ease-out both}}'
]

for r in range(rows_count):
    lines.append(f'.r{r}{{animation-delay:{r * delay_step:.3f}s}}')

lines.append('</style>')
lines.append(f'<rect width="{svg_w:.1f}" height="{svg_h:.1f}" fill="#0d1117"/>')
lines.append(f'<g transform="translate({cell/2:.1f},{cell/2:.1f})">')

for r_idx, r_cells in enumerate(bmap):
    group_circles = []
    for c_idx, val in enumerate(r_cells):
        if val < 0.05:
            continue
        # Radius scale based on brightness
        radius = max_r * (0.3 + 0.7 * val)
        cx = c_idx * cell
        cy = r_idx * cell
        color = get_ramped_color(val)
        group_circles.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius:.2f}" fill="{color}"/>')

    if group_circles:
        lines.append(f'<g class="rw r{r_idx}">')
        lines.extend(group_circles)
        lines.append('</g>')

lines.append('</g>')
lines.append('</svg>')

with open(output_svg_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Successfully generated {output_svg_path} with warm amber palette!")
