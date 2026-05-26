#!/usr/bin/env python3
"""Render a minimal eMAG detail HTML snippet from product + section-plan JSON."""

from __future__ import annotations

import argparse
import json
import pathlib
from html import escape


def load_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text())


def image_for_slot(product: dict, slot: str | None) -> str | None:
    if not slot:
        return None
    for item in product.get("image_assets", []):
        if item.get("slot") == slot:
            return item.get("url")
    return None


def render_img(url: str, alt: str) -> str:
    return (
        '<p style="text-align:center;">\n'
        f'  <img src="{escape(url, quote=True)}" alt="{escape(alt, quote=True)}" width="800">\n'
        "</p>"
    )


def render_list(items: list[str]) -> str:
    lines = ["<ul>"]
    lines.extend(f"  <li>{escape(item)}</li>" for item in items)
    lines.append("</ul>")
    return "\n".join(lines)


def render_dense_feature(product: dict, plan: dict) -> str:
    blocks: list[str] = []
    for section in plan.get("sections", []):
        slot = section.get("image_slot")
        url = image_for_slot(product, slot)
        if url and slot != "motion_proof_gray_zone":
            blocks.append(render_img(url, section.get("title", product.get("product_title", "Product image"))))

        title = section.get("title")
        if title:
            blocks.append(f"<h2>{escape(title)}</h2>")

        body_points = section.get("body_points", [])
        section_type = section.get("section_type")
        if section_type in {"feature_proof", "specs", "package_contents", "safety_or_usage", "compatibility"}:
            blocks.append(render_list(body_points))
        elif body_points:
            lead = body_points[0]
            tail = " ".join(body_points[1:])
            if tail:
                blocks.append(f"<p><strong>{escape(lead)}</strong> {escape(tail)}</p>")
            else:
                blocks.append(f"<p>{escape(lead)}</p>")
    return "\n".join(blocks) + "\n"


def render_minimal_clean(product: dict, plan: dict) -> str:
    blocks: list[str] = []
    hero = plan["sections"][0]
    hero_url = image_for_slot(product, hero.get("image_slot"))
    if hero_url:
        blocks.append(render_img(hero_url, hero.get("title", product.get("product_title", "Product hero"))))
    blocks.append(f"<h2>{escape(hero.get('title', product.get('product_title', 'Product')))}</h2>")
    blocks.append(
        f"<p><strong>{escape(product['product_type'])}</strong> with {escape(product['core_features'][0])}, "
        f"{escape(product['core_features'][2])}, and {escape(product['core_features'][3])}.</p>"
    )
    blocks.append("<h2>Key reasons to choose it</h2>")
    blocks.append(render_list(product.get("core_features", [])[:4]))
    blocks.append("<h2>What you receive</h2>")
    blocks.append(render_list(product.get("package_contents", [])))
    blocks.append("<h2>Quick care reminders</h2>")
    blocks.append(render_list(product.get("risk_notes", [])))
    return "\n".join(blocks) + "\n"


def render_spec_first(product: dict, plan: dict) -> str:
    blocks: list[str] = []
    hero = plan["sections"][0]
    hero_url = image_for_slot(product, hero.get("image_slot"))
    if hero_url:
        blocks.append(render_img(hero_url, hero.get("title", product.get("product_title", "Product hero"))))
    blocks.append("<h2>Technical details at a glance</h2>")
    blocks.append("<table>")
    for row in product.get("specs", []):
        blocks.append(
            "  <tr>"
            f"<td><strong>{escape(row['label'])}</strong></td>"
            f"<td>{escape(row['value'])}</td>"
            "</tr>"
        )
    blocks.append("</table>")
    blocks.append("<h2>Compatibility and use</h2>")
    blocks.append(render_list(product.get("compatibility", [])))
    blocks.append("<h2>What you receive</h2>")
    blocks.append(render_list(product.get("package_contents", [])))
    return "\n".join(blocks) + "\n"


def render_family(family: str, product: dict, plan: dict) -> str:
    if family == "dense_feature":
        return render_dense_feature(product, plan)
    if family == "minimal_clean":
        return render_minimal_clean(product, plan)
    if family == "spec_first":
        return render_spec_first(product, plan)
    raise ValueError(f"Unsupported template family: {family}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", type=pathlib.Path, required=True)
    parser.add_argument("--plan", type=pathlib.Path, required=True)
    parser.add_argument("--family", choices=["minimal_clean", "dense_feature", "spec_first"], default="dense_feature")
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args()

    product = load_json(args.product)
    plan = load_json(args.plan)
    html = render_family(args.family, product, plan)
    args.out.write_text(html)
    print(json.dumps({"status": "ok", "family": args.family, "out": str(args.out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
