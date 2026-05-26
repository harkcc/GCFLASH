#!/usr/bin/env python3
"""Build stable, high-fidelity GIF animations with precise product and background effects."""

from __future__ import annotations

import json
import math
import os
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


def white_to_alpha(image: Image.Image, tolerance: int = 15) -> Image.Image:
    rgba = image.convert("RGBA")
    data = rgba.getdata()
    new_data = []
    for item in data:
        r, g, b, a = item
        if r > (255 - tolerance) and g > (255 - tolerance) and b > (255 - tolerance):
            new_data.append((r, g, b, 0))
        else:
            new_data.append(item)
    rgba.putdata(new_data)
    bbox = rgba.getbbox()
    if bbox:
        rgba = rgba.crop(bbox)
    return rgba


def apply_opacity(image: Image.Image, opacity: float) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    new_alpha = alpha.point(lambda p: min(255, max(0, int(p * opacity))))
    rgba.putalpha(new_alpha)
    return rgba


def build_precise_product_glow(product_path: Path, output_path: Path) -> None:
    """Creates a breathing neon glow emanating from behind the product cutout."""
    print("-> Generating Precise Product Edge Glow GIF...")
    # Load and cutout product
    prod = white_to_alpha(Image.open(product_path), tolerance=15)
    # Resize to fit inside 800x450 canvas
    prod.thumbnail((320, 320), Image.Resampling.LANCZOS)
    
    # Create canvas
    canvas_size = (800, 450)
    bg_color = (10, 15, 30) # Premium dark navy
    
    # Generate the blurred glow layer
    # Create a canvas matching the product size to hold the silhouette
    glow_canvas = Image.new("RGBA", prod.size, (0, 229, 255, 255)) # Bright cyan glow
    glow_canvas.putalpha(prod.getchannel("A"))
    
    # Place it on a larger canvas so the blur doesn't get clipped
    glow_large = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    px = (canvas_size[0] - prod.width) // 2
    py = (canvas_size[1] - prod.height) // 2
    glow_large.paste(glow_canvas, (px, py), prod.getchannel("A"))
    
    # Blur it heavily to create the glow
    glow_blurred = glow_large.filter(ImageFilter.GaussianBlur(25))
    
    frames = []
    num_frames = 20
    for i in range(num_frames):
        # Calculate sine wave for breathing opacity (from 0.35 to 0.95)
        t = (math.sin(i / num_frames * math.tau) + 1.0) / 2.0
        opacity = 0.35 + 0.60 * t
        
        # Build base frame
        frame = Image.new("RGBA", canvas_size, (*bg_color, 255))
        
        # Draw tech background details
        fd = ImageDraw.Draw(frame)
        fd.text((30, 30), "PRECISE PRODUCT EDGE GLOW", font=get_font(22, True), fill=(255, 255, 255, 200))
        fd.text((30, 65), "True alpha-mask breathing silhouette glow", font=get_font(15), fill=(0, 229, 255, 180))
        
        # Draw a technical grid
        for x in range(0, canvas_size[0], 40):
            fd.line([(x, 0), (x, canvas_size[1])], fill=(255, 255, 255, 8))
        for y in range(0, canvas_size[1], 40):
            fd.line([(0, y), (canvas_size[0], y)], fill=(255, 255, 255, 8))
            
        # Paste animated glow
        glow_frame = apply_opacity(glow_blurred, opacity)
        frame.alpha_composite(glow_frame)
        
        # Paste product cutout (static, never warps)
        frame.alpha_composite(prod, (px, py))
        
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
        
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)
    print(f"-> Saved: {output_path.name}")


def build_ambient_particle_drift(product_path: Path, output_path: Path) -> None:
    """Creates soft ambient particles drifting in the background behind the product."""
    print("-> Generating Ambient Particle Drift GIF...")
    prod = white_to_alpha(Image.open(product_path), tolerance=15)
    prod.thumbnail((280, 280), Image.Resampling.LANCZOS)
    
    canvas_size = (800, 450)
    bg_color = (8, 10, 16) # Deep charcoal/black
    
    # Initialize 15 particles with random positions, velocities, and sizes
    import random
    random.seed(42)
    particles = []
    for _ in range(18):
        particles.append({
            "x": random.uniform(0, canvas_size[0]),
            "y": random.uniform(0, canvas_size[1]),
            "vx": random.uniform(-0.8, 0.8),
            "vy": random.uniform(-1.5, -0.4), # Float upwards
            "size": random.uniform(4, 16),
            "alpha": random.randint(30, 120)
        })
        
    frames = []
    num_frames = 24
    for frame_idx in range(num_frames):
        frame = Image.new("RGBA", canvas_size, (*bg_color, 255))
        fd = ImageDraw.Draw(frame)
        
        # Text details
        fd.text((30, 30), "AMBIENT PARTICLE DRIFT", font=get_font(22, True), fill=(255, 255, 255, 200))
        fd.text((30, 65), "Drifting background bokeh particles with product static", font=get_font(15), fill=(255, 176, 54, 180))
        
        # Draw and update particles
        # Create a separate layer to blur the particles slightly
        particle_layer = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        pd = ImageDraw.Draw(particle_layer)
        
        for p in particles:
            # Draw particle as a soft circle
            cx = p["x"] + p["vx"] * frame_idx
            cy = p["y"] + p["vy"] * frame_idx
            # Wrap around canvas
            cx %= canvas_size[0]
            cy %= canvas_size[1]
            
            r = p["size"]
            # Color is soft gold/orange
            pd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 180, 60, p["alpha"]))
            
        # Blur the particles layer slightly for a bokeh look
        particle_layer = particle_layer.filter(ImageFilter.GaussianBlur(3))
        frame.alpha_composite(particle_layer)
        
        # Paste product cutout (static, on top of particles)
        px = (canvas_size[0] - prod.width) // 2
        py = (canvas_size[1] - prod.height) // 2
        frame.alpha_composite(prod, (px, py))
        
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
        
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)
    print(f"-> Saved: {output_path.name}")


