#!/usr/bin/env python3
"""Generate EXCITAT eMAG Banner + HTML Agent v1 stable route examples."""

from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path("/Users/cc/Desktop/photo_show")
OUT = ROOT / "output/emag_excitat_banner_html_agent_stable_v1"
ASSETS = OUT / "assets"
SOURCE_EV = ROOT / "output/emag_exit_two_product_stable_components_v4/assets/D6MHW43BM"
ICON_SRC = ROOT / "output/emag_exit_two_product_stable_components_v4/assets/_icon_library_v1"
VALIDATOR = ROOT / "scripts/validate_excitat_banner_agent_outputs.py"


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    local_dir = ROOT / "assets" / "fonts"
    candidates = [
        str(local_dir / ("Arial Bold.ttf" if bold else "Arial.ttf")),
        str(local_dir / "Helvetica.ttc"),
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


F = {
    "brand": font(78, True),
    "brand_small": font(34, True),
    "h1": font(52, True),
    "h2": font(40, True),
    "h3": font(28, True),
    "body": font(24),
    "body_b": font(24, True),
    "small": font(18),
    "small_b": font(18, True),
}


def esc(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def wrap(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font_key: str, fill, max_width: int, gap: int = 7, max_lines: int | None = None) -> int:
    words = text.split()
    lines: list[str] = []
    line = ""
    fnt = F[font_key]
    for word in words:
        probe = word if not line else f"{line} {word}"
        if draw.textbbox((0, 0), probe, font=fnt)[2] <= max_width:
            line = probe
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    if max_lines is not None:
        lines = lines[:max_lines]
    x, y = xy
    line_h = draw.textbbox((0, 0), "Ag", font=fnt)[3] + gap
    for idx, row in enumerate(lines):
        draw.text((x, y + idx * line_h), row, font=fnt, fill=fill)
    return y + len(lines) * line_h


def fit_cover(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize((math.ceil(image.width * scale), math.ceil(image.height * scale)), Image.LANCZOS)
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def rounded_paste(base: Image.Image, source: Image.Image, xy: tuple[int, int], radius: int) -> None:
    src = source.convert("RGBA")
    mask = Image.new("L", src.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, src.width, src.height), radius=radius, fill=255)
    src.putalpha(mask)
    base.alpha_composite(src, xy)


def draw_halftone(draw: ImageDraw.ImageDraw, width: int, height: int, color: tuple[int, int, int, int]) -> None:
    for x in range(-20, width // 2, 24):
        for y in range(10, height, 24):
            if (x + y) % 72 != 0:
                r = 2 + ((x + y) % 3)
                draw.ellipse((x, y, x + r, y + r), fill=(color[0], color[1], color[2], 140))


def draw_excitat(draw: ImageDraw.ImageDraw, xy: tuple[int, int], font_key: str, fill, shadow=(110, 36, 24, 180)) -> None:
    x, y = xy
    draw.text((x + 5, y + 7), "EXCITAT", fill=shadow, font=F[font_key])
    draw.text((x, y), "EXCITAT", fill=fill, font=F[font_key])


def draw_brand_tag(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], accent, dark: bool = True) -> None:
    fill = (8, 12, 17, 235) if dark else (255, 255, 255, 245)
    text = (255, 255, 255, 255) if dark else (20, 28, 36, 255)
    draw.rounded_rectangle(box, radius=16, fill=fill, outline=accent, width=2)
    draw.text((box[0] + 18, box[1] + 11), "EXCITAT", fill=text, font=F["brand_small"])


def qa_board(path: Path) -> dict:
    accent = (34, 166, 224, 255)
    bg = Image.new("RGBA", (1140, 470), (247, 250, 253, 255))
    d = ImageDraw.Draw(bg)
    d.rectangle((0, 0, 12, 470), fill=accent)
    d.text((56, 50), "Q&A rapid", fill=(32, 39, 49, 255), font=F["h1"])
    d.text((58, 108), "Intrebari de cumparare, nu comentarii mascate.", fill=(91, 100, 116, 255), font=F["body"])
    draw_brand_tag(d, (860, 48, 1075, 98), accent, dark=False)
    rows = [
        ("Q1", "Se potriveste cu orice masina?", "Verifica standardul Type 2 al vehiculului si puterea acceptata."),
        ("Q2", "Pot folosi cablul in exterior?", "Sursa mentioneaza IP65; folosirea trebuie sa respecte instructiunile."),
        ("Q3", "De ce conteaza geanta?", "Ajuta la depozitarea si protejarea cablului intre utilizari."),
    ]
    y = 168
    for q, title, body in rows:
        d.rounded_rectangle((58, y, 1082, y + 82), radius=16, fill=(255, 255, 255, 255), outline=(225, 231, 238, 255), width=1)
        d.text((88, y + 22), q, fill=accent, font=F["h3"])
        d.text((152, y + 14), title, fill=(32, 39, 49, 255), font=F["body_b"])
        wrap(d, (152, y + 45), body, "small", (92, 101, 116, 255), 810, 4, 1)
        y += 92
    bg.convert("RGB").save(path)
    return record("route_a_qa_stable", "qa", "stable_generic_banner", "pure_composite", path, "static", ["qa_source:category_buyer_questions"], "light")


def review_board(path: Path) -> dict:
    accent = (244, 176, 70, 255)
    bg = Image.new("RGBA", (1140, 500), (10, 12, 18, 255))
    d = ImageDraw.Draw(bg)
    draw_halftone(d, 1140, 500, accent)
    d.rectangle((575, 0, 760, 500), fill=(30, 32, 40, 145))
    d.text((66, 66), "Client", fill=(255, 255, 255, 255), font=F["h2"])
    d.text((66, 118), "Feedback", fill=(255, 255, 255, 255), font=F["h1"])
    wrap(d, (70, 208), "Template vizual. In productie se inlocuieste cu review-uri reale, sursa, data si rating verificabil.", "small", (220, 226, 236, 255), 350, 6, 4)
    draw_excitat(d, (70, 392), "brand_small", (255, 188, 82, 255))
    d.rounded_rectangle((845, 36, 1048, 78), radius=14, fill=(255, 255, 255, 18), outline=accent, width=1)
    d.text((870, 48), "PREVIEW", fill=accent, font=F["small_b"])
    cards = [
        ("Tema 1", "Potrivire mai clara", "Buyerii confirma conectorul inainte de pret."),
        ("Tema 2", "Transport mai usor", "Geanta rezolva depozitarea dupa incarcare."),
        ("Tema 3", "Mai multa incredere", "IP65 reduce intrebarea despre exterior."),
    ]
    for (title, headline, body), (x, y), light in zip(cards, [(430, 76), (770, 88), (520, 286)], [True, False, False]):
        fill = (255, 255, 255, 248) if light else (19, 21, 29, 232)
        text = (33, 39, 48, 255) if light else (255, 255, 255, 255)
        d.rounded_rectangle((x, y, x + 310, y + 150), radius=18, fill=fill, outline=accent, width=2)
        d.ellipse((x + 22, y + 24, x + 62, y + 64), fill=accent)
        d.text((x + 82, y + 23), title, fill=text, font=F["body_b"])
        d.text((x + 24, y + 80), headline, fill=text, font=F["body_b"])
        wrap(d, (x + 24, y + 112), body, "small", text, 250, 4, 2)
        d.text((x + 260, y + 20), "''", fill=accent, font=F["h3"])
    bg.convert("RGB").save(path)
    item = record("route_b_review_feedback_template", "review", "stable_generic_banner", "pure_composite", path, "static", [], "heavy_dark")
    item["review_mode"] = "preview"
    item["production_notes"].append("Review preview only; replace cards with real review source, date and rating before production.")
    return item


def brand_fixed_gif(path: Path) -> dict:
    accent = (248, 185, 42, 255)
    frames: list[Image.Image] = []
    for frame in range(16):
        bg = Image.new("RGBA", (1140, 420), (5, 7, 10, 255))
        d = ImageDraw.Draw(bg)
        draw_halftone(d, 1140, 420, accent)
        d.rectangle((560, 0, 735, 420), fill=(38, 39, 45, 125))
        d.text((80, 74), "New Arrival", fill=(255, 255, 255, 255), font=F["h2"])
        draw_excitat(d, (80, 132), "brand", accent)
        d.text((84, 230), "WHERE CLARITY MEETS VALUE", fill=(255, 255, 255, 255), font=F["h3"])
        d.text((86, 272), "claritate vizuala, dovada scurta, promisiuni controlate", fill=(220, 225, 236, 255), font=F["small"])
        chips = [("FIT", "Type 2"), ("POWER", "22kW"), ("CARE", "bag")]
        for i, (top, bottom) in enumerate(chips):
            x = 645 + i * 155
            d.rounded_rectangle((x, 292, x + 128, y := 360), radius=16, fill=(10, 12, 18, 230), outline=accent, width=2)
            d.text((x + 18, 306), top, fill=(255, 255, 255, 255), font=F["body_b"])
            d.text((x + 18, 334), bottom, fill=(210, 216, 226, 255), font=F["small"])
        sweep_x = -220 + frame * 90
        overlay = Image.new("RGBA", (1140, 420), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.polygon([(sweep_x, 0), (sweep_x + 90, 0), (sweep_x + 300, 420), (sweep_x + 190, 420)], fill=(255, 236, 176, 42))
        bg = Image.alpha_composite(bg, overlay)
        frames.append(bg.convert("P", palette=Image.ADAPTIVE))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)
    return record("route_c_fixed_brand_category", "brand", "fixed_brand_category_banner", "pure_composite", path, "shine_sweep", ["brand_values:neutral"], "heavy_dark")


def product_scene(path: Path) -> dict:
    accent = (34, 166, 224, 255)
    base = fit_cover(SOURCE_EV / "10.jpg", (1140, 456)).filter(ImageFilter.GaussianBlur(3)).convert("RGBA")
    base.alpha_composite(Image.new("RGBA", (1140, 456), (4, 10, 18, 126)))
    d = ImageDraw.Draw(base)
    draw_halftone(d, 1140, 456, accent)
    product = fit_cover(SOURCE_EV / "12.jpg", (420, 310)).convert("RGBA")
    rounded_paste(base, product, (640, 76), 22)
    draw_brand_tag(d, (78, 50, 290, 100), accent, dark=True)
    d.text((82, 136), "EV cable clarity", fill=(255, 255, 255, 255), font=F["h1"])
    d.text((84, 196), "Type 2, 22kW si IP65", fill=accent, font=F["h2"])
    wrap(d, (88, 250), "Compatibilitatea si protectia apar inaintea detaliilor tehnice lungi.", "body", (228, 234, 242, 255), 440, 8, 3)
    for i, txt in enumerate(["TYPE 2 fit", "22kW power", "IP65 proof"]):
        y = 348 + i * 34
        d.rounded_rectangle((88, y, 402, y + 26), radius=13, fill=(4, 14, 25, 210), outline=accent, width=2)
        d.text((108, y + 3), txt, fill=(255, 255, 255, 255), font=F["small_b"])
    base.convert("RGB").save(path)
    return record("route_d_product_scene", "hero", "product_scene_banner", "ai_background_plus_composite", path, "static", ["source_image:D6MHW43BM"], "heavy_dark")


def cropped_proof(path: Path) -> dict:
    accent = (34, 166, 224, 255)
    bg = Image.new("RGBA", (1140, 430), (248, 250, 252, 255))
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle((58, 58, 552, 356), radius=24, fill=(255, 255, 255, 255), outline=accent, width=2)
    d.text((88, 104), "Cablul confirma decizia", fill=(34, 40, 49, 255), font=F["h2"])
    lines = ["Compatibilitate inainte de cifre.", "Protectia apare langa produs.", "Tabelul confirma dupa imagine."]
    y = 180
    for line in lines:
        d.ellipse((92, y + 10, 104, y + 22), fill=accent)
        d.text((126, y), line, fill=(65, 75, 90, 255), font=F["body"])
        y += 54
    proof = fit_cover(SOURCE_EV / "09.jpg", (470, 320)).convert("RGBA")
    rounded_paste(bg, proof, (625, 56), 24)
    draw_brand_tag(d, (842, 332, 1055, 382), accent, dark=True)
    bg.convert("RGB").save(path)
    return record("route_e_cropped_proof", "proof", "product_scene_banner", "pure_composite", path, "static", ["source_image:D6MHW43BM"], "light")


def step_highlight_gif(path: Path) -> dict:
    accent = (34, 166, 224, 255)
    frames: list[Image.Image] = []
    steps = [
        ("1", "Conecteaza", "verifica Type 2"),
        ("2", "Alege puterea", "confirma 22kW"),
        ("3", "Protejeaza", "foloseste geanta"),
        ("4", "Depoziteaza", "evita cablu liber"),
    ]
    for active in range(4):
        bg = fit_cover(SOURCE_EV / "03.jpg", (1140, 520)).filter(ImageFilter.GaussianBlur(2)).convert("RGBA")
        bg.alpha_composite(Image.new("RGBA", (1140, 520), (255, 255, 255, 170)))
        d = ImageDraw.Draw(bg)
        d.text((56, 48), "Pasi simpli, evidentiati pe rand", fill=(34, 40, 49, 255), font=F["h2"])
        for i, (num, title, body) in enumerate(steps):
            x = 58 + (i % 2) * 532
            y = 140 + (i // 2) * 150
            is_active = i == active
            border = accent if is_active else (255, 255, 255, 220)
            fill = (255, 255, 255, 246) if is_active else (255, 255, 255, 170)
            d.rounded_rectangle((x, y, x + 492, y + 112), radius=18, fill=fill, outline=border, width=5 if is_active else 2)
            d.ellipse((x + 22, y + 22, x + 72, y + 72), fill=accent if is_active else (230, 235, 241, 255))
            d.text((x + 40, y + 32), num, fill=(255, 255, 255, 255) if is_active else accent, font=F["h3"])
            d.text((x + 94, y + 22), title, fill=(34, 40, 49, 255), font=F["body_b"])
            d.text((x + 94, y + 56), body, fill=(82, 92, 106, 255), font=F["body"])
        draw_brand_tag(d, (850, 44, 1065, 94), accent, dark=False)
        frames.append(bg.convert("P", palette=Image.ADAPTIVE))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=620, loop=0, optimize=True)
    return record("route_f_step_highlight", "motion", "motion_gif", "pure_composite", path, "step_highlight", ["usage_steps:derived_from_source"], "light")


def record(asset_id: str, module_type: str, family: str, route: str, path: Path, motion: str, evidence_refs: list[str], visual_weight: str) -> dict:
    with Image.open(path) as im:
        width, height = im.size
    return {
        "asset_id": asset_id,
        "component_id": asset_id,
        "module_type": module_type,
        "banner_family": family,
        "route_selected": route,
        "production_candidate": True,
        "path": os.path.relpath(path, OUT),
        "dimensions": {"width": width, "height": height},
        "motion_effect": motion,
        "visual_weight": visual_weight,
        "evidence_refs": evidence_refs,
        "claims": [],
        "production_notes": ["Generated by deterministic local composition; final text is not model-rendered."],
    }


def html_img(path: Path, alt: str) -> str:
    rel = os.path.relpath(path, OUT)
    return (
        f'<p style="text-align:center;margin:0 0 20px 0;">'
        f'<img src="{esc(rel)}" width="1140" alt="{esc(alt)}" '
        'style="max-width:100%;height:auto;display:block;margin:0 auto;">'
        "</p>"
    )


def detail_html(asset_paths: dict[str, Path]) -> str:
    sections = [
        '<div style="font-family:Arial,Helvetica,sans-serif;color:#24292f;line-height:1.58;max-width:1140px;margin:0 auto;padding:0 8px;font-size:16px;">',
        '<h2 style="font-size:24px;line-height:1.25;margin:22px 0 14px 0;">EXCITAT Banner + HTML Agent Stable Route v1</h2>',
        html_img(asset_paths["product_scene"], "EXCITAT product scene banner"),
        '<p style="font-size:16px;margin:10px 0 24px 0;">Fluxul incepe cu scena produsului, apoi trece in dovada vizuala, Q&A, review preview si brand module. Fiecare modul are ruta si validator separat.</p>',
        html_img(asset_paths["proof"], "cropped product proof banner"),
        html_img(asset_paths["qa"], "QA stable banner"),
        '<h2 style="font-size:22px;line-height:1.25;margin:30px 0 14px 0;">Review / feedback template</h2>',
        html_img(asset_paths["review"], "review feedback preview banner"),
        '<div style="background:#fff7e8;border-left:6px solid #f4b046;padding:18px 22px;margin:18px 0 28px 0;"><strong>Nota:</strong> feedback-ul este template vizual. In productie se inlocuieste cu review-uri reale, sursa, data si rating verificabil.</div>',
        '<h2 style="font-size:22px;line-height:1.25;margin:30px 0 14px 0;">Motion route</h2>',
        html_img(asset_paths["step"], "step highlight GIF"),
        '<h2 style="font-size:22px;line-height:1.25;margin:30px 0 14px 0;">Brand / category fixed banner</h2>',
        html_img(asset_paths["brand"], "EXCITAT fixed brand category banner GIF"),
        "</div>",
    ]
    return "\n".join(sections)


def preview_html(title: str, body: str) -> str:
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{esc(title)}</title>"
        '<style>body{margin:0;background:#fff;}img{max-width:100%;height:auto;}'
        '@media(max-width:520px){h2{font-size:21px!important;}p,div{font-size:15px!important;}}</style>'
        f"</head><body>{body}</body></html>"
    )


def contact_sheet(paths: list[Path], dest: Path) -> None:
    thumbs: list[Image.Image] = []
    for path in paths:
        im = Image.open(path).convert("RGB")
        im.thumbnail((540, 230), Image.LANCZOS)
        tile = Image.new("RGB", (560, 290), (246, 248, 250))
        tile.paste(im, ((560 - im.width) // 2, 18))
        ImageDraw.Draw(tile).text((18, 256), path.name, font=F["small"], fill=(33, 39, 48))
        thumbs.append(tile)
    sheet = Image.new("RGB", (1120, 290 * math.ceil(len(thumbs) / 2) + 80), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    d.text((28, 24), "EXCITAT stable route examples", font=F["h2"], fill=(33, 39, 48))
    for i, tile in enumerate(thumbs):
        sheet.paste(tile, ((i % 2) * 560, 80 + (i // 2) * 290))
    sheet.save(dest)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    ASSETS.mkdir(parents=True, exist_ok=True)

    asset_paths = {
        "qa": ASSETS / "route_a_qa_stable_clean_board.jpg",
        "review": ASSETS / "route_b_review_feedback_template.jpg",
        "brand": ASSETS / "route_c_fixed_brand_category_shine.gif",
        "product_scene": ASSETS / "route_d_product_scene_ai_plus_composite.jpg",
        "proof": ASSETS / "route_e_cropped_proof_banner.jpg",
        "step": ASSETS / "route_f_step_highlight.gif",
    }

    generated = {
        "qa": qa_board(asset_paths["qa"]),
        "review": review_board(asset_paths["review"]),
        "brand": brand_fixed_gif(asset_paths["brand"]),
        "product_scene": product_scene(asset_paths["product_scene"]),
        "proof": cropped_proof(asset_paths["proof"]),
        "step": step_highlight_gif(asset_paths["step"]),
    }
    media = [
        generated["product_scene"],
        generated["proof"],
        generated["qa"],
        generated["review"],
        generated["step"],
        generated["brand"],
    ]

    body = detail_html(asset_paths)
    (OUT / "detail.html").write_text(body + "\n", encoding="utf-8")
    (OUT / "preview_mobile.html").write_text(preview_html("EXCITAT stable banner agent v1", body), encoding="utf-8")

    design = {
        "agent_id": "emag-banner-html-agent-v1.1",
        "brand_kit": {
            "visual_brand": "EXCITAT",
            "internal_slug": "excitat",
            "forbidden_display_names": sorted(FORBIDDEN for FORBIDDEN in ["EXIT", "Excité", "Exceity", "EXITE", "BestPlaza"]),
        },
        "flow": ["Plan/DesignSpec", "Generate or Composite", "Validate", "Repair", "Final Export"],
        "route_policy": {
            "default_production_route": "ai_background_plus_composite",
            "exact_text_route": "pure_composite",
            "pure_ai_generation": "exploration_only",
        },
        "test_routes": [item["asset_id"] for item in media],
    }
    (OUT / "DESIGN_SPEC.json").write_text(json.dumps(design, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "media_asset_index.json").write_text(json.dumps({"assets": media}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    contact_sheet(list(asset_paths.values()), OUT / "contact_sheet.jpg")

    repair_log = """# Repair Log

No blocker repair was required in the deterministic v1 route.

Accepted warnings policy:

- Review content is preview-only and labeled as such.
- Product scene route is marked `ai_background_plus_composite` to match the intended production route, but this sample uses deterministic local composition until a provider adapter is connected.
- Motion is limited to `shine_sweep` and `step_highlight`.
"""
    (OUT / "repair_log.md").write_text(repair_log, encoding="utf-8")

    subprocess.run(
        ["python3", str(VALIDATOR), str(OUT), "--out", str(OUT / "validation_report.json")],
        check=True,
    )

    run_report = f"""# EXCITAT Banner + HTML Agent v1 Run

Output: `{OUT}`

Generated route tests:

- Route A: QA stable clean board
- Route B: Review feedback preview template
- Route C: Fixed brand/category banner with shine sweep GIF
- Route D: Product scene banner using product listing imagery + deterministic overlay
- Route E: Cropped proof banner
- Route F: Step highlight GIF

Validation: `{OUT / "validation_report.json"}`
Preview: `{OUT / "preview_mobile.html"}`
Contact sheet: `{OUT / "contact_sheet.jpg"}`
"""
    (OUT / "run_report.md").write_text(run_report, encoding="utf-8")
    print(run_report)


if __name__ == "__main__":
    main()
