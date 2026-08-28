import os
from PIL import Image, ImageEnhance

input_path = "/Users/sha/Sha portfolio/sha-portfolio/public/Adobe Express - file-7.png"
dark_svg_path = "/tmp/shachin-profile/assets/portrait-dark.svg"
light_svg_path = "/tmp/shachin-profile/assets/portrait-light.svg"
legacy_svg_path = "/tmp/shachin-profile/assets/portrait.svg"

# 1. Load image and keep transparency (RGBA is crucial here)
img = Image.open(input_path).convert("RGBA")

# Create a grayscale version JUST for calculating dot sizes
gray = img.convert("L")
enhancer = ImageEnhance.Contrast(gray)
gray_enhanced = enhancer.enhance(1.2)

# Grid dimensions
grid_cols = 75
cw, ch = img.size
grid_rows = int(grid_cols * (ch / cw))

# Resize both RGBA (for colors) and Grayscale (for dot sizes)
img_color = img.resize((grid_cols, grid_rows), Image.Resampling.LANCZOS)
img_gray = gray_enhanced.resize((grid_cols, grid_rows), Image.Resampling.LANCZOS)

spacing = 10
margin = 20
width_svg = grid_cols * spacing + margin * 2
height_svg = grid_rows * spacing + margin * 2

# CSS animations
css_lines = []
css_lines.append("@keyframes rv { from { opacity: 0; transform: scale(0.4); } to { opacity: 1; transform: scale(1); } }")
css_lines.append(".rw { animation: rv 0.45s cubic-bezier(0.16, 1, 0.3, 1) both; transform-origin: center; }")

max_delay = 2.5
for r in range(grid_rows):
    delay = (r / grid_rows) * max_delay
    css_lines.append(f".r{r} {{ animation-delay: {delay:.3f}s; }}")

css_block = "<style>" + "".join(css_lines) + "</style>"

# ─── LIGHT MODE SVG ───────────────────────────────────────────────────────────
light_content = []
light_content.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_svg} {height_svg}" width="{width_svg}" height="{height_svg}" role="img" aria-label="dot-matrix portrait">')
light_content.append(css_block)
light_content.append(f'<g transform="translate({margin}, {margin})">')

for r in range(grid_rows):
    light_content.append(f'<g class="rw r{r}">')
    for c in range(grid_cols):
        r_px, g_px, b_px, a_px = img_color.getpixel((c, r))
        
        # Skip transparent background
        if a_px < 50:
            continue
            
        # LIGHT MODE MATH: Darker pixels = Larger dots!
        gray_val = img_gray.getpixel((c, r))
        intensity = (255 - gray_val) / 255.0
        radius = round(1.0 + (intensity * 3.8), 2)
        
        cx = c * spacing + spacing / 2
        cy = r * spacing + spacing / 2
        
        hex_color = f"#{r_px:02x}{g_px:02x}{b_px:02x}"
        light_content.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{hex_color}" />')
    light_content.append('</g>')

light_content.append('</g>')
light_content.append('</svg>')

# ─── DARK MODE SVG ────────────────────────────────────────────────────────────
dark_content = []
dark_content.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_svg} {height_svg}" width="{width_svg}" height="{height_svg}" role="img" aria-label="dot-matrix portrait">')
dark_content.append(css_block)
dark_content.append(f'<g transform="translate({margin}, {margin})">')

for r in range(grid_rows):
    dark_content.append(f'<g class="rw r{r}">')
    for c in range(grid_cols):
        r_px, g_px, b_px, a_px = img_color.getpixel((c, r))
        
        if a_px < 50:
            continue
            
        # DARK MODE MATH: Lighter pixels = Larger dots!
        gray_val = img_gray.getpixel((c, r))
        intensity = gray_val / 255.0
        radius = round(1.0 + (intensity * 3.8), 2)
        
        cx = c * spacing + spacing / 2
        cy = r * spacing + spacing / 2
        
        hex_color = f"#{r_px:02x}{g_px:02x}{b_px:02x}"
        dark_content.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{hex_color}" />')
    dark_content.append('</g>')

dark_content.append('</g>')
dark_content.append('</svg>')

# Write files
with open(light_svg_path, "w", encoding="utf-8") as f:
    f.write("\n".join(light_content))

with open(dark_svg_path, "w", encoding="utf-8") as f:
    f.write("\n".join(dark_content))

with open(legacy_svg_path, "w", encoding="utf-8") as f:
    f.write("\n".join(dark_content))

pub_dir = "/Users/sha/Sha portfolio/sha-portfolio/public/images"
os.makedirs(pub_dir, exist_ok=True)
with open(os.path.join(pub_dir, "portrait-light.svg"), "w", encoding="utf-8") as f:
    f.write("\n".join(light_content))
with open(os.path.join(pub_dir, "portrait-dark.svg"), "w", encoding="utf-8") as f:
    f.write("\n".join(dark_content))
with open(os.path.join(pub_dir, "sha_matrix.svg"), "w", encoding="utf-8") as f:
    f.write("\n".join(dark_content))

print("Successfully generated portrait-light.svg with reversed math (dark pixels = large dots) and true RGB colors!")
