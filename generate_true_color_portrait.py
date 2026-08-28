import os
from PIL import Image, ImageEnhance, ImageOps

# Source photo path
input_path = "/Users/sha/Sha portfolio/sha-portfolio/public/Adobe Express - file-7.png"
output_svg_path = "/tmp/shachin-profile/assets/portrait.svg"

# Load image preserving RGBA alpha channel
img = Image.open(input_path).convert("RGBA")

w, h = img.size

# Split RGBA channels
r, g, b, alpha = img.split()
img_rgb = Image.merge("RGB", (r, g, b))

# Grayscale for dot intensity and structure
gray = img_rgb.convert("L")

# Enhance contrast for dot size calculations
enhancer = ImageEnhance.Contrast(gray)
gray_enhanced = enhancer.enhance(1.4)

# Grid dimensions
grid_cols = 75
cw, ch = img.size
grid_rows = int(grid_cols * (ch / cw))

# Resize image & channels to grid resolution
img_small = img_rgb.resize((grid_cols, grid_rows), Image.Resampling.LANCZOS)
gray_small = gray_enhanced.resize((grid_cols, grid_rows), Image.Resampling.LANCZOS)
alpha_small = alpha.resize((grid_cols, grid_rows), Image.Resampling.LANCZOS)

spacing = 10
margin = 20
width_svg = grid_cols * spacing + margin * 2
height_svg = grid_rows * spacing + margin * 2

# Generate CSS animations for dots
css_lines = []
css_lines.append("@keyframes rv { from { opacity: 0; transform: scale(0.4); } to { opacity: 1; transform: scale(1); } }")
css_lines.append(".rw { animation: rv 0.45s cubic-bezier(0.16, 1, 0.3, 1) both; transform-origin: center; }")

max_delay = 2.5
for r_idx in range(grid_rows):
    delay = (r_idx / grid_rows) * max_delay
    css_lines.append(f".r{r_idx} {{ animation-delay: {delay:.3f}s; }}")

svg_content = []
svg_content.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_svg} {height_svg}" width="{width_svg}" height="{height_svg}" role="img" aria-label="dot-matrix portrait">')
svg_content.append('<style>' + "".join(css_lines) + '</style>')
# NOTE: Removed solid background <rect> so SVG has NO square background!
svg_content.append(f'<g transform="translate({margin}, {margin})">')

for r_idx in range(grid_rows):
    svg_content.append(f'<g class="rw r{r_idx}">')
    for c_idx in range(grid_cols):
        # 1. Skip transparent alpha pixels completely
        a_val = alpha_small.getpixel((c_idx, r_idx))
        if a_val < 30:
            continue

        # Get grayscale value for dot radius calculation
        val = gray_small.getpixel((c_idx, r_idx))
        
        # Calculate dot radius
        intensity = val / 255.0
        radius = round(1.2 + intensity * 3.4, 2)
        cx = c_idx * spacing + spacing / 2
        cy = r_idx * spacing + spacing / 2

        # Extract TRUE RGB COLOR from original image
        r_px, g_px, b_px = img_small.getpixel((c_idx, r_idx))
        hex_color = f"#{r_px:02x}{g_px:02x}{b_px:02x}"

        svg_content.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{hex_color}" />')
    svg_content.append('</g>')

svg_content.append('</g>')
svg_content.append('</svg>')

with open(output_svg_path, "w", encoding="utf-8") as f:
    f.write("\n".join(svg_content))

# Also copy to portfolio public images
public_path = "/Users/sha/Sha portfolio/sha-portfolio/public/images/sha_matrix.svg"
os.makedirs(os.path.dirname(public_path), exist_ok=True)
with open(public_path, "w", encoding="utf-8") as f:
    f.write("\n".join(svg_content))

print(f"Generated completely transparent true-color portrait.svg without background rect!")
