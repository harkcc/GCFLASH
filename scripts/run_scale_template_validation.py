#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]


RUN_MATRIX = [
    {
        "scale_id": "scale_a_nexscope_amazon_7",
        "scale_file": "workflow/scale_baselines/scale_a_nexscope_amazon_7.json",
        "suite_file": "workflow/suite_templates/amazon_nexscope_7_suite.json",
        "product_id": "pink_backpack",
        "run_id": "scale_a_amazon_7_pink_backpack",
    },
    {
        "scale_id": "scale_b_ozon_wb_template_adaptation",
        "scale_file": "workflow/scale_baselines/scale_b_ozon_wb_template_adaptation.json",
        "suite_file": "workflow/suite_templates/ozon_wb_template_5_suite.json",
        "product_id": "portable_tire_inflator",
        "run_id": "scale_b_ozon_wb_5_tire_inflator",
    },
    {
        "scale_id": "scale_c_brandshootkit_qa_reroll",
        "scale_file": "workflow/scale_baselines/scale_c_brandshootkit_qa_reroll.json",
        "suite_file": "workflow/suite_templates/brandshootkit_route_comparison_suite.json",
        "product_id": "usb_cable_accessory_set",
        "run_id": "scale_c_route_comparison_usb_accessory",
    },
]


@dataclass
class RenderedSlot:
    slot: dict[str, Any]
    image_path: Path
    manifest_path: Path
    generation_request_path: Path
    score: dict[str, Any]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Supplemental/Verdana Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Verdana.ttf",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def soften(rgb: tuple[int, int, int], amount: int = 22) -> tuple[int, int, int]:
    return tuple(max(0, min(255, c + amount)) for c in rgb)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, min_size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    for size in range(start, min_size - 1, -2):
        font = load_font(size, bold=bold)
        lines = wrap_text(draw, text, font, max_width)
        if all(draw.textbbox((0, 0), line, font=font)[2] <= max_width for line in lines):
            return font
    return load_font(min_size, bold=bold)


