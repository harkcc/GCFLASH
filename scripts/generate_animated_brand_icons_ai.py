#!/usr/bin/env python3
"""Generates premium animated brand GIF icons using AI-generated base assets from fal.ai."""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path
from urllib.request import urlretrieve

import fal_client
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path("/Users/cc/Desktop/photo_show")
OUT = ROOT / "output/emag_motion_effect_demos"
FONTS_DIR = ROOT / "assets" / "fonts"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


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


def extract_object_from_black(image: Image.Image, threshold: int = 15) -> Image.Image:
    """Converts black background to transparency using luminance mapping."""
    rgba = image.convert("RGBA")
    data = rgba.getdata()
    new_data = []
    for item in data:
        r, g, b, a = item
        # Luminance calculation
        lum = int(0.299 * r + 0.587 * g + 0.114 * b)
        if lum < threshold:
            # Fully transparent black
            new_data.append((0, 0, 0, 0))
        else:
            # Keep color, map alpha to luminance for smooth glow edges
            alpha = min(255, int(lum * 1.5))
            new_data.append((r, g, b, alpha))
            
    rgba.putdata(new_data)
    bbox = rgba.getbbox()
    if bbox:
        rgba = rgba.crop(bbox)
    return rgba


def generate_icon_base(name: str, prompt: str, run_ai: bool) -> Path:
    base_file = OUT / f"ai_base_{name}.png"
    if base_file.exists():
        print(f"-> Using cached AI base asset: {base_file.name}")
        return base_file
        
    if not run_ai:
        # Create a synthetic placeholder on solid black
        img = Image.new("RGBA", (512, 512), (0, 0, 0, 255))
        d = ImageDraw.Draw(img)
        if "bolt" in name:
            d.polygon([(256, 50), (380, 250), (280, 250), (340, 450), (160, 220), (250, 220)], fill=(255, 180, 54, 255))
        elif "shield" in name:
            d.polygon([(256, 70), (400, 140), (400, 320), (256, 450), (112, 320), (112, 140)], fill=(0, 229, 255, 255))
        else: # badge
            d.rounded_rectangle((50, 180, 462, 332), radius=30, fill=(15, 23, 40, 255), outline=(0, 229, 255, 255), width=6)
            font = get_font(42, True)
            d.text((256, 256), "EXCITAT", font=font, fill=(255, 255, 255), anchor="mm")
        img.save(base_file)
        return base_file

    print(f"-> Generating AI base asset for '{name}' via fal.ai...")
    result = fal_client.subscribe(
        "fal-ai/flux-pro/v1.1",
        arguments={
            "prompt": prompt,
            "image_size": {"width": 512, "height": 512},
            "num_images": 1,
            "safety_tolerance": "5",
            "output_format": "png",
        },
        with_logs=False
    )
    images = result.get("images") or []
    if not images:
        raise RuntimeError("fal.ai returned no images")
    url = images[0]["url"]
    urlretrieve(url, base_file)
    return base_file


def make_animated_badge_ai(ref_path: Path, output_path: Path) -> None:
    print(f"-> Rendering AI animated brand badge...")
    img = Image.open(ref_path)
    badge = extract_object_from_black(img, threshold=20)
    badge.thumbnail((240, 90), Image.Resampling.LANCZOS)
    
    w, h = 240, 90
    frames = []
    num_frames = 20
    
    # Outer glow base mask
    glow_mask = Image.new("L", (w, h), 0)
    gd = ImageDraw.Draw(glow_mask)
    gd.rounded_rectangle((8, 8, w - 8, h - 8), radius=18, fill=255)
    glow_blurred = glow_mask.filter(ImageFilter.GaussianBlur(10))
    
    for i in range(num_frames):
        t = (math.sin(i / num_frames * math.tau) + 1.0) / 2.0
        alpha = int(40 + 180 * t) # pulse intensity
        
        frame = Image.new("RGBA", (w, h), (10, 12, 18, 255))
        fd = ImageDraw.Draw(frame)
        
        # Paste ambient background glow
        glow_color = (0, 229, 255, alpha) # cyan glow
        glow_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gd_color = ImageDraw.Draw(glow_img)
        gd_color.bitmap((0, 0), glow_blurred, fill=glow_color)
        frame.alpha_composite(glow_img)
        
        # Paste the AI badge object in center
        bx = (w - badge.width) // 2
        by = (h - badge.height) // 2
        frame.alpha_composite(badge, (bx, by))
        
        # Draw breathing border overlay
        border_alpha = int(100 + 155 * t)
        fd.rounded_rectangle((8, 8, w - 8, h - 8), radius=18, outline=(0, 229, 255, border_alpha), width=2)
        
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
        
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)
    print(f"   ✓ Saved: {output_path.name}")


