#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/SFNS.ttf",
    ]
    for p in candidates:
        if p and Path(p).exists():
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def text_size(draw, text, fnt):
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def fit(draw, text, max_width, start_size, min_size=22):
    size = start_size
    while size >= min_size:
        f = font(size, True)
        if text_size(draw, text, f)[0] <= max_width:
            return f
        size -= 2
    return font(min_size, True)


def rounded(draw, box, r, fill, outline=None, width=2):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    im = Image.open(args.base).convert("RGBA")
    w, h = im.size
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # Right-side structure matching the direct-text layout, but fully editable.
    headline = (int(w * 0.53), int(h * 0.075), int(w * 0.955), int(h * 0.245))
    cards = [
        ((int(w * 0.58), int(h * 0.305), int(w * 0.955), int(h * 0.425)), "Large\nCapacity", (47, 111, 214, 255)),
        ((int(w * 0.58), int(h * 0.475), int(w * 0.955), int(h * 0.595)), "Organized\nPockets", (245, 176, 0, 255)),
        ((int(w * 0.58), int(h * 0.645), int(w * 0.955), int(h * 0.765)), "Daily\nCarry", (226, 92, 117, 255)),
    ]

    manifest = {
        "method": "hybrid_codex_layout_plus_deterministic_overlay",
        "base_image": args.base,
        "output": args.out,
        "layers": [],
    }

    rounded(d, headline, 28, (255, 255, 255, 238), (236, 164, 178, 210), 3)
    headline_lines = [("Soft Daily", (12, 38, 78, 255)), ("Backpack", (226, 103, 126, 255))]
    y = headline[1] + 24
    for text, color in headline_lines:
        f = fit(d, text, headline[2] - headline[0] - 62, 62, 36)
        d.text((headline[0] + 34, y), text, font=f, fill=color)
        y += text_size(d, text, f)[1] + 10
    manifest["layers"].append({"id": "headline", "type": "editable_text_group", "bbox": list(headline), "texts": ["Soft Daily", "Backpack"]})

    for idx, (box, copy, accent) in enumerate(cards, 1):
        rounded(d, box, 24, (255, 255, 255, 235), (185, 204, 232, 230), 3)
        cx = box[0] + 54
        cy = (box[1] + box[3]) // 2
        d.ellipse((cx - 28, cy - 28, cx + 28, cy + 28), fill=accent)
        # Simple white line icon substitute.
        d.rounded_rectangle((cx - 12, cy - 10, cx + 12, cy + 14), radius=4, outline=(255, 255, 255, 255), width=4)
        d.arc((cx - 12, cy - 22, cx + 12, cy + 4), start=200, end=340, fill=(255, 255, 255, 255), width=4)
        f = font(32, True)
        lines = copy.split("\n")
        total_h = sum(text_size(d, line, f)[1] for line in lines) + (len(lines) - 1) * 5
        yy = box[1] + (box[3] - box[1] - total_h) / 2 - 3
        for line in lines:
            d.text((box[0] + 108, yy), line, font=f, fill=(26, 36, 52, 255))
            yy += text_size(d, line, f)[1] + 5
        manifest["layers"].append({"id": f"feature_card_{idx}", "type": "editable_text_badge", "bbox": list(box), "editable_text": copy.replace("\n", " "), "accent_rgba": list(accent)})

    out = Image.alpha_composite(im, layer).convert("RGB")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.save(args.out, quality=95)
    Path(args.manifest).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
