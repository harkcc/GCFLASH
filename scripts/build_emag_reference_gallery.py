#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path("references/user_cases/20260521_emag_cangswjp")
PRODUCTS_DIR = ROOT / "products"
CONTACT_DIR = ROOT / "contact_sheets"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_products() -> list[tuple[Path, dict]]:
    products: list[tuple[Path, dict]] = []
    for meta_path in sorted(PRODUCTS_DIR.glob("*/product_meta.json")):
        data = json.loads(meta_path.read_text())
        products.append((meta_path.parent, data))
    return products


def local_image_paths(product_dir: Path, data: dict, key: str) -> list[Path]:
    paths = []
    for image in data.get(key, []):
        local_path = image.get("localPath")
        if local_path:
            paths.append(ROOT / local_path)
    return paths


def render_contact_sheet(
    items: list[tuple[str, Path]],
    output_path: Path,
    *,
    columns: int = 5,
    thumb_w: int = 210,
    thumb_h: int = 210,
    label_h: int = 42,
    bg: str = "white",
) -> None:
    if not items:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = math.ceil(len(items) / columns)
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), bg)
    draw = ImageDraw.Draw(sheet)

    for index, (label, image_path) in enumerate(items):
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception:
            continue
        image.thumbnail((thumb_w - 12, thumb_h - 12), Image.LANCZOS)
        col = index % columns
        row = index // columns
        x = col * thumb_w + (thumb_w - image.width) // 2
        y = row * (thumb_h + label_h) + (thumb_h - image.height) // 2
        sheet.paste(image, (x, y))
        text_x = col * thumb_w + 8
        text_y = row * (thumb_h + label_h) + thumb_h + 4
        draw.text((text_x, text_y), label[:34], fill=(24, 24, 24))

    sheet.save(output_path, quality=92)


def write_manifest(products: list[tuple[Path, dict]]) -> None:
    manifest_path = ROOT / "image_manifest.csv"
    with manifest_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "product_index",
                "product_id",
                "role",
                "image_index",
                "local_path",
                "source_url",
                "width",
                "height",
                "bytes",
                "title",
            ],
        )
        writer.writeheader()
        for product_index, (product_dir, data) in enumerate(products, start=1):
            for role, key in [("main_gallery", "galleryImages"), ("detail_image", "detailImages")]:
                for image_index, image in enumerate(data.get(key, []), start=1):
                    writer.writerow(
                        {
                            "product_index": product_index,
                            "product_id": data.get("productId", ""),
                            "role": role,
                            "image_index": image_index,
                            "local_path": image.get("localPath", ""),
                            "source_url": image.get("sourceUrl", ""),
                            "width": image.get("naturalWidth", ""),
                            "height": image.get("naturalHeight", ""),
                            "bytes": image.get("bytes", ""),
                            "title": data.get("h1") or data.get("listingTitle", ""),
                        }
                    )


def build_contact_sheets(products: list[tuple[Path, dict]]) -> None:
    CONTACT_DIR.mkdir(parents=True, exist_ok=True)

    all_gallery: list[tuple[str, Path]] = []
    all_detail: list[tuple[str, Path]] = []
    first_images: list[tuple[str, Path]] = []

    for product_index, (product_dir, data) in enumerate(products, start=1):
        product_id = data.get("productId", f"{product_index:02d}")
        gallery_paths = local_image_paths(product_dir, data, "galleryImages")
        detail_paths = local_image_paths(product_dir, data, "detailImages")

        product_items = [
            (f"{product_id} G{idx:02d}", image_path)
            for idx, image_path in enumerate(gallery_paths, start=1)
        ] + [
            (f"{product_id} D{idx:02d}", image_path)
            for idx, image_path in enumerate(detail_paths, start=1)
        ]
        render_contact_sheet(
            product_items,
            product_dir / "contact_sheet.jpg",
            columns=5,
            thumb_w=220,
            thumb_h=220,
            label_h=38,
        )

        all_gallery.extend(
            (f"{product_index:02d} {product_id} G{idx:02d}", image_path)
            for idx, image_path in enumerate(gallery_paths, start=1)
        )
        all_detail.extend(
            (f"{product_index:02d} {product_id} D{idx:02d}", image_path)
            for idx, image_path in enumerate(detail_paths, start=1)
        )
        if gallery_paths:
            first_images.append((f"{product_index:02d} {product_id}", gallery_paths[0]))

    render_contact_sheet(
        first_images,
        CONTACT_DIR / "all_products_first_main_image.jpg",
        columns=6,
        thumb_w=210,
        thumb_h=210,
        label_h=38,
    )

    for page_index, start in enumerate(range(0, len(all_gallery), 60), start=1):
        render_contact_sheet(
            all_gallery[start : start + 60],
            CONTACT_DIR / f"all_main_gallery_page_{page_index:02d}.jpg",
            columns=6,
            thumb_w=200,
            thumb_h=200,
            label_h=36,
        )

    for page_index, start in enumerate(range(0, len(all_detail), 48), start=1):
        render_contact_sheet(
            all_detail[start : start + 48],
            CONTACT_DIR / f"all_detail_images_page_{page_index:02d}.jpg",
            columns=4,
            thumb_w=240,
            thumb_h=260,
            label_h=36,
        )


