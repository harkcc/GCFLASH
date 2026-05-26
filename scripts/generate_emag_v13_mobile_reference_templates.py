#!/usr/bin/env python3
"""Generate richer mobile-first eMAG detail HTML reference runs.

The samples intentionally keep product-photo slots as requirements. Banner,
motion GIF, FAQ, and review/social-proof modules are separate module families.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/cc/Desktop/photo_show")
OUT = ROOT / "output/emag_html_detail_agent_v1_3_mobile_reference"
ASSETS = OUT / "assets"
BANNER_SRC = ROOT / "output/emag_banner_generation_tests"
V12_ASSET = ROOT / "output/emag_html_detail_agent_v1_2_rich_mobile/assets/brand_trust_motion_demo.gif"


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
    "b54": font(54, True),
    "b42": font(42, True),
    "b32": font(32, True),
    "b26": font(26, True),
    "b22": font(22, True),
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


def rel(path: Path) -> str:
    return "../" + path.relative_to(OUT).as_posix()


def copy_asset(src_name: str, dest_name: str) -> Path:
    src = BANNER_SRC / src_name
    dest = ASSETS / dest_name
    if src.exists():
        shutil.copy2(src, dest)
    else:
        Image.new("RGB", (1140, 456), (20, 20, 24)).save(dest)
    return dest


def create_review_template(path: Path) -> None:
    image = Image.new("RGB", (1140, 456), (10, 12, 17))
    draw = ImageDraw.Draw(image)
    for x in range(0, 1140, 22):
        for y in range(0, 456, 22):
            if (x + y) % 66 == 0:
                draw.ellipse((x, y, x + 2, y + 2), fill=(58, 62, 75))
    draw.rectangle((0, 0, 1140, 456), outline=(39, 43, 54), width=2)
    draw.text((56, 54), "Review Evidence", fill=(255, 255, 255), font=FONTS["b54"])
    draw.text((58, 118), "template", fill=(255, 189, 74), font=FONTS["b42"])
    draw.text((58, 190), "Use only real review text,", fill=(218, 222, 230), font=FONTS["r24"])
    draw.text((58, 224), "real rating evidence and", fill=(218, 222, 230), font=FONTS["r24"])
    draw.text((58, 258), "verified source dates.", fill=(218, 222, 230), font=FONTS["r24"])
    draw.text((58, 360), "NOT FAQ", fill=(255, 255, 255), font=FONTS["b26"])
    draw.text((168, 363), "separate social-proof module", fill=(190, 196, 207), font=FONTS["r20"])

    cards = [
        (420, 52, 724, 202, (255, 255, 255), (255, 189, 74)),
        (756, 52, 1084, 202, (21, 23, 32), (73, 78, 92)),
        (420, 238, 724, 396, (21, 23, 32), (73, 78, 92)),
        (756, 238, 1084, 396, (21, 23, 32), (73, 78, 92)),
    ]
    for idx, (x1, y1, x2, y2, fill, outline) in enumerate(cards, start=1):
        draw.rounded_rectangle((x1, y1, x2, y2), radius=20, fill=fill, outline=outline, width=2)
        text = (25, 26, 34) if fill == (255, 255, 255) else (238, 240, 245)
        sub = (85, 88, 100) if fill == (255, 255, 255) else (185, 190, 202)
        draw.ellipse((x1 + 24, y1 + 28, x1 + 74, y1 + 78), fill=(255, 189, 74))
        draw.text((x1 + 92, y1 + 28), f"Review slot {idx}", fill=text, font=FONTS["b22"])
        draw.text((x1 + 92, y1 + 62), "rating/source/date", fill=sub, font=FONTS["r18"])
        draw.line((x1 + 24, y1 + 102, x2 - 26, y1 + 102), fill=outline, width=2)
        draw.text((x1 + 24, y1 + 116), "Quote area after evidence import", fill=sub, font=FONTS["r18"])
    image.save(path)


def create_motion_gif(src: Path, dest: Path) -> None:
    base = Image.open(src).convert("RGB").resize((1140, 456), Image.LANCZOS)
    frames = []
    for i in range(10):
        frame = base.copy().convert("RGBA")
        overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        x = -180 + i * 150
        draw.polygon([(x, 0), (x + 95, 0), (x + 275, 456), (x + 180, 456)], fill=(255, 255, 255, 34))
        frames.append(Image.alpha_composite(frame, overlay).convert("P", palette=Image.Palette.ADAPTIVE))
    frames[0].save(dest, save_all=True, append_images=frames[1:], duration=90, loop=0)


def p(text: str) -> str:
    return f'<p style="margin:10px 0 14px 0;">{esc(text)}</p>'


def h2(text: str) -> str:
    return (
        f'<h2 style="font-size:22px;line-height:1.25;margin:30px 0 14px 0;'
        f'font-weight:500;color:#2b2f36;letter-spacing:0;">{esc(text)}</h2>'
    )


def img(src: str, alt: str, height_note: str = "") -> str:
    note = (
        f'<p style="text-align:center;color:#6b7280;margin:-8px 0 18px 0;">{esc(height_note)}</p>'
        if height_note
        else ""
    )
    return (
        f'<p style="text-align:center;margin:0 0 18px 0;">'
        f'<img src="{esc(src)}" width="1140" alt="{esc(alt)}" '
        f'style="max-width:100%;height:auto;display:block;margin:0 auto;">'
        f"</p>{note}"
    )


def page(body: str) -> str:
    return (
        '<div style="font-family:Arial,Helvetica,sans-serif;color:#24292f;line-height:1.62;'
        'max-width:1140px;margin:0 auto;padding:0 8px;font-size:16px;">'
        f"{body}</div>"
    )


def color_band(title: str, rows: list[tuple[str, str]], bg: str = "#e9f6eb", accent: str = "#156f45") -> str:
    items = "\n".join(
        f'<p style="margin:8px 0;"><strong>- {esc(k)}</strong> - {esc(v)}</p>' for k, v in rows
    )
    return (
        f'<div style="background:{bg};padding:18px 18px;margin:18px 0;border-left:6px solid {accent};">'
        f'<h3 style="margin:0 0 10px 0;font-size:17px;color:#1f2937;">{esc(title)}</h3>{items}</div>'
    )


def proof_steps(rows: list[tuple[str, str, str]]) -> str:
    cells = []
    for idx, (label, title, body) in enumerate(rows, start=1):
        cells.append(
            '<blockquote style="margin:14px 0;padding:14px 14px;border-left:5px solid '
            f'{label};background:#fbfcfe;">'
            f'<p style="margin:0 0 4px 0;"><strong>{idx:02d}. {esc(title)}</strong></p>'
            f'<p style="margin:0;color:#374151;">{esc(body)}</p>'
            '</blockquote>'
        )
    return "\n".join(cells)


def image_slot(slot_id: str, title: str, dimensions: str, purpose: str, requirements: list[str]) -> str:
    lis = "\n".join(f'<li style="margin:5px 0;">{esc(item)}</li>' for item in requirements)
    return (
        f'<blockquote data-slot-id="{esc(slot_id)}" style="margin:20px 0;padding:16px;'
        'border:2px dashed #2f80ed;background:#f7fbff;">'
        f'<h3 style="margin:0 0 8px 0;font-size:18px;color:#10233f;">PRODUCT IMAGE REQUIREMENT - {esc(title)}</h3>'
        f'<p style="margin:0 0 8px 0;"><strong>Target:</strong> {esc(dimensions)}. {esc(purpose)}</p>'
        f'<ul style="margin:0;padding-left:20px;">{lis}</ul>'
        '<p style="margin:8px 0 0 0;color:#586574;">Replace this whole block with a centered img width 1140 module after image generation.</p>'
        '</blockquote>'
    )


def spec_table(rows: list[tuple[str, str]]) -> str:
    body = "\n".join(
        f'<tr style="background:{"#f7f7f7" if idx % 2 == 0 else "#fff"};">'
        f'<td style="padding:11px;border:1px solid #dedede;font-weight:bold;width:38%;vertical-align:top;">{esc(k)}</td>'
        f'<td style="padding:11px;border:1px solid #dedede;vertical-align:top;word-break:break-word;">{esc(v)}</td>'
        '</tr>'
        for idx, (k, v) in enumerate(rows)
    )
    return f'<table style="width:100%;border-collapse:collapse;margin:18px 0;font-size:15px;table-layout:fixed;">{body}</table>'


def package_table(rows: list[tuple[str, str]]) -> str:
    body = "\n".join(
        f'<tr><td style="padding:10px;border:1px solid #d7e4ef;font-weight:bold;width:34%;">{esc(k)}</td>'
        f'<td style="padding:10px;border:1px solid #d7e4ef;">{esc(v)}</td></tr>'
        for k, v in rows
    )
    return f'<table style="width:100%;border-collapse:collapse;background:#eef7ff;margin:16px 0;table-layout:fixed;">{body}</table>'


def faq(items: list[tuple[str, str]]) -> str:
    rows = [h2("INTREBARI FRECVENTE")]
    for idx, (q, a) in enumerate(items, start=1):
        rows.append(f'<p style="margin:14px 0;"><strong>{idx}. {esc(q)}</strong><br>{esc(a)}</p>')
    return "\n".join(rows)


def review_module() -> str:
    return (
        h2("RECENZII SI DOVADA SOCIALA")
        + img("../assets/review_evidence_template_1140x456.png", "Review evidence template board")
        + '<blockquote style="margin:12px 0;padding:14px;border-left:5px solid #f4b740;background:#fff8e8;">'
        + '<p style="margin:0;"><strong>Regula:</strong> acest modul nu este FAQ. Se completeaza numai cu texte, ratinguri si date extrase din recenzii reale. Daca nu exista date, modulul se omite sau ramane cerinta pentru urmatorul agent.</p>'
        + '</blockquote>'
    )


def cta(title: str, body: str) -> str:
    return (
        '<div style="background:#050505;padding:20px;margin:26px 0;text-align:center;border:5px solid #f4c300;">'
        f'<p style="font-size:18px;font-weight:bold;color:#fff;margin:8px 0;">{esc(title)}</p>'
        f'<p style="font-size:16px;color:#fff;margin:8px 0;">{esc(body)}</p>'
        '</div>'
    )


def module_plan(case: dict) -> list[dict]:
    plan = []
    for idx, module in enumerate(case["modules"]):
        plan.append(
            {
                "module_id": module["id"],
                "buyer_question": module["question"],
                "purpose": module["purpose"],
                "comes_after": case["modules"][idx - 1]["id"] if idx else "input_audit",
                "sets_up_next": case["modules"][idx + 1]["id"] if idx + 1 < len(case["modules"]) else "review_log",
                "required_evidence": module.get("evidence", []),
                "html_component": module["component"],
                "asset_slots": module.get("asset_slots", []),
                "failure_mode": module.get("failure", "Module becomes decorative or unsupported by evidence."),
            }
        )
    return plan


def build_cases(asset_paths: dict[str, Path]) -> list[dict]:
    return [
        {
            "id": "01_ev_charger_mobile_tech",
            "title": "EV charger mobile technical detail",
            "product_type": "technical_electronics",
            "banner": rel(asset_paths["ev"]),
            "truth": {
                "core_result": "Cumparatorul intelege rapid daca statia se potriveste masinii si locului de montaj.",
                "pain_points": ["neclaritate despre compatibilitate", "teama de instalare gresita", "specificatii greu de verificat"],
                "constraints": ["nu promite instalare", "nu folosi certificari fara dovada"],
            },
            "modules": [
                {"id": "product_tech_hero", "question": "Ce produs este si de ce conteaza pentru mine?", "purpose": "Deschide cu rezultat tehnic si context EV.", "component": "img.banner", "asset_slots": ["banner_ev_tech"]},
                {"id": "fit_first_logic", "question": "Se potriveste masinii si spatiului meu?", "purpose": "Mută atentia pe compatibilitate inainte de decor.", "component": "blockquote.sequence", "evidence": ["putere", "conector", "protectie"]},
                {"id": "product_cutout_requirement", "question": "Cum arata produsul si conectorul real?", "purpose": "Cere imaginea care dovedeste produsul.", "component": "image_requirement", "asset_slots": ["product_cutout", "connector_crop"]},
                {"id": "feature_proof_band", "question": "Care sunt dovezile pentru functii?", "purpose": "Leaga fiecare functie de beneficiu verificabil.", "component": "color_band", "evidence": ["WiFi/RFID", "IP rating", "power"]},
                {"id": "specs_table", "question": "Parametrii imi ajung?", "purpose": "Confirmare rationala dupa context.", "component": "table.specs", "evidence": ["all specs"]},
                {"id": "install_scene_requirement", "question": "Cum imi imaginez montajul?", "purpose": "Cere imagine de scenariu sigur, fara DIY riscant.", "component": "image_requirement", "asset_slots": ["garage_scene"]},
                {"id": "faq", "question": "Ce as verifica inainte sa cumpar?", "purpose": "Raspunde obiectiilor de compatibilitate.", "component": "faq"},
                {"id": "motion_support", "question": "Pagina poate folosi miscare?", "purpose": "Demonstreaza GIF ca modul separat.", "component": "img.gif", "asset_slots": ["motion_gif"]},
                {"id": "trust_close", "question": "Cu ce raman la final?", "purpose": "Inchide fara promisiuni nesustinute.", "component": "cta"},
            ],
            "body": lambda: page(
                img(rel(asset_paths["ev"]), "EV charger technical banner")
                + h2("IN PRIMELE SECUNDE: POTRIVIRE, CONTROL, SIGURANTA")
                + p("Pentru o statie EV, cumparatorul nu cauta doar un obiect tehnic. El vrea sa stie daca produsul se potriveste masinii, spatiului si modului lui de incarcare.")
                + proof_steps(
                    [
                        ("#0ea5e9", "Compatibilitatea se decide prima", "Puterea, conectorul si alimentarea trebuie sa fie vizibile in primele module."),
                        ("#22c55e", "Controlul trebuie explicat prin scenariu", "WiFi si RFID se prezinta ca moduri de administrare, nu ca termeni decorativi."),
                        ("#7c3aed", "Specificatiile vin dupa imagine", "Tabelul confirma decizia dupa ce contextul este clar."),
                    ]
                )
                + image_slot(
                    "ev_product_cutout",
                    "produs + conector + display",
                    "1140x705",
                    "Imaginea trebuie sa arate exact produsul, nu o scena generica.",
                    [
                        "Produs central pe fundal tehnic navy/purple, display si cablu vizibile.",
                        "Crop lateral cu conectorul si pinii, luminat clar.",
                        "Zone goale pentru overlay deterministic: 11kW, WiFi/RFID, IP65.",
                        "Fara text generat de model si fara badge-uri neconfirmate.",
                    ],
                )
                + color_band(
                    "BENEFICII CARE AU DOVADA",
                    [
                        ("Putere si control", "foloseste exact valoarea din ProductTruthPack, fara rotunjiri persuasive."),
                        ("Protectie in utilizare", "IP65 sau alte standarde se scriu doar daca sunt in fisa produsului."),
                        ("Potrivire cu mediul", "garaj, parcare privata sau spatiu protejat se arata ca scenarii, nu ca promisiuni."),
                        ("Decizie mai usoara", "imaginea si tabelul raspund impreuna la intrebarea de compatibilitate."),
                    ],
                    "#e8f3ff",
                    "#0ea5e9",
                )
                + h2("SPECIFICATII TEHNICE COMPLETE")
                + spec_table(
                    [
                        ("Putere", "11 kW - daca este confirmat"),
                        ("Control", "WiFi, RFID - daca sunt confirmate"),
                        ("Protectie", "IP65 - daca este confirmat"),
                        ("Compatibilitate", "tip conector si alimentare verificate inainte de publicare"),
                        ("De verificat", "conditii locale de montaj si folosire"),
                    ]
                )
                + image_slot(
                    "ev_install_scene",
                    "scena de montaj verificabil",
                    "1140x684",
                    "Ajuta cumparatorul sa vada unde se foloseste produsul.",
                    [
                        "Garaj curat sau parcare privata, masina EV vizibila, statie pe perete.",
                        "Traseu cablu clar, fara cabluri periculoase sau montaj improvizat.",
                        "Callout-uri goale pentru overlay: sursa, pozitie masina, lungime cablu.",
                    ],
                )
                + faq(
                    [
                        ("Ce verific inainte de achizitie?", "Puterea, conectorul, alimentarea, mediul de montaj si modul de control."),
                        ("De ce apar intai imaginile?", "Pentru ca in mobil cumparatorul decide rapid daca produsul se potriveste vizual situatiei lui."),
                        ("Cand folosim tabelul?", "Dupa modulele vizuale, ca dovada rationala si nu ca prima impresie."),
                    ]
                )
                + img(rel(asset_paths["motion"]), "Animated trust and motion proof GIF")
                + cta("Prezentare tehnica usor de verificat", "Flux mobil: rezultat, compatibilitate, dovada vizuala, specificatii si obiectii.")
            ),
        },
        {
            "id": "02_handheld_vacuum_mobile_cleaning",
            "title": "Handheld vacuum mobile cleaning detail",
            "product_type": "home_cleaning",
            "banner": rel(asset_paths["brand"]),
            "truth": {
                "core_result": "Curata rapid masina, canapeaua si colturile mici fara sa scoti un aparat mare.",
                "pain_points": ["firimituri in masina", "praf in spatii inguste", "accesorii neclare"],
                "constraints": ["nu inventa cifre de aspiratie", "nu inventa durata bateriei"],
            },
            "modules": [
                {"id": "brand_motion_banner", "question": "De ce sa am incredere in pagina?", "purpose": "Deschide cu GIF si prezenta de brand.", "component": "img.gif", "asset_slots": ["motion_banner"]},
                {"id": "pain_scene", "question": "Ce problema imi rezolva?", "purpose": "Porneste de la masina/canapea/colturi.", "component": "text.blockquote"},
                {"id": "product_scene_requirement", "question": "Unde il folosesc?", "purpose": "Cere scena de produs in mana.", "component": "image_requirement", "asset_slots": ["car_scene", "sofa_scene"]},
                {"id": "feature_stack", "question": "Care functie imi aduce ce beneficiu?", "purpose": "Functie -> beneficiu -> dovada.", "component": "color_band"},
                {"id": "accessory_requirement", "question": "Ce face fiecare accesoriu?", "purpose": "Evita lista moarta de accesorii.", "component": "image_requirement", "asset_slots": ["accessory_board"]},
                {"id": "specs_table", "question": "Parametrii sunt suficienti?", "purpose": "Verifica putere, baterie, greutate.", "component": "table.specs"},
                {"id": "package_table", "question": "Ce primesc in cutie?", "purpose": "Face pachetul scanabil pe mobil.", "component": "table.package"},
                {"id": "faq", "question": "Ce mai poate bloca decizia?", "purpose": "Obiectii despre intretinere, zgomot si baterie.", "component": "faq"},
                {"id": "review_template", "question": "Exista dovada sociala reala?", "purpose": "Separă recenzia de FAQ.", "component": "img.review_template"},
                {"id": "trust_close", "question": "Care e mesajul final?", "purpose": "Inchidere fara claimuri neprobate.", "component": "cta"},
            ],
            "body": lambda: page(
                img(rel(asset_paths["motion"]), "Animated dark brand GIF")
                + h2("CURATAREA RAPIDA INCEPE CU O SCENA PE CARE O RECUNOSTI")
                + p("Pagina trebuie sa arate situatii reale: masina dupa drum, canapea cu praf local, birou cu firimituri sau colturi unde aparatul mare este prea incomod.")
                + proof_steps(
                    [
                        ("#16a34a", "Durerea este locala", "Nu vindem curatenie generica, ci rezolvarea mizeriei mici si dese."),
                        ("#2563eb", "Produsul trebuie tinut in mana", "Mobilul cere scara vizuala: marime, duza, acces in spatiu ingust."),
                        ("#f59e0b", "Accesoriile au roluri", "Fiecare duza trebuie legata de o suprafata concreta."),
                    ]
                )
                + image_slot(
                    "vacuum_use_scene",
                    "masina + canapea + produs in mana",
                    "1140x705",
                    "Prima imagine de produs dupa banner trebuie sa faca scenariul evident.",
                    [
                        "Stanga: scaun auto cu firimituri, produsul in mana si duza montata.",
                        "Dreapta: canapea sau colt ingust, close-up pe LED/duza.",
                        "Centru jos: produs cutout curat, fara text generat.",
                        "Zone goale pentru overlay: cordless, LED, filtru, accesorii.",
                    ],
                )
                + color_band(
                    "PRINCIPALELE BENEFICII SI CARACTERISTICI",
                    [
                        ("Aspiratie pentru murdarie locala", "valoarea se foloseste doar daca este confirmata de produs."),
                        ("Fara fir", "beneficiul se vede in masina si colturi, nu in propozitie izolata."),
                        ("LED pentru zone intunecate", "leaga lumina de sub scaun sau marginile canapelei."),
                        ("Filtru lavabil", "spune doar daca filtrul este confirmat ca reutilizabil."),
                        ("Greutate redusa", "transforma cifra in folosire cu o singura mana."),
                    ],
                )
                + image_slot(
                    "vacuum_accessory_board",
                    "placa de accesorii",
                    "1140x684",
                    "Arata ce primeste cumparatorul si unde se foloseste fiecare piesa.",
                    [
                        "Produs principal + 4 accesorii pe fundal alb/albastru deschis.",
                        "Fiecare accesoriu are zona goala de eticheta pentru overlay determinist.",
                        "Include mini-scene: perie pentru textile, duza plata pentru spatii inguste, furtun pentru colturi.",
                    ],
                )
                + h2("SPECIFICATII TEHNICE COMPLETE")
                + spec_table(
                    [
                        ("Putere aspirare", "9500 Pa - numai daca este confirmat"),
                        ("Baterie", "2200 mAh - numai daca este confirmat"),
                        ("Autonomie", "pana la 30 min - numai daca este confirmat"),
                        ("Greutate", "545 g - numai daca este confirmat"),
                        ("Recipient praf", "0.4 L - numai daca este confirmat"),
                        ("Nivel zgomot", "50 dB - numai daca este confirmat"),
                    ]
                )
                + h2("PACHET COMPLET")
                + package_table(
                    [
                        ("Aspirator portabil", "produs principal"),
                        ("Duza scurta", "pentru spatii inguste"),
                        ("Duza cu perie", "pentru textile si praf local"),
                        ("Cablu incarcare", "doar daca este inclus in faptele produsului"),
                        ("Manual", "daca apare in pachet"),
                    ]
                )
                + faq(
                    [
                        ("Este potrivit pentru masina?", "Da doar daca slotul vizual si specificatiile sustin portabilitatea si accesoriile."),
                        ("Cum se intretine?", "Se mentioneaza golirea recipientului si filtrul lavabil numai cand aceste informatii sunt confirmate."),
                        ("Ce imagine lipseste cel mai des?", "Placa de accesorii cu rol clar pentru fiecare piesa."),
                    ]
                )
                + review_module()
                + cta("Curatare rapida, explicata pe mobil", "Scena, produsul, accesoriile si parametrii lucreaza impreuna in loc sa fie liste separate.")
            ),
        },
        {
            "id": "03_beauty_personal_care_mobile",
            "title": "Beauty personal care mobile detail",
            "product_type": "beauty_personal_care",
            "banner": rel(asset_paths["blue"]),
            "truth": {
                "core_result": "Rutina de ingrijire pare mai simpla, mai confortabila si mai usor de repetat.",
                "pain_points": ["teama de disconfort", "nu intelege pasii de folosire", "nu stie cum se curata"],
                "constraints": ["nu promite rezultate estetice fara dovada", "nu folosi claims medicale"],
            },
            "modules": [
                {"id": "people_category_banner", "question": "Ce senzatie transmite categoria?", "purpose": "Emotie si categorie, fara claim medical.", "component": "img.banner"},
                {"id": "emotional_result", "question": "Ce rezultat de rutina cumpar?", "purpose": "Definește confortul, nu rezultate imposibile.", "component": "text.blockquote"},
                {"id": "model_use_requirement", "question": "Cum il folosesc fara disconfort?", "purpose": "Cere model-use sigur.", "component": "image_requirement", "asset_slots": ["model_use", "texture_crop"]},
                {"id": "routine_steps", "question": "Care sunt pasii?", "purpose": "Transforma produsul in rutina repetabila.", "component": "blockquote.sequence"},
                {"id": "specs_table", "question": "Ce detalii confirm?", "purpose": "Moduri, material, alimentare, curatare.", "component": "table.specs"},
                {"id": "faq", "question": "Ce nu avem voie sa exageram?", "purpose": "Limiteaza claims.", "component": "faq"},
                {"id": "review_template", "question": "Avem recenzii reale?", "purpose": "Social proof separat de QA.", "component": "img.review_template"},
                {"id": "trust_close", "question": "Cum se inchide pagina?", "purpose": "Confort si claritate.", "component": "cta"},
            ],
            "body": lambda: page(
                img(rel(asset_paths["blue"]), "People and category style banner")
                + h2("RUTINA MAI USOARA, NU PROMISIUNI EXAGERATE")
                + p("Pentru ingrijire personala, pagina trebuie sa creeze confort: cum se tine produsul, cum atinge pielea sau parul, cum se curata si cum se depoziteaza.")
                + image_slot(
                    "beauty_model_use",
                    "model-use + textura produs",
                    "1140x705",
                    "Imaginea trebuie sa arate folosirea reala si detaliul materialului.",
                    [
                        "Model calm, lumina curata, produsul folosit natural.",
                        "Close-up pe cap, material, suprafata sau accesoriu, dupa produs.",
                        "Fara before/after cosmetic si fara piele retusata excesiv.",
                        "Zone goale pentru overlay: confort, moduri, curatare, depozitare.",
                    ],
                )
                + color_band(
                    "SIGURANTA, CONFORT SI RUTINA",
                    [
                        ("Confort la folosire", "aratat prin mana, unghi si scara produsului."),
                        ("Material si contact", "close-up-ul sustine increderea fara text mult."),
                        ("Moduri de utilizare", "fiecare mod trebuie legat de un pas de rutina."),
                        ("Curatare si depozitare", "elimina teama ca produsul ramane greu de intretinut."),
                    ],
                    "#fff1f7",
                    "#db2777",
                )
                + proof_steps(
                    [
                        ("#db2777", "Pregatire", "Ce se face inainte de folosire si ce accesoriu se alege."),
                        ("#7c3aed", "Utilizare", "Cum se aplica sau se tine produsul in pozitie sigura."),
                        ("#0891b2", "Curatare", "Cum se indeparteaza reziduurile, doar daca produsul permite."),
                        ("#16a34a", "Depozitare", "Unde intra produsul dupa folosire si ce piese raman impreuna."),
                    ]
                )
                + h2("DETALII DE CONFIRMAT")
                + spec_table(
                    [
                        ("Tip produs", "completat din input"),
                        ("Moduri", "numai modurile confirmate"),
                        ("Material", "material exact, daca exista"),
                        ("Alimentare", "USB, baterie sau cablu, daca exista"),
                        ("Curatare", "lavabil/detasabil doar daca este confirmat"),
                    ]
                )
                + faq(
                    [
                        ("Putem promite rezultate vizibile?", "Nu fara date sau teste. Pagina poate promite doar rutina, confort si folosire verificabila."),
                        ("Ce imagine este obligatorie?", "Model-use plus close-up de material, ca sa nu ramana un produs abstract."),
                    ]
                )
                + review_module()
                + cta("Ingrijire personala explicata prin rutina", "Emotie la inceput, detalii vizuale la mijloc, limite clare la final.")
            ),
        },
        {
            "id": "04_baby_safety_mobile",
            "title": "Baby safety mobile detail",
            "product_type": "baby",
            "banner": rel(asset_paths["blue"]),
            "truth": {
                "core_result": "Parintele intelege rapid siguranta, igiena, pasii de folosire si curatarea.",
                "pain_points": ["teama pentru siguranta", "pasi neclari", "curatare complicata"],
                "constraints": ["nu folosi claims medicale", "nu promite sanatate sau dezvoltare"],
            },
            "modules": [
                {"id": "soft_people_banner", "question": "Pagina pare potrivita pentru parinti?", "purpose": "Deschide bland si sigur.", "component": "img.banner"},
                {"id": "safety_first", "question": "Este sigur si usor de controlat?", "purpose": "Siguranta inainte de feature.", "component": "color_band"},
                {"id": "baby_product_requirement", "question": "Cum se foloseste in rutina reala?", "purpose": "Cere scena produs + maini adulte + masa curata.", "component": "image_requirement", "asset_slots": ["routine_scene"]},
                {"id": "usage_steps", "question": "Care sunt pasii?", "purpose": "Reduce frictiunea.", "component": "blockquote.sequence"},
                {"id": "hygiene_requirement", "question": "Cum se curata?", "purpose": "Cere imagine de piese si curatare.", "component": "image_requirement", "asset_slots": ["cleaning_board"]},
                {"id": "specs_table", "question": "Ce parametri confirma siguranta?", "purpose": "Volum, alimentare, materiale.", "component": "table.specs"},
                {"id": "faq", "question": "Ce intreaba parintii?", "purpose": "Obiectii despre curatare si folosire.", "component": "faq"},
                {"id": "trust_close", "question": "Care este concluzia?", "purpose": "Inchidere calma.", "component": "cta"},
            ],
            "body": lambda: page(
                img(rel(asset_paths["blue"]), "Soft people category banner")
                + h2("PENTRU PRODUSE DE BEBELUSI, SIGURANTA VINE INAINTEA DECORULUI")
                + color_band(
                    "CE TREBUIE SA SIMTA PARINTELE",
                    [
                        ("Control", "intelege ce face fiecare buton sau functie."),
                        ("Igiena", "vede piesele care se curata sau se separa."),
                        ("Rutina", "stie pasii fara sa citeasca un manual lung."),
                        ("Limite clare", "nu apar promisiuni medicale sau de sanatate."),
                    ],
                    "#fff7ed",
                    "#f97316",
                )
                + image_slot(
                    "baby_routine_scene",
                    "rutina sigura pe masa curata",
                    "1140x705",
                    "Scena trebuie sa calmeze, nu sa supra-incarce pagina.",
                    [
                        "Masa curata, maini adulte, produsul si recipiente vizibile.",
                        "Fara bebelus in situatie riscanta si fara claim medical.",
                        "Zone goale pentru overlay: pas 1, pas 2, pas 3, curatare.",
                    ],
                )
                + proof_steps(
                    [
                        ("#f97316", "Pregatire", "Arata ingredientele, recipientul si produsul inainte de folosire."),
                        ("#22c55e", "Proces", "Arata fluxul produsului, fara elemente care par nesigure."),
                        ("#0ea5e9", "Curatare", "Piesele si igiena trebuie sa fie la fel de vizibile ca functiile."),
                    ]
                )
                + image_slot(
                    "baby_cleaning_board",
                    "piese demontabile si igiena",
                    "1140x684",
                    "Imaginea trebuie sa raspunda la intrebarea: se curata usor?",
                    [
                        "Piesele asezate ordonat pe fundal deschis.",
                        "Close-up pe zonele care intra in contact cu alimentele.",
                        "Etichete goale pentru overlay: clatire, asamblare, depozitare.",
                    ],
                )
                + h2("SPECIFICATII DE VERIFICAT")
                + spec_table(
                    [
                        ("Tip produs", "ex. aparat aburi/blender, daca este cazul"),
                        ("Materiale", "doar materialele confirmate"),
                        ("Capacitate", "valoare exacta din input"),
                        ("Alimentare", "valoare exacta din input"),
                        ("Curatare", "piese lavabile/detasabile doar daca sunt confirmate"),
                    ]
                )
                + faq(
                    [
                        ("De ce nu incepem cu tabelul?", "Parintele trebuie intai sa vada siguranta si rutina, apoi confirma parametrii."),
                        ("Ce claims sunt interzise?", "Sanatate, dezvoltare, efect medical sau rezultate fara dovada."),
                    ]
                )
                + cta("Pagina calma pentru decizie rapida", "Siguranta, rutina si curatarea sunt ordinea corecta pentru mobil.")
            ),
        },
        {
            "id": "05_coffee_kitchen_mobile_lifestyle",
            "title": "Coffee and kitchen mobile lifestyle detail",
            "product_type": "coffee_kitchen",
            "banner": rel(asset_paths["brand"]),
            "truth": {
                "core_result": "Cumparatorul vede gustul, comoditatea si curatarea ca parte din aceeasi rutina.",
                "pain_points": ["spuma inconsistente", "curatare neclara", "nu intelege setarile"],
                "constraints": ["nu promite gust perfect fara dovada", "nu inventa putere sau timp"],
            },
            "modules": [
                {"id": "lifestyle_banner", "question": "Ce rezultat de viata cumpar?", "purpose": "Creeaza pofta si rutina.", "component": "img.banner"},
                {"id": "result_scene", "question": "Ce obtin in fiecare zi?", "purpose": "Rezultat concret, nu functie seaca.", "component": "text.blockquote"},
                {"id": "product_scene_requirement", "question": "Cum arata rezultatul?", "purpose": "Cere cafea/masa/produs.", "component": "image_requirement", "asset_slots": ["coffee_result_scene"]},
                {"id": "feature_proof", "question": "De ce merita functiile?", "purpose": "Leaga functie de rutina.", "component": "color_band"},
                {"id": "cleaning_requirement", "question": "Se curata usor?", "purpose": "Cere imagine de spalare/piese.", "component": "image_requirement", "asset_slots": ["cleaning_scene"]},
                {"id": "specs_table", "question": "Ce confirm tehnic?", "purpose": "Putere, volum, materiale.", "component": "table.specs"},
                {"id": "faq", "question": "Ce obiectii raman?", "purpose": "Spuma, zgomot, curatare.", "component": "faq"},
                {"id": "review_template", "question": "Avem feedback real?", "purpose": "Review separat.", "component": "img.review_template"},
                {"id": "trust_close", "question": "Ce retine cumparatorul?", "purpose": "Rutina si confort.", "component": "cta"},
            ],
            "body": lambda: page(
                img(rel(asset_paths["brand"]), "Dark lifestyle brand banner")
                + h2("NU VINZI UN APARAT, VINZI O RUTINA MAI PLACUTA")
                + p("Pentru bucatarie si cafea, pagina trebuie sa arate rezultatul: bautura, textura, masa curata si produsul la scara reala.")
                + image_slot(
                    "coffee_result_scene",
                    "rezultat + produs + mana",
                    "1140x705",
                    "Prima imagine trebuie sa faca rezultatul aproape palpabil.",
                    [
                        "Cana sau pahar cu rezultat final, produsul in apropiere, mana folosind produsul.",
                        "Fundal cald dar curat, fara aglomeratie.",
                        "Close-up pe textura rezultatului, daca produsul are legatura cu spuma/mixare.",
                        "Fara text generat, fara claim de gust perfect.",
                    ],
                )
                + color_band(
                    "DE LA FUNCTIE LA MOMENTUL DE FOLOSIRE",
                    [
                        ("Rezultat vizibil", "arata produsul alaturi de rezultatul pe care il creeaza."),
                        ("Control simplu", "butonul sau modul de operare trebuie vazut in close-up."),
                        ("Curatare rapida", "daca exista piese lavabile, ele merita un modul separat."),
                        ("Depozitare", "produsul trebuie sa para usor de pastrat in bucatarie."),
                    ],
                    "#fff7ed",
                    "#b45309",
                )
                + proof_steps(
                    [
                        ("#b45309", "Pregateste", "Ingredientele si recipientul apar langa produs."),
                        ("#0ea5e9", "Foloseste", "Arata un gest simplu, nu doar produsul static."),
                        ("#16a34a", "Curata", "Demonstreaza piese si spalare daca sunt confirmate."),
                    ]
                )
                + image_slot(
                    "coffee_cleaning_board",
                    "curatare si depozitare",
                    "1140x684",
                    "Inlatura teama ca aparatul va fi folosit o data si abandonat.",
                    [
                        "Piese pe fundal deschis, chiuveta sau prosop curat.",
                        "Zone pentru overlay: clatire, uscare, depozitare.",
                        "Nu arata produsul complet scufundat daca nu este rezistent la apa.",
                    ],
                )
                + h2("SPECIFICATII DE CONFIRMAT")
                + spec_table(
                    [
                        ("Tip produs", "ex. spumator, blender mic, aparat cafea"),
                        ("Putere", "valoare exacta din input"),
                        ("Volum", "valoare exacta din input"),
                        ("Material", "otel inoxidabil, ABS etc. doar daca exista"),
                        ("Curatare", "componenta lavabila doar daca e confirmata"),
                    ]
                )
                + faq(
                    [
                        ("Ce trebuie sa arate prima imagine?", "Rezultatul final plus produsul, nu doar un cutout izolat."),
                        ("Ce nu promitem?", "Gust perfect, rezultate garantate sau curatare imposibil de probat."),
                    ]
                )
                + review_module()
                + cta("Rutina de bucatarie explicata vizual", "Rezultat, gest, curatare si specificatii intr-o pagina mobila continua.")
            ),
        },
        {
            "id": "06_store_brand_trust_mobile",
            "title": "Store and brand trust mobile detail",
            "product_type": "store_brand_trust",
            "banner": rel(asset_paths["brand"]),
            "truth": {
                "core_result": "Brandul devine familiar prin produs, oameni, pachet si dovada reala.",
                "pain_points": ["brand necunoscut", "teama de promisiuni goale", "nu exista dovada sociala"],
                "constraints": ["nu inventa servicii platforma", "nu inventa review-uri"],
            },
            "modules": [
                {"id": "brand_trust_banner", "question": "De ce pare brandul familiar?", "purpose": "Black premium + oameni + pachet.", "component": "img.banner"},
                {"id": "brand_positioning", "question": "Ce trebuie sa simt despre brand?", "purpose": "Leaga brandul de contextul de cumparare.", "component": "color_band"},
                {"id": "package_people_requirement", "question": "Cum arata increderea vizual?", "purpose": "Cere oameni + pachet + produs.", "component": "image_requirement", "asset_slots": ["people_package_scene"]},
                {"id": "service_evidence_band", "question": "Ce servicii pot mentiona?", "purpose": "Doar servicii dovedite.", "component": "color_band", "evidence": ["seller/platform service facts"]},
                {"id": "range_familiarity_requirement", "question": "Ce gama are brandul?", "purpose": "Arata varietate fara a parea logo repetat.", "component": "image_requirement", "asset_slots": ["range_board"]},
                {"id": "review_template", "question": "Avem recenzii reale?", "purpose": "Testimonial separat de QA.", "component": "img.review_template"},
                {"id": "faq", "question": "Ce obiectii despre brand raman?", "purpose": "Raspunde fara claims inventate.", "component": "faq"},
                {"id": "trust_close", "question": "Cum inchidem?", "purpose": "Claritate, nu presiune.", "component": "cta"},
            ],
            "body": lambda: page(
                img(rel(asset_paths["brand"]), "Dark brand trust banner")
                + h2("INCREDEREA NU INSEAMNA SA REPETI LOGO-UL")
                + color_band(
                    "CE FACE BANNERUL DE BRAND",
                    [
                        ("Fundal negru", "creste senzatia premium si separa brandul de pagina alba."),
                        ("Oameni reali sau stil realist", "adauga apropiere si reduce raceala unui brand necunoscut."),
                        ("Pachet si context eMAG", "creeaza familiaritate prin obiecte recunoscibile, fara a pretinde parteneriat neconfirmat."),
                        ("Ancore de serviciu", "se scriu doar daca exista dovada: altfel se formuleaza neutru ca proces."),
                    ],
                    "#eef2ff",
                    "#4f46e5",
                )
                + image_slot(
                    "brand_people_package",
                    "oameni + pachet + produs",
                    "1140x456 sau 1140x684",
                    "Imaginea trebuie sa faca brandul cald si familiar.",
                    [
                        "Doua persoane sau o persoana primind/deschizand pachetul, expresie naturala.",
                        "Cutie simpla cu zona pentru overlay de brand; nu insera logo eMAG daca drepturile nu permit.",
                        "Produsul sau gama apare in plan secundar, nu doar logo-ul.",
                    ],
                )
                + color_band(
                    "SERVICII SI DOVEZI: NU LE INVENTAM",
                    [
                        ("Proces de suport", "se poate descrie neutru daca exista instructiuni pe ambalaj sau manual."),
                        ("Retur, garantie, livrare", "se mentioneaza numai cu dovada platforma/seller."),
                        ("Recenzii", "nume, stele, date si citate doar din review-uri reale."),
                    ],
                    "#f8fafc",
                    "#111827",
                )
                + image_slot(
                    "brand_range_board",
                    "gama de produse ca familiaritate",
                    "1140x705",
                    "Arata ca brandul are o lume coerenta, nu un singur produs izolat.",
                    [
                        "3-5 produse sau categorii in aceeasi familie vizuala.",
                        "Fundal curat, ancore cromatice consistente cu bannerul.",
                        "Fara badge-uri oficiale si fara claims neconfirmate.",
                    ],
                )
                + review_module()
                + faq(
                    [
                        ("Ce facem daca nu avem recenzii reale?", "Nu completam testimonialul. Lasam cerinta pentru colectarea dovezii sau omitem modulul."),
                        ("Ce facem daca nu avem dovada serviciilor?", "Scriem doar proces neutru, fara termeni care promit beneficii comerciale."),
                    ]
                )
                + cta("Brand trust ca sistem, nu ca logo repetat", "Banner, oameni, pachet, gama, dovezi si FAQ trebuie sa lucreze in aceeasi ordine.")
            ),
        },
    ]


def write_case(case: dict) -> None:
    case_dir = OUT / case["id"]
    case_dir.mkdir(parents=True, exist_ok=True)
    html = case["body"]()
    (case_dir / "detail.html").write_text(html + "\n", encoding="utf-8")
    preview = (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>eMAG mobile preview</title>"
        "<style>body{margin:0;background:#fff;} img{max-width:100%;height:auto;}</style>"
        "</head><body>"
        f"{html}</body></html>"
    )
    (case_dir / "preview_mobile.html").write_text(preview + "\n", encoding="utf-8")
    plan = module_plan(case)
    (case_dir / "module_plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    slots = [
        {
            "slot_id": slot,
            "source_module": module["id"],
            "status": "pending_next_image_agent",
            "note": "Only product/detail image slots are placeholders. Banner/GIF/review template modules are already separate assets.",
        }
        for module in case["modules"]
        for slot in module.get("asset_slots", [])
    ]
    (case_dir / "image_requirements.json").write_text(json.dumps(slots, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (case_dir / "product_truth_pack.json").write_text(
        json.dumps(
            {
                "product_type": case["product_type"],
                "product_title": case["title"],
                **case["truth"],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def write_index(cases: list[dict]) -> None:
    links = "\n".join(
        f'<tr><td style="padding:10px;border:1px solid #ddd;">{idx}</td>'
        f'<td style="padding:10px;border:1px solid #ddd;"><a href="{case["id"]}/detail.html">{esc(case["title"])}</a></td>'
        f'<td style="padding:10px;border:1px solid #ddd;">{esc(case["product_type"])}</td>'
        f'<td style="padding:10px;border:1px solid #ddd;">{len(case["modules"])} modules</td></tr>'
        for idx, case in enumerate(cases, start=1)
    )
    index = page(
        h2("eMAG HTML Detail Agent v1.3 mobile reference runs")
        + p("This set uses the 2026-05-23 mobile-adapted Excitat store sample as the structural baseline: single-column image flow, GIF support, blockquote explanation, specs/package tables, FAQ, and review/social-proof as a separate module.")
        + '<table style="width:100%;border-collapse:collapse;table-layout:fixed;">'
        + '<tbody>'
        + links
        + "</tbody></table>"
    )
    (OUT / "index.html").write_text(index + "\n", encoding="utf-8")


def write_reference_findings() -> None:
    text = """# v1.3 mobile reference findings

