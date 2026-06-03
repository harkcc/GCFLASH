#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SOURCE_DIR = REPO / "skills" / "ozon-image-generator"


@dataclass
class ProductAnalysis:
    product_name: str
    category: str
    silhouette: str
    archetype: str
    frame_family: str
    staging_context: str
    accent_palette: list[str]
    primary_click_catch: str
    title: str
    subtitle: str
    feature_badges: list[dict[str, str]]
    trust_badge: dict[str, str]
    parameter_story: dict[str, object]
    bottom_info_bar: str
    verified_facts: list[str]
    inferred_facts: list[str]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def find_matching_blueprint(product_name: str, explicit: str | None) -> Path | None:
    if explicit:
        path = Path(explicit)
        return path if path.exists() else None
    generic_tokens = {"excitat", "kit", "with", "for", "inch", "product", "premium"}
    tokens = [
        t
        for t in re.split(r"[^a-z0-9]+", product_name.lower())
        if len(t) >= 3 and t not in generic_tokens
    ]
    best: tuple[int, Path] | None = None
    for path in (REPO / "outputs").glob("*_blueprint.md"):
        haystack = path.name.lower() + "\n" + read_text(path).lower()
        score = sum(1 for t in tokens if t in haystack)
        if score and (best is None or score > best[0]):
            best = (score, path)
    if not best:
        return None
    # Avoid matching unrelated blueprints only through generic marketplace text.
    min_score = 2 if len(tokens) >= 2 else 1
    return best[1] if best[0] >= min_score else None


def has_any(text: str, terms: list[str]) -> bool:
    low = text.lower()
    return any(term.lower() in low for term in terms)


def build_parameter_story_contract(
    feature_badges: list[dict[str, str]],
    trust_badge: dict[str, str],
    verified_facts: list[str],
) -> dict[str, object]:
    part_callouts = [
        {
            "label": badge["label"],
            "icon": badge["icon"],
            "source": badge.get("claim_source", "product specs"),
            "visual_role": "part_anchored_callout",
            "anchor_rule": "point to a visible product part or accessory when possible",
        }
        for badge in feature_badges[:3]
    ]

    return {
        "planner_required": True,
        "candidate_verified_facts": verified_facts,
        "role_taxonomy": [
            "hero_parameter",
            "side_spec_rail",
            "part_anchored_callout",
            "bundle_accessory_count",
            "trust_seal",
        ],
        "hero_parameter": {
            "value": "",
            "unit": "",
            "label": "planner must select from verified facts only when commercially decisive",
            "source": "planner_placeholder",
            "visual_role": "planner_selected_hero_parameter",
        },
        "spec_rail": [],
        "part_callouts": part_callouts,
        "bundle_trust": [
            {
                "label": trust_badge["label"],
                "icon": trust_badge["icon"],
                "source": trust_badge.get("claim_source", "brand trust overlay"),
                "visual_role": "trust_seal_candidate",
            }
        ],
        "planning_rule": (
            "A model planner must choose which verified facts become the hero parameter, "
            "side spec rail, part callouts, bundle blocks, and trust seals. The compiler "
            "only publishes source facts and role taxonomy; it must not classify parameter "
            "importance with regex, unit scoring, or category hard-coding."
        ),
    }