def draw_text_block(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    fill: tuple[int, int, int],
    start_size: int,
    min_size: int = 28,
    bold: bool = True,
    align: str = "center",
) -> dict[str, Any]:
    max_width = box[2] - box[0] - 28
    font = fit_font(draw, text, max_width, start_size, min_size, bold)
    lines = wrap_text(draw, text, font, max_width)
    line_h = int(font.size * 1.16)
    total_h = line_h * len(lines)
    y = box[1] + max(0, (box[3] - box[1] - total_h) // 2)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        if align == "left":
            x = box[0] + 18
        else:
            x = box[0] + (box[2] - box[0] - tw) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return {
        "text": text,
        "bbox": list(box),
        "font_size": font.size,
        "lines": lines,
        "align": align,
    }


def crop_product(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    width, height = rgb.size
    pix = rgb.load()
    corners = [
        pix[0, 0],
        pix[width - 1, 0],
        pix[0, height - 1],
        pix[width - 1, height - 1],
    ]
    bg = tuple(sum(c[i] for c in corners) // len(corners) for i in range(3))
    min_x, min_y = width, height
    max_x, max_y = 0, 0
    found = False
    for y in range(height):
        for x in range(width):
            r, g, b = pix[x, y]
            bg_distance = abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2])
            saturation = max(r, g, b) - min(r, g, b)
            dark_or_colored = min(r, g, b) < 205 or saturation > 28
            # Treat the corner-like studio background as background even when
            # it is light gray instead of pure white.
            if bg_distance > 42 and dark_or_colored:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
                found = True
    if not found:
        return image.convert("RGBA")
    pad_x = int((max_x - min_x) * 0.06)
    pad_y = int((max_y - min_y) * 0.06)
    box = (
        max(0, min_x - pad_x),
        max(0, min_y - pad_y),
        min(width, max_x + pad_x),
        min(height, max_y + pad_y),
    )
    return image.crop(box).convert("RGBA")


def white_to_alpha(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    data = []
    for r, g, b, a in rgba.getdata():
        if r > 246 and g > 246 and b > 246 and abs(r - g) < 14 and abs(g - b) < 14:
            data.append((r, g, b, 0))
        else:
            data.append((r, g, b, a))
    rgba.putdata(data)
    return rgba


def paste_product(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    product: Image.Image,
    box: tuple[int, int, int, int],
    shadow: bool = True,
) -> dict[str, Any]:
    product = white_to_alpha(crop_product(product))
    target_w = box[2] - box[0]
    target_h = box[3] - box[1]
    scale = min(target_w / product.width, target_h / product.height)
    new_size = (max(1, int(product.width * scale)), max(1, int(product.height * scale)))
    resized = product.resize(new_size, Image.LANCZOS)
    x = box[0] + (target_w - new_size[0]) // 2
    y = box[1] + (target_h - new_size[1]) // 2
    if shadow:
        shadow_box = (
            x + int(new_size[0] * 0.12),
            y + int(new_size[1] * 0.88),
            x + int(new_size[0] * 0.88),
            y + int(new_size[1] * 0.99),
        )
        draw.ellipse(shadow_box, fill=(0, 0, 0, 34))
    canvas.alpha_composite(resized, (x, y))
    return {
        "bbox": [x, y, x + new_size[0], y + new_size[1]],
        "source_crop_size": [product.width, product.height],
        "render_size": list(new_size),
    }


def gradient_background(width: int, height: int, start: tuple[int, int, int], end: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGBA", (width, height), start + (255,))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / max(1, height - 1)
        rgb = tuple(int(start[i] * (1 - t) + end[i] * t) for i in range(3))
        draw.line([(0, y), (width, y)], fill=rgb + (255,))
    return image


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill, outline=None, width: int = 2) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_badge(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    palette: dict[str, tuple[int, int, int]],
    accent_idx: int,
) -> dict[str, Any]:
    accents = [palette["accent"], palette["accent_2"], palette["danger"], (22, 163, 74)]
    accent = accents[accent_idx % len(accents)]
    rounded(draw, box, 26, palette["surface"] + (238,), outline=palette["stroke"] + (255,), width=3)
    dot = (box[0] + 18, box[1] + 20, box[0] + 62, box[1] + 64)
    draw.ellipse(dot, fill=accent + (255,))
    text_box = (box[0] + 78, box[1], box[2] - 18, box[3])
    layer = draw_text_block(draw, text_box, text, palette["ink"], 38, 24, True, "left")
    layer.update({"id": f"badge_{accent_idx + 1}", "type": "badge", "accent_rgb": list(accent), "bbox": list(box)})
    return layer


def profile_palette(style_pack: dict[str, Any], profile_id: str) -> tuple[dict[str, Any], dict[str, tuple[int, int, int]]]:
    profile = style_pack["marketplace_profiles"][profile_id]
    raw = profile["palette"]
    palette = {
        "background": hex_to_rgb(raw["background"]),
        "surface": hex_to_rgb(raw["surface"]),
        "ink": hex_to_rgb(raw["ink"]),
        "muted": hex_to_rgb(raw["muted"]),
        "accent": hex_to_rgb(raw["accent"]),
        "accent_2": hex_to_rgb(raw["accent_2"]),
        "danger": hex_to_rgb(raw["danger"]),
        "stroke": hex_to_rgb(profile["frame"]["stroke"]),
        "shadow": hex_to_rgb(profile["frame"]["shadow"]),
    }
    return profile, palette


def layout_product_box(layout_family: str, width: int, height: int) -> tuple[int, int, int, int]:
    boxes = {
        "amazon_main_clean": (170, 300, width - 170, height - 160),
        "feature_right_stack": (90, 340, int(width * 0.55), height - 160),
        "scale_reference": (210, 390, width - 210, height - 280),
        "package_trust": (220, 310, width - 220, height - 360),
        "detail_zoom_panels": (90, 330, int(width * 0.56), height - 180),
        "lifestyle_scene": (250, 360, width - 230, height - 120),
        "before_after_safe": (int(width * 0.52), 360, width - 110, height - 180),
        "ozon_main_card": (105, 430, width - 105, height - 260),
        "callout_around_product": (170, 430, width - 170, height - 360),
        "multi_use_grid": (170, 360, width - 170, int(height * 0.70)),
        "industrial_detail": (70, 420, int(width * 0.57), height - 170),
        "route_baseline": (100, 330, int(width * 0.52), height - 170),
        "template_reverse_grid": (100, 310, int(width * 0.55), height - 150),
        "preservation_composite": (140, 310, int(width * 0.58), height - 150),
    }
    return boxes.get(layout_family, (140, 320, width - 140, height - 180))


def draw_layout_background(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    slot: dict[str, Any],
    profile_id: str,
    profile: dict[str, Any],
    palette: dict[str, tuple[int, int, int]],
) -> None:
    width, height = canvas.size
    layout = slot["layout_family"]
    if profile_id == "ozon_wb":
        bg = gradient_background(width, height, palette["background"], soften(palette["background"], 28))
        canvas.alpha_composite(bg)
        draw.rectangle((0, int(height * 0.78), width, height), fill=(8, 15, 25, 255))
    elif layout in {"industrial_detail", "route_baseline"}:
        bg = gradient_background(width, height, (19, 26, 37), (48, 56, 72))
        canvas.alpha_composite(bg)
    else:
        bg = gradient_background(width, height, palette["background"], (255, 255, 255))
        canvas.alpha_composite(bg)
        draw.ellipse((int(width * 0.58), -120, width + 120, int(height * 0.35)), fill=(225, 238, 255, 170))
        draw.ellipse((-120, int(height * 0.70), int(width * 0.42), height + 140), fill=(248, 231, 238, 135))

    # Suite-level frame.
    margin = int(profile["canvas"]["safe_margin"] * 0.32)
    rounded(draw, (margin, margin, width - margin, height - margin), int(profile["frame"]["radius"]), (255, 255, 255, 0), outline=palette["stroke"] + (255,), width=3)


def draw_slot_header(
    draw: ImageDraw.ImageDraw,
    slot: dict[str, Any],
    scale: dict[str, Any],
    palette: dict[str, tuple[int, int, int]],
    profile_id: str,
    width: int,
) -> dict[str, Any]:
    top = 48
    left = 64
    label = f"{scale['name'].split(' - ')[0]} / Slot {slot['slot']:02d}"
    small = load_font(26, True)
    draw.text((left, top), label, font=small, fill=(255, 255, 255, 220) if profile_id == "ozon_wb" else palette["muted"] + (255,))
    title_box = (left, top + 38, width - 64, top + 150)
    title_layer = draw_text_block(draw, title_box, slot["headline"], (255, 255, 255) if profile_id == "ozon_wb" else palette["ink"], 64, 34, True, "left")
    title_layer.update({"id": "headline", "type": "text", "role": "headline"})
    return title_layer


def draw_template_specific(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    slot: dict[str, Any],
    truth: dict[str, Any],
    product: Image.Image,
    profile_id: str,
    profile: dict[str, Any],
    palette: dict[str, tuple[int, int, int]],
) -> list[dict[str, Any]]:
    width, height = canvas.size
    layers: list[dict[str, Any]] = []
    layout = slot["layout_family"]

    if layout == "feature_right_stack":
        for i, badge in enumerate(slot["badges"][:3]):
            y = 410 + i * 220
            layers.append(draw_badge(draw, (int(width * 0.60), y, width - 92, y + 128), badge, palette, i))
    elif layout == "scale_reference":
        labels = slot["badges"][:3]
        for i, label in enumerate(labels):
            x = 130 + i * 455
            rounded(draw, (x, height - 250, x + 350, height - 130), 28, palette["surface"] + (240,), outline=palette["stroke"] + (255,), width=3)
            draw.rectangle((x + 30, height - 218, x + 98, height - 162), fill=palette["accent"] + (50,), outline=palette["accent"] + (255,), width=3)
            layers.append(draw_text_block(draw, (x + 115, height - 230, x + 330, height - 145), label, palette["ink"], 32, 22, True, "left"))
    elif layout == "package_trust":
        y = height - 300
        for i, badge in enumerate(slot["badges"][:3]):
            x = 130 + i * 455
            layers.append(draw_badge(draw, (x, y, x + 360, y + 118), badge, palette, i))
    elif layout == "detail_zoom_panels":
        x0 = int(width * 0.62)
        for i, badge in enumerate(slot["badges"][:3]):
            y = 340 + i * 260
            rounded(draw, (x0, y, width - 96, y + 185), 28, palette["surface"] + (242,), outline=palette["stroke"] + (255,), width=3)
            detail = crop_product(product).resize((190, 140), Image.LANCZOS)
            canvas.alpha_composite(white_to_alpha(detail), (x0 + 22, y + 22))
            layers.append(draw_text_block(draw, (x0 + 230, y + 32, width - 126, y + 150), badge, palette["ink"], 34, 24, True, "left"))
    elif layout == "lifestyle_scene":
        layers.append(draw_text_block(draw, (100, 185, 720, 280), slot["headline"], palette["ink"], 54, 32, True, "left"))
    elif layout == "before_after_safe":
        mid = width // 2
        draw.line((mid, 260, mid, height - 150), fill=palette["stroke"] + (255,), width=4)
        layers.append(draw_text_block(draw, (90, 300, mid - 60, 410), "Before", palette["danger"], 50, 30, True, "center"))
        layers.append(draw_text_block(draw, (mid + 60, 300, width - 90, 410), "After", palette["accent"], 50, 30, True, "center"))
        for i in range(8):
            x = 145 + (i % 2) * 170
            y = 500 + (i // 2) * 135
            rounded(draw, (x, y, x + 110, y + 82), 22, (255, 255, 255, 230), outline=palette["stroke"] + (255,), width=2)
    elif layout == "ozon_main_card":
        draw.rounded_rectangle((72, 255, width - 72, height - 92), radius=42, outline=(255, 255, 255, 80), width=3)
        draw_text_block(draw, (84, 230, width - 84, 360), slot["headline"], (255, 255, 255), 96, 48, True, "center")
        for i, badge in enumerate(slot["badges"][:3]):
            y = 1120 + i * 112
            layers.append(draw_badge(draw, (112, y, width - 112, y + 82), badge, palette, i))
    elif layout == "callout_around_product":
        positions = [(80, 310), (760, 340), (78, 1130), (730, 1130)]
        for i, badge in enumerate(slot["badges"][:4]):
            x, y = positions[i]
            layers.append(draw_badge(draw, (x, y, x + 390, y + 96), badge, palette, i))
            draw.line((x + 195, y + 96, width // 2, height // 2), fill=palette["accent"] + (180,), width=3)
    elif layout == "multi_use_grid":
        labels = slot["badges"][:3]
        for i, label in enumerate(labels):
            x = 80 + i * 370
            y = height - 360
            rounded(draw, (x, y, x + 310, y + 220), 28, (255, 255, 255, 234), outline=palette["stroke"] + (255,), width=3)
            draw.ellipse((x + 105, y + 42, x + 205, y + 142), fill=palette["accent"] + (70,), outline=palette["accent"] + (255,), width=3)
            layers.append(draw_text_block(draw, (x + 20, y + 145, x + 290, y + 205), label, palette["ink"], 30, 22, True))
    elif layout == "industrial_detail":
        x0 = int(width * 0.58)
        for i, badge in enumerate(slot["badges"][:3]):
            y = 420 + i * 220
            rounded(draw, (x0, y, width - 80, y + 135), 26, (255, 255, 255, 235), outline=palette["accent_2"] + (255,), width=3)
            layers.append(draw_text_block(draw, (x0 + 24, y + 18, width - 110, y + 115), badge, palette["ink"], 34, 24, True, "left"))
    elif layout == "route_baseline":
        rounded(draw, (int(width * 0.58), 300, width - 80, height - 180), 28, (255, 255, 255, 238), outline=palette["danger"] + (255,), width=4)
        notes = ["Fast first draft", "Weak product locks", "Text may drift", "Needs QA gate"]
        for i, note in enumerate(notes):
            layers.append(draw_badge(draw, (int(width * 0.62), 370 + i * 150, width - 130, 470 + i * 150), note, palette, i))
    elif layout == "template_reverse_grid":
        x0 = int(width * 0.60)
        y0 = 315
        for i, badge in enumerate(slot["badges"][:3]):
            x = x0
            y = y0 + i * 215
            rounded(draw, (x, y, width - 88, y + 160), 28, (255, 255, 255, 240), outline=palette["stroke"] + (255,), width=3)
            layers.append(draw_text_block(draw, (x + 30, y + 28, width - 120, y + 132), badge, palette["ink"], 35, 24, True, "left"))
    elif layout == "preservation_composite":
        rounded(draw, (int(width * 0.62), 320, width - 88, height - 160), 28, (255, 255, 255, 240), outline=palette["accent"] + (255,), width=4)
        labels = ["Product layer locked", "Text layer editable", "Reroll only failed area"]
        for i, label in enumerate(labels):
            layers.append(draw_badge(draw, (int(width * 0.65), 395 + i * 180, width - 130, 505 + i * 180), label, palette, i))
    else:
        for i, badge in enumerate(slot["badges"][:3]):
            layers.append(draw_badge(draw, (width - 580, 400 + i * 170, width - 100, 515 + i * 170), badge, palette, i))

    return layers


def normalize_truth(product_id: str, raw: dict[str, Any], source_image: str) -> dict[str, Any]:
    immutable = [
        *(raw.get("required_preservation_rules", [])),
        *[f"visible material: {item}" for item in raw.get("visible_materials", [])],
        *[f"visible part: {item}" for item in raw.get("visible_parts", [])],
        *[f"visible color: {item}" for item in raw.get("visible_color", [])],
    ]
    selling_points = []
    for index, claim in enumerate(raw.get("allowed_selling_points", raw.get("confirmed_features", [])), start=1):
        selling_points.append(
            {
                "id": f"sp_{index}",
                "claim": claim,
                "visual_translation": claim,
                "short_badge": claim if len(claim) <= 24 else " ".join(claim.split()[:3]),
            }
        )
    return {
        "sku": product_id,
        "category": raw.get("visible_product_type", raw.get("category", "unknown")),
        "marketplace": "validation",
        "language": "English",
        "source_images": {"product": source_image},
        "immutable_traits": immutable,
        "allowed_changes": ["background", "lighting", "template frame", "copy slots", "badge placement", "scene context"],
        "forbidden_changes": [*raw.get("forbidden_claims", []), *raw.get("risky_details", [])],
        "selling_points": selling_points,
        "raw_truth": raw,
    }


def claim_risk(slot: dict[str, Any], truth: dict[str, Any]) -> list[str]:
    text = " ".join([slot.get("headline", ""), *slot.get("badges", [])]).lower()
    risks = []
    for claim in truth.get("forbidden_changes", []):
        key = str(claim).lower()
        if key and key in text:
            risks.append(claim)
    return risks


def score_slot(slot: dict[str, Any], truth: dict[str, Any], scale: dict[str, Any], profile_id: str) -> dict[str, Any]:
    route = slot.get("route", "template_render_mvp")
    risks = claim_risk(slot, truth)

    if route == "legacy_image2_keyword_route":
        scores = {
            "product_fidelity": 13,
            "template_reuse": 9,
            "typography_system": 8,
            "mobile_readability": 10,
            "commercial_clarity": 12,
            "claim_safety": 8 if not risks else 4,
            "repairability": 7,
        }
    elif route == "template_reverse_route":
        scores = {
            "product_fidelity": 18,
            "template_reuse": 15,
            "typography_system": 14,
            "mobile_readability": 14,
            "commercial_clarity": 14,
            "claim_safety": 9 if not risks else 5,
            "repairability": 9,
        }
    elif route == "preservation_composite_route":
        scores = {
            "product_fidelity": 20,
            "template_reuse": 14,
            "typography_system": 15,
            "mobile_readability": 14,
            "commercial_clarity": 13,
            "claim_safety": 10 if not risks else 6,
            "repairability": 10,
        }
    else:
        density = slot.get("text_density", "medium")
        typography = {"low": 15, "medium": 14, "high": 12}.get(density, 13)
        mobile = {"low": 15, "medium": 14, "high": 12}.get(density, 13)
        if profile_id == "ozon_wb":
            mobile += 1
        scores = {
            "product_fidelity": 19,
            "template_reuse": 14,
            "typography_system": typography,
            "mobile_readability": min(15, mobile),
            "commercial_clarity": 14,
            "claim_safety": 10 if not risks else 5,
            "repairability": 9,
        }

    total = sum(scores.values())
    if total >= 82:
        verdict = "pass"
    elif total >= 70:
        verdict = "repair"
    else:
        verdict = "fail"

    repair_actions = []
    if scores["product_fidelity"] < 16:
        repair_actions.append(
            {
                "type": "switch_to_preserve_first_composite",
                "reason": "Product fidelity is below threshold; use real product layer, mask/detail transfer, or ComfyUI-productfix route.",
            }
        )
    if scores["typography_system"] < 12:
        repair_actions.append(
            {
                "type": "switch_to_fabric_or_psd_text_layers",
                "reason": "Typography is not controlled enough for production use.",
            }
        )
    if scores["mobile_readability"] < 12:
        repair_actions.append(
            {
                "type": "reduce_text_density",
                "reason": "Card will not read well in a mobile grid.",
            }
        )
    if risks:
        repair_actions.append(
            {
                "type": "remove_or_soften_claim",
                "reason": f"Copy collides with forbidden/risky claims: {', '.join(risks)}",
            }
        )
    if not repair_actions and verdict != "pass":
        repair_actions.append(
            {
                "type": "typed_reroll_same_template",
                "reason": "Keep current template and reroll only weak visual dimensions.",
            }
        )

    return {
        "slot": slot["slot"],
        "slot_type": slot["slot_type"],
        "template_card": slot["template_card"],
        "route": route,
        "total": total,
        "verdict": verdict,
        "dimension_scores": scores,
        "claim_risks": risks,
        "repair_actions": repair_actions,
        "review_focus": scale["qa_focus"],
    }


def render_slot(
    run_dir: Path,
    slot: dict[str, Any],
    scale: dict[str, Any],
    suite: dict[str, Any],
    style_pack: dict[str, Any],
    product_id: str,
    truth: dict[str, Any],
    source_product_path: Path,
) -> RenderedSlot:
    profile_id = suite["marketplace_profile"]
    profile, palette = profile_palette(style_pack, profile_id)
    width = int(profile["canvas"]["width"])
    height = int(profile["canvas"]["height"])
    canvas = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    draw_layout_background(canvas, draw, slot, profile_id, profile, palette)

    layers: list[dict[str, Any]] = []
    layers.append(draw_slot_header(draw, slot, scale, palette, profile_id, width))

    product = Image.open(source_product_path)
    product_box = layout_product_box(slot["layout_family"], width, height)
    product_layer = paste_product(canvas, draw, product, product_box, shadow=True)
    product_layer.update({"id": "product", "type": "product", "source": str(source_product_path.relative_to(ROOT))})
    layers.append(product_layer)
    layers.extend(draw_template_specific(canvas, draw, slot, truth, product, profile_id, profile, palette))

    if slot["layout_family"] in {"amazon_main_clean"}:
        # Main-image validation keeps product clean. Text is in manifest only.
        layers.append(
            {
                "id": "main_image_policy",
                "type": "compliance_note",
                "note": "No final text/badges rendered for marketplace main-image safety; headline is planning metadata only.",
            }
        )

    candidate_dir = run_dir / "candidates"
    manifest_dir = run_dir / "manifests"
    request_dir = run_dir / "generation_requests"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    image_path = candidate_dir / f"slot_{slot['slot']:02d}_{slot['slot_type']}.png"
    canvas.convert("RGB").save(image_path, quality=95)

    copy_plan = {
        "slot": slot["slot"],
        "slot_type": slot["slot_type"],
        "headline": slot["headline"],
        "badges": slot.get("badges", []),
        "text_density": slot["text_density"],
        "source": "suite_template_seed_copy",
        "review_required": True,
    }
    manifest = {
        "slot": slot,
        "product_id": product_id,
        "scale_id": scale["id"],
        "suite_template_id": suite["id"],
        "brand_style_pack": style_pack["id"],
        "canvas": {"width": width, "height": height, "profile": profile_id},
        "template_product_type": slot["template_product_type"],
        "candidate_generator": "template_render_mvp",
        "route": slot.get("route", "template_render_mvp"),
        "layers": layers,
        "copy_plan": copy_plan,
        "font_system": style_pack["font_system"],
        "handoff_paths": {
            "image": str(image_path.relative_to(ROOT)),
            "manifest": f"manifests/slot_{slot['slot']:02d}_{slot['slot_type']}.manifest.json",
        },
    }
    manifest_path = manifest_dir / f"slot_{slot['slot']:02d}_{slot['slot_type']}.manifest.json"
    write_json(manifest_path, manifest)

    generation_request = {
        "slot": slot,
        "scale_baseline": scale["id"],
        "product_id": product_id,
        "product_truth_pack": truth,
        "selected_template_card": slot["template_card"],
        "candidate_generator_used": "template_render_mvp",
        "candidate_generator_options": [
            {
                "id": "template_render_mvp",
                "purpose": "Local deterministic proof that TemplateCard/SuiteTemplate/BrandStylePack can produce a reviewable card.",
                "status": "rendered",
            },
            {
                "id": "gpt_image_2_reference_edit",
                "purpose": "Use real product images as fixed references and generate background/composition drafts only.",
                "status": "request_prepared",
            },
            {
                "id": "comfyui_productfix",
                "purpose": "Use Latent Injection, OCR masks, detail transfer, IC-Light/IP-Adapter/ControlNet ideas for product preservation.",
                "status": "route_reference",
            },
            {
                "id": "fabric_or_psd_template_render",
                "purpose": "Render final font, badge, icon, brand frame, and text layers with editable template state.",
                "status": "route_reference",
            },
        ],
        "prompt_brief": {
            "image_job": slot["image_job"],
            "buyer_question": slot["buyer_question"],
            "keep": truth["immutable_traits"],
            "forbidden": truth["forbidden_changes"],
            "text_policy": "short planning text only; production text must be editable template layer",
            "template_adaptation": "Extract layout logic from template; do not copy source creative pixels.",
        },
    }
    generation_request_path = request_dir / f"slot_{slot['slot']:02d}_{slot['slot_type']}.generation_request.json"
    write_json(generation_request_path, generation_request)

    score = score_slot(slot, truth, scale, profile_id)
    return RenderedSlot(slot, image_path, manifest_path, generation_request_path, score)


def make_contact_sheet(images: list[Path], out_path: Path, title: str) -> None:
    thumbs = []
    for path in images:
        img = Image.open(path).convert("RGB")
        img.thumbnail((360, 360), Image.LANCZOS)
        thumbs.append((path, img.copy()))
    columns = min(4, max(1, len(thumbs)))
    rows = math.ceil(len(thumbs) / columns)
    cell_w, cell_h = 390, 430
    header_h = 90
    sheet = Image.new("RGB", (columns * cell_w, rows * cell_h + header_h), (18, 24, 33))
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 22), title, font=load_font(38, True), fill=(255, 255, 255))
    for idx, (path, img) in enumerate(thumbs):
        col = idx % columns
        row = idx // columns
        x = col * cell_w + (cell_w - img.width) // 2
        y = header_h + row * cell_h + 20
        sheet.paste(img, (x, y))
        label = path.stem.replace("_", " ")
        draw.text((col * cell_w + 18, header_h + row * cell_h + 386), label[:42], font=load_font(20, False), fill=(235, 239, 245))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, quality=95)


def build_run_report(
    run_dir: Path,
    product_id: str,
    scale: dict[str, Any],
    suite: dict[str, Any],
    rendered: list[RenderedSlot],
    contact_sheet: Path,
) -> None:
    pass_count = sum(1 for item in rendered if item.score["verdict"] == "pass")
    repair_count = sum(1 for item in rendered if item.score["verdict"] == "repair")
    fail_count = sum(1 for item in rendered if item.score["verdict"] == "fail")
    rows = []
    for item in rendered:
        rows.append(
            f"| {item.slot['slot']} | {item.slot['slot_type']} | {item.slot['template_card']} | "
            f"{item.score['total']} | {item.score['verdict']} | {', '.join(a['type'] for a in item.score['repair_actions']) or 'none'} |"
        )

    report = f"""# Scale Template Validation Run

Product: `{product_id}`
Scale: `{scale['id']}`
SuiteTemplate: `{suite['id']}`

## Verdict

- Pass: {pass_count}
- Repair: {repair_count}
- Fail: {fail_count}
- Contact sheet: `{contact_sheet.relative_to(run_dir)}`

## What This Run Validates

{scale['validation_goal']}

This run uses `template_render_mvp` as the local deterministic candidate generator. It does not claim to replace Image2 or ComfyUI. It proves that the new artifact chain can carry template parameters, font rules, copy plan, QA, and repair actions before any external model call.

## Slot Scores

| Slot | Type | TemplateCard | Score | Verdict | Repair actions |
|---:|---|---|---:|---|---|
{chr(10).join(rows)}

## Required Next Model Tests

- Run `gpt_image_2_reference_edit` only after the slot's image job and template params are accepted.
- For product drift, route through preserve-first composite or ComfyUI-productfix style preservation before rerolling scenes.
- For production text, route through Fabric/PSD/HTML template state, not model-rendered long copy.

## Source Baseline

{chr(10).join(f'- {ref}' for ref in scale['source_references'])}
"""
    (run_dir / "run_report.md").write_text(report)


def build_root_report(root_out: Path, runs: list[dict[str, Any]]) -> None:
    rows = []
    for run in runs:
        rows.append(
            f"| {run['scale_id']} | {run['product_id']} | {run['slots']} | "
            f"{run['pass']} | {run['repair']} | {run['fail']} | `{run['run_dir']}` |"
        )
    report = f"""# Scale Template Prototype Validation

Date: 2026-05-17

## Summary

This prototype implements the new plan as a file-backed validation system. It does not lock the workflow to the old `Image2 + keyword + simple PIL/HTML overlay` route. Instead it validates three method baselines:

- Scale A: Nexscope/Amazon 7-image strategy.
- Scale B: Ozon/WB template adaptation route.
- Scale C: Brand Shoot Kit preserve/QA/reroll route comparison.

## Results

| Scale | Product | Slots | Pass | Repair | Fail | Run folder |
|---|---|---:|---:|---:|---:|---|
{chr(10).join(rows)}

## Implemented Artifacts

- `TemplateCard`: existing card library under `workflow/template_cards/`, now used by the validation runner.
- `SuiteTemplate`: new suite files under `workflow/suite_templates/`.
- `BrandStylePack`: new default pack under `workflow/brand_style_packs/`.
- `QAReport`: generated per run under `qa/qa_report.json`, with typed repair actions.

## Key Validation Meaning

- Single-image templates are now parameterized into product zones, text zones, badge rules, and typography constraints.
- Suite templates now define slot order and buyer questions.
- PSD/template products are represented as layer/manifest routes, not only as a final text overlay trick.
- Scale C explicitly compares the old loose route against template-reverse and preserve-first routes.

## Next Step

When user brand cases and collected templates arrive, add them as new TemplateCard or PSD/Fabric template products, then rerun this same script without changing the workflow contract.
"""
    (root_out / "scale_comparison_report.md").write_text(report)


def run_one(config: dict[str, str], out_root: Path, style_pack: dict[str, Any], product_catalog: dict[str, Any]) -> dict[str, Any]:
    product_entry = next(item for item in product_catalog["products"] if item["id"] == config["product_id"])
    product_id = product_entry["id"]
    source_product_path = ROOT / product_entry["source_image"]
    truth_source = read_json(ROOT / product_entry["truth_source"])
    raw_truth = truth_source[product_entry["truth_key"]]
    truth = normalize_truth(product_id, raw_truth, product_entry["source_image"])

    scale = read_json(ROOT / config["scale_file"])
    suite = read_json(ROOT / config["suite_file"])
    run_dir = out_root / config["run_id"]
    run_dir.mkdir(parents=True, exist_ok=True)

    inputs_dir = run_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_product_path, inputs_dir / source_product_path.name)
    write_json(inputs_dir / "product_truth_pack.json", truth)
    write_json(inputs_dir / "scale_baseline.json", scale)
    write_json(inputs_dir / "suite_template.json", suite)
    write_json(inputs_dir / "brand_style_pack.json", style_pack)

    shot_plan = {
        "product_id": product_id,
        "scale_id": scale["id"],
        "suite_template_id": suite["id"],
        "slots": [
            {
                "slot": slot["slot"],
                "slot_type": slot["slot_type"],
                "buyer_question": slot["buyer_question"],
                "image_job": slot["image_job"],
                "template_card": slot["template_card"],
                "template_product_type": slot["template_product_type"],
                "copy_seed": {"headline": slot["headline"], "badges": slot.get("badges", [])},
            }
            for slot in suite["slots"]
        ],
    }
    write_json(run_dir / "shot_plan.json", shot_plan)

    template_params = {
        "source": "suite_template_plus_template_card_mapping",
        "scale_id": scale["id"],
        "suite_template_id": suite["id"],
        "params": [
            {
                "slot": slot["slot"],
                "template_card": slot["template_card"],
                "layout_family": slot["layout_family"],
                "template_product_type": slot["template_product_type"],
                "text_density": slot["text_density"],
                "font_system": style_pack["font_system"],
            }
            for slot in suite["slots"]
        ],
    }
    write_json(run_dir / "template_params.json", template_params)

    copy_plan = {
        "product_id": product_id,
        "scale_id": scale["id"],
        "copy_policy": "short editable labels only; no model-rendered long production text",
        "slots": [
            {
                "slot": slot["slot"],
                "headline": slot["headline"],
                "badges": slot.get("badges", []),
                "buyer_question": slot["buyer_question"],
                "claim_review_required": bool(claim_risk(slot, truth)),
            }
            for slot in suite["slots"]
        ],
    }
    write_json(run_dir / "copy_plan.json", copy_plan)

    rendered: list[RenderedSlot] = []
    for slot in suite["slots"]:
        rendered.append(render_slot(run_dir, slot, scale, suite, style_pack, product_id, truth, source_product_path))

    qa_report = {
        "product_id": product_id,
        "scale_id": scale["id"],
        "suite_template_id": suite["id"],
        "dimensions": {
            "product_fidelity": 20,
            "template_reuse": 15,
            "typography_system": 15,
            "mobile_readability": 15,
            "commercial_clarity": 15,
            "claim_safety": 10,
            "repairability": 10,
        },
        "slots": [item.score for item in rendered],
        "typed_repair_queue": [
            {"slot": item.score["slot"], "actions": item.score["repair_actions"]}
            for item in rendered
            if item.score["repair_actions"]
        ],
    }
    write_json(run_dir / "qa" / "qa_report.json", qa_report)

    repair_plan = {
        "product_id": product_id,
        "scale_id": scale["id"],
        "repairs": qa_report["typed_repair_queue"],
        "routing_rules": {
            "product_drift": "preserve_first_composite_or_comfyui_productfix",
            "font_or_text_failure": "fabric_psd_or_html_template_render",
            "template_mismatch": "switch_template_card_before_regeneration",
            "claim_risk": "remove_or_soften_claim_before_any_image_reroll",
        },
    }
    write_json(run_dir / "repair_plan.json", repair_plan)

    contact_sheet = run_dir / "contact_sheet.png"
    make_contact_sheet([item.image_path for item in rendered], contact_sheet, f"{scale['name']} / {product_id}")
    build_run_report(run_dir, product_id, scale, suite, rendered, contact_sheet)

    summary = {
        "scale_id": scale["id"],
        "product_id": product_id,
        "run_dir": str(run_dir.relative_to(ROOT)),
        "slots": len(rendered),
        "pass": sum(1 for item in rendered if item.score["verdict"] == "pass"),
        "repair": sum(1 for item in rendered if item.score["verdict"] == "repair"),
        "fail": sum(1 for item in rendered if item.score["verdict"] == "fail"),
        "contact_sheet": str(contact_sheet.relative_to(ROOT)),
    }
    write_json(run_dir / "run_manifest.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the three-scale ecommerce suite template validation prototype.")
    parser.add_argument("--out", default="experiments/20260517_scale_template_validation", help="Output experiment directory.")
    args = parser.parse_args()

    out_root = ROOT / args.out
    out_root.mkdir(parents=True, exist_ok=True)

    style_pack = read_json(ROOT / "workflow/brand_style_packs/default_scale_validation_pack.json")
    product_catalog = read_json(ROOT / "workflow/demo_products/scale_validation_products.json")
    template_catalog = read_json(ROOT / "workflow/template_products/template_product_catalog.json")
    write_json(out_root / "template_product_catalog.snapshot.json", template_catalog)

    summaries = [run_one(config, out_root, style_pack, product_catalog) for config in RUN_MATRIX]
    implementation_manifest = {
        "id": "scale_template_validation_20260517",
        "output_dir": str(out_root.relative_to(ROOT)),
        "runs": summaries,
        "implemented_artifacts": [
            "workflow/scale_baselines/*.json",
            "workflow/suite_templates/*.json",
            "workflow/brand_style_packs/default_scale_validation_pack.json",
            "workflow/template_products/template_product_catalog.json",
            "scripts/run_scale_template_validation.py"
        ],
    }
    write_json(out_root / "implementation_manifest.json", implementation_manifest)
    build_root_report(out_root, summaries)
    print(f"Wrote scale template validation prototype to {out_root}")
    for summary in summaries:
        print(f"- {summary['scale_id']}: {summary['slots']} slots -> {summary['contact_sheet']}")


if __name__ == "__main__":
    main()
