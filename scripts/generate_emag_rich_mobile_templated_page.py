#!/usr/bin/env python3
"""Builds the final premium eMAG mobile-first detail page HTML integrating templated cards and GIF icons."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path("/Users/cc/Desktop/photo_show")
OUT = ROOT / "output/emag_detail_suite_templated"
ASSETS_DIR = OUT / "assets"


def esc(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def html_img(src_rel: str, alt: str, max_w: int = 1140) -> str:
    return (
        f'<p style="text-align:center;margin:0 0 20px 0;">'
        f'<img src="{esc(src_rel)}" alt="{esc(alt)}" '
        f'style="max-width:100%;width:{max_w}px;height:auto;display:block;margin:0 auto;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.08);">'
        f"</p>"
    )


def proof_steps(rows: list[tuple[str, str, str]]) -> str:
    cells = []
    for idx, (color, title, body) in enumerate(rows, start=1):
        cells.append(
            '<blockquote style="margin:16px 0;padding:16px;border-left:5px solid '
            f'{color};background:#f8fafc;border-radius:0 8px 8px 0;box-shadow:0 1px 3px rgba(0,0,0,0.02);">'
            f'<p style="margin:0 0 4px 0;font-size:16px;font-weight:bold;color:#1e293b;">{idx:02d}. {esc(title)}</p>'
            f'<p style="margin:0;font-size:14px;color:#64748b;line-height:1.5;">{esc(body)}</p>'
            '</blockquote>'
        )
    return "\n".join(cells)


def spec_table(rows: list[tuple[str, str]]) -> str:
    body = "\n".join(
        f'<tr style="background:{"#f8fafc" if idx % 2 == 0 else "#ffffff"};">'
        f'<td style="padding:12px 16px;border:1px solid #e2e8f0;font-weight:bold;color:#475569;width:38%;vertical-align:top;font-size:14px;">{esc(k)}</td>'
        f'<td style="padding:12px 16px;border:1px solid #e2e8f0;color:#1e293b;vertical-align:top;word-break:break-word;font-size:14px;">{esc(v)}</td>'
        '</tr>'
        for idx, (k, v) in enumerate(rows)
    )
    return f'<table style="width:100%;border-collapse:collapse;margin:20px 0;table-layout:fixed;border-radius:8px;overflow:hidden;border:1px solid #e2e8f0;">{body}</table>'


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    
    # Paths of assets relative to the output HTML file
    # Banners/Cards:
    # 01_brand_frame_hero.jpg
    # 02_core_feature_proof.jpg
    # 03_detail_or_material_proof.jpg
    # 04_parameters_or_compatibility.jpg
    # 05_package_contents.jpg
    # 06_usage_or_scenario.jpg
    #
    # GIFs and brand icons are located in ../emag_motion_effect_demos/
    gif_dir = "../emag_motion_effect_demos"
    
    body = (
        '<div style="font-family:Arial,Helvetica,sans-serif;color:#1e293b;line-height:1.62;max-width:1140px;margin:0 auto;padding:16px 8px;font-size:16px;background:#ffffff;">'
        
        # 1. Hero Banner
        + html_img("01_brand_frame_hero.jpg", "EXCITAT Premium EV Charging Cable Hero")
        
        # Intro
        + '<div style="margin:24px 0 32px;text-align:center;">'
        + '<h2 style="font-size:28px;color:#0f172a;margin-bottom:8px;font-weight:bold;letter-spacing:-0.5px;">EXCITAT Cablu Incarcare EV</h2>'
        + '<p style="color:#64748b;font-size:17px;max-width:800px;margin:0 auto;">O solutie premium si ultra-rapida de incarcare pentru vehiculul dumneavoastra electric, proiectata pentru siguranta si durabilitate maxima.</p>'
        + '</div>'
        
        # Brand Trust GIF Banner (breathing border effect)
        + h2("1. Brand Authority & Trust")
        + html_img(f"{gif_dir}/brand_icon_glow_ai.gif", "EXCITAT Neon Brand Tag", max_w=240)
        + p("Familiaritatea si increderea in brand sunt asigurate prin elemente de design premium si indicatori vizuali dinamici care subliniaza calitatea produsului.")
        
        # 2. Features Grid Card
        + h2("2. Core Technical Performance")
        + html_img("02_core_feature_proof.jpg", "EXCITAT Core Features proof grid")
        
        # 3. Macro details Zoom-in
        + h2("3. Macro Detail Zoom-In")
        + html_img("03_detail_or_material_proof.jpg", "EXCITAT Precision contact details")
        
        # 4. Interactive GIF preview for details
        + h2("4. Interactive Detail Visualisation (GIF)")
        + html_img(f"{gif_dir}/stable_precise_product_glow.gif", "EXCITAT Precise product glow animation")
        
        # 5. Technical Parameters table
        + h2("5. Technical Parameters & Compatibility")
        + html_img("04_parameters_or_compatibility.jpg", "EXCITAT Technical parameters")
        + spec_table([
            ("Tip Conector", "Type 2 la Type 2 (IEC 62196-2)"),
            ("Putere de incarcare", "Pana la 22 kW (Trifazat) / 32A"),
            ("Tensiune de lucru", "480V AC"),
            ("Lungime cablu", "5 metri (TPU premium)"),
            ("Clasa de protectie", "IP65 (rezistent la praf si jeturi de apa)"),
            ("Temperatura de lucru", "-30°C pana la +50°C")
        ])
        
        # 6. Package contents card
        + h2("6. Package Contents")
        + html_img("05_package_contents.jpg", "EXCITAT Package contents")
        
        # 7. Real world scenario card
        + h2("7. Usage Steps & Scenario")
        + html_img("06_usage_or_scenario.jpg", "EXCITAT Real-world charging scenario")
        
        # Process steps checklist matching listing_b styles
        + proof_steps([
            ("#0ea5e9", "Conectati la statia de incarcare", "Introduceti conectorul Type 2 tata in portul statiei publice sau de perete (wallbox)."),
            ("#f59e0b", "Conectati la portul masinii", "Introduceti conectorul Type 2 mama in portul de incarcare al vehiculului dumneavoastra electric."),
            ("#10b981", "Incepe incarcarea sigura", "Statia si masina negociaza automat parametrii optimi de curent. Monitorizati statusul din masina.")
        ])
        
        # 8. Dynamic Badges Pulsate preview
        + h2("8. Dynamic Parameter Highlight (GIF)")
        + html_img(f"{gif_dir}/stable_badge_pulsate.gif", "EXCITAT Badge pulsate animation")
        
        # Brand Icons Row
        + '<div style="display:flex;gap:20px;justify-content:center;align-items:center;margin:40px 0;padding:20px;border-top:1px solid #e2e8f0;border-bottom:1px solid #e2e8f0;">'
        + f'<img src="{gif_dir}/brand_icon_charge_ai.gif" style="width:80px;height:80px;">'
        + f'<img src="{gif_dir}/brand_icon_shield_ai.gif" style="width:80px;height:80px;">'
        + '</div>'
        
        # Call to action footer
        + '<div style="background:#0f172a;padding:32px 24px;border-radius:16px;text-align:center;margin-top:40px;border:3px solid #00e5ff;">'
        + '<h3 style="color:#ffffff;font-size:22px;margin:0 0 10px 0;font-weight:bold;letter-spacing:-0.5px;">EXCITAT - Calitate Fara Compromis</h3>'
        + '<p style="color:#94a3b8;font-size:15px;margin:0 0 20px 0;">Fiecare cablu este testat individual pentru a asigura o compatibilitate si o siguranta 100% cu vehiculul dumneavoastra.</p>'
        + '<div style="display:inline-block;padding:12px 32px;background:#00e5ff;color:#0f172a;font-weight:bold;border-radius:8px;font-size:15px;text-transform:uppercase;letter-spacing:0.5px;">Incarca Acum</div>'
        + '</div>'
        
        + "</div>"
    )
    
    # Wrap in standard preview boilerplate
    html_page = (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>EXCITAT Premium EV Charging Cable Listing</title>'
        '<style>body{margin:0;background:#f8fafc;} '
        'h2{font-size:22px;line-height:1.25;margin:36px 0 14px 0;font-weight:bold;color:#0f172a;border-bottom:2px solid #f1f5f9;padding-bottom:8px;}'
        'p{color:#475569;margin:10px 0 16px 0;} </style></head>'
        f"<body>{body}</body></html>"
    )
    
    (OUT / "detail_page_templated.html").write_text(html_page, encoding="utf-8")
    print(f"Generated final templated detail page HTML: {OUT / 'detail_page_templated.html'}")


def h2(text: str) -> str:
    return f'<h2>{esc(text)}</h2>'


def p(text: str) -> str:
    return f'<p>{esc(text)}</p>'


if __name__ == "__main__":
    main()
