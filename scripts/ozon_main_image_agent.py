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
4. Choose short overlay copy: title, one click-catch badge, 2-3 feature badges,
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
5. Write the final image prompt in the original Antigravity style:
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
    "required": ["image_name", "product_analysis", "generation_directives", "overlay_copy", "prompt"],
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
    if subtitle:
        top_left_bits.append(f"subtitle '{subtitle}'")
    if numeric_badge:
        top_left_bits.append(f"accent badge '{numeric_badge}'")
    top_left = ", ".join(top_left_bits) if top_left_bits else "short title and one numeric accent badge"
    feature_text = join_items([f"'{item}'" for item in feature_badges], 3) or "2-3 product-specific feature badges"
    trust_text = f"'{trust_badge}'" if trust_badge else "one circular trust badge"

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
                f"3) Right side: rounded/icon feature badges {feature_text}. "
                f"4) Right side circular badge: {trust_text}."
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
