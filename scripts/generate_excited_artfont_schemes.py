#!/usr/bin/env python3
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path("references/user_cases/20260521_emag_cangswjp/products")
FONT_DIR = Path("assets/fonts/google_fonts")
OUT = Path("experiments/20260522_excited_artfont_schemes")
CANVAS = 1200
BRAND = "EXCITED"


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def system_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


SMALL = system_font(22)
LABEL = system_font(30, True)


@dataclass
class Scheme:
    name: str
    source: str
    font_file: str
    logo_style: str
    shelf: tuple[int, int, int]
    accent: tuple[int, int, int]
    ink: tuple[int, int, int]
    fill_a: tuple[int, int, int]
    fill_b: tuple[int, int, int]
    logo_ratio: float
    border: str
    note: str


SCHEMES = [
    Scheme(
        "01_clean_teal_racing",
        "02_D5YN6S3BM_Aparat-de-gatit-cu-aburi-si-blender-pentru-bebelusi-Excitat-multifunctional-Alarma-LED-a/main_gallery/01_890ab6b4.jpg",
        "RacingSansOne-Regular.ttf",
        "clean",
        (0, 169, 164),
        (255, 144, 24),
        (7, 72, 78),
        (255, 255, 255),
        (230, 255, 252),
        0.39,
        "clean_teal",
        "clean home/baby: big but light logo, teal sleeve, orange feature dots",
    ),
    Scheme(
        "02_tool_orange_bungee",
        "13_D393L43BM_Set-de-4-balamale-pliabile-cu-40-suruburi-Excitat-otel-unghi-reglabil-090180-pentru-masa/main_gallery/01_778a22a1.jpg",
        "Bungee-Regular.ttf",
        "block",
        (242, 88, 37),
        (255, 211, 56),
        (48, 24, 15),
        (255, 255, 255),
        (255, 236, 196),
        0.44,
        "tool_orange",
        "hardware/tool: top bar logo can be wider, bottom black proof band stays heavy",
    ),
    Scheme(
        "03_auto_neon_racing",
        "34_D346JS3BM_Set-2-Becuri-LED-Auto-D1S-Excitat-110W-12.000-Lumeni-6500k-Becuri-Faruri-Conversie-HID-L/main_gallery/01_a24640b1.jpg",
        "RacingSansOne-Regular.ttf",
        "neon",
        (13, 17, 26),
        (30, 232, 230),
        (7, 9, 14),
        (255, 255, 255),
        (232, 255, 252),
        0.37,
        "auto_neon",
        "auto/LED: smaller top-right logo than game, stronger chromatic edge and dark shelf",
    ),
    Scheme(
        "04_kids_bubble_bungee",
        "32_DCNYHS3BM_Jucarii-Interactice-pentru-Baie-Excitat-RataLeuCrocodil-Multicolor-Cadou-Bebe-Timpul-Bai/main_gallery/01_e79efe60.jpg",
        "BungeeShade-Regular.ttf",
        "bubble",
        (255, 196, 214),
        (74, 207, 221),
        (43, 132, 143),
        (97, 219, 229),
        (210, 252, 255),
        0.34,
        "kids_soft",
        "kids/toy: bubble art font, soft shelf, small icon accents instead of aggressive spear",
    ),
    Scheme(
        "05_green_home_russo",
        "05_DZ9JSS3BM_Ventilator-de-evacuare-6-inch-Excitat-cu-7-palete-din-otel-inoxidabil-Carcasa-din-otel-M/main_gallery/01_f7d4dfe9.jpg",
        "RussoOne-Regular.ttf",
        "clean",
        (37, 151, 83),
        (158, 222, 111),
        (18, 55, 32),
        (255, 255, 255),
        (242, 255, 237),
        0.38,
        "green_leaf",
        "home/nature: stable readable logo, patterned green border, product remains dominant",
    ),
    Scheme(
        "06_game_magenta_racing",
        "01_DMJHW83BM_Consola-jocuri-tip-stick-Excitat-PRO-4K-2-jucatori-2-controlere-wireless-2.4G-128GB-31.9/main_gallery/01_643780ad.jpg",
        "RacingSansOne-Regular.ttf",
        "neon",
        (31, 19, 66),
        (255, 54, 152),
        (8, 6, 20),
        (255, 255, 255),
        (235, 252, 255),
        0.42,
        "game_neon",
        "gaming: biggest logo ratio, dark magenta shelf, stronger energy allowed",
    ),
]


