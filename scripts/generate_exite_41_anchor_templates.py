#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "assets/fonts/google_fonts"
OUT = ROOT / "experiments/20260522_exite_41_replication_anchors"
BRAND = "EXITE"
W = H = 1200


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    p = FONT_DIR / name
    if p.exists():
        return ImageFont.truetype(str(p), size)
    return system_font(size, True)


def system_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


F_RACING = font("RacingSansOne-Regular.ttf", 118)
F_RACING_BIG = font("RacingSansOne-Regular.ttf", 150)
F_BUNGEE = font("Bungee-Regular.ttf", 94)
F_RUSSO = font("RussoOne-Regular.ttf", 105)
F_ORBITRON = font("Orbitron-wght.ttf", 72)
F_KIDS = font("BungeeShade-Regular.ttf", 78)
F_TITLE = system_font(44, True)
F_TEXT = system_font(27, True)
F_SMALL = system_font(19, True)


def rgba(rgb: tuple[int, int, int], a: int = 255) -> tuple[int, int, int, int]:
    return (*rgb, a)


def mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        round(a[0] * (1 - t) + b[0] * t),
        round(a[1] * (1 - t) + b[1] * t),
        round(a[2] * (1 - t) + b[2] * t),
    )


def gradient(size: tuple[int, int], a: tuple[int, int, int], b: tuple[int, int, int], vertical: bool = True) -> Image.Image:
    w, h = size
    im = Image.new("RGBA", size)
    px = im.load()
    span = max(1, h - 1 if vertical else w - 1)
    for y in range(h):
        for x in range(w):
            t = (y if vertical else x) / span
            px[x, y] = rgba(mix(a, b, t))
    return im


def paper(size: tuple[int, int], base: tuple[int, int, int], strength: int = 7) -> Image.Image:
    w, h = size
    im = Image.new("RGBA", size, rgba(base))
    px = im.load()
    for y in range(h):
        for x in range(w):
            n = ((x * 17 + y * 31 + (x * y) % 23) % (strength * 2 + 1)) - strength
            r, g, b, a = px[x, y]
            px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)), a)
    return im.filter(ImageFilter.GaussianBlur(0.18))


def shadow_layer(size: tuple[int, int], draw_fn, blur: float = 10, alpha: int = 90) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d, (0, 0, 0, alpha))
    return layer.filter(ImageFilter.GaussianBlur(blur))


def draw_brand(
    im: Image.Image,
    accent: tuple[int, int, int],
    *,
    x: int = 610,
    y: int = 34,
    w: int = 540,
    h: int = 142,
    font_face: ImageFont.ImageFont = F_RACING,
    fill: tuple[int, int, int] = (255, 255, 255),
    stroke: tuple[int, int, int] = (14, 19, 25),
    gold: bool = False,
    bubble: bool = False,
) -> None:
    d = ImageDraw.Draw(im)
    sl = 55
    shelf = [(x + sl, y), (x + w, y), (x + w - 22, y + h - 34), (x, y + h)]
    underside = [(x + sl + 22, y + h - 52), (x + w, y + h - 48), (x + w - 10, y + h + 8), (x + 18, y + h + 22)]
    d.polygon([(px + 10, py + 11) for px, py in underside], fill=(0, 0, 0, 75))
    d.polygon(underside, fill=(5, 8, 12, 235))
    d.polygon([(px + 7, py + 8) for px, py in shelf], fill=(0, 0, 0, 65))
    d.polygon(shelf, fill=rgba(accent, 240))
    d.polygon([(x + 10, y + h - 18), (x + sl + 18, y + 3), (x + sl + 78, y + 0), (x + 42, y + h + 12)], fill=(255, 184, 45, 245))
    d.polygon([(x + 66, y + h - 12), (x + sl + 92, y + 4), (x + sl + 164, y + 6), (x + 106, y + h + 2)], fill=(255, 255, 255, 120))
    d.line((x + 52, y + h - 5, x + w - 8, y + h - 54), fill=(255, 255, 255, 95), width=3)

    text_layer = Image.new("RGBA", (620, 190), (0, 0, 0, 0))
    td = ImageDraw.Draw(text_layer)
    bbox = td.textbbox((0, 0), BRAND, font=font_face, stroke_width=7)
    tx = 38 - bbox[0]
    ty = 30 - bbox[1]
    td.text((tx + 9, ty + 10), BRAND, font=font_face, fill=(0, 0, 0, 140), stroke_width=9, stroke_fill=(0, 0, 0, 140))
    if gold:
        td.text((tx, ty), BRAND, font=font_face, fill=(255, 224, 118), stroke_width=7, stroke_fill=stroke)
        mask = Image.new("L", text_layer.size, 0)
        md = ImageDraw.Draw(mask)
        md.text((tx, ty), BRAND, font=font_face, fill=255)
        chrome = gradient(text_layer.size, (255, 246, 178), (170, 92, 18), vertical=True)
        chrome.putalpha(mask)
        text_layer.alpha_composite(chrome)
    elif bubble:
        td.text((tx, ty), BRAND, font=font_face, fill=(114, 226, 238), stroke_width=9, stroke_fill=(255, 255, 255))
        td.text((tx, ty), BRAND, font=font_face, fill=(114, 226, 238), stroke_width=3, stroke_fill=stroke)
    else:
        td.text((tx, ty), BRAND, font=font_face, fill=fill, stroke_width=7, stroke_fill=stroke)
        td.text((tx - 4, ty - 3), BRAND, font=font_face, fill=(255, 255, 255, 105), stroke_width=1, stroke_fill=(255, 255, 255, 105))
    text_layer = text_layer.transform((650, 190), Image.Transform.AFFINE, (1, -0.08, 18, 0, 1, 0), Image.Resampling.BICUBIC)
    im.alpha_composite(text_layer, (x + 92, y + 18))


