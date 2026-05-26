#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Supplemental/Verdana Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Verdana.ttf",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def rounded_rect(draw: ImageDraw.ImageDraw, xy, radius: int, fill, outline=None, width: int = 1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def fit_text(draw: ImageDraw.ImageDraw, text: str, font_path_bold: bool, max_width: int, start_size: int, min_size: int = 24):
    size = start_size
    while size >= min_size:
        font = load_font(size, bold=font_path_bold)
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            return font
        size -= 2
    return load_font(min_size, bold=font_path_bold)


def draw_centered_text(draw, box, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = box[0] + (box[2] - box[0] - tw) / 2
    y = box[1] + (box[3] - box[1] - th) / 2 - 2
    draw.text((x, y), text, font=font, fill=fill)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--text-plan", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    image = Image.open(args.base).convert("RGBA")
    w, h = image.size
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    plan = json.loads(Path(args.text_plan).read_text())

    # Semi-transparent headline panel, sized for the actual 1254px test image.
    panel = (int(w * 0.50), int(h * 0.055), int(w * 0.94), int(h * 0.215))
    rounded_rect(draw, panel, radius=28, fill=(255, 255, 255, 232), outline=(218, 226, 238, 255), width=3)
    headline_text = "Soft Daily Backpack"
    headline_font = fit_text(draw, headline_text, True, panel[2] - panel[0] - 60, 58, 30)
    draw_centered_text(draw, panel, headline_text, headline_font, (28, 36, 48, 255))

    badge_specs = [
        ((int(w * 0.61), int(h * 0.255), int(w * 0.94), int(h * 0.365)), "Large Capacity", (31, 111, 235, 255)),
        ((int(w * 0.61), int(h * 0.405), int(w * 0.94), int(h * 0.515)), "Organized Pockets", (245, 176, 0, 255)),
        ((int(w * 0.61), int(h * 0.555), int(w * 0.94), int(h * 0.665)), "Daily Carry", (23, 163, 74, 255)),
    ]

    manifest = {
        "base_image": args.base,
        "output": args.out,
        "text_plan": args.text_plan,
        "layers": [
            {"id": "base_image", "type": "image", "bbox": [0, 0, w, h]},
            {"id": "headline_panel", "type": "shape", "bbox": list(panel), "editable_text": headline_text},
        ],
        "method": "pillow_overlay",
        "editable_text_source": "manifest",
    }

    for idx, (box, text, accent) in enumerate(badge_specs, start=1):
        rounded_rect(draw, box, radius=24, fill=(255, 255, 255, 238), outline=(214, 224, 238, 255), width=3)
        dot = (box[0] + 24, box[1] + 24, box[0] + 70, box[1] + 70)
        draw.ellipse(dot, fill=accent)
        font = fit_text(draw, text, True, box[2] - box[0] - 118, 40, 24)
        text_box = (box[0] + 88, box[1], box[2] - 18, box[3])
        draw_centered_text(draw, text_box, text, font, (28, 36, 48, 255))
        manifest["layers"].append({
            "id": f"badge_{idx}",
            "type": "text_badge",
            "bbox": list(box),
            "editable_text": text,
            "accent_rgba": list(accent),
        })

    result = Image.alpha_composite(image, overlay).convert("RGB")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    result.save(args.out, quality=95)
    Path(args.manifest).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
