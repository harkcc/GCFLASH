#!/usr/bin/env python3
"""Generates premium animated brand GIF icons for EXCITAT."""

from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path("/Users/cc/Desktop/photo_show")
OUT = ROOT / "output/emag_motion_effect_demos"
FONTS_DIR = ROOT / "assets" / "fonts"

def get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    name = "Arial Bold.ttf" if bold else "Arial.ttf"
    probe = FONTS_DIR / name
    if probe.exists():
        return ImageFont.truetype(str(probe), size=size)
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def make_glow_icon(output_path: Path) -> None:
    """Generates an animated EXCITAT brand logo badge with breathing neon glow."""
    print("-> Rendering animated brand logo icon...")
    w, h = 240, 90
    frames = []
    num_frames = 20
    
    # Pre-render the static text and badge shape on transparent canvas
    base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    # Rounded badge container
    d.rounded_rectangle((6, 6, w - 6, h - 6), radius=18, fill=(12, 18, 30, 240))
    
    # Orbitron font or Bold Arial for logo text
    font_brand = get_font(26, True)
    text = "EXCITAT"
    bbox = d.textbbox((0, 0), text, font=font_brand)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((w - tw) // 2, (h - th) // 2 - 2), text, font=font_brand, fill=(255, 255, 255))
    
    # Outer glow base mask
    glow_mask = Image.new("L", (w, h), 0)
    gd = ImageDraw.Draw(glow_mask)
    gd.rounded_rectangle((6, 6, w - 6, h - 6), radius=18, fill=255)
    glow_blurred = glow_mask.filter(ImageFilter.GaussianBlur(8))
    
    for i in range(num_frames):
        t = (math.sin(i / num_frames * math.tau) + 1.0) / 2.0
        # Opacity breathing from 60 to 220
        alpha = int(60 + 160 * t)
        
        # Create output frame
        frame = Image.new("RGBA", (w, h), (10, 12, 18, 255))
        fd = ImageDraw.Draw(frame)
        
        # Colorize and paste blurred neon glow behind the badge
        glow_color = (0, 229, 255, alpha) # Neon cyan
        glow_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gd_color = ImageDraw.Draw(glow_img)
        gd_color.bitmap((0, 0), glow_blurred, fill=glow_color)
        
        frame.alpha_composite(glow_img)
        
        # Draw a sharp breathing inner border
        border_alpha = int(120 + 135 * t)
        fd.rounded_rectangle((6, 6, w - 6, h - 6), radius=18, outline=(0, 229, 255, border_alpha), width=2)
        
        # Composite text badge
        frame.alpha_composite(base)
        
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
        
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=70, loop=0, optimize=True)
    print(f"-> Saved brand logo icon: {output_path.name}")


def make_charging_icon(output_path: Path) -> None:
    """Generates an animated charging bolt icon with flowing energy lines."""
    print("-> Rendering animated charging bolt icon...")
    w, h = 120, 120
    frames = []
    num_frames = 16
    
    # Load raw bolt icon if exists, else draw a bolt silhouette
    icon_src = ROOT / "output/emag_exit_two_product_stable_components_v4/assets/_icon_library_v1/bolt.png"
    if icon_src.exists():
        bolt_raw = Image.open(icon_src).convert("RGBA").resize((48, 48), Image.Resampling.LANCZOS)
    else:
        # Draw placeholder bolt
        bolt_raw = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bolt_raw)
        bd.polygon([(24, 4), (36, 24), (26, 24), (32, 44), (16, 20), (24, 20)], fill=(255, 255, 255, 255))
        
    for i in range(num_frames):
        frame = Image.new("RGBA", (w, h), (10, 12, 18, 255))
        fd = ImageDraw.Draw(frame)
        
        # Draw circular border
        fd.ellipse((10, 10, w - 10, h - 10), outline=(255, 176, 54, 80), width=2)
        
        # Animate progress arc around the circle (0 to 360 deg)
        angle = int((i / num_frames) * 360)
        fd.arc((10, 10, w - 10, h - 10), start=-90, end=-90 + angle, fill=(255, 176, 54, 255), width=3)
        
        # Colorize and pulse the bolt in the center
        t = (math.sin(i / num_frames * math.tau * 2) + 1.0) / 2.0
        bolt_alpha = int(140 + 115 * t)
        
        # Colorize bolt with neon orange/gold
        bolt_colored = Image.new("RGBA", bolt_raw.size, (255, 180, 54, bolt_alpha))
        bolt_colored.putalpha(bolt_raw.getchannel("A"))
        
        # Add a soft gold glow behind the bolt
        bolt_glow_mask = bolt_raw.getchannel("A").filter(ImageFilter.GaussianBlur(6))
        bglow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        bgd = ImageDraw.Draw(bglow)
        bx = (w - bolt_raw.width) // 2
        by = (h - bolt_raw.height) // 2
        bglow_mask_large = Image.new("L", (w, h), 0)
        bglow_mask_large.paste(bolt_glow_mask, (bx, by))
        bgd.bitmap((0, 0), bglow_mask_large, fill=(255, 180, 54, int(80 * t)))
        
        frame.alpha_composite(bglow)
        frame.alpha_composite(bolt_colored, (bx, by))
        
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
        
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)
    print(f"-> Saved charging icon: {output_path.name}")


