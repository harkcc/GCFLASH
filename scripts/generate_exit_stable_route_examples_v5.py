#!/usr/bin/env python3
"""Generate v5 EXIT eMAG detail examples using the premium stable banner route."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

import generate_excite_two_product_sop_test_v3 as v3
import generate_excite_two_product_sop_test_v4 as v4


ROOT = Path("/Users/cc/Desktop/photo_show")
OUT = ROOT / "output/emag_exit_stable_route_examples_v5"
ASSETS = OUT / "assets"
V4_ASSETS = ROOT / "output/emag_exit_two_product_stable_components_v4/assets"
VALIDATOR = ROOT / "scripts/validate_emag_detail_html.py"

F = v4.F


def esc(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def rel(path: Path, base: Path) -> str:
    return os.path.relpath(path, base)


def html_img(path: Path, base: Path, alt: str) -> str:
    return (
        f'<p style="text-align:center;margin:0 0 20px 0;">'
        f'<img src="{esc(rel(path, base))}" width="1140" alt="{esc(alt)}" '
        'style="max-width:100%;height:auto;display:block;margin:0 auto;">'
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
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{esc(title)}</title>'
        '<style>body{margin:0;background:#fff;}img{max-width:100%;height:auto;}'
        '@media(max-width:520px){h2{font-size:21px!important;}}</style></head>'
        f"<body>{body}</body></html>"
    )


def rgba(color, alpha: int | None = None):
    if len(color) == 4:
        return tuple(color)
    return (color[0], color[1], color[2], 255 if alpha is None else alpha)


def wrap(draw: ImageDraw.ImageDraw, xy, text: str, font_key: str, fill, max_width: int, gap: int = 8, max_lines: int | None = None) -> int:
    return v3.draw_wrapped(draw, xy, text, font_key, fill, max_width, gap, max_lines)


def copy_assets(sku: str) -> Path:
    src = V4_ASSETS / sku
    dest = ASSETS / sku
    dest.mkdir(parents=True, exist_ok=True)
    for path in src.glob("*"):
        if path.is_file():
            shutil.copy2(path, dest / path.name)
    return dest


def dim(path: Path) -> dict[str, int]:
    with Image.open(path) as im:
        return {"width": im.width, "height": im.height}


def save_gif(frames: list[Image.Image], path: Path, duration: int = 95) -> None:
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=duration, loop=0, optimize=True)


def draw_exit(draw: ImageDraw.ImageDraw, xy, size_key: str, fill, shadow=(120, 32, 22, 160)) -> None:
    x, y = xy
    draw.text((x + 5, y + 7), "EXIT", fill=shadow, font=F[size_key])
    draw.text((x, y), "EXIT", fill=fill, font=F[size_key])


def product_scene_hero(case: dict, assets: Path, dest: Path) -> None:
    accent = rgba(case["accent"])
    if case["sku"] == "D5YN6S3BM":
        bg = Image.new("RGBA", (1140, 456), (255, 247, 235, 255))
        draw = ImageDraw.Draw(bg)
        for r, a in [(560, 28), (420, 35), (260, 45)]:
            draw.ellipse((650 - r // 2, 35, 650 + r, 35 + r), fill=(255, 226, 184, a))
        source = v3.fit_cover(Image.open(assets / "03.jpg"), (500, 360)).filter(ImageFilter.GaussianBlur(1.2))
        source = ImageOps.autocontrast(source.convert("RGB")).convert("RGBA")
        mask = Image.new("L", source.size, 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle((0, 0, source.width, source.height), radius=28, fill=255)
        source.putalpha(mask)
        bg.alpha_composite(source, (590, 54))
        product = v3.fit_contain(Image.open(assets / "02.jpg"), (330, 310))
        shadow = Image.new("RGBA", product.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.ellipse((34, product.height - 48, product.width - 22, product.height - 6), fill=(0, 0, 0, 34))
        bg.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)), (680, 112))
        bg.alpha_composite(product, (680, 74))
        draw = ImageDraw.Draw(bg)
        draw.text((70, 66), "Pentru rutina de hranire", fill=(35, 40, 48, 255), font=F["b30"])
        draw.text((70, 112), "mai calma", fill=accent, font=F["b64"])
        wrap(draw, (74, 196), "Abur, mixare, incalzire si curatare intr-un flux clar pentru parinti.", "r24", (74, 82, 94, 255), 430, 8, 3)
        for i, (top, bottom) in enumerate(case["chips"]):
            x = 74 + i * 150
            draw.rounded_rectangle((x, 318, x + 126, 374), radius=16, fill=(255, 255, 255, 245), outline=accent, width=2)
            draw.text((x + 14, 327), top, fill=accent, font=F["b22"])
            draw.text((x + 14, 352), bottom, fill=(66, 72, 82, 255), font=F["r18"])
        draw_exit(draw, (70, 388), "b36", (98, 211, 218, 255), (244, 151, 54, 120))
        bg.convert("RGB").save(dest)
        return

    # Use clean scene/product assets instead of the earlier baked-brand hero.
    # This keeps EXIT from competing with the source image's old brand text.
    base_img = v3.fit_cover(Image.open(assets / "10.jpg"), (1140, 456)).filter(ImageFilter.GaussianBlur(3))
    bg = base_img.convert("RGBA")
    bg.alpha_composite(Image.new("RGBA", (1140, 456), (0, 0, 0, 116)))
    draw = ImageDraw.Draw(bg)
    v3.draw_halftone(draw, 1140, 456, accent)
    v3.add_diagonal_glow(bg, accent)
    product_source = Image.open(assets / "12.jpg").crop((280, 0, 900, 420))
    product = v3.fit_contain(product_source, (450, 330))
    bg.alpha_composite(product, (620, 76))
    draw = ImageDraw.Draw(bg)
    draw.text((76, 70), "EV cable clarity", fill=(255, 255, 255, 255), font=F["b56"])
    draw.text((78, 142), "Type 2, 22kW si IP65", fill=accent, font=F["b36"])
    wrap(draw, (82, 196), "Compatibilitatea si protectia apar inaintea detaliilor tehnice lungi.", "r24", (224, 231, 240, 255), 440, 8, 3)
    for i, (top, bottom) in enumerate(case["chips"]):
        y = 304 + i * 48
        draw.rounded_rectangle((82, y, 438, y + 34), radius=17, fill=(2, 14, 28, 190), outline=accent, width=2)
        draw.text((104, y + 5), f"{top}  {bottom}", fill=(255, 255, 255, 255), font=F["b22"])
    bg.convert("RGB").save(dest)


def crop_proof_board(case: dict, assets: Path, dest: Path) -> None:
    accent = rgba(case["accent"])
    bg_color = (248, 250, 252, 255) if case["sku"] == "D6MHW43BM" else (255, 251, 245, 255)
    canvas = Image.new("RGBA", (1140, 430), bg_color)
    draw = ImageDraw.Draw(canvas)
    if case["sku"] == "D5YN6S3BM":
        img = v3.fit_cover(Image.open(assets / "05.jpg"), (470, 320))
        title = "Dovada vizuala, nu inca un bloc de text"
        lines = ["Imaginea explica textura si fluxul.", "Textul ramane scurt.", "Parametrii vin dupa ce contextul e clar."]
        tx, ix = 74, 625
    else:
        img = v3.fit_cover(Image.open(assets / "09.jpg"), (470, 320))
        title = "Cablul si conectorul confirma decizia"
        lines = ["Compatibilitate inainte de cifre.", "Protectia apare langa produs.", "Tabelul confirma ce imaginea a introdus."]
        tx, ix = 74, 625
    draw.rounded_rectangle((56, 58, 552, 356), radius=24, fill=(255, 255, 255, 245), outline=accent, width=2)
    draw.text((90, 104), title, fill=(35, 44, 54, 255), font=F["b36"])
    y = 176
    for line in lines:
        draw.ellipse((94, y + 10, 104, y + 20), fill=accent)
        draw.text((122, y), line, fill=(59, 70, 84, 255), font=F["r24"])
        y += 52
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, img.width, img.height), radius=24, fill=255)
    img_rgba = img.convert("RGBA")
    img_rgba.putalpha(mask)
    canvas.alpha_composite(img_rgba, (ix, 56))
    draw.rounded_rectangle((ix, 56, ix + img.width, 56 + img.height), radius=24, outline=(255, 255, 255, 180), width=2)
    canvas.convert("RGB").save(dest)


def clean_spec_board(case: dict, icon_paths: dict[str, Path], dest: Path) -> None:
    accent = rgba(case["accent"])
    bg = Image.new("RGBA", (1140, 640), (255, 255, 255, 255))
    draw = ImageDraw.Draw(bg)
    draw.text((58, 54), "Specificatii cu rol clar", fill=(34, 40, 49, 255), font=F["b44"])
    draw.text((60, 108), "Cifrele importante apar vizual; tabelul complet ramane ca sursa rationala.", fill=(82, 91, 105, 255), font=F["r22"])
    cards = [(58, 176), (590, 176), (58, 308), (590, 308), (58, 440), (590, 440)]
    for (x, y), item in zip(cards, v3.SPEC_CARDS[case["sku"]]):
        draw.rounded_rectangle((x, y, x + 492, y + 100), radius=18, fill=(248, 250, 252, 255), outline=(221, 226, 232, 255), width=2)
        icon = v4.tint_icon(icon_paths[item["icon"]], accent).resize((64, 64), Image.LANCZOS)
        bg.alpha_composite(icon, (x + 22, y + 18))
        draw.text((x + 102, y + 15), item["label"], fill=(35, 40, 48, 255), font=F["b22"])
        draw.text((x + 102, y + 43), item["value"], fill=accent, font=F["b30"])
        wrap(draw, (x + 102, y + 77), item["note"], "r18", (82, 91, 105, 255), 340, 4, 1)
    bg.convert("RGB").save(dest)


def qa_clean_board(case: dict, dest: Path) -> None:
    accent = rgba(case["accent"])
    bg = Image.new("RGBA", (1140, 470), (248, 250, 252, 255))
    draw = ImageDraw.Draw(bg)
    draw.rectangle((0, 0, 12, 470), fill=accent)
    draw.text((58, 58), "Q&A rapid", fill=(34, 40, 49, 255), font=F["b44"])
    draw.text((60, 112), "Intrebari reale de cumparare, nu comentarii mascate.", fill=(82, 91, 105, 255), font=F["r22"])
    y = 176
    for idx, (q, a) in enumerate(case["qa"], start=1):
        draw.rounded_rectangle((60, y, 1080, y + 82), radius=16, fill=(255, 255, 255, 255), outline=(226, 231, 236, 255), width=1)
        draw.text((88, y + 22), f"Q{idx}", fill=accent, font=F["b24"])
        draw.text((150, y + 16), q, fill=(35, 40, 48, 255), font=F["b22"])
        wrap(draw, (150, y + 46), a, "r18", (82, 91, 105, 255), 820, 4, 1)
        y += 92
    bg.convert("RGB").save(dest)


def review_board_light(case: dict, dest: Path) -> None:
    accent = rgba(case["accent"])
    bg = Image.new("RGBA", (1140, 500), (12, 14, 20, 255))
    draw = ImageDraw.Draw(bg)
    v3.draw_halftone(draw, 1140, 500, accent)
    draw.text((66, 70), "Client", fill=(255, 255, 255, 255), font=F["b44"])
    draw.text((66, 126), "Feedback", fill=(255, 255, 255, 255), font=F["b56"])
    wrap(draw, (70, 214), "Template vizual pentru review. In productie se folosesc doar recenzii reale, rating si data verificabila.", "r20", (218, 224, 235, 255), 330, 6, 4)
    draw_exit(draw, (70, 400), "b36", (255, 190, 82, 255), (98, 30, 20, 200))
    positions = [(450, 68), (782, 68), (450, 282)]
    for i, ((title, *body), (x, y)) in enumerate(zip(case["reviews"], positions), start=1):
        fill = (255, 255, 255, 246) if i == 1 else (22, 24, 32, 230)
        text_fill = (35, 40, 48, 255) if i == 1 else (255, 255, 255, 255)
        draw.rounded_rectangle((x, y, x + 292, y + 148), radius=18, fill=fill, outline=accent, width=2)
        draw.ellipse((x + 22, y + 22, x + 60, y + 60), fill=accent)
        draw.text((x + 78, y + 22), f"Tema {i}", fill=text_fill, font=F["b22"])
        draw.text((x + 22, y + 78), title, fill=text_fill, font=F["b22"])
        wrap(draw, (x + 22, y + 108), " ".join(body), "r18", text_fill, 244, 4, 2)
        draw.text((x + 246, y + 20), "''", fill=accent, font=F["b30"])
    bg.convert("RGB").save(dest)


def brand_closer_clean(case: dict, dest: Path) -> None:
    accent = rgba(case["accent"])
    dark = Image.new("RGBA", (1140, 360), (6, 8, 12, 255))
    draw = ImageDraw.Draw(dark)
    v3.draw_halftone(draw, 1140, 360, accent)
    v3.add_diagonal_glow(dark, accent)
    draw_exit(draw, (78, 72), "b76", (255, 190, 82, 255) if case["sku"] == "D6MHW43BM" else (98, 211, 218, 255), (130, 33, 22, 180))
    draw.text((82, 166), case["brand_line"], fill=(255, 255, 255, 255), font=F["b30"])
    wrap(draw, (84, 216), "Claritate vizuala, dovezi scurte si explicatii inainte de promisiuni.", "r22", (225, 231, 238, 255), 520, 8, 2)
    x = 700
    for top, bottom in case["brand_cues"]:
        draw.rounded_rectangle((x, 126, x + 118, 206), radius=16, fill=(15, 17, 24, 240), outline=accent, width=2)
        draw.text((x + 18, 145), top, fill=(255, 255, 255, 255), font=F["b22"])
        draw.text((x + 18, 174), bottom, fill=(206, 214, 224, 255), font=F["r18"])
        x += 146
    dark.convert("RGB").save(dest)


def simple_text_panel(title: str, lines: list[str], accent_css: str) -> str:
    lis = "".join(f'<li style="margin:6px 0;">{esc(line)}</li>' for line in lines)
    return (
        f'<div style="margin:18px 0 22px 0;padding:20px 22px;border-left:6px solid {accent_css};'
        'background:#ffffff;">'
        f'<h3 style="font-size:20px;line-height:1.25;margin:0 0 8px 0;color:#24292f;">{esc(title)}</h3>'
        f'<ul style="margin:0;padding-left:20px;">{lis}</ul></div>'
    )


def source_table(rows: list[tuple[str, str]]) -> str:
    body = ""
    for i, (k, v) in enumerate(rows):
        bg = "#f7f7f7" if i % 2 == 0 else "#ffffff"
        body += (
            f'<tr><td style="padding:12px 14px;font-weight:700;background:{bg};border:1px solid #e2e2e2;">{esc(k)}</td>'
            f'<td style="padding:12px 14px;background:{bg};border:1px solid #e2e2e2;">{esc(v)}</td></tr>'
        )
    return f'<table style="border-collapse:collapse;width:100%;margin:10px 0 20px 0;">{body}</table>'


def html_note(text: str) -> str:
    return (
        '<blockquote style="margin:12px 0;padding:12px 14px;border-left:5px solid #f4b740;background:#fff8e8;">'
        f'<p style="margin:0;font-size:14px;line-height:1.45;"><strong>Nota:</strong> {esc(text)}</p></blockquote>'
    )


def media_record(component_id: str, path: Path, case_dir: Path, route: str, notes: list[str]) -> dict:
    return {
        "component_id": component_id,
        "component_version": "v5",
        "route_selected": route,
        "asset_path": rel(path, case_dir),
        "dimensions": dim(path),
        "risk_level": "low" if "pure_composite" in route else "medium",
        "production_notes": notes,
    }


def build_case(case_in: dict, icon_paths: dict[str, Path]) -> None:
    case = json.loads(json.dumps(case_in))
    case["brand_name"] = "EXIT"
    sku = case["sku"]
    assets = copy_assets(sku)
    case_dir = OUT / sku
    case_dir.mkdir(parents=True, exist_ok=True)

    hero = assets / "v5_product_scene_hero.jpg"
    proof = assets / "v5_cropped_proof_board.jpg"
    spec = assets / "v5_spec_icon_board_clean.jpg"
    qa = assets / "v5_qa_clean_board.jpg"
    review = assets / "v5_review_template_board.jpg"
    brand = assets / "v5_exit_brand_closer.jpg"

    product_scene_hero(case, assets, hero)
    crop_proof_board(case, assets, proof)
    clean_spec_board(case, icon_paths, spec)
    qa_clean_board(case, qa)
    review_board_light(case, review)
    brand_closer_clean(case, brand)

    body = ""
    body += html_img(hero, case_dir, "EXIT product scene hero")
    body += h2(case["name"].upper())
    body += p("V5 testeaza ruta stabila: fundal/scena premium, apoi produs, text, logo si icon-uri controlate local. Fara repetitie inutila de imagini si fara mici carduri in fiecare modul.")
    body += v3.anchor_triplet(case)
    body += h2("DOVADA VIZUALA")
    body += html_img(proof, case_dir, "cropped visual proof board")
    if sku == "D5YN6S3BM":
        body += simple_text_panel(
            "De ce urmeaza parametrii abia acum",
            ["Prima imagine a creat contextul de rutina.", "Dovada vizuala arata controlul si rezultatul.", "Specificatiile confirma daca aparatul se potriveste bucatariei."],
            case["accent_css"],
        )
    else:
        body += simple_text_panel(
            "De ce nu folosim pasii ca decor",
            ["Pentru cablul EV, cumparatorul verifica intai conectorul.", "Manualul conteaza doar dupa compatibilitate si protectie.", "De aceea aici folosim crop de produs, nu patru casete de instructiuni."],
            case["accent_css"],
        )
    body += h2("PARAMETRI CARE CONTEAZA")
    body += html_img(spec, case_dir, "clean spec icon board")
    body += h2("SPECIFICATII COMPLETE")
    body += source_table(case["specs"])
    body += h2("CONTINUT PACHET")
    body += source_table(case["package"])
    body += h2("Q&A / INTREBARI INAINTE DE CUMPARARE")
    body += html_img(qa, case_dir, "clean buyer question board")
    body += h2("REVIEW / FEEDBACK TEMPLATE")
    body += html_img(review, case_dir, "review feedback template")
    body += html_note("feedback-ul este doar template vizual. Pentru productie se inlocuieste cu review-uri reale, sursa, data si rating verificabil.")
    body += h2("DESPRE EXIT")
    body += html_img(brand, case_dir, "clean EXIT brand closer")

    html = page(body)
    (case_dir / "detail.html").write_text(html + "\n", encoding="utf-8")
    (case_dir / "detail_v5.html").write_text(html + "\n", encoding="utf-8")
    (case_dir / "preview_mobile.html").write_text(preview(f"EXIT v5 {sku}", html), encoding="utf-8")

    media = {
        "sku": sku,
        "brand": "EXIT",
        "version": "v5",
        "generation_strategy": "ai_background_plus_composite_design_logic_without_external_model_call",
        "note": "No external AI model was called in this run because FAL_KEY/Google credentials are not present. The route is simulated with captured/reference assets and deterministic local composition.",
        "component_records": [
            media_record("product_scene_hero", hero, case_dir, "ai_background_plus_composite", ["Product and text are deterministic layers; background is sourced from captured/reference asset."]),
            media_record("cropped_visual_proof", proof, case_dir, "pure_composite", ["Uses crop/proof rhythm instead of repeating full product images."]),
            media_record("spec_icon_board", spec, case_dir, "pure_composite", ["Icon library and exact source specs."]),
            media_record("qa_clean_board", qa, case_dir, "pure_composite", ["QA is separate from review."]),
            media_record("review_template_board", review, case_dir, "pure_composite", ["Template only; replace with real reviews."]),
            media_record("exit_brand_closer", brand, case_dir, "pure_composite", ["One concise brand closer; no repeated service promises."]),
        ],
    }
    (case_dir / "media_asset_index.json").write_text(json.dumps(media, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    spec_json = {
        "sku": sku,
        "brand": "EXIT",
        "version": "v5",
        "design_direction": "Premium ecommerce rhythm: one hero, proof crop, clean text, icon specs, QA, review template, concise brand closer.",
        "applied_rules": [
            "small cards only when they serve anchors/specs",
            "no consecutive heavy dark modules",
            "image crop used as proof instead of repeated full source image",
            "QA and review are separate modules",
            "exact text and specs are deterministic overlays",
        ],
    }
    (case_dir / "DESIGN_SPEC.json").write_text(json.dumps(spec_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    subprocess.run(
        ["python3", str(VALIDATOR), str(case_dir / "detail.html"), "--out", str(case_dir / "validation_report.json")],
        check=True,
        capture_output=True,
        text=True,
    )


def write_index() -> None:
    cards = []
    for case in v3.CASES:
        sku = case["sku"]
        cards.append(
            f'<li style="margin:10px 0;"><strong>{sku}</strong> - '
            f'<a href="{sku}/preview_mobile.html">preview_mobile</a> | '
            f'<a href="{sku}/DESIGN_SPEC.json">DESIGN_SPEC</a> | '
            f'<a href="{sku}/media_asset_index.json">media index</a> | '
            f'<a href="{sku}/validation_report.json">validation</a></li>'
        )
    body = page(
        h2("EXIT stable route examples v5")
        + p("Second-step examples for the new premium route: fewer repeated boxes, crop-based proof, stable deterministic text/icon overlays, QA separate from review.")
        + "<ul>"
        + "".join(cards)
        + "</ul>"
    )
    (OUT / "index.html").write_text(preview("EXIT stable route examples v5", body), encoding="utf-8")


def write_report() -> None:
    lines = [
        "# EXIT stable route examples v5",
        "",
        "Generated examples using the route defined in `workflow/emag_premium_banner_generation_strategy.v1.md`.",
        "",
        "## What changed from v4",
        "",
        "- Reduced repeated large image modules.",
        "- Small boxes are only used for anchor/spec roles.",
        "- Step-highlight GIF is not forced into the EV page as a decorative module.",
        "- QA and review are separated.",
        "- Brand closer is concise and no longer repeats unsupported service promises.",
        "- The hero follows `AI background + deterministic composite` logic, but no external model was called because credentials are not configured.",
        "",
        "## Outputs",
        "",
    ]
    for case in v3.CASES:
        sku = case["sku"]
        lines.append(f"- `{sku}`: `{OUT / sku / 'preview_mobile.html'}`")
    (OUT / "run_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    icon_paths = v4.ensure_icon_library()
    for case in v3.CASES:
        build_case(case, icon_paths)
    write_index()
    write_report()
    print(OUT)


if __name__ == "__main__":
    main()
