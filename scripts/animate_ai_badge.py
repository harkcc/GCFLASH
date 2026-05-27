#!/usr/bin/env python3
"""Animates the AI-generated EXCITAT glassmorphism logo badge with a breathing neon glow."""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path("/Users/cc/Desktop/photo_show")
BRAIN_DIR = Path("/Users/cc/.gemini/antigravity/brain/1367e8e5-d106-4385-8319-4bfc66dff76c")
OUT = ROOT / "output/emag_motion_effect_demos"

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    
    # 1. Find the latest generated logo badge
    candidates = sorted(list(BRAIN_DIR.glob("excitat_brand_badge_ai_*.png")))
    if not candidates:
        print("Error: excitat_brand_badge_ai image not found!")
        return
    badge_src = candidates[-1]
    print(f"Loading generated badge from: {badge_src.name}")
    
    # 2. Open and resize to fit standard detail dimensions (240x240px or 180x180px)
    # Since it is a square 3D badge with perspective, let's keep it square
    src_img = Image.open(badge_src).convert("RGBA")
    src_img.thumbnail((240, 240), Image.Resampling.LANCZOS)
    
    w, h = 240, 240
    frames = []
    num_frames = 20
    
    # Circular ambient glow mask in the background
    glow_mask = Image.new("L", (w, h), 0)
    gd = ImageDraw.Draw(glow_mask)
    gd.ellipse((20, 20, w - 20, h - 20), fill=255)
    glow_blurred = glow_mask.filter(ImageFilter.GaussianBlur(15))
    
    for i in range(num_frames):
        t = (math.sin(i / num_frames * math.tau) + 1.0) / 2.0
        # Opacity breathes between 40 and 200
        alpha = int(40 + 160 * t)
        
        # Base frame canvas (dark background matching detail page style)
        frame = Image.new("RGBA", (w, h), (10, 12, 18, 255))
        fd = ImageDraw.Draw(frame)
        
        # Paste soft background pulse glow behind badge
        glow_color = (0, 229, 255, alpha) # neon cyan
        glow_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gd_color = ImageDraw.Draw(glow_img)
        gd_color.bitmap((0, 0), glow_blurred, fill=glow_color)
        frame.alpha_composite(glow_img)
        
        # Paste the premium AI logo badge in center
        bx = (w - src_img.width) // 2
        by = (h - src_img.height) // 2
        frame.alpha_composite(src_img, (bx, by))
        
        # Draw breathing border frame overlay
        border_alpha = int(80 + 175 * t)
        fd.rectangle((10, 10, w - 10, h - 10), outline=(0, 229, 255, border_alpha), width=2)
        
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
        
    output_path = OUT / "brand_icon_glow_ai_generated.gif"
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)
    print(f"✓ Saved animated brand badge GIF: {output_path.name}")

if __name__ == "__main__":
    main()
