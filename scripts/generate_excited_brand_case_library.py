#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


FONT_DIR = Path("assets/fonts/google_fonts")
OUT = Path("experiments/20260522_excited_brand_case_library")
BRAND = "EXCITED"


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def system_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def case_font(file_name: str, size: int) -> ImageFont.FreeTypeFont:
    if file_name == "GeorgiaBold":
        return system_font(size, True)
    return ImageFont.truetype(str(FONT_DIR / file_name), size)


TITLE = system_font(34, True)
TEXT = system_font(20)
SMALL = system_font(16)


@dataclass(frozen=True)
class BrandCase:
    case_id: str
    title: str
    category: str
    font_file: str
    style: str
    bg: tuple[int, int, int]
    shelf: tuple[int, int, int]
    accent: tuple[int, int, int]
    ink: tuple[int, int, int]
    fill_a: tuple[int, int, int]
    fill_b: tuple[int, int, int]
    note: str


CASES = [
    BrandCase("01", "Racing White Cut", "default / clean", "RacingSansOne-Regular.ttf", "clean", (244, 252, 251), (0, 169, 164), (255, 164, 54), (4, 72, 78), (255, 255, 255), (241, 255, 253), "default clean shelf; use for home/baby/appliance"),
    BrandCase("02", "Racing Neon Cyan", "tech / auto", "RacingSansOne-Regular.ttf", "neon", (12, 18, 28), (15, 20, 30), (39, 233, 231), (5, 8, 14), (255, 255, 255), (226, 255, 255), "white face with cyan edge; strong but readable"),
    BrandCase("03", "Racing Magenta Game", "game / RGB", "RacingSansOne-Regular.ttf", "neon", (24, 12, 42), (34, 20, 70), (255, 52, 156), (8, 4, 18), (255, 255, 255), (242, 236, 255), "high-energy gaming shelf"),
    BrandCase("04", "Bungee Tool Block", "tool / hardware", "Bungee-Regular.ttf", "block", (255, 247, 240), (239, 92, 42), (255, 215, 60), (58, 25, 14), (255, 255, 255), (255, 228, 190), "thick retail block; works on orange top bars"),
    BrandCase("05", "Bungee Orange Badge", "warning / proof", "Bungee-Regular.ttf", "badge", (255, 251, 245), (248, 105, 32), (20, 20, 20), (68, 28, 15), (255, 250, 230), (255, 180, 86), "badge-like hard sell version"),
    BrandCase("06", "Russo Green Shelf", "green / home", "RussoOne-Regular.ttf", "clean", (246, 253, 246), (35, 150, 85), (170, 223, 120), (19, 64, 38), (255, 255, 255), (240, 255, 238), "calmer green home version"),
    BrandCase("07", "Orbitron Future", "electronics", "Orbitron-wght.ttf", "line", (242, 250, 255), (0, 121, 193), (70, 216, 255), (12, 44, 76), (255, 255, 255), (220, 247, 255), "thin futuristic; good for compatibility cards"),
    BrandCase("08", "Audiowide Sleek", "digital accessory", "Audiowide-Regular.ttf", "line", (244, 249, 252), (22, 98, 126), (99, 225, 238), (6, 43, 56), (255, 255, 255), (222, 250, 255), "sleek electronics alternative"),
    BrandCase("09", "Black Ops Industrial", "industrial / rugged", "BlackOpsOne-Regular.ttf", "industrial", (246, 246, 242), (45, 48, 50), (205, 181, 124), (20, 20, 20), (255, 255, 255), (210, 210, 205), "use sparingly; stencil feel"),
    BrandCase("10", "Bebas Tall Poster", "poster / large title", "BebasNeue-Regular.ttf", "poster", (255, 250, 244), (206, 68, 44), (255, 214, 94), (46, 24, 20), (255, 255, 255), (255, 237, 210), "tall title-bar option"),
    BrandCase("11", "Teko Speed Label", "sports / tools", "Teko-wght.ttf", "speed", (250, 251, 248), (32, 38, 44), (255, 119, 34), (10, 12, 14), (255, 255, 255), (255, 229, 198), "condensed speed mark"),
    BrandCase("12", "Anton Heavy Retail", "mass retail", "Anton-Regular.ttf", "block", (246, 250, 252), (20, 142, 160), (255, 178, 41), (8, 54, 62), (255, 255, 255), (232, 255, 255), "very readable at thumbnail size"),
    BrandCase("13", "Staatliches Label", "clean infographic", "Staatliches-Regular.ttf", "poster", (248, 251, 250), (18, 148, 117), (105, 220, 183), (12, 62, 50), (255, 255, 255), (237, 255, 249), "clean label for infographic pages"),
    BrandCase("14", "Rubik Mono Tech", "tech / toolkit", "RubikMonoOne-Regular.ttf", "block", (246, 250, 255), (38, 90, 184), (78, 218, 255), (13, 35, 88), (255, 255, 255), (230, 246, 255), "solid tech monoline"),
    BrandCase("15", "Rubik Glitch RGB", "gaming / glitch", "RubikGlitch-Regular.ttf", "glitch", (14, 9, 25), (33, 15, 62), (255, 40, 153), (5, 3, 12), (255, 255, 255), (224, 247, 255), "glitch accent; not default but useful for RGB"),
    BrandCase("16", "Faster Motion", "speed / gaming", "FasterOne-Regular.ttf", "motion", (24, 16, 45), (39, 28, 82), (64, 231, 255), (7, 5, 18), (255, 255, 255), (229, 249, 255), "motion-line option; must be kept large"),
    BrandCase("17", "Monoton Retro Arcade", "retro / game", "Monoton-Regular.ttf", "retro", (22, 18, 38), (52, 24, 84), (255, 197, 43), (8, 5, 16), (255, 232, 104), (255, 86, 167), "retro arcade, for nostalgic gaming"),
    BrandCase("18", "Bungee Shade Kids", "kids / toy", "BungeeShade-Regular.ttf", "bubble", (255, 248, 251), (255, 190, 214), (73, 209, 221), (45, 127, 142), (91, 217, 229), (218, 253, 255), "kids bubble outline"),
    BrandCase("19", "Knewave Sticker", "young / playful", "Knewave-Regular.ttf", "sticker", (255, 250, 242), (255, 156, 46), (255, 221, 76), (58, 28, 12), (255, 255, 255), (255, 238, 196), "handmade sticker energy"),
    BrandCase("20", "Fascinate Inline Gift", "gift / craft", "FascinateInline-Regular.ttf", "inline", (253, 247, 252), (40, 36, 42), (246, 150, 190), (20, 18, 22), (255, 255, 255), (255, 220, 238), "ornamental inline logo"),
    BrandCase("21", "Bowlby Premium Pop", "premium / bold", "BowlbyOneSC-Regular.ttf", "premium", (250, 248, 242), (42, 42, 38), (210, 181, 110), (18, 18, 16), (255, 246, 205), (188, 130, 42), "heavy premium retail"),
    BrandCase("22", "Georgia Gold Classic", "classic / luxury", "GeorgiaBold", "gold", (249, 247, 240), (34, 31, 27), (224, 185, 86), (30, 22, 12), (255, 239, 169), (166, 98, 20), "serif classic for gift/fashion variants"),
    BrandCase("23", "Chrome Auto", "auto / metal", "RacingSansOne-Regular.ttf", "chrome", (246, 248, 250), (18, 22, 30), (72, 226, 232), (4, 6, 9), (255, 255, 255), (180, 196, 206), "chrome-like automotive mark"),
    BrandCase("24", "Teal Compatibility", "compatibility / clean tech", "Orbitron-wght.ttf", "clean", (246, 253, 253), (0, 166, 171), (60, 222, 222), (8, 66, 72), (255, 255, 255), (235, 255, 255), "clean compatibility/product-fit logo"),
]


