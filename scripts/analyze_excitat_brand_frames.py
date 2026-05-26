#!/usr/bin/env python3
from __future__ import annotations

import colorsys
import csv
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat


ROOT = Path("references/user_cases/20260521_emag_cangswjp")
PRODUCTS = ROOT / "products"
OUT = Path("experiments/20260522_excitat_frame_study")
CANVAS = 1200


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_font(size: int, bold: bool = False, italic: bool = False) -> ImageFont.ImageFont:
    candidates = []
    if italic:
        candidates.extend([
            "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf",
            "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
        ])
    candidates.extend([
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ])
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def load_brand_art_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Black.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


FONTS = {
    "brand": load_font(150, True, True),
    "brand_mid": load_font(108, True, True),
    "brand_art": load_brand_art_font(154),
    "brand_small": load_font(28, True, True),
    "h2": load_font(38, True),
    "small": load_font(20),
    "tiny": load_font(15),
}


def resize_square(img: Image.Image, size: int) -> Image.Image:
    src = img.convert("RGB")
    ratio = size / max(src.size)
    new_size = (round(src.width * ratio), round(src.height * ratio))
    src = src.resize(new_size, Image.Resampling.LANCZOS)
    dst = Image.new("RGB", (size, size), "white")
    dst.paste(src, ((size - src.width) // 2, (size - src.height) // 2))
    return dst


def main_images() -> list[Path]:
    return sorted(PRODUCTS.glob("*/main_gallery/01_*"))


def product_id(path: Path) -> str:
    return path.parts[-3].split("_", 2)[1]


def crop_edges(img: Image.Image, band: int = 105) -> Image.Image:
    w, h = img.size
    top = img.crop((0, 0, w, band)).resize((300, 42), Image.Resampling.LANCZOS)
    right = img.crop((w - band, 0, w, h)).resize((42, 300), Image.Resampling.LANCZOS)
    bottom = img.crop((0, h - band, w, h)).resize((300, 42), Image.Resampling.LANCZOS)
    left = img.crop((0, 0, band, h)).resize((42, 300), Image.Resampling.LANCZOS)
    tile = Image.new("RGB", (386, 386), "white")
    tile.paste(top, (43, 0))
    tile.paste(right, (344, 43))
    tile.paste(bottom, (43, 344))
    tile.paste(left, (0, 43))
    center = img.resize((300, 300), Image.Resampling.LANCZOS)
    tile.paste(center, (43, 43))
    return tile


def crop_corners(img: Image.Image, corner: int = 230) -> Image.Image:
    w, h = img.size
    crops = [
        img.crop((0, 0, corner, corner)),
        img.crop((w - corner, 0, w, corner)),
        img.crop((0, h - corner, corner, h)),
        img.crop((w - corner, h - corner, w, h)),
    ]
    tile = Image.new("RGB", (corner * 2 + 8, corner * 2 + 8), "white")
    tile.paste(crops[0], (0, 0))
    tile.paste(crops[1], (corner + 8, 0))
    tile.paste(crops[2], (0, corner + 8))
    tile.paste(crops[3], (corner + 8, corner + 8))
    return tile


def dominant_edge_colors(img: Image.Image, band_ratio: float = 0.055) -> list[tuple[int, int, int]]:
    small = resize_square(img, 420)
    w, h = small.size
    band = max(18, int(w * band_ratio))
    masks = [
        small.crop((0, 0, w, band)),
        small.crop((0, h - band, w, h)),
        small.crop((0, 0, band, h)),
        small.crop((w - band, 0, w, h)),
    ]
    colors: list[tuple[int, int, int]] = []
    for crop in masks:
        q = crop.convert("P", palette=Image.Palette.ADAPTIVE, colors=10).convert("RGB")
        for (count, color) in q.getcolors(maxcolors=10_000) or []:
            r, g, b = color
            # Ignore pure white/near-white paper and near-black product shadows.
            if r > 238 and g > 238 and b > 238:
                continue
            if r < 18 and g < 18 and b < 18:
                continue
            sat = max(color) - min(color)
            if sat < 18 and sum(color) > 630:
                continue
            colors.extend([color] * max(1, count // 60))
    if not colors:
        return [(0, 160, 170)]
    counter = Counter(colors)
    top = [c for c, _ in counter.most_common(8)]
    return top[:5]


def color_name(rgb: tuple[int, int, int]) -> str:
    r, g, b = [v / 255 for v in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    deg = h * 360
    if s < 0.12:
        if v > 0.78:
            return "light-neutral"
        if v < 0.25:
            return "black-charcoal"
        return "grey-metal"
    if deg < 18 or deg >= 340:
        return "red"
    if deg < 45:
        return "orange"
    if deg < 72:
        return "yellow-gold"
    if deg < 155:
        return "green"
    if deg < 195:
        return "teal"
    if deg < 245:
        return "blue"
    if deg < 285:
        return "purple"
    if deg < 340:
        return "pink-magenta"
    return "accent"


@dataclass
class FrameSpec:
    name: str
    base: tuple[int, int, int]
    accent: tuple[int, int, int]
    ink: tuple[int, int, int]
    bg: tuple[int, int, int]
    pattern: str


def paper_texture(size: int, base: tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGBA", (size, size), (*base, 255))
    px = img.load()
    for y in range(size):
        for x in range(size):
            n = ((x * 17 + y * 31 + (x * y) % 19) % 17) - 8
            r, g, b, a = px[x, y]
            px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)), a)
    return img.filter(ImageFilter.GaussianBlur(0.25))


def render_art_wordmark(
    text: str,
    *,
    spec: FrameSpec,
    target_width: int,
    style: str = "angular",
) -> Image.Image:
    text = text.upper()
    scratch = Image.new("RGBA", (1400, 360), (0, 0, 0, 0))
    draw = ImageDraw.Draw(scratch)

    if style == "kids":
        font = load_font(170, True)
        fill = (96, 217, 225)
        stroke = (55, 150, 160)
        shadow = (25, 80, 90)
        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=9)
        tx = 72 - bbox[0]
        ty = 60 - bbox[1]
        for ox, oy, alpha in [(14, 18, 90), (7, 10, 70)]:
            draw.text((tx + ox, ty + oy), text, font=font, fill=(*shadow, alpha), stroke_width=10, stroke_fill=(*shadow, alpha))
        draw.text((tx, ty), text, font=font, fill=fill, stroke_width=10, stroke_fill=(225, 255, 255))
        draw.text((tx, ty), text, font=font, fill=fill, stroke_width=4, stroke_fill=stroke)
        draw.ellipse((tx - 5, ty - 18, tx + 42, ty + 30), fill=(172, 232, 231), outline=(77, 168, 175), width=3)
        draw.ellipse((tx + 58, ty - 18, tx + 105, ty + 30), fill=(255, 177, 202), outline=(188, 96, 130), width=3)
        draw.polygon([(tx + 360, ty - 22), (tx + 378, ty + 12), (tx + 414, ty + 17), (tx + 388, ty + 42), (tx + 397, ty + 78), (tx + 360, ty + 60), (tx + 326, ty + 78), (tx + 334, ty + 42), (tx + 310, ty + 17), (tx + 345, ty + 12)], fill=(255, 214, 43), outline=(190, 145, 20))
    elif style == "serif":
        font = load_font(156, True)
        fill = (94, 64, 23)
        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=2)
        tx = 80 - bbox[0]
        ty = 70 - bbox[1]
        draw.text((tx + 5, ty + 5), text, font=font, fill=(80, 60, 35, 55), stroke_width=2, stroke_fill=(80, 60, 35, 55))
        draw.text((tx, ty), text, font=font, fill=fill, stroke_width=1, stroke_fill=(232, 217, 185))
        y = ty + 172
        draw.arc((tx + 52, y - 34, tx + 420, y + 34), 178, 360, fill=fill, width=3)
        draw.line((tx + 42, y, tx + 430, y), fill=fill, width=2)
    else:
        font = FONTS["brand_art"]
        fill = (255, 255, 255)
        stroke = spec.ink
        accent = spec.accent
        if spec.name == "green_home":
            fill = (255, 219, 36)
            stroke = (12, 58, 105)
        if "tech" in spec.pattern or "black" in spec.pattern:
            accent = (41, 230, 230)
        if "tool" in spec.pattern:
            accent = (255, 219, 85)

        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=8)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = 88 - bbox[0]
        ty = 70 - bbox[1]

        # Extruded shadow and chromatic offset. Reference logos are stacked,
        # not flat text: black depth, grey side face, then a colored edge.
        for ox, oy, col, sw in [
            (18, 20, (0, 0, 0, 145), 9),
            (10, 12, (82, 87, 90, 155), 7),
            (-6, 7, (*accent, 175), 6),
        ]:
            draw.text((tx + ox, ty + oy), text, font=font, fill=col, stroke_width=sw, stroke_fill=col)
        draw.text((tx, ty), text, font=font, fill=fill, stroke_width=8, stroke_fill=stroke)
        draw.text((tx, ty), text, font=font, fill=fill, stroke_width=3, stroke_fill=(245, 245, 245))

        # Lightning spear under the E and a sharp right cap, both visible in
        # the reference mark family.
        spear_shadow = [
            (tx + round(tw * 0.16) + 8, ty + round(th * 0.58) + 10),
            (tx + round(tw * 0.27) + 8, ty + round(th * 0.6) + 10),
            (tx + round(tw * 0.04) + 8, ty + round(th * 1.16) + 10),
        ]
        spear = [(x - 10, y - 12) for x, y in spear_shadow]
        draw.polygon(spear_shadow, fill=(0, 0, 0, 140))
        draw.polygon(spear, fill=stroke)
        inner_spear = [
            (spear[0][0] + 8, spear[0][1] + 4),
            (spear[1][0] - 6, spear[1][1] + 2),
            (spear[2][0] + 19, spear[2][1] - 10),
        ]
        draw.polygon(inner_spear, fill=fill)
        right_cap = [
            (tx + round(tw * 0.82), ty + round(th * 0.2)),
            (tx + round(tw * 1.04), ty + round(th * 0.05)),
            (tx + round(tw * 0.94), ty + round(th * 0.31)),
        ]
        draw.polygon([(x + 7, y + 8) for x, y in right_cap], fill=(0, 0, 0, 95))
        draw.polygon(right_cap, fill=fill)

    bbox = scratch.getbbox()
    if not bbox:
        return scratch
    mark = scratch.crop(bbox)
    if style == "angular":
        mark = mark.resize((round(mark.width * 1.42), round(mark.height * 0.82)), Image.Resampling.LANCZOS)
    shear = -0.13
    extra = round(abs(shear) * mark.height)
    skewed = Image.new("RGBA", (mark.width + extra + 8, mark.height), (0, 0, 0, 0))
    skewed = mark.transform(
        skewed.size,
        Image.Transform.AFFINE,
        (1, shear, extra, 0, 1, 0),
        resample=Image.Resampling.BICUBIC,
    )
    ratio = target_width / skewed.width
    target_height = max(1, round(skewed.height * ratio))
    return skewed.resize((target_width, target_height), Image.Resampling.LANCZOS)


