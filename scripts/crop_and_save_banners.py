#!/usr/bin/env python3
"""Crops the newly generated 1:1 square banners into standard eMAG 1140x456px (2.5:1) formats."""

from pathlib import Path
from PIL import Image

ROOT = Path("/Users/cc/Desktop/photo_show")
BRAIN_DIR = Path("/Users/cc/.gemini/antigravity/brain/1367e8e5-d106-4385-8319-4bfc66dff76c")
OUT = ROOT / "output/emag_banner_generation_tests"

def crop_center_ratio(img_path: Path, output_path: Path, target_w: int = 1140, target_h: int = 456) -> None:
    if not img_path.exists():
        print(f"Error: source not found: {img_path}")
        return
        
    img = Image.open(img_path)
    # Target aspect ratio
    ratio = target_w / target_h
    
    # Calculate crop coordinates for center band
    current_w, current_h = img.size
    crop_h = int(current_w / ratio)
    
    if crop_h > current_h:
        # Fall back to landscape scale
        crop_w = int(current_h * ratio)
        left = (current_w - crop_w) // 2
        top = 0
        right = left + crop_w
        bottom = current_h
    else:
        left = 0
        top = (current_h - crop_h) // 2
        right = current_w
        bottom = top + crop_h
        
    cropped = img.crop((left, top, right, bottom))
    resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    resized.save(output_path, "JPEG", quality=94)
    print(f"✓ Cropped and resized {img_path.name} -> {output_path.name} ({target_w}x{target_h})")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    
    # Match the newly generated image files inside the brain directory
    # Find files based on prefix
    glassmorphism_src = list(BRAIN_DIR.glob("glassmorphism_banner_ai_*.png"))
    premium_dark_src = list(BRAIN_DIR.glob("premium_dark_banner_ai_*.png"))
    organic_wood_src = list(BRAIN_DIR.glob("organic_wood_banner_ai_*.png"))
    
    if glassmorphism_src:
        crop_center_ratio(glassmorphism_src[-1], OUT / "generator_banner_glassmorphism.jpg")
    if premium_dark_src:
        crop_center_ratio(premium_dark_src[-1], OUT / "generator_banner_premium_dark.jpg")
    if organic_wood_src:
        crop_center_ratio(organic_wood_src[-1], OUT / "generator_banner_organic_wood.jpg")

if __name__ == "__main__":
    main()
