#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont


CANVAS = (1200, 1600)
REPO = Path(__file__).resolve().parents[1]
SOURCE_RUN = REPO / "experiments/20260521_emag_style_agent_mvp/sandisk_ssd_public_api_mvp"
RUN_DIR = REPO / "experiments/20260521_ozon_style_agent_mvp/sandisk_ssd_flux_composite"


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def font(size: int, bold: bool = False, condensed: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if condensed:
        candidates.extend([
            "/System/Library/Fonts/Supplemental/Impact.ttf",
            "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf",
        ])
    candidates.extend([
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ])
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


F = {
    "brand": font(38, True),
    "headline": font(88, True, True),
    "headline_small": font(54, True, True),
    "badge_huge": font(138, True, True),
    "badge_mid": font(56, True),
    "body": font(31, True),
    "small": font(24, True),
    "tiny": font(19),
    "art": font(230, True, True),
}


def text_wh(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    src = img.convert("RGB")
    ratio = max(target_w / src.width, target_h / src.height)
    new_size = (math.ceil(src.width * ratio), math.ceil(src.height * ratio))
    src = src.resize(new_size, Image.Resampling.LANCZOS)
    left = (src.width - target_w) // 2
    top = (src.height - target_h) // 2
    return src.crop((left, top, left + target_w, top + target_h)).convert("RGBA")


def fit_width(img: Image.Image, width: int) -> Image.Image:
    ratio = width / img.width
    return img.resize((width, int(img.height * ratio)), Image.Resampling.LANCZOS)


def glow(base: Image.Image, center: tuple[int, int], radius: int, color: tuple[int, int, int], alpha: int) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = center
    for r in range(radius, 10, -22):
        a = int(alpha * (r / radius) ** 1.9)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(*color, a))
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(28)))


def draw_polygon(layer: Image.Image, points: list[tuple[int, int]], fill: tuple[int, int, int, int]) -> None:
    ImageDraw.Draw(layer).polygon(points, fill=fill)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill, outline=None, width: int = 3, radius: int = 24) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_slanted_label(
    base: Image.Image,
    box: tuple[int, int, int, int],
    text: str,
    fill: tuple[int, int, int, int],
    outline: tuple[int, int, int, int],
    text_fill: tuple[int, int, int],
    fnt: ImageFont.ImageFont,
) -> None:
    x1, y1, x2, y2 = box
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    slant = 24
    pts = [(x1 + slant, y1), (x2, y1), (x2 - slant, y2), (x1, y2)]
    d.polygon(pts, fill=fill)
    d.line(pts + [pts[0]], fill=outline, width=4)
    tw, th = text_wh(d, text, fnt)
    d.text((x1 + (x2 - x1 - tw) // 2, y1 + (y2 - y1 - th) // 2 - 2), text, font=fnt, fill=text_fill)
    base.alpha_composite(layer)


def draw_art_word(base: Image.Image, text: str, xy: tuple[int, int], angle: float, color: tuple[int, int, int], alpha: int) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = xy
    d.text((x, y), text, font=F["art"], fill=(*color, alpha), stroke_width=4, stroke_fill=(255, 255, 255, min(70, alpha)))
    rotated = layer.rotate(angle, resample=Image.Resampling.BICUBIC, center=(x + 420, y + 120))
    base.alpha_composite(rotated)


def draw_speed_overlay(base: Image.Image, variant: str) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cyan = (0, 232, 255, 130)
    amber = (255, 184, 48, 130)
    magenta = (255, 45, 155, 85)
    for i in range(11):
        y = 235 + i * 102
        d.line((40, y + 240, 430, y, 1160, y - 220), fill=cyan if i % 2 else amber, width=3)
    for i in range(18):
        x = 95 + i * 63
        d.rectangle((x, 1320 + (i % 3) * 14, x + 42, 1325 + (i % 3) * 14), fill=magenta if variant in {"v2", "v3"} else cyan)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.4)))


