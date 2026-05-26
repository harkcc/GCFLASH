#!/usr/bin/env python3
"""Generate two eMAG detail pages from captured Excitat products using the new Excité SOP."""

from __future__ import annotations

import json
import os
import re
import shutil
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path("/Users/cc/Desktop/photo_show")
SOURCE = ROOT / "output/emag_detail_html_live_batch"
OUT = ROOT / "output/emag_excite_two_product_sop_test"
ASSETS = OUT / "assets"
VISUAL_BOARDS = ROOT / "output/emag_html_detail_agent_v1_3_mobile_reference/assets"
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
    "b64": font(64, True),
    "b48": font(48, True),
    "b36": font(36, True),
    "b28": font(28, True),
    "b24": font(24, True),
    "r24": font(24),
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


def download(url: str, dest: Path) -> Path:
    if dest.exists() and dest.stat().st_size > 100:
        return dest
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        dest.write_bytes(resp.read())
    return dest


def ext_from_url(url: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    return suffix if suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp"} else ".jpg"


def localize_images(sku: str, images: list[dict]) -> list[dict]:
    folder = ASSETS / sku
    folder.mkdir(parents=True, exist_ok=True)
    localized = []
    for idx, item in enumerate(images, start=1):
        url = item["src"]
        ext = ext_from_url(url)
        path = folder / f"{idx:02d}{ext}"
        try:
            download(url, path)
            ok = True
        except Exception:
            path = Path(url)
            ok = False
        localized.append({**item, "local_path": path.as_posix(), "downloaded": ok})
    return localized


def gradient(size: tuple[int, int], left: tuple[int, int, int], right: tuple[int, int, int]) -> Image.Image:
    w, h = size
    image = Image.new("RGB", size)
    pix = image.load()
    for x in range(w):
        t = x / max(1, w - 1)
        color = tuple(int(left[i] * (1 - t) + right[i] * t) for i in range(3))
        for y in range(h):
            pix[x, y] = color
    return image


def paste_fit(base: Image.Image, src_path: Path, box: tuple[int, int, int, int], radius: int = 0) -> Image.Image:
    try:
        src = Image.open(src_path).convert("RGB")
    except Exception:
        return base
    x1, y1, x2, y2 = box
    src.thumbnail((x2 - x1, y2 - y1), Image.LANCZOS)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    px = x1 + (x2 - x1 - src.width) // 2
    py = y1 + (y2 - y1 - src.height) // 2
    if radius:
        mask = Image.new("L", src.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, src.width, src.height), radius=radius, fill=255)
        layer.paste(src.convert("RGBA"), (px, py), mask)
    else:
        layer.paste(src.convert("RGBA"), (px, py))
    return Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")


def save_shine_gif(base: Image.Image, dest: Path, frames_count: int = 14) -> None:
    frames = []
    for i in range(frames_count):
        frame = base.copy().convert("RGBA")
        overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        x = -260 + i * 112
        draw.polygon([(x, 0), (x + 92, 0), (x + 330, 456), (x + 238, 456)], fill=(255, 255, 255, 36))
        frames.append(Image.alpha_composite(frame, overlay).convert("P", palette=Image.Palette.ADAPTIVE))
    frames[0].save(dest, save_all=True, append_images=frames[1:], duration=90, loop=0, optimize=False)


def make_banner(case: dict, images: list[dict]) -> Path:
    out = ASSETS / case["sku"] / "excite_brand_banner.gif"
    base = gradient((1140, 456), case["banner_left"], case["banner_right"])
    draw = ImageDraw.Draw(base)
    for x in range(0, 520, 18):
        for y in range(34, 220, 18):
            if (x + y) % 54 == 0:
                draw.ellipse((x, y, x + 3, y + 3), fill=(154, 113, 41))
    draw.text((68, 78), "EXCITÉ", fill=(255, 190, 43), font=FONTS["b64"])
    draw.text((72, 152), case["banner_subtitle"], fill=(255, 255, 255), font=FONTS["b36"])
    draw.text((74, 206), case["banner_body"], fill=(225, 228, 235), font=FONTS["r24"])
    chips = case["banner_chips"]
    for idx, chip in enumerate(chips):
        x = 74 + idx * 184
        y = 322
        draw.rounded_rectangle((x, y, x + 152, y + 62), radius=14, fill=(9, 10, 13), outline=(255, 190, 43), width=3)
        draw.text((x + 16, y + 10), chip[0], fill=(255, 255, 255), font=FONTS["b24"])
        draw.text((x + 16, y + 36), chip[1], fill=(220, 224, 232), font=FONTS["r18"])
    product_img = next((Path(i["local_path"]) for i in images if i["downloaded"] and not i["local_path"].lower().endswith(".gif")), None)
    if product_img:
        base = paste_fit(base, product_img, (706, 42, 1080, 404), radius=18)
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle((690, 372, 1080, 422), radius=14, fill=(0, 0, 0), outline=(255, 190, 43), width=2)
    draw.text((715, 386), case["banner_note"], fill=(255, 255, 255), font=FONTS["r20"])
    save_shine_gif(base, out)
    return out


