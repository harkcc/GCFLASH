#!/usr/bin/env python3
from __future__ import annotations

from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from generate_exite_41_anchor_templates import (
    F_BUNGEE,
    F_ORBITRON,
    F_RACING,
    F_RACING_BIG,
    F_RUSSO,
    F_SMALL,
    F_TEXT,
    F_TITLE,
    draw_brand,
    draw_outer_sleeve,
    gradient,
    paper,
    rgba,
    system_font,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/20260522_exite_framekit_v0_samples"
W = H = 1200


SRC = ROOT / "references/user_cases/20260521_emag_cangswjp/products"
PRODUCTS = {
    "blender": SRC
    / "02_D5YN6S3BM_Aparat-de-gatit-cu-aburi-si-blender-pentru-bebelusi-Excitat-multifunctional-Alarma-LED-a/detail_images/03_fb669aee.jpg",
    "hinge": SRC
    / "13_D393L43BM_Set-de-4-balamale-pliabile-cu-40-suruburi-Excitat-otel-unghi-reglabil-090180-pentru-masa/detail_images/07_d1ce84ea.jpg",
    "robot": SRC
    / "36_D263HS3BM_Caine-robot-inteligent-Excitat-Caine-Robot-Razboinic-cu-Telecomanda-Programabil-Interact/detail_images/04_a65d6798.jpg",
}


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def color_dist(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def estimate_bg(img: Image.Image) -> tuple[int, int, int]:
    rgb = img.convert("RGB")
    w, h = rgb.size
    points = []
    for x in range(0, w, max(1, w // 12)):
        points.append(rgb.getpixel((x, 0)))
        points.append(rgb.getpixel((x, h - 1)))
    for y in range(0, h, max(1, h // 12)):
        points.append(rgb.getpixel((0, y)))
        points.append(rgb.getpixel((w - 1, y)))
    points.sort(key=sum)
    mid = points[len(points) // 2]
    return mid


def remove_edge_background(img: Image.Image, tolerance: int = 58) -> Image.Image:
    rgb = img.convert("RGB")
    w, h = rgb.size
    bg = estimate_bg(rgb)
    visited = bytearray(w * h)
    remove = bytearray(w * h)
    q: deque[tuple[int, int]] = deque()

    def push(x: int, y: int) -> None:
        idx = y * w + x
        if visited[idx]:
            return
        visited[idx] = 1
        px = rgb.getpixel((x, y))
        bright = sum(px) / 3
        sat = max(px) - min(px)
        if color_dist(px, bg) <= tolerance or (bright > 226 and sat < 42):
            remove[idx] = 1
            q.append((x, y))

    for x in range(w):
        push(x, 0)
        push(x, h - 1)
    for y in range(h):
        push(0, y)
        push(w - 1, y)

    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h:
                push(nx, ny)

    alpha = Image.new("L", (w, h), 255)
    px_alpha = alpha.load()
    for y in range(h):
        for x in range(w):
            if remove[y * w + x]:
                px_alpha[x, y] = 0
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
    rgba_img = img.convert("RGBA")
    rgba_img.putalpha(alpha)
    bbox = alpha.getbbox()
    if bbox:
        rgba_img = rgba_img.crop(bbox)
    return rgba_img


def load_cutout(name: str) -> Image.Image:
    img = Image.open(PRODUCTS[name]).convert("RGB")
    if name == "blender":
        img = img.crop((0, 126, img.width, img.height - 8))
        return remove_edge_background(img, tolerance=62)
    if name == "robot":
        img = img.crop((20, 220, img.width - 18, 720))
        return remove_edge_background(img, tolerance=72)
    return remove_edge_background(img, tolerance=66)


def drop_shadow(product: Image.Image, size: tuple[int, int], offset: tuple[int, int], blur: float = 18, alpha: int = 90) -> Image.Image:
    shadow = Image.new("RGBA", size, (0, 0, 0, 0))
    mask = product.getchannel("A").filter(ImageFilter.GaussianBlur(blur))
    black = Image.new("RGBA", product.size, (0, 0, 0, alpha))
    black.putalpha(mask)
    shadow.alpha_composite(black, offset)
    return shadow


def place_product(
    card: Image.Image,
    product: Image.Image,
    box: tuple[int, int, int, int],
    *,
    shadow: bool = True,
    blur: float = 18,
    alpha: int = 85,
) -> None:
    x1, y1, x2, y2 = box
    max_w, max_h = x2 - x1, y2 - y1
    ratio = min(max_w / product.width, max_h / product.height)
    product = product.resize((round(product.width * ratio), round(product.height * ratio)), Image.Resampling.LANCZOS)
    x = x1 + (max_w - product.width) // 2
    y = y1 + (max_h - product.height) // 2
    if shadow:
        card.alpha_composite(drop_shadow(product, card.size, (x + 18, y + 24), blur, alpha))
    card.alpha_composite(product, (x, y))


def chip(d: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str, fill, ink=(255, 255, 255)) -> None:
    d.rounded_rectangle(box, radius=14, fill=fill, outline=(*ink[:3], 110), width=2)
    d.text((box[0] + 18, box[1] + 15), label, font=F_SMALL, fill=ink)


def teal_blender(product: Image.Image) -> Image.Image:
    card = paper((W, H), (240, 255, 254), 5)
    d = ImageDraw.Draw(card)
    draw_outer_sleeve(card, (0, 171, 168), 34, 56)
    for y in range(104, 990, 74):
        d.line((60, y, 1140, y + 36), fill=(0, 171, 168, 22), width=2)
    for i, label in enumerate(("STEAM", "BLEND", "PUREE", "HEAT", "CLEAN")):
        cy = 188 + i * 92
        d.ellipse((94, cy, 172, cy + 78), fill=(255, 169, 38), outline=(255, 255, 255), width=4)
        d.text((194, cy + 22), label, font=F_SMALL, fill=(0, 132, 130))
    d.rounded_rectangle((790, 690, 1058, 892), radius=24, fill=(255, 255, 255, 220), outline=(0, 156, 152), width=3)
    for i, label in enumerate(("FOOD GRADE", "LED PANEL", "400ml BOWL")):
        chip(d, (820, 720 + i * 54, 1028, 764 + i * 54), label, (255, 255, 255, 235), (0, 125, 122))
    place_product(card, product, (250, 230, 820, 860), shadow=True, blur=20, alpha=70)
    d.rectangle((58, 1018, 1142, 1128), fill=(0, 171, 168))
    d.rectangle((58, 1075, 1142, 1128), fill=(18, 43, 48))
    d.text((102, 1035), "Baby Steamer & Blender", font=F_TITLE, fill=(255, 255, 255))
    d.text((102, 1086), "SAFE MATERIAL  |  EASY CLEAN  |  ONE-TOUCH", font=F_SMALL, fill=(245, 255, 255))
    draw_brand(card, (0, 171, 168), font_face=F_RACING)
    return card.convert("RGB")


def orange_hinge(product: Image.Image) -> Image.Image:
    card = paper((W, H), (255, 248, 238), 4)
    d = ImageDraw.Draw(card)
    d.rectangle((0, 0, W, 176), fill=(247, 89, 34))
    d.polygon([(0, 176), (330, 176), (0, 312)], fill=(255, 126, 42))
    draw_outer_sleeve(card, (239, 86, 36), 22, 48, (255, 255, 255))
    for i in range(11):
        x = 815 + i * 34
        d.line((x, 210, x + 120, 88), fill=(34, 34, 34, 38), width=8)
    place_product(card, product, (165, 255, 760, 860), shadow=True, blur=14, alpha=95)
    for i, title in enumerate(("90deg", "180deg", "4PCS")):
        d.rounded_rectangle((815, 300 + i * 144, 1100, 408 + i * 144), radius=14, fill=(255, 255, 255), outline=(239, 86, 36), width=5)
        d.text((852, 326 + i * 144), title, font=F_TITLE, fill=(239, 86, 36))
    d.rectangle((48, 990, 1152, 1138), fill=(25, 25, 25))
    d.rectangle((48, 990, 316, 1138), fill=(239, 86, 36))
    d.text((86, 1020), "SILVER", font=F_TITLE, fill=(255, 255, 255))
    d.text((356, 1029), "SELF-LOCKING HINGE  |  SCREWS INCLUDED", font=F_TEXT, fill=(255, 255, 255))
    draw_brand(card, (247, 89, 34), font_face=F_BUNGEE, fill=(255, 247, 216), stroke=(30, 18, 12), x=598, y=28, w=580, h=148)
    return card.convert("RGB")


def dark_robot(product: Image.Image) -> Image.Image:
    card = gradient((W, H), (8, 9, 22), (46, 18, 76), vertical=True)
    d = ImageDraw.Draw(card)
    d.rectangle((0, 0, W - 1, H - 1), outline=(54, 235, 255), width=26)
    d.rectangle((38, 38, W - 39, H - 39), outline=(255, 42, 154), width=6)
    for i in range(10):
        x = -130 + i * 155
        d.line((x, 1160, x + 530, 60), fill=(65, 229, 255, 34), width=8)
    d.text((70, 88), "RC", font=F_RACING_BIG, fill=(245, 245, 255), stroke_width=5, stroke_fill=(75, 44, 190))
    d.text((72, 220), "ROBOT", font=F_TITLE, fill=(255, 55, 156))
    place_product(card, product, (160, 205, 1040, 865), shadow=True, blur=24, alpha=125)
    for i, label in enumerate(("MULTI-MODE", "REMOTE", "LIGHT", "TURRET")):
        chip(d, (105 + i * 250, 986, 322 + i * 250, 1056), label, (16, 18, 30, 245), (69, 235, 255))
    draw_brand(card, (255, 54, 156), x=610, y=28, w=560, h=150, font_face=F_RACING, fill=(255, 255, 255), stroke=(10, 8, 22))
    return card.convert("RGB")


def clean_info(product: Image.Image) -> Image.Image:
    card = paper((W, H), (246, 252, 253), 4)
    d = ImageDraw.Draw(card)
    draw_outer_sleeve(card, (17, 145, 165), 18, 50)
    d.line((78, 174, 550, 174), fill=(17, 145, 165), width=5)
    d.line((78, 174, 78, 540), fill=(17, 145, 165), width=5)
    d.line((1125, 990, 690, 990), fill=(17, 145, 165), width=5)
    d.line((1125, 990, 1125, 590), fill=(17, 145, 165), width=5)
    d.rounded_rectangle((120, 230, 620, 835), radius=24, fill=(255, 255, 255, 220), outline=(17, 145, 165), width=4)
    place_product(card, product, (150, 290, 590, 780), shadow=True, blur=14, alpha=80)
    d.rectangle((720, 218, 1108, 945), fill=(238, 244, 246), outline=(130, 147, 154), width=3)
    for i, label in enumerate(("ANGLE LOCK", "METAL BODY", "4 PCS SET", "SCREWS", "CABINET USE")):
        y = 252 + i * 124
        d.rounded_rectangle((750, y, 1076, y + 82), radius=10, fill=(255, 255, 255), outline=(17, 145, 165), width=3)
        d.text((780, y + 24), label, font=F_TEXT, fill=(25, 58, 68))
    d.rectangle((74, 982, 660, 1110), fill=(17, 145, 165))
    d.text((106, 1010), "FOLDING HINGE KIT", font=F_TITLE, fill=(255, 255, 255))
    d.text((106, 1062), "METAL  |  90/180 DEG  |  EASY INSTALL", font=F_SMALL, fill=(230, 255, 255))
    draw_brand(card, (17, 145, 165), x=604, y=38, w=540, h=128, font_face=F_ORBITRON, fill=(255, 255, 255), stroke=(20, 54, 62))
    return card.convert("RGB")


def make_sheet(paths: list[tuple[Path, str]]) -> Path:
    cell_w, cell_h = 640, 710
    sheet = Image.new("RGB", (cell_w * 2, cell_h * 2), "white")
    d = ImageDraw.Draw(sheet)
    title = system_font(28, True)
    small = system_font(18)
    for i, (path, label) in enumerate(paths):
        x = (i % 2) * cell_w
        y = (i // 2) * cell_h
        img = Image.open(path).convert("RGB").resize((590, 590), Image.Resampling.LANCZOS)
        sheet.paste(img, (x + 25, y + 20))
        d.text((x + 28, y + 622), label, font=title, fill=(26, 31, 36))
        d.text((x + 28, y + 658), "FrameKit v0 deterministic render", font=small, fill=(91, 99, 110))
    out = OUT / "framekit_v0_sample_sheet.jpg"
    sheet.save(out, quality=94)
    return out


def make_cutout_sheet(cutouts: dict[str, Image.Image]) -> Path:
    cell = 360
    sheet = Image.new("RGB", (cell * len(cutouts), cell), "white")
    d = ImageDraw.Draw(sheet)
    for i, (name, img) in enumerate(cutouts.items()):
        bg = Image.new("RGBA", (cell, cell), (255, 255, 255, 255))
        preview = img.copy()
        preview.thumbnail((cell - 60, cell - 90), Image.Resampling.LANCZOS)
        bg.alpha_composite(preview, ((cell - preview.width) // 2, 35 + (cell - 90 - preview.height) // 2))
        sheet.paste(bg.convert("RGB"), (i * cell, 0))
        d.text((i * cell + 25, cell - 45), name, font=F_TEXT, fill=(24, 30, 36))
    out = OUT / "input_cutouts_sheet.jpg"
    sheet.save(out, quality=94)
    return out


def main() -> None:
    ensure(OUT / "samples")
    ensure(OUT / "cutouts")
    cutouts = {name: load_cutout(name) for name in PRODUCTS}
    for name, img in cutouts.items():
        img.save(OUT / "cutouts" / f"{name}_cutout.png")

    samples = [
        (teal_blender(cutouts["blender"]), "01_teal_blender.png", "Teal Paper Sleeve"),
        (orange_hinge(cutouts["hinge"]), "02_orange_hinge.png", "Orange Tool Poster"),
        (dark_robot(cutouts["robot"]), "03_dark_robot.png", "Dark Neon Tech"),
        (clean_info(cutouts["hinge"]), "04_clean_info_hinge.png", "Clean Technical Info"),
    ]
    written: list[tuple[Path, str]] = []
    for img, file_name, label in samples:
        path = OUT / "samples" / file_name
        img.save(path)
        written.append((path, label))
    cutout_sheet = make_cutout_sheet(cutouts)
    sample_sheet = make_sheet(written)
    print(sample_sheet)
    print(cutout_sheet)


if __name__ == "__main__":
    main()
