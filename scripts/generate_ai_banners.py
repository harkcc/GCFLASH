#!/usr/bin/env python3
"""Generate premium eMAG banners using fal.ai background generation and PIL local composition."""

from __future__ import annotations

import argparse
import json
import os
import sys
import math
from pathlib import Path
from urllib.request import urlretrieve

import fal_client
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path("/Users/cc/Desktop/photo_show")
OUT = ROOT / "output/emag_banner_generation_tests"
FONTS_DIR = ROOT / "assets" / "fonts"
GOOGLE_FONTS_DIR = FONTS_DIR / "google_fonts"

# Base prompt templates for premium backgrounds (no text, no products, no logos)
BACKGROUND_TEMPLATES = {
    "glassmorphism": (
        "A premium high-impact web banner background template with a frosted glassmorphism card floating "
        "on a dark navy and electric blue gradient background. Soft blurred neon cyan and purple light circles "
        "in the background. Ultra modern, clean, sleek, high-tech aesthetic, subtle glass reflections, depth of field. "
        "3D render style. Completely blank: no text, no letters, no logos, no products, no watermarks, no frames."
    ),
    "premium_dark": (
        "An industrial premium web banner background template. Dark gray brushed metal surface, diagonal carbon fiber grid patterns. "
        "Sharp accent lines of gold and neon blue glowing light cutting across. Highly technical, energetic, high contrast, "
        "clean commercial studio lighting. Completely blank: no text, no letters, no logos, no products, no watermarks, no frames."
    ),
    "organic_wood": (
        "A clean organic lifestyle web banner background template. A light beige travertine stone or terrazzo marble table surface "
        "next to a warm natural wood wall. Soft, warm afternoon sunlight casting delicate diagonal shadows of leaves across the scene. "
        "Cozy, organic, premium minimalist spa aesthetic. Completely blank: no text, no letters, no logos, no products, no watermarks, no frames."
    )
}


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_font(font_name: str, size: int) -> ImageFont.ImageFont:
    """Load a specific font from local assets or fall back to system fonts."""
    # Check Google Fonts directory first
    for ext in ["Regular.ttf", "-wght.ttf", ".ttf"]:
        probe = GOOGLE_FONTS_DIR / f"{font_name}{ext}"
        if probe.exists():
            return ImageFont.truetype(str(probe), size=size)
        probe_lower = GOOGLE_FONTS_DIR / f"{font_name.lower()}{ext}"
        if probe_lower.exists():
            return ImageFont.truetype(str(probe_lower), size=size)
            
    # Check base fonts directory
    probe_base = FONTS_DIR / font_name
    if probe_base.exists():
        return ImageFont.truetype(str(probe_base), size=size)

    # Standard fallback
    candidates = [
        str(FONTS_DIR / "Arial.ttf"),
        str(FONTS_DIR / "Arial Bold.ttf"),
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def white_to_alpha(image: Image.Image, tolerance: int = 15) -> Image.Image:
    """Removes a clean white background from an image to create a cutout."""
    rgba = image.convert("RGBA")
    data = rgba.getdata()
    new_data = []
    for item in data:
        # Check if color is close to white
        r, g, b, a = item
        if r > (255 - tolerance) and g > (255 - tolerance) and b > (255 - tolerance):
            # Make fully transparent
            new_data.append((r, g, b, 0))
        else:
            new_data.append(item)
    rgba.putdata(new_data)
    
    # Auto crop to bounding box
    bbox = rgba.getbbox()
    if bbox:
        rgba = rgba.crop(bbox)
    return rgba


def draw_text_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int, int] | str,
    max_width: int,
    line_gap: int = 6
) -> int:
    """Draws text wrapped within max_width and returns the bottom y-coordinate."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        probe = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), probe, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width or not current_line:
            current_line = probe
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
        
    x, y = xy
    line_h = draw.textbbox((0, 0), "Ag", font=font)[3] + line_gap
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y


def draw_brand_tag(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    accent_color: tuple[int, int, int, int],
    bg_color: tuple[int, int, int, int],
    text_color: tuple[int, int, int, int]
) -> None:
    """Draws a premium rounded EXCITAT brand tag."""
    draw.rounded_rectangle(box, radius=12, fill=bg_color, outline=accent_color, width=2)
    font_brand = get_font("Orbitron", 18)
    # Centered text in box
    text = "EXCITAT"
    bbox = draw.textbbox((0, 0), text, font=font_brand)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    bx1, by1, bx2, by2 = box
    cx = bx1 + (bx2 - bx1 - tw) // 2
    cy = by1 + (by2 - by1 - th) // 2 - 2
    draw.text((cx, cy), text, font=font_brand, fill=text_color)


def generate_background(style: str, width: int, height: int, run_ai: bool) -> Path:
    """Obtains the background image, either by calling fal.ai or returning a cached/placeholder one."""
    bg_file = OUT / f"bg_{style}_{width}x{height}.png"
    if bg_file.exists():
        print(f"-> Using cached background: {bg_file}")
        return bg_file
        
    if not run_ai:
        print(f"-> [Dry Run] Creating local synthetic placeholder background for {style}")
        # Create a beautiful gradient placeholder
        img = Image.new("RGBA", (width, height), (15, 23, 42, 255))
        d = ImageDraw.Draw(img)
        if style == "glassmorphism":
            # Dark blue to violet gradient
            for y in range(height):
                t = y / height
                r = int(15 * (1 - t) + 40 * t)
                g = int(23 * (1 - t) + 16 * t)
                b = int(42 * (1 - t) + 80 * t)
                d.line([(0, y), (width, y)], fill=(r, g, b, 255))
            # Floating glow circles
            d.ellipse((width - 300, 50, width - 100, 250), fill=(0, 229, 255, 30))
            d.ellipse((100, height - 200, 300, height - 50), fill=(217, 70, 239, 20))
        elif style == "premium_dark":
            # Charcoal to deep gray gradient
            for y in range(height):
                t = y / height
                val = int(20 * (1 - t) + 10 * t)
                d.line([(0, y), (width, y)], fill=(val, val, val + 5, 255))
            # Metallic accents
            d.line([(0, 0), (width, height)], fill=(255, 176, 54, 15), width=4)
        else: # organic_wood
            # Sand to warm beige gradient
            for y in range(height):
                t = y / height
                r = int(245 * (1 - t) + 235 * t)
                g = int(240 * (1 - t) + 220 * t)
                b = int(230 * (1 - t) + 200 * t)
                d.line([(0, y), (width, y)], fill=(r, g, b, 255))
        img.save(bg_file)
        return bg_file

    print(f"-> Calling fal.ai (flux-pro/v1.1) to generate background for {style}...")
    prompt = BACKGROUND_TEMPLATES[style]
    
    # fal flux supports width/height. We will snap them to multiples of 32
    gen_w = int(math.ceil(width / 32) * 32)
    gen_h = int(math.ceil(height / 32) * 32)
    
    result = fal_client.subscribe(
        "fal-ai/flux-pro/v1.1",
        arguments={
            "prompt": prompt,
            "image_size": {"width": gen_w, "height": gen_h},
            "num_images": 1,
            "safety_tolerance": "5",
            "output_format": "png",
        },
        with_logs=True
    )
    
    images = result.get("images") or []
    if not images:
        raise RuntimeError("FAL returned no images!")
        
    url = images[0]["url"]
    temp_download = OUT / f"temp_{style}.png"
    print(f"-> Downloading background from: {url}")
    urlretrieve(url, temp_download)
    
    # Load and crop/resize to exact target size
    img = Image.open(temp_download)
    if img.size != (width, height):
        print(f"-> Resizing/cropping background from {img.size} to {(width, height)}")
        img = img.resize((width, height), Image.Resampling.LANCZOS)
    img.save(bg_file)
    if temp_download.exists():
        temp_download.unlink()
        
    return bg_file


def paste_product_with_shadow(
    base: Image.Image,
    product: Image.Image,
    position: tuple[int, int],
    shadow_offset: tuple[int, int] = (15, 20),
    shadow_blur: int = 25,
    shadow_alpha: int = 140
) -> None:
    """Pastes product cutout onto base image with a beautiful soft blurred drop shadow."""
    x, y = position
    pw, ph = product.size
    
    # Create shadow canvas same size as base
    shadow_canvas = Image.new("RGBA", base.size, (0, 0, 0, 0))
    # Extract alpha mask of the product
    alpha = product.convert("RGBA").getchannel("A")
    
    # Create shadow mask pasted with offset
    shadow_mask = Image.new("L", base.size, 0)
    shadow_mask.paste(alpha, (x + shadow_offset[0], y + shadow_offset[1]))
    # Apply Gaussian blur
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(shadow_blur))
    
    # Draw soft black shadow onto shadow_canvas using the blurred mask
    d_shadow = ImageDraw.Draw(shadow_canvas)
    d_shadow.bitmap((0, 0), shadow_mask, fill=(0, 0, 0, shadow_alpha))
    
    # Composite shadow, then product
    base.alpha_composite(shadow_canvas)
    base.alpha_composite(product.convert("RGBA"), (x, y))


def assemble_banner(
    bg_path: Path,
    product_path: Path,
    title: str,
    subtitle: str,
    style: str,
    output_path: Path
) -> None:
    """Composites product and premium text overlays onto the generated background."""
    print(f"-> Assembling final banner: {output_path.name}")
    canvas = Image.open(bg_path).convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    
    # Load and process product cutout
    prod_raw = Image.open(product_path)
    # Check if we need to remove white background
    # Usually product_path is a raw white-bg jpg or a pre-cut png
    if product_path.suffix.lower() in [".jpg", ".jpeg"] or prod_raw.mode != "RGBA":
        print(f"   -> Processing product white-to-alpha for: {product_path.name}")
        product = white_to_alpha(prod_raw, tolerance=15)
    else:
        product = prod_raw.convert("RGBA")
        
    # Resize product to fit nicely (about 40-45% of banner height)
    target_ph = int(canvas.height * 0.75)
    scale = target_ph / product.height
    target_pw = int(product.width * scale)
    product_resized = product.resize((target_pw, target_ph), Image.Resampling.LANCZOS)
    
    # Determine colors based on style
    if style in ["glassmorphism", "premium_dark"]:
        accent_color = (0, 229, 255, 255) # Electric cyan
        text_primary = (255, 255, 255, 255)
        text_secondary = (180, 200, 230, 255)
        tag_bg = (10, 18, 30, 220)
    else: # organic_wood
        accent_color = (194, 120, 60, 255) # Warm terra cotta / wood brown
        text_primary = (30, 28, 25, 255)
        text_secondary = (100, 95, 90, 255)
        tag_bg = (255, 255, 255, 220)
        
    # Position product in the right half
    # px = canvas.width - product_resized.width - int(canvas.width * 0.08)
    px = int(canvas.width * 0.58)
    py = (canvas.height - product_resized.height) // 2
    paste_product_with_shadow(canvas, product_resized, (px, py))
    
    # Left-side layout details
    lx = int(canvas.width * 0.06)
    ly = int(canvas.height * 0.12)
    
    # Draw EXCITAT brand tag
    draw_brand_tag(draw, (lx, ly, lx + 120, ly + 36), accent_color, tag_bg, text_primary)
    
    # Load premium Google fonts for title and body
    font_title = get_font("Orbitron", 38)
    font_sub = get_font("Arial", 20)
    
    # Draw Title
    ly_text = ly + 65
    bottom_y = draw_text_wrapped(draw, (lx, ly_text), title, font_title, text_primary, max_width=int(canvas.width * 0.46), line_gap=8)
    
    # Draw Subtitle/Specs
    ly_sub = bottom_y + 12
    draw_text_wrapped(draw, (lx, ly_sub), subtitle, font_sub, text_secondary, max_width=int(canvas.width * 0.46), line_gap=6)
    
    # Save output
    canvas.convert("RGB").save(output_path, quality=94)
    print(f"-> Banner saved: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate AI Background + Local Composite Banners")
    parser.add_argument("--run-ai", action="store_true", help="Call fal.ai API to generate real backgrounds. If false, creates gradient placeholders.")
    parser.add_argument("--style", default="glassmorphism", choices=list(BACKGROUND_TEMPLATES.keys()), help="Style of background to generate")
    parser.add_argument("--width", type=int, default=1140, help="Banner width")
    parser.add_argument("--height", type=int, default=456, help="Banner height")
    args = parser.parse_args()
    
    load_env(ROOT / ".env")
    
    if args.run_ai and not os.environ.get("FAL_KEY"):
        print("Error: FAL_KEY is not set in environment or .env file, but --run-ai was requested.", file=sys.stderr)
        sys.exit(1)
        
    OUT.mkdir(parents=True, exist_ok=True)
    
    # Locate a product image from the workspace to use
    # Let's search output/emag_exit_two_product_stable_components_v4/assets/D6MHW43BM/12.jpg
    product_img = ROOT / "output/emag_exit_two_product_stable_components_v4/assets/D6MHW43BM/12.jpg"
    if not product_img.exists():
        # Fall back to any image in that folder
        product_dir = ROOT / "output/emag_exit_two_product_stable_components_v4/assets/D6MHW43BM"
        if product_dir.exists():
            candidates = list(product_dir.glob("*.jpg"))
            if candidates:
                product_img = candidates[0]
            else:
                print("Error: No product images found in D6MHW43BM asset directory.", file=sys.stderr)
                sys.exit(1)
        else:
            print("Error: Product asset directory does not exist.", file=sys.stderr)
            sys.exit(1)
            
    print(f"Using product image: {product_img.name}")
    
    # 1. Generate background
    bg_path = generate_background(args.style, args.width, args.height, args.run_ai)
    
    # 2. Assemble banner
    output_name = f"banner_{args.style}_{'ai' if args.run_ai else 'placeholder'}.jpg"
    output_path = OUT / output_name
    
    # Define premium text values
    if args.style == "glassmorphism":
        title = "Premium EV Charging Cable"
        subtitle = "Type 2 | 22kW | Three Phase | IP65 Waterproof\nSafe charging anywhere, anytime."
    elif args.style == "premium_dark":
        title = "22kW Ultra-Fast EV Charger"
        subtitle = "Industrial grade reliability.\nDesigned for fast, high-performance charging cycles."
    else: # organic_wood
        title = "Minimalist Travel charging"
        subtitle = "Includes elegant storage bag.\nConvenient and eco-friendly charging lifestyle."
        
    assemble_banner(bg_path, product_img, title, subtitle, args.style, output_path)


if __name__ == "__main__":
    main()