def draw_outer_sleeve(im: Image.Image, color: tuple[int, int, int], width: int, inner: int, fill_inner: tuple[int, int, int] = (255, 255, 255)) -> None:
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W - 1, H - 1), outline=rgba(color, 235), width=width)
    d.rectangle((inner, inner, W - inner - 1, H - inner - 1), fill=rgba(fill_inner, 245), outline=(255, 255, 255, 180), width=4)


def rounded_panel(d: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill, outline, width: int = 3, radius: int = 24) -> None:
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_product_placeholder(d: ImageDraw.ImageDraw, family: str) -> None:
    if family == "appliance":
        d.rounded_rectangle((350, 310, 600, 820), radius=58, fill=(244, 252, 252), outline=(70, 160, 160), width=5)
        d.rounded_rectangle((390, 360, 560, 610), radius=30, fill=(18, 173, 168), outline=(0, 116, 116), width=5)
        d.ellipse((418, 650, 532, 764), fill=(255, 255, 255), outline=(0, 150, 145), width=6)
        d.rounded_rectangle((607, 388, 705, 790), radius=42, fill=(235, 250, 250), outline=(70, 160, 160), width=5)
        d.line((654, 450, 654, 735), fill=(0, 150, 145), width=5)
    elif family == "fan":
        d.rounded_rectangle((340, 300, 755, 755), radius=32, fill=(40, 52, 50), outline=(14, 105, 62), width=8)
        d.ellipse((405, 360, 690, 645), fill=(220, 236, 226), outline=(12, 92, 56), width=8)
        cx, cy = 548, 502
        for a in (0, 120, 240):
            r = math.radians(a)
            p = [
                (cx + math.cos(r) * 28, cy + math.sin(r) * 28),
                (cx + math.cos(r + 0.52) * 126, cy + math.sin(r + 0.52) * 126),
                (cx + math.cos(r + 1.1) * 50, cy + math.sin(r + 1.1) * 50),
            ]
            d.polygon(p, fill=(58, 78, 72))
        d.ellipse((505, 460, 590, 545), fill=(240, 248, 240), outline=(30, 95, 64), width=5)
    elif family == "tool":
        for i, x in enumerate((250, 390, 530, 670)):
            d.rounded_rectangle((x, 330, x + 90, 760), radius=12, fill=(225, 230, 232), outline=(85, 88, 90), width=4)
            d.ellipse((x + 21, 374, x + 69, 422), fill=(250, 250, 250), outline=(100, 100, 100), width=4)
            d.line((x + 18, 660, x + 72, 406), fill=(120, 120, 120), width=4)
    elif family == "tech":
        d.rounded_rectangle((342, 320, 768, 690), radius=44, fill=(18, 18, 28), outline=(67, 233, 255), width=5)
        d.rounded_rectangle((388, 380, 718, 580), radius=16, fill=(88, 39, 180), outline=(255, 57, 161), width=5)
        for x in (410, 482, 554, 626):
            d.ellipse((x, 618, x + 38, 656), fill=(45, 235, 240), outline=(255, 255, 255), width=2)
        d.line((270, 835, 870, 735), fill=(255, 57, 161, 180), width=8)
        d.line((260, 860, 870, 760), fill=(49, 225, 255, 180), width=4)
    elif family == "gift":
        d.rounded_rectangle((334, 310, 775, 760), radius=28, fill=(255, 248, 252), outline=(40, 32, 38), width=5)
        for i, (x, y) in enumerate(((410, 392), (555, 368), (490, 540), (635, 550))):
            d.polygon([(x, y), (x + 90, y + 28), (x + 50, y + 130), (x - 42, y + 94)], fill=((255, 94, 166) if i % 2 else (70, 36, 58)), outline=(30, 24, 32))
        d.ellipse((610, 670, 690, 750), fill=(255, 216, 234), outline=(196, 70, 120), width=5)
    elif family == "info":
        d.rounded_rectangle((135, 250, 590, 820), radius=18, fill=(245, 252, 254), outline=(17, 145, 165), width=4)
        d.rounded_rectangle((180, 330, 545, 585), radius=24, fill=(24, 156, 172), outline=(12, 92, 104), width=4)
        for i in range(3):
            d.rounded_rectangle((165 + i * 135, 645, 265 + i * 135, 770), radius=14, fill=(255, 255, 255), outline=(17, 145, 165), width=3)


