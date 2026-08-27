#!/usr/bin/env python3
"""
dotify.py — convert a photo into an animated SVG dot-matrix portrait.

Usage:
  python dotify.py SOURCE -o OUTPUT_STEM [options]

Options:
  --cols N        Number of dot columns (default 88)
  --mode MODE     dots | binary | ascii | braille (default dots)
  --equalize      Histogram-equalize for better contrast on portraits
  --detail F      Blend sharpened detail back in (0-1, default 0)
  --color         Keep each dot's original pixel colour (writes one SVG,
                  not a -dark/-light pair)
  --animate       Add a column-sweep shimmer animation
  --reveal        Fade in row by row on load (--reveal-time, --reveal-fade)
  --reveal-time F Total sweep time in seconds (default 2.5)
  --reveal-fade F One-row fade duration in seconds (default 0.45)
  --reveal-dir D  up | down (default down)
  --invert        Swap foreground/background
  --circle        Mask to a circle
  --square        Crop to 1:1 before processing
  --focus X,Y     Centre point for --square crop (default 0.5,0.5)
  --limit N       Max brightness level (0-255, default 240)
"""

import argparse, math, sys
from pathlib import Path

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
except ImportError:
    sys.exit("Pillow required: pip install Pillow")


# ── helpers ────────────────────────────────────────────────────────────────────

def crop_square(img: Image.Image, fx: float, fy: float) -> Image.Image:
    w, h = img.size
    s = min(w, h)
    x0 = int((w - s) * fx)
    y0 = int((h - s) * fy)
    return img.crop((x0, y0, x0 + s, y0 + s))


def circle_mask(img: Image.Image) -> Image.Image:
    import struct, zlib
    w, h = img.size
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    from PIL import ImageDraw
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([0, 0, w - 1, h - 1], fill=255)
    img.putalpha(mask)
    return img


def prepare(img: Image.Image, args) -> Image.Image:
    if args.square:
        fx, fy = (float(v) for v in args.focus.split(","))
        img = crop_square(img, fx, fy)
    if args.invert:
        img = ImageOps.invert(img.convert("RGB"))
    if args.circle:
        img = circle_mask(img)
    if args.equalize:
        # equalize luminance only, preserve hue
        lab = img.convert("RGB")
        r, g, b = lab.split()
        r = ImageOps.equalize(r)
        g = ImageOps.equalize(g)
        b = ImageOps.equalize(b)
        img = Image.merge("RGB", (r, g, b))
    if args.detail:
        sharpened = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150))
        img = Image.blend(img, sharpened, args.detail)
    return img


def brightness_map(img_gray: Image.Image, cols: int, limit: int):
    """Return list of rows; each row is list of (col_idx, brightness 0-1)."""
    w, h = img_gray.size
    cell = w / cols
    rows_count = int(h / cell)
    rows = []
    px = img_gray.load()
    for row in range(rows_count):
        cells = []
        for col in range(cols):
            x0 = int(col * cell)
            x1 = int((col + 1) * cell)
            y0 = int(row * cell)
            y1 = int((row + 1) * cell)
            total = 0
            count = 0
            for y in range(y0, min(y1, h)):
                for x in range(x0, min(x1, w)):
                    v = px[x, y]
                    if isinstance(v, int):
                        total += v
                    else:
                        total += v[0]
                    count += 1
            avg = total / count if count else 0
            b = min(avg, limit) / limit
            cells.append(b)
        rows.append(cells)
    return rows, cell


