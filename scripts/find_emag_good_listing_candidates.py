#!/usr/bin/env python3
"""Rank saved eMAG detail HTML captures for visual/template scouting."""

from __future__ import annotations

import argparse
import html
import json
import pathlib
from html.parser import HTMLParser
from urllib.parse import urlparse


DEFAULT_ROOT = pathlib.Path("/Users/cc/Desktop/photo_show/output/emag_detail_html_live_batch")
DEFAULT_OUT = pathlib.Path("/Users/cc/Desktop/photo_show/research/2026-05-23_emag_good_listing_candidates.md")
DEFAULT_HTML_OUT = pathlib.Path("/Users/cc/Desktop/photo_show/research/2026-05-23_emag_good_listing_candidates.html")


class TagCounter(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: dict[str, int] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags[tag.lower()] = self.tags.get(tag.lower(), 0) + 1


def load_meta_files(root: pathlib.Path) -> list[pathlib.Path]:
    files = sorted(root.glob("*.meta.json"))
    return [path for path in files if path.name not in {"summary.meta.json"}]


def score_range(value: int | float, low: int | float, high: int | float, peak: int | float) -> float:
    if low <= value <= high:
        distance = abs(value - peak) / max(peak - low, high - peak, 1)
        return max(0.5, 1 - distance * 0.35)
    if value < low:
        return max(0, value / max(low, 1) * 0.5)
    return max(0, 1 - ((value - high) / max(high, 1)))


def image_shape_mix(images: list[dict]) -> tuple[float, list[str]]:
    buckets: set[str] = set()
    valid = 0
    for image in images:
        width = image.get("naturalWidth") or image.get("width") or 0
        height = image.get("naturalHeight") or image.get("height") or 0
        if width <= 0 or height <= 0:
            continue
        valid += 1
        ratio = width / height
        if ratio >= 1.55:
            buckets.add("wide")
        elif ratio <= 0.75:
            buckets.add("tall")
        else:
            buckets.add("square")
    if not valid:
        return 0, []
    return min(len(buckets) / 3, 1), sorted(buckets)


def full_width_rate(images: list[dict]) -> float:
    if not images:
        return 0
    full = sum(1 for image in images if (image.get("width") or 0) >= 360)
    return full / len(images)


def host_profile(images: list[dict]) -> dict[str, int]:
    hosts: dict[str, int] = {}
    for image in images:
        src = image.get("src") or ""
        host = urlparse(src).hostname or "(unknown)"
        hosts[host] = hosts.get(host, 0) + 1
    return dict(sorted(hosts.items(), key=lambda item: item[1], reverse=True))


def count_gifs(images: list[dict]) -> int:
    return sum(1 for image in images if ".gif" in (image.get("src") or "").lower())


def parse_tags(root: pathlib.Path, product_id: str) -> dict[str, int]:
    html_path = root / f"{product_id}.inner.html"
    if not html_path.exists():
        return {}
    parser = TagCounter()
    parser.feed(html_path.read_text("utf-8", errors="ignore"))
    return parser.tags


def score_candidate(root: pathlib.Path, meta: dict) -> dict:
    product_id = meta["productId"]
    images = meta.get("images") or []
    tags = parse_tags(root, product_id)
    image_count = int(meta.get("imageCount") or 0)
    heading_count = int(meta.get("headingCount") or 0)
    paragraph_count = int(meta.get("paragraphCount") or 0)
    list_count = int(meta.get("listCount") or 0)
    table_count = int(meta.get("tableCount") or 0)
    text_length = int(meta.get("textLength") or 0)
    max_images_per_row = int(meta.get("maxImagesPerRow") or 0)
    gif_count = count_gifs(images)
    shape_score, shapes = image_shape_mix(images)
    full_rate = full_width_rate(images)

    score = 0.0
    reasons: list[str] = []
    risks: list[str] = []

    score += score_range(image_count, 6, 14, 10) * 18
    if 6 <= image_count <= 14:
        reasons.append(f"{image_count} images gives enough visual material without becoming extreme")

    score += score_range(heading_count, 4, 18, 8) * 14
    if heading_count >= 4:
        reasons.append(f"{heading_count} headings suggest modular structure")

    score += score_range(text_length, 1800, 5200, 3200) * 14
    if 1800 <= text_length <= 5200:
        reasons.append(f"{text_length} chars is substantial but still readable")

    score += min(paragraph_count / 24, 1) * 8
    score += min(list_count / 3, 1) * 8
    if list_count:
        reasons.append(f"{list_count} list block(s) can support specs or package modules")

    if max_images_per_row == 1:
        score += 14
        reasons.append("mobile capture stays single-column")
    else:
        risks.append(f"mobile capture has {max_images_per_row} images in one row")

    score += shape_score * 8
    if shapes:
        reasons.append(f"image rhythm includes {', '.join(shapes)} assets")

    score += full_rate * 6
    if full_rate >= 0.8:
        reasons.append("most images occupy the mobile column cleanly")

    if 1 <= table_count <= 3:
        score += 4
        reasons.append(f"{table_count} table(s) may be useful for specs")
    elif table_count > 5:
        score -= 5
        risks.append(f"{table_count} tables may be too heavy on mobile")

    if gif_count:
        score += min(gif_count, 3) * 2
        reasons.append(f"{gif_count} GIF asset(s) show motion/proof potential")

    if image_count < 5:
        risks.append("too few images for a rich detail template")
    if heading_count > 24:
        risks.append("too many headings may indicate fragmented imported markup")
    if text_length > 6500:
        risks.append("description may be too long for a clean mobile template")
    if tags.get("button", 0) or tags.get("span", 0):
        risks.append("contains editor/platform residue tags")

    return {
        "productId": product_id,
        "score": round(score, 1),
        "title": meta.get("listingTitle") or meta.get("title") or "",
        "url": meta.get("productUrl") or meta.get("url") or "",
        "previewImages": [
            {
                "src": image.get("src") or "",
                "alt": image.get("alt") or "",
                "width": image.get("width") or 0,
                "height": image.get("height") or 0,
            }
            for image in images[:6]
        ],
        "metrics": {
            "imageCount": image_count,
            "gifCount": gif_count,
            "headingCount": heading_count,
            "paragraphCount": paragraph_count,
            "listCount": list_count,
            "tableCount": table_count,
            "textLength": text_length,
            "maxImagesPerRow": max_images_per_row,
            "imageShapes": shapes,
            "fullWidthImageRate": round(full_rate, 2),
            "topHosts": host_profile(images),
        },
        "reasons": reasons[:6],
        "risks": risks,
    }


def build_report(root: pathlib.Path) -> dict:
    rows = []
    for path in load_meta_files(root):
        meta = json.loads(path.read_text("utf-8"))
        if meta.get("found"):
            rows.append(score_candidate(root, meta))
    rows.sort(key=lambda row: row["score"], reverse=True)
    return {
        "root": str(root),
        "candidateCount": len(rows),
        "rankingMethod": "mobile-first structure score from saved eMAG detail HTML captures",
        "candidates": rows,
    }


def write_markdown(report: dict, out_path: pathlib.Path, top: int) -> None:
    lines = [
        "# eMAG Good-Looking Detail Listing Candidates",
        "",
        "This is a scouting shortlist from saved live detail HTML. It ranks candidates for manual visual review; it is not a final aesthetic judgment.",
        "",
        f"- Source root: `{report['root']}`",
        f"- Candidates scored: `{report['candidateCount']}`",
        "- Priority: mobile single-column fit, modular rhythm, enough images, readable text depth, lists/spec structure, accepted GIF motion assets.",
        "",
        "## Top Candidates",
        "",
    ]
    for index, row in enumerate(report["candidates"][:top], start=1):
        metrics = row["metrics"]
        lines.extend(
            [
                f"### {index}. `{row['productId']}` - score {row['score']}",
                "",
                f"- Title: {row['title']}",
                f"- URL: {row['url']}",
                (
                    "- Metrics: "
                    f"images={metrics['imageCount']}, gifs={metrics['gifCount']}, headings={metrics['headingCount']}, "
                    f"paragraphs={metrics['paragraphCount']}, lists={metrics['listCount']}, tables={metrics['tableCount']}, "
                    f"text={metrics['textLength']}, maxImagesPerRow={metrics['maxImagesPerRow']}"
                ),
                f"- Image shapes: {', '.join(metrics['imageShapes']) if metrics['imageShapes'] else 'unknown'}",
                f"- Top hosts: {', '.join(f'{host}({count})' for host, count in list(metrics['topHosts'].items())[:3])}",
                "- Why inspect: " + "; ".join(row["reasons"]),
                "- Risks: " + ("; ".join(row["risks"]) if row["risks"] else "none flagged by structure score"),
                "",
            ]
        )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_html(report: dict, out_path: pathlib.Path, top: int) -> None:
    cards = []
    for index, row in enumerate(report["candidates"][:top], start=1):
        metrics = row["metrics"]
        images = "\n".join(
            f'<img src="{html.escape(image["src"])}" alt="{html.escape(image["alt"])}" loading="lazy">'
            for image in row["previewImages"]
            if image["src"]
        )
        reasons = "".join(f"<li>{html.escape(reason)}</li>" for reason in row["reasons"])
        risks = "".join(f"<li>{html.escape(risk)}</li>" for risk in row["risks"]) or "<li>No structural risk flagged.</li>"
        cards.append(
            f"""
            <article class="candidate">
              <div class="rank">#{index}</div>
              <div class="meta">
                <a class="product-link" href="{html.escape(row['url'])}" target="_blank" rel="noreferrer">{html.escape(row['productId'])}</a>
                <h2>{html.escape(row['title'])}</h2>
                <div class="score">{row['score']}</div>
                <p class="metrics">images {metrics['imageCount']} · gifs {metrics['gifCount']} · headings {metrics['headingCount']} · lists {metrics['listCount']} · tables {metrics['tableCount']} · text {metrics['textLength']} · row {metrics['maxImagesPerRow']}</p>
              </div>
              <div class="image-strip">{images}</div>
              <div class="notes">
                <section><h3>Why inspect</h3><ul>{reasons}</ul></section>
                <section><h3>Risks</h3><ul>{risks}</ul></section>
              </div>
            </article>
            """
        )

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>eMAG Detail Listing Candidates</title>
  <style>
    :root {{
      --ink: #1f2428;
      --muted: #66707a;
      --line: #d9dee3;
      --paper: #f6f8f7;
      --accent: #0b6bcb;
      --good: #0d7a53;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Avenir Next, Helvetica, Arial, sans-serif;
      color: var(--ink);
      background: var(--paper);
    }}
    header {{
      padding: 28px 24px 18px;
      border-bottom: 1px solid var(--line);
      background: #fff;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
      line-height: 1.15;
      letter-spacing: 0;
    }}
    header p {{
      margin: 0;
      max-width: 920px;
      color: var(--muted);
      line-height: 1.5;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 22px;
    }}
    .candidate {{
      display: grid;
      grid-template-columns: 52px minmax(220px, 1fr);
      gap: 14px;
      padding: 18px 0 22px;
      border-bottom: 1px solid var(--line);
      background: transparent;
    }}
    .rank {{
      width: 44px;
      height: 44px;
      display: grid;
      place-items: center;
      border: 1px solid var(--line);
      color: var(--accent);
      font-weight: 700;
      background: #fff;
    }}
    .meta {{
      position: relative;
      min-width: 0;
      padding-right: 90px;
    }}
    .product-link {{
      color: var(--accent);
      font-weight: 700;
      text-decoration: none;
    }}
    h2 {{
      margin: 6px 0 10px;
      font-size: 18px;
      line-height: 1.28;
      letter-spacing: 0;
    }}
    .score {{
      position: absolute;
      top: 0;
      right: 0;
      width: 72px;
      height: 44px;
      display: grid;
      place-items: center;
      color: #fff;
      background: var(--good);
      font-weight: 800;
    }}
    .metrics {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }}
    .image-strip {{
      grid-column: 2;
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 8px;
      overflow: hidden;
    }}
    .image-strip img {{
      width: 100%;
      aspect-ratio: 1 / 1;
      object-fit: cover;
      border: 1px solid var(--line);
      background: #fff;
    }}
    .notes {{
      grid-column: 2;
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 18px;
      margin-top: 2px;
    }}
    h3 {{
      margin: 0 0 6px;
      font-size: 13px;
      text-transform: uppercase;
      color: var(--muted);
      letter-spacing: .04em;
    }}
    ul {{
      margin: 0;
      padding-left: 18px;
      line-height: 1.45;
      font-size: 14px;
    }}
    @media (max-width: 720px) {{
      header {{ padding: 22px 16px 14px; }}
      main {{ padding: 14px; }}
      .candidate {{
        grid-template-columns: 1fr;
        gap: 10px;
      }}
      .rank {{ width: 40px; height: 36px; }}
      .meta, .image-strip, .notes {{ grid-column: 1; }}
      .meta {{ padding-right: 0; }}
      .score {{
        position: static;
        width: 64px;
        height: 34px;
        margin: 8px 0;
      }}
      .image-strip {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
      .notes {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>eMAG Detail Listing Candidates</h1>
    <p>Scored from saved live detail HTML captures. Use this as a shortlist for visual review, with mobile single-column behavior and GIF-capable media treated as useful signals.</p>
  </header>
  <main>
    {''.join(cards)}
  </main>
</body>
</html>
"""
    out_path.write_text(document, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=pathlib.Path, default=DEFAULT_ROOT)
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    parser.add_argument("--html-out", type=pathlib.Path, default=DEFAULT_HTML_OUT)
    parser.add_argument("--json-out", type=pathlib.Path, default=None)
    parser.add_argument("--top", type=int, default=12)
    args = parser.parse_args()

    report = build_report(args.root)
    write_markdown(report, args.out, args.top)
    write_html(report, args.html_out, args.top)
    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "out": str(args.out),
                "htmlOut": str(args.html_out),
                "candidateCount": report["candidateCount"],
                "top": report["candidates"][:3],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