def chip(d: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str, color: tuple[int, int, int], ink=(255, 255, 255)) -> None:
    d.rounded_rectangle(box, radius=14, fill=rgba(color, 230), outline=rgba(ink, 110), width=2)
    d.text((box[0] + 16, box[1] + 15), label, font=F_SMALL, fill=ink)


def teal_paper() -> Image.Image:
    im = paper((W, H), (242, 255, 254), 5)
    d = ImageDraw.Draw(im)
    draw_outer_sleeve(im, (0, 171, 168), 34, 56)
    for y in range(95, 1090, 76):
        d.line((58, y, 1142, y + 38), fill=(0, 171, 168, 18), width=2)
    draw_product_placeholder(d, "appliance")
    d.ellipse((115, 160, 205, 250), fill=(255, 176, 55), outline=(0, 170, 168), width=4)
    d.text((132, 181), "3+", font=F_TEXT, fill=(255, 255, 255))
    d.rectangle((58, 1018, 1142, 1126), fill=(0, 171, 168))
    d.rectangle((58, 1074, 1142, 1126), fill=(18, 43, 48))
    d.text((104, 1036), "Baby Steamer & Blender", font=F_TITLE, fill=(255, 255, 255))
    d.text((104, 1086), "FOOD GRADE  |  EASY CLEAN  |  LED ALARM", font=F_SMALL, fill=(245, 255, 255))
    for i, text in enumerate(("STEAM", "BLEND", "SAFE")):
        chip(d, (790, 770 + i * 72, 1045, 822 + i * 72), text, (255, 255, 255), (0, 128, 126))
    draw_brand(im, (0, 171, 168), font_face=F_RACING)
    return im


def green_botanical() -> Image.Image:
    im = paper((W, H), (246, 253, 244), 6)
    d = ImageDraw.Draw(im)
    draw_outer_sleeve(im, (33, 145, 75), 30, 58)
    for x in range(90, 1120, 120):
        for y in (110, 995):
            d.ellipse((x, y, x + 46, y + 20), fill=(98, 188, 93, 75), outline=(33, 145, 75, 105))
            d.line((x + 9, y + 11, x + 45, y + 2), fill=(33, 145, 75, 130), width=2)
    for y in range(140, 960, 170):
        d.ellipse((75, y, 118, y + 22), fill=(83, 176, 83, 80), outline=(33, 145, 75, 120))
        d.ellipse((1082, y + 40, 1128, y + 64), fill=(83, 176, 83, 80), outline=(33, 145, 75, 120))
    draw_product_placeholder(d, "fan")
    d.rectangle((78, 978, 1122, 1118), fill=(28, 124, 65))
    for i, label in enumerate(("500m3/h", "7 BLADES", "WALL READY", "LOW NOISE")):
        chip(d, (110 + i * 250, 1016, 322 + i * 250, 1078), label, (255, 255, 255), (28, 124, 65))
    draw_brand(im, (33, 145, 75), font_face=F_RUSSO, fill=(255, 255, 240), stroke=(20, 69, 38))
    return im


