#!/usr/bin/env python3
"""Template-driven eMAG Banner Generator using Reference Images (Img2Img).

Accepts a JSON config describing the product, style, colors, and layout,
uploads a reference template image from the Desktop/banner folder, calls
fal.ai's Image-to-Image API to generate the background, and composites the
product and text locally.
"""

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
BANNER_REF_DIR = Path("/Users/cc/Desktop/banner")
FONTS_DIR = ROOT / "assets" / "fonts"
GOOGLE_FONTS_DIR = FONTS_DIR / "google_fonts"

# Pre-defined style templates matching generate_templated_banner.py
STYLE_TEMPLATES = {
    "glassmorphism": {
        "prompt_template": (
            "A premium high-impact web banner background template with a frosted glassmorphism card floating "
            "on a {color_1} and {color_2} gradient background. Soft blurred neon {accent_color} light circles "
            "in the background. Ultra modern, clean, sleek, high-tech aesthetic, subtle glass reflections, depth of field. "
            "3D render style. Completely blank: no text, no letters, no logos, no products, no watermarks, no frames."
        ),
        "defaults": {
            "color_1": "dark navy",
            "color_2": "electric blue",
            "accent_color": "cyan"
        },
        "styling": {
            "accent_color_rgb": (0, 229, 255, 255),
            "text_primary_rgb": (255, 255, 255, 255),
            "text_secondary_rgb": (180, 200, 230, 255),
            "tag_bg_rgb": (10, 18, 30, 220),
            "font_title": "Orbitron",
            "font_body": "Arial"
        },
        "default_ref": "img_v3_02120_86e9c5a3-a999-4fd0-ad22-bb34544737bg.jpg" # Horizontal cyan/purple neon banner template
    },
    "premium_dark": {
        "prompt_template": (
            "An industrial premium web banner background template. Dark {color_1} brushed metal surface, "
            "diagonal carbon fiber grid patterns. Sharp accent lines of {accent_color} and {color_2} glowing light cutting across. "
            "Highly technical, energetic, high contrast, clean commercial studio lighting. "
            "Completely blank: no text, no letters, no logos, no products, no watermarks, no frames."
        ),
        "defaults": {
            "color_1": "gray",
            "color_2": "cobalt blue",
            "accent_color": "neon gold"
        },
        "styling": {
            "accent_color_rgb": (255, 176, 54, 255),
            "text_primary_rgb": (255, 255, 255, 255),
            "text_secondary_rgb": (200, 210, 225, 255),
            "tag_bg_rgb": (15, 15, 20, 230),
            "font_title": "Orbitron",
            "font_body": "Arial"
        },
        "default_ref": "img_v3_02120_8765ee8f-75a8-4e47-8e08-ca536a39719g.jpg" # Horizontal gold banner template
    },
    "organic_wood": {
        "prompt_template": (
            "A clean organic lifestyle web banner background template. A light {color_1} travertine stone or terrazzo marble table surface "
            "next to a warm natural {color_2} wood wall. Soft, warm afternoon sunlight casting delicate diagonal shadows of {accent_color} across the scene. "
            "Cozy, organic, premium minimalist spa aesthetic. Completely blank: no text, no letters, no logos, no products, no watermarks, no frames."
        ),
        "defaults": {
            "color_1": "beige",
            "color_2": "oak",
            "accent_color": "tree leaves"
        },
        "styling": {
            "accent_color_rgb": (194, 120, 60, 255),
            "text_primary_rgb": (33, 30, 27, 255),
            "text_secondary_rgb": (110, 100, 95, 255),
            "tag_bg_rgb": (255, 255, 255, 220),
            "font_title": "RussoOne",
            "font_body": "Arial"
        },
        "default_ref": "img_v3_02120_5cac50f6-f295-40f4-98b6-5f2764bcbddg.jpg" # Horizontal soft ambient banner template
    }
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


def get_font(font_name: str, size: int, bold: bool = False) -> ImageFont.ImageFont:
    actual_name = font_name
    if bold and font_name.lower() == "arial":
        actual_name = "Arial Bold"
        
    for ext in ["Regular.ttf", "-wght.ttf", "-Regular.ttf", ".ttf", ".ttc"]:
        probe = GOOGLE_FONTS_DIR / f"{actual_name}{ext}"
        if probe.exists():
            return ImageFont.truetype(str(probe), size=size)
        probe_lower = GOOGLE_FONTS_DIR / f"{actual_name.lower()}{ext}"
        if probe_lower.exists():
            return ImageFont.truetype(str(probe_lower), size=size)
            
    probe_base = FONTS_DIR / actual_name
    if probe_base.exists():
        return ImageFont.truetype(str(probe_base), size=size)
    if bold:
        probe_base_bold = FONTS_DIR / "Arial Bold.ttf"
        if probe_base_bold.exists():
            return ImageFont.truetype(str(probe_base_bold), size=size)

    # Fallbacks
    candidates = [
        str(FONTS_DIR / ("Arial Bold.ttf" if bold else "Arial.ttf")),
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def remove_white_bg(image: Image.Image, tolerance: int = 15) -> Image.Image:
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


def wrap_text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
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
    return lines


def draw_brand_tag(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    accent_color: tuple[int, int, int, int],
    bg_color: tuple[int, int, int, int],
    text_color: tuple[int, int, int, int]
) -> None:
    draw.rounded_rectangle(box, radius=12, fill=bg_color, outline=accent_color, width=2)
    font_brand = get_font("Orbitron", 18)
    text = "EXCITAT"
    bbox = draw.textbbox((0, 0), text, font=font_brand)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    bx1, by1, bx2, by2 = box
    cx = bx1 + (bx2 - bx1 - tw) // 2
    cy = by1 + (by2 - by1 - th) // 2 - 2
    draw.text((cx, cy), text, font=font_brand, fill=text_color)


def paste_product_shadow(
    base: Image.Image,
    product: Image.Image,
    position: tuple[int, int],
    offset: tuple[int, int] = (15, 20),
    blur: int = 25,
    alpha_val: int = 130
) -> None:
    x, y = position
    shadow_canvas = Image.new("RGBA", base.size, (0, 0, 0, 0))
    alpha = product.convert("RGBA").getchannel("A")
    shadow_mask = Image.new("L", base.size, 0)
    shadow_mask.paste(alpha, (x + offset[0], y + offset[1]))
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(blur))
    
    d_shadow = ImageDraw.Draw(shadow_canvas)
    d_shadow.bitmap((0, 0), shadow_mask, fill=(0, 0, 0, alpha_val))
    
    base.alpha_composite(shadow_canvas)
    base.alpha_composite(product.convert("RGBA"), (x, y))


def generate_ref_bg(
    style: str,
    colors: dict[str, str],
    ref_image_path: Path,
    width: int,
    height: int,
    strength: float,
    run_ai: bool,
    use_redux: bool = False
) -> Path:
    """Generate or retrieve background by using reference image to guide style/composition."""
    color_slug = "_".join(f"{k}-{v.replace(' ', '')}" for k, v in sorted(colors.items()))
    ref_slug = ref_image_path.stem.replace("img_v3_02120_", "")[:8]
    method_slug = "redux" if use_redux else "img2img"
    bg_file = OUT / f"bg_{method_slug}_{style}_{ref_slug}_{color_slug}_{width}x{height}.png"
    
    if bg_file.exists():
        print(f"-> Using cached background: {bg_file.name}")
        return bg_file
        
    template_config = STYLE_TEMPLATES[style]
    prompt = template_config["prompt_template"].format(**colors)
    
    if not run_ai:
        print(f"-> [Dry Run] Copying reference image as placeholder background for {style}")
        # Just resize the reference image as the placeholder
        img = Image.open(ref_image_path).convert("RGBA")
        img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
        img_resized.save(bg_file)
        return bg_file

    print(f"-> Uploading reference image: {ref_image_path.name} to fal.ai...")
    ref_url = fal_client.upload_file(str(ref_image_path))
    print(f"   ✓ Uploaded URL: {ref_url}")

    # fal supports width/height. Snapping them to multiples of 32
    gen_w = int(math.ceil(width / 32) * 32)
    gen_h = int(math.ceil(height / 32) * 32)

    if use_redux:
        print(f"-> Calling fal.ai Flux Redux (style variation) model...")
        result = fal_client.subscribe(
            "fal-ai/flux-pro/v1.1/redux",
            arguments={
                "prompt": prompt,
                "image_url": ref_url,
                "image_size": {"width": gen_w, "height": gen_h},
                "num_images": 1,
                "safety_tolerance": "5",
                "output_format": "png",
            },
            with_logs=True
        )
    else:
        print(f"-> Calling fal.ai Flux Image-to-Image model (strength={strength})...")
        result = fal_client.subscribe(
            "fal-ai/flux-general/image-to-image",
            arguments={
                "prompt": prompt,
                "image_url": ref_url,
                "strength": strength,
                "image_size": {"width": gen_w, "height": gen_h},
                "num_images": 1,
                "safety_tolerance": "5",
                "output_format": "png",
            },
            with_logs=True
        )
    
    images = result.get("images") or []
    if not images:
        raise RuntimeError("fal.ai returned no images")
        
    url = images[0]["url"]
    temp_download = OUT / f"temp_ref_gen.png"
    urlretrieve(url, temp_download)
    
    img = Image.open(temp_download)
    if img.size != (width, height):
        img = img.resize((width, height), Image.Resampling.LANCZOS)
    img.save(bg_file)
    if temp_download.exists():
        temp_download.unlink()
        
    return bg_file


def run_job(job_config: dict, run_ai: bool) -> Path:
    """Executes a banner generation job based on reference image + prompt configuration."""
    style = job_config.get("style", "glassmorphism")
    if style not in STYLE_TEMPLATES:
        raise ValueError(f"Unknown style template: {style}")
        
    dim = job_config.get("dimensions", {"width": 1140, "height": 456})
    width, height = dim.get("width", 1140), dim.get("height", 456)
    
    style_def = STYLE_TEMPLATES[style]
    colors = {**style_def["defaults"], **job_config.get("colors", {})}
    styling = style_def["styling"]
    
    # 1. Resolve reference image path
    ref_name = job_config.get("reference_image") or style_def["default_ref"]
    ref_image_path = BANNER_REF_DIR / ref_name
    if not ref_image_path.exists():
        # Search fallback: pick first available jpg
        candidates = sorted(list(BANNER_REF_DIR.glob("*.jpg")))
        if candidates:
            print(f"Warning: Selected reference '{ref_name}' not found, falling back to '{candidates[0].name}'")
            ref_image_path = candidates[0]
        else:
            raise FileNotFoundError(f"No reference images found in: {BANNER_REF_DIR}")
            
    prod_path = Path(job_config["product_image"])
    title = job_config.get("product_title", "Product Title")
    attributes = job_config.get("attributes", [])
    strength = job_config.get("strength", 0.60)
    use_redux = job_config.get("use_redux", False)
    
    print(f"\n=== Running Reference-Driven Banner Job for: {title} ===")
    print(f"Style: {style} | Reference Template: {ref_image_path.name}")
    print(f"Target Size: {width}x{height} | Strength: {strength} | Redux: {use_redux}")
    
    # 2. Get Background using Img2Img / Redux
    bg_path = generate_ref_bg(style, colors, ref_image_path, width, height, strength, run_ai, use_redux)
    
    # 3. Load Background and Draw
    canvas = Image.open(bg_path).convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    
    # 4. Process product image
    prod_raw = Image.open(prod_path)
    if prod_raw.mode != "RGBA" or prod_path.suffix.lower() in [".jpg", ".jpeg"]:
        product = remove_white_bg(prod_raw, tolerance=15)
    else:
        product = prod_raw.convert("RGBA")
        
    # Scale product
    layout = job_config.get("layout", "product-right")
    target_ph = int(height * 0.76)
    scale = target_ph / product.height
    target_pw = int(product.width * scale)
    product_resized = product.resize((target_pw, target_ph), Image.Resampling.LANCZOS)
    
    # Position product
    if layout == "product-left":
        px = int(width * 0.08)
        py = (height - product_resized.height) // 2
        lx = int(width * 0.52)
        text_max_w = int(width * 0.42)
    elif layout == "product-center":
        px = (width - product_resized.width) // 2
        py = int(height * 0.20)
        lx = int(width * 0.06)
        text_max_w = int(width * 0.88)
    else: # product-right (default)
        px = int(width * 0.58)
        py = (height - product_resized.height) // 2
        lx = int(width * 0.06)
        text_max_w = int(width * 0.46)
        
    # Paste product with shadow
    paste_product_shadow(canvas, product_resized, (px, py))
    
    # 5. Draw text overlays
    ly = int(height * 0.12)
    accent_rgb = styling["accent_color_rgb"]
    text_pri_rgb = styling["text_primary_rgb"]
    text_sec_rgb = styling["text_secondary_rgb"]
    tag_bg_rgb = styling["tag_bg_rgb"]
    
    # Brand Tag
    draw_brand_tag(draw, (lx, ly, lx + 120, ly + 36), accent_rgb, tag_bg_rgb, text_pri_rgb)
    
    # Fonts
    font_title = get_font(styling["font_title"], 38)
    font_sub = get_font(styling["font_body"], 19)
    
    # Wrap and draw title
    ly_text = ly + 65
    title_lines = wrap_text_width(draw, title, font_title, text_max_w)
    line_h_title = draw.textbbox((0, 0), "Ag", font=font_title)[3] + 8
    for line in title_lines:
        draw.text((lx, ly_text), line, font=font_title, fill=text_pri_rgb)
        ly_text += line_h_title
        
    # Draw attributes
    ly_sub = ly_text + 12
    line_h_sub = draw.textbbox((0, 0), "Ag", font=font_sub)[3] + 6
    for attr in attributes:
        bullet_text = f"•  {attr}"
        draw.text((lx, ly_sub), bullet_text, font=font_sub, fill=text_sec_rgb)
        ly_sub += line_h_sub
        
    # Save output
    output_name = f"ref_banner_{style}_{'redux' if use_redux else 'img2img'}_{'ai' if run_ai else 'placeholder'}.jpg"
    output_path = OUT / output_name
    canvas.convert("RGB").save(output_path, quality=94)
    print(f"-> Completed Banner assembly: {output_path.name}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Template-driven reference-guided eMAG Banner Builder")
    parser.add_argument("--job", help="Path to job JSON config file. If not provided, runs a batch of styles.")
    parser.add_argument("--run-ai", action="store_true", help="Connect to fal.ai to generate real background using reference image.")
    args = parser.parse_args()
    
    load_env(ROOT / ".env")
    
    if args.run_ai and not os.environ.get("FAL_KEY"):
        print("Error: FAL_KEY not found in environment or .env file, but --run-ai was requested.", file=sys.stderr)
        sys.exit(1)
        
    OUT.mkdir(parents=True, exist_ok=True)
    
    if args.job:
        job_path = Path(args.job).expanduser().resolve()
        if not job_path.exists():
            print(f"Error: Job file not found: {job_path}", file=sys.stderr)
            sys.exit(1)
        with job_path.open("r", encoding="utf-8") as f:
            job_config = json.load(f)
        run_job(job_config, args.run_ai)
    else:
        # Batch generate 3 styles to show variety and stability
        default_product = "output/emag_exit_two_product_stable_components_v4/assets/D6MHW43BM/12.jpg"
        
        jobs = [
            {
                "product_image": default_product,
                "product_title": "EXCITAT Premium EV Cable",
                "attributes": [
                    "Type 2 Male-to-Female connection",
                    "22kW Three Phase power supply",
                    "IP65 waterproof protection",
                    "Includes durable storage bag"
                ],
                "style": "glassmorphism",
                "colors": {
                    "color_1": "deep violet",
                    "color_2": "electric indigo",
                    "accent_color": "bright magenta"
                },
                "dimensions": {"width": 1140, "height": 456},
                "layout": "product-right",
                "strength": 0.60
            },
            {
                "product_image": default_product,
                "product_title": "EXCITAT Industrial EV Charger",
                "attributes": [
                    "Heavy-duty copper contact pins",
                    "TPU high-tension strain relief",
                    "Tested for 10,000+ plug cycles",
                    "Universal EU compatibility"
                ],
                "style": "premium_dark",
                "colors": {
                    "color_1": "dark grey",
                    "color_2": "neon blue",
                    "accent_color": "amber orange"
                },
                "dimensions": {"width": 1140, "height": 456},
                "layout": "product-right",
                "strength": 0.65
            },
            {
                "product_image": default_product,
                "product_title": "EXCITAT Travel Companion",
                "attributes": [
                    "Lightweight flexible TPU sleeve",
                    "Soft water-resistant carry bag",
                    "Eco-friendly materials",
                    "Romanian local support"
                ],
                "style": "organic_wood",
                "colors": {
                    "color_1": "warm sand",
                    "color_2": "light teak",
                    "accent_color": "olive green"
                },
                "dimensions": {"width": 1140, "height": 456},
                "layout": "product-right",
                "strength": 0.55
            }
        ]
        
        for job in jobs:
            run_job(job, args.run_ai)


if __name__ == "__main__":
    main()