def write_html(products: list[tuple[Path, dict]]) -> None:
    total_gallery = sum(len(data.get("galleryImages", [])) for _, data in products)
    total_detail = sum(len(data.get("detailImages", [])) for _, data in products)
    rows = []

    for product_index, (product_dir, data) in enumerate(products, start=1):
        title = data.get("h1") or data.get("listingTitle") or ""
        product_id = data.get("productId", "")
        gallery_count = len(data.get("galleryImages", []))
        detail_count = len(data.get("detailImages", []))
        contact_sheet = product_dir / "contact_sheet.jpg"
        rows.append(
            f"""
            <section class="product">
              <h2>{product_index:02d}. {html.escape(product_id)} <span>{html.escape(title)}</span></h2>
              <p><a href="{html.escape(data.get('productUrl', '#'))}">eMAG page</a> |
                 gallery {gallery_count} | detail {detail_count} |
                 <a href="{html.escape(rel(product_dir / 'product_meta.json'))}">metadata</a></p>
              <a href="{html.escape(rel(contact_sheet))}"><img src="{html.escape(rel(contact_sheet))}" loading="lazy"></a>
            </section>
            """
        )

    html_doc = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>eMAG Cangswjp / Excitat reference gallery</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #172033; background: #f5f6f8; }}
    header {{ padding: 28px 32px; background: #172033; color: white; }}
    main {{ padding: 24px 32px 48px; max-width: 1320px; margin: 0 auto; }}
    h1 {{ margin: 0 0 8px; font-size: 26px; }}
    h2 {{ font-size: 18px; margin: 0 0 8px; }}
    h2 span {{ display: block; margin-top: 4px; font-size: 14px; font-weight: 500; color: #4c5b70; }}
    a {{ color: #006bcf; }}
    .overview, .product {{ background: white; border: 1px solid #d8dee8; border-radius: 8px; padding: 16px; margin-bottom: 18px; }}
    .overview img, .product img {{ width: 100%; max-width: 1260px; height: auto; display: block; border: 1px solid #e1e5ec; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }}
    .grid a {{ display: block; padding: 10px 12px; background: #eef3f8; border-radius: 6px; text-decoration: none; }}
    p {{ margin: 0 0 12px; line-height: 1.5; }}
  </style>
</head>
<body>
  <header>
    <h1>eMAG Cangswjp / Excitat reference gallery</h1>
    <p>41 products, {total_gallery} platform gallery images, {total_detail} description/detail images.</p>
  </header>
  <main>
    <section class="overview">
      <h2>All products: first main image</h2>
      <a href="contact_sheets/all_products_first_main_image.jpg"><img src="contact_sheets/all_products_first_main_image.jpg"></a>
    </section>
    <section class="overview">
      <h2>Full contact sheets</h2>
      <div class="grid">
        {"".join(f'<a href="{p.as_posix()}">{p.name}</a>' for p in sorted(Path("contact_sheets").glob("all_*.jpg")))}
      </div>
    </section>
    {"".join(rows)}
  </main>
</body>
</html>
"""
    (ROOT / "index.html").write_text(html_doc)


def main() -> None:
    products = load_products()
    write_manifest(products)
    build_contact_sheets(products)
    write_html(products)
    print(f"products={len(products)}")
    print(f"index={ROOT / 'index.html'}")
    print(f"manifest={ROOT / 'image_manifest.csv'}")


if __name__ == "__main__":
    main()
