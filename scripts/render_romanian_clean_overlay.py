#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def load_font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Avenir Next Condensed.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/SFNS.ttf",
    ]
    for path in candidates:
        if path and Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def measure(draw, text, f):
    b = draw.textbbox((0, 0), text, font=f)
    return b[2] - b[0], b[3] - b[1]


def fit(draw, text, max_width, start, min_size=18, bold=True):
    for size in range(start, min_size - 1, -2):
        f = load_font(size, bold)
        if measure(draw, text, f)[0] <= max_width:
            return f
    return load_font(min_size, bold)


def rr(draw, box, radius, fill, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def shadow(layer, box, radius=30, blur=18, opacity=42):
    s = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(s)
    sd.rounded_rectangle(box, radius=radius, fill=(20, 30, 55, opacity))
    s = s.filter(ImageFilter.GaussianBlur(blur))
    layer.alpha_composite(s)


def draw_bag_icon(draw, cx, cy, color=(255, 255, 255, 255), scale=1.0):
    w = int(25 * scale)
    h = int(28 * scale)
    draw.rounded_rectangle((cx - w, cy - h // 3, cx + w, cy + h), radius=int(7 * scale), outline=color, width=max(2, int(4 * scale)))
    draw.arc((cx - int(18 * scale), cy - int(26 * scale), cx + int(18 * scale), cy + int(11 * scale)), 200, 340, fill=color, width=max(2, int(4 * scale)))


def draw_lines(draw, x, y, lines, max_width, color, start_size, gap=6):
    fonts = [fit(draw, line, max_width, start_size, 18, True) for line in lines]
    heights = [measure(draw, line, f)[1] for line, f in zip(lines, fonts)]
    total = sum(heights) + gap * (len(lines) - 1)
    yy = y - total / 2
    for line, f, h in zip(lines, fonts, heights):
        draw.text((x, yy), line, font=f, fill=color)
        yy += h + gap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args()

    base = Image.open(args.base).convert("RGBA")
    w, h = base.size
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    navy = (12, 38, 78, 255)
    pink = (225, 96, 124, 255)
    soft_border = (204, 220, 242, 235)
    accents = [(47, 111, 214, 255), (245, 176, 0, 255), (226, 92, 117, 255)]

    # Right-side design system. Keep all graphics on clean empty area.
    right_x = int(w * 0.535)
    headline = (right_x, int(h * 0.070), int(w * 0.955), int(h * 0.255))
    cards = [
        ((right_x + 34, int(h * 0.325), int(w * 0.955), int(h * 0.445)), ["Capacitate", "mare"], accents[0]),
        ((right_x + 34, int(h * 0.505), int(w * 0.955), int(h * 0.625)), ["Buzunare", "organizate"], accents[1]),
        ((right_x + 34, int(h * 0.685), int(w * 0.955), int(h * 0.805)), ["Pentru zi", "de zi"], accents[2]),
    ]

    manifest = {
        "method": "clean_base_plus_complete_romanian_overlay",
        "language": "ro-RO",
        "base_image": args.base,
        "output": args.out,
        "layers": [],
    }

    # Decorative rhythm similar to Codex direct text: color blocks, not just text.
    shadow(layer, headline, radius=30, blur=14, opacity=30)
    rr(d, headline, 30, (255, 255, 255, 244), (242, 190, 202, 230), 3)
    f_top = fit(d, "Rucsac zilnic", headline[2] - headline[0] - 64, 54, 34)
    f_bottom = fit(d, "moale", headline[2] - headline[0] - 64, 66, 42)
    d.text((headline[0] + 36, headline[1] + 34), "Rucsac zilnic", font=f_top, fill=navy)
    d.text((headline[0] + 36, headline[1] + 104), "moale", font=f_bottom, fill=pink)
    d.rounded_rectangle((headline[0] + 36, headline[3] - 18, headline[0] + 184, headline[3] - 10), radius=4, fill=(225, 96, 124, 215))
    manifest["layers"].append({"id": "headline", "type": "editable_text_group", "bbox": list(headline), "texts": ["Rucsac zilnic", "moale"]})

    for idx, (box, lines, accent) in enumerate(cards, start=1):
        shadow(layer, box, radius=25, blur=12, opacity=28)
        rr(d, box, 26, (255, 255, 255, 238), soft_border, 3)
        # Accent rail.
        d.rounded_rectangle((box[0], box[1], box[0] + 9, box[3]), radius=5, fill=accent)
        cx, cy = box[0] + 64, (box[1] + box[3]) // 2
        d.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), fill=accent)
        draw_bag_icon(d, cx, cy, scale=0.78)
        draw_lines(d, box[0] + 124, cy, lines, box[2] - box[0] - 154, (25, 37, 55, 255), 34, gap=4)
        manifest["layers"].append({
            "id": f"feature_card_{idx}",
            "type": "editable_text_badge",
            "bbox": list(box),
            "editable_text": " ".join(lines),
            "accent_rgba": list(accent),
        })

    # Small trust/footer chips to use the lower right space without text clutter.
    chip_y = int(h * 0.885)
    chip_w = 112
    for i, accent in enumerate(accents):
        x = right_x + 38 + i * (chip_w + 22)
        box = (x, chip_y, x + chip_w, chip_y + 52)
        rr(d, box, 18, (255, 255, 255, 218), (220, 230, 245, 220), 2)
        d.ellipse((x + 16, chip_y + 13, x + 42, chip_y + 39), fill=accent)

    out = Image.alpha_composite(base, layer).convert("RGB")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.save(args.out, quality=95)
    Path(args.manifest).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