def build_badge_pulsate(product_path: Path, output_path: Path) -> None:
    """Creates a pulsate scale/glow effect on a parameter badge."""
    print("-> Generating Badge Pulsate GIF...")
    prod = white_to_alpha(Image.open(product_path), tolerance=15)
    prod.thumbnail((260, 260), Image.Resampling.LANCZOS)
    
    canvas_size = (800, 450)
    bg_color = (12, 20, 32)
    
    # Create the badge base image so we can scale it
    badge_w, badge_h = 160, 100
    badge_base = Image.new("RGBA", (badge_w, badge_h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge_base)
    bd.rounded_rectangle((0, 0, badge_w - 1, badge_h - 1), radius=16, fill=(18, 30, 50, 240), outline=(0, 229, 255, 255), width=3)
    bd.text((22, 18), "22kW", font=get_font(26, True), fill=(0, 229, 255))
    bd.text((22, 54), "FAST CHARGE", font=get_font(13), fill=(255, 255, 255, 200))
    
    frames = []
    num_frames = 16
    for i in range(num_frames):
        # Scale factor oscillates between 0.95 and 1.05
        t = math.sin(i / num_frames * math.tau)
        scale = 1.0 + 0.05 * t
        
        # Build base frame
        frame = Image.new("RGBA", canvas_size, (*bg_color, 255))
        fd = ImageDraw.Draw(frame)
        
        fd.text((30, 30), "BADGE PULSATE EFFECT", font=get_font(22, True), fill=(255, 255, 255, 200))
        fd.text((30, 65), "Oscillating parameters badge scale, product remains static", font=get_font(15), fill=(0, 229, 255, 180))
        
        # Paste product static
        px = int(canvas_size[0] * 0.45)
        py = (canvas_size[1] - prod.height) // 2
        frame.alpha_composite(prod, (px, py))
        
        # Resize badge based on scale
        bw_scaled = int(badge_w * scale)
        bh_scaled = int(badge_h * scale)
        badge_scaled = badge_base.resize((bw_scaled, bh_scaled), Image.Resampling.LANCZOS)
        
        # Paste scaled badge on the left side
        bx = int(canvas_size[0] * 0.15) - (bw_scaled - badge_w) // 2
        by = (canvas_size[1] - bh_scaled) // 2
        
        # Add badge glow behind it
        if scale > 1.0:
            glow_strength = int((scale - 1.0) * 10.0 * 255)
            badge_glow = Image.new("RGBA", badge_scaled.size, (0, 229, 255, 255))
            badge_glow.putalpha(badge_scaled.getchannel("A"))
            # Paste it onto a larger canvas to blur
            bglow_canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
            bglow_canvas.paste(badge_glow, (bx, by))
            bglow_blurred = bglow_canvas.filter(ImageFilter.GaussianBlur(12))
            frame.alpha_composite(apply_opacity(bglow_blurred, (scale - 1.0) * 4.0))
            
        frame.alpha_composite(badge_scaled, (bx, by))
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
        
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)
    print(f"-> Saved: {output_path.name}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    
    product_img = ROOT / "output/emag_exit_two_product_stable_components_v4/assets/D6MHW43BM/12.jpg"
    if not product_img.exists():
        print(f"Error: Product image not found at {product_img}", file=sys.stderr)
        sys.exit(1)
        
    build_precise_product_glow(product_img, OUT / "stable_precise_product_glow.gif")
    build_ambient_particle_drift(product_img, OUT / "stable_ambient_particle_drift.gif")
    build_badge_pulsate(product_img, OUT / "stable_badge_pulsate.gif")
    
    # Create HTML preview for the demo page
    html = (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>eMAG Stable Dynamic Effects Demos</title>'
        '<style>body{margin:0;background:#f0f2f5;font-family:Arial,sans-serif;} '
        'main{max-width:900px;margin:0 auto;padding:24px 12px;} '
        'section{margin-bottom:28px;padding:20px;background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.06);}'
        'h2{margin-top:0;color:#1e293b;} img{max-width:100%;height:auto;border-radius:8px;display:block;}'
        'p{color:#64748b;line-height:1.5;}</style></head>'
        '<body><main>'
        '<h1>eMAG Stable Dynamic Effects (GIF)</h1>'
        '<p>These effects animates secondary overlays and properties while keeping product pixels 100% stable, preventing warp or distortion.</p>'
        
        '<section>'
        '<h2>1. Precise Product Edge Glow</h2>'
        '<p>Creates a breathing neon glow silhouette directly behind the product cutout. Excellent for high-tech tools, cables, or gaming components.</p>'
        '<img src="stable_precise_product_glow.gif">'
        '</section>'
        
        '<section>'
        '<h2>2. Ambient Particle Drift</h2>'
        '<p>Soft drifting background bokeh particles that create depth and visual excitement. Product remains completely static on top.</p>'
        '<img src="stable_ambient_particle_drift.gif">'
        '</section>'
        
        '<section>'
        '<h2>3. Badge Pulsate</h2>'
        '<p>Pulsates the scale and glow of key specification badges to draw user attention, keeping the layout clean and technical.</p>'
        '<img src="stable_badge_pulsate.gif">'
        '</section>'
        
        '</main></body></html>'
    )
    (OUT / "stable_effects_preview.html").write_text(html, encoding="utf-8")
    print(f"-> Generated preview HTML: {OUT / 'stable_effects_preview.html'}")


if __name__ == "__main__":
    main()
