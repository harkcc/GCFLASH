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


def bbox(draw, text, f):
    b = draw.textbbox((0, 0), text, font=f)
    return b[2] - b[0], b[3] - b[1]


def fit(draw, text, max_width, start, min_size=18):
    size = start
    while size >= min_size:
        f = font(size, True)
        if bbox(draw, text, f)[0] <= max_width:
            return f
        size -= 2
    return font(min_size, True)


def rounded(draw, box, r, fill, outline=None, width=2):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args()

    im = Image.open(args.base).convert("RGBA")
    w, h = im.size
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    navy = (11, 36, 78, 255)
    pink = (226, 103, 126, 255)
    accents = [(47, 111, 214, 255), (245, 176, 0, 255), (226, 92, 117, 255)]
    headline = (int(w * 0.53), int(h * 0.075), int(w * 0.955), int(h * 0.245))
    cards = [
        ((int(w * 0.58), int(h * 0.305), int(w * 0.955), int(h * 0.425)), ["Capacitate", "mare"], accents[0]),
        ((int(w * 0.58), int(h * 0.475), int(w * 0.955), int(h * 0.595)), ["Buzunare", "organizate"], accents[1]),
        ((int(w * 0.58), int(h * 0.645), int(w * 0.955), int(h * 0.765)), ["Pentru zi", "de zi"], accents[2]),
    ]

    manifest = {
        "method": "romanian_hybrid_overlay",
        "language": "ro-RO",
        "base_image": args.base,
        "output": args.out,
        "layers": [],
    }

    # Paint over blank generated cards to create a consistent final template.
    rounded(d, headline, 24, (255, 255, 255, 242), (242, 190, 202, 230), 3)
    f1 = fit(d, "Rucsac zilnic", headline[2] - headline[0] - 64, 48, 30)
    f2 = fit(d, "moale", headline[2] - headline[0] - 64, 58, 34)
    d.text((headline[0] + 34, headline[1] + 34), "Rucsac zilnic", font=f1, fill=navy)
    d.text((headline[0] + 34, headline[1] + 102), "moale", font=f2, fill=pink)
    manifest["layers"].append({"id": "headline", "type": "editable_text_group", "bbox": list(headline), "texts": ["Rucsac zilnic", "moale"]})

    for idx, (box, lines, accent) in enumerate(cards, 1):
        rounded(d, box, 22, (255, 255, 255, 238), (205, 221, 244, 235), 3)
        cx, cy = box[0] + 54, (box[1] + box[3]) // 2
        d.ellipse((cx - 28, cy - 28, cx + 28, cy + 28), fill=accent)
        # Minimal bag icon.
        d.rounded_rectangle((cx - 13, cy - 9, cx + 13, cy + 16), radius=4, outline=(255, 255, 255, 255), width=4)
        d.arc((cx - 13, cy - 23, cx + 13, cy + 8), 200, 340, fill=(255, 255, 255, 255), width=4)
        max_line = max(lines, key=len)
        f = fit(d, max_line, box[2] - box[0] - 132, 30, 20)
        heights = [bbox(d, line, f)[1] for line in lines]
        total_h = sum(heights) + 4 * (len(lines) - 1)
        y = box[1] + (box[3] - box[1] - total_h) / 2 - 3
        for line, th in zip(lines, heights):
            d.text((box[0] + 108, y), line, font=f, fill=(26, 36, 52, 255))
            y += th + 4
        manifest["layers"].append({"id": f"feature_{idx}", "type": "editable_text_badge", "bbox": list(box), "editable_text": " ".join(lines), "accent_rgba": list(accent)})

    out = Image.alpha_composite(im, layer).convert("RGB")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.save(args.out, quality=95)
    Path(args.manifest).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
