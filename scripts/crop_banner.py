#!/usr/bin/env python3
"""Crops a 2.5:1 aspect ratio banner from the center of a square image and resizes it to 1140x456."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from PIL import Image


def crop_to_banner(input_path: Path, output_path: Path, target_w: int = 1140, target_h: int = 456) -> None:
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
        
    img = Image.open(input_path)
    w, h = img.size
    print(f"-> Processing image: {input_path.name} ({w}x{h})")
    
    # Calculate crop height based on 2.5:1 aspect ratio (1140/456 = 2.5)
    target_ratio = target_w / target_h
    
    # If the source is square, we crop a slice from the center
    # crop_h = w / target_ratio
    crop_h = int(w / target_ratio)
    if crop_h > h:
        # If the target height is taller than available height, we crop width instead
        crop_w = int(h * target_ratio)
        crop_h = h
        left = (w - crop_w) // 2
        top = 0
        right = left + crop_w
        bottom = h
    else:
        left = 0
        top = (h - crop_h) // 2
        right = w
        bottom = top + crop_h
        
    print(f"-> Cropping box: ({left}, {top}, {right}, {bottom})")
    cropped = img.crop((left, top, right, bottom))
    
    # Resize to exact target dimensions
    resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    resized.save(output_path, quality=94)
    print(f"-> Saved banner: {output_path} ({target_w}x{target_h})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Crop square images to 2.5:1 banners")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output image path")
    parser.add_argument("--width", type=int, default=1140, help="Target width")
    parser.add_argument("--height", type=int, default=456, help="Target height")
    args = parser.parse_args()
    
    crop_to_banner(Path(args.input), Path(args.output), args.width, args.height)


if __name__ == "__main__":
    main()
