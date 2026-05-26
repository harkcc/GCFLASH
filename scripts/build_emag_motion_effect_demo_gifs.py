#!/usr/bin/env python3
"""Build deterministic GIF demos for eMAG detail-page motion effects."""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path("/Users/cc/Desktop/photo_show")
SRC = ROOT / "output/emag_html_detail_agent_v1_3_mobile_reference/assets"
OUT = ROOT / "output/emag_motion_effect_demos"


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    local_dir = ROOT / "assets" / "fonts"
    paths = [
        str(local_dir / ("Arial Bold.ttf" if bold else "Arial.ttf")),
        str(local_dir / "Helvetica.ttc"),
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


FONTS = {
    "b26": font(26, True),
    "b22": font(22, True),
    "r18": font(18),
}


def load_base(name: str = "brand") -> Image.Image:
    if name == "ev":
        path = SRC / "ev_tech_hero_1140x326.png"
        target = (1140, 456)
        image = Image.open(path).convert("RGB")
        canvas = Image.new("RGB", target, (8, 10, 18))
        canvas.paste(image.resize((1140, 326), Image.LANCZOS), (0, 65))
        return canvas
    path = SRC / "brand_trust_dark_1140x456.png"
    return Image.open(path).convert("RGB").resize((1140, 456), Image.LANCZOS)


def label(image: Image.Image, text: str) -> Image.Image:
    frame = image.convert("RGBA")
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((18, 18, 390, 58), radius=8, fill=(0, 0, 0, 168))
    draw.text((34, 27), text, fill=(255, 255, 255), font=FONTS["b22"])
    return Image.alpha_composite(frame, overlay).convert("RGB")


def save_gif(frames: list[Image.Image], path: Path, duration: int = 80) -> None:
    prepared = [frame.convert("P", palette=Image.Palette.ADAPTIVE) for frame in frames]
    prepared[0].save(path, save_all=True, append_images=prepared[1:], duration=duration, loop=0, optimize=False)


def shine_sweep() -> Path:
    base = label(load_base("brand"), "01 Shine sweep")
    frames = []
    for i in range(16):
        frame = base.convert("RGBA")
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        x = -260 + i * 105
        draw.polygon([(x, 0), (x + 90, 0), (x + 330, 456), (x + 240, 456)], fill=(255, 255, 255, 34))
        frames.append(Image.alpha_composite(frame, overlay).convert("RGB"))
    path = OUT / "01_shine_sweep.gif"
    save_gif(frames, path)
    return path


def icon_sequential_glow() -> Path:
    base = label(load_base("brand"), "02 Icon sequential glow")
    boxes = [(78, 312, 210, 377), (270, 312, 405, 377), (462, 312, 598, 377)]
    frames = []
    for i in range(18):
        frame = base.convert("RGBA")
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        active = (i // 6) % 3
        for idx, box in enumerate(boxes):
            if idx == active:
                glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
                gd = ImageDraw.Draw(glow)
                gd.rounded_rectangle((box[0] - 10, box[1] - 10, box[2] + 10, box[3] + 10), radius=18, fill=(255, 200, 40, 92))
                overlay = Image.alpha_composite(overlay, glow.filter(ImageFilter.GaussianBlur(8)))
                draw = ImageDraw.Draw(overlay)
                draw.rounded_rectangle(box, radius=12, outline=(255, 220, 88, 255), width=4)
        frames.append(Image.alpha_composite(frame, overlay).convert("RGB"))
    path = OUT / "02_icon_sequential_glow.gif"
    save_gif(frames, path, 110)
    return path


def border_breathing() -> Path:
    base = label(load_base("brand"), "03 Border breathing")
    frames = []
    for i in range(20):
        t = (math.sin(i / 20 * math.tau) + 1) / 2
        color = (255, int(175 + 70 * t), 30, int(80 + 150 * t))
        frame = base.convert("RGBA")
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for w in range(3):
            draw.rectangle((10 + w, 10 + w, 1129 - w, 445 - w), outline=color, width=2)
        overlay = overlay.filter(ImageFilter.GaussianBlur(1.5))
        frames.append(Image.alpha_composite(frame, overlay).convert("RGB"))
    path = OUT / "03_border_breathing.gif"
    save_gif(frames, path, 90)
    return path


def product_edge_glow() -> Path:
    base = label(load_base("ev"), "04 Product edge glow")
    product_box = (520, 110, 810, 350)
    frames = []
    for i in range(18):
        t = (math.sin(i / 18 * math.tau) + 1) / 2
        frame = base.convert("RGBA")
        glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(glow)
        draw.rounded_rectangle(product_box, radius=30, outline=(80, 255, 160, int(90 + 130 * t)), width=8)
        glow = glow.filter(ImageFilter.GaussianBlur(10))
        frames.append(Image.alpha_composite(frame, glow).convert("RGB"))
    path = OUT / "04_product_edge_glow.gif"
    save_gif(frames, path, 90)
    return path


def background_light_streak() -> Path:
    base = label(load_base("ev"), "05 Background light streak")
    frames = []
    for i in range(16):
        frame = base.convert("RGBA")
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        y = 410 - i * 22
        for k in range(4):
            draw.line((0, y + k * 18, 1140, y - 190 + k * 18), fill=(80, 140, 255, 40), width=7)
        frames.append(Image.alpha_composite(frame, overlay).convert("RGB"))
    path = OUT / "05_background_light_streak.gif"
    save_gif(frames, path)
    return path


def dotted_twinkle() -> Path:
    base = label(load_base("brand"), "06 Dotted twinkle")
    points = [(30 + x * 18, 72 + y * 18) for x in range(22) for y in range(12) if (x + y) % 3 == 0]
    frames = []
    for i in range(18):
        frame = base.convert("RGBA")
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for idx, (x, y) in enumerate(points):
            if (idx + i) % 7 in {0, 1}:
                draw.ellipse((x, y, x + 4, y + 4), fill=(255, 190, 54, 130))
        frames.append(Image.alpha_composite(frame, overlay).convert("RGB"))
    path = OUT / "06_dotted_twinkle.gif"
    save_gif(frames, path, 100)
    return path


def step_highlight() -> Path:
    base = Image.new("RGB", (1140, 456), (248, 250, 252))
    draw = ImageDraw.Draw(base)
    draw.text((40, 30), "07 Step highlight", fill=(36, 41, 50), font=FONTS["b26"])
    boxes = [(60, 105, 1080, 180), (60, 205, 1080, 280), (60, 305, 1080, 380)]
    labels = [("01", "Pregateste produsul"), ("02", "Conecteaza corect"), ("03", "Verifica indicatorul")]
    for box, (num, title) in zip(boxes, labels):
        draw.rectangle(box, fill=(255, 255, 255), outline=(220, 225, 232), width=2)
        draw.text((95, box[1] + 20), num, fill=(14, 165, 233), font=FONTS["b26"])
        draw.text((180, box[1] + 20), title, fill=(36, 41, 50), font=FONTS["b26"])
    frames = []
    for i in range(18):
        frame = base.convert("RGBA")
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        active = (i // 6) % 3
        box = boxes[active]
        draw.rectangle(box, outline=(34, 197, 94, 255), width=7)
        draw.rectangle((box[0], box[1], box[0] + 10, box[3]), fill=(34, 197, 94, 255))
        frames.append(Image.alpha_composite(frame, overlay).convert("RGB"))
    path = OUT / "07_step_highlight.gif"
    save_gif(frames, path, 110)
    return path


def before_after_wipe() -> Path:
    left = Image.new("RGB", (1140, 456), (54, 59, 68))
    right = Image.new("RGB", (1140, 456), (232, 247, 238))
    dl = ImageDraw.Draw(left)
    dr = ImageDraw.Draw(right)
    dl.text((46, 34), "08 Before-after wipe", fill=(255, 255, 255), font=FONTS["b26"])
    dl.text((80, 190), "Before / problem scene", fill=(230, 230, 230), font=FONTS["b26"])
    dr.text((80, 190), "After / solution result", fill=(35, 60, 45), font=FONTS["b26"])
    frames = []
    for i in range(18):
        x = int(120 + i * (900 / 17))
        frame = left.copy()
        crop = right.crop((0, 0, x, 456))
        frame.paste(crop, (0, 0))
        draw = ImageDraw.Draw(frame)
        draw.line((x, 0, x, 456), fill=(255, 204, 48), width=8)
        frames.append(frame)
    path = OUT / "08_before_after_wipe.gif"
    save_gif(frames, path, 90)
    return path


def magnifier_pulse() -> Path:
    base = label(load_base("ev"), "09 Detail magnifier pulse")
    center = (760, 172)
    frames = []
    for i in range(18):
        t = (math.sin(i / 18 * math.tau) + 1) / 2
        radius = int(44 + 12 * t)
        frame = base.convert("RGBA")
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw.ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), outline=(255, 220, 80, 240), width=6)
        draw.line((center[0] + radius - 4, center[1] + radius - 4, center[0] + radius + 44, center[1] + radius + 44), fill=(255, 220, 80, 240), width=7)
        frames.append(Image.alpha_composite(frame, overlay).convert("RGB"))
    path = OUT / "09_magnifier_pulse.gif"
    save_gif(frames, path, 80)
    return path


def parcel_micro_motion() -> Path:
    base = label(load_base("brand"), "10 Parcel micro motion")
    frames = []
    box = (690, 238, 955, 370)
    for i in range(18):
        t = math.sin(i / 18 * math.tau)
        frame = base.convert("RGBA")
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        y = int(t * 4)
        draw.rounded_rectangle((box[0] - 8, box[1] + y - 8, box[2] + 8, box[3] + y + 8), radius=18, outline=(255, 198, 70, 180), width=5)
        draw.line((box[0] + 20, box[1] + 16 + y, box[2] - 20, box[1] + 16 + y), fill=(255, 255, 255, 88), width=5)
        frames.append(Image.alpha_composite(frame, overlay).convert("RGB"))
    path = OUT / "10_parcel_micro_motion.gif"
    save_gif(frames, path, 90)
    return path


def write_preview(paths: list[Path]) -> None:
    cards = []
    for path in paths:
        title = path.stem.replace("_", " ").title()
        cards.append(
            f'<section style="margin:22px 0;padding:14px;border:1px solid #e5e7eb;background:#fff;">'
            f'<h2 style="font-size:18px;margin:0 0 12px 0;">{title}</h2>'
            f'<img src="{path.name}" width="1140" style="max-width:100%;height:auto;display:block;">'
            f'</section>'
        )
    html = (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>eMAG Motion Effect Demos</title></head>'
        '<body style="margin:0;background:#f6f7f9;font-family:Arial,Helvetica,sans-serif;color:#24292f;">'
        '<main style="max-width:900px;margin:0 auto;padding:16px 10px 40px;">'
        '<h1 style="font-size:24px;margin:8px 0 12px;">eMAG Motion Effect Demos</h1>'
        '<p style="line-height:1.55;color:#4b5563;">Deterministic GIF effects for detail-page banners, proof boards, steps, and trust modules.</p>'
        + "".join(cards)
        + "</main></body></html>"
    )
    (OUT / "index.html").write_text(html, encoding="utf-8")


def write_manifest(paths: list[Path]) -> None:
    recipes = [
        ("motion_shine_sweep", "brand banner, tech hero, CTA", "subtle premium attention"),
        ("motion_icon_sequential_glow", "service cues, three anchors, proof chips", "guide reading order"),
        ("motion_border_breathing", "CTA, important notice, trust closer", "soft emphasis"),
        ("motion_product_edge_glow", "electronics, EV, tools", "product authority and tech feel"),
        ("motion_background_light_streak", "technical banner", "add energy without moving product"),
        ("motion_dotted_twinkle", "dark brand trust banner", "premium texture"),
        ("motion_step_highlight", "installation/use/cleaning steps", "show process order"),
        ("motion_before_after_wipe", "cleaning/repair/comparison with evidence", "show transition"),
        ("motion_magnifier_pulse", "ports/material/filter/buttons", "draw attention to detail"),
        ("motion_parcel_micro_motion", "brand trust/package proof", "warm trust signal"),
    ]
    manifest = {
        "output_dir": str(OUT),
        "rule": "Store these as motion recipes in the component library; generate per product with source assets and evidence gates.",
        "files": [
            {
                "effect_id": recipes[idx][0],
                "file": path.name,
                "best_for": recipes[idx][1],
                "purpose": recipes[idx][2],
                "html_form": '<p style="text-align:center;"><img src="..." width="1140"></p>',
            }
            for idx, path in enumerate(paths)
        ],
    }
    (OUT / "motion_effect_recipes.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = [
        shine_sweep(),
        icon_sequential_glow(),
        border_breathing(),
        product_edge_glow(),
        background_light_streak(),
        dotted_twinkle(),
        step_highlight(),
        before_after_wipe(),
        magnifier_pulse(),
        parcel_micro_motion(),
    ]
    write_preview(paths)
    write_manifest(paths)
    print(OUT)


if __name__ == "__main__":
    main()
