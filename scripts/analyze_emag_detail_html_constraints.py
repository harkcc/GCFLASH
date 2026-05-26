#!/usr/bin/env python3
"""Extract style/layout constraint signals from saved eMAG detail HTML samples."""

from __future__ import annotations

import json
import pathlib
import re
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urlparse


ROOT = pathlib.Path("/Users/cc/Desktop/photo_show/output/emag_detail_html_live_batch")


class DetailParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tag_counter: Counter[str] = Counter()
        self.style_counter: Counter[str] = Counter()
        self.host_counter: Counter[str] = Counter()
        self.width_counter: Counter[str] = Counter()
        self.gif_count = 0
        self.image_count = 0
        self.images_with_width_1140 = 0
        self.centered_nodes = 0
        self.fixed_1140_nodes = 0
        self.has_table = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        self.tag_counter[tag] += 1

        style = attrs_dict.get("style") or ""
        if style:
            self.style_counter[style] += 1
            flat_style = style.replace(" ", "").lower()
            if "text-align:center" in flat_style:
                self.centered_nodes += 1
            if "1140px" in style:
                self.fixed_1140_nodes += 1
            for value in re.findall(r"width\s*:\s*([0-9.]+px)", style, flags=re.I):
                self.width_counter[value] += 1

        width_attr = attrs_dict.get("width")
        if width_attr is not None:
            self.width_counter[str(width_attr)] += 1

        if tag.lower() == "table":
            self.has_table = True

        if tag.lower() != "img":
            return

        self.image_count += 1
        src = attrs_dict.get("src") or ""
        if src:
            host = urlparse(src).hostname
            if host:
                self.host_counter[host] += 1
        if ".gif" in src.lower():
            self.gif_count += 1
        width_ref = str(width_attr or "")
        style_width_1140 = "1140px" in style
        attr_width_1140 = width_ref == "1140"
        if style_width_1140 or attr_width_1140:
            self.images_with_width_1140 += 1


def analyze() -> dict:
    html_files = sorted(ROOT.glob("*.inner.html"))
    if not html_files:
        raise SystemExit(f"No .inner.html files found under {ROOT}")

    aggregate_tags: Counter[str] = Counter()
    aggregate_styles: Counter[str] = Counter()
    aggregate_hosts: Counter[str] = Counter()
    aggregate_widths: Counter[str] = Counter()

    product_rows: list[dict] = []

    for path in html_files:
        parser = DetailParser()
        parser.feed(path.read_text("utf-8", errors="ignore"))
        aggregate_tags.update(parser.tag_counter)
        aggregate_styles.update(parser.style_counter)
        aggregate_hosts.update(parser.host_counter)
        aggregate_widths.update(parser.width_counter)

        product_rows.append(
            {
                "productId": path.stem.replace(".inner", ""),
                "imageCount": parser.image_count,
                "gifCount": parser.gif_count,
                "hasTable": parser.has_table,
                "centeredNodes": parser.centered_nodes,
                "fixed1140Nodes": parser.fixed_1140_nodes,
                "imagesWithWidth1140": parser.images_with_width_1140,
            }
        )

    product_count = len(product_rows)
    products_with_gif = sum(1 for row in product_rows if row["gifCount"] > 0)
    products_with_table = sum(1 for row in product_rows if row["hasTable"])
    total_images = sum(row["imageCount"] for row in product_rows)
    image_width_1140_count = sum(row["imagesWithWidth1140"] for row in product_rows)

    summary = {
        "root": str(ROOT),
        "sampleCount": product_count,
        "productsWithGif": products_with_gif,
        "productsWithTable": products_with_table,
        "totalGifCount": sum(row["gifCount"] for row in product_rows),
        "totalImageCount": total_images,
        "imagesWithWidth1140": image_width_1140_count,
        "imagesWithWidth1140Pct": round((image_width_1140_count / total_images) * 100, 2) if total_images else 0,
        "avgCenteredNodes": round(sum(row["centeredNodes"] for row in product_rows) / product_count, 2),
        "avgFixed1140Nodes": round(sum(row["fixed1140Nodes"] for row in product_rows) / product_count, 2),
        "topTags": aggregate_tags.most_common(20),
        "topStyles": aggregate_styles.most_common(20),
        "topWidths": aggregate_widths.most_common(20),
        "topHosts": aggregate_hosts.most_common(10),
        "topFixed1140Products": sorted(product_rows, key=lambda row: row["fixed1140Nodes"], reverse=True)[:10],
        "products": product_rows,
    }
    return summary


def write_outputs(summary: dict) -> None:
    json_path = ROOT / "constraints_summary.json"
    md_path = ROOT / "constraints_summary.md"

    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# eMAG Detail HTML Constraint Signals",
        "",
        f"- Sample count: {summary['sampleCount']}",
        f"- Products with GIF: {summary['productsWithGif']} / {summary['sampleCount']}",
        f"- Total GIF count: {summary['totalGifCount']}",
        f"- Products with table: {summary['productsWithTable']} / {summary['sampleCount']}",
        f"- Total image count: {summary['totalImageCount']}",
        f"- Images rendered with width `1140` / `1140px`: {summary['imagesWithWidth1140']}",
        f"- Share of images rendered at `1140`: {summary['imagesWithWidth1140Pct']}%",
        f"- Avg centered nodes per product: {summary['avgCenteredNodes']}",
        f"- Avg nodes containing `1140px` per product: {summary['avgFixed1140Nodes']}",
        "",
        "## Top widths",
    ]
    lines.extend(f"- `{value}`: {count}" for value, count in summary["topWidths"][:12])
    lines.extend(["", "## Top inline styles"])
    lines.extend(f"- `{value}`: {count}" for value, count in summary["topStyles"][:12])
    lines.extend(["", "## Top image hosts"])
    lines.extend(f"- `{host}`: {count}" for host, count in summary["topHosts"])
    lines.extend(["", "## Top `1140px` products"])
    for row in summary["topFixed1140Products"][:8]:
        lines.append(
            f"- `{row['productId']}`: fixed1140={row['fixed1140Nodes']}, centered={row['centeredNodes']}, "
            f"gif={row['gifCount']}, table={row['hasTable']}"
        )

    md_path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    write_outputs(analyze())