def resize_square(img: Image.Image) -> Image.Image:
    src = img.convert("RGB")
    ratio = CANVAS / min(src.size)
    src = src.resize((round(src.width * ratio), round(src.height * ratio)), Image.Resampling.LANCZOS)
    left = max(0, (src.width - CANVAS) // 2)
    top = max(0, (src.height - CANVAS) // 2)
    return src.crop((left, top, left + CANVAS, top + CANVAS))


def gradient(size: tuple[int, int], a: tuple[int, int, int], b: tuple[int, int, int], horizontal: bool = True) -> Image.Image:
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    px = img.load()
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
    return img


def draw_logo(text: str, scheme: Scheme, target_w: int) -> Image.Image:
    # Render large, then scale. This keeps strokes cleaner after shear/stretch.
    face = font(scheme.font_file, 178 if scheme.logo_style != "bubble" else 162)
    scratch = Image.new("RGBA", (2400, 620), (0, 0, 0, 0))
    d = ImageDraw.Draw(scratch)
    bbox = d.textbbox((0, 0), text, font=face, stroke_width=12)
    x = 110 - bbox[0]
    y = 130 - bbox[1]

    if scheme.logo_style == "bubble":
        for ox, oy, alpha in [(12, 16, 95), (5, 8, 70)]:
            d.text((x + ox, y + oy), text, font=face, fill=(*scheme.ink, alpha), stroke_width=10, stroke_fill=(*scheme.ink, alpha))
        d.text((x, y), text, font=face, fill=scheme.fill_a, stroke_width=12, stroke_fill=(238, 255, 255))
        d.text((x, y), text, font=face, fill=scheme.fill_a, stroke_width=4, stroke_fill=scheme.ink)
        d.ellipse((x + 22, y - 34, x + 72, y + 18), fill=(168, 235, 230), outline=scheme.ink, width=3)
        d.ellipse((x + 92, y - 34, x + 142, y + 18), fill=(255, 166, 204), outline=(186, 78, 126), width=3)
        d.polygon([(x + 420, y - 40), (x + 442, y - 2), (x + 484, y + 2), (x + 454, y + 32), (x + 464, y + 76), (x + 420, y + 54), (x + 381, y + 76), (x + 392, y + 32), (x + 362, y + 2), (x + 404, y - 2)], fill=(255, 219, 38), outline=(172, 122, 11))
    elif scheme.logo_style == "clean":
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        cap = [
            (x + round(tw * 0.78), y + round(th * 0.18)),
            (x + round(tw * 1.04), y + round(th * 0.03)),
            (x + round(tw * 0.92), y + round(th * 0.31)),
        ]
        d.polygon([(px + 5, py + 6) for px, py in cap], fill=(0, 70, 72, 85))
        d.polygon(cap, fill=(255, 255, 255, 230))
        d.text((x + 9, y + 10), text, font=face, fill=(0, 82, 86, 130), stroke_width=5, stroke_fill=(0, 82, 86, 130))
        d.text((x, y), text, font=face, fill=(255, 255, 255), stroke_width=4, stroke_fill=(235, 255, 255))
        d.text((x, y), text, font=face, fill=(255, 255, 255), stroke_width=1, stroke_fill=(255, 255, 255))
    elif scheme.logo_style == "neon":
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        spear = [
            (x + round(tw * 0.13), y + round(th * 0.62)),
            (x + round(tw * 0.27), y + round(th * 0.61)),
            (x + round(tw * 0.04), y + round(th * 1.25)),
        ]
        cap = [
            (x + round(tw * 0.78), y + round(th * 0.17)),
            (x + round(tw * 1.09), y + round(th * 0.02)),
            (x + round(tw * 0.93), y + round(th * 0.32)),
        ]
        d.polygon([(px + 9, py + 10) for px, py in spear], fill=(0, 0, 0, 155))
        d.polygon(spear, fill=scheme.ink)
        d.polygon([(spear[0][0] + 8, spear[0][1] + 4), (spear[1][0] - 8, spear[1][1] + 2), (spear[2][0] + 18, spear[2][1] - 12)], fill=(255, 255, 255))
        d.polygon([(px + 8, py + 8) for px, py in cap], fill=(0, 0, 0, 130))
        d.polygon(cap, fill=(255, 255, 255))
        d.text((x + 18, y + 20), text, font=face, fill=(0, 0, 0, 160), stroke_width=9, stroke_fill=(0, 0, 0, 160))
        d.text((x - 7, y + 7), text, font=face, fill=(*scheme.accent, 210), stroke_width=6, stroke_fill=(*scheme.accent, 210))
        d.text((x + 5, y - 4), text, font=face, fill=(255, 64, 142, 180), stroke_width=5, stroke_fill=(255, 64, 142, 180))
        d.text((x, y), text, font=face, fill=(255, 255, 255), stroke_width=9, stroke_fill=scheme.ink)
        d.text((x, y), text, font=face, fill=(255, 255, 255), stroke_width=2, stroke_fill=(255, 255, 255))
    else:
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        # Extrusion and chromatic offsets.
        for ox, oy, col, sw in [
            (22, 24, (0, 0, 0, 135), 12),
            (12, 13, (84, 90, 92, 160), 9),
            (-8, 7, (*scheme.accent, 170), 7),
        ]:
            d.text((x + ox, y + oy), text, font=face, fill=col, stroke_width=sw, stroke_fill=col)

        # Speed spear and cap sit behind the readable letter faces. The
        # previous pass put them on top and damaged legibility.
        spear = [
            (x + round(tw * 0.13), y + round(th * 0.62)),
            (x + round(tw * 0.26), y + round(th * 0.61)),
            (x + round(tw * 0.04), y + round(th * 1.28)),
        ]
        d.polygon([(px + 8, py + 10) for px, py in spear], fill=(0, 0, 0, 125))
        d.polygon(spear, fill=scheme.ink)
        d.polygon([(spear[0][0] + 8, spear[0][1] + 4), (spear[1][0] - 8, spear[1][1] + 2), (spear[2][0] + 18, spear[2][1] - 12)], fill=scheme.fill_a)

        cap = [
            (x + round(tw * 0.78), y + round(th * 0.19)),
            (x + round(tw * 1.08), y + round(th * 0.02)),
            (x + round(tw * 0.93), y + round(th * 0.33)),
        ]
        d.polygon([(px + 8, py + 8) for px, py in cap], fill=(0, 0, 0, 90))
        d.polygon(cap, fill=scheme.fill_a)

        # Main stroke.
        d.text((x, y), text, font=face, fill=scheme.fill_a, stroke_width=12, stroke_fill=scheme.ink)

        # Subtle gradient face fill, clipped in the same coordinate system.
        mask = Image.new("L", scratch.size, 0)
        md = ImageDraw.Draw(mask)
        md.text((x, y), text, font=face, fill=255)
        face_layer = gradient(scratch.size, scheme.fill_a, scheme.fill_b)
        face_layer.putalpha(mask)
        scratch.alpha_composite(face_layer)

        # Thin white highlight to avoid the face becoming muddy after scaling.
        d.text((x, y), text, font=face, fill=(255, 255, 255, 20), stroke_width=1, stroke_fill=(255, 255, 255, 80))

    bbox = scratch.getbbox()
    logo = scratch.crop(bbox) if bbox else scratch
    if scheme.logo_style in {"angular", "neon", "botanical", "block", "clean"}:
        logo = logo.resize((round(logo.width * 1.12), round(logo.height * 0.88)), Image.Resampling.LANCZOS)
    if scheme.logo_style == "neon_speed":
        logo = logo.resize((round(logo.width * 1.2), round(logo.height * 0.9)), Image.Resampling.LANCZOS)
    shear = -0.08 if scheme.logo_style != "bubble" else 0.0
    extra = round(abs(shear) * logo.height)
    if extra:
        logo = logo.transform((logo.width + extra, logo.height), Image.Transform.AFFINE, (1, shear, extra, 0, 1, 0), resample=Image.Resampling.BICUBIC)
    ratio = target_w / logo.width
    return logo.resize((target_w, max(1, round(logo.height * ratio))), Image.Resampling.LANCZOS)


def draw_leaf_pattern(d: ImageDraw.ImageDraw, color: tuple[int, int, int]) -> None:
    for i in range(12):
        x = 30 + i * 96
        d.arc((x, 20, x + 72, 90), 200, 30, fill=(*color, 115), width=2)
        d.line((x + 33, 83, x + 63, 36), fill=(*color, 95), width=2)
        y = CANVAS - 150 + (i % 3) * 18
        d.arc((x, y, x + 82, y + 54), 185, 25, fill=(*color, 90), width=2)


def draw_base_frame(canvas: Image.Image, scheme: Scheme) -> None:
    layer = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    base = scheme.shelf
    accent = scheme.accent

    if scheme.border == "game_neon":
        d.rectangle((0, 0, CANVAS - 1, CANVAS - 1), outline=(14, 7, 34, 235), width=26)
        d.rectangle((20, 20, CANVAS - 21, CANVAS - 21), outline=(*accent, 175), width=4)
        for x in range(80, CANVAS, 210):
            d.line((x, CANVAS - 28, x + 120, CANVAS - 28), fill=(64, 225, 255, 150), width=5)
    elif scheme.border == "auto_neon":
        d.rectangle((0, 0, CANVAS - 1, CANVAS - 1), outline=(8, 12, 20, 235), width=22)
        d.line((28, CANVAS - 104, CANVAS - 28, CANVAS - 104), fill=(*accent, 170), width=4)
        d.line((44, 34, 360, 34), fill=(255, 54, 78, 155), width=4)
    elif scheme.border == "tool_orange":
        d.rectangle((0, 0, CANVAS - 1, CANVAS - 1), outline=(*base, 225), width=20)
        d.rectangle((20, 20, CANVAS - 21, CANVAS - 21), outline=(255, 255, 255, 180), width=3)
        d.line((0, CANVAS - 150, CANVAS, CANVAS - 150), fill=(12, 12, 12, 210), width=26)
    elif scheme.border == "kids_soft":
        d.rectangle((0, 0, CANVAS - 1, CANVAS - 1), outline=(255, 195, 214, 225), width=22)
        d.rectangle((23, 23, CANVAS - 24, CANVAS - 24), outline=(145, 215, 224, 165), width=3)
        for x in range(38, CANVAS, 112):
            d.rounded_rectangle((x, CANVAS - 98, x + 86, CANVAS - 24), radius=18, outline=(255, 255, 255, 175), width=3)
    else:
        d.rectangle((0, 0, CANVAS - 1, CANVAS - 1), outline=(*base, 215), width=24)
        d.rectangle((28, 28, CANVAS - 29, CANVAS - 29), outline=(255, 255, 255, 190), width=4)
        if scheme.border == "green_leaf":
            draw_leaf_pattern(d, (255, 255, 255))
        if scheme.border == "clean_teal":
            for x in range(20, CANVAS, 38):
                d.line((x, CANVAS - 78, x + 18, CANVAS - 42), fill=(255, 255, 255, 55), width=2)

    canvas.alpha_composite(layer)


def draw_logo_shelf(canvas: Image.Image, scheme: Scheme, logo: Image.Image) -> None:
    layer = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    shelf_w = max(round(CANVAS * 0.46), logo.width + 100)
    shelf_h = max(round(CANVAS * 0.115), logo.height + 34)
    x0 = CANVAS - shelf_w
    y0 = 18

    if scheme.border in {"tool_orange"}:
        x0 = 0
        shelf_w = CANVAS
        shelf_h = max(round(CANVAS * 0.125), logo.height + 40)
    if scheme.border in {"game_neon", "auto_neon"}:
        y0 = 12
        shelf_h += 16

    points = [
        (x0 + round(shelf_w * 0.16), y0),
        (CANVAS, y0),
        (CANVAS, y0 + round(shelf_h * 0.72)),
        (x0 + round(shelf_w * 0.06), y0 + shelf_h),
        (x0, y0 + round(shelf_h * 0.32)),
    ]
    if scheme.border == "tool_orange":
        points = [(0, 0), (CANVAS, 0), (CANVAS, shelf_h), (round(CANVAS * 0.58), shelf_h), (round(CANVAS * 0.54), shelf_h + 36), (0, shelf_h)]

    # Full-opacity cover for the original reference logo area. Otherwise the
    # old logo ghosts through and weakens the new art-word proposal.
    cover_h = y0 + shelf_h + 24
    if scheme.border == "tool_orange":
        d.rectangle((0, 0, CANVAS, cover_h), fill=(*scheme.shelf, 255))
    else:
        d.rectangle((max(0, x0 - 28), 0, CANVAS, cover_h), fill=(*scheme.shelf, 255))

    d.polygon([(x + 8, y + 10) for x, y in points], fill=(0, 0, 0, 85))
    d.polygon(points, fill=(*scheme.shelf, 255))
    d.polygon(
        [
            (points[0][0] + 4, y0 + round(shelf_h * 0.62)),
            (CANVAS, y0 + round(shelf_h * 0.48)),
            (CANVAS, y0 + round(shelf_h * 0.78)),
            (x0 + round(shelf_w * 0.08), y0 + shelf_h + 12),
        ],
        fill=(0, 0, 0, 105),
    )
    d.line(points + [points[0]], fill=(255, 255, 255, 170), width=3)

    fold = [
        (x0 + round(shelf_w * 0.03), y0 + round(shelf_h * 0.18)),
        (x0 + round(shelf_w * 0.35), y0 - 6),
        (x0 + round(shelf_w * 0.28), y0 + round(shelf_h * 0.78)),
        (x0 - 8, y0 + shelf_h),
    ]
    d.polygon(fold, fill=(*scheme.accent, 120))
    canvas.alpha_composite(layer)

    lx = CANVAS - logo.width - 28
    ly = y0 + max(8, round((shelf_h - logo.height) * 0.22))
    if scheme.border == "tool_orange":
        lx = CANVAS - logo.width - 52
        ly = max(8, round((shelf_h - logo.height) * 0.18))
    canvas.alpha_composite(logo, (lx, ly))


def polish_background(base: Image.Image, scheme: Scheme) -> Image.Image:
    img = base.convert("RGBA")
    if scheme.border in {"clean_teal", "green_leaf", "kids_soft"}:
        white = Image.new("RGBA", img.size, (255, 255, 255, 34))
        img = Image.alpha_composite(img, white)
    if scheme.border in {"game_neon", "auto_neon"}:
        img = ImageEnhance.Contrast(img.convert("RGB")).enhance(1.08).convert("RGBA")
    return img


def render_scheme(scheme: Scheme) -> Path:
    src = resize_square(Image.open(ROOT / scheme.source))
    canvas = polish_background(src, scheme)
    draw_base_frame(canvas, scheme)
    logo = draw_logo(BRAND, scheme, round(CANVAS * scheme.logo_ratio))
    draw_logo_shelf(canvas, scheme, logo)

    out = OUT / f"{scheme.name}.png"
    canvas.convert("RGB").save(out, quality=96)
    return out


def render_font_sheet() -> Path:
    ensure(OUT)
    fonts = [
        ("Racing Sans One", "RacingSansOne-Regular.ttf"),
        ("Bungee", "Bungee-Regular.ttf"),
        ("Bungee Shade", "BungeeShade-Regular.ttf"),
        ("Black Ops One", "BlackOpsOne-Regular.ttf"),
        ("Audiowide", "Audiowide-Regular.ttf"),
        ("Russo One", "RussoOne-Regular.ttf"),
        ("Faster One", "FasterOne-Regular.ttf"),
    ]
    width = 1400
    row_h = 176
    sheet = Image.new("RGB", (width, 72 + row_h * len(fonts)), "white")
    d = ImageDraw.Draw(sheet)
    d.text((32, 22), "EXCITED art-font candidates", font=LABEL, fill=(24, 30, 38))
    sample_scheme = SCHEMES[0]
    for i, (label, font_file) in enumerate(fonts):
        y = 72 + i * row_h
        d.text((32, y + 54), label, font=SMALL, fill=(55, 63, 72))
        s = Scheme(
            label.lower().replace(" ", "_"),
            SCHEMES[0].source,
            font_file,
            "bubble" if "Bungee Shade" in label else ("neon_speed" if "Faster" in label else "angular"),
            sample_scheme.shelf,
            sample_scheme.accent,
            sample_scheme.ink,
            sample_scheme.fill_a,
            sample_scheme.fill_b,
            0.4,
            "clean_teal",
            "",
        )
        logo = draw_logo(BRAND, s, 520)
        tile = Image.new("RGBA", (900, 150), (246, 250, 250, 255))
        td = ImageDraw.Draw(tile)
        td.rounded_rectangle((6, 12, 894, 138), radius=18, outline=(210, 224, 224), width=2)
        tile.alpha_composite(logo, (340, max(8, (150 - logo.height) // 2)))
        sheet.paste(tile.convert("RGB"), (420, y + 12))
    out = OUT / "artfont_logo_candidates.jpg"
    sheet.save(out, quality=94)
    return out


def render_scheme_sheet(paths: list[Path]) -> Path:
    cols = 3
    tile = 360
    label_h = 64
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * tile + 48, rows * (tile + label_h) + 84), "white")
    d = ImageDraw.Draw(sheet)
    d.text((24, 24), "EXCITED full-product frame schemes", font=LABEL, fill=(24, 30, 38))
    for i, path in enumerate(paths):
        x = 24 + (i % cols) * tile
        y = 84 + (i // cols) * (tile + label_h)
        img = Image.open(path).resize((330, 330), Image.Resampling.LANCZOS)
        sheet.paste(img, (x, y))
        name = path.stem.replace("_", " ")
        d.text((x, y + 338), name, font=SMALL, fill=(45, 52, 60))
    out = OUT / "scheme_contact_sheet.jpg"
    sheet.save(out, quality=94)
    return out


def main() -> None:
    ensure(OUT)
    font_sheet = render_font_sheet()
    scheme_paths = [render_scheme(s) for s in SCHEMES]
    scheme_sheet = render_scheme_sheet(scheme_paths)
    print({
        "brand": BRAND,
        "font_sheet": str(font_sheet),
        "scheme_sheet": str(scheme_sheet),
        "schemes": [str(p) for p in scheme_paths],
    })


if __name__ == "__main__":
    main()