def color_map(img_rgb: Image.Image, cols: int):
    """Return list of rows; each row is list of (r,g,b) tuples averaged per cell."""
    w, h = img_rgb.size
    cell = w / cols
    rows_count = int(h / cell)
    rows = []
    px = img_rgb.load()
    for row in range(rows_count):
        cells = []
        for col in range(cols):
            x0 = int(col * cell)
            x1 = int((col + 1) * cell)
            y0 = int(row * cell)
            y1 = int((row + 1) * cell)
            rs = gs = bs = count = 0
            for y in range(y0, min(y1, h)):
                for x in range(x0, min(x1, w)):
                    v = px[x, y]
                    if isinstance(v, (list, tuple)) and len(v) >= 3:
                        rs += v[0]; gs += v[1]; bs += v[2]
                    elif isinstance(v, int):
                        rs += v; gs += v; bs += v
                    count += 1
            if count:
                cells.append((rs // count, gs // count, bs // count))
            else:
                cells.append((0, 0, 0))
        rows.append(cells)
    return rows, cell


# ── SVG builders ───────────────────────────────────────────────────────────────

def _hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


def build_dots_svg(bmap, cmap, cell, cols, args, dark_bg="#0d1117", dot_color="#39d353"):
    rows_count = len(bmap)
    max_r = cell * 0.48
    W = H = cell * cols

    lines = []
    # animation style
    if args.reveal:
        RT = args.reveal_time
        RF = args.reveal_fade
        delay_step = (RT - RF) / max(rows_count - 1, 1)
        css = ["<style>"]
        css.append("@keyframes rv{from{opacity:0}to{opacity:1}}")
        css.append(".rw{animation:rv %.2fs ease-out both}" % RF)
        for r in range(rows_count):
            css.append(".r%d{animation-delay:%.3fs}" % (r, r * delay_step))
        css.append("</style>")
        lines.extend(css)
    elif args.animate:
        css = ["<style>"]
        css.append("@keyframes sh{0%,100%{opacity:.55}50%{opacity:1}}")
        for c in range(cols):
            css.append(".c%d{animation:sh 3s ease-in-out %.2fs infinite}" % (c, c * 0.03))
        css.append("</style>")
        lines.extend(css)

    svg_w = cell * cols
    svg_h = cell * rows_count

    lines.insert(0,
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {svg_w:.1f} {svg_h:.1f}" '
        f'width="{svg_w:.1f}" height="{svg_h:.1f}" '
        f'role="img" aria-label="dot-matrix portrait">')
    lines.append(f'<rect width="{svg_w:.1f}" height="{svg_h:.1f}" fill="{dark_bg}"/>')
    lines.append(f'<g transform="translate({cell/2:.1f},{cell/2:.1f})">')

    for row_idx, (b_row, c_row) in enumerate(zip(bmap, cmap)):
        if args.reveal:
            class_attr = f'class="rw r{row_idx}"'
        else:
            class_attr = ""

        group_circles = []
        for col_idx, (b, (cr, cg, cb)) in enumerate(zip(b_row, c_row)):
            if b < 0.03:
                continue
            r = max_r * b
            cx = col_idx * cell
            cy = row_idx * cell

            if args.color:
                fill = _hex(cr, cg, cb)
            else:
                fill = dot_color

            if args.animate:
                col_class = f'class="c{col_idx}"'
                group_circles.append(
                    f'<circle {col_class} cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.2f}" fill="{fill}"/>'
                )
            else:
                group_circles.append(
                    f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.2f}" fill="{fill}"/>'
                )

        if group_circles:
            if args.reveal:
                lines.append(f'<g {class_attr}>')
                lines.extend(group_circles)
                lines.append('</g>')
            else:
                lines.extend(group_circles)

    lines.append('</g>')
    lines.append('</svg>')
    return "\n".join(lines)


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Photo → animated dot-matrix SVG")
    p.add_argument("source", help="Source image file")
    p.add_argument("-o", "--output", required=True, help="Output stem (no extension)")
    p.add_argument("--cols", type=int, default=88)
    p.add_argument("--mode", default="dots", choices=["dots", "binary", "ascii", "braille"])
    p.add_argument("--equalize", action="store_true")
    p.add_argument("--detail", type=float, default=0.0)
    p.add_argument("--color", action="store_true")
    p.add_argument("--animate", action="store_true")
    p.add_argument("--reveal", action="store_true")
    p.add_argument("--reveal-time", type=float, default=2.5)
    p.add_argument("--reveal-fade", type=float, default=0.45)
    p.add_argument("--reveal-dir", default="down", choices=["up", "down"])
    p.add_argument("--invert", action="store_true")
    p.add_argument("--circle", action="store_true")
    p.add_argument("--square", action="store_true")
    p.add_argument("--focus", default="0.5,0.5")
    p.add_argument("--limit", type=int, default=240)
    args = p.parse_args()

    src = Path(args.source)
    if not src.exists():
        sys.exit(f"Source not found: {src}")

    img = Image.open(src)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")

    img = prepare(img, args)

    # get colour map before converting to gray
    img_rgb = img.convert("RGB")
    cmap_rows, cell = color_map(img_rgb, args.cols)

    img_gray = img_rgb.convert("L")
    bmap_rows, _ = brightness_map(img_gray, args.cols, args.limit)

    out_stem = args.output
    svg = build_dots_svg(bmap_rows, cmap_rows, cell, args.cols, args)

    if args.color:
        out_path = Path(out_stem + ".svg")
        out_path.write_text(svg, encoding="utf-8")
        print(f"wrote {out_path}")
    else:
        # write dark and light variants
        out_d = Path(out_stem + "-dark.svg")
        out_l = Path(out_stem + "-light.svg")
        out_d.write_text(svg, encoding="utf-8")
        svg_light = svg.replace("#0d1117", "#ffffff").replace("#39d353", "#1a7f37")
        out_l.write_text(svg_light, encoding="utf-8")
        print(f"wrote {out_d}  {out_l}")


if __name__ == "__main__":
    main()