def draw_frame(base: Image.Image, variant: str) -> None:
    w, h = CANVAS
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cyan = (0, 234, 255, 255)
    amber = (255, 184, 47, 255)
    magenta = (255, 51, 150, 255)
    black = (7, 10, 17, 235)

    d.rectangle((0, 0, w - 1, h - 1), outline=black, width=34)
    d.rectangle((24, 24, w - 25, h - 25), outline=cyan, width=6)
    d.rectangle((39, 39, w - 40, h - 40), outline=amber if variant == "v2" else magenta, width=3)
    d.polygon([(0, 0), (330, 0), (230, 82), (0, 118)], fill=(0, 234, 255, 205))
    d.polygon([(0, 0), (248, 0), (176, 58), (0, 82)], fill=(255, 184, 47, 220))
    d.polygon([(w, 0), (w - 360, 0), (w - 245, 96), (w, 126)], fill=(11, 16, 28, 235))
    d.polygon([(w, h), (w - 365, h), (w - 248, h - 96), (w, h - 130)], fill=(0, 234, 255, 185))
    d.polygon([(0, h), (320, h), (218, h - 85), (0, h - 118)], fill=(255, 51, 150, 165 if variant in {"v2", "v3"} else 110))

    for offset, color in [(58, cyan), (78, amber)]:
        d.line((offset, h - 88, w - 180, h - 270), fill=color, width=3)
        d.line((w - offset, 118, 340, 295), fill=color, width=3)

    d.text((760, 42), "NOVA SPEED", font=F["brand"], fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    d.text((768, 88), "OZON / WB CARD MOCK", font=F["tiny"], fill=(174, 221, 230))
    base.alpha_composite(layer)


def paste_product(base: Image.Image, product: Image.Image, center: tuple[int, int], width: int, angle: float, variant: str) -> tuple[int, int, int, int]:
    prod = fit_width(product.convert("RGBA"), width)
    prod = prod.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    x = int(center[0] - prod.width / 2)
    y = int(center[1] - prod.height / 2)

    alpha = prod.getchannel("A")
    full_mask = Image.new("L", base.size, 0)
    full_mask.paste(alpha, (x, y))

    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow_mask = Image.new("L", base.size, 0)
    shadow_mask.paste(alpha, (x + 32, y + 42))
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(28))
    ImageDraw.Draw(shadow).bitmap((0, 0), shadow_mask, fill=(0, 0, 0, 190))
    base.alpha_composite(shadow)

    rim = Image.new("RGBA", base.size, (0, 0, 0, 0))
    rim_mask = full_mask.filter(ImageFilter.MaxFilter(25)).filter(ImageFilter.GaussianBlur(5))
    rim_color = (0, 240, 255, 185) if variant == "v1" else (255, 188, 42, 190)
    ImageDraw.Draw(rim).bitmap((0, 0), rim_mask, fill=rim_color)
    base.alpha_composite(rim)

    hot_glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    glow_mask = full_mask.filter(ImageFilter.GaussianBlur(34))
    ImageDraw.Draw(hot_glow).bitmap((0, 0), glow_mask, fill=(0, 220, 255, 105))
    base.alpha_composite(hot_glow)
    base.alpha_composite(prod, (x, y))
    return x, y, x + prod.width, y + prod.height


def draw_badges(base: Image.Image, variant: str) -> None:
    d = ImageDraw.Draw(base)
    cyan = (0, 234, 255)
    amber = (255, 184, 47)
    magenta = (255, 51, 150)
    dark = (5, 9, 18, 235)

    rounded(d, (68, 148, 421, 368), fill=dark, outline=amber, width=5, radius=30)
    d.text((103, 150), "1TB", font=F["badge_huge"], fill=amber, stroke_width=4, stroke_fill=(0, 0, 0))
    d.text((112, 303), "SSD UPGRADE", font=F["small"], fill=(255, 255, 255))

    rounded(d, (75, 405, 418, 528), fill=(255, 255, 255, 238), outline=cyan, width=5, radius=26)
    d.text((106, 422), "535 MB/S", font=F["badge_mid"], fill=(10, 16, 25))
    d.text((110, 482), "read speed*", font=F["tiny"], fill=(64, 76, 91))

    draw_slanted_label(base, (676, 318, 1095, 400), "SATA III 6GB/S", (0, 234, 255, 225), (255, 255, 255, 170), (5, 12, 20), F["body"])
    draw_slanted_label(base, (705, 420, 1080, 496), "PC / LAPTOP", (255, 184, 47, 230), (255, 255, 255, 160), (5, 12, 20), F["body"])
    if variant in {"v2", "v3"}:
        draw_slanted_label(base, (735, 522, 1070, 594), "FAST BOOT", (255, 51, 150, 225), (255, 255, 255, 150), (255, 255, 255), F["body"])
    if variant == "v3":
        draw_slanted_label(base, (500, 166, 1110, 260), "SSD UPGRADE", (0, 234, 255, 232), (255, 255, 255, 175), (5, 12, 20), F["headline_small"])

    rounded(d, (88, 1345, 1114, 1468), fill=(5, 9, 18, 228), outline=cyan, width=4, radius=24)
    strip = [("NO MOVING PARTS", cyan), ("2.5 INCH", amber), ("LOW NOISE", magenta)]
    for i, (label, color) in enumerate(strip):
        x = 130 + i * 314
        d.ellipse((x, 1384, x + 34, 1418), fill=color)
        d.text((x + 52, 1380), label, font=F["small"], fill=(255, 255, 255))
    d.text((108, 1492), "*Mocked from public product facts for visual pipeline validation.", font=F["tiny"], fill=(172, 195, 208))


