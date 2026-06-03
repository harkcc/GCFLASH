#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


REPO = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT_FILES = [
    REPO / "skills" / "ozon-image-generator" / "SKILL.md",
    REPO / "skills" / "ozon-image-generator" / "DESIGN.md",
    REPO / "skills" / "ozon-image-generator" / "README.md",
    REPO / "skills" / "ozon-image-generator" / "RUNTIME_CONTEXT.md",
]
DEFAULT_PROMPT_COMPILER = "fusion_v1"

PLANNER_SYSTEM = """You are the planning model for an e-commerce main-image generation agent.

Match the original stable Antigravity generate_image behavior: produce one
short, direct, image-to-image prompt that asks the image model to render the
entire e-commerce main card in one pass. Do not create a production layering
plan, background-only prompt, deterministic sticker plan, or long repair list.

Workflow:
1. Inspect the source image and product facts.
2. Route the product to a physically relevant scene, lighting plan, and color
   palette. The palette must come from the product category, material, usage
   environment, and visible product light source.
   Build the background as three quiet layers: the physical support surface, one
   low-detail category depth cue, and a functional light source. Do not collapse
   the background into a bare wall, table, texture, or gradient. For example:
   gaming gear can use a dark wall plus blurred monitor/shelf depth and cyan/RGB
   edge light; lab devices can use a bench plus PCB/tool bokeh and probe spark;
   car accessories can use the trunk surface plus folded seats and window light;
   STEM kits can use a study desk plus star/window/telescope depth and warm glow.
   Create the lighting plan as internal reasoning, not as a rigid style label:
   name the physical light source, the commercial job it does, the visible
   effect on the product/material/action, and the glow/beam/spark/rim-light risk
   to avoid. Translate the plan into natural image language in the final prompt,
   such as "warm sunlight streams through SUV side windows", "cyan sparks emit
   from the probe tips where they touch PCB pads", "the RGB dock casts a soft
   wash under the controllers", or "the central Sun sphere glows warmly and
   highlights the brass gears". Neon, rim glow, volumetric beams, and RGB washes
   require a physical reason.
3. Choose the hero pose inside the fixed Ozon main-card skeleton. The product
   still dominates the center area, but the pose is product-specific: front view,
   slight side angle, 3/4 angle, mounted state, expanded state, plugged-in state,
   or accessory-connected action. Prefer the pose that best explains function
   and physical logic, not the safest catalog front view.
   Active actions must name both a contact point and a visible result. Avoid
   vague phrasing like "toward the PCB" or "near the dock"; say that probe tips
   touch PCB pads and create a controlled spark, a dock emits RGB light under
   controllers, a pump nozzle connects to a valve, or a bracket visibly supports
   the mounted object.
4. Build a parameter story from verified product facts and the source image.
   Do this as product reasoning, not regex extraction or unit scoring. Decide
   what the buyer needs to notice in the first second:
   - One hero parameter only when a verified number/unit or compatibility claim
     is commercially decisive for this product. If no parameter is decisive,
     leave it empty and let the product/function carry the hook.
   - 0-4 secondary parameters for a side rail or stacked slabs when the product
     has multiple important specs.
   - 1-3 part callouts anchored to visible product parts, ports, lights, handles,
     batteries, blades, screens, nozzles, brackets, or accessories.
   - Bundle, warranty, compatibility, or trust claims must stay separate from
     functional parameters.
   - Design the visible parameter hierarchy like an Ozon scan poster, not a
     normal badge stack: the first-read value must become a large integrated
     value island or slab with the value text dominating the block; secondary
     facts become smaller slabs; only detail explanations become small callouts.
     Avoid generic header words on these blocks.
   - Parameter blocks must use the category palette from DESIGN.md. Do not use
     a black/white slab by default. Home/baby appliances should feel clean,
     soft, and trustworthy with light appliance base plus blue, teal, warm gold,
     or soft orange accents; tools and automotive can use harder black/orange or
     dark cyan blocks; gaming/electronics can use dark/cyan neon.
   - Parameter blocks should look like they grow out from the product area or
     sit beside the product edge. Do not pull long leader lines across the main
     product. Use adjacent tabs, short offset slabs, small connector dots, or
     compact callout chips close to the relevant part.
   - Do not repeat the same value or claim in multiple regions. Once a value is
     used as the hero island or a secondary slab, it must not appear again in the
     trust badge, bottom support block, or feature callout.
   Examples only, not hard-coded rules: a gaming console may highlight game
   count or memory, car lamps may highlight model/brightness/power/color
   temperature, a drill may highlight RPM/voltage/batteries/case, and a saw may
   highlight power/voltage/bar length/gift battery. For blenders, mixers,
   grinders, fans, drills, saws, and other rotating products, verified blade or
   motor speed/RPM is often a first-read hero value because it proves power and
   performance. The deciding factor is the product's buying logic and verified
   facts, not the unit text itself.
   For baby food processors and kitchen appliances, prioritize operating value:
   preset modes, power, speed settings, safety alarm, and self-cleaning usually
   matter more than voltage or dimensions. Capacity is important only when it is
   the clearest buyer hook; otherwise make it secondary.
5. Choose short overlay copy: title, one click-catch badge, 2-3 feature badges,
   one circular trust badge, and an EXCITAT brand shelf when the brand applies.
   The brand shelf structure is stable, but its border glow, badge colors, and
   lighting temperature are product-routed, not fixed. Cyan/charcoal is only
   appropriate for tech, gaming, electronics, or products whose own light source
   supports it. Warm amber/gold, orange, green, white/blue, or other accents can
   be used when they fit the product.
   Do not invent certification, material, medical, baby-safety, warranty, or
   compliance claims that are not present in the product facts or source image.
   For baby products, claims such as "BPA Free", "food grade", "CE", or
   "hospital safe" are forbidden unless explicitly supplied by the user.
6. Write the final image prompt in the original Antigravity style:
   - Start with "Extract the original [product] from the source image."
   - Add one product fidelity sentence.
   - Add one staging/background sentence that states the support surface,
     background depth cue, chosen hero pose, accessory interaction, and
     product-relevant key light, rim light, glow, reflection, or ambient lighting.
   - Add one overlay layout sentence with numbered layout components.
   - End with "Clean layout, professional advertising style."

Keep the final prompt compact, usually 120-180 words. Avoid terms that caused
drift in later local experiments: safe margin, repair priority, forbidden edits,
support area, production pipeline, matting, inpaint, denoise, alpha mask, layer,
overlay pass, deterministic sticker, PSD, HTML, Pillow, local composite.

Use one visible language/script across the whole prompt. If no language is
requested, use English Latin-script text like the original stable examples.
Do not reuse the PS5/gaming cyan look unless the new product actually belongs
to that visual logic.

Return only JSON."""

PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "image_name": {"type": "string"},
        "product_analysis": {
            "type": "object",
            "properties": {
                "category": {"type": "string"},
                "core_object": {"type": "string"},
                "immutable_features": {"type": "array", "items": {"type": "string"}},
                "accessories_or_parts": {"type": "array", "items": {"type": "string"}},
                "primary_value": {"type": "string"},
                "scene_logic": {"type": "string"},
                "background_support_surface": {"type": "string"},
                "background_depth_cues": {"type": "string"},
                "functional_lighting_source": {"type": "string"},
                "lighting_role": {"type": "string"},
                "physical_light_source": {"type": "string"},
                "lighting_effect_on_scene": {"type": "string"},
                "shadow_and_depth_behavior": {"type": "string"},
                "lighting_overuse_risk": {"type": "string"},
                "lighting_strategy": {"type": "string"},
                "lighting_constraints": {"type": "string"},
                "hero_pose": {"type": "string"},
                "active_physical_interaction": {"type": "string"},
                "object_logic_risks": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "category",
                "core_object",
                "immutable_features",
                "accessories_or_parts",
                "primary_value",
                "scene_logic",
                "background_support_surface",
                "background_depth_cues",
                "functional_lighting_source",
                "lighting_role",
                "physical_light_source",
                "lighting_effect_on_scene",
                "shadow_and_depth_behavior",
                "lighting_overuse_risk",
                "hero_pose",
                "active_physical_interaction",
                "object_logic_risks",
            ],
        },
        "parameter_story": {
            "type": "object",
            "properties": {
                "hero_parameter": {
                    "type": "object",
                    "properties": {
                        "should_display": {"type": "boolean"},
                        "value": {"type": "string"},
                        "unit": {"type": "string"},
                        "label": {"type": "string"},
                        "source_fact": {"type": "string"},
                        "role_reason": {"type": "string"},
                        "visual_treatment": {"type": "string"},
                    },
                    "required": [
                        "should_display",
                        "value",
                        "unit",
                        "label",
                        "source_fact",
                        "role_reason",
                        "visual_treatment",
                    ],
                },
                "secondary_parameters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "string"},
                            "unit": {"type": "string"},
                            "label": {"type": "string"},
                            "source_fact": {"type": "string"},
                            "visual_treatment": {"type": "string"},
                        },
                        "required": ["value", "unit", "label", "source_fact", "visual_treatment"],
                    },
                },
                "part_callouts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string"},
                            "anchor_part": {"type": "string"},
                            "source_fact": {"type": "string"},
                            "visual_treatment": {"type": "string"},
                        },
                        "required": ["label", "anchor_part", "source_fact", "visual_treatment"],
                    },
                },
                "bundle_or_trust": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string"},
                            "source_fact": {"type": "string"},
                            "visual_treatment": {"type": "string"},
                        },
                        "required": ["label", "source_fact", "visual_treatment"],
                    },
                },
                "omitted_parameter_reason": {"type": "string"},
            },
            "required": [
                "hero_parameter",
                "secondary_parameters",
                "part_callouts",
                "bundle_or_trust",
                "omitted_parameter_reason",
            ],
        },
        "generation_directives": {
            "type": "object",
            "properties": {
                "mode": {"type": "string"},
                "aspect_ratio": {"type": "string"},
                "product_fidelity": {"type": "string"},
                "allowed_edits": {"type": "array", "items": {"type": "string"}},
                "forbidden_edits": {"type": "array", "items": {"type": "string"}},
                "layout": {"type": "string"},
                "repair_priority": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "mode",
                "aspect_ratio",
                "product_fidelity",
                "allowed_edits",
                "forbidden_edits",
                "layout",
                "repair_priority",
            ],
        },
        "overlay_copy": {
            "type": "object",
            "properties": {
                "brand": {"type": "string"},
                "title": {"type": "string"},
                "subtitle": {"type": "string"},
                "numeric_badge": {"type": "string"},
                "feature_badges": {"type": "array", "items": {"type": "string"}},
                "trust_badge": {"type": "string"},
                "support_area": {"type": "string"},
            },
            "required": ["brand", "title", "subtitle", "numeric_badge", "feature_badges", "trust_badge", "support_area"],
        },
        "prompt": {"type": "string"},
    },
    "required": ["image_name", "product_analysis", "parameter_story", "generation_directives", "overlay_copy", "prompt"],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_source_contract(paths: list[Path]) -> str:
    chunks: list[str] = []
    for path in paths:
        try:
            label = str(path.relative_to(REPO))
        except ValueError:
            label = str(path)
        if not path.exists():
            chunks.append(f"\n## Missing Contract File\n{label}\n")
        else:
            chunks.append(f"\n## Contract File: {label}\n{read_text(path)}\n")
    return "\n".join(chunks)