def gradient(size: tuple[int, int], a: tuple[int, int, int], b: tuple[int, int, int], horizontal: bool = True) -> Image.Image:
    w, h = size
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    px = out.load()
    span = max(1, (w - 1) if horizontal else (h - 1))
    for y in range(h):
        for x in range(w):
            t = (x if horizontal else y) / span
            px[x, y] = (
                round(a[0] * (1 - t) + b[0] * t),
                round(a[1] * (1 - t) + b[1] * t),
                round(a[2] * (1 - t) + b[2] * t),
                255,
            )
    return out


def paper_texture(size: tuple[int, int], color: tuple[int, int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGBA", size, (*color, 255))
    px = img.load()
    for y in range(h):
        for x in range(w):
            n = ((x * 13 + y * 29 + (x * y) % 17) % 15) - 7
            r, g, b, a = px[x, y]
            px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)), a)
    return img.filter(ImageFilter.GaussianBlur(0.22))


def draw_text_layer(text: str, face: ImageFont.ImageFont, fill: tuple[int, int, int], stroke: tuple[int, int, int], stroke_width: int) -> Image.Image:
    scratch = Image.new("RGBA", (1900, 500), (0, 0, 0, 0))
    d = ImageDraw.Draw(scratch)
    bbox = d.textbbox((0, 0), text, font=face, stroke_width=stroke_width)
    x = 82 - bbox[0]
    y = 92 - bbox[1]
    d.text((x, y), text, font=face, fill=fill, stroke_width=stroke_width, stroke_fill=stroke)
    return scratch