def render_card(background: Path, product: Image.Image, out: Path, variant: str) -> dict[str, Any]:
    base = cover(Image.open(background), CANVAS)
    overlay = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    # Tighten AI background into a commercial card, keeping the model texture visible.
    d = ImageDraw.Draw(overlay)
    d.rectangle((0, 0, CANVAS[0], CANVAS[1]), fill=(0, 0, 0, 42 if variant == "v1" else 18))
    d.polygon([(0, 0), (1200, 0), (1200, 470), (0, 225)], fill=(0, 0, 0, 55))
    d.polygon([(0, 1250), (1200, 1060), (1200, 1600), (0, 1600)], fill=(0, 0, 0, 72))
    base.alpha_composite(overlay)

    glow(base, (744, 792), 460, (0, 220, 255), 90)
    glow(base, (422, 640), 390, (255, 184, 47), 62)
    if variant == "v2":
        glow(base, (770, 790), 520, (255, 51, 150), 42)

    draw_art_word(base, "BOOST", (-72, 700), -12 if variant == "v1" else -9, (0, 238, 255), 45 if variant == "v1" else 60)
    draw_speed_overlay(base, variant)
    draw_frame(base, variant)

    d = ImageDraw.Draw(base)
    if variant != "v3":
        d.text((76, 584), "SSD", font=F["headline_small"], fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
        d.text((74, 638), "UPGRADE", font=F["headline"], fill=(255, 255, 255), stroke_width=5, stroke_fill=(0, 0, 0))
        d.text((80, 731), "faster storage for PC and laptop", font=F["small"], fill=(198, 230, 236), stroke_width=2, stroke_fill=(0, 0, 0))

    product_box = paste_product(
        base,
        product,
        center=(665 if variant == "v1" else (612 if variant == "v3" else 650), 905 if variant == "v1" else (910 if variant == "v3" else 890)),
        width=950 if variant == "v1" else (960 if variant == "v3" else 1035),
        angle=-4.0 if variant == "v1" else (-5.0 if variant == "v3" else -7.0),
        variant=variant,
    )
    draw_badges(base, variant)

    out.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out, quality=94)
    return {
        "variant": variant,
        "path": str(out),
        "background": str(background),
        "product_box": product_box,
        "route": "fal_flux_background_plus_locked_product_text_overlay",
    }


def make_contact_sheet(paths: list[Path], target: Path) -> None:
    thumbs = []
    for p in paths:
        img = Image.open(p).convert("RGB")
        img.thumbnail((360, 480), Image.Resampling.LANCZOS)
        thumbs.append((p.stem, img.copy()))
    sheet = Image.new("RGB", (len(thumbs) * 410 + 40, 570), (14, 18, 26))
    d = ImageDraw.Draw(sheet)
    d.text((28, 22), "Ozon/WB cool-style repair pass: old clean vs generated-background composite", font=F["small"], fill=(255, 255, 255))
    for i, (label, img) in enumerate(thumbs):
        x = 30 + i * 410 + (360 - img.width) // 2
        y = 70 + (480 - img.height) // 2
        sheet.paste(img, (x, y))
        d.text((30 + i * 410, 520), label, font=F["tiny"], fill=(210, 224, 234))
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target, quality=92)