def img(path: str, alt: str) -> str:
    return (
        f'<p style="text-align:center;margin:0 0 18px 0;">'
        f'<img src="{esc(path)}" width="1140" alt="{esc(alt)}" style="max-width:100%;height:auto;display:block;margin:0 auto;">'
        f"</p>"
    )


def h2(text: str) -> str:
    return f'<h2 style="font-size:22px;line-height:1.25;margin:28px 0 14px 0;font-weight:500;color:#2b2f36;">{esc(text)}</h2>'


def paragraph(text: str) -> str:
    return f'<p style="margin:10px 0 14px 0;">{esc(text)}</p>'


def anchor_triplet(items: list[tuple[str, str, str]]) -> str:
    colors = ["#0ea5e9", "#22c55e", "#7c3aed"]
    blocks = []
    for idx, (title, body, role) in enumerate(items):
        blocks.append(
            f'<blockquote data-role="{esc(role)}" style="margin:12px 0;padding:16px 18px;border-left:7px solid {colors[idx]};background:#fbfcfe;">'
            f'<p style="margin:0 0 8px 0;font-size:18px;font-weight:bold;">{idx + 1:02d}. {esc(title)}</p>'
            f'<p style="margin:0;color:#374151;">{esc(body)}</p>'
            f"</blockquote>"
        )
    return "\n".join(blocks)


def color_band(title: str, rows: list[tuple[str, str]], bg: str, accent: str) -> str:
    body = "".join(f'<p style="margin:8px 0;"><strong>- {esc(k)}</strong> - {esc(v)}</p>' for k, v in rows)
    return (
        f'<div style="background:{bg};padding:18px;margin:18px 0;border-left:6px solid {accent};">'
        f'<h3 style="margin:0 0 10px 0;font-size:17px;color:#1f2937;">{esc(title)}</h3>{body}</div>'
    )


def spec_table(rows: list[tuple[str, str]]) -> str:
    body = ""
    for idx, (k, v) in enumerate(rows):
        bg = "#f7f7f7" if idx % 2 == 0 else "#fff"
        body += (
            f'<tr style="background:{bg};"><td style="padding:11px;border:1px solid #dedede;font-weight:bold;width:38%;vertical-align:top;">{esc(k)}</td>'
            f'<td style="padding:11px;border:1px solid #dedede;vertical-align:top;word-break:break-word;">{esc(v)}</td></tr>'
        )
    return f'<table style="width:100%;border-collapse:collapse;margin:18px 0;font-size:15px;table-layout:fixed;">{body}</table>'


def faq(items: list[tuple[str, str]]) -> str:
    out = [h2("INTREBARI FRECVENTE")]
    for idx, (q, a) in enumerate(items, start=1):
        out.append(f'<p style="margin:14px 0;"><strong>{idx}. {esc(q)}</strong><br>{esc(a)}</p>')
    return "\n".join(out)


def cta(title: str, text: str) -> str:
    return (
        '<div style="background:#050505;padding:20px;margin:26px 0;text-align:center;border:5px solid #f4c300;">'
        f'<p style="font-size:18px;font-weight:bold;color:#fff;margin:8px 0;">{esc(title)}</p>'
        f'<p style="font-size:16px;color:#fff;margin:8px 0;">{esc(text)}</p>'
        '</div>'
    )


def page(body: str) -> str:
    return (
        '<div style="font-family:Arial,Helvetica,sans-serif;color:#24292f;line-height:1.62;'
        'max-width:1140px;margin:0 auto;padding:0 8px;font-size:16px;">'
        f"{body}</div>"
    )


