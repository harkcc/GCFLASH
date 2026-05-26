#!/usr/bin/env python3
"""Generate v2 Excité eMAG detail pages with richer modular layout."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path("/Users/cc/Desktop/photo_show")
SOURCE_ROOT = ROOT / "output/emag_excite_two_product_sop_test"
OUT = ROOT / "output/emag_excite_two_product_sop_test_v2"
ASSETS = OUT / "assets"
VALIDATOR = ROOT / "scripts/validate_emag_detail_html.py"


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    if not bold:
        paths = paths[1:] + paths[:1]
    for path in paths:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


FONTS = {
    "b76": font(76, True),
    "b64": font(64, True),
    "b60": font(60, True),
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


def fit_cover(src: Image.Image, size: tuple[int, int]) -> Image.Image:
    src = src.convert("RGB")
    w, h = src.size
    tw, th = size
    scale = max(tw / w, th / h)
    resized = src.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    x = (resized.width - tw) // 2
    y = (resized.height - th) // 2
    return resized.crop((x, y, x + tw, y + th))


def fit_contain(src: Image.Image, size: tuple[int, int]) -> Image.Image:
    img = src.convert("RGBA")
    img.thumbnail(size, Image.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    canvas.paste(img, ((size[0] - img.width) // 2, (size[1] - img.height) // 2), img)
    return canvas


def draw_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill, font_key: str) -> None:
    draw.text(xy, text, fill=fill, font=FONTS[font_key])


def save_gif(frames: list[Image.Image], path: Path, duration: int = 90) -> None:
    prepared = [frame.convert("P", palette=Image.Palette.ADAPTIVE) for frame in frames]
    prepared[0].save(path, save_all=True, append_images=prepared[1:], duration=duration, loop=0, optimize=False)


def logo_color(case: dict) -> tuple[int, int, int]:
    return case["logo_color"]


def make_scenario_banner(case: dict, src_dir: Path, dest: Path) -> None:
    bg = fit_cover(Image.open(src_dir / case["hero_bg"]), (1140, 456)).filter(ImageFilter.GaussianBlur(5))
    overlay = Image.new("RGBA", (1140, 456), case["overlay"])
    base = Image.alpha_composite(bg.convert("RGBA"), overlay)
    product = fit_contain(Image.open(src_dir / case["hero_product"]), (470, 360))
    base.alpha_composite(product, (620, 56))
    frames = []
    for i in range(16):
        frame = base.copy()
        draw = ImageDraw.Draw(frame)
        draw.rounded_rectangle((44, 48, 622, 394), radius=24, fill=case["panel"], outline=case["accent"], width=3)
        letters = "EXCITÉ"
        x = 82
        for idx, ch in enumerate(letters):
            active = (i // 2) % len(letters) == idx
            fill = (255, 226, 118, 255) if active else (*logo_color(case), 255)
            draw.text((x, 82 - (3 if active else 0)), ch, fill=fill, font=FONTS["b76"])
            x += 55 if ch != "I" else 30
        draw.text((88, 168), case["banner_title"], fill=(255, 255, 255, 255), font=FONTS["b36"])
        draw.text((88, 218), case["banner_sub"], fill=(234, 238, 242, 255), font=FONTS["r24"])
        for idx, (a, b) in enumerate(case["chips"]):
            cx = 88 + idx * 160
            cy = 306
            draw.rounded_rectangle((cx, cy, cx + 138, cy + 58), radius=14, fill=(255, 255, 255, 235), outline=case["accent"], width=3)
            draw.text((cx + 14, cy + 8), a, fill=case["accent"], font=FONTS["b22"])
            draw.text((cx + 14, cy + 33), b, fill=(58, 65, 74, 255), font=FONTS["r18"])
        shine = Image.new("RGBA", (1140, 456), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shine)
        sx = -260 + i * 110
        sd.polygon([(sx, 0), (sx + 80, 0), (sx + 310, 456), (sx + 230, 456)], fill=(255, 255, 255, 28))
        frame = Image.alpha_composite(frame, shine)
        frames.append(frame.convert("RGB"))
    save_gif(frames, dest)


def make_video_placeholder(case: dict, src_dir: Path, dest: Path) -> None:
    bg = fit_cover(Image.open(src_dir / case["video_bg"]), (1140, 520)).filter(ImageFilter.GaussianBlur(2))
    layer = Image.new("RGBA", (1140, 520), (0, 0, 0, 72))
    frame = Image.alpha_composite(bg.convert("RGBA"), layer)
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle((60, 70, 1080, 450), radius=24, outline=(255, 255, 255, 150), width=3)
    draw.ellipse((500, 190, 640, 330), fill=(255, 255, 255, 230))
    draw.polygon([(555, 226), (555, 294), (610, 260)], fill=case["accent"])
    draw.text((98, 104), "Demonstratie video produs", fill=(255, 255, 255, 255), font=FONTS["b36"])
    draw.text((98, 152), case["video_text"], fill=(236, 240, 244, 255), font=FONTS["r24"])
    draw.text((98, 392), "Video slot - in productie se inlocuieste cu clip/GIF real", fill=(255, 255, 255, 210), font=FONTS["r20"])
    frame.convert("RGB").save(dest)


def make_green_buffer(case: dict, src_dir: Path, dest: Path) -> None:
    frame = Image.new("RGB", (1140, 520), case["buffer_bg"])
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle((50, 54, 700, 458), radius=24, fill=(255, 255, 255), outline=case["accent"], width=3)
    draw.text((86, 102), case["buffer_title"], fill=(35, 48, 42), font=FONTS["b44"])
    y = 178
    for line in case["buffer_lines"]:
        draw.text((92, y), "• " + line, fill=(58, 72, 64), font=FONTS["r26"])
        y += 54
    product = fit_contain(Image.open(src_dir / case["buffer_product"]), (360, 400))
    frame = frame.convert("RGBA")
    frame.alpha_composite(product, (740, 70))
    frame.convert("RGB").save(dest)


def make_step_gif(case: dict, src_dir: Path, dest: Path) -> None:
    bg = fit_cover(Image.open(src_dir / case["step_bg"]), (1140, 720))
    frames = []
    boxes = case["step_boxes"]
    for i in range(20):
        frame = bg.copy().convert("RGBA")
        overlay = Image.new("RGBA", (1140, 720), (255, 255, 255, 20))
        draw = ImageDraw.Draw(overlay)
        active = (i // 5) % len(boxes)
        for idx, box in enumerate(boxes):
            color = case["accent"] if idx == active else (255, 255, 255, 120)
            width = 7 if idx == active else 3
            draw.rounded_rectangle(box, radius=18, outline=color, width=width)
            draw.ellipse((box[0] + 18, box[1] + 18, box[0] + 68, box[1] + 68), fill=case["accent"] if idx == active else (255, 255, 255, 210))
            draw.text((box[0] + 34, box[1] + 25), str(idx + 1), fill=(255, 255, 255) if idx == active else case["accent"], font=FONTS["b24"])
        frames.append(Image.alpha_composite(frame, overlay).convert("RGB"))
    save_gif(frames, dest, 120)


def make_review_board(case: dict, dest: Path) -> None:
    frame = Image.new("RGB", (1140, 520), (13, 15, 22))
    draw = ImageDraw.Draw(frame)
    draw.text((60, 58), "Feedback preview", fill=(255, 255, 255), font=FONTS["b44"])
    draw.text((60, 112), "Concept pentru recenzii - in productie se inlocuieste cu date reale", fill=(204, 212, 224), font=FONTS["r22"])
    cards = [(60, 178, 358, 414), (420, 178, 718, 414), (780, 178, 1080, 414)]
    for idx, (box, item) in enumerate(zip(cards, case["reviews"]), start=1):
        draw.rounded_rectangle(box, radius=20, fill=(255, 255, 255), outline=case["accent"], width=3)
        draw.ellipse((box[0] + 24, box[1] + 24, box[0] + 70, box[1] + 70), fill=case["accent"])
        draw.text((box[0] + 92, box[1] + 24), f"Review {idx}", fill=(35, 38, 45), font=FONTS["b22"])
        draw.text((box[0] + 24, box[1] + 94), item[0], fill=(35, 38, 45), font=FONTS["b22"])
        y = box[1] + 132
        for line in item[1:]:
            draw.text((box[0] + 24, y), line, fill=(75, 82, 94), font=FONTS["r18"])
            y += 28
    frame.save(dest)


def make_brand_professional(case: dict, dest: Path) -> None:
    base = Image.new("RGB", (1140, 360), (7, 8, 11))
    draw = ImageDraw.Draw(base)
    for x in range(0, 500, 18):
        for y in range(20, 190, 18):
            if (x + y) % 54 == 0:
                draw.ellipse((x, y, x + 3, y + 3), fill=(96, 80, 42))
    draw.text((68, 74), "EXCITÉ", fill=logo_color(case), font=FONTS["b64"])
    draw.text((70, 150), case["brand_line"], fill=(255, 255, 255), font=FONTS["b30"])
    draw.text((70, 204), case["brand_sub"], fill=(214, 220, 228), font=FONTS["r24"])
    for idx, cue in enumerate(case["brand_cues"]):
        x = 642 + idx * 150
        draw.rounded_rectangle((x, 118, x + 125, 210), radius=16, outline=case["accent"], fill=(18, 20, 28), width=3)
        draw.text((x + 20, 140), cue[0], fill=(255, 255, 255), font=FONTS["b22"])
        draw.text((x + 20, 168), cue[1], fill=(210, 218, 225), font=FONTS["r18"])
    frames = []
    for i in range(14):
        frame = base.copy().convert("RGBA")
        shine = Image.new("RGBA", (1140, 360), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shine)
        sx = -220 + i * 105
        sd.polygon([(sx, 0), (sx + 70, 0), (sx + 260, 360), (sx + 190, 360)], fill=(255, 255, 255, 32))
        frames.append(Image.alpha_composite(frame, shine).convert("RGB"))
    save_gif(frames, dest, 95)


def html_img(path: Path, base: Path, alt: str) -> str:
    return (
        f'<p style="text-align:center;margin:0 0 18px 0;">'
        f'<img src="{esc(rel(path, base))}" width="1140" alt="{esc(alt)}" style="max-width:100%;height:auto;display:block;margin:0 auto;">'
        "</p>"
    )


def h2(text: str) -> str:
    return f'<h2 style="font-size:22px;line-height:1.25;margin:28px 0 14px 0;font-weight:500;color:#2b2f36;">{esc(text)}</h2>'


def p(text: str) -> str:
    return f'<p style="margin:10px 0 14px 0;">{esc(text)}</p>'


def anchor_triplet(case: dict) -> str:
    colors = case["anchor_colors"]
    out = []
    for idx, item in enumerate(case["anchors"]):
        out.append(
            f'<blockquote style="margin:12px 0;padding:16px 18px;border-left:7px solid {colors[idx]};background:#fbfcfe;">'
            f'<p style="margin:0 0 8px 0;font-size:18px;font-weight:bold;">{idx + 1:02d}. {esc(item[0])}</p>'
            f'<p style="margin:0;color:#374151;">{esc(item[1])}</p>'
            "</blockquote>"
        )
    return "\n".join(out)


def mixed_feature_blocks(case: dict, base: Path, src_dir: Path) -> str:
    out = [h2("CE TREBUIE SA INTELEGI RAPID")]
    for idx, item in enumerate(case["mixed_blocks"]):
        img_path = src_dir / item["image"]
        out.append(html_img(img_path, base, item["title"]))
        out.append(
            f'<div style="background:{item["bg"]};padding:16px 18px;margin:0 0 20px 0;border-left:6px solid {item["accent"]};">'
            f'<p style="margin:0 0 8px 0;"><strong>{esc(item["title"])}</strong></p>'
            f'<p style="margin:0;">{esc(item["text"])}</p>'
            "</div>"
        )
    return "\n".join(out)


def qa_module(case: dict) -> str:
    out = [h2("Q&A RAPID")]
    for q, a in case["qa"]:
        out.append(
            '<blockquote style="margin:12px 0;padding:14px;border-left:5px solid '
            f'{case["accent_css"]};background:#f9fbff;">'
            f'<p style="margin:0;"><strong>{esc(q)}</strong><br>{esc(a)}</p></blockquote>'
        )
    return "\n".join(out)


def spec_table(rows: list[tuple[str, str]]) -> str:
    body = ""
    for idx, (k, v) in enumerate(rows):
        bg = "#f7f7f7" if idx % 2 == 0 else "#fff"
        body += (
            f'<tr style="background:{bg};"><td style="padding:11px;border:1px solid #dedede;font-weight:bold;width:38%;vertical-align:top;">{esc(k)}</td>'
            f'<td style="padding:11px;border:1px solid #dedede;vertical-align:top;word-break:break-word;">{esc(v)}</td></tr>'
        )
    return f'<table style="width:100%;border-collapse:collapse;margin:18px 0;font-size:15px;table-layout:fixed;">{body}</table>'


def page(body: str) -> str:
    return (
        '<div style="font-family:Arial,Helvetica,sans-serif;color:#24292f;line-height:1.62;'
        'max-width:1140px;margin:0 auto;padding:0 8px;font-size:16px;">'
        f"{body}</div>"
    )


def preview(title: str, body: str) -> str:
    return (
        '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{esc(title)}</title><style>body{{margin:0;background:#fff;}}img{{max-width:100%;height:auto;}}</style></head><body>{body}</body></html>'
    )


CASES = [
    {
        "sku": "D5YN6S3BM",
        "name": "Baby food routine",
        "hero_bg": "16.jpg",
        "hero_product": "02.jpg",
        "video_bg": "01.gif",
        "buffer_product": "11.jpg",
        "step_bg": "13.jpg",
        "overlay": (16, 54, 45, 86),
        "panel": (8, 24, 20, 222),
        "accent": (249, 115, 22, 255),
        "accent_css": "#f97316",
        "logo_color": (98, 211, 218),
        "buffer_bg": (232, 248, 239),
        "banner_title": "Baby food made calmer",
        "banner_sub": "Abur, mixare, incalzire si curatare intr-un flux usor.",
        "chips": [("4 MODURI", "presetate"), ("450W", "putere"), ("FARA BPA", "siguranta")],
        "video_text": "Foloseste GIF-ul sau un clip scurt pentru a arata rutina, nu doar produsul static.",
        "buffer_title": "O pauza vizuala inainte de detalii",
        "buffer_lines": ["Siguranta inainte de functie", "Rutina clara pentru parinti", "Curatare mai usoara dupa masa"],
        "step_boxes": [(8, 4, 558, 354), (582, 4, 1132, 354), (8, 370, 558, 710), (582, 370, 1132, 710)],
        "brand_line": "Specialist in rutina pentru bebelusi",
        "brand_sub": "Design cald, pasi clari si dovezi vizuale inainte de claims.",
        "brand_cues": [("SAFE", "facts"), ("EASY", "steps"), ("CLEAN", "care")],
        "anchors": [
            ("Siguranta si materiale", "Fara BPA, blocare de siguranta si alarma pentru nivel scazut de apa."),
            ("Rutina in 4 functii", "Abur, mixare, incalzire lapte si sterilizare explicate in ordine."),
            ("Curatare mai usoara", "Autocuratare si piese detasabile pentru folosire zilnica."),
        ],
        "anchor_colors": ["#f97316", "#22c55e", "#0ea5e9"],
        "mixed_blocks": [
            {"image": "03.jpg", "title": "Functii vizibile, nu doar text", "text": "Primul modul de produs trebuie sa arate panoul, vasul si rezultatul alimentar, ca parintele sa inteleaga rapid fluxul.", "bg": "#fff7ed", "accent": "#f97316"},
            {"image": "05.jpg", "title": "Preparare si rezultat in aceeasi poveste", "text": "Imaginea si textul se alterneaza: o scena de preparare, apoi o explicatie scurta despre ce intrebare rezolva.", "bg": "#f0fdf4", "accent": "#22c55e"},
            {"image": "08.jpg", "title": "Textura adaptata varstei", "text": "Aici explicam textura reglabila si cele doua viteze, fara un bloc lung de text care oboseste pe mobil.", "bg": "#eff6ff", "accent": "#0ea5e9"},
        ],
        "qa": [
            ("Poate gati si mixa in acelasi aparat?", "Da, sursa mentioneaza gatire la abur si mixare, plus incalzire lapte si sterilizare."),
            ("Este potrivit pentru rutina zilnica?", "Da, daca folosesti capacitatea 50-400 ml si functiile conform manualului produsului."),
            ("Cum se intretine dupa folosire?", "Sursa mentioneaza autocuratare si componente detasabile/lavabile."),
        ],
        "reviews": [
            ("Rutina mai simpla", "Parintii cauta pasi clari", "si curatare rapida."),
            ("Control mai bun", "Panoul LED si modurile", "reduc incercarile inutile."),
            ("Mai putina frictiune", "Abur + mixare intr-un", "singur flux de lucru."),
        ],
        "specs": [
            ("Putere", "450W"),
            ("Capacitate bol", "50-400 ml"),
            ("Functii", "abur, mixare, incalzire lapte, sterilizare, autocuratare"),
            ("Material", "corp KBS, lama inox, fara BPA"),
            ("Siguranta", "blocare de siguranta, alarma nivel scazut apa"),
            ("Dimensiuni", "31 x 13 x 20.3 cm"),
        ],
        "package": [("Aparat principal", "1 bucata"), ("Perie pentru cani", "1 bucata"), ("Manual", "1 bucata")],
    },
    {
        "sku": "D6MHW43BM",
        "name": "EV cable tech routine",
        "hero_bg": "01.jpg",
        "hero_product": "03.jpg",
        "video_bg": "02.gif",
        "buffer_product": "09.jpg",
        "step_bg": "08.jpg",
        "overlay": (8, 12, 38, 96),
        "panel": (5, 8, 18, 224),
        "accent": (14, 165, 233, 255),
        "accent_css": "#0ea5e9",
        "logo_color": (255, 190, 43),
        "buffer_bg": (231, 244, 255),
        "banner_title": "EV cable fit first",
        "banner_sub": "Tip 2, 22kW si IP65 explicate inainte de parametri.",
        "chips": [("TYPE 2", "fit"), ("22kW", "power"), ("IP65", "proof")],
        "video_text": "Foloseste GIF-ul pentru compatibilitate sau conectare, nu pentru decor.",
        "buffer_title": "Respiratie vizuala in zona tehnica",
        "buffer_lines": ["Compatibilitate inainte de cifre", "Cablul si conectorii trebuie vazuti", "Parametrii confirma decizia"],
        "step_boxes": [(20, 30, 360, 330), (400, 30, 740, 330), (780, 30, 1120, 330), (20, 360, 1120, 690)],
        "brand_line": "Specialist in accesorii tehnice clare",
        "brand_sub": "Compatibilitate, protectie si transport explicate fara claims inutile.",
        "brand_cues": [("FIT", "Type 2"), ("POWER", "22kW"), ("CARE", "bag")],
        "anchors": [
            ("Compatibil Type 2", "Pentru vehicule EV/PHEV cu standard Type 2 IEC 62196-2."),
            ("32A / 22kW trifazic", "Puterea se confirma inainte de scenarii si accesorii."),
            ("IP65 + TPU", "Protectie si material potrivite pentru transport si folosire zilnica."),
        ],
        "anchor_colors": ["#0ea5e9", "#22c55e", "#7c3aed"],
        "mixed_blocks": [
            {"image": "03.jpg", "title": "Compatibilitatea trebuie vazuta", "text": "Primul modul dupa ancore arata standardul Type 2 si lista de vehicule compatibile.", "bg": "#eff6ff", "accent": "#0ea5e9"},
            {"image": "04.jpg", "title": "Puterea se confirma vizual", "text": "32A si 22kW raman in context tehnic, cu imaginea langa text pentru a evita oboseala.", "bg": "#f0fdf4", "accent": "#22c55e"},
            {"image": "09.jpg", "title": "Protectia raspunde la teama de exterior", "text": "IP65 si cablul TPU sunt explicate ca folosire, depozitare si rezistenta.", "bg": "#f5f3ff", "accent": "#7c3aed"},
        ],
        "qa": [
            ("Se potriveste cu orice masina?", "Trebuie verificat standardul Type 2 al vehiculului si statia compatibila."),
            ("Pot folosi cablul in exterior?", "Sursa mentioneaza IP65 si rezistenta la apa/praf, cu respectarea instructiunilor."),
            ("De ce conteaza geanta?", "Ajuta la depozitare si protejarea cablului intre utilizari."),
        ],
        "reviews": [
            ("Potrivire mai clara", "Buyerii vor sa confirme", "standardul conectorului."),
            ("Transport mai usor", "Geanta rezolva depozitarea", "dupa incarcare."),
            ("Mai multa incredere", "IP65 si TPU reduc", "intrebarile despre exterior."),
        ],
        "specs": [
            ("Tip cablu", "Type 2 la Type 2, IEC 62196-2"),
            ("Curent", "32A"),
            ("Putere", "22kW"),
            ("Faze", "3 faze"),
            ("Lungime", "5 metri"),
            ("Protectie", "IP65"),
        ],
        "package": [("Cablu EV", "Type 2 la Type 2, 5m"), ("Geanta transport", "1 bucata"), ("Manual", "1 bucata")],
    },
]


def build(case: dict) -> None:
    sku = case["sku"]
    source_assets = SOURCE_ROOT / "assets" / sku
    case_assets = ASSETS / sku
    case_assets.mkdir(parents=True, exist_ok=True)
    for path in source_assets.glob("*"):
        if path.is_file():
            shutil.copy2(path, case_assets / path.name)
    case_dir = OUT / sku
    case_dir.mkdir(parents=True, exist_ok=True)

    scenario_banner = case_assets / "v2_scenario_banner.gif"
    video_placeholder = case_assets / "v2_video_placeholder.png"
    green_buffer = case_assets / "v2_visual_buffer.png"
    step_gif = case_assets / "v2_step_highlight.gif"
    review_board = case_assets / "v2_review_preview_board.png"
    brand_banner = case_assets / "v2_brand_professional.gif"

    make_scenario_banner(case, case_assets, scenario_banner)
    make_video_placeholder(case, case_assets, video_placeholder)
    make_green_buffer(case, case_assets, green_buffer)
    make_step_gif(case, case_assets, step_gif)
    make_review_board(case, review_board)
    make_brand_professional(case, brand_banner)

    body = ""
    body += html_img(scenario_banner, case_dir, "Excité scenario banner")
    body += html_img(video_placeholder, case_dir, "video placeholder module")
    body += h2(case["name"].upper())
    body += p("Aceasta versiune foloseste un ritm mai variat: banner de scena, video slot, ancore rapide, imagini reale din listing, blocuri text scurte, pauza vizuala, Q&A si feedback preview.")
    body += anchor_triplet(case)
    body += mixed_feature_blocks(case, case_dir, case_assets)
    body += html_img(green_buffer, case_dir, "visual buffer")
    body += h2("PASII SI MOMENTELE CHEIE")
    body += html_img(step_gif, case_dir, "step highlight gif")
    body += h2("SPECIFICATII CARE CONFIRMA DECIZIA")
    body += spec_table(case["specs"])
    body += h2("CONTINUT PACHET")
    body += spec_table(case["package"])
    body += qa_module(case)
    body += h2("COMENTARII / REVIEW PREVIEW")
    body += html_img(review_board, case_dir, "review concept board")
    body += '<blockquote style="margin:12px 0;padding:14px;border-left:5px solid #f4b740;background:#fff8e8;"><p style="margin:0;"><strong>Nota:</strong> continutul de review este concept preview. Pentru productie se inlocuieste cu review-uri reale, sursa, data si rating verificabil.</p></blockquote>'
    body += h2("DESPRE EXCITÉ")
    body += html_img(brand_banner, case_dir, "Excité brand professional banner")
    body += '<div style="background:#050505;padding:16px;margin:22px 0;text-align:center;border:4px solid #f4c300;"><p style="font-size:17px;font-weight:bold;color:#fff;margin:8px 0;">Excité - claritate vizuala, informatii scurte si dovezi inainte de promisiuni.</p></div>'
    html = page(body)
    (case_dir / "detail_v2.html").write_text(html + "\n", encoding="utf-8")
    (case_dir / "preview_mobile.html").write_text(preview(f"Excité v2 {sku}", html), encoding="utf-8")
    spec = {
        "sku": sku,
        "brand": "Excité",
        "design_direction": "scenario-led mobile PDP, varied visual rhythm, evidence-gated review and service claims",
        "palette": {
            "accent": case["accent_css"],
            "logo_rgb": case["logo_color"],
            "buffer_bg_rgb": case["buffer_bg"],
        },
        "modules": [
            "scenario_banner_gif",
            "video_placeholder",
            "first_screen_anchor_triplet",
            "mixed_image_text_blocks",
            "fresh_visual_buffer",
            "step_highlight_gif",
            "spec_table",
            "package_table",
            "qa_module",
            "review_preview_board",
            "brand_professional_banner",
        ],
        "production_notes": [
            "Replace review preview with real review data before publishing.",
            "Use image-agent to clean baked old-brand marks from source product images.",
            "Generate final video/GIF asset when actual product motion is available.",
        ],
    }
    (case_dir / "DESIGN_SPEC.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    validate = subprocess.run(["python3", str(VALIDATOR), str(case_dir / "detail_v2.html"), "--out", str(case_dir / "validation_report.json")], capture_output=True, text=True)
    if validate.returncode:
        raise RuntimeError(validate.stderr or validate.stdout)


def write_index() -> None:
    items = []
    for case in CASES:
        sku = case["sku"]
        items.append(f'<li style="margin:10px 0;"><strong>{sku}</strong> - <a href="{sku}/preview_mobile.html">v2 preview</a> | <a href="{sku}/DESIGN_SPEC.json">DESIGN_SPEC</a> | <a href="{sku}/validation_report.json">validation</a></li>')
    html = preview("Excité SOP test v2", page(h2("Excité SOP test v2") + p("V2 adds scenario-led banners, video slots, mixed image/text rhythm, fresh color breaks, Q&A, review preview and brand professional modules.") + "<ul>" + "".join(items) + "</ul>"))
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
