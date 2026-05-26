#!/usr/bin/env python3
"""Minimal validator for eMAG detail HTML snippets."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urlparse


SAFE_TAGS = {"p", "h1", "h2", "h3", "strong", "br", "img", "ul", "li", "table", "tr", "td"}
GRAY_TAGS = {"div", "blockquote", "em", "b", "center", "u"}
EMAG_HOSTS = {"marketplace-static.emag.ro", "s13emagst.akamaized.net"}
BANNED_PATTERNS = {
    "promo_buy_now": re.compile(r"\b(buy now|shop now|get yours now|limited offer|special offer)\b", re.I),
    "shipping": re.compile(r"\b(free shipping|shipping|delivery)\b", re.I),
    "warranty": re.compile(r"\b(warranty|guarantee)\b", re.I),
    "contact": re.compile(r"\b(email|e-mail|phone|whatsapp|contact us|www\.)\b", re.I),
    "price": re.compile(r"(\$|€|£|\bprice\b|\bcheap\b|\bdiscount\b)", re.I),
}


class DetailValidator(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tag_counter: Counter[str] = Counter()
        self.unknown_tags: Counter[str] = Counter()
        self.gray_tags: Counter[str] = Counter()
        self.image_hosts: Counter[str] = Counter()
        self.gif_images = 0
        self.images = 0
        self.tables = 0
        self.center_styles = 0
        self.inline_styles = 0
        self.desktop_width_images = 0
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        tag = tag.lower()
        self.tag_counter[tag] += 1

        if tag in GRAY_TAGS:
            self.gray_tags[tag] += 1
        elif tag not in SAFE_TAGS:
            self.unknown_tags[tag] += 1

        style = attrs_dict.get("style") or ""
        if style:
            self.inline_styles += 1
            if "text-align:center" in style.replace(" ", "").lower():
                self.center_styles += 1

        if tag == "table":
            self.tables += 1

        if tag != "img":
            return

        self.images += 1
        src = attrs_dict.get("src") or ""
        if src:
            host = urlparse(src).hostname or "(unknown)"
            self.image_hosts[host] += 1
        if ".gif" in src.lower():
            self.gif_images += 1
        width_attr = (attrs_dict.get("width") or "").strip()
        if width_attr.isdigit() and int(width_attr) > 800:
            self.desktop_width_images += 1
        if "1140px" in style or "width:1140" in style.replace(" ", "").lower():
            self.desktop_width_images += 1

    def handle_data(self, data: str) -> None:
        cleaned = data.strip()
        if cleaned:
            self.text_parts.append(cleaned)


def validate(path: pathlib.Path) -> dict:
    parser = DetailValidator()
    parser.feed(path.read_text("utf-8", errors="ignore"))
    text = " ".join(parser.text_parts)

    violations = []
    for code, pattern in BANNED_PATTERNS.items():
        if pattern.search(text):
            violations.append({"level": "error", "code": code, "message": f"Banned phrase category matched: {code}"})

    warnings = []
    if parser.gif_images:
        warnings.append(
            {
                "level": "info",
                "code": "gif_detail_media_accepted",
                "message": f"{parser.gif_images} GIF image(s) found; accepted for detail HTML, still separate from main-image upload rules",
            }
        )
    if parser.tables:
        warnings.append({"level": "warning", "code": "table_gray_zone", "message": f"{parser.tables} table(s) found"})
    if parser.gray_tags:
        warnings.append(
            {
                "level": "warning",
                "code": "gray_tags_used",
                "message": "Gray-zone tags used",
                "tags": dict(parser.gray_tags),
            }
        )
    if parser.unknown_tags:
        violations.append(
            {
                "level": "error",
                "code": "unknown_tags",
                "message": "Unsupported tags found",
                "tags": dict(parser.unknown_tags),
            }
        )
    external_hosts = [(host, count) for host, count in parser.image_hosts.items() if host not in EMAG_HOSTS]
    if external_hosts:
        warnings.append(
            {
                "level": "warning",
                "code": "external_image_hosts",
                "message": "External image host(s) found",
                "hosts": external_hosts,
            }
        )
    if parser.desktop_width_images:
        warnings.append(
            {
                "level": "warning",
                "code": "desktop_width_bias",
                "message": f"{parser.desktop_width_images} image(s) look desktop-width-biased (>800 or 1140-style)",
            }
        )

    return {
        "path": str(path),
        "status": "pass" if not violations else "fail",
        "metrics": {
            "images": parser.images,
            "gifImages": parser.gif_images,
            "tables": parser.tables,
            "inlineStyles": parser.inline_styles,
            "centerStyles": parser.center_styles,
            "desktopWidthImages": parser.desktop_width_images,
        },
        "topTags": parser.tag_counter.most_common(20),
        "imageHosts": parser.image_hosts.most_common(10),
        "violations": violations,
        "warnings": warnings,
    }


def main() -> None:
    argp = argparse.ArgumentParser()
    argp.add_argument("html_path", type=pathlib.Path)
    argp.add_argument("--out", type=pathlib.Path, default=None)
    args = argp.parse_args()

    report = validate(args.html_path)
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(payload + "\n")
    print(payload)


if __name__ == "__main__":
    main()