def draw_exite_frame(
    base: Image.Image,
    *,
    spec: FrameSpec,
    brand: str = "EXITE",
    product_box: tuple[int, int, int, int] | None = None,
) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    w, h = base.size
    edge = max(8, round(w * 0.008))
    inset = max(12, round(w * 0.014))

    # Thin, partial paper-like outer strokes. Reference cards usually feel like
    # a printed sleeve, not a thick futuristic frame.
    outer_w = max(14, round(w * 0.022))
    draw.rectangle((0, 0, w - 1, h - 1), outline=(*spec.base, 190), width=outer_w)
    draw.rectangle((outer_w + 8, outer_w + 8, w - outer_w - 9, h - outer_w - 9), outline=(255, 255, 255, 185), width=3)
    draw.line((inset, h - inset, w - inset, h - inset), fill=(*spec.accent, 160), width=max(5, edge // 2))
    draw.line((inset, inset, inset, h - inset), fill=(*spec.accent, 125), width=max(5, edge // 2))

    # Top-right brand shelf. The reference is not just a label: the art
    # wordmark sits over a colored paper shelf with a dark underside.
    tab_h = round(h * 0.17)
    tab_w = round(w * 0.54)
    x0 = w - tab_w - round(w * 0.006)
    y0 = round(h * 0.012)
    tab = Image.new("RGBA", base.size, (0, 0, 0, 0))
    tab_draw = ImageDraw.Draw(tab)
    points = [
        (x0 + round(tab_w * 0.18), y0),
        (w, y0),
        (w, y0 + round(tab_h * 0.68)),
        (x0 + round(tab_w * 0.06), y0 + tab_h),
        (x0, y0 + round(tab_h * 0.35)),
    ]
    shadow = [(x + 8, y + 10) for x, y in points]
    tab_draw.polygon(shadow, fill=(0, 0, 0, 105))
    tab_draw.polygon(points, fill=(*spec.base, 238))
    tab_draw.line(points + [points[0]], fill=(255, 255, 255, 190), width=max(3, edge // 2))
    tab_draw.polygon(
        [
            (x0 + round(tab_w * 0.2), y0 + round(tab_h * 0.66)),
            (w, y0 + round(tab_h * 0.5)),
            (w, y0 + round(tab_h * 0.72)),
            (x0 + round(tab_w * 0.12), y0 + round(tab_h * 0.96)),
        ],
        fill=(0, 0, 0, 110),
    )

    # Small layered fold behind the brand shard.
    fold = [
        (x0 - round(tab_w * 0.05), y0 + round(tab_h * 0.24)),
        (x0 + round(tab_w * 0.34), y0),
        (x0 + round(tab_w * 0.24), y0 + round(tab_h * 0.82)),
        (x0 - round(tab_w * 0.1), y0 + tab_h),
    ]
    tab_draw.polygon(fold, fill=(*spec.accent, 150))
    if "tech" in spec.pattern or "tool" in spec.pattern or "black" in spec.pattern:
        stripe_color = (255, 255, 255, 190)
        for i in range(3):
            sx = x0 + 26 + i * 42
            tab_draw.polygon([(sx, y0 + 18), (sx + 30, y0 + 18), (sx + 8, y0 + 44), (sx - 22, y0 + 44)], fill=stripe_color)
    layer.alpha_composite(tab)

    # Optional product-following accent bracket.
    if product_box:
        px1, py1, px2, py2 = product_box
        pad = round(w * 0.025)
        bx1 = max(inset + 8, px1 - pad)
        by1 = max(inset + 8, py1 - pad)
        bx2 = min(w - inset - 8, px2 + pad)
        by2 = min(h - inset - 8, py2 + pad)
        corner = round(w * 0.075)
        bracket_w = max(4, edge // 2)
        for line in [
            (bx1, by1, bx1 + corner, by1),
            (bx1, by1, bx1, by1 + corner),
            (bx2, by1, bx2 - corner, by1),
            (bx2, by1, bx2, by1 + corner),
            (bx1, by2, bx1 + corner, by2),
            (bx1, by2, bx1, by2 - corner),
            (bx2, by2, bx2 - corner, by2),
            (bx2, by2, bx2, by2 - corner),
        ]:
            draw.line(line, fill=(*spec.base, 150), width=bracket_w)

    # Bottom-left tiny paper corner, not a heavy neon block.
    bl_w = round(w * 0.19)
    bl_h = round(h * 0.075)
    draw.polygon(
        [(inset, h - inset), (inset + bl_w, h - inset), (inset + bl_w - round(bl_h * 0.7), h - inset - bl_h), (inset, h - inset - round(bl_h * 0.45))],
        fill=(*spec.accent, 115),
    )

    base.alpha_composite(layer)
    logo_style = "kids" if spec.name == "pink_beauty" else "angular"
    logo = render_art_wordmark(brand, spec=spec, target_width=round(w * 0.39), style=logo_style)
    lx = w - logo.width - round(w * 0.025)
    ly = y0 + round(h * 0.018)
    base.alpha_composite(logo, (lx, ly))


def make_reference_sheets(paths: list[Path]) -> dict[str, str]:
    ensure(OUT / "reference")
    edge_tiles = []
    corner_tiles = []
    for p in paths:
        img = resize_square(Image.open(p), 520)
        edge_tiles.append((product_id(p), crop_edges(img)))
        corner_tiles.append((product_id(p), crop_corners(img, 150)))

    def sheet(items: list[tuple[str, Image.Image]], tile_size: tuple[int, int], title: str, out: Path) -> None:
        cols = 6
        label_h = 28
        pad = 10
        rows = math.ceil(len(items) / cols)
        canvas = Image.new("RGB", (cols * (tile_size[0] + pad) + pad, rows * (tile_size[1] + label_h + pad) + 56), "white")
        d = ImageDraw.Draw(canvas)
        d.text((14, 14), title, font=FONTS["h2"], fill=(28, 34, 42))
        for i, (label, tile) in enumerate(items):
            x = pad + (i % cols) * (tile_size[0] + pad)
            y = 56 + (i // cols) * (tile_size[1] + label_h + pad)
            canvas.paste(tile.resize(tile_size, Image.Resampling.LANCZOS), (x, y))
            d.text((x, y + tile_size[1] + 5), label, font=FONTS["tiny"], fill=(55, 62, 70))
        canvas.save(out, quality=94)

    edge_path = OUT / "reference/excitat_41_edge_strip_sheet.jpg"
    corner_path = OUT / "reference/excitat_41_corner_sheet.jpg"
    sheet(edge_tiles, (188, 188), "Excitat 41 first main images - edge strip extraction", edge_path)
    sheet(corner_tiles, (188, 188), "Excitat 41 first main images - corner/brand paper extraction", corner_path)
    return {"edge_sheet": str(edge_path), "corner_sheet": str(corner_path)}


def analyze(paths: list[Path]) -> list[dict[str, object]]:
    rows = []
    for idx, p in enumerate(paths, start=1):
        img = Image.open(p).convert("RGB")
        colors = dominant_edge_colors(img)
        family_counts = Counter(color_name(c) for c in colors)
        dominant_family = family_counts.most_common(1)[0][0]
        resized = resize_square(img, 420)
        stat = ImageStat.Stat(resized)
        rows.append({
            "index": idx,
            "product_id": product_id(p),
            "path": str(p),
            "size": img.size,
            "dominant_edge_colors": ["#%02x%02x%02x" % c for c in colors],
            "dominant_family": dominant_family,
            "mean_luma": round(sum(stat.mean) / 3, 1),
        })
    return rows


def palette_from_rows(rows: list[dict[str, object]]) -> list[FrameSpec]:
    # Curated from the extracted families plus visible reference behavior.
    return [
        FrameSpec("teal_clean", (0, 174, 173), (114, 220, 213), (22, 42, 46), (247, 251, 250), "thin_teal_paper"),
        FrameSpec("cyan_blue_tech", (0, 128, 210), (69, 216, 255), (10, 30, 50), (244, 249, 253), "blue_corner_flash"),
        FrameSpec("orange_tool", (235, 96, 39), (255, 178, 48), (50, 30, 15), (255, 249, 243), "warm_tool_label"),
        FrameSpec("green_home", (31, 151, 93), (142, 211, 106), (20, 55, 35), (247, 252, 246), "leaf_soft_corner"),
        FrameSpec("black_premium", (38, 41, 41), (182, 162, 119), (20, 20, 20), (250, 249, 245), "black_gold_edge"),
        FrameSpec("pink_beauty", (206, 88, 139), (255, 190, 210), (74, 24, 50), (255, 248, 251), "soft_beauty_tab"),
    ]


def draw_demo_product(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: tuple[int, int, int], label: str) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=26, fill=(255, 255, 255), outline=(205, 213, 218), width=3)
    draw.rounded_rectangle((x1 + 30, y1 + 40, x2 - 30, y2 - 42), radius=20, fill=color, outline=(70, 70, 70), width=2)
    draw.text((x1 + 58, y1 + 78), label, font=FONTS["h2"], fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))


def make_frame_demo(specs: list[FrameSpec]) -> str:
    ensure(OUT / "generated_frames")
    cards = []
    for spec in specs:
        paper = paper_texture(CANVAS, spec.bg)
        card = paper.copy()
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((118, 305, 1082, 1065), radius=18, fill=(255, 255, 255, 224), outline=(230, 235, 237), width=2)
        product_box = (260, 520, 860, 820)
        draw_demo_product(d, product_box, spec.base, spec.name.replace("_", " ").upper())
        d.text((104, 1112), "stable brand paper frame", font=FONTS["h2"], fill=(40, 50, 58))
        d.text((108, 1162), "large top-right EXITE shard + thin product-following border", font=FONTS["small"], fill=(82, 93, 102))
        draw_exite_frame(card, spec=spec, brand="EXITE", product_box=product_box)
        path = OUT / "generated_frames" / f"{spec.name}.png"
        card.save(path)
        cards.append((spec.name, card.resize((220, 220), Image.Resampling.LANCZOS)))

    cols = 3
    rows = math.ceil(len(cards) / cols)
    sheet = Image.new("RGB", (cols * 300 + 60, rows * 290 + 72), "white")
    d = ImageDraw.Draw(sheet)
    d.text((30, 18), "EXITE brand paper frame generator", font=FONTS["h2"], fill=(28, 34, 42))
    for i, (name, img) in enumerate(cards):
        x = 30 + (i % cols) * 300
        y = 72 + (i // cols) * 290
        sheet.paste(img.convert("RGB"), (x, y))
        d.text((x, y + 228), name, font=FONTS["small"], fill=(50, 58, 64))
    sheet_path = OUT / "generated_frames/exite_frame_variant_sheet.jpg"
    sheet.save(sheet_path, quality=94)
    return str(sheet_path)


def write_outputs(rows: list[dict[str, object]], specs: list[FrameSpec], sheets: dict[str, str], demo_sheet: str) -> None:
    ensure(OUT)
    with (OUT / "frame_feature_table.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["index", "product_id", "path", "size", "dominant_family", "dominant_edge_colors", "mean_luma"])
        writer.writeheader()
        for row in rows:
            out = row.copy()
            out["size"] = f"{row['size'][0]}x{row['size'][1]}"
            out["dominant_edge_colors"] = ",".join(row["dominant_edge_colors"])
            writer.writerow(out)

    summary = {
        "reference_root": str(ROOT),
        "main_image_count": len(rows),
        "gallery_count": len(list(PRODUCTS.glob("*/main_gallery/*"))),
        "observed_frame_patterns": {
            "brand_lockup": "top-right EXCITAT art-word logo on a slanted paper shelf",
            "logo_anatomy": "wide low angular wordmark, white fill, thick dark outline, grey extrusion, category-color edge, first-letter lightning spear",
            "frame_weight": "thin 4-12 px strokes, often partial rather than heavy full neon frame",
            "texture": "paper shelf, fold, dark underside, patterned corners, not a generic rounded label",
            "color_logic": "accent color follows product category and dominant product/background color",
            "product_following": "small brackets/callout strokes echo product bounding area rather than enclosing whole canvas heavily",
        },
        "dominant_family_counts": dict(Counter(row["dominant_family"] for row in rows)),
        "generated_specs": [
            {
                "name": s.name,
                "base": "#%02x%02x%02x" % s.base,
                "accent": "#%02x%02x%02x" % s.accent,
                "ink": "#%02x%02x%02x" % s.ink,
                "bg": "#%02x%02x%02x" % s.bg,
                "pattern": s.pattern,
            }
            for s in specs
        ],
        "sheets": {**sheets, "demo_sheet": demo_sheet},
    }
    (OUT / "frame_style_summary.json").write_text(json.dumps(summary, indent=2))

    md = f"""# Excitat / EXITE Brand Frame Study

Date: 2026-05-22

## Scope

- Reference set: 41 first main images from the eMAG seller capture.
- Supporting gallery set: {summary['gallery_count']} main-gallery images available for later slot-level study.
- Output goal: stabilize the brand-frame layer before improving full product-card generation.

## What The Reference Is Doing

1. The brand must be an art-word logo first. The default `EXCITAT` mark is wide, low, angular, forward-moving, and usually top-right.
2. The logo is layered: white fill, thick black/dark outline, grey or black extrusion, category-color edge, first-letter lightning spear, and a small right-side triangular cap.
3. The logo sits on a slanted paper shelf, not on a generic rounded label. The shelf often has a darker underside and a folded/torn left edge.
4. The frame is thin and simple. It is not a thick neon border. Most cards use 4-12 px strokes or partial edge lines.
5. The visible texture is an art-paper/fold feeling: angled tabs, torn/cut corners, light shadows, and small corner accents.
6. The frame color follows the product: teal for clean/home/electronics, blue/purple for gaming/tech, orange/red for tools or warnings, green for nature/home, black/gold for premium.
7. The frame supports the product instead of dominating it. Small brackets or colored strokes often echo the product area, while the main canvas remains light and readable.

## Stable Generation Rule

For our future `EXITE` brand frame:

- draw the EXITE art-word layer before drawing the frame
- keep a top-right slanted brand shelf
- use white angular letters with dark outline, extrusion, accent edge, and lightning first-letter spear
- keep outer strokes thin
- make only 1-2 corners expressive
- choose frame palette from product/category colors
- add a subtle paper texture, not a heavy cyber glow
- allow product-following brackets, but do not box the whole product too loudly
- switch logo style by category where needed: clean cut-out, bubble kids, serif ornamental, chromatic tech

## First Generator Variants

The current local generator creates six stable brand-paper variants:

| Variant | Use |
|---|---|
| `teal_clean` | default clean products, baby, home, small appliance |
| `cyan_blue_tech` | electronics, game, digital accessory |
| `orange_tool` | tools, hardware, warning/proof cards |
| `green_home` | home, garden, natural/eco scenes |
| `black_premium` | premium, office, classic, gift |
| `pink_beauty` | beauty, hair, personal care |

## Artifacts

- Edge extraction sheet: `{sheets['edge_sheet']}`
- Corner/brand extraction sheet: `{sheets['corner_sheet']}`
- Generated EXITE frame variants: `{demo_sheet}`
- Feature table: `frame_feature_table.csv`
- Machine summary: `frame_style_summary.json`

## Current Judgment

This is closer to the reference than the previous heavy Ozon frame because it
keeps the border as a lightweight brand-paper system and upgrades the brand
from plain italic text into an art-word mark. The next step is to apply these
frames on real product cards and tune product-aware color selection.
"""
    (OUT / "EXCITAT_EXITE_FRAME_STUDY.md").write_text(md)


def main() -> None:
    ensure(OUT)
    paths = main_images()
    if len(paths) != 41:
        raise SystemExit(f"expected 41 first main images, found {len(paths)}")
    sheets = make_reference_sheets(paths)
    rows = analyze(paths)
    specs = palette_from_rows(rows)
    demo_sheet = make_frame_demo(specs)
    write_outputs(rows, specs, sheets, demo_sheet)
    print(json.dumps({
        "main_images": len(paths),
        "out": str(OUT),
        "edge_sheet": sheets["edge_sheet"],
        "corner_sheet": sheets["corner_sheet"],
        "demo_sheet": demo_sheet,
    }, indent=2))


if __name__ == "__main__":
    main()
