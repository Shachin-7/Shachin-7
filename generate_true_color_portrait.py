import os
from PIL import Image, ImageEnhance, ImageOps

input_path = "/Users/sha/Sha portfolio/sha-portfolio/public/Adobe Express - file-7.png"
dark_svg_path = "/tmp/shachin-profile/assets/portrait-dark.svg"
light_svg_path = "/tmp/shachin-profile/assets/portrait-light.svg"
legacy_svg_path = "/tmp/shachin-profile/assets/portrait.svg"

# Load image with alpha
img = Image.open(input_path).convert("RGBA")
w, h = img.size

r, g, b, alpha = img.split()
img_rgb = Image.merge("RGB", (r, g, b))

gray = img_rgb.convert("L")
enhancer = ImageEnhance.Contrast(gray)
gray_enhanced = enhancer.enhance(1.5)

grid_cols = 75
cw, ch = img.size
grid_rows = int(grid_cols * (ch / cw))

img_small = img_rgb.resize((grid_cols, grid_rows), Image.Resampling.LANCZOS)
gray_small = gray_enhanced.resize((grid_cols, grid_rows), Image.Resampling.LANCZOS)
alpha_small = alpha.resize((grid_cols, grid_rows), Image.Resampling.LANCZOS)

spacing = 10
margin = 20
width_svg = grid_cols * spacing + margin * 2
height_svg = grid_rows * spacing + margin * 2

# Common animation CSS
css_lines = [
    "@keyframes rv { from { opacity: 0; transform: scale(0.4); } to { opacity: 1; transform: scale(1); } }",
    ".rw { animation: rv 0.45s cubic-bezier(0.16, 1, 0.3, 1) both; transform-origin: center; }"
]
max_delay = 2.5
for r_idx in range(grid_rows):
    delay = (r_idx / grid_rows) * max_delay
    css_lines.append(f".r{r_idx} {{ animation-delay: {delay:.3f}s; }}")

css_str = "<style>" + "".join(css_lines) + "</style>"

# ─── 1. DARK MODE PORTRAIT (portrait-dark.svg) ────────────────────────────────
dark_lines = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_svg} {height_svg}" width="{width_svg}" height="{height_svg}" role="img" aria-label="dot-matrix portrait">',
    css_str,
    f'<g transform="translate({margin}, {margin})">'
]

for r_idx in range(grid_rows):
    dark_lines.append(f'<g class="rw r{r_idx}">')
    for c_idx in range(grid_cols):
        a_val = alpha_small.getpixel((c_idx, r_idx))
        if a_val < 30:
            continue

        val = gray_small.getpixel((c_idx, r_idx))
        intensity = val / 255.0
        radius = round(1.2 + intensity * 3.4, 2)
        cx = c_idx * spacing + spacing / 2
        cy = r_idx * spacing + spacing / 2

        r_px, g_px, b_px = img_small.getpixel((c_idx, r_idx))
        hex_color = f"#{r_px:02x}{g_px:02x}{b_px:02x}"
        dark_lines.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{hex_color}" />')
    dark_lines.append('</g>')

dark_lines.append('</g>')
dark_lines.append('</svg>')

# ─── 2. LIGHT MODE PORTRAIT (portrait-light.svg) ──────────────────────────────
# In light mode:
# - Darker pixels (hair, eyes, shadows) generate LARGER & DARKER dots so face features pop!
# - Lighter pixels (skin highlights) generate smaller, warm-toned dots with darkened contrast.
light_lines = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_svg} {height_svg}" width="{width_svg}" height="{height_svg}" role="img" aria-label="dot-matrix portrait">',
    css_str,
    f'<g transform="translate({margin}, {margin})">'
]

for r_idx in range(grid_rows):
    light_lines.append(f'<g class="rw r{r_idx}">')
    for c_idx in range(grid_cols):
        a_val = alpha_small.getpixel((c_idx, r_idx))
        if a_val < 30:
            continue

        val = gray_small.getpixel((c_idx, r_idx))
        # INVERTED DOT SIZING for light mode: dark pixels = larger dots
        darkness = (255 - val) / 255.0
        radius = round(1.0 + darkness * 3.8, 2)

        cx = c_idx * spacing + spacing / 2
        cy = r_idx * spacing + spacing / 2

        # Extract RGB and apply dark-mode-contrast multiplication for light BG
        r_px, g_px, b_px = img_small.getpixel((c_idx, r_idx))
        
        # Darken light skin colors slightly so they are sharp against white background
        factor = 0.72 if val > 160 else 0.88
        r_dark = int(r_px * factor)
        g_dark = int(g_px * factor)
        b_dark = int(b_px * factor)
        hex_color = f"#{r_dark:02x}{g_dark:02x}{b_dark:02x}"

        light_lines.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{hex_color}" />')
    light_lines.append('</g>')

light_lines.append('</g>')
light_lines.append('</svg>')

# Save dark, light, and legacy fallback SVGs
with open(dark_svg_path, "w", encoding="utf-8") as f:
    f.write("\n".join(dark_lines))

with open(light_svg_path, "w", encoding="utf-8") as f:
    f.write("\n".join(light_lines))

with open(legacy_svg_path, "w", encoding="utf-8") as f:
    f.write("\n".join(dark_lines))

# Also copy to sha-portfolio public images
pub_dir = "/Users/sha/Sha portfolio/sha-portfolio/public/images"
os.makedirs(pub_dir, exist_ok=True)
with open(os.path.join(pub_dir, "portrait-dark.svg"), "w", encoding="utf-8") as f:
    f.write("\n".join(dark_lines))
with open(os.path.join(pub_dir, "portrait-light.svg"), "w", encoding="utf-8") as f:
    f.write("\n".join(light_lines))
with open(os.path.join(pub_dir, "sha_matrix.svg"), "w", encoding="utf-8") as f:
    f.write("\n".join(dark_lines))

print("Successfully generated portrait-dark.svg and high-contrast portrait-light.svg!")