def build_analysis(product_name: str, specs: str, blueprint_text: str) -> ProductAnalysis:
    combined = f"{product_name}\n{specs}\n{blueprint_text}"
    product_only = f"{product_name}\n{specs}"
    is_gaming = has_any(combined, ["ps5", "controller", "gaming", "rgb", "console", "headset"])
    is_ventilation = has_any(
        product_only,
        ["ventilator", "evacuare", "exhaust fan", "fan", "cfm", "aerisire", "anti-insecte", "palete"],
    )
    is_tool = has_any(combined, ["steel", "tool", "automotive", "car", "workshop"])
    is_home = has_any(combined, ["kitchen", "home", "appliance", "vacuum", "humidifier"])

    if is_ventilation:
        category = "Home Ventilation / Industrial Appliance"
        archetype = "custom_ventilation_green"
        frame_family = "Eco Industrial / Clean Air"
        staging = "clean kitchen or utility-room wall with subtle airflow trails, anti-insect shutter cue, and fresh green leaf accents"
        accents = ["#22c55e clean green", "#12151a deep charcoal", "#ffffff white"]
    elif is_gaming:
        category = "Tech / Gaming Accessories"
        archetype = "tech_dark_green"
        frame_family = "Dark Neon / Tech Poster"
        staging = "futuristic gaming room wall with dark slate panels and controlled cyan/magenta RGB light"
        accents = ["#00e5ff cyan", "#12151a deep charcoal", "#c94cff controlled magenta"]
    elif is_tool:
        category = "Tools / Hardware"
        archetype = "rugged_grey_orange"
        frame_family = "Rugged Grey / Orange Hardware"
        staging = "workshop bench, concrete, real tool-use environment, shallow depth of field"
        accents = ["#ff6b00 safety orange", "#2b2d31 muted grey", "#ffffff white"]
    elif is_home:
        category = "Home Appliances"
        archetype = "appliance_white_blue"
        frame_family = "Clean White / Blue Appliance"
        staging = "warm home or kitchen surface with soft practical lighting"
        accents = ["#005bff OZON blue", "#f0f2f5 light appliance", "#ffb800 warm gold"]
    else:
        category = "Tech / Smart Device"
        archetype = "tech_dark_green"
        frame_family = "Dark Tech"
        staging = "matte graphite product scene with subtle relevant context"
        accents = ["#00e5ff cyan", "#12151a deep charcoal", "#ffffff white"]

    click = "planner_selected_parameter"

    features: list[dict[str, str]] = []
    if has_any(product_only, ["dual", "controller", "charger"]):
        features.append({"label": "Dual Charger", "icon": "gamepad", "claim_source": "product specs"})
    if has_any(product_only, ["rgb", "lighting", "led"]):
        features.append({"label": "RGB Light", "icon": "rgb-ring", "claim_source": "product specs"})
    if is_ventilation:
        if has_any(product_only, ["25db", "silentios", "silent"]):
            features.append({"label": "25dB Silent", "icon": "sound", "claim_source": "product specs"})
        if has_any(product_only, ["40w", "40 w"]):
            features.append({"label": "40W Power", "icon": "bolt", "claim_source": "product specs"})
        if has_any(product_only, ["otel inoxidabil", "steel", "otel"]):
            features.append({"label": "Steel Blades", "icon": "fan", "claim_source": "product specs"})
        if has_any(product_only, ["anti-insecte", "clapeta"]):
            features.append({"label": "Anti-Insect", "icon": "shield", "claim_source": "product specs"})
    if has_any(product_only, ["steel", "durable", "construction", "otel"]):
        features.append({"label": "Durable Steel", "icon": "bolt", "claim_source": "product specs"})
    # Keep the strongest three without duplicates.
    deduped = []
    seen = set()
    for item in features:
        if item["label"] not in seen:
            seen.add(item["label"])
            deduped.append(item)
    features = deduped
    if not features:
        features = [
            {"label": "Complete Kit", "icon": "box", "claim_source": "inferred"},
            {"label": "Easy Use", "icon": "gear", "claim_source": "inferred"},
        ]

    if is_gaming:
        title = "WALL MOUNT KIT"
        subtitle = "For PS5 Slim & Pro"
        silhouette = "vertical wall-mounted console kit with headset hook, black steel bracket, and bottom dual controller charging dock"
    elif is_ventilation:
        title = "VENTILATOR 6 INCH"
        subtitle = "Evacuare aer"
        silhouette = "square black exhaust fan faceplate with circular stainless guard, visible 7-blade fan, cylindrical rear duct, and power cable"
    else:
        title = product_name[:32].upper()
        subtitle = "Premium E-commerce Hero"
        silhouette = "dominant product body centered with clear category silhouette"

    verified = [s.strip() for s in re.split(r"[,;\n]+", specs) if s.strip()]
    inferred = []
    if is_gaming:
        inferred.append("gaming room wall staging selected from category routing")
    if is_ventilation:
        inferred.append("clean-air green staging selected from ventilation category routing")
    if not blueprint_text:
        inferred.append("no product-specific blueprint found; used source contract heuristics")

    trust_badge = {"label": "EXCITAT 1-Year Warranty", "icon": "shield", "claim_source": "brand trust overlay"}
    parameter_story = build_parameter_story_contract(features, trust_badge, verified)

    return ProductAnalysis(
        product_name=product_name,
        category=category,
        silhouette=silhouette,
        archetype=archetype,
        frame_family=frame_family,
        staging_context=staging,
        accent_palette=accents,
        primary_click_catch=click,
        title=title,
        subtitle=subtitle,
        feature_badges=features[:3],
        trust_badge=trust_badge,
        parameter_story=parameter_story,
        bottom_info_bar=(
            "Clapeta anti-insecte + motor cupru"
            if is_ventilation
            else "Controller Charging Indicators & Hook"
            if is_gaming
            else "Included accessories / key use state"
        ),
        verified_facts=verified,
        inferred_facts=inferred,
    )