def make_animated_bolt_ai(ref_path: Path, output_path: Path) -> None:
    print(f"-> Rendering AI animated energy bolt...")
    img = Image.open(ref_path)
    bolt = extract_object_from_black(img, threshold=15)
    bolt.thumbnail((64, 64), Image.Resampling.LANCZOS)
    
    w, h = 120, 120
    frames = []
    num_frames = 18
    
    for i in range(num_frames):
        frame = Image.new("RGBA", (w, h), (10, 12, 18, 255))
        fd = ImageDraw.Draw(frame)
        
        # Animate progress energy arc (0 to 360 deg)
        angle = int((i / num_frames) * 360)
        fd.ellipse((10, 10, w - 10, h - 10), outline=(255, 176, 54, 60), width=2)
        fd.arc((10, 10, w - 10, h - 10), start=-90, end=-90 + angle, fill=(255, 176, 54, 255), width=3)
        
        # Brightness pulse
        t = (math.sin(i / num_frames * math.tau * 2) + 1.0) / 2.0
        opacity = int(160 + 95 * t)
        
        # Blend energy bolt with brightness multiplier
        bolt_pulse = Image.new("RGBA", bolt.size, (255, 255, 255, opacity))
        bolt_combined = Image.new("RGBA", bolt.size, (0, 0, 0, 0))
        bolt_combined.paste(bolt, (0, 0))
        bolt_combined.alpha_composite(bolt_pulse)
        
        # Add ambient glow behind bolt
        bolt_glow_mask = bolt.getchannel("A").filter(ImageFilter.GaussianBlur(6))
        bglow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        bgd = ImageDraw.Draw(bglow)
        bx = (w - bolt.width) // 2
        by = (h - bolt.height) // 2
        bglow_mask_large = Image.new("L", (w, h), 0)
        bglow_mask_large.paste(bolt_glow_mask, (bx, by))
        bgd.bitmap((0, 0), bglow_mask_large, fill=(255, 180, 54, int(110 * t)))
        
        frame.alpha_composite(bglow)
        frame.alpha_composite(bolt_combined, (bx, by))
        
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
        
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=70, loop=0, optimize=True)
    print(f"   ✓ Saved: {output_path.name}")


def make_animated_shield_ai(ref_path: Path, output_path: Path) -> None:
    print(f"-> Rendering AI animated security shield...")
    img = Image.open(ref_path)
    shield = extract_object_from_black(img, threshold=15)
    shield.thumbnail((64, 64), Image.Resampling.LANCZOS)
    
    w, h = 120, 120
    frames = []
    num_frames = 18
    
    for i in range(num_frames):
        frame = Image.new("RGBA", (w, h), (10, 12, 18, 255))
        fd = ImageDraw.Draw(frame)
        
        # Circular tech scale ring
        fd.ellipse((10, 10, w - 10, h - 10), outline=(0, 229, 255, 60), width=2)
        
        # Paste shield icon
        bx = (w - shield.width) // 2
        by = (h - shield.height) // 2
        frame.alpha_composite(shield, (bx, by))
        
        # Animate horizontal scanning bar passing from top to bottom
        scan_y = 15 + int((i / num_frames) * 90)
        # Laser scan line with falloff glow
        for dy in range(-3, 4):
            opacity = int(255 * (1.0 - abs(dy)/4.0))
            fd.line((14, scan_y + dy, w - 14, scan_y + dy), fill=(255, 255, 255, opacity), width=1)
            
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
        
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=85, loop=0, optimize=True)
    print(f"   ✓ Saved: {output_path.name}")


def main() -> None:
    load_env(ROOT / ".env")
    OUT.mkdir(parents=True, exist_ok=True)
    
    run_ai = os.environ.get("FAL_KEY") is not None
    
    # 1. Prompts for creating premium 3D base assets
    prompt_badge = (
        "A premium glowing 3D rectangular glassmorphism ui card badge, rounded corners, "
        "frosted glass texture, with the text 'EXCITAT' embossed in glowing white sans-serif letters "
        "in the center, floating on a solid black background, neon cyan and deep indigo edge glow, "
        "high detail, futuristic aesthetic, isolated."
    )
    
    prompt_bolt = (
        "A premium glowing 3D charging energy bolt icon, neon gold and amber light energy glow, "
        "complex tech wireframe details, floating on a solid black background, "
        "clean studio lighting, futuristic design, isolated."
    )
    
    prompt_shield = (
        "A premium glowing 3D cybersecurity shield icon, neon cyan and electric blue light beams, "
        "clean polished steel metallic accents, floating on a solid black background, "
        "high contrast tech emblem, isolated."
    )
    
    # 2. Generate or cache base files
    badge_base = generate_icon_base("badge", prompt_badge, run_ai)
    bolt_base = generate_icon_base("bolt", prompt_bolt, run_ai)
    shield_base = generate_icon_base("shield", prompt_shield, run_ai)
    
    # 3. Create animated brand GIF icons using AI bases
    make_animated_badge_ai(badge_base, OUT / "brand_icon_glow_ai.gif")
    make_animated_bolt_ai(bolt_base, OUT / "brand_icon_charge_ai.gif")
    make_animated_shield_ai(shield_base, OUT / "brand_icon_shield_ai.gif")
    
    # 4. Integrate into rich HTML preview if exists
    preview_path = OUT / "stable_effects_preview.html"
    if preview_path.exists():
        html = preview_path.read_text(encoding="utf-8")
        if "Animated AI-Powered Brand GIFs" not in html:
            ai_icons_html = (
                '<section>'
                '<h2>5. Animated AI-Powered Brand GIFs</h2>'
                '<p>Premium animated 3D brand icons generated using AI base assets and loopable frame rendering.</p>'
                '<div style="display:flex;gap:20px;align-items:center;margin-top:14px;background:#0d1117;padding:20px;border-radius:12px;">'
                '<img src="brand_icon_glow_ai.gif" style="width:240px;height:90px;max-width:none;">'
                '<img src="brand_icon_charge_ai.gif" style="width:120px;height:120px;max-width:none;">'
                '<img src="brand_icon_shield_ai.gif" style="width:120px;height:120px;max-width:none;">'
                '</div>'
                '</section>'
            )
            html = html.replace('</main>', f'{ai_icons_html}</main>')
            preview_path.write_text(html, encoding="utf-8")
            print("-> Successfully updated stable_effects_preview.html with AI brand icons section.")


if __name__ == "__main__":
    main()
