#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
NORM = ROOT / "experiments/20260522_excitat_41_frame_extract/normalized_full"
OUT = ROOT / "experiments/20260522_logo_ratio_analysis"
SIZE = 1200


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


TITLE = font(18, True)
SMALL = font(13)


def non_white_bbox(crop: Image.Image) -> tuple[int, int, int, int] | None:
    # This is a deliberately simple measurement helper. It finds the dominant
    # non-white content in the top-right crop, then trims edge-only border lines.
    pix = crop.convert("RGB").load()
    w, h = crop.size
    points: list[tuple[int, int]] = []
    for y in range(h):
        for x in range(w):
            r, g, b = pix[x, y]
            if max(r, g, b) < 244 and (max(r, g, b) - min(r, g, b) > 12 or min(r, g, b) < 210):
                points.append((x, y))
    if not points:
        return None

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)

    # Trim very long one-pixel-ish border rails from the detected bbox.
    while y0 < y1:
        row_count = sum(1 for x in range(x0, x1 + 1) if pix[x, y0] != (255, 255, 255))
        if row_count > (x1 - x0 + 1) * 0.62 and y0 < 18:
            y0 += 1
        else:
            break
    while x1 > x0:
        col_count = sum(1 for y in range(y0, y1 + 1) if pix[x1, y] != (255, 255, 255))
        if col_count > (y1 - y0 + 1) * 0.72 and x1 > w - 18:
            x1 -= 1
        else:
            break
    return x0, y0, x1, y1


def main() -> None:
    ensure(OUT / "logo_crops")
    rows: list[dict[str, object]] = []
    files = sorted(NORM.glob("*.jpg")) + sorted(NORM.glob("*.png"))
    if not files:
        raise SystemExit(f"No normalized sources found in {NORM}")

    crop_box = (600, 0, SIZE, 190)
    for path in files:
        img = Image.open(path).convert("RGB")
        crop = img.crop(crop_box)
        bbox = non_white_bbox(crop)
        draw_crop = crop.copy()
        d = ImageDraw.Draw(draw_crop)
        if bbox:
            d.rectangle(bbox, outline=(255, 0, 0), width=3)
            x0, y0, x1, y1 = bbox
            full_bbox = (crop_box[0] + x0, crop_box[1] + y0, crop_box[0] + x1, crop_box[1] + y1)
            width = full_bbox[2] - full_bbox[0] + 1
            height = full_bbox[3] - full_bbox[1] + 1
        else:
            full_bbox = None
            width = 0
            height = 0
        label = path.stem.split("_", 1)[0]
        out_crop = OUT / "logo_crops" / f"{label}_top_right_crop.jpg"
        draw_crop.save(out_crop, quality=94)
        rows.append(
            {
                "id": label,
                "source": str(path),
                "crop": str(out_crop),
                "bbox": full_bbox,
                "width_px": width,
                "height_px": height,
                "width_pct": round(width / SIZE, 4),
                "height_pct": round(height / SIZE, 4),
            }
        )

    with (OUT / "logo_ratio_manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    (OUT / "logo_ratio_manifest.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    tile_w, tile_h = 300, 130
    label_h = 34
    cols = 4
    sheet = Image.new("RGB", (cols * tile_w, ((len(rows) + cols - 1) // cols) * (tile_h + label_h)), "white")
    d = ImageDraw.Draw(sheet)
    for i, row in enumerate(rows):
        x = (i % cols) * tile_w
        y = (i // cols) * (tile_h + label_h)
        crop = Image.open(row["crop"]).convert("RGB")
        crop.thumbnail((tile_w - 12, tile_h - 8), Image.Resampling.LANCZOS)
        sheet.paste(crop, (x + (tile_w - crop.width) // 2, y + 4))
        d.text(
            (x + 8, y + tile_h + 4),
            f"{row['id']} h {row['height_pct']:.1%} w {row['width_pct']:.1%}",
            font=SMALL,
            fill=(25, 30, 36),
        )
    sheet.save(OUT / "logo_crops_sheet.jpg", quality=94)

    valid = [row for row in rows if row["height_px"]]
    heights = sorted(float(row["height_pct"]) for row in valid)
    widths = sorted(float(row["width_pct"]) for row in valid)
    summary = {
        "count": len(rows),
        "valid": len(valid),
        "median_height_pct": heights[len(heights) // 2] if heights else None,
        "median_width_pct": widths[len(widths) // 2] if widths else None,
        "recommended_logo_height_pct": [0.04, 0.07],
        "recommended_logo_width_pct": [0.18, 0.26],
        "recommended_1024_box": {"x": [760, 1012], "y": [8, 74]},
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUT / "logo_crops_sheet.jpg")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