def build_base_prompt(analysis: ProductAnalysis) -> str:
    badge_labels = ", ".join(b["label"] for b in analysis.feature_badges)
    parameter_story = analysis.parameter_story
    hero_parameter = parameter_story["hero_parameter"]
    spec_rail = parameter_story["spec_rail"]
    spec_rail_labels = ", ".join(
        f"{item.get('value', '')} {item.get('unit', '')}".strip()
        for item in spec_rail  # type: ignore[union-attr]
    ) or "model planner required"
    return f"""Use case: ads-marketing / product-mockup
Asset type: square 1:1 e-commerce hero base image for deterministic overlay.

Product analysis:
- Product: {analysis.product_name}
- Category: {analysis.category}
- Silhouette: {analysis.silhouette}
- Parameter display: planner must select the hero parameter, optional secondary rail, part callouts, and trust/accessory blocks from verified facts before overlay rendering.
- Feature badges for later overlay: {badge_labels}
- Frame family: {analysis.frame_family}
- Accent palette: {", ".join(analysis.accent_palette)}
- Parameter story contract for later overlay: hero parameter {hero_parameter['label']}; secondary spec rail: {spec_rail_labels}.

Primary request:
Create a premium marketplace base image for {analysis.product_name}. The product should be the unmistakable focal point and occupy 60-70% of the canvas.

Scene and background:
Use {analysis.staging_context}. Keep the background low-noise, high contrast, and directly related to the product use case. Use shallow depth of field, soft vignette, realistic contact or wall shadows, and controlled commercial rim lighting.

Composition:
Place the product centrally or slightly right in a heroic three-quarter view. Preserve the visible product parts and category silhouette. Leave clean safe zones in the top-left for title and an optional planner-selected hero parameter block, left or lower-left for an optional stacked spec rail, top-right for slanted EXCITAT brand shelf, right side for part-anchored feature callouts, and bottom for accessory/info bar.

Text policy:
No generated text. No readable logos. No watermark. All title, brand, icons, badges, and claims will be added later as deterministic overlay layers.

Negative constraints:
No official console/platform logos unless provided by the user, no extra products beyond the requested kit, no cluttered rainbow poster, no busy smoke, no human hands, no cropped product, no model-rendered typography.
"""


