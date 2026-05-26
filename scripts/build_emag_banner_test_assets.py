#!/usr/bin/env python3
"""Build eMAG banner validation assets from captured references."""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/cc/Desktop/photo_show")
OFFICIAL_DIR = ROOT / "references/emag_official_assets/20260524_homepage_banners"
OFFICIAL_IMAGES = OFFICIAL_DIR / "images"
QOLTEC_BANNER = ROOT / "references/user_cases/20260524_emag_qoltec_d978tdybm/images/01_1280x366.jpg"
OUT_DIR = ROOT / "output/emag_banner_generation_tests"
GEN_ROOT = Path("/Users/cc/.codex/generated_images")


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    if not bold:
        paths = paths[1:] + paths[:1]
    for path in paths:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


FONTS = {
    "b72": font(72, True),
    "b64": font(64, True),
    "b48": font(48, True),
    "b38": font(38, True),
    "b34": font(34, True),
    "b30": font(30, True),
    "b26": font(26, True),
    "r26": font(26),
    "r24": font(24),
    "r22": font(22),
    "r20": font(20),
    "r18": font(18),
}


def gradient(size: tuple[int, int], left: tuple[int, int, int], right: tuple[int, int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size)
    pixels = image.load()
    for x in range(width):
        t = x / max(1, width - 1)
        color = tuple(int(left[i] * (1 - t) + right[i] * t) for i in range(3))
        for y in range(height):
            pixels[x, y] = color
    return image


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def fit_paste(base: Image.Image, src: Image.Image, box: tuple[int, int, int, int], radius: int = 0) -> Image.Image:
    x1, y1, x2, y2 = box
    source = src.convert("RGB")
    source.thumbnail((x2 - x1, y2 - y1), Image.LANCZOS)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    px = x1 + (x2 - x1 - source.width) // 2
    py = y1 + (y2 - y1 - source.height) // 2
    if radius:
        mask = Image.new("L", source.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, source.width, source.height), radius=radius, fill=255)
        layer.paste(source.convert("RGBA"), (px, py), mask)
    else:
        layer.paste(source.convert("RGBA"), (px, py))
    return Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")