def orange_tool() -> Image.Image:
    im = paper((W, H), (255, 248, 238), 5)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 168), fill=(247, 89, 34))
    d.polygon([(0, 168), (318, 168), (0, 300)], fill=(255, 123, 43))
    draw_outer_sleeve(im, (239, 86, 36), 22, 48, (255, 255, 255))
    for i in range(12):
        x = 835 + i * 32
        d.line((x, 190, x + 120, 80), fill=(34, 34, 34, 40), width=8)
    draw_product_placeholder(d, "tool")
    for i, title in enumerate(("90deg", "180deg", "4PCS")):
        rounded_panel(d, (835, 292 + i * 145, 1090, 400 + i * 145), (255, 255, 255), (239, 86, 36), 4, 12)
        d.text((864, 318 + i * 145), title, font=F_TITLE, fill=(239, 86, 36))
    d.rectangle((48, 996, 1152, 1138), fill=(25, 25, 25))
    d.rectangle((48, 996, 312, 1138), fill=(239, 86, 36))
    d.text((82, 1022), "SILVER", font=F_TITLE, fill=(255, 255, 255))
    d.text((350, 1028), "SELF-LOCKING HINGE  |  SCREWS INCLUDED", font=F_TEXT, fill=(255, 255, 255))
    draw_brand(im, (247, 89, 34), font_face=F_BUNGEE, fill=(255, 247, 216), stroke=(30, 18, 12))
    return im


def dark_tech() -> Image.Image:
    im = gradient((W, H), (9, 10, 24), (45, 18, 70), vertical=True)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W - 1, H - 1), outline=(54, 235, 255), width=24)
    d.rectangle((34, 34, W - 35, H - 35), outline=(255, 42, 154), width=5)
    for i in range(9):
        x = -80 + i * 160
        d.line((x, 1150, x + 520, 30), fill=(65, 229, 255, 30), width=8)
    d.text((68, 88), "4K", font=F_RACING_BIG, fill=(245, 245, 255), stroke_width=5, stroke_fill=(75, 44, 190))
    d.text((68, 222), "RGB", font=F_TITLE, fill=(255, 55, 156))
    draw_product_placeholder(d, "tech")
    for i, label in enumerate(("500 GAMES", "2 PLAYERS", "HDMI", "1200mAh")):
        chip(d, (110 + i * 245, 988, 322 + i * 245, 1056), label, (16, 18, 30), (69, 235, 255))
    draw_brand(im, (255, 54, 156), x=610, y=30, w=560, h=150, font_face=F_RACING, fill=(255, 255, 255), stroke=(10, 8, 22))
    return im


def ornamental_gift() -> Image.Image:
    im = paper((W, H), (255, 249, 253), 5)
    d = ImageDraw.Draw(im)
    draw_outer_sleeve(im, (38, 28, 36), 24, 58)
    d.rectangle((24, 24, W - 25, H - 25), outline=(255, 116, 181), width=7)
    for x in range(86, 1110, 96):
        d.arc((x, 68, x + 80, 142), 205, 340, fill=(255, 116, 181), width=4)
        d.ellipse((x + 22, 92, x + 40, 110), fill=(255, 116, 181))
        d.polygon([(x + 62, 104), (x + 82, 92), (x + 92, 112), (x + 72, 122)], fill=(38, 28, 36))
    for y in range(200, 945, 120):
        d.polygon([(58, y), (92, y + 18), (62, y + 48), (28, y + 30)], fill=(255, 116, 181, 160), outline=(38, 28, 36))
        d.polygon([(1142, y + 30), (1108, y + 48), (1138, y + 78), (1172, y + 60)], fill=(255, 116, 181, 160), outline=(38, 28, 36))
    rounded_panel(d, (140, 185, 1045, 925), (255, 255, 255, 238), (255, 116, 181, 150), 3, 34)
    draw_product_placeholder(d, "gift")
    d.text((120, 1010), "WOODEN PUZZLE", font=F_TITLE, fill=(38, 28, 36))
    d.line((120, 1070, 520, 1070), fill=(255, 116, 181), width=6)
    draw_brand(im, (45, 35, 42), x=600, y=34, w=550, h=140, font_face=F_KIDS, fill=(95, 224, 236), stroke=(38, 28, 36), bubble=True)
    return im