def build_overlay_plan(analysis: ProductAnalysis) -> dict:
    return {
        "canvas": "1:1 square",
        "text_policy": "deterministic_overlay_only",
        "parameter_story": analysis.parameter_story,
        "brand_shelf": {
            "position": "top-right",
            "variant": "EXCITAT Speed Lightning Shelf",
            "style": "slanted -6deg dark graphite/glass shelf, cyan stroke, subtle magenta offset",
        },
        "title_block": {
            "position": "top-left",
            "title": analysis.title,
            "subtitle": analysis.subtitle,
            "primary_badge": None,
            "primary_badge_source": "parameter_story.hero_parameter when planner selects should_display=true",
        },
        "hero_parameter_block": {
            "position": "top-left or left-center",
            "display": analysis.parameter_story["hero_parameter"],
            "style": "largest numeric slab or circle; value 2.5-3x larger than unit/label",
        },
        "spec_rail": {
            "position": "left vertical rail or lower-left stacked slabs",
            "items": analysis.parameter_story["spec_rail"],
            "style": "large high-contrast parameter containers, not small equal-weight pills",
        },
        "part_callouts": {
            "position": "right side or product-adjacent detail tags",
            "items": analysis.parameter_story["part_callouts"],
            "style": "short labels connected to visible product features with thin connector lines",
        },
        "bundle_trust_blocks": {
            "position": "bottom strip, lower corner seals, or accessory inset area",
            "items": analysis.parameter_story["bundle_trust"],
            "style": "accessory counts use compact slabs; warranty/trust uses circular seal or shield",
        },
        "feature_badges": [
            {"position": f"right-column-{i+1}", **badge}
            for i, badge in enumerate(analysis.feature_badges)
        ],
        "trust_badge": {
            "position": "right-side",
            **analysis.trust_badge,
        },
        "bottom_info_bar": {
            "position": "bottom-left or bottom-center",
            "copy": analysis.bottom_info_bar,
        },
        "connector_lines": {
            "style": "1px thin cyan straight lines, small round endpoint, no arrowheads",
            "rule": "connect feature badges to visible product parts without covering core details",
        },
        "safe_margin_px": 15,
        "palette_budget": analysis.accent_palette,
    }


def write_outputs(out: Path, analysis: ProductAnalysis, prompt: str, overlay: dict) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "analysis.md").write_text(
        "# Product Analysis\n\n"
        + "\n".join(f"- **{k}**: {v}" for k, v in asdict(analysis).items()),
        encoding="utf-8",
    )
    (out / "base_prompt.txt").write_text(prompt, encoding="utf-8")
    (out / "overlay_plan.json").write_text(json.dumps(overlay, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "qa_checklist.md").write_text(
        """# QA Checklist

- [ ] Product silhouette recognizable at 160px.
- [ ] Hero parameter remains readable at 160px and is the largest numeric overlay.
- [ ] Secondary numeric specs use large containers when verified specs exist.
- [ ] Product occupies roughly 60-75% of canvas.
- [ ] No model-generated text/logos are present in base image.
- [ ] Title, badges, icons, and brand shelf are deterministic overlay layers.
- [ ] At least 15px spacing between product contour and overlays.
- [ ] Background is category-relevant, not generic.
- [ ] Visual palette stays within base, ink, and accent roles.
- [ ] Claims are traceable to product specs or marked as inferred.
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-name", required=True)
    parser.add_argument("--product-specs", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--blueprint")
    args = parser.parse_args()

    source_files = ["README.md", "SKILL.md", "DESIGN.md", "RUNTIME_CONTEXT.md"]
    missing = [name for name in source_files if not (SOURCE_DIR / name).exists()]
    if missing:
        raise SystemExit(f"Missing source contract files: {', '.join(missing)}")

    blueprint_path = find_matching_blueprint(args.product_name, args.blueprint)
    blueprint_text = read_text(blueprint_path) if blueprint_path else ""
    analysis = build_analysis(args.product_name, args.product_specs, blueprint_text)
    prompt = build_base_prompt(analysis)
    overlay = build_overlay_plan(analysis)
    overlay["source_contract"] = {
        "read_as_one_system": [str(SOURCE_DIR / name) for name in source_files],
        "product_blueprint": str(blueprint_path) if blueprint_path else None,
        "brand_frame_blueprint": str(REPO / "workflow" / "design_systems" / "exite_41_reference_replication.BLUEPRINT.md"),
    }
    write_outputs(Path(args.out), analysis, prompt, overlay)
    print(Path(args.out).resolve())


if __name__ == "__main__":
    main()
