#!/usr/bin/env python3
"""Validate EXCITAT eMAG banner/HTML agent run folders."""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from PIL import Image


REQUIRED_FILES = {
    "detail.html",
    "preview_mobile.html",
    "DESIGN_SPEC.json",
    "media_asset_index.json",
    "repair_log.md",
}

FORBIDDEN_BRAND_TEXT = {"EXIT", "Excité", "Exceity", "EXITE", "BestPlaza", "BESTPLAZA"}
ALLOWED_ROUTES = {"pure_composite", "ai_background_plus_composite", "pure_ai_generation"}
PRODUCTION_ROUTES = {"pure_composite", "ai_background_plus_composite"}
STABLE_MOTION = {"none", "static", "shine_sweep", "light_trail", "step_highlight", "icon_pulse"}
FORBIDDEN_TAGS = {"script", "iframe", "form", "link"}
ALLOWED_TAGS = {
    "div",
    "p",
    "img",
    "h1",
    "h2",
    "h3",
    "strong",
    "br",
    "ul",
    "li",
    "table",
    "tbody",
    "tr",
    "td",
    "span",
    "blockquote",
}


class TagParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag.lower())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def add(findings: list[dict[str, str]], level: str, code: str, message: str) -> None:
    findings.append({"level": level, "code": code, "message": message})


def image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as im:
        return im.size


def validate_html(run_dir: Path, findings: list[dict[str, str]]) -> None:
    html_path = run_dir / "detail.html"
    html = html_path.read_text(encoding="utf-8")
    parser = TagParser()
    parser.feed(html)
    tags = set(parser.tags)
    forbidden = sorted(tags & FORBIDDEN_TAGS)
    if forbidden:
        add(findings, "error", "html_forbidden_tags", ", ".join(forbidden))
    unknown = sorted(tags - ALLOWED_TAGS)
    if unknown:
        add(findings, "warning", "html_gray_or_unknown_tags", ", ".join(unknown))
    for token in FORBIDDEN_BRAND_TEXT:
        if re.search(rf"\b{re.escape(token)}\b", html):
            add(findings, "error", "forbidden_brand_text", f"Found display token: {token}")


def validate_design(spec: dict[str, Any], findings: list[dict[str, str]]) -> None:
    brand = spec.get("brand_kit", {}).get("visual_brand")
    if brand != "EXCITAT":
        add(findings, "error", "brand_display_must_be_EXCITAT", f"brand_kit.visual_brand={brand!r}")
    slug = spec.get("brand_kit", {}).get("internal_slug")
    if slug != "excitat":
        add(findings, "warning", "brand_slug_unexpected", f"internal_slug={slug!r}")


def validate_media(run_dir: Path, media: list[dict[str, Any]], findings: list[dict[str, str]]) -> None:
    if len(media) < 6:
        add(findings, "error", "too_few_route_test_assets", "Expected at least six route test assets")

    previous_heavy = False
    for item in media:
        asset_id = item.get("asset_id", "<unknown>")
        rel = item.get("path")
        if not rel:
            add(findings, "error", "asset_missing_path", asset_id)
            continue
        path = run_dir / rel
        if not path.exists():
            add(findings, "error", "asset_path_not_found", f"{asset_id}: {rel}")
            continue
        width, height = image_size(path)
        if width != 1140:
            add(findings, "warning", "image_width_policy", f"{asset_id}: width={width}, expected 1140")
        if height < 300:
            add(findings, "warning", "image_height_short", f"{asset_id}: height={height}")

        route = item.get("route_selected")
        if route not in ALLOWED_ROUTES:
            add(findings, "error", "unknown_route", f"{asset_id}: {route}")
        if item.get("production_candidate") and route not in PRODUCTION_ROUTES:
            add(findings, "error", "pure_ai_not_production", asset_id)

        motion = item.get("motion_effect", "none")
        if motion not in STABLE_MOTION:
            add(findings, "warning", "experimental_motion", f"{asset_id}: {motion}")

        module_type = item.get("module_type")
        if module_type == "qa" and item.get("review_mode"):
            add(findings, "error", "qa_review_mixed", asset_id)
        if module_type == "qa" and item.get("rating_fields"):
            add(findings, "error", "qa_contains_review_signals", asset_id)
        if module_type == "review":
            if item.get("review_mode") != "real":
                note = " ".join(item.get("production_notes", []))
                if "preview" not in note.lower():
                    add(findings, "error", "review_preview_note_missing", asset_id)
            if item.get("review_mode") == "real" and not item.get("review_source_refs"):
                add(findings, "error", "real_review_source_missing", asset_id)

        for claim in item.get("claims", []):
            if not claim.get("evidence_refs"):
                add(findings, "error", "unsupported_claim", f"{asset_id}: {claim.get('text')}")

        heavy = item.get("visual_weight") == "heavy_dark"
        if previous_heavy and heavy:
            add(findings, "warning", "consecutive_heavy_dark_modules", asset_id)
        previous_heavy = heavy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    run_dir = args.run_dir
    findings: list[dict[str, str]] = []

    missing = sorted(name for name in REQUIRED_FILES if not (run_dir / name).exists())
    if missing:
        add(findings, "error", "missing_required_files", ", ".join(missing))

    if (run_dir / "detail.html").exists():
        validate_html(run_dir, findings)
    if (run_dir / "DESIGN_SPEC.json").exists():
        validate_design(load_json(run_dir / "DESIGN_SPEC.json"), findings)
    if (run_dir / "media_asset_index.json").exists():
        validate_media(run_dir, load_json(run_dir / "media_asset_index.json").get("assets", []), findings)

    status = "fail" if any(f["level"] == "error" for f in findings) else "pass"
    report = {
        "status": status,
        "run_dir": str(run_dir),
        "checked_brand": "EXCITAT",
        "findings": findings,
    }
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    raise SystemExit(0 if status == "pass" else 1)


if __name__ == "__main__":
    main()