def find_matching_blueprint(product_name: str, explicit: list[str]) -> list[Path]:
    paths: list[Path] = []
    for item in explicit:
        path = Path(item).expanduser().resolve()
        if path.exists():
            paths.append(path)

    generic_tokens = {
        "excitat",
        "product",
        "premium",
        "with",
        "for",
        "and",
        "kit",
        "main",
        "image",
    }
    tokens = [
        token
        for token in re.split(r"[^a-z0-9]+", product_name.lower())
        if len(token) >= 3 and token not in generic_tokens
    ]
    best: tuple[int, Path] | None = None
    for path in (REPO / "outputs").glob("*_blueprint.md"):
        haystack = (path.name + "\n" + read_text(path)).lower()
        score = sum(1 for token in tokens if token in haystack)
        if score and (best is None or score > best[0]):
            best = (score, path)
    if best and best[1] not in paths:
        min_score = 2 if len(tokens) >= 2 else 1
        if best[0] >= min_score:
            paths.append(best[1])
    return paths


def post_gemini(model: str, api_key: str, payload: dict, timeout: int) -> dict:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise RuntimeError(f"{model} request failed before response: {exc.__class__.__name__}") from exc
    if resp.status_code != 200:
        raise RuntimeError(f"{model} returned HTTP {resp.status_code}: {resp.text[:1200]}")
    return resp.json()


def extract_text_response(raw: dict) -> str:
    candidates = raw.get("candidates") or []
    if not candidates:
        raise ValueError(f"Gemini response has no candidates: {raw}")
    parts = candidates[0].get("content", {}).get("parts", [])
    texts = [part.get("text", "") for part in parts if part.get("text")]
    if not texts:
        raise ValueError(f"Gemini response has no text parts: {raw}")
    return "\n".join(texts)


def compile_plan(
    api_key: str,
    prompt_model: str,
    product_name: str,
    product_specs: str,
    source_hint: str,
    language: str,
    source_contract: str,
    source_image: Path,
) -> dict:
    user = f"""SOURCE SKILL CONTRACT:
{source_contract}

PRODUCT NAME:
{product_name}

PRODUCT FACTS:
{product_specs}

SOURCE IMAGE NOTES:
{source_hint or "Use the source image as the visual product truth."}

VISIBLE TEXT LANGUAGE:
{language}

Create a product-specific image-to-image generation plan and one complete prompt
for the image model. Use the same short one-pass full-card style as the original
Antigravity generate_image calls. The prompt should be compact, direct, and
free of production-pipeline terminology."""
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": f"{PLANNER_SYSTEM}\n\n{user}"},
                    {"inlineData": encode_image(source_image)},
                ],
            }
        ],
        "generationConfig": {"responseMimeType": "application/json", "responseSchema": PLAN_SCHEMA},
    }
    raw = post_gemini(prompt_model, api_key, payload, timeout=60)
    plan = json.loads(extract_text_response(raw))
    plan["planner_prompt"] = ensure_full_card_prompt(plan, language)
    plan["source_facts_text"] = f"{product_name}\n{product_specs}\n{source_hint}"
    return plan