def render_logo(case: BrandCase, target_w: int) -> Image.Image:
    size = 168
    if case.style in {"poster", "speed"}:
        size = 196
    if case.style in {"bubble", "inline", "gold"}:
        size = 154
    if case.style == "retro":
        size = 132
    face = case_font(case.font_file, size)
    logo = Image.new("RGBA", (1900, 520), (0, 0, 0, 0))
    d = ImageDraw.Draw(logo)
    bbox = d.textbbox((0, 0), BRAND, font=face, stroke_width=10)
    x = 88 - bbox[0]
    y = 110 - bbox[1]
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    def text(pos: tuple[int, int], fill: tuple[int, int, int] | tuple[int, int, int, int], stroke_width: int = 0, stroke: tuple[int, int, int] | tuple[int, int, int, int] | None = None) -> None:
        d.text(pos, BRAND, font=face, fill=fill, stroke_width=stroke_width, stroke_fill=stroke or fill)

    if case.style in {"clean", "poster"}:
        cap = [(x + round(tw * 0.78), y + round(th * 0.18)), (x + round(tw * 1.04), y + round(th * 0.03)), (x + round(tw * 0.92), y + round(th * 0.31))]
        d.polygon([(px + 5, py + 6) for px, py in cap], fill=(*case.ink, 80))
        d.polygon(cap, fill=(255, 255, 255, 235))
        text((x + 10, y + 10), (*case.ink, 120), 4, (*case.ink, 120))
        text((x, y), case.fill_a, 4, (238, 255, 255))
    elif case.style in {"neon", "glitch", "chrome"}:
        spear = [(x + round(tw * 0.14), y + round(th * 0.62)), (x + round(tw * 0.28), y + round(th * 0.6)), (x + round(tw * 0.04), y + round(th * 1.24))]
        d.polygon([(px + 8, py + 10) for px, py in spear], fill=(0, 0, 0, 150))
        d.polygon(spear, fill=case.ink)
        d.polygon([(spear[0][0] + 8, spear[0][1] + 4), (spear[1][0] - 8, spear[1][1] + 2), (spear[2][0] + 18, spear[2][1] - 12)], fill=case.fill_a)
        text((x + 18, y + 22), (0, 0, 0, 165), 10, (0, 0, 0, 165))
        text((x - 8, y + 7), (*case.accent, 210), 7, (*case.accent, 210))
        if case.style == "glitch":
            text((x + 6, y - 5), (255, 46, 151, 170), 5, (255, 46, 151, 170))
            for offset in range(0, 90, 26):
                d.rectangle((x + offset, y + offset // 2, x + offset + 88, y + offset // 2 + 9), fill=(*case.accent, 120))
        if case.style == "chrome":
            text((x, y), (235, 244, 248), 9, case.ink)
            mask = Image.new("L", logo.size, 0)
            md = ImageDraw.Draw(mask)
            md.text((x, y), BRAND, font=face, fill=255)
            chrome = gradient(logo.size, (255, 255, 255), (122, 145, 158), horizontal=False)
            chrome.putalpha(mask)
            logo.alpha_composite(chrome)
        else:
            text((x, y), case.fill_a, 9, case.ink)
    elif case.style in {"block", "badge", "industrial", "premium"}:
        text((x + 18, y + 20), (0, 0, 0, 130), 10, (0, 0, 0, 130))
        text((x + 8, y + 9), (92, 90, 84, 150), 7, (92, 90, 84, 150))
        text((x, y), case.fill_a, 9, case.ink)
        mask = Image.new("L", logo.size, 0)
        md = ImageDraw.Draw(mask)
        md.text((x, y), BRAND, font=face, fill=255)
        fill = gradient(logo.size, case.fill_a, case.fill_b, horizontal=False)
        fill.putalpha(mask)
        logo.alpha_composite(fill)
    elif case.style == "gold":
        text((x + 12, y + 14), (60, 35, 12, 120), 8, (60, 35, 12, 120))
        text((x, y), case.fill_a, 6, case.ink)
        mask = Image.new("L", logo.size, 0)
        md = ImageDraw.Draw(mask)
        md.text((x, y), BRAND, font=face, fill=255)
        gold = gradient(logo.size, (255, 246, 180), (156, 82, 14), horizontal=False)
        gold.putalpha(mask)
        logo.alpha_composite(gold)
        d.line((x + 8, y + th + 18, x + tw - 8, y + th + 18), fill=(*case.accent, 190), width=4)
    elif case.style in {"bubble", "sticker"}:
        text((x + 11, y + 14), (*case.ink, 100), 10, (*case.ink, 100))
        text((x, y), case.fill_a, 12, (245, 255, 255))
        text((x, y), case.fill_a, 4, case.ink)
        d.ellipse((x + 24, y - 36, x + 75, y + 14), fill=case.accent, outline=case.ink, width=3)
        d.ellipse((x + 96, y - 32, x + 144, y + 16), fill=(255, 166, 204), outline=(176, 72, 119), width=3)
    elif case.style == "retro":
        text((x + 8, y + 10), (0, 0, 0, 150), 5, (0, 0, 0, 150))
        text((x - 4, y + 4), case.accent, 4, case.accent)
        text((x, y), case.fill_a, 3, case.ink)
    elif case.style == "inline":
        text((x + 10, y + 11), (0, 0, 0, 120), 8, (0, 0, 0, 120))
        text((x, y), case.fill_a, 7, case.ink)
        d.arc((x + 34, y + th + 5, x + tw - 34, y + th + 68), 190, 350, fill=case.accent, width=4)
    elif case.style in {"line", "motion", "speed"}:
        text((x + 16, y + 18), (0, 0, 0, 135), 7, (0, 0, 0, 135))
        text((x - 7, y + 6), (*case.accent, 170), 5, (*case.accent, 170))
        text((x, y), case.fill_a, 7, case.ink)
        for i in range(5):
            yy = y + round(th * (0.18 + i * 0.13))
            d.line((x - 72, yy, x + round(tw * 0.18), yy), fill=(*case.accent, 140), width=4)
    else:
        text((x + 14, y + 16), (0, 0, 0, 120), 8, (0, 0, 0, 120))
        text((x, y), case.fill_a, 8, case.ink)

    crop = logo.crop(logo.getbbox()) if logo.getbbox() else logo
    if case.style not in {"bubble", "gold", "retro", "inline"}:
        crop = crop.resize((round(crop.width * 1.10), round(crop.height * 0.90)), Image.Resampling.LANCZOS)
    shear = 0 if case.style in {"bubble", "gold", "retro", "inline"} else -0.07
    if shear:
        extra = round(abs(shear) * crop.height)
        crop = crop.transform((crop.width + extra, crop.height), Image.Transform.AFFINE, (1, shear, extra, 0, 1, 0), resample=Image.Resampling.BICUBIC)
    ratio = target_w / crop.width
    return crop.resize((target_w, max(1, round(crop.height * ratio))), Image.Resampling.LANCZOS)


def draw_case(case: BrandCase) -> Path:
    ensure(OUT / "cases")
    card_w, card_h = 1200, 1200
    card = paper_texture((card_w, card_h), case.bg)
    d = ImageDraw.Draw(card)

    # Main-image proportions: reference borders are slim sleeves around a
    # product-dominant square canvas, not thick presentation cards.
    outer_w = 22
    inner = 42
    d.rectangle((0, 0, card_w - 1, card_h - 1), outline=(*case.shelf, 215), width=outer_w)
    d.rectangle((inner, inner, card_w - inner - 1, card_h - inner - 1), fill=(255, 255, 255, 210), outline=(255, 255, 255, 190), width=3)

    # Ghosted product-safe area so border scale is judged against a full main
    # image, not against an empty logo swatch.
    safe = (112, 230, 820, 910)
    d.rounded_rectangle(safe, radius=22, fill=(255, 255, 255, 130), outline=(*case.shelf, 55), width=3)
    d.rounded_rectangle((190, 380, 720, 720), radius=28, fill=(*case.shelf, 22), outline=(*case.shelf, 65), width=3)
    for i, alpha in enumerate([130, 88, 54]):
        y_line = 790 + i * 38
        d.line((210, y_line, 680 - i * 80, y_line), fill=(*case.ink, alpha), width=5 - i)

    shelf_h = 132
    shelf_w = 548
    if case.style in {"neon", "glitch", "chrome"}:
        shelf_w = 590
        shelf_h = 146
    if case.style in {"block", "badge", "poster", "premium"}:
        shelf_w = 610
        shelf_h = 140
    if case.style in {"bubble", "gold", "inline", "retro"}:
        shelf_w = 540
        shelf_h = 138
    x0 = card_w - shelf_w - 18
    y0 = 22
    shelf = [
        (x0 + round(shelf_w * 0.16), y0),
        (card_w - 18, y0),
        (card_w - 18, y0 + round(shelf_h * 0.72)),
        (x0 + round(shelf_w * 0.08), y0 + shelf_h),
        (x0, y0 + round(shelf_h * 0.36)),
    ]
    d.polygon([(x + 8, y + 12) for x, y in shelf], fill=(0, 0, 0, 70))
    d.polygon(shelf, fill=(*case.shelf, 245))
    d.polygon(
        [
            (x0 + round(shelf_w * 0.06), y0 + round(shelf_h * 0.2)),
            (x0 + round(shelf_w * 0.38), y0 - 8),
            (x0 + round(shelf_w * 0.32), y0 + round(shelf_h * 0.78)),
            (x0 - 12, y0 + shelf_h),
        ],
        fill=(*case.accent, 135),
    )
    d.polygon(
        [
            (x0 + round(shelf_w * 0.2), y0 + round(shelf_h * 0.68)),
            (card_w - 18, y0 + round(shelf_h * 0.52)),
            (card_w - 18, y0 + round(shelf_h * 0.82)),
            (x0 + round(shelf_w * 0.1), y0 + shelf_h + 8),
        ],
        fill=(0, 0, 0, 92),
    )
    d.line(shelf + [shelf[0]], fill=(255, 255, 255, 150), width=3)

    logo_w = round(card_w * 0.36)
    if case.style in {"neon", "glitch", "chrome"}:
        logo_w = round(card_w * 0.40)
    if case.style in {"block", "badge", "poster", "premium"}:
        logo_w = round(card_w * 0.38)
    if case.style in {"bubble", "gold", "inline", "retro"}:
        logo_w = round(card_w * 0.35)
    logo = render_logo(case, logo_w)
    card.alpha_composite(logo, (card_w - logo.width - 36, y0 + max(7, (shelf_h - logo.height) // 3)))

    # Proportional bottom or side details. These are intentionally lighter than
    # the top brand shelf, matching the reference hierarchy.
    if case.style in {"block", "badge", "premium"}:
        band_h = 108
        d.rectangle((inner, card_h - inner - band_h, card_w - inner, card_h - inner), fill=(*case.shelf, 225))
        d.rectangle((inner + 230, card_h - inner - band_h, card_w - inner, card_h - inner), fill=(0, 0, 0, 205))
        d.text((inner + 28, card_h - inner - 80), "FEATURE", font=TEXT, fill=(255, 255, 255))
        d.text((inner + 270, card_h - inner - 80), case.category.upper(), font=TEXT, fill=(255, 255, 255))
    else:
        d.rounded_rectangle((72, card_h - 184, 324, card_h - 72), radius=16, outline=(*case.shelf, 135), width=4)
        d.line((98, card_h - 145, 245, card_h - 145), fill=(*case.accent, 145), width=5)
        d.line((98, card_h - 112, 285, card_h - 112), fill=(*case.ink, 75), width=4)

    d.text((72, card_h - 46), f"{case.case_id}. {case.title}", font=SMALL, fill=(44, 52, 58))

    out = OUT / "cases" / f"{case.case_id}_{case.title.lower().replace(' ', '_').replace('/', '-')}.png"
    card.convert("RGB").save(out, quality=96)
    return out


def render_sheet(paths: list[Path]) -> Path:
    cols = 3
    thumb_w, thumb_h = 360, 360
    pad = 28
    label_h = 58
    rows = math.ceil(len(paths) / cols)
    width = cols * thumb_w + (cols + 1) * pad
    height = 92 + rows * (thumb_h + label_h + pad)
    sheet = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(sheet)
    d.text((pad, 24), "EXCITED / EXITE Art-Word Brand Case Library", font=TITLE, fill=(24, 30, 38))
    for i, path in enumerate(paths):
        x = pad + (i % cols) * (thumb_w + pad)
        y = 92 + (i // cols) * (thumb_h + label_h + pad)
        img = Image.open(path).resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(img, (x, y))
        case = CASES[i]
        d.text((x, y + thumb_h + 8), f"{case.case_id}. {case.title}", font=SMALL, fill=(40, 47, 54))
        d.text((x, y + thumb_h + 30), case.category, font=SMALL, fill=(86, 94, 102))
    out = OUT / "brand_case_library_sheet.jpg"
    sheet.save(out, quality=94)
    return out


def write_index(paths: list[Path], sheet: Path) -> None:
    rows = []
    for case, path in zip(CASES, paths):
        rows.append({
            "case_id": case.case_id,
            "title": case.title,
            "category": case.category,
            "font_file": case.font_file,
            "style": case.style,
            "path": str(path),
            "note": case.note,
        })
    with (OUT / "brand_case_index.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    (OUT / "brand_case_index.json").write_text(json.dumps({"brand": BRAND, "sheet": str(sheet), "cases": rows}, indent=2))


def main() -> None:
    ensure(OUT)
    paths = [draw_case(case) for case in CASES]
    sheet = render_sheet(paths)
    write_index(paths, sheet)
    print(json.dumps({"brand": BRAND, "case_count": len(paths), "sheet": str(sheet), "out": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