def contact_sheet() -> Path:
    paths = sorted(OFFICIAL_IMAGES.glob("*"))
    thumbs = []
    for path in paths:
        image = Image.open(path).convert("RGB")
        image.thumbnail((210, 240), Image.LANCZOS)
        tile = Image.new("RGB", (230, 285), "white")
        tile.paste(image, ((230 - image.width) // 2, 10))
        ImageDraw.Draw(tile).text((10, 255), path.name, fill=(20, 20, 20), font=FONTS["r18"])
        thumbs.append(tile)
    cols = 5
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * 230, rows * 285 + 70), (245, 245, 245))
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 20), "eMAG official homepage asset references - captured 2026-05-24", fill=(20, 20, 20), font=FONTS["b26"])
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((index % cols) * 230, 70 + (index // cols) * 285))
    path = OFFICIAL_DIR / "official_asset_contact_sheet.png"
    sheet.save(path)
    return path


def brand_trust_dark() -> list[Path]:
    image = gradient((1200, 480), (5, 6, 8), (38, 24, 45))
    draw = ImageDraw.Draw(image)
    for x in range(0, 600, 18):
        for y in range(20, 245, 18):
            if (x + y) // 18 % 3:
                draw.ellipse((x, y, x + 2, y + 2), fill=(95, 95, 110))
    draw.text((64, 70), "BESTPLAZA", fill=(255, 182, 42), font=FONTS["b64"])
    draw.text((68, 145), "WHERE THE BEST MEET", fill=(245, 245, 245), font=FONTS["b34"])
    draw.text((70, 204), "A detail-page trust banner: brand, support, buying context.", fill=(220, 220, 220), font=FONTS["r24"])

    services = [("FAST", "24-48h*"), ("EASY", "Returns*"), ("CLEAR", "Support")]
    for index, (title, subtitle) in enumerate(services):
        x = 70 + index * 205
        y = 330
        rounded(draw, (x, y, x + 165, y + 74), 16, (18, 18, 18), (255, 186, 38), 3)
        draw.text((x + 18, y + 10), title, fill=(255, 255, 255), font=FONTS["b26"])
        draw.text((x + 18, y + 42), subtitle, fill=(220, 220, 220), font=FONTS["r22"])

    cards = [OFFICIAL_IMAGES / "02_420x480.jpg", OFFICIAL_IMAGES / "07_420x480.jpg"]
    for path, box in zip(cards, [(790, 46, 1015, 305), (960, 90, 1170, 344)]):
        if path.exists():
            image = fit_paste(image, Image.open(path), box, radius=22)
    draw = ImageDraw.Draw(image)
    rounded(draw, (770, 358, 1148, 428), 18, (28, 28, 28), (255, 186, 38), 3)
    draw.text((794, 374), "Static image or GIF first frame", fill=(255, 255, 255), font=FONTS["b26"])
    draw.text((794, 404), "*Only when listing evidence supports it", fill=(215, 215, 215), font=FONTS["r18"])

    path = OUT_DIR / "01_brand_trust_dark_package_1200x480.png"
    rendered = OUT_DIR / "01_brand_trust_dark_package_rendered_1140x456.png"
    image.save(path)
    image.resize((1140, 456), Image.LANCZOS).save(rendered)
    return [path, rendered]


def ev_product_tech() -> list[Path]:
    image = gradient((1280, 366), (9, 10, 36), (46, 13, 80))
    draw = ImageDraw.Draw(image)
    for x in range(0, 1280, 52):
        draw.line((x, 0, x + 160, 366), fill=(48, 58, 118), width=1)
    for y in range(0, 366, 40):
        draw.line((0, y, 780, y + 60), fill=(34, 52, 100), width=1)
    if QOLTEC_BANNER.exists():
        crop = Image.open(QOLTEC_BANNER).convert("RGB").crop((280, 0, 930, 366))
        image = fit_paste(image, crop, (455, 22, 905, 346), radius=18)
    draw = ImageDraw.Draw(image)
    draw.text((54, 62), "Smart EV Charging", fill=(255, 255, 255), font=FONTS["b48"])
    for index, line in enumerate(["11kW daily control", "Wi-Fi + RFID access", "IP65 outdoor protection"]):
        y = 138 + index * 54
        rounded(draw, (58, y, 410, y + 40), 20, (12, 29, 58), (52, 226, 145), 2)
        draw.text((82, y + 7), line, fill=(235, 255, 247), font=FONTS["b22"] if "b22" in FONTS else FONTS["b26"])
    rounded(draw, (944, 68, 1214, 286), 24, (16, 20, 28), (87, 255, 143), 3)
    draw.text((974, 98), "For drivers who need", fill=(210, 230, 240), font=FONTS["r24"])
    draw.text((974, 137), "speed", fill=(255, 255, 255), font=FONTS["b38"])
    draw.text((974, 184), "control", fill=(255, 255, 255), font=FONTS["b38"])
    draw.text((974, 238), "and safety", fill=(255, 255, 255), font=FONTS["b30"])
    path = OUT_DIR / "02_ev_charger_product_tech_1280x366.png"
    rendered = OUT_DIR / "02_ev_charger_product_tech_rendered_1140x326.png"
    image.save(path)
    image.resize((1140, 326), Image.LANCZOS).save(rendered)
    return [path, rendered]


def official_people_category() -> list[Path]:
    image = gradient((1200, 480), (0, 137, 225), (51, 177, 244))
    draw = ImageDraw.Draw(image)
    for radius in range(80, 520, 58):
        draw.arc((650 - radius // 2, 70 - radius // 2, 650 + radius * 2, 70 + radius * 2), 20, 335, fill=(153, 219, 255), width=4)
    rounded(draw, (72, 66, 420, 130), 28, (111, 203, 255), (255, 255, 255), 2)
    draw.text((108, 80), "#MultiDeals style", fill=(255, 255, 255), font=FONTS["b34"])
    draw.text((78, 170), "Match product,", fill=(255, 255, 255), font=FONTS["b48"])
    draw.text((78, 222), "scene and category", fill=(255, 255, 255), font=FONTS["b48"])
    rounded(draw, (80, 318, 470, 374), 28, (246, 29, 39), (255, 255, 255), 0)
    draw.text((116, 328), "APP-first visual hook", fill=(255, 255, 255), font=FONTS["b30"])
    cards = [OFFICIAL_IMAGES / "01_420x480.jpg", OFFICIAL_IMAGES / "03_420x480.jpg", OFFICIAL_IMAGES / "04_420x480.jpg"]
    for index, path in enumerate(cards):
        if path.exists():
            x = 700 + index * 145
            y = 42 + index * 28
            image = fit_paste(image, Image.open(path), (x, y, x + 180, y + 248), radius=24)
    draw = ImageDraw.Draw(image)
    for index, label in enumerate(["People", "Product", "Category"]):
        x = 698 + index * 145
        rounded(draw, (x, 340, x + 137, 392), 18, (255, 255, 255), (255, 255, 255), 0)
        draw.text((x + 24, 354), label, fill=(0, 125, 210), font=FONTS["b26"])
    path = OUT_DIR / "03_official_people_category_style_1200x480.png"
    rendered = OUT_DIR / "03_official_people_category_style_rendered_1140x456.png"
    image.save(path)
    image.resize((1140, 456), Image.LANCZOS).save(rendered)
    return [path, rendered]


def latest_ai_image() -> Path | None:
    if not GEN_ROOT.exists():
        return None
    images = [path for path in GEN_ROOT.rglob("*") if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
    if not images:
        return None
    return max(images, key=lambda path: path.stat().st_mtime)


def ai_brand_trust_overlay() -> list[Path]:
    source = latest_ai_image()
    if source is None:
        return []
    raw = OUT_DIR / "04_ai_brand_trust_background_raw.png"
    shutil.copy2(source, raw)
    image = Image.open(raw).convert("RGB").resize((1200, 480), Image.LANCZOS)
    draw = ImageDraw.Draw(image)
    draw.text((70, 72), "BESTPLAZA", fill=(255, 186, 42), font=FONTS["b64"])
    draw.text((74, 148), "Premium everyday essentials", fill=(250, 250, 250), font=FONTS["b34"])
    draw.text((76, 205), "Brand familiarity, clear service cues, human warmth.", fill=(220, 220, 225), font=FONTS["r24"])
    for index, (title, subtitle) in enumerate([("FAST", "24-48h*"), ("EASY", "Returns*"), ("CLEAR", "Support")]):
        x = 76 + index * 220
        y = 352
        rounded(draw, (x, y, x + 176, y + 66), 16, (8, 8, 10), (255, 186, 42), 2)
        draw.text((x + 18, y + 10), title, fill=(255, 255, 255), font=FONTS["b26"])
        draw.text((x + 18, y + 39), subtitle, fill=(215, 215, 215), font=FONTS["r20"])
    final = OUT_DIR / "04_ai_brand_trust_background_overlay_1200x480.png"
    rendered = OUT_DIR / "04_ai_brand_trust_background_overlay_rendered_1140x456.png"
    image.save(final)
    image.resize((1140, 456), Image.LANCZOS).save(rendered)
    return [raw, final, rendered]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = [contact_sheet()]
    outputs += brand_trust_dark()
    outputs += ev_product_tech()
    outputs += official_people_category()
    outputs += ai_brand_trust_overlay()
    manifest = {
        "generated_at": "2026-05-24",
        "method": "Captured eMAG official assets + deterministic PIL layouts; optional AI background uses generated image then local text overlay.",
        "outputs": [str(path.relative_to(ROOT)) for path in outputs],
        "notes": [
            "Official eMAG assets are kept as reference material unless reuse rights are confirmed.",
            "Service claims marked with * require listing/platform evidence before production use.",
        ],
    }
    (OUT_DIR / "banner_generation_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
