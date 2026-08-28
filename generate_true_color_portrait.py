import os
from PIL import Image, ImageEnhance, ImageOps

input_path = "/Users/sha/Sha portfolio/sha-portfolio/public/Adobe Express - file-7.png"
dark_svg_path = "/tmp/shachin-profile/assets/portrait-dark.svg"
light_svg_path = "/tmp/shachin-profile/assets/portrait-light.svg"
legacy_svg_path = "/tmp/shachin-profile/assets/portrait.svg"

img = Image.open(input_path).convert("RGBA")
w, h = img.size

r, g, b, alpha = img.split()
img_rgb = Image.merge("RGB", (r, g, b))

# Grayscale for structure
gray = img_rgb.convert("L")

# Enhance contrast for sharp facial features
enhancer = ImageEnhance.Contrast(gray)
gray_enhanced = enhancer.enhance(1.6)

grid_cols = 80
cw, ch = img.size
grid_rows = int(grid_cols * (ch / cw))

img_small = img_rgb.resize((grid_cols, grid_rows), Image.Resampling.LANCZOS)
gray_small = gray_enhanced.resize((grid_cols, grid_rows), Image.Resampling.LANCZOS)
alpha_small = alpha.resize((grid_cols, grid_rows), Image.Resampling.LANCZOS)

spacing = 10
margin = 20
width_svg = grid_cols * spacing + margin * 2
height_svg = grid_rows * spacing + margin * 2

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


# ─── 2. HIGH-CONTRAST LIGHT MODE PORTRAIT (portrait-light.svg) ───────────────
# For Light Mode:
# 1. Hair, eyes, shadows & dark shirt MUST be solid deep black (#121316 to #1a1c23) with large radius (3.8-4.8) so hair & suit look rich and defined!
# 2. Skin tones must be rich warm bronze/copper (#b86030 to #d47840) with sharp facial feature definition (eyes, nose, mouth in dark charcoal/brown).
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
        r_px, g_px, b_px = img_small.getpixel((c_idx, r_idx))
        cx = c_idx * spacing + spacing / 2
        cy = r_idx * spacing + spacing / 2

        # Check if pixel is part of dark features (hair, shirt, eyes, eyebrows)
        is_dark_feature = (val < 110) or (r_px < 100 and g_px < 100 and b_px < 100)

        if is_dark_feature:
            # Black hair & shirt: large dense dots + deep rich dark tone
            darkness = (110 - min(val, 110)) / 110.0
            radius = round(3.2 + darkness * 1.5, 2)
            # Ensure hair & suit are rich deep black/charcoal, NOT light gray!
            hex_color = "#111318" if val < 60 else "#22252c"
        else:
            # Skin & face highlights: warm rich copper/bronze tone for high contrast against white
            radius = round(2.2 + (val / 255.0) * 2.0, 2)
            
            # Color grade skin to rich warm amber/copper tone for crisp contrast on light background
            # Blend natural RGB with warm copper tint
            cr = int(r_px * 0.75 + 60)
            cg = int(g_px * 0.55 + 25)
            cb = int(b_px * 0.40 + 10)
            
            # Clamp values
            cr = min(230, max(140, cr))
            cg = min(140, max(70, cg))
            cb = min(90, max(20, cb))
            
            hex_color = f"#{cr:02x}{cg:02x}{cb:02x}"

        light_lines.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{hex_color}" />')
    light_lines.append('</g>')

light_lines.append('</g>')
light_lines.append('</svg>')

# Write outputs
with open(dark_svg_path, "w", encoding="utf-8") as f:
    f.write("\n".join(dark_lines))

with open(light_svg_path, "w", encoding="utf-8") as f:
    f.write("\n".join(light_lines))

with open(legacy_svg_path, "w", encoding="utf-8") as f:
    f.write("\n".join(dark_lines))

pub_dir = "/Users/sha/Sha portfolio/sha-portfolio/public/images"
os.makedirs(pub_dir, exist_ok=True)
with open(os.path.join(pub_dir, "portrait-dark.svg"), "w", encoding="utf-8") as f:
    f.write("\n".join(dark_lines))
with open(os.path.join(pub_dir, "portrait-light.svg"), "w", encoding="utf-8") as f:
    f.write("\n".join(light_lines))
with open(os.path.join(pub_dir, "sha_matrix.svg"), "w", encoding="utf-8") as f:
    f.write("\n".join(dark_lines))

print("Successfully generated bold, crisp portrait-light.svg and portrait-dark.svg!")