def clean_info() -> Image.Image:
    im = paper((W, H), (246, 252, 253), 4)
    d = ImageDraw.Draw(im)
    draw_outer_sleeve(im, (17, 145, 165), 16, 50)
    d.line((70, 170, 540, 170), fill=(17, 145, 165), width=5)
    d.line((70, 170, 70, 540), fill=(17, 145, 165), width=5)
    d.line((1128, 990, 690, 990), fill=(17, 145, 165), width=5)
    d.line((1128, 990, 1128, 590), fill=(17, 145, 165), width=5)
    draw_product_placeholder(d, "info")
    d.rectangle((718, 220, 1108, 945), fill=(238, 244, 246), outline=(130, 147, 154), width=3)
    for i, label in enumerate(("AI TRACK", "EXTENSION", "STABLE", "360deg", "REMOTE")):
        y = 252 + i * 125
        d.rounded_rectangle((748, y, 1076, y + 82), radius=10, fill=(255, 255, 255), outline=(17, 145, 165), width=3)
        d.text((778, y + 24), label, font=F_TEXT, fill=(25, 58, 68))
    d.rectangle((74, 980, 630, 1110), fill=(17, 145, 165))
    d.text((106, 1008), "STABILIZER GIMBAL", font=F_TITLE, fill=(255, 255, 255))
    d.text((106, 1062), "PHONE HOLDER  |  REMOTE  |  TRIPOD", font=F_SMALL, fill=(230, 255, 255))
    draw_brand(im, (17, 145, 165), x=602, y=38, w=540, h=128, font_face=F_ORBITRON, fill=(255, 255, 255), stroke=(20, 54, 62))
    return im


TEMPLATES = [
    ("01_teal_paper_sleeve", "Teal Paper Sleeve", "refs 02/07/22/25", teal_paper),
    ("02_green_botanical", "Green Botanical", "refs 05/16/27/38", green_botanical),
    ("03_orange_tool_poster", "Orange Tool Poster", "refs 04/13/29/33/39", orange_tool),
    ("04_dark_neon_tech", "Dark Neon Tech", "refs 01/12/20/23/31/34/36", dark_tech),
    ("05_ornamental_gift", "Ornamental Gift", "refs 15/19/26/28/30/32/40", ornamental_gift),
    ("06_clean_technical_info", "Clean Technical Info", "refs 03/06/10/14/17/18/35/37/41", clean_info),
]


def make_sheet(paths: list[tuple[Path, str, str]]) -> Path:
    cell_w, cell_h = 620, 700
    sheet = Image.new("RGB", (cell_w * 3, cell_h * 2), "white")
    sd = ImageDraw.Draw(sheet)
    title_font = system_font(28, True)
    small_font = system_font(20)
    for idx, (path, title, refs) in enumerate(paths):
        x = (idx % 3) * cell_w
        y = (idx // 3) * cell_h
        im = Image.open(path).convert("RGB").resize((560, 560), Image.Resampling.LANCZOS)
        sheet.paste(im, (x + 30, y + 20))
        sd.text((x + 30, y + 594), f"{idx + 1}. {title}", font=title_font, fill=(24, 28, 33))
        sd.text((x + 30, y + 632), refs, font=small_font, fill=(90, 95, 102))
    out = OUT / "exite_41_anchor_templates_sheet.jpg"
    sheet.save(out, quality=94)
    return out


def main() -> None:
    ensure(OUT / "templates")
    written: list[tuple[Path, str, str]] = []
    for slug, title, refs, maker in TEMPLATES:
        im = maker().convert("RGB")
        path = OUT / "templates" / f"{slug}.png"
        im.save(path)
        written.append((path, title, refs))
    sheet = make_sheet(written)
    print(f"Wrote {len(written)} anchor templates")
    print(sheet)


if __name__ == "__main__":
    main()