def make_shield_icon(output_path: Path) -> None:
    """Generates an animated security shield icon with scanning sweep."""
    print("-> Rendering animated security shield icon...")
    w, h = 120, 120
    frames = []
    num_frames = 16
    
    # Load shield icon or draw a shield silhouette
    icon_src = ROOT / "output/emag_exit_two_product_stable_components_v4/assets/_icon_library_v1/shield.png"
    if icon_src.exists():
        shield_raw = Image.open(icon_src).convert("RGBA").resize((48, 48), Image.Resampling.LANCZOS)
    else:
        shield_raw = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shield_raw)
        sd.polygon([(24, 6), (38, 12), (38, 28), (24, 42), (10, 28), (10, 12)], fill=(255, 255, 255, 255))
        
    for i in range(num_frames):
        frame = Image.new("RGBA", (w, h), (10, 12, 18, 255))
        fd = ImageDraw.Draw(frame)
        
        # Draw circular frame
        fd.ellipse((10, 10, w - 10, h - 10), outline=(0, 229, 255, 80), width=2)
        
        # Colorize shield to cyan
        shield_colored = Image.new("RGBA", shield_raw.size, (0, 229, 255, 220))
        shield_colored.putalpha(shield_raw.getchannel("A"))
        
        bx = (w - shield_raw.width) // 2
        by = (h - shield_raw.height) // 2
        frame.alpha_composite(shield_colored, (bx, by))
        
        # Animate horizontal scan line moving from top to bottom
        scan_y = 12 + int((i / num_frames) * 96)
        # Gradient scan line
        for dy in range(-3, 4):
            opacity = int(255 * (1.0 - abs(dy)/4.0))
            fd.line((14, scan_y + dy, w - 14, scan_y + dy), fill=(255, 255, 255, opacity), width=1)
            
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
        
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=90, loop=0, optimize=True)
    print(f"-> Saved shield icon: {output_path.name}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    make_glow_icon(OUT / "brand_icon_glow.gif")
    make_charging_icon(OUT / "brand_icon_charge.gif")
    make_shield_icon(OUT / "brand_icon_shield.gif")
    
    # Update HTML preview
    preview_path = OUT / "stable_effects_preview.html"
    if preview_path.exists():
        html = preview_path.read_text(encoding="utf-8")
        # Insert icons section right before </main>
        icons_html = (
            '<section>'
            '<h2>4. Animated Brand GIF Icons</h2>'
            '<p>Premium animated vector brand icons designed for listing headers, badges, or trust anchors.</p>'
            '<div style="display:flex;gap:20px;align-items:center;margin-top:14px;">'
            '<img src="brand_icon_glow.gif" style="width:240px;height:90px;max-width:none;">'
            '<img src="brand_icon_charge.gif" style="width:120px;height:120px;max-width:none;">'
            '<img src="brand_icon_shield.gif" style="width:120px;height:120px;max-width:none;">'
            '</div>'
            '</section>'
        )
        html = html.replace('</main>', f'{icons_html}</main>')
        preview_path.write_text(html, encoding="utf-8")
        print(f"-> Updated HTML preview with brand icons: {preview_path.name}")


if __name__ == "__main__":
    main()
