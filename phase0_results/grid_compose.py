#!/usr/bin/env python3
"""4-panel grid composer for scene_multi_use image

Usage:
  python3 grid_compose.py <panel1> <panel2> <panel3> <panel4> <out_path> [border_px]
"""
import sys
from PIL import Image

def compose(panels, out_path, border=8, size=1024):
    """2x2 grid. Each panel resized to (size/2 - border) square."""
    tile = (size - 3 * border) // 2
    canvas = Image.new("RGB", (size, size), (255, 255, 255))
    positions = [
        (border, border),
        (border + tile + border, border),
        (border, border + tile + border),
        (border + tile + border, border + tile + border),
    ]
    for panel_path, pos in zip(panels, positions):
        p = Image.open(panel_path).convert("RGB").resize((tile, tile), Image.LANCZOS)
        canvas.paste(p, pos)
    canvas.save(out_path, "JPEG", quality=90)
    print(f"✅ Grid -> {out_path}  ({size}x{size})")

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print(__doc__)
        sys.exit(1)
    border = int(sys.argv[6]) if len(sys.argv) > 6 else 8
    compose(sys.argv[1:5], sys.argv[5], border=border)
