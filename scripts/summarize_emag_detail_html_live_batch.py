#!/usr/bin/env python3
"""Summarize captured eMAG detail HTML samples from the live browser batch."""

from __future__ import annotations

import json
import pathlib
import statistics
from collections import Counter
from urllib.parse import urlparse


ROOT = pathlib.Path("/Users/cc/Desktop/photo_show/output/emag_detail_html_live_batch")


def load_metas() -> list[dict]:
    return [json.loads(path.read_text()) for path in sorted(ROOT.glob("*.meta.json"))]


def median(values: list[float]) -> float:
    return statistics.median(values) if values else 0


def summarize() -> dict:
    metas = load_metas()
    host_counter: Counter[str] = Counter()
    tag_counter: Counter[str] = Counter()
    image_count_dist: Counter[int] = Counter()
    max_row_dist: Counter[int] = Counter()
    list_count_dist: Counter[int] = Counter()
    table_count_dist: Counter[int] = Counter()

    for meta in metas:
        image_count_dist[meta.get("imageCount", 0)] += 1
        max_row_dist[meta.get("maxImagesPerRow", 0)] += 1
        list_count_dist[meta.get("listCount", 0)] += 1
        table_count_dist[meta.get("tableCount", 0)] += 1
        tag_counter.update(meta.get("tags", {}))
        for image in meta.get("images", []):
            host = urlparse(image.get("src", "")).hostname
            if host:
                host_counter[host] += 1

    summary = {
        "root": str(ROOT),
        "sampleCount": len(metas),
        "productIds": [meta["productId"] for meta in metas],
        "metrics": {
            "avgImageCount": round(statistics.mean(meta["imageCount"] for meta in metas), 2),
            "medianImageCount": median([meta["imageCount"] for meta in metas]),
            "minImageCount": min(meta["imageCount"] for meta in metas),
            "maxImageCount": max(meta["imageCount"] for meta in metas),
            "avgTextLength": round(statistics.mean(meta["textLength"] for meta in metas), 2),
            "medianTextLength": median([meta["textLength"] for meta in metas]),
            "minTextLength": min(meta["textLength"] for meta in metas),
            "maxTextLength": max(meta["textLength"] for meta in metas),
            "avgHeadingCount": round(statistics.mean(meta["headingCount"] for meta in metas), 2),
            "avgParagraphCount": round(statistics.mean(meta["paragraphCount"] for meta in metas), 2),
        },
        "imageCountDistribution": dict(sorted(image_count_dist.items())),
        "maxImagesPerRowDistribution": dict(sorted(max_row_dist.items())),
        "listCountDistribution": dict(sorted(list_count_dist.items())),
        "tableCountDistribution": dict(sorted(table_count_dist.items())),
        "topImageHosts": host_counter.most_common(10),
        "topTags": tag_counter.most_common(20),
        "examples": [
            {
                "productId": meta["productId"],
                "imageCount": meta["imageCount"],
                "textLength": meta["textLength"],
                "headingCount": meta["headingCount"],
                "paragraphCount": meta["paragraphCount"],
                "listCount": meta["listCount"],
                "tableCount": meta["tableCount"],
                "maxImagesPerRow": meta["maxImagesPerRow"],
            }
            for meta in metas[:10]
        ],
    }
    return summary


def write_outputs(summary: dict) -> None:
    json_path = ROOT / "summary.json"
    md_path = ROOT / "summary.md"

    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    metrics = summary["metrics"]
    lines = [
        "# eMAG Detail HTML Live Batch Summary",
        "",
        f"- Sample count: {summary['sampleCount']}",
        f"- Avg image count: {metrics['avgImageCount']}",
        f"- Median image count: {metrics['medianImageCount']}",
        f"- Image count range: {metrics['minImageCount']} - {metrics['maxImageCount']}",
        f"- Avg text length: {metrics['avgTextLength']}",
        f"- Median text length: {metrics['medianTextLength']}",
        f"- Text length range: {metrics['minTextLength']} - {metrics['maxTextLength']}",
        f"- Avg heading count: {metrics['avgHeadingCount']}",
        f"- Avg paragraph count: {metrics['avgParagraphCount']}",
        "",
        "## Max images per row",
    ]
    lines.extend(
        f"- {count} image(s) per row: {freq} products"
        for count, freq in summary["maxImagesPerRowDistribution"].items()
    )
    lines.extend(
        [
            "",
            "## Image count distribution",
        ]
    )
    lines.extend(
        f"- {count} images: {freq} products"
        for count, freq in summary["imageCountDistribution"].items()
    )
    lines.extend(
        [
            "",
            "## List count distribution",
        ]
    )
    lines.extend(
        f"- {count} lists: {freq} products"
        for count, freq in summary["listCountDistribution"].items()
    )
    lines.extend(
        [
            "",
            "## Table count distribution",
        ]
    )
    lines.extend(
        f"- {count} tables: {freq} products"
        for count, freq in summary["tableCountDistribution"].items()
    )
    lines.extend(
        [
            "",
            "## Top image hosts",
        ]
    )
    lines.extend(f"- {host}: {count}" for host, count in summary["topImageHosts"])
    lines.extend(
        [
            "",
            "## Top tags",
        ]
    )
    lines.extend(f"- {tag}: {count}" for tag, count in summary["topTags"][:12])

    md_path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    write_outputs(summarize())
