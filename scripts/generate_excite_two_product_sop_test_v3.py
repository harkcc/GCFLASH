#!/usr/bin/env python3
"""Generate v3 Excite eMAG detail pages with icon specs and Manner-style boards."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from generate_excite_two_product_sop_test_v2 import (
    ASSETS as V2_ASSETS,
    CASES,
    FONTS,
    ROOT,
    VALIDATOR,
    anchor_triplet,
    esc,
    fit_contain,
    fit_cover,
    h2,
    html_img,
    make_green_buffer,
    make_step_gif,
    mixed_feature_blocks,
    p,
    page,
    preview,
    qa_module,
    rel,
    save_gif,
    spec_table,
)


OUT = ROOT / "output/emag_excite_two_product_sop_test_v3"
ASSETS = OUT / "assets"


def rgba(color: tuple[int, int, int] | tuple[int, int, int, int], alpha: int | None = None) -> tuple[int, int, int, int]:
    if len(color) == 4:
        return color
    if alpha is None:
        alpha = 255
    return (color[0], color[1], color[2], alpha)


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font_key: str,
    fill: tuple[int, int, int] | tuple[int, int, int, int],
    max_width: int,
    line_gap: int = 8,
    max_lines: int | None = None,
) -> int:
    words = text.split()
    lines: list[str] = []
    current = ""
    font = FONTS[font_key]
    for word in words:
        candidate = f"{current} {word}".strip()
        width = draw.textbbox((0, 0), candidate, font=font)[2]
        if width <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    if max_lines is not None:
        lines = lines[:max_lines]
    x, y = xy
    step = font.size + line_gap if hasattr(font, "size") else 28
    for line in lines:
        draw.text((x, y), line, fill=fill, font=font)
        y += step
    return y


def draw_halftone(draw: ImageDraw.ImageDraw, width: int, height: int, accent: tuple[int, int, int, int]) -> None:
    for x in range(0, width // 2, 18):
        for y in range(0, height, 18):
            if (x // 18 + y // 18) % 3 == 0:
                r = 1 + max(0, 5 - x // 90)
                draw.ellipse((x, y, x + r, y + r), fill=(accent[0], accent[1], accent[2], 70))


def add_diagonal_glow(base: Image.Image, accent: tuple[int, int, int, int]) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    w, h = base.size
    gd.polygon([(w * 0.42, 0), (w * 0.58, 0), (w * 0.75, h), (w * 0.55, h)], fill=(255, 255, 255, 20))
    for i in range(7):
        y = int(h * 0.62 + i * 18)
        gd.line((int(w * 0.42), y, int(w * 0.94), y - 126), fill=(accent[0], accent[1], accent[2], 42), width=4)
    base.alpha_composite(glow)


def draw_icon(draw: ImageDraw.ImageDraw, kind: str, center: tuple[int, int], accent: tuple[int, int, int, int]) -> None:
    x, y = center
    color = (accent[0], accent[1], accent[2], 255)
    white = (255, 255, 255, 255)
    draw.ellipse((x - 31, y - 31, x + 31, y + 31), fill=color)
    if kind == "bolt":
        draw.polygon([(x - 4, y - 25), (x - 20, y + 4), (x - 4, y + 4), (x - 10, y + 25), (x + 21, y - 8), (x + 4, y - 8)], fill=white)
    elif kind == "cup":
        draw.rounded_rectangle((x - 16, y - 20, x + 14, y + 20), radius=6, outline=white, width=4)
        draw.arc((x + 8, y - 7, x + 29, y + 14), 280, 80, fill=white, width=4)
        draw.line((x - 12, y - 4, x + 10, y - 4), fill=white, width=3)
    elif kind == "steam":
        for dx in [-12, 0, 12]:
            draw.arc((x + dx - 8, y - 29, x + dx + 8, y + 5), 90, 260, fill=white, width=3)
        draw.arc((x - 25, y - 2, x + 25, y + 28), 0, 180, fill=white, width=4)
        draw.line((x - 18, y + 14, x + 18, y + 14), fill=white, width=4)
    elif kind == "shield":
        draw.polygon([(x, y - 24), (x + 22, y - 14), (x + 17, y + 17), (x, y + 28), (x - 17, y + 17), (x - 22, y - 14)], outline=white, fill=None)
        draw.line((x - 9, y + 1, x - 1, y + 10, x + 13, y - 10), fill=white, width=4)
    elif kind == "ruler":
        draw.rounded_rectangle((x - 24, y - 8, x + 24, y + 12), radius=4, outline=white, width=4)
        for dx in [-14, -5, 4, 13]:
            draw.line((x + dx, y - 8, x + dx, y + 3), fill=white, width=2)
    elif kind == "touch":
        draw.rounded_rectangle((x - 18, y - 26, x + 18, y + 26), radius=7, outline=white, width=4)
        draw.ellipse((x - 5, y + 13, x + 5, y + 23), fill=white)
        draw.line((x + 20, y + 5, x + 31, y + 17), fill=white, width=4)
    elif kind == "plug":
        draw.rounded_rectangle((x - 12, y - 3, x + 18, y + 22), radius=6, outline=white, width=4)
        draw.line((x - 13, y - 16, x - 13, y - 2), fill=white, width=4)
        draw.line((x + 7, y - 16, x + 7, y - 2), fill=white, width=4)
        draw.line((x + 18, y + 11, x + 28, y + 11), fill=white, width=4)
    elif kind == "cable":
        draw.arc((x - 28, y - 10, x + 20, y + 38), 185, 345, fill=white, width=5)
        draw.rounded_rectangle((x + 5, y - 22, x + 24, y - 2), radius=4, outline=white, width=3)
    elif kind == "phases":
        for dx in [-16, 0, 16]:
            draw.line((x + dx, y - 18, x + dx, y + 18), fill=white, width=5)
    else:
        draw.text((x - 12, y - 18), "i", fill=white, font=FONTS["b36"])


def make_manner_scenario_banner(case: dict, src_dir: Path, dest: Path) -> None:
    scene = fit_cover(Image.open(src_dir / case["hero_bg"]), (1140, 456)).filter(ImageFilter.GaussianBlur(4))
    product = fit_contain(Image.open(src_dir / case["hero_product"]), (430, 340))
    accent = rgba(case["accent"])
    base = Image.new("RGBA", (1140, 456), (7, 9, 12, 255))
    base.alpha_composite(scene.convert("RGBA").point(lambda p: int(p * 0.68)))
    veil = Image.new("RGBA", (1140, 456), (0, 0, 0, 98))
    base.alpha_composite(veil)
    draw = ImageDraw.Draw(base)
    draw_halftone(draw, 1140, 456, accent)
    add_diagonal_glow(base, accent)
    draw.rounded_rectangle((46, 52, 640, 394), radius=24, fill=(2, 12, 15, 218), outline=accent, width=3)
    frames: list[Image.Image] = []
    for i in range(16):
        frame = base.copy()
        frame.alpha_composite(product, (655, 72))
        fd = ImageDraw.Draw(frame)
        x = 88
        for idx, ch in enumerate("EXCITÉ"):
            lit = idx == (i // 2) % 6
            fill = (255, 220, 122, 255) if lit else rgba(case["logo_color"])
            fd.text((x, 88 - (3 if lit else 0)), ch, fill=fill, font=FONTS["b76"])
            x += 56 if ch != "I" else 30
        fd.text((88, 170), case["banner_title"], fill=(255, 255, 255, 255), font=FONTS["b36"])
        draw_wrapped(fd, (88, 222), case["banner_sub"], "r24", (231, 237, 244, 255), 500, 6, 2)
        for idx, (top, bottom) in enumerate(case["chips"]):
            bx = 88 + idx * 164
            by = 310
            fd.rounded_rectangle((bx, by, bx + 142, by + 58), radius=14, fill=(255, 255, 255, 245), outline=accent, width=3)
            fd.text((bx + 16, by + 8), top, fill=accent, font=FONTS["b22"])
            fd.text((bx + 16, by + 34), bottom, fill=(58, 65, 74, 255), font=FONTS["r18"])
        shine = Image.new("RGBA", (1140, 456), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shine)
        sx = -240 + i * 115
        sd.polygon([(sx, 0), (sx + 78, 0), (sx + 300, 456), (sx + 222, 456)], fill=(255, 255, 255, 30))
        frames.append(Image.alpha_composite(frame, shine).convert("RGB"))
    save_gif(frames, dest, 95)


def make_spec_icon_board(case: dict, dest: Path) -> None:
    accent = rgba(case["accent"])
    bg = Image.new("RGBA", (1140, 680), (247, 249, 250, 255))
    draw = ImageDraw.Draw(bg)
    draw.rounded_rectangle((34, 34, 1106, 646), radius=24, fill=(255, 255, 255, 255), outline=(224, 228, 232, 255), width=2)
    draw.rectangle((34, 34, 48, 646), fill=accent)
    draw.text((78, 72), "SPECIFICATII CU ROL CLAR", fill=(34, 40, 49, 255), font=FONTS["b44"])
    draw.text((80, 128), "Parametrii nu stau izolati: fiecare cifra explica o decizie de cumparare.", fill=(82, 91, 105, 255), font=FONTS["r24"])
    cards = [(78, 198), (594, 198), (78, 338), (594, 338), (78, 478), (594, 478)]
    for (x, y), item in zip(cards, case["spec_cards"]):
        draw.rounded_rectangle((x, y, x + 470, y + 112), radius=18, fill=(250, 252, 253, 255), outline=(222, 226, 231, 255), width=2)
        draw_icon(draw, item["icon"], (x + 58, y + 56), accent)
        draw.text((x + 112, y + 18), item["label"], fill=(35, 40, 48, 255), font=FONTS["b24"])
        draw.text((x + 112, y + 50), item["value"], fill=accent, font=FONTS["b30"])
        draw_wrapped(draw, (x + 112, y + 86), item["note"], "r18", (82, 91, 105, 255), 330, 4, 1)
    bg.convert("RGB").save(dest)


def make_manner_qa_board(case: dict, dest: Path) -> None:
    accent = rgba(case["accent"])
    frame = Image.new("RGBA", (1140, 520), (8, 10, 16, 255))
    draw = ImageDraw.Draw(frame)
    draw_halftone(draw, 1140, 520, accent)
    add_diagonal_glow(frame, accent)
    draw.text((64, 62), "Buyer questions", fill=(255, 255, 255, 255), font=FONTS["b44"])
    draw_wrapped(draw, (66, 120), "Raspunde obiectiilor inainte ca utilizatorul sa caute raspunsuri in alta parte.", "r22", (213, 220, 232, 255), 420, 8, 3)
    positions = [(510, 58), (790, 58), (510, 276), (790, 276)]
    questions = list(case["qa"]) + [(case["qa"][0][0], case["qa"][0][1])]
    for idx, ((q, a), (x, y)) in enumerate(zip(questions[:4], positions), start=1):
        draw.rounded_rectangle((x, y, x + 260, y + 176), radius=18, fill=(24, 22, 31, 235), outline=(accent[0], accent[1], accent[2], 180), width=2)
        draw.rounded_rectangle((x + 18, y + 20, x + 68, y + 48), radius=12, fill=accent)
        draw.text((x + 31, y + 24), f"Q{idx}", fill=(255, 255, 255, 255), font=FONTS["b22"])
        draw_wrapped(draw, (x + 82, y + 18), q, "r18", (255, 255, 255, 255), 150, 4, 2)
        draw_wrapped(draw, (x + 22, y + 78), a, "r18", (214, 221, 231, 255), 216, 5, 3)
    frame.convert("RGB").save(dest)


def make_manner_review_board(case: dict, dest: Path) -> None:
    accent = rgba(case["accent"])
    frame = Image.new("RGBA", (1140, 520), (8, 10, 16, 255))
    draw = ImageDraw.Draw(frame)
    draw_halftone(draw, 1140, 520, accent)
    add_diagonal_glow(frame, accent)
    draw.text((64, 58), "Feedback preview", fill=(255, 255, 255, 255), font=FONTS["b44"])
    draw_wrapped(draw, (66, 116), "Concept vizual pentru zona de review. In productie se folosesc doar review-uri reale, data si sursa verificabila.", "r22", (213, 220, 232, 255), 460, 8, 3)
    cards = [(86, 245, 358, 438), (434, 174, 706, 367), (782, 245, 1054, 438)]
    for idx, (box, item) in enumerate(zip(cards, case["reviews"]), start=1):
        x1, y1, x2, y2 = box
        draw.rounded_rectangle(box, radius=20, fill=(255, 255, 255, 245), outline=accent, width=3)
        draw.ellipse((x1 + 24, y1 + 24, x1 + 66, y1 + 66), fill=accent)
        draw.text((x1 + 82, y1 + 24), f"Tema {idx}", fill=(35, 40, 48, 255), font=FONTS["b22"])
        draw.text((x2 - 48, y1 + 20), "''", fill=accent, font=FONTS["b36"])
        draw.text((x1 + 24, y1 + 86), item[0], fill=(35, 40, 48, 255), font=FONTS["b22"])
        draw_wrapped(draw, (x1 + 24, y1 + 122), " ".join(item[1:]), "r18", (75, 82, 94, 255), 218, 6, 2)
    frame.convert("RGB").save(dest)


def make_manner_brand_banner(case: dict, dest: Path) -> None:
    accent = rgba(case["accent"])
    base = Image.new("RGBA", (1140, 420), (7, 8, 11, 255))
    draw = ImageDraw.Draw(base)
    draw_halftone(draw, 1140, 420, accent)
    add_diagonal_glow(base, accent)
    draw.rounded_rectangle((40, 42, 1100, 378), radius=24, outline=(255, 255, 255, 36), width=2)
    draw.text((76, 78), "EXCITÉ", fill=rgba(case["logo_color"]), font=FONTS["b76"])
    draw.text((78, 160), case["brand_line"], fill=(255, 255, 255, 255), font=FONTS["b30"])
    draw_wrapped(draw, (80, 212), case["brand_sub"], "r22", (218, 225, 235, 255), 480, 8, 2)
    for idx, cue in enumerate(case["brand_cues"]):
        x = 630 + idx * 150
        draw.rounded_rectangle((x, 148, x + 126, 240), radius=16, fill=(15, 18, 26, 235), outline=accent, width=3)
        draw.text((x + 20, 170), cue[0], fill=(255, 255, 255, 255), font=FONTS["b22"])
        draw.text((x + 20, 198), cue[1], fill=(210, 218, 226, 255), font=FONTS["r18"])
    draw.text((80, 316), "claritate vizuala + informatii scurte + dovezi inainte de promisiuni", fill=(245, 248, 250, 235), font=FONTS["b22"])
    frames: list[Image.Image] = []
    for i in range(14):
        frame = base.copy()
        shine = Image.new("RGBA", (1140, 420), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shine)
        sx = -220 + i * 108
        sd.polygon([(sx, 0), (sx + 70, 0), (sx + 280, 420), (sx + 210, 420)], fill=(255, 255, 255, 32))
        frames.append(Image.alpha_composite(frame, shine).convert("RGB"))
    save_gif(frames, dest, 95)


def html_note(text: str) -> str:
    return (
        '<blockquote style="margin:12px 0;padding:14px;border-left:5px solid #f4b740;background:#fff8e8;">'
        f'<p style="margin:0;"><strong>Nota:</strong> {esc(text)}</p></blockquote>'
    )


def asset_record(
    path: Path,
    case_dir: Path,
    component_id: str,
    buyer_question: str,
    risk_level: str,
    notes: list[str] | None = None,
) -> dict:
    with Image.open(path) as img:
        dimensions = {"width": img.width, "height": img.height}
        asset_format = img.format
    return {
        "component_id": component_id,
        "component_version": "v3",
        "buyer_question": buyer_question,
        "asset_path": rel(path, case_dir),
        "asset_format": asset_format,
        "dimensions": dimensions,
        "evidence_refs": ["ProductTruthPack", "captured_product_assets"],
        "risk_level": risk_level,
        "mobile_preview_status": "requires_390px_visual_check",
        "production_notes": notes or [],
    }


SPEC_CARDS = {
    "D5YN6S3BM": [
        {"icon": "bolt", "label": "Putere", "value": "450W", "note": "abur + mixare pentru rutina scurta"},
        {"icon": "cup", "label": "Capacitate", "value": "50-400 ml", "note": "portii mici sau volum complet"},
        {"icon": "steam", "label": "Functii", "value": "5 moduri", "note": "abur, blend, incalzire, sterilizare"},
        {"icon": "shield", "label": "Siguranta", "value": "Fara BPA", "note": "blocare si alarma apa scazuta"},
        {"icon": "touch", "label": "Control", "value": "LED", "note": "panou vizibil pentru pasi clari"},
        {"icon": "ruler", "label": "Dimensiuni", "value": "31 x 13 x 20.3 cm", "note": "format de blat pentru bucatarie"},
    ],
    "D6MHW43BM": [
        {"icon": "plug", "label": "Conector", "value": "Type 2", "note": "IEC 62196-2 pentru EV/PHEV"},
        {"icon": "bolt", "label": "Putere", "value": "22kW", "note": "incarcare AC trifazata"},
        {"icon": "phases", "label": "Curent", "value": "32A", "note": "parametru cheie de compatibilitate"},
        {"icon": "cable", "label": "Lungime", "value": "5 m", "note": "raza utila langa statie"},
        {"icon": "shield", "label": "Protectie", "value": "IP65", "note": "apa si praf conform sursei"},
        {"icon": "ruler", "label": "Material", "value": "TPU", "note": "cablul ramane usor de transportat"},
    ],
}


def build(case: dict) -> None:
    sku = case["sku"]
    source_assets = V2_ASSETS / sku
    case_assets = ASSETS / sku
    case_assets.mkdir(parents=True, exist_ok=True)
    for path in source_assets.glob("*"):
        if path.is_file():
            shutil.copy2(path, case_assets / path.name)
    case_dir = OUT / sku
    case_dir.mkdir(parents=True, exist_ok=True)
    case["spec_cards"] = SPEC_CARDS[sku]

    scenario_banner = case_assets / "v3_manner_scenario_banner.gif"
    green_buffer = case_assets / "v3_visual_buffer.png"
    step_gif = case_assets / "v3_step_highlight.gif"
    spec_board = case_assets / "v3_spec_icon_board.png"
    qa_board = case_assets / "v3_qa_board.png"
    review_board = case_assets / "v3_review_manner_board.png"
    brand_banner = case_assets / "v3_brand_manner.gif"

    make_manner_scenario_banner(case, case_assets, scenario_banner)
    make_green_buffer(case, case_assets, green_buffer)
    make_step_gif(case, case_assets, step_gif)
    make_spec_icon_board(case, spec_board)
    make_manner_qa_board(case, qa_board)
    make_manner_review_board(case, review_board)
    make_manner_brand_banner(case, brand_banner)

    body = ""
    body += html_img(scenario_banner, case_dir, "Excite Manner scenario banner")
    body += h2(case["name"].upper())
    body += p("V3 foloseste componente mai stabile: banner compus local, ancore mobile, imagini reale alternante, specificatii cu pictograme, Q&A si review in stil Manner.")
    body += anchor_triplet(case)
    body += mixed_feature_blocks(case, case_dir, case_assets)
    body += html_img(green_buffer, case_dir, "visual buffer")
    body += h2("PASII SI MOMENTELE CHEIE")
    body += html_img(step_gif, case_dir, "step highlight gif")
    body += h2("SPECIFICATII CARE CONFIRMA DECIZIA")
    body += html_img(spec_board, case_dir, "specification icon board")
    body += spec_table(case["specs"])
    body += h2("CONTINUT PACHET")
    body += spec_table(case["package"])
    body += h2("Q&A / INTREBARI INAINTE DE CUMPARARE")
    body += html_img(qa_board, case_dir, "buyer question board")
    body += qa_module(case)
    body += h2("COMENTARII / REVIEW PREVIEW")
    body += html_img(review_board, case_dir, "review concept board")
    body += html_note("continutul de review este concept preview. Pentru productie se inlocuieste cu review-uri reale, sursa, data si rating verificabil.")
    body += h2("DESPRE EXCITÉ")
    body += html_img(brand_banner, case_dir, "Excite Manner brand banner")

    html = page(body)
    (case_dir / "detail.html").write_text(html + "\n", encoding="utf-8")
    (case_dir / "detail_v3.html").write_text(html + "\n", encoding="utf-8")
    (case_dir / "preview_mobile.html").write_text(preview(f"Excité v3 {sku}", html), encoding="utf-8")
    media_index = {
        "sku": sku,
        "brand": "Excité",
        "generation_mode": "deterministic_pillow_composition",
        "component_records": [
            asset_record(
                scenario_banner,
                case_dir,
                "manner_scenario_banner",
                "What result do I get and why should I keep reading?",
                "medium",
                ["Uses captured product assets; clean old baked branding before production if visible."],
            ),
            asset_record(
                green_buffer,
                case_dir,
                "warm_visual_buffer",
                "Can the page rest the eye before dense detail?",
                "low",
                ["Color should stay category-compatible."],
            ),
            asset_record(
                step_gif,
                case_dir,
                "step_highlight_gif",
                "How do I use it without guessing?",
                "low",
                ["Stable GIF recipe: sequential highlight only."],
            ),
            asset_record(
                spec_board,
                case_dir,
                "spec_icon_board",
                "Which specs decide whether this product fits my needs?",
                "low",
                ["Source spec table follows the board."],
            ),
            asset_record(
                qa_board,
                case_dir,
                "qa_buyer_question_board",
                "What would the buyer otherwise go back to check?",
                "low",
                ["QA answers must trace to ProductTruthPack."],
            ),
            asset_record(
                review_board,
                case_dir,
                "manner_review_preview_board",
                "Did real buyers care about the same points?",
                "medium",
                ["Preview mode only; replace with real review source, date and rating before production."],
            ),
            asset_record(
                brand_banner,
                case_dir,
                "manner_brand_closer",
                "Can I trust this brand style and support process?",
                "low",
                ["No delivery/return/warranty promises unless evidence is supplied."],
            ),
        ],
    }
    (case_dir / "media_asset_index.json").write_text(json.dumps(media_index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    spec = {
        "sku": sku,
        "brand": "Excité",
        "version": "v3",
        "design_direction": "Manner-style dark premium boards plus product-color spec icon culture",
        "image_generation": "No AI image model used in this pass; deterministic Pillow compositing over captured product assets.",
        "modules": [
            "manner_scenario_banner_gif",
            "first_screen_anchor_triplet",
            "mixed_image_text_blocks",
            "fresh_visual_buffer",
            "step_highlight_gif",
            "spec_icon_board",
            "source_spec_table",
            "package_table",
            "qa_manner_board",
            "qa_text_module",
            "review_manner_board",
            "brand_manner_banner_gif",
        ],
        "production_notes": [
            "Replace review preview with real review data before publishing.",
            "Use image agent for final product-photo cleanup where old baked branding remains.",
            "Keep black/gold or accent shine sweep as the first stable motion recipe; other GIF styles remain experimental.",
        ],
    }
    (case_dir / "DESIGN_SPEC.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    validate = subprocess.run(
        ["python3", str(VALIDATOR), str(case_dir / "detail.html"), "--out", str(case_dir / "validation_report.json")],
        capture_output=True,
        text=True,
    )
    if validate.returncode:
        raise RuntimeError(validate.stderr or validate.stdout)


def write_index() -> None:
    items = []
    for case in CASES:
        sku = case["sku"]
        items.append(
            f'<li style="margin:10px 0;"><strong>{sku}</strong> - '
            f'<a href="{sku}/preview_mobile.html">v3 preview</a> | '
            f'<a href="{sku}/DESIGN_SPEC.json">DESIGN_SPEC</a> | '
            f'<a href="{sku}/validation_report.json">validation</a></li>'
        )
    html = preview(
        "Excité SOP test v3",
        page(
            h2("Excité SOP test v3")
            + p("V3 replaces the plain spec table and rough bottom modules with icon spec boards and Manner-style QA/review/brand boards.")
            + "<ul>"
            + "".join(items)
            + "</ul>"
        ),
    )
    (OUT / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    for case in CASES:
        build(case)
    write_index()
    print(OUT)


if __name__ == "__main__":
    main()
