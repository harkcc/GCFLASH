#!/usr/bin/env python3
"""Generate v4 EXIT eMAG detail pages with stable component/code contracts."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import generate_excite_two_product_sop_test_v3 as v3


ROOT = Path("/Users/cc/Desktop/photo_show")
OUT = ROOT / "output/emag_exit_two_product_stable_components_v4"
ASSETS = OUT / "assets"
ICON_LIB = ASSETS / "_icon_library_v1"
V3_ASSETS = ROOT / "output/emag_excite_two_product_sop_test_v3/assets"
VISUAL_BOARDS = ROOT / "output/emag_detail_visual_boards"
VALIDATOR = ROOT / "scripts/validate_emag_detail_html.py"


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        ("/System/Library/Fonts/Avenir Next.ttc", 2 if bold else 5),
        ("/System/Library/Fonts/HelveticaNeue.ttc", 1 if bold else 10),
        ("/System/Library/Fonts/Avenir.ttc", 4 if bold else 8),
        ("/System/Library/Fonts/Helvetica.ttc", 1 if bold else 0),
    ]
    for path, index in candidates:
        try:
            return ImageFont.truetype(path, size=size, index=index)
        except OSError:
            continue
    return ImageFont.load_default()


v3.FONTS.update(
    {
        "b92": font(92, True),
        "b76": font(76, True),
        "b64": font(64, True),
        "b56": font(56, True),
        "b48": font(48, True),
        "b44": font(44, True),
        "b36": font(36, True),
        "b30": font(30, True),
        "b26": font(26, True),
        "b24": font(24, True),
        "b22": font(22, True),
        "r30": font(30),
        "r26": font(26),
        "r24": font(24),
        "r22": font(22),
        "r20": font(20),
        "r18": font(18),
    }
)

F = v3.FONTS


def rel(path: Path, base: Path) -> str:
    return os.path.relpath(path, base)


def esc(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def html_img(path: Path, base: Path, alt: str) -> str:
    return (
        f'<p style="text-align:center;margin:0 0 18px 0;">'
        f'<img src="{esc(rel(path, base))}" width="1140" alt="{esc(alt)}" style="max-width:100%;height:auto;display:block;margin:0 auto;">'
        "</p>"
    )


def h2(text: str) -> str:
    return f'<h2 style="font-size:22px;line-height:1.25;margin:30px 0 14px 0;font-weight:500;color:#2b2f36;">{esc(text)}</h2>'


def p(text: str) -> str:
    return f'<p style="margin:10px 0 14px 0;">{esc(text)}</p>'


def page(body: str) -> str:
    return (
        '<div style="font-family:Arial,Helvetica,sans-serif;color:#24292f;line-height:1.58;'
        'max-width:1140px;margin:0 auto;padding:0 8px;font-size:16px;">'
        f"{body}</div>"
    )


def preview(title: str, body: str) -> str:
    return (
        '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{esc(title)}</title><style>body{{margin:0;background:#fff;}}img{{max-width:100%;height:auto;}}</style></head><body>{body}</body></html>'
    )


def draw_icon_png(kind: str, path: Path) -> None:
    img = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    accent = (255, 111, 18, 255)
    draw.ellipse((8, 8, 88, 88), fill=accent)
    v3.draw_icon(draw, kind, (48, 48), accent)
    img.save(path)


def ensure_icon_library() -> dict[str, Path]:
    ICON_LIB.mkdir(parents=True, exist_ok=True)
    icons = ["bolt", "cup", "steam", "shield", "ruler", "touch", "plug", "cable", "phases"]
    out: dict[str, Path] = {}
    for icon_id in icons:
        path = ICON_LIB / f"{icon_id}.png"
        if not path.exists():
            draw_icon_png(icon_id, path)
        out[icon_id] = path
    (ICON_LIB / "icon_library_manifest.json").write_text(
        json.dumps(
            {
                "library_id": "emag_param_icons_v1",
                "style": "solid circular pictograms",
                "usage": "spec_icon_board",
                "icons": {key: path.name for key, path in out.items()},
                "rule": "Components reference icon_id; do not redraw icons per product unless the icon library version changes.",
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return out


def tint_icon(icon_path: Path, accent: tuple[int, int, int, int]) -> Image.Image:
    icon = Image.open(icon_path).convert("RGBA")
    px = icon.load()
    for y in range(icon.height):
        for x in range(icon.width):
            r, g, b, a = px[x, y]
            if a and r > 200 and g < 150:
                px[x, y] = (accent[0], accent[1], accent[2], a)
    return icon


def draw_brand_word(draw: ImageDraw.ImageDraw, xy: tuple[int, int], word: str, font_key: str, fill, shadow=None) -> None:
    x, y = xy
    if shadow:
        draw.text((x + 7, y + 9), word, fill=shadow, font=F[font_key])
    draw.text((x, y), word, fill=fill, font=F[font_key])


def norm_color(color) -> tuple[int, int, int, int]:
    return tuple(v3.rgba(tuple(color)))


def make_exit_hero_banner(case: dict, src_dir: Path, dest: Path) -> None:
    scene = v3.fit_cover(Image.open(src_dir / case["hero_bg"]), (1140, 456)).filter(ImageFilter.GaussianBlur(4))
    product = v3.fit_contain(Image.open(src_dir / case["hero_product"]), (420, 326))
    accent = norm_color(case["accent"])
    base = Image.new("RGBA", (1140, 456), (7, 9, 12, 255))
    base.alpha_composite(scene.convert("RGBA").point(lambda p: int(p * 0.52)))
    base.alpha_composite(Image.new("RGBA", (1140, 456), (0, 0, 0, 124)))
    draw = ImageDraw.Draw(base)
    v3.draw_halftone(draw, 1140, 456, accent)
    v3.add_diagonal_glow(base, accent)
    draw.rounded_rectangle((42, 56, 630, 382), radius=22, fill=(2, 12, 15, 214), outline=accent, width=2)
    base.alpha_composite(product, (670, 70))

    frames = []
    for i in range(14):
        frame = base.copy()
        fd = ImageDraw.Draw(frame)
        draw_brand_word(fd, (86, 88), "EXIT", "b92", norm_color(case["logo_color"]), (88, 32, 22, 160))
        fd.text((90, 185), case["banner_title"], fill=(255, 255, 255, 255), font=F["b30"])
        v3.draw_wrapped(fd, (90, 230), case["banner_sub"], "r22", (226, 232, 240, 255), 470, 7, 2)
        for idx, (top, bottom) in enumerate(case["chips"]):
            bx = 90 + idx * 158
            by = 306
            fd.rounded_rectangle((bx, by, bx + 136, by + 54), radius=13, fill=(255, 255, 255, 244), outline=accent, width=2)
            fd.text((bx + 14, by + 8), top, fill=accent, font=F["b22"])
            fd.text((bx + 14, by + 32), bottom, fill=(58, 65, 74, 255), font=F["r18"])
        shine = Image.new("RGBA", (1140, 456), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shine)
        sx = -260 + i * 118
        sd.polygon([(sx, 0), (sx + 70, 0), (sx + 290, 456), (sx + 220, 456)], fill=(255, 255, 255, 24))
        frames.append(Image.alpha_composite(frame, shine).convert("RGB"))
    v3.save_gif(frames, dest, 95)


def make_spec_icon_board_v4(case: dict, icon_paths: dict[str, Path], dest: Path) -> None:
    accent = norm_color(case["accent"])
    bg = Image.new("RGBA", (1140, 680), (248, 250, 251, 255))
    draw = ImageDraw.Draw(bg)
    draw.rounded_rectangle((38, 34, 1102, 646), radius=24, fill=(255, 255, 255, 255), outline=(224, 228, 232, 255), width=2)
    draw.rectangle((38, 34, 50, 646), fill=accent)
    draw.text((82, 76), "SPECIFICATII CHEIE", fill=(34, 40, 49, 255), font=F["b44"])
    draw.text((84, 128), "4-6 parametri importanti sus, tabelul complet ramane dedesubt.", fill=(82, 91, 105, 255), font=F["r22"])
    cards = [(82, 198), (598, 198), (82, 340), (598, 340), (82, 482), (598, 482)]
    for (x, y), item in zip(cards, case["spec_cards"]):
        draw.rounded_rectangle((x, y, x + 458, y + 112), radius=18, fill=(251, 252, 253, 255), outline=(220, 225, 230, 255), width=2)
        icon = tint_icon(icon_paths[item["icon"]], accent).resize((70, 70), Image.LANCZOS)
        bg.alpha_composite(icon, (x + 22, y + 21))
        draw.text((x + 108, y + 18), item["label"], fill=(35, 40, 48, 255), font=F["b22"])
        draw.text((x + 108, y + 48), item["value"], fill=accent, font=F["b30"])
        v3.draw_wrapped(draw, (x + 108, y + 84), item["note"], "r18", (82, 91, 105, 255), 320, 4, 1)
    bg.convert("RGB").save(dest)


def make_testimonial_feedback_board(case: dict, dest: Path) -> None:
    raw = Image.open(VISUAL_BOARDS / "faq_review_board_background_imagegen.png").convert("RGBA")
    bg = v3.fit_cover(raw, (1140, 520)).convert("RGBA")
    overlay = Image.new("RGBA", (1140, 520), (0, 0, 0, 36))
    frame = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(frame)
    accent = norm_color(case["accent"])
    draw.text((64, 64), "Client", fill=(255, 255, 255, 255), font=F["b44"])
    draw.text((64, 118), "Feedback", fill=(255, 255, 255, 255), font=F["b56"])
    v3.draw_wrapped(
        draw,
        (68, 198),
        "Review area template. In productie se completeaza doar cu recenzii reale, rating si data verificabila.",
        "r20",
        (218, 224, 235, 255),
        260,
        7,
        5,
    )
    draw_brand_word(draw, (70, 420), "EXIT", "b36", (247, 188, 56, 255), (104, 31, 26, 180))

    cards = [
        (384, 58, 754, 238, (255, 255, 255, 244), (35, 40, 48, 255)),
        (790, 74, 1080, 230, (15, 15, 23, 190), (255, 255, 255, 255)),
        (384, 300, 754, 462, (15, 15, 23, 190), (255, 255, 255, 255)),
        (790, 300, 1080, 462, (15, 15, 23, 190), (255, 255, 255, 255)),
    ]
    for idx, (box, item) in enumerate(zip(cards, case["reviews"]), start=1):
        x1, y1, x2, y2, fill, text_fill = box
        draw.rounded_rectangle((x1, y1, x2, y2), radius=18, fill=fill, outline=accent if idx == 1 else (255, 255, 255, 18), width=2)
        draw.text((x1 + 24, y1 + 24), f"Review slot {idx}", fill=text_fill, font=F["b22"])
        draw.text((x2 - 52, y1 - 8), "''", fill=(255, 190, 82, 255), font=F["b48"])
        draw.text((x1 + 24, y1 + 68), item[0], fill=text_fill, font=F["b22"])
        v3.draw_wrapped(draw, (x1 + 24, y1 + 104), " ".join(item[1:]), "r18", text_fill, x2 - x1 - 48, 6, 2)
    frame.convert("RGB").save(dest)


def make_exit_trust_banner(case: dict, dest: Path) -> None:
    raw = Image.open(VISUAL_BOARDS / "brand_trust_banner_background_imagegen.png").convert("RGBA")
    bg = v3.fit_cover(raw, (1140, 456)).convert("RGBA")
    overlay = Image.new("RGBA", (1140, 456), (0, 0, 0, 22))
    base = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(base)
    draw.text((104, 68), "New Arrival", fill=(255, 255, 255, 255), font=F["b36"])
    draw_brand_word(draw, (82, 145), "EXIT", "b92", (255, 182, 42, 255), (128, 28, 24, 200))
    draw.text((88, 252), "WHERE CLARITY MEETS VALUE", fill=(255, 255, 255, 255), font=F["b30"])
    v3.draw_wrapped(draw, (90, 300), case["brand_sub"], "r22", (230, 235, 242, 255), 430, 7, 2)
    cues = case["brand_cues"]
    for idx, cue in enumerate(cues):
        x = 90 + idx * 212
        y = 370
        draw.rounded_rectangle((x, y, x + 184, y + 58), radius=14, fill=(6, 7, 10, 190), outline=(255, 184, 42, 210), width=2)
        draw.text((x + 18, y + 10), cue[0], fill=(255, 255, 255, 255), font=F["b22"])
        draw.text((x + 18, y + 35), cue[1], fill=(230, 218, 184, 255), font=F["r18"])
    frames = []
    for i in range(14):
        frame = base.copy()
        shine = Image.new("RGBA", (1140, 456), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shine)
        sx = -240 + i * 118
        sd.polygon([(sx, 0), (sx + 64, 0), (sx + 294, 456), (sx + 230, 456)], fill=(255, 255, 255, 22))
        frames.append(Image.alpha_composite(frame, shine).convert("RGB"))
    v3.save_gif(frames, dest, 100)


def html_note(text: str) -> str:
    return (
        '<blockquote style="margin:12px 0;padding:12px 14px;border-left:5px solid #f4b740;background:#fff8e8;">'
        f'<p style="margin:0;font-size:14px;line-height:1.45;"><strong>Nota:</strong> {esc(text)}</p></blockquote>'
    )


def copy_case(case: dict) -> dict:
    copied = json.loads(json.dumps(case))
    copied["brand_name"] = "EXIT"
    copied["brand_sub"] = copied["brand_sub"].replace("claims", "promisiuni").replace("Compatibilitate", "Claritate")
    for key in ["overlay", "panel", "accent", "logo_color", "buffer_bg"]:
        if key in copied:
            copied[key] = tuple(copied[key])
    if "anchor_colors" in copied:
        copied["anchor_colors"] = list(copied["anchor_colors"])
    return copied


def asset_record(path: Path, case_dir: Path, component_id: str, risk_level: str, notes: list[str]) -> dict:
    with Image.open(path) as img:
        dims = {"width": img.width, "height": img.height}
        fmt = img.format
    return {
        "component_id": component_id,
        "component_version": "v4",
        "buyer_question": COMPONENT_QUESTIONS[component_id],
        "asset_path": rel(path, case_dir),
        "asset_format": fmt,
        "dimensions": dims,
        "evidence_refs": ["ProductTruthPack", "captured_product_assets"],
        "risk_level": risk_level,
        "mobile_preview_status": "manual_preview_required_for_file_url",
        "production_notes": notes,
    }


COMPONENT_QUESTIONS = {
    "exit_hero_banner": "What result do I get and why should I keep reading?",
    "warm_visual_buffer": "Can the page rest the eye before dense detail?",
    "step_highlight_gif": "How do I use it without guessing?",
    "spec_icon_board": "Which specs decide whether this product fits my needs?",
    "testimonial_feedback_board": "How should real review evidence be presented?",
    "exit_trust_banner": "Can I trust this brand style and support process?",
}


SPEC_CARDS = v3.SPEC_CARDS


def build(case_in: dict, icon_paths: dict[str, Path]) -> None:
    case = copy_case(case_in)
    sku = case["sku"]
    source_assets = V3_ASSETS / sku
    case_assets = ASSETS / sku
    case_assets.mkdir(parents=True, exist_ok=True)
    for path in source_assets.glob("*"):
        if path.is_file():
            shutil.copy2(path, case_assets / path.name)
    case_dir = OUT / sku
    case_dir.mkdir(parents=True, exist_ok=True)
    case["spec_cards"] = SPEC_CARDS[sku]

    hero_banner = case_assets / "v4_exit_hero_banner.gif"
    green_buffer = case_assets / "v4_visual_buffer.png"
    step_gif = case_assets / "v4_step_highlight.gif"
    spec_board = case_assets / "v4_spec_icon_board.png"
    feedback_board = case_assets / "v4_testimonial_feedback_board.png"
    trust_banner = case_assets / "v4_exit_trust_banner.gif"

    make_exit_hero_banner(case, case_assets, hero_banner)
    v3.make_green_buffer(case, case_assets, green_buffer)
    v3.make_step_gif(case, case_assets, step_gif)
    make_spec_icon_board_v4(case, icon_paths, spec_board)
    make_testimonial_feedback_board(case, feedback_board)
    make_exit_trust_banner(case, trust_banner)

    body = ""
    body += html_img(hero_banner, case_dir, "EXIT result banner")
    body += h2(case["name"].upper())
    body += p("V4 foloseste componente stabile: brand EXIT, ierarhie mai calma, imagini reale alternante, parametri cu icon library, feedback separat de Q&A si brand trust banner.")
    body += v3.anchor_triplet(case)
    body += v3.mixed_feature_blocks(case, case_dir, case_assets)
    body += html_img(green_buffer, case_dir, "visual buffer")
    body += h2("PASII SI MOMENTELE CHEIE")
    body += html_img(step_gif, case_dir, "step highlight gif")
    body += h2("PARAMETRI CHEIE")
    body += html_img(spec_board, case_dir, "core parameter icon board")
    body += h2("SPECIFICATII COMPLETE")
    body += v3.spec_table(case["specs"])
    body += h2("CONTINUT PACHET")
    body += v3.spec_table(case["package"])
    body += h2("INTREBARI INAINTE DE CUMPARARE")
    body += html_note("Q&A textual complet ramane in ProductTruthPack; in pagina finala il afisam doar cand nu exista board vizual sau cand e nevoie de text SEO.")
    body += h2("REVIEW / FEEDBACK TEMPLATE")
    body += html_img(feedback_board, case_dir, "testimonial style feedback board")
    body += html_note("feedback-ul este template vizual. In productie se inlocuieste cu review-uri reale, sursa, data si rating verificabil.")
    body += h2("DESPRE EXIT")
    body += html_img(trust_banner, case_dir, "EXIT trust banner")

    html = page(body)
    (case_dir / "detail.html").write_text(html + "\n", encoding="utf-8")
    (case_dir / "detail_v4.html").write_text(html + "\n", encoding="utf-8")
    (case_dir / "preview_mobile.html").write_text(preview(f"EXIT v4 {sku}", html), encoding="utf-8")
    media_index = {
        "sku": sku,
        "brand": "EXIT",
        "generation_mode": "deterministic_pillow_composition_with_icon_library",
        "icon_library": rel(ICON_LIB / "icon_library_manifest.json", case_dir),
        "component_records": [
            asset_record(hero_banner, case_dir, "exit_hero_banner", "medium", ["Uses captured product assets; clean old baked branding before production if visible."]),
            asset_record(green_buffer, case_dir, "warm_visual_buffer", "low", ["Color should stay category-compatible."]),
            asset_record(step_gif, case_dir, "step_highlight_gif", "low", ["Stable GIF recipe: sequential highlight only."]),
            asset_record(spec_board, case_dir, "spec_icon_board", "low", ["Icons are loaded from icon library; source spec table follows."]),
            asset_record(feedback_board, case_dir, "testimonial_feedback_board", "medium", ["Template only; use real reviews for production."]),
            asset_record(trust_banner, case_dir, "exit_trust_banner", "medium", ["People/parcel background is reference-style generated asset; confirm rights before commercial use."]),
        ],
    }
    (case_dir / "media_asset_index.json").write_text(json.dumps(media_index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    design_spec = {
        "sku": sku,
        "brand": "EXIT",
        "version": "v4",
        "design_direction": "Stable components with code contract, calmer typography, icon library, testimonial-style feedback, and trust-banner closer.",
        "component_code_contract": {
            "input": ["ProductTruthPack", "BrandKit", "AssetInventory", "EvidencePack"],
            "renderer": "component_id + props -> asset/html_snippet + media_asset_index record",
            "validation": ["html_validator", "claim_evidence_policy", "mobile_preview"],
        },
        "modules": [
            "exit_hero_banner",
            "first_screen_anchor_triplet",
            "mixed_image_text_block",
            "warm_visual_buffer",
            "step_highlight_gif",
            "spec_icon_board",
            "source_spec_table",
            "package_table",
            "testimonial_feedback_board",
            "exit_trust_banner",
        ],
        "notes": [
            "Brand text is EXIT; old accented brand spelling is not used.",
            "QA board/text is not duplicated in this version.",
            "Human or product motion should be pre-rendered as GIF/WebP and embedded as img; HTML does not animate the person directly.",
        ],
    }
    (case_dir / "DESIGN_SPEC.json").write_text(json.dumps(design_spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    validate = subprocess.run(
        ["python3", str(VALIDATOR), str(case_dir / "detail.html"), "--out", str(case_dir / "validation_report.json")],
        capture_output=True,
        text=True,
    )
    if validate.returncode:
        raise RuntimeError(validate.stderr or validate.stdout)


def write_index() -> None:
    items = []
    for case in v3.CASES:
        sku = case["sku"]
        items.append(
            f'<li style="margin:10px 0;"><strong>{sku}</strong> - '
            f'<a href="{sku}/preview_mobile.html">v4 preview</a> | '
            f'<a href="{sku}/DESIGN_SPEC.json">DESIGN_SPEC</a> | '
            f'<a href="{sku}/media_asset_index.json">media index</a> | '
            f'<a href="{sku}/validation_report.json">validation</a></li>'
        )
    html = preview(
        "EXIT stable components v4",
        page(h2("EXIT stable components v4") + p("Brand renamed to EXIT; v4 adds icon library, calmer typography, testimonial feedback board and original-style trust banner.") + "<ul>" + "".join(items) + "</ul>"),
    )
    (OUT / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    icons = ensure_icon_library()
    for case in v3.CASES:
        build(case, icons)
    write_index()
    print(OUT)


if __name__ == "__main__":
    main()