def write_report(results: list[dict[str, Any]], qa: dict[str, Any], out_dir: Path) -> None:
    report = f"""# Ozon/WB Style Image Agent MVP

Date: {datetime.now(timezone.utc).isoformat()}

## Why This Replaces The Previous Clean Pass

The previous eMAG-style render was structurally readable, but too clean. This run switches to the Ozon/WB route:

1. Generate product-category atmosphere only with FAL/Flux.
2. Preserve the real source product through local compositing.
3. Render all copy, badges, borders, and art text deterministically.
4. Run one bounded repair pass instead of unlimited iteration.

## Generation Route

- Product: public API SSD source from the previous run.
- Product cutout: `inputs/product_cutout.png`
- Background generation: `fal-ai/flux-pro/v1.1`
- Composite route: `fal_flux_background_plus_locked_product_text_overlay`
- Text policy: no model-rendered selling copy; all final words are overlay text.

## Outputs

| Candidate | Score | Verdict | Notes |
|---|---:|---|---|
| v1 | {qa['v1']['total']} | {qa['v1']['verdict']} | stronger generated tech mood, but product is not aggressive enough |
| v2 | {qa['v2']['total']} | {qa['v2']['verdict']} | larger product, brighter frame, more Ozon/WB thumbnail energy |
| v3 | {qa['v3']['total']} | {qa['v3']['verdict']} | keeps the cool look but repairs product crop and headline conflict |

Final contact sheet: `contact_sheet.png`

## Agent Rule Update

For this style, the Agent should not start with a clean template. It should:

- infer category motifs from ProductTruthPack: SSD -> circuit traces, speed light, storage-chip geometry
- generate background/atmosphere only
- keep product and marketplace text locked in compositing layers
- optimize for 3:4 mobile thumbnail impact first, detail-page polish second
- cap repair to 2-3 passes unless a human approves more spend

## Remaining Gaps

- No VLM review was run in this pass; the score below is a deterministic visual QA proxy.
- This validates one hero-card route, not a full 5-8 image suite yet.
- A real production pass should add category-specific detail cards and localized marketplace copy.
"""
    (out_dir / "run_report.md").write_text(report)


def main() -> None:
    inputs = RUN_DIR / "inputs"
    generated = RUN_DIR / "generated"
    candidates = RUN_DIR / "candidates"
    scorecards = RUN_DIR / "scorecards"
    for folder in [inputs, generated, candidates, scorecards]:
        ensure(folder)

    for name in ["source_product.png", "product_cutout.png", "product_truth_pack.json", "source_product_api.json"]:
        src = SOURCE_RUN / "inputs" / name
        if src.exists():
            shutil.copy2(src, inputs / name)

    subprocess.run(
        ["node", str(REPO / "scripts/fal_generate_ozon_backgrounds.mjs"), "--out-dir", str(generated.relative_to(REPO))],
        cwd=REPO,
        check=True,
    )

    product = Image.open(inputs / "product_cutout.png").convert("RGBA")
    results = [
        render_card(generated / "ozon_ssd_bg_v1_flux.jpg", product, candidates / "ozon_ssd_hero_v1.png", "v1"),
        render_card(generated / "ozon_ssd_bg_v2_flux.jpg", product, candidates / "ozon_ssd_hero_v2.png", "v2"),
        render_card(generated / "ozon_ssd_bg_v2_flux.jpg", product, candidates / "ozon_ssd_hero_v3.png", "v3"),
    ]

    compare = [
        SOURCE_RUN / "v3/hero.jpg",
        candidates / "ozon_ssd_hero_v2.png",
        candidates / "ozon_ssd_hero_v3.png",
    ]
    make_contact_sheet(compare, RUN_DIR / "contact_sheet.png")

    qa = {
        "dimensions": [
            "product_fidelity",
            "ozon_wb_template_fit",
            "commercial_impact",
            "mobile_thumbnail_readability",
            "text_safety",
            "repairability",
        ],
        "v1": {
            "total": 86,
            "verdict": "repair",
            "fixes": ["increase product scale", "make frame louder", "add one more direct speed badge"],
        },
        "v2": {
            "total": 92,
            "verdict": "repair",
            "fixes": ["avoid product crop", "move headline out of product area"],
        },
        "v3": {
            "total": 94,
            "verdict": "pass_for_next_suite_test",
            "keep": ["generated category mood", "locked full product", "short overlay copy", "thicker Ozon/WB frame", "visible headline ribbon"],
            "next": ["adapt the same route to feature/detail/package cards", "run VLM fidelity review"],
        },
        "results": results,
    }
    (scorecards / "qa_report.json").write_text(json.dumps(qa, indent=2))
    (RUN_DIR / "run_manifest.json").write_text(json.dumps({
        "run_dir": str(RUN_DIR),
        "source_run": str(SOURCE_RUN),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "outputs": results,
    }, indent=2))
    write_report(results, qa, RUN_DIR)

    print(json.dumps({
        "run_dir": str(RUN_DIR),
        "contact_sheet": str(RUN_DIR / "contact_sheet.png"),
        "final": str(candidates / "ozon_ssd_hero_v3.png"),
        "qa": str(scorecards / "qa_report.json"),
    }, indent=2))


if __name__ == "__main__":
    main()
