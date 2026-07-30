#!/usr/bin/env python3
"""Build a labelled side-by-side comparison board for G1 acceptance (SPEC §10).

Used by all three online acceptance steps: P0 replication vs the 2026-07-11
baseline (§10.1), the convergence round table (§10.2), and style transfer
(§10.3).

Usage::

    python scripts/build_g1_comparison_board.py \
        --panel "2026-07-11 baseline (exec-ef89d9cc)=/abs/baseline.png" \
        --panel "2026-07-30 adapter replication=/abs/candidate.png" \
        --title "G1 P0 replication smoke" \
        --out artifacts/g1_p0_smoke/board.png
"""
from __future__ import annotations

import argparse
import pathlib

from PIL import Image, ImageDraw, ImageFont

PANEL_H = 1100
GAP = 28
MARGIN = 28
LABEL_H = 62
TITLE_H = 72
BG = (250, 250, 250)
FG = (17, 17, 17)
SUB = (110, 110, 110)

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if pathlib.Path(path).is_file():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default(size)


def build(panels: list[tuple[str, pathlib.Path]], out: pathlib.Path,
          title: str | None = None) -> pathlib.Path:
    loaded = []
    for label, path in panels:
        im = Image.open(path).convert("RGB")
        scale = PANEL_H / im.height
        im = im.resize((max(1, round(im.width * scale)), PANEL_H), Image.LANCZOS)
        loaded.append((label, path, im))

    top = MARGIN + (TITLE_H if title else 0)
    width = MARGIN * 2 + sum(im.width for _, _, im in loaded) + GAP * (len(loaded) - 1)
    height = top + LABEL_H + PANEL_H + MARGIN
    board = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(board)

    if title:
        draw.text((MARGIN, MARGIN - 6), title, font=_font(38), fill=FG)

    x = MARGIN
    for label, path, im in loaded:
        draw.text((x, top + 4), label, font=_font(27), fill=FG)
        draw.text((x, top + 34), f"{im.width}x{PANEL_H}  ·  {path.name}",
                  font=_font(18), fill=SUB)
        board.paste(im, (x, top + LABEL_H))
        draw.rectangle([x, top + LABEL_H, x + im.width - 1,
                        top + LABEL_H + PANEL_H - 1], outline=(220, 220, 220))
        x += im.width + GAP

    out.parent.mkdir(parents=True, exist_ok=True)
    board.save(out, "PNG")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="G1 comparison board builder")
    ap.add_argument("--panel", action="append", required=True, metavar="LABEL=PATH",
                    help="repeatable, left to right")
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--title", default=None)
    args = ap.parse_args()

    panels = []
    for spec in args.panel:
        if "=" not in spec:
            ap.error(f"--panel needs LABEL=PATH, got: {spec}")
        label, _, path = spec.partition("=")
        p = pathlib.Path(path).expanduser()
        if not p.is_file():
            ap.error(f"panel image not found: {p}")
        panels.append((label.strip(), p))

    out = build(panels, args.out, args.title)
    im = Image.open(out)
    print(f"wrote {out}  ({im.width}x{im.height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