Source baseline: `output/emag_detail_html_live_batch`, captured from the earlier eMAG detail-page research store.

- 30/30 sampled details are one-image-per-row mobile-first flows.
- 30/30 include GIF assets; total GIF count is 44.
- 320 images in the sample set; most production HTML uses `width=\"1140\"` even when rendered narrower on mobile.
- Common module rhythm: banner/detail image -> short centered or blockquote copy -> image/GIF -> proof block -> parameters/package -> brand closer.
- Common safe/gray tags: `p`, `strong`, `img`, `br`, `td`, `li`, `div`, `tr`, `blockquote`, `h2`, `ul`, `h1`.
- Review/testimonial is not FAQ. It requires real review evidence; otherwise it remains a pending asset/data slot.
- Product image placeholders in this v1.3 run are intentional. Banner/GIF/review-template modules are already assets; only product/detail imagery is delegated to the next image agent.
"""
    (OUT / "reference_findings.md").write_text(text, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    assets = {
        "brand": copy_asset("01_brand_trust_dark_package_rendered_1140x456.png", "brand_trust_dark_1140x456.png"),
        "ev": copy_asset("02_ev_charger_product_tech_rendered_1140x326.png", "ev_tech_hero_1140x326.png"),
        "blue": copy_asset("03_official_people_category_style_rendered_1140x456.png", "official_blue_people_style_1140x456.png"),
    }
    review = ASSETS / "review_evidence_template_1140x456.png"
    create_review_template(review)
    assets["review"] = review

    if V12_ASSET.exists():
        shutil.copy2(V12_ASSET, ASSETS / "brand_trust_motion_1140x456.gif")
    else:
        create_motion_gif(assets["brand"], ASSETS / "brand_trust_motion_1140x456.gif")
    assets["motion"] = ASSETS / "brand_trust_motion_1140x456.gif"

    cases = build_cases(assets)
    for case in cases:
        write_case(case)
    write_index(cases)
    write_reference_findings()
    (OUT / "review_template_requirements.json").write_text(
        json.dumps(
            {
                "module_id": "review_social_proof_board",
                "not_faq": True,
                "template_asset": review.relative_to(OUT).as_posix(),
                "allowed_inputs": ["real review text", "real rating evidence", "source date/url", "reviewer display name only if sourced"],
                "blocked_inputs": ["invented names", "invented dates", "invented star ratings", "generic FAQ copied into review cards"],
                "fallback": "omit the review board or keep it as a pending evidence slot",
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(OUT)


if __name__ == "__main__":
    main()