def preview_wrap(title: str, body: str) -> str:
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{esc(title)}</title><style>body{{margin:0;background:#fff;}} img{{max-width:100%;height:auto;}}</style>'
        f'</head><body>{body}</body></html>'
    )


CASES = [
    {
        "sku": "D6MHW43BM",
        "kind": "technical_ev",
        "banner_left": (4, 6, 15),
        "banner_right": (40, 16, 64),
        "banner_subtitle": "EV charging essentials",
        "banner_body": "Cablu Type 2 pentru incarcare rapida, controlata si usor de verificat.",
        "banner_chips": [("TIP 2", "compatibil"), ("22kW", "trifazic"), ("IP65", "protectie")],
        "banner_note": "Source facts from captured eMAG detail",
        "headline": "IN PRIMELE SECUNDE: COMPATIBILITATE, PUTERE, PROTECTIE",
        "intro": "Pentru un cablu EV, cumparatorul vrea sa confirme rapid daca se potriveste masinii, statiei si mediului de folosire. De aceea pagina incepe cu trei ancore clare, apoi arata dovada vizuala si parametrii.",
        "anchors": [
            ("Compatibil Type 2 la Type 2", "Pentru vehicule electrice si PHEV cu standard IEC 62196-2.", "compatibility"),
            ("Incarcare 32A / 22kW", "Putere trifazica pentru statii AC publice sau casnice compatibile.", "power"),
            ("Protectie IP65 + cablu TPU", "Rezistenta la apa, praf si conditii de exterior, conform detaliilor sursa.", "safety"),
        ],
        "feature_band": [
            ("Compatibilitate larga", "lista sursa include marci EV si PHEV populare cu mufa Type 2."),
            ("Cablul de 5 metri", "ajuta la conectare in parcare, garaj sau statii publice."),
            ("Material TPU", "sursa mentioneaza flexibilitate, rezistenta la frig, caldura, indoire si impact."),
            ("Geanta inclusa", "rezolva depozitarea si transportul cablului intre utilizari."),
        ],
        "specs": [
            ("Tip cablu", "Type 2 la Type 2, IEC 62196-2"),
            ("Curent nominal", "32A"),
            ("Putere maxima", "22kW"),
            ("Faze", "3 faze, trifazic"),
            ("Tensiune", "400V AC"),
            ("Lungime cablu", "5 metri"),
            ("Material cablu", "TPU rezistent la intemperii"),
            ("Temperatura de lucru", "-35°C ~ +50°C"),
            ("Protectie", "IP65, apa si praf"),
            ("Utilizare", "interior si exterior"),
        ],
        "package": [
            ("Cablu EV", "Type 2 la Type 2, 5m, 32A, 22kW, trifazic"),
            ("Geanta transport", "pentru depozitare si protectie"),
            ("Manual", "manual de utilizare"),
        ],
        "faq": [
            ("Este potrivit pentru masina mea?", "Verifica daca vehiculul foloseste conector Type 2 si daca statia suporta parametrii cablului."),
            ("Pot folosi cablul afara?", "Sursa mentioneaza protectie IP65 si rezistenta la ploaie/praf, dar conditiile reale de folosire trebuie respectate."),
            ("De ce conteaza lungimea de 5 metri?", "Ajuta cand portul masinii si punctul de incarcare nu sunt perfect aliniate."),
        ],
        "image_roles": ["hero_source", "source_gif", "compatibility", "power", "material", "protection", "package"],
    },
    {
        "sku": "D5YN6S3BM",
        "kind": "baby_home",
        "banner_left": (18, 28, 34),
        "banner_right": (56, 88, 74),
        "banner_subtitle": "Baby food routine",
        "banner_body": "Abur, mixare, incalzire si curatare intr-un flux usor pentru parinti.",
        "banner_chips": [("4 MODURI", "presetate"), ("450W", "putere"), ("FARA BPA", "material")],
        "banner_note": "Excité baby routine detail test",
        "headline": "IN PRIMELE SECUNDE: SIGURANTA, RUTINA, IGIENA",
        "intro": "Pentru un aparat de mancare pentru bebelusi, pagina trebuie sa calmeze intai intrebarile parintilor: este sigur, este usor de folosit si se curata rapid?",
        "anchors": [
            ("4 moduri presetate", "Gatire la abur, mixare, incalzire si sterilizare explicate ca rutina.", "routine"),
            ("Materiale fara BPA", "Sursa mentioneaza corp KBS rezistent la caldura si lama din otel inoxidabil.", "safety"),
            ("Autocuratare si panou LED", "Operare tactila si curatare mai usoara pentru utilizare zilnica.", "hygiene"),
        ],
        "feature_band": [
            ("Gatire la abur + mixare", "combina doua etape importante pentru piureuri si alimente pentru bebelusi."),
            ("Textura reglabila", "cele 2 viteze ajuta la adaptarea consistentei in functie de etapa de diversificare."),
            ("Siguranta in folosire", "blocarea de siguranta si alarma pentru nivel scazut de apa reduc riscul de utilizare gresita."),
            ("Curatare mai simpla", "functia de autocuratare si piesele lavabile reduc timpul dupa preparare."),
        ],
        "specs": [
            ("Tip produs", "robot de gatit si aparat de gatit la abur pentru bebelusi"),
            ("Putere", "450W"),
            ("Capacitate bol", "50~400 ml"),
            ("Moduri gatit", "4 moduri presetate"),
            ("Viteze", "reglaj cu 2 viteze"),
            ("Material", "corp KBS rezistent la caldura, lama din otel inoxidabil, fara BPA"),
            ("Functii", "gatire la abur, mixare, incalzire lapte, sterilizare biberoane, autocuratare"),
            ("Ecran", "panou tactil si afisaj digital LED"),
            ("Siguranta", "blocare de siguranta, alarma nivel scazut de apa"),
            ("Dimensiuni", "31 x 13 x 20.3 cm"),
            ("Tensiune", "220V"),
        ],
        "package": [
            ("Aparat de gatit alimente", "1 bucata"),
            ("Aparat de gatit cu aburi", "1 bucata, conform textului sursa"),
            ("Perie pentru cani", "1 bucata"),
            ("Manual instructiuni", "1 bucata"),
        ],
        "faq": [
            ("Este potrivit pentru pregatirea piureurilor?", "Da, sursa mentioneaza gatire la abur si mixare, plus reglaj de textura."),
            ("Ce elemente de siguranta sunt mentionate?", "Blocare de siguranta, alarma pentru nivel scazut de apa si materiale fara BPA apar in detaliile sursa."),
            ("Cum se reduce timpul de curatare?", "Sursa mentioneaza autocuratare si componente detasabile/lavabile."),
        ],
        "image_roles": ["source_gif", "product", "functions", "process", "cleaning", "package"],
    },
]


def build_case(case: dict) -> None:
    sku = case["sku"]
    case_dir = OUT / sku
    case_dir.mkdir(parents=True, exist_ok=True)
    meta = json.loads((SOURCE / f"{sku}.meta.json").read_text())
    inner = (SOURCE / f"{sku}.inner.html").read_text()
    title = meta["listingTitle"].replace("Excitat®", "Excité").replace("Excitat", "Excité")
    images = localize_images(sku, meta["images"])
    banner = make_banner(case, images)
    rel_banner = os.path.relpath(banner, case_dir)

    def rel_img(index: int) -> str:
        return os.path.relpath(Path(images[index]["local_path"]), case_dir)

    body = ""
    body += img(rel_banner, f"Excité banner {sku}")
    body += h2(case["headline"])
    body += paragraph(case["intro"])
    body += anchor_triplet(case["anchors"])
    body += img(rel_img(0), "source hero image")
    if len(images) > 1 and images[1]["local_path"].lower().endswith(".gif"):
        body += img(rel_img(1), "source product GIF")
    body += color_band("DE CE MERITA SA CONTINUI", case["feature_band"], "#e8f3ff" if case["kind"] == "technical_ev" else "#fff7ed", "#0ea5e9" if case["kind"] == "technical_ev" else "#f97316")
    for idx in [2, 3, 4]:
        if idx < len(images):
            body += img(rel_img(idx), f"source proof image {idx}")
    body += h2("SPECIFICATII TEHNICE COMPLETE")
    body += spec_table(case["specs"])
    for idx in [5, 6]:
        if idx < len(images):
            body += img(rel_img(idx), f"source detail image {idx}")
    body += h2("CONTINUT PACHET")
    body += spec_table(case["package"])
    body += faq(case["faq"])
    body += (
        '<blockquote style="margin:16px 0;padding:14px;border-left:5px solid #f4b740;background:#fff8e8;">'
        '<p style="margin:0;"><strong>Recenzii:</strong> nu am introdus testimonial sau rating, deoarece setul local folosit aici nu contine dovezi de review pentru acest SKU. Modulul de review ramane blocat pana exista sursa reala.</p>'
        '</blockquote>'
    )
    body += cta(f"Excité - {case['banner_subtitle']}", "Pagina foloseste imagini reale din listing, parametri sursa si ordinea SOP: rezultat, ancore, dovada, specificatii, pachet, FAQ.")
    html = page(body)
    (case_dir / "generated_detail.html").write_text(html + "\n", encoding="utf-8")
    (case_dir / "preview_mobile.html").write_text(preview_wrap(title, html), encoding="utf-8")

    source_html = inner.replace("Excitat®", "Excité").replace("Excitat", "Excité")
    (case_dir / "original_source_rebranded.html").write_text(preview_wrap(f"Original source {sku}", page(source_html)), encoding="utf-8")
    compare = (
        '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>Before After {sku}</title><style>body{{font-family:Arial;margin:0;background:#f3f4f6;}}iframe{{width:100%;height:760px;border:1px solid #ddd;background:#fff;}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px;}}@media(max-width:800px){{.grid{{grid-template-columns:1fr;}}}}</style></head><body>'
        f'<h1 style="font-size:22px;margin:14px;">{esc(sku)} - original rebranded vs generated SOP</h1>'
        '<div class="grid"><section><h2 style="font-size:16px;">Original captured detail, brand text replaced</h2><iframe src="original_source_rebranded.html"></iframe></section>'
        '<section><h2 style="font-size:16px;">Generated Excité SOP detail</h2><iframe src="preview_mobile.html"></iframe></section></div></body></html>'
    )
    (case_dir / "before_after_preview.html").write_text(compare, encoding="utf-8")
    truth = {
        "product_id": sku,
        "brand": "Excité",
        "source_url": meta["productUrl"],
        "source_listing_title": meta["listingTitle"],
        "rewritten_title": title,
        "product_type": case["kind"],
        "core_result": case["intro"],
        "anchors": case["anchors"],
        "specs": case["specs"],
        "package_contents": case["package"],
        "source_images": [{"src": im["src"], "local_path": im["local_path"], "downloaded": im["downloaded"]} for im in images],
        "constraints": ["review/testimonial blocked without real review evidence", "source detail images may still contain original baked-in visual branding and need image-agent replacement for production"],
    }
    (case_dir / "product_truth_pack.json").write_text(json.dumps(truth, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    modules = [
        "excite_shine_banner",
        "first_screen_anchor_triplet",
        "source_product_visual",
        "source_gif_motion",
        "feature_benefit_band",
        "source_detail_proof_images",
        "spec_table_clean",
        "package_contents_table",
        "faq_objection",
        "review_blocked_without_evidence",
        "trust_close",
    ]
    plan = [
        {
            "module_id": module,
            "buyer_question": {
                "excite_shine_banner": "What is the product and brand context?",
                "first_screen_anchor_triplet": "What are the first three purchase decisions?",
                "source_product_visual": "What does the product look like?",
                "source_gif_motion": "Can motion explain use or brand?",
                "feature_benefit_band": "Why do the features matter?",
                "source_detail_proof_images": "Which visual details prove the claims?",
                "spec_table_clean": "Does it fit my technical requirement?",
                "package_contents_table": "What arrives in the box?",
                "faq_objection": "What doubts remain?",
                "review_blocked_without_evidence": "Can we use social proof?",
                "trust_close": "What should the buyer remember?",
            }[module],
            "comes_after": modules[idx - 1] if idx else "input_audit",
            "sets_up_next": modules[idx + 1] if idx + 1 < len(modules) else "review_log",
            "required_evidence": ["product_truth_pack", "captured_detail_html"],
        }
        for idx, module in enumerate(modules)
    ]
    (case_dir / "module_plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    review_log = f"""# Review Log - {sku}

- Source URL: {meta['productUrl']}
- Brand changed in generated copy: `Excitat®` -> `Excité`
- Source assets used: {len(images)} images, {sum(1 for im in images if im['local_path'].lower().endswith('.gif'))} GIF
- Selected SOP: {case['kind']}
- Review/testimonial module: blocked because no real local review evidence was available.
- Production caveat: source detail images may contain baked-in old brand marks; image-agent should regenerate/clean them for final production.
"""
    (case_dir / "review_log.md").write_text(review_log, encoding="utf-8")


def write_index() -> None:
    cards = []
    for case in CASES:
        sku = case["sku"]
        cards.append(
            f'<li style="margin:10px 0;"><strong>{esc(sku)}</strong> - '
            f'<a href="{sku}/preview_mobile.html">Generated mobile</a> | '
            f'<a href="{sku}/before_after_preview.html">Before/after</a> | '
            f'<a href="{sku}/product_truth_pack.json">TruthPack</a></li>'
        )
    html = preview_wrap(
        "Excité two product SOP test",
        page(
            h2("Excité two product SOP test")
            + paragraph("Two products were selected from the captured eMAG Excitat store and regenerated with the current Excité detail SOP.")
            + "<ul>" + "".join(cards) + "</ul>"
        ),
    )
    (OUT / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    for case in CASES:
        build_case(case)
    write_index()
    print(OUT)


if __name__ == "__main__":
    main()
