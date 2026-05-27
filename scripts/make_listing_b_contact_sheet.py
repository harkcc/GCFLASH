#!/usr/bin/env python3
"""Builds a visual contact sheet of all images in the listing_b folder."""

from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/cc/Desktop/photo_show")
FONTS_DIR = ROOT / "assets" / "fonts"

def get_font(size: int) -> ImageFont.ImageFont:
    probe = FONTS_DIR / "Arial.ttf"
    if probe.exists():
        return ImageFont.truetype(str(probe), size=size)
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def main() -> None:
    listing_dir = Path("/Users/cc/Desktop/listing_b")
    if not listing_dir.exists():
        print(f"Error: Directory not found: {listing_dir}")
        return

    # Gather all images
    images = sorted(list(listing_dir.glob("*.jpg")) + list(listing_dir.glob("*.png")))
    if not images:
        print("No images found in listing_b")
        return
        
    print(f"Found {len(images)} images in listing_b. Creating contact sheet...")
    
    # Thumb size
    thumb_w, thumb_h = 320, 320
    cols = 5
    rows = math.ceil(len(images) / cols)
    
    tile_w = thumb_w + 20
    tile_h = thumb_h + 60
    
    sheet = Image.new("RGB", (cols * tile_w + 40, rows * tile_h + 100), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    
    # Title
    font_title = get_font(32)
    draw.text((20, 20), "Listing_b Templates Catalog", font=font_title, fill=(20, 30, 40))
    
    font_label = get_font(12)
    
    for idx, path in enumerate(images):
        col = idx % cols
        row = idx // cols
        
        # Load and resize image to fit thumb
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        
        # Calculate paste position (center within tile)
        tx = 20 + col * tile_w + (thumb_w - img.width) // 2
        ty = 100 + row * tile_h + (thumb_h - img.height) // 2
        
        sheet.paste(img, (tx, ty))
        
        # Draw filename label
        label = path.name
        # Truncate label if too long
        if len(label) > 35:
            label = label[:16] + "..." + label[-16:]
            
        lx = 20 + col * tile_w
        ly = 100 + row * tile_h + thumb_h + 10
        draw.text((lx, ly), label, font=font_label, fill=(60, 70, 80))
        
    output_path = ROOT / "output/listing_b_contact_sheet.jpg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, quality=88)
    print(f"Contact sheet saved to: {output_path}")


if __name__ == "__main__":
    main()
