import os
from PIL import Image, ImageEnhance, ImageOps

input_path = "/Users/sha/Sha portfolio/sha-portfolio/public/Adobe Express - file-7.png"
dark_svg_path = "/tmp/shachin-profile/assets/portrait-dark.svg"
light_svg_path = "/tmp/shachin-profile/assets/portrait-light.svg"
legacy_svg_path = "/tmp/shachin-profile/assets/portrait.svg"

# Load image preserving RGBA transparency
img_rgba = Image.open(input_path).convert("RGBA")
w, h = img_rgba.size

r, g, b, alpha = img_rgba.split()
img_rgb = Image.merge("RGB", (r, g, b))

gray = img_rgb.convert("L")

grid_cols = 75
cw, ch = img_rgba.size
grid_rows = int(grid_cols * (ch / cw))

img_small_rgba = img_rgba.resize((grid_cols, grid_rows), Image.Resampling.LANCZOS)
img_small_rgb = img_rgb.resize((grid_cols, grid_rows), Image.Resampling.LANCZOS)
gray_small = gray.resize((grid_cols, grid_rows), Image.Resampling.LANCZOS)
alpha_small = alpha.resize((grid_cols, grid_rows), Image.Resampling.LANCZOS)

spacing = 10
margin = 20
width_svg = grid_cols * spacing + margin * 2
height_svg = grid_rows * spacing + margin * 2

# CSS keyframes animation
css_lines = [
    "@keyframes rv { from { opacity: 0; transform: scale(0.4); } to { opacity: 1; transform: scale(1); } }",
    ".rw { animation: rv 0.45s cubic-bezier(0.16, 1, 0.3, 1) both; transform-origin: center; }"
]
max_delay = 2.5
for r_idx in range(grid_rows):
    delay = (r_idx / grid_rows) * max_delay
    css_lines.append(f".r{r_idx} {{ animation-delay: {delay:.3f}s; }}")

css_str = "<style>" + "".join(css_lines) + "</style>"

# ─── 1. DARK THEME PORTRAIT (portrait-dark.svg) ──────────────────────────────
# Dark Mode: High grayscale value (bright pixels/face) = LARGE dot
dark_lines = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_svg} {height_svg}" width="{width_svg}" height="{height_svg}" role="img" aria-label="dot-matrix portrait">',
    css_str,
    f'<g transform="translate({margin}, {margin})">'
]

for r_idx in range(grid_rows):
    dark_lines.append(f'<g class="rw r{r_idx}">')
    for c_idx in range(grid_cols):
        a_px = alpha_small.getpixel((c_idx, r_idx))
        if a_px < 30:
            continue

        val = gray_small.getpixel((c_idx, r_idx))
        intensity = val / 255.0
        radius = round(1.2 + intensity * 3.4, 2)
        cx = c_idx * spacing + spacing / 2
        cy = r_idx * spacing + spacing / 2

        r_px, g_px, b_px = img_small_rgb.getpixel((c_idx, r_idx))
        hex_color = f"#{r_px:02x}{g_px:02x}{b_px:02x}"
        dark_lines.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{hex_color}" />')
    dark_lines.append('</g>')

dark_lines.append('</g>')
dark_lines.append('</svg>')


# ─── 2. LIGHT THEME PORTRAIT (portrait-light.svg) ─────────────────────────────
# Light Mode: Low grayscale value (dark area e.g. hair/suit) = LARGE dot (intensity = (255 - val) / 255.0)
# Uses TRUE RGB pixel values without filters/boosters.
light_lines = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_svg} {height_svg}" width="{width_svg}" height="{height_svg}" role="img" aria-label="dot-matrix portrait">',
    css_str,
    f'<g transform="translate({margin}, {margin})">'
]

for r_idx in range(grid_rows):
    light_lines.append(f'<g class="rw r{r_idx}">')
    for c_idx in range(grid_cols):
        a_px = alpha_small.getpixel((c_idx, r_idx))
        if a_px < 30:
            continue

        val = gray_small.getpixel((c_idx, r_idx))
        
        # REVERSED DOT SIZING MATH FOR LIGHT THEME:
        # Dark pixels (hair/suit/shadows) -> low val -> high intensity -> LARGE DOT
        intensity = (255.0 - val) / 255.0
        radius = round(0.8 + intensity * 3.8, 2)

        cx = c_idx * spacing + spacing / 2
        cy = r_idx * spacing + spacing / 2

        # TRUE RGB PIXEL COLORS (No brightness boosters or amber filters)
        r_px, g_px, b_px = img_small_rgb.getpixel((c_idx, r_idx))
        hex_color = f"#{r_px:02x}{g_px:02x}{b_px:02x}"

        light_lines.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{hex_color}" />')
    light_lines.append('</g>')

light_lines.append('</g>')
light_lines.append('</svg>')


# Save files
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

print("Successfully generated portrait-dark.svg and true-RGB reversed-math portrait-light.svg!")
