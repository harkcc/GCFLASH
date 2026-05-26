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


def fit(draw, text, max_width, start, min_size=18, bold=True):
    size = start
    while size >= min_size:
        f = font(size, bold)
        bbox = draw.textbbox((0, 0), text, font=f)
        if bbox[2] - bbox[0] <= max_width:
            return f
        size -= 2
    return font(min_size, bold)


def draw_center(draw, box, text, f, fill):
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = box[0] + (box[2] - box[0] - tw) / 2
    y = box[1] + (box[3] - box[1] - th) / 2 - 2
    draw.text((x, y), text, font=f, fill=fill)


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
    blue = (59, 123, 216, 255)
    gold = (245, 176, 0, 255)
    rose = (235, 118, 139, 255)

    # Coordinates target the A direct-text composition.
    headline = (615, 86, 1212, 304)
    cards = [
        ((700, 335, 1215, 505), "Capacitate\nmare", blue),
        ((700, 565, 1215, 735), "Buzunare\norganizate", gold),
        ((700, 795, 1215, 965), "Pentru zi\nde zi", rose),
    ]

    # Repaint text panels with soft white cards, preserving the surrounding
    # image composition while removing baked English.
    rounded(d, headline, 24, (255, 255, 255, 244), (242, 190, 202, 220), 3)
    f1 = fit(d, "Rucsac zilnic", headline[2] - headline[0] - 70, 66, 36)
    f2 = fit(d, "moale", headline[2] - headline[0] - 70, 70, 42)
    d.text((headline[0] + 42, headline[1] + 35), "Rucsac zilnic", font=f1, fill=navy)
    d.text((headline[0] + 42, headline[1] + 112), "moale", font=f2, fill=pink)

    manifest = {
        "method": "direct_image_text_replacement",
        "base_image": args.base,
        "output": args.out,
        "language": "ro-RO",
        "layers": [
            {"id": "headline", "type": "covered_text_replacement", "bbox": list(headline), "editable_text": "Rucsac zilnic moale"}
        ],
        "note": "English text is covered with matched panels and replaced with Romanian overlay text.",
    }

    for idx, (box, text, accent) in enumerate(cards, 1):
        rounded(d, box, 22, (255, 255, 255, 246), (205, 221, 244, 235), 3)
        cx, cy = box[0] + 58, (box[1] + box[3]) // 2
        d.ellipse((cx - 32, cy - 32, cx + 32, cy + 32), fill=accent)
        d.rounded_rectangle((cx - 13, cy - 10, cx + 13, cy + 15), radius=4, outline=(255, 255, 255, 255), width=4)
        d.arc((cx - 13, cy - 24, cx + 13, cy + 6), 200, 340, fill=(255, 255, 255, 255), width=4)
        lines = text.split("\n")
        f = fit(d, max(lines, key=len), box[2] - box[0] - 150, 37, 22)
        line_heights = [d.textbbox((0, 0), line, font=f)[3] - d.textbbox((0, 0), line, font=f)[1] for line in lines]
        total = sum(line_heights) + 7 * (len(lines) - 1)
        y = box[1] + (box[3] - box[1] - total) / 2 - 2
        for line, lh in zip(lines, line_heights):
            d.text((box[0] + 120, y), line, font=f, fill=(27, 38, 55, 255))
            y += lh + 7
        manifest["layers"].append({"id": f"feature_{idx}", "type": "covered_text_replacement", "bbox": list(box), "editable_text": text.replace("\n", " ")})

    out = Image.alpha_composite(im, layer).convert("RGB")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.save(args.out, quality=95)
    Path(args.manifest).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
