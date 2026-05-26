#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ROOT / "references/user_cases/20260521_emag_cangswjp/products"
OUT = ROOT / "experiments/20260522_excitat_41_frame_extract"
CANVAS = 1200


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


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


TITLE_FONT = system_font(26, True)
SMALL_FONT = system_font(18)


@dataclass(frozen=True)
class SourceImage:
    index: int
    product_id: str
    source: Path
    product_dir: Path


def list_first_main_images() -> list[SourceImage]:
    out: list[SourceImage] = []
    for product_dir in sorted(PRODUCTS.iterdir()):
        if not product_dir.is_dir():
            continue
        parts = product_dir.name.split("_", 2)
        if len(parts) < 2 or not parts[0].isdigit():
            continue
        first = sorted((product_dir / "main_gallery").glob("01_*"))
        if not first:
            continue
        out.append(SourceImage(int(parts[0]), parts[1], first[0], product_dir))
    return sorted(out, key=lambda item: item.index)


def normalize_square(path: Path, size: int = CANVAS) -> Image.Image:
    src = Image.open(path).convert("RGB")
    ratio = size / max(src.width, src.height)
    new_size = (round(src.width * ratio), round(src.height * ratio))
    resized = src.resize(new_size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (size, size), "white")
    canvas.paste(resized, ((size - resized.width) // 2, (size - resized.height) // 2))
    return canvas


def add_rect(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], fill: int = 255) -> None:
    draw.rectangle(rect, fill=fill)


def add_brand_shelf(draw: ImageDraw.ImageDraw, *, broad: bool) -> None:
    if broad:
        draw.polygon([(560, 0), (CANVAS, 0), (CANVAS, 290), (520, 260)], fill=255)
        draw.polygon([(660, 0), (CANVAS, 0), (CANVAS, 370), (610, 330)], fill=255)
    else:
        draw.polygon([(680, 0), (CANVAS, 0), (CANVAS, 205), (635, 190)], fill=255)


# Rectangles that preserve non-edge composition modules from the 41 references:
# right proof cards, bottom title strips, side panels, top-left commercial tags,
# and ornamental/technical zones that visually function as the frame.
EXTRA_RECTS: dict[int, list[tuple[int, int, int, int]]] = {
    1: [(0, 0, 340, 430), (0, 900, 1200, 1200), (870, 0, 1200, 420)],
    2: [(0, 945, 1200, 1200), (0, 0, 275, 520), (760, 675, 1200, 1020)],
    3: [(0, 0, 1200, 230), (0, 980, 1200, 1200), (900, 0, 1200, 520)],
    4: [(0, 0, 460, 360), (850, 230, 1200, 880), (0, 960, 1200, 1200)],
    5: [(0, 0, 260, 1200), (940, 0, 1200, 1200), (0, 930, 1200, 1200)],
    6: [(0, 0, 1200, 250), (0, 890, 1200, 1200), (780, 0, 1200, 1200)],
    7: [(0, 0, 295, 620), (0, 920, 1200, 1200), (735, 700, 1200, 1050)],
    8: [(0, 0, 1200, 220), (0, 940, 1200, 1200), (760, 420, 1200, 880)],
    9: [(0, 0, 340, 1200), (850, 0, 1200, 1200), (0, 905, 1200, 1200)],
    10: [(0, 0, 1200, 240), (0, 900, 1200, 1200), (805, 0, 1200, 1200)],
    11: [(0, 0, 1200, 210), (0, 870, 1200, 1200), (760, 0, 1200, 930)],
    12: [(0, 0, 370, 520), (0, 880, 1200, 1200), (820, 0, 1200, 480)],
    13: [(0, 0, 1200, 260), (760, 250, 1200, 900), (0, 880, 1200, 1200)],
    14: [(0, 0, 1200, 245), (0, 915, 1200, 1200), (800, 0, 1200, 1200)],
    15: [(0, 0, 1200, 260), (0, 880, 1200, 1200), (0, 0, 270, 1200), (930, 0, 1200, 1200)],
    16: [(0, 0, 300, 1200), (900, 0, 1200, 1200), (0, 870, 1200, 1200)],
    17: [(0, 0, 1200, 240), (0, 855, 1200, 1200), (830, 0, 1200, 1200)],
    18: [(0, 0, 1200, 250), (0, 885, 1200, 1200), (760, 0, 1200, 1200)],
    19: [(0, 0, 1200, 280), (0, 870, 1200, 1200), (0, 0, 260, 1200), (930, 0, 1200, 1200)],
    20: [(0, 0, 1200, 300), (0, 860, 1200, 1200), (0, 0, 300, 1200), (900, 0, 1200, 1200)],
    21: [(0, 0, 1200, 250), (0, 900, 1200, 1200), (760, 0, 1200, 1200)],
    22: [(0, 0, 1200, 250), (0, 880, 1200, 1200), (760, 0, 1200, 1200)],
    23: [(0, 0, 1200, 330), (0, 820, 1200, 1200), (0, 0, 260, 1200), (940, 0, 1200, 1200)],
    24: [(0, 0, 1200, 260), (0, 820, 1200, 1200), (0, 0, 260, 1200), (920, 0, 1200, 1200)],
    25: [(0, 0, 1200, 260), (0, 880, 1200, 1200), (780, 0, 1200, 1200)],
    26: [(0, 0, 1200, 300), (0, 850, 1200, 1200), (0, 0, 295, 1200), (905, 0, 1200, 1200)],
    27: [(0, 0, 1200, 300), (0, 870, 1200, 1200), (0, 0, 280, 1200), (900, 0, 1200, 1200)],
    28: [(0, 0, 1200, 300), (0, 840, 1200, 1200), (0, 0, 300, 1200), (900, 0, 1200, 1200)],
    29: [(0, 0, 1200, 265), (0, 885, 1200, 1200), (770, 0, 1200, 1200)],
    30: [(0, 0, 1200, 300), (0, 850, 1200, 1200), (0, 0, 300, 1200), (900, 0, 1200, 1200)],
    31: [(0, 0, 1200, 300), (0, 820, 1200, 1200), (0, 0, 280, 1200), (900, 0, 1200, 1200)],
    32: [(0, 0, 1200, 320), (0, 830, 1200, 1200), (0, 0, 280, 1200), (900, 0, 1200, 1200)],
    33: [(0, 0, 1200, 260), (0, 850, 1200, 1200), (760, 0, 1200, 1200)],
    34: [(0, 0, 1200, 300), (0, 820, 1200, 1200), (760, 0, 1200, 1200), (0, 0, 280, 1200)],
    35: [(0, 0, 1200, 320), (0, 820, 1200, 1200), (760, 0, 1200, 1200), (0, 0, 320, 1200)],
    36: [(0, 0, 1200, 320), (0, 820, 1200, 1200), (0, 0, 280, 1200), (900, 0, 1200, 1200)],
    37: [(0, 0, 1200, 280), (0, 830, 1200, 1200), (0, 0, 270, 1200), (900, 0, 1200, 1200)],
    38: [(0, 0, 1200, 300), (0, 820, 1200, 1200), (0, 0, 300, 1200), (900, 0, 1200, 1200)],
    39: [(0, 0, 1200, 260), (0, 880, 1200, 1200), (770, 0, 1200, 1200)],
    40: [(0, 0, 1200, 320), (0, 830, 1200, 1200), (0, 0, 300, 1200), (900, 0, 1200, 1200)],
    41: [(0, 0, 1200, 260), (0, 880, 1200, 1200), (740, 0, 1200, 1200)],
}


def strict_edge_mask(index: int) -> Image.Image:
    mask = Image.new("L", (CANVAS, CANVAS), 0)
    d = ImageDraw.Draw(mask)
    edge = 132
    add_rect(d, (0, 0, CANVAS, edge))
    add_rect(d, (0, CANVAS - edge, CANVAS, CANVAS))
    add_rect(d, (0, 0, edge, CANVAS))
    add_rect(d, (CANVAS - edge, 0, CANVAS, CANVAS))
    add_brand_shelf(d, broad=False)
    if index in {1, 12, 20, 23, 31, 34, 36}:
        add_rect(d, (0, 0, 290, 390))
        add_rect(d, (0, 890, CANVAS, CANVAS))
    return mask


def design_frame_mask(index: int) -> Image.Image:
    mask = Image.new("L", (CANVAS, CANVAS), 0)
    d = ImageDraw.Draw(mask)
    edge = 172
    add_rect(d, (0, 0, CANVAS, edge))
    add_rect(d, (0, CANVAS - edge, CANVAS, CANVAS))
    add_rect(d, (0, 0, edge, CANVAS))
    add_rect(d, (CANVAS - edge, 0, CANVAS, CANVAS))
    add_brand_shelf(d, broad=True)
    for rect in EXTRA_RECTS.get(index, []):
        add_rect(d, rect)
    # Preserve four expressive corners, because many references place decorative
    # paper, floral, tech-line, or neon treatments just inside the edge.
    corner = 300
    for rect in [
        (0, 0, corner, corner),
        (CANVAS - corner, 0, CANVAS, corner),
        (0, CANVAS - corner, corner, CANVAS),
        (CANVAS - corner, CANVAS - corner, CANVAS, CANVAS),
    ]:
        add_rect(d, rect)
    # Soften only the alpha edge slightly. The extracted layer stays crisp but
    # compositing into new cards does not show harsh cut lines.
    return mask.filter(ImageFilter.GaussianBlur(0.65))


def apply_mask(img: Image.Image, mask: Image.Image) -> Image.Image:
    rgba = img.convert("RGBA")
    rgba.putalpha(mask)
    return rgba


def checkerboard(size: tuple[int, int], cell: int = 32) -> Image.Image:
    w, h = size
    im = Image.new("RGB", size, "white")
    d = ImageDraw.Draw(im)
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            color = (232, 236, 240) if (x // cell + y // cell) % 2 else (252, 252, 252)
            d.rectangle((x, y, x + cell - 1, y + cell - 1), fill=color)
    return im


def preview_on_checker(layer: Image.Image) -> Image.Image:
    base = checkerboard(layer.size)
    base = base.convert("RGBA")
    base.alpha_composite(layer)
    return base.convert("RGB")


def make_contact_sheet(
    items: list[tuple[str, Path]],
    out_path: Path,
    *,
    cols: int = 6,
    tile: int = 220,
    label_h: int = 52,
) -> None:
    rows = math.ceil(len(items) / cols)
    sheet = Image.new("RGB", (cols * tile, rows * (tile + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    for pos, (label, path) in enumerate(items):
        x = (pos % cols) * tile
        y = (pos // cols) * (tile + label_h)
        img = Image.open(path).convert("RGB")
        img.thumbnail((tile - 16, tile - 16), Image.Resampling.LANCZOS)
        ox = x + (tile - img.width) // 2
        oy = y + 8 + (tile - 16 - img.height) // 2
        sheet.paste(img, (ox, oy))
        draw.text((x + 10, y + tile + 5), label[:23], font=SMALL_FONT, fill=(28, 32, 36))
    sheet.save(out_path, quality=94)


def make_source_vs_frame_sheet(rows: list[dict[str, str]], out_path: Path) -> None:
    tile = 245
    gap = 16
    label_h = 42
    cols = 4
    cell_w = tile * 2 + gap
    cell_h = tile + label_h
    sheet = Image.new("RGB", (cols * cell_w, math.ceil(len(rows) / cols) * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    for pos, row in enumerate(rows):
        x = (pos % cols) * cell_w
        y = (pos // cols) * cell_h
        full = Image.open(row["normalized"]).convert("RGB")
        frame = Image.open(row["design_preview"]).convert("RGB")
        full.thumbnail((tile, tile), Image.Resampling.LANCZOS)
        frame.thumbnail((tile, tile), Image.Resampling.LANCZOS)
        sheet.paste(full, (x + (tile - full.width) // 2, y + 4 + (tile - full.height) // 2))
        sheet.paste(frame, (x + tile + gap + (tile - frame.width) // 2, y + 4 + (tile - frame.height) // 2))
        draw.text((x + 8, y + tile + 8), f"{int(row['index']):02d} {row['product_id']}", font=SMALL_FONT, fill=(28, 32, 36))
    sheet.save(out_path, quality=94)


def write_readme() -> None:
    readme = OUT / "README.md"
    readme.write_text(
        """# Excitat 41 Frame Extraction

This folder contains extracted frame layers from the 41 first main images.

Outputs:

- `normalized_full/`: the 41 first main images normalized to 1200 x 1200.
- `strict_edge_layers/`: transparent PNG layers preserving only the outer edge bands and top-right brand zone.
- `design_frame_layers/`: transparent PNG layers preserving the frame plus design modules such as brand tab, bottom bar, side panels, proof boxes, and expressive corners.
- `masks/`: alpha masks used for the design frame extraction.
- `previews/`: checkerboard previews for transparent PNG review.
- `contact_sheets/strict_edge_layers_sheet.jpg`: quick review of strict border extraction.
- `contact_sheets/design_frame_layers_sheet.jpg`: quick review of design frame extraction.
- `contact_sheets/source_vs_design_frame_sheet.jpg`: source image next to extracted design frame.
- `frame_extract_manifest.csv`: source path and output path manifest.

Method:

The extraction is region-based, not a semantic inpainting model. It is designed
to isolate the reusable visual frame language from the references: outer sleeve,
brand tab, expressive corners, side/bottom modules, and technical/ornamental
edge details. Some product pixels remain when the original product overlaps the
frame zone. That is useful for studying collision behavior, but these PNGs
should be treated as reference layers, not final reusable commercial assets.
""",
        encoding="utf-8",
    )


def main() -> None:
    sources = list_first_main_images()
    if len(sources) != 41:
        raise SystemExit(f"Expected 41 first main images, found {len(sources)}")

    for sub in [
        "normalized_full",
        "strict_edge_layers",
        "design_frame_layers",
        "masks",
        "previews/strict_edge",
        "previews/design_frame",
        "contact_sheets",
    ]:
        ensure(OUT / sub)

    manifest_rows: list[dict[str, str]] = []
    strict_items: list[tuple[str, Path]] = []
    design_items: list[tuple[str, Path]] = []

    for item in sources:
        label = f"{item.index:02d}_{item.product_id}"
        full = normalize_square(item.source)
        strict_mask = strict_edge_mask(item.index)
        design_mask = design_frame_mask(item.index)
        strict_layer = apply_mask(full, strict_mask)
        design_layer = apply_mask(full, design_mask)

        full_path = OUT / "normalized_full" / f"{label}.png"
        strict_path = OUT / "strict_edge_layers" / f"{label}_strict_edge.png"
        design_path = OUT / "design_frame_layers" / f"{label}_design_frame.png"
        mask_path = OUT / "masks" / f"{label}_design_mask.png"
        strict_preview = OUT / "previews/strict_edge" / f"{label}_strict_edge_preview.jpg"
        design_preview = OUT / "previews/design_frame" / f"{label}_design_frame_preview.jpg"

        full.save(full_path)
        strict_layer.save(strict_path)
        design_layer.save(design_path)
        design_mask.save(mask_path)
        preview_on_checker(strict_layer).save(strict_preview, quality=94)
        preview_on_checker(design_layer).save(design_preview, quality=94)

        strict_items.append((f"{item.index:02d} {item.product_id}", strict_preview))
        design_items.append((f"{item.index:02d} {item.product_id}", design_preview))
        manifest_rows.append(
            {
                "index": str(item.index),
                "product_id": item.product_id,
                "source": str(item.source.relative_to(ROOT)),
                "normalized": str(full_path),
                "strict_edge_layer": str(strict_path),
                "design_frame_layer": str(design_path),
                "design_mask": str(mask_path),
                "strict_preview": str(strict_preview),
                "design_preview": str(design_preview),
            }
        )

    make_contact_sheet(strict_items, OUT / "contact_sheets/strict_edge_layers_sheet.jpg")
    make_contact_sheet(design_items, OUT / "contact_sheets/design_frame_layers_sheet.jpg")
    make_source_vs_frame_sheet(manifest_rows, OUT / "contact_sheets/source_vs_design_frame_sheet.jpg")

    manifest_path = OUT / "frame_extract_manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(manifest_rows[0].keys()))
        writer.writeheader()
        writer.writerows(manifest_rows)
    (OUT / "frame_extract_manifest.json").write_text(json.dumps(manifest_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme()

    print(f"Extracted {len(sources)} frame layers")
    print(OUT)


if __name__ == "__main__":
    main()