def ensure_full_card_prompt(plan: dict, language: str) -> str:
    """Keep one-shot prompts close to the original Antigravity full-card style."""
    prompt = str(plan.get("prompt", "")).strip()
    # The planner is the control layer. Do not append repair clauses here; that
    # recreates the late-prompt patching behavior that made prior generations
    # drift. Keep this function as a light normalization gate only.
    prompt = re.sub(r"\s+", " ", prompt)
    return prompt


def clean_phrase(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def join_items(items: list[str], limit: int | None = None) -> str:
    values = [clean_phrase(item) for item in items if clean_phrase(item)]
    if limit is not None:
        values = values[:limit]
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    return ", ".join(values[:-1]) + ", and " + values[-1]


def compact_fact_text(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", clean_phrase(value).lower())


def singularize_compact(value: str) -> str:
    return value[:-1] if value.endswith("s") else value


def has_digits(value: str) -> bool:
    return any(ch.isdigit() for ch in value)


def parameter_value_is_verified(item: dict, source_facts: str) -> bool:
    value = clean_phrase(item.get("value"))
    unit = clean_phrase(item.get("unit"))
    label = clean_phrase(item.get("label"))
    source_fact = clean_phrase(item.get("source_fact"))
    combined = compact_fact_text(f"{source_facts} {source_fact}")
    value_unit = " ".join(part for part in [value, unit] if part).strip()
    compact_value_unit = compact_fact_text(value_unit)
    compact_value = compact_fact_text(value)
    compact_unit = compact_fact_text(unit)
    compact_label = compact_fact_text(label)
    if not value_unit and not label:
        return False
    if has_digits(value_unit):
        candidates = [
            compact_value_unit,
            compact_value + singularize_compact(compact_unit),
            compact_value + compact_label,
            compact_value + singularize_compact(compact_label),
        ]
        return any(candidate and candidate in combined for candidate in candidates)
    if compact_value and compact_value in combined:
        return True
    return bool(compact_label and compact_label in combined)


def visible_text_is_verified(text: str, source_facts: str) -> bool:
    text = clean_phrase(text)
    if not has_digits(text):
        return True
    compact_text = compact_fact_text(text)
    compact_source = compact_fact_text(source_facts)
    if compact_text and compact_text in compact_source:
        return True
    if re.search(r"\d+\s*[- ]?\s*in\s*[- ]?\s*\d+", text, re.I):
        return False
    numbers = re.findall(r"\d+(?:\.\d+)?", text)
    return bool(numbers) and all(number in compact_source for number in numbers)


def choose_value_island(
    hero_parameter: str,
    secondary_parameters: list[str],
    part_callouts: list[str],
) -> tuple[str, list[str], list[str]]:
    """Pick one first-read value island without inventing unsupported claims."""
    if hero_parameter:
        return hero_parameter, secondary_parameters, part_callouts
    if secondary_parameters:
        return secondary_parameters[0], secondary_parameters[1:], part_callouts
    if part_callouts:
        return part_callouts[0], secondary_parameters, part_callouts[1:]
    return "", secondary_parameters, part_callouts


def format_parameter_item(item: object, source_facts: str = "") -> str:
    if not isinstance(item, dict):
        return ""
    if item.get("should_display") is False:
        return ""
    if source_facts and not parameter_value_is_verified(item, source_facts):
        return ""
    value = clean_phrase(item.get("value"))
    unit = clean_phrase(item.get("unit"))
    label = clean_phrase(item.get("label"))
    treatment = clean_phrase(item.get("visual_treatment"))
    value_unit = " ".join(part for part in [value, unit] if part).strip()
    if value_unit and label:
        base = f"'{value_unit}' for {label}"
    elif value_unit:
        base = f"'{value_unit}'"
    elif label:
        base = f"'{label}'"
    else:
        return ""
    if treatment:
        return f"{base} as {treatment}"
    return base


def format_callout_item(item: object) -> str:
    if not isinstance(item, dict):
        return ""
    label = clean_phrase(item.get("label"))
    anchor = clean_phrase(item.get("anchor_part"))
    treatment = clean_phrase(item.get("visual_treatment"))
    if not label:
        return ""
    parts = [f"'{label}'"]
    if anchor:
        parts.append(f"anchored to {anchor}")
    if treatment:
        parts.append(f"as {treatment}")
    return ", ".join(parts)


def plan_route_text(plan: dict) -> tuple[str, set[str]]:
    analysis = plan.get("product_analysis", {})
    text = " ".join(
        [
            clean_phrase(analysis.get("category")),
            clean_phrase(analysis.get("core_object")),
            clean_phrase(analysis.get("scene_logic")),
            clean_phrase(analysis.get("functional_lighting_source")),
            clean_phrase(analysis.get("physical_light_source")),
        ]
    ).lower()
    tokens = {token for token in re.split(r"[^a-z0-9]+", text) if token}
    return text, tokens


def infer_visual_prototype(plan: dict) -> str:
    haystack, tokens = plan_route_text(plan)
    if tokens & {"ps5", "gaming", "charger", "game"}:
        return "Dark Neon / Tech Poster for a gaming accessory"
    if tokens & {"baby", "kitchen", "appliance", "processor", "blender", "steamer"}:
        return "Clean Kitchen / Baby Care Appliance Card"
    if tokens & {"mattress", "suv", "auto", "vehicle", "travel"} or " car " in f" {haystack} ":
        return "Teal Paper Sleeve / Auto Outdoor Comfort for a vehicle travel accessory"
    if tokens & {"solar", "stem", "science", "educational", "planet"}:
        return "Cosmic Science / Study Ambient for a STEM educational assembly kit"
    if tokens & {"oscilloscope", "meter", "lab", "electronics", "pcb"}:
        return "Tech Lab / Measurement Poster for an electronics instrument"
    return "Product-first Ozon commercial main-card frame"


def infer_brand_shelf(plan: dict) -> str:
    copy = plan.get("overlay_copy", {})
    brand = clean_phrase(copy.get("brand")) or "EXCITAT"
    haystack, tokens = plan_route_text(plan)
    if tokens & {"solar", "stem", "science", "educational", "planet"}:
        return f"slanted carbon-fiber {brand} brand shelf with warm orange-gold border glow and bold white logo"
    if tokens & {"baby", "kitchen", "appliance", "processor", "blender", "steamer"}:
        return f"slanted teal/white {brand} brand shelf with a soft orange baby-care accent and bold white logo"
    if tokens & {"mattress", "suv", "auto", "vehicle", "travel"} or " car " in f" {haystack} ":
        return f"slanted teal/charcoal {brand} brand shelf with bold white logo"
    if tokens & {"ps5", "gaming", "charger", "oscilloscope", "meter", "lab", "electronics", "pcb"}:
        return f"{brand} Speed Lightning Shelf, slanted cyan/charcoal brushed-metal shelf with bold white logo"
    return f"slanted category-matched {brand} brand shelf with bold white logo"


def infer_parameter_palette(plan: dict) -> str:
    haystack, tokens = plan_route_text(plan)
    if tokens & {"baby", "kitchen", "appliance", "processor", "blender", "steamer"}:
        return "light appliance palette: white/soft grey base, teal or OZON blue value islands, warm orange/gold food accent, dark ink text; avoid black slabs"
    if tokens & {"mattress", "suv", "auto", "vehicle", "travel"} or " car " in f" {haystack} ":
        return "auto comfort palette: teal/charcoal structure with warm daylight accents; value blocks should be teal or warm gold, not pure black"
    if tokens & {"solar", "stem", "science", "educational", "planet"}:
        return "cosmic science palette: dark study base with warm solar-gold value islands and small orange highlights"
    if tokens & {"tool", "drill", "saw", "hardware", "garden", "automotive"}:
        return "tool palette: dark graphite structure with cyan or safety-orange value islands and strong white numeric text"
    if tokens & {"ps5", "gaming", "charger", "oscilloscope", "meter", "lab", "electronics", "pcb"}:
        return "tech palette: charcoal/cyan value islands with controlled neon edges and white numeric text"
    return "category-matched Ozon 3-color palette from DESIGN.md; one accent for value islands, dark ink for text, no generic black/white default"


def accessory_support_sentence(plan: dict) -> str:
    analysis = plan.get("product_analysis", {})
    copy = plan.get("overlay_copy", {})
    accessories = [clean_phrase(item) for item in analysis.get("accessories_or_parts", []) if clean_phrase(item)]
    support_area = clean_phrase(copy.get("support_area")).lower()
    haystack = " ".join(accessories + [support_area, clean_phrase(analysis.get("category"))]).lower()
    if not accessories:
        return ""
    if any(token in haystack for token in ["pump", "nozzle", "carry bag", "flat-lay", "accessory strip", "bottom"]):
        return f"Accessories including {join_items(accessories, 5)} are arranged as a clean bottom flat-lay strip with soft contact shadows."
    return ""


FORBIDDEN_UNVERIFIED_TRUST_TERMS = (
    "bpa",
    "fda",
    "ce",
    "certified",
    "food grade",
    "medical",
    "hospital",
    "safe",
)


def facts_text(plan: dict) -> str:
    return clean_phrase(plan.get("source_facts_text")).lower()


def verified_trust_badge(plan: dict, trust_badge: str) -> str:
    trust = clean_phrase(trust_badge)
    facts = facts_text(plan)
    lowered = trust.lower()
    if trust and not any(term in lowered for term in FORBIDDEN_UNVERIFIED_TRUST_TERMS):
        return trust
    if trust and lowered in facts:
        return trust
    if any(term in facts for term in ["消毒", "steriliz", "sterilis"]):
        return "Bottle Sterilizer"
    if "220v" in facts or "220 v" in facts:
        return "220V Power"
    if any(term in facts for term in ["led", "报警", "alarm"]):
        return "LED Alarm"
    if any(term in facts for term in ["清洁", "clean"]):
        return "Easy Clean"
    return "EXCITAT Quality"


def compile_fusion_v1_prompt(plan: dict, language: str) -> str:
    """Compile the selected fusion-v1 one-shot prompt shape.

    The planner is allowed to reason, but final prompt wording is assembled here
    so required regions do not get dropped or replaced by late-stage fixes.
    """
    analysis = plan.get("product_analysis", {})
    directives = plan.get("generation_directives", {})
    copy = plan.get("overlay_copy", {})
    parameter_story = plan.get("parameter_story", {})
    core = clean_phrase(analysis.get("core_object")) or "product"
    immutable = [clean_phrase(item) for item in analysis.get("immutable_features", []) if clean_phrase(item)]
    product_fidelity = clean_phrase(directives.get("product_fidelity"))
    hero_pose = clean_phrase(analysis.get("hero_pose"))
    support_surface = clean_phrase(analysis.get("background_support_surface"))
    depth_cues = clean_phrase(analysis.get("background_depth_cues"))
    active_interaction = clean_phrase(analysis.get("active_physical_interaction"))
    physical_light = clean_phrase(analysis.get("physical_light_source") or analysis.get("functional_lighting_source"))
    lighting_effect = clean_phrase(analysis.get("lighting_effect_on_scene"))
    shadow_depth = clean_phrase(analysis.get("shadow_and_depth_behavior"))
    title = clean_phrase(copy.get("title"))
    subtitle = clean_phrase(copy.get("subtitle"))
    numeric_badge = clean_phrase(copy.get("numeric_badge"))
    feature_badges = [clean_phrase(item) for item in copy.get("feature_badges", []) if clean_phrase(item)]
    trust_badge = verified_trust_badge(plan, clean_phrase(copy.get("trust_badge")))
    source_facts = clean_phrase(plan.get("source_facts_text"))
    hero_parameter = ""
    secondary_parameters: list[str] = []
    part_callouts: list[str] = []
    bundle_or_trust: list[str] = []
    if isinstance(parameter_story, dict):
        hero_parameter = format_parameter_item(parameter_story.get("hero_parameter"), source_facts)
        secondary_parameters = [
            format_parameter_item(item, source_facts)
            for item in parameter_story.get("secondary_parameters", [])
            if format_parameter_item(item, source_facts)
        ]
        part_callouts = [
            format_callout_item(item)
            for item in parameter_story.get("part_callouts", [])
            if format_callout_item(item)
        ]
        bundle_or_trust = [
            format_callout_item(item)
            for item in parameter_story.get("bundle_or_trust", [])
            if format_callout_item(item)
        ]
    language_label = "English" if "english" in language.lower() else language

    preserve_bits = []
    if product_fidelity:
        preserve_bits.append(product_fidelity.rstrip("."))
    if immutable:
        preserve_bits.append(f"Preserve {join_items(immutable, 6)} 100% exact and undeformed")
    preserve_sentence = ". ".join(preserve_bits) + "." if preserve_bits else "Preserve product shapes, colors, proportions, materials, and physical contact points 100% exact and undeformed."

    staging_parts = []
    if hero_pose:
        staging_parts.append(hero_pose)
    if support_surface:
        staging_parts.append(f"grounded on {support_surface}")
    if active_interaction:
        staging_parts.append(active_interaction)
    staging_sentence = "Staging: " + "; ".join(staging_parts).rstrip(".") + "." if staging_parts else "Staging: place the product in its most functional, physically believable hero pose."

    accessory_sentence = accessory_support_sentence(plan)
    background_parts = []
    if depth_cues:
        background_parts.append(f"Background is shallow-depth category context with {depth_cues}")
    if physical_light or lighting_effect:
        if physical_light and lighting_effect:
            background_parts.append(f"Lighting comes from {physical_light}, creating {lighting_effect}")
        elif physical_light:
            background_parts.append(f"Lighting comes from {physical_light}")
        else:
            background_parts.append(f"Lighting creates {lighting_effect}")
    if shadow_depth:
        background_parts.append(shadow_depth)
    background_sentence = ". ".join(part.rstrip(".") for part in background_parts) + "." if background_parts else ""

    top_left_bits = []
    if title:
        top_left_bits.append(f"bold white '{title}'")
    if subtitle and visible_text_is_verified(subtitle, source_facts):
        top_left_bits.append(f"subtitle '{subtitle}'")
    top_left = ", ".join(top_left_bits) if top_left_bits else "short title and one numeric accent badge"
    feature_items = part_callouts or [f"'{item}'" for item in feature_badges]
    feature_text = join_items(feature_items, 3) or "2-3 product-specific feature badges"
    trust_text = f"'{trust_badge}'" if trust_badge else "one circular trust badge"
    value_island_text, secondary_parameters, part_callouts = choose_value_island(
        hero_parameter,
        secondary_parameters,
        part_callouts,
    )
    parameter_rail_text = join_items(secondary_parameters, 4)
    feature_items = part_callouts or [f"'{item}'" for item in feature_badges]
    feature_text = join_items(feature_items, 3) or "2-3 product-specific feature badges"
    bundle_text = join_items(bundle_or_trust, 2)

    sentences = [
        "Generate a 1:1 square Ozon main image card, not a wide banner or landscape poster.",
        "Keep the product centered and occupying 60-75% of the square canvas.",
        f"Extract the original {core} from the source image.",
        preserve_sentence,
        f"Visual prototype: {infer_visual_prototype(plan)}.",
        staging_sentence,
    ]
    if accessory_sentence:
        sentences.append(accessory_sentence)
    if background_sentence:
        sentences.append(background_sentence)
    sentences.extend(
        [
            (
                f"Overlay {language_label} layout: 1) Top-right: {infer_brand_shelf(plan)}. "
                f"2) Top-left: {top_left}. "
                + f"Use {infer_parameter_palette(plan)} for all value islands and badges. "
                + (f"3) Beside the product edge, place one oversized commerce value island with {value_island_text}; it should occupy about one-fifth of the card width, use a category-colored slab/circle, make the value text dominate the block, and look like a freestanding adjacent label with no connector line. " if value_island_text else "")
                + (f"{'4' if value_island_text else '3'}) Near the lower-left product/support area, place secondary value slabs with {parameter_rail_text}; smaller than the main value island but larger than icons, freestanding with no connector line, integrated with the scene and using the same category accent. " if parameter_rail_text else "")
                + f"{'5' if value_island_text and parameter_rail_text else '4' if value_island_text or parameter_rail_text else '3'}) Product-adjacent feature callouts {feature_text}; use compact chips close to the relevant part, short connector dots or very short elbow lines only, never long leader lines crossing the product. "
                + f"{'6' if value_island_text and parameter_rail_text else '5' if value_island_text or parameter_rail_text else '4'}) Circular trust badge: {trust_text}. "
                + (f"{'7' if value_island_text and parameter_rail_text else '6' if value_island_text or parameter_rail_text else '5'}) Bottom/corner support block: {bundle_text}; trust/accessory only, do not repeat any value already shown in the value island or secondary slabs." if bundle_text else "")
                + " No duplicate numbers or duplicate claims across regions. Value islands and value slabs must not use connector lines."
            ),
            "Clean layout, professional advertising style.",
        ]
    )
    return re.sub(r"\s+", " ", " ".join(sentences)).strip()


def compile_image_prompt(plan: dict, language: str, compiler: str) -> str:
    if compiler == "planner_raw":
        return ensure_full_card_prompt(plan, language)
    if compiler == "fusion_v1":
        return compile_fusion_v1_prompt(plan, language)
    raise ValueError(f"Unknown prompt compiler: {compiler}")


def encode_image(path: Path) -> dict:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return {"mimeType": mime, "data": base64.b64encode(path.read_bytes()).decode("ascii")}


def save_inline_image(raw: dict, out_path: Path) -> Path:
    candidates = raw.get("candidates") or []
    if not candidates:
        raise ValueError(f"Image response has no candidates: {raw}")
    for part in candidates[0].get("content", {}).get("parts", []):
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data"):
            mime = inline.get("mimeType") or inline.get("mime_type") or "image/png"
            suffix = ".jpg" if "jpeg" in mime or "jpg" in mime else ".png"
            target = out_path.with_suffix(suffix)
            target.write_bytes(base64.b64decode(inline["data"]))
            return target
    raise ValueError(f"Image response contains no inline image data: {raw}")


def generate_image(
    api_key: str,
    image_model: str,
    source_image: Path,
    prompt: str,
    out_path: Path,
    retries: int,
    image_timeout: int,
) -> Path:
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}, {"inlineData": encode_image(source_image)}],
            }
        ]
    }
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            raw = post_gemini(image_model, api_key, payload, timeout=image_timeout)
            return save_inline_image(raw, out_path)
        except Exception as exc:
            last_error = exc
            print(f"image generation attempt {attempt}/{retries} failed: {exc}", file=sys.stderr)
            if attempt < retries:
                time.sleep(8 * attempt)
    assert last_error is not None
    raise last_error


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return value or "ozon_main_image"


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Ozon main-image generation agent.")
    parser.add_argument("--product-name", required=True)
    parser.add_argument("--product-specs", required=True, help="Facts text or path to a text/markdown file.")
    parser.add_argument("--product-image", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--source-hint", default="")
    parser.add_argument("--language", default="English / Latin script")
    parser.add_argument("--google-key", default=os.getenv("GEMINI_KEY"))
    parser.add_argument("--prompt-model", default="gemini-3.5-flash")
    parser.add_argument("--image-model", default="gemini-3.1-flash-image")
    parser.add_argument(
        "--prompt-compiler",
        choices=["fusion_v1", "planner_raw"],
        default=DEFAULT_PROMPT_COMPILER,
        help="Final prompt assembly mode. fusion_v1 is the locked selected workflow; planner_raw is for diagnostics.",
    )
    parser.add_argument("--contract-file", action="append", default=[])
    parser.add_argument("--blueprint", action="append", default=[], help="Optional product blueprint markdown file.")
    parser.add_argument("--prompt-only", action="store_true")
    parser.add_argument("--image-timeout", type=int, default=600, help="Seconds to wait for one image request.")
    parser.add_argument("--retries", type=int, default=1)
    args = parser.parse_args()

    if not args.google_key:
        raise SystemExit("Missing Google API key. Use --google-key or GEMINI_KEY.")

    source = Path(args.product_image).resolve()
    if not source.exists():
        raise SystemExit(f"Missing product image: {source}")

    specs = args.product_specs
    specs_path = Path(specs)
    try:
        if specs_path.exists() and specs_path.is_file():
            specs = specs_path.read_text(encoding="utf-8")
    except OSError:
        # Treat long/free-form product facts as literal text, not a path.
        pass

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_paths = list(DEFAULT_CONTRACT_FILES)
    contract_paths.extend(Path(p).resolve() for p in args.contract_file)
    contract_paths.extend(find_matching_blueprint(args.product_name, args.blueprint))
    source_contract = read_source_contract(contract_paths)
    (out_dir / "source_contract_snapshot.md").write_text(source_contract, encoding="utf-8")

    plan = compile_plan(
        api_key=args.google_key,
        prompt_model=args.prompt_model,
        product_name=args.product_name,
        product_specs=specs,
        source_hint=args.source_hint,
        language=args.language,
        source_contract=source_contract,
        source_image=source,
    )
    plan["prompt_compiler"] = args.prompt_compiler
    plan["prompt"] = compile_image_prompt(plan, args.language, args.prompt_compiler)
    (out_dir / "agent_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "image_model_prompt.txt").write_text(plan["prompt"], encoding="utf-8")

    report = [
        "# Ozon Main Image Agent Run",
        "",
        f"- prompt_model: `{args.prompt_model}`",
        f"- image_model: `{args.image_model}`",
        f"- prompt_compiler: `{args.prompt_compiler}`",
        f"- source_image: `{source}`",
        f"- category: `{plan['product_analysis']['category']}`",
        f"- core_object: `{plan['product_analysis']['core_object']}`",
        f"- physical_light_source: `{plan['product_analysis'].get('physical_light_source') or plan['product_analysis'].get('functional_lighting_source', '')}`",
        f"- lighting_role: `{plan['product_analysis'].get('lighting_role', '')}`",
        f"- lighting_effect_on_scene: `{plan['product_analysis'].get('lighting_effect_on_scene', '')}`",
        f"- shadow_and_depth_behavior: `{plan['product_analysis'].get('shadow_and_depth_behavior', '')}`",
        f"- lighting_overuse_risk: `{plan['product_analysis'].get('lighting_overuse_risk', '')}`",
        f"- hero_pose: `{plan['product_analysis'].get('hero_pose', '')}`",
        f"- active_physical_interaction: `{plan['product_analysis'].get('active_physical_interaction', '')}`",
        f"- product_fidelity: `{plan['generation_directives']['product_fidelity']}`",
        f"- object_logic_risks: `{'; '.join(plan['product_analysis']['object_logic_risks'])}`",
        "",
    ]

    if args.prompt_only:
        report.append("Image generation skipped by `--prompt-only`.")
        (out_dir / "run_report.md").write_text("\n".join(report), encoding="utf-8")
        print(out_dir)
        return

    final = generate_image(
        api_key=args.google_key,
        image_model=args.image_model,
        source_image=source,
        prompt=plan["prompt"],
        out_path=out_dir / f"{slugify(plan['image_name'])}",
        retries=args.retries,
        image_timeout=args.image_timeout,
    )
    report.extend([f"- final_image: `{final}`", ""])
    (out_dir / "run_report.md").write_text("\n".join(report), encoding="utf-8")
    print(final)


if __name__ == "__main__":
    main()
