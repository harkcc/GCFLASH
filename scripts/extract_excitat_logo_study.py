#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("references/user_cases/20260521_emag_cangswjp")
PRODUCTS = ROOT / "products"
OUT = Path("experiments/20260522_excitat_logo_study")


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


FONT_LABEL = load_font(24, True)
FONT_SMALL = load_font(18)


def main_images() -> list[Path]:
    return sorted(PRODUCTS.glob("*/main_gallery/01_*"))


def product_id(path: Path) -> str:
    return path.parts[-3].split("_", 2)[1]


def crop_top_right_logo(img: Image.Image) -> Image.Image:
    w, h = img.size
    x1 = int(w * 0.46)
    y1 = 0
    x2 = w
    y2 = int(h * 0.26)
    return img.crop((x1, y1, x2, y2)).convert("RGB")


def crop_header_band(img: Image.Image) -> Image.Image:
    w, h = img.size
    return img.crop((0, 0, w, int(h * 0.23))).convert("RGB")


def crop_right_upper_quarter(img: Image.Image) -> Image.Image:
    w, h = img.size
    return img.crop((int(w * 0.38), 0, w, int(h * 0.42))).convert("RGB")


def fit_tile(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    ratio = min(tw / img.width, th / img.height)
    resized = img.resize((max(1, round(img.width * ratio)), max(1, round(img.height * ratio))), Image.Resampling.LANCZOS)
    tile = Image.new("RGB", size, "white")
    tile.paste(resized, ((tw - resized.width) // 2, (th - resized.height) // 2))
    return tile


def sheet(items: list[tuple[str, Image.Image]], tile_size: tuple[int, int], title: str, out: Path) -> None:
    cols = 3
    rows = math.ceil(len(items) / cols)
    pad = 24
    label_h = 36
    width = cols * tile_size[0] + (cols + 1) * pad
    height = rows * (tile_size[1] + label_h) + (rows + 1) * pad + 54
    page = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(page)
    d.text((pad, 18), title, font=FONT_LABEL, fill=(25, 32, 38))
    for i, (label, img) in enumerate(items):
        x = pad + (i % cols) * (tile_size[0] + pad)
        y = 72 + (i // cols) * (tile_size[1] + label_h + pad)
        page.paste(fit_tile(img, tile_size), (x, y))
        d.text((x, y + tile_size[1] + 8), label, font=FONT_SMALL, fill=(48, 55, 62))
    page.save(out, quality=94)


def main() -> None:
    ensure(OUT / "top_right_logo")
    ensure(OUT / "header_band")
    ensure(OUT / "right_upper_quarter")

    top_items: list[tuple[str, Image.Image]] = []
    header_items: list[tuple[str, Image.Image]] = []
    quarter_items: list[tuple[str, Image.Image]] = []

    for i, path in enumerate(main_images(), start=1):
        img = Image.open(path).convert("RGB")
        pid = product_id(path)
        label = f"{i:02d}_{pid}"

        top = crop_top_right_logo(img)
        header = crop_header_band(img)
        quarter = crop_right_upper_quarter(img)

        top.save(OUT / "top_right_logo" / f"{label}.jpg", quality=96)
        header.save(OUT / "header_band" / f"{label}.jpg", quality=96)
        quarter.save(OUT / "right_upper_quarter" / f"{label}.jpg", quality=96)

        top_items.append((label, top))
        header_items.append((label, header))
        quarter_items.append((label, quarter))

    sheet(top_items, (500, 240), "Excitat logo study - top-right brand region", OUT / "excitat_logo_top_right_sheet.jpg")
    sheet(header_items, (620, 180), "Excitat logo study - full header band", OUT / "excitat_logo_header_band_sheet.jpg")
    sheet(quarter_items, (500, 360), "Excitat logo study - right upper quarter", OUT / "excitat_logo_right_upper_quarter_sheet.jpg")

    print({
        "count": len(top_items),
        "out": str(OUT),
        "top_right_sheet": str(OUT / "excitat_logo_top_right_sheet.jpg"),
        "header_sheet": str(OUT / "excitat_logo_header_band_sheet.jpg"),
        "quarter_sheet": str(OUT / "excitat_logo_right_upper_quarter_sheet.jpg"),
    })


if __name__ == "__main__":
    main()
