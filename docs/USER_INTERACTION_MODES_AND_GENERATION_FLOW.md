# User Interaction Modes and Generation Flow

Date: 2026-05-22

## Position

The frame is a late-stage composition module. The next work should focus on the
product image generation flow and the user interaction model.

Core rule:

```text
user uploads product
  -> system extracts product truth
  -> user chooses mode and direction
  -> user enters mode-specific parameters
  -> generate scene/background/layout candidates
  -> composite preserved product, deterministic text, and optional frame
  -> review, repair, and export
```

The product body should remain controlled. AI generation is mainly responsible
for scene, background, atmosphere, props, lighting, visual logic, and local
decorative elements. Important product pixels, claims, final text, and frame
placement should be handled by deterministic layers whenever possible.

## Two User Modes

### Mode 1: PuHuo Batch Mode

Use when the user wants broad listing coverage, fast output, and low per-SKU
decision cost.

User intent:

- upload many products
- choose one marketplace/style direction
- enter minimal product parameters
- get usable main-card or small suite outputs quickly
- accept template similarity if product fidelity and selling-point clarity are
  good enough

Default output:

- 1-3 images per SKU
- main marketplace card first
- optional feature/callout card
- low iteration count
- no PSD by default
- deterministic text overlay only when text is needed

Recommended defaults:

- marketplace profile: Ozon/WB or Amazon-compatible
- image direction: high-conversion main card
- copy density: low to medium
- style intensity: medium
- product fidelity: strict
- review depth: automated QA plus contact sheet
- repair budget: one retry

PuHuo should not expose too many controls. The user should mainly choose:

1. marketplace / target channel
2. visual direction
3. language
4. key selling points
5. output count

### Mode 2: JingPu Premium Mode

Use when the user wants a polished listing, stronger differentiation, and human
review between iterations.

User intent:

- upload one important product or a small SKU set
- provide listing text, competitor references, and brand preferences
- choose a full suite direction
- inspect candidate routes before finalizing
- get a more coherent set of hero, selling-point, proof, use-case, package, and
  parameter images

Default output:

- 5-8 image suite
- multiple direction candidates for the first hero/main image
- stronger ProductTruthPack and CopyPlan
- human review checkpoint after candidate contact sheet
- deterministic text and badge overlay
- optional PSD/layered handoff
- optional frame/brand-kit composition after direction is accepted

Recommended defaults:

- marketplace profile: selected by user
- image direction: suite strategy, not one card only
- copy density: slot-specific
- style intensity: medium to high
- product fidelity: strictest
- review depth: QA report plus human selection
- repair budget: two retries with typed repair plans

JingPu should expose more controls:

1. marketplace and audience
2. product title and source truth
3. safe claims and forbidden claims
4. visual route candidates
5. slot plan
6. competitor/reference images
7. brand style pack
8. language and text tone
9. export format

## Direction Selection

The user should not choose a raw renderer or model first. They should choose a
business-facing direction:

- `ozon_wb_main_card`: high-density marketplace tile, large product, short
  badges, strong contrast.
- `amazon_buyer_question_suite`: 5-8 images organized by buyer questions.
- `premium_detail_proof`: detail, material, parameter, and close-up proof.
- `scene_lifestyle`: usage scene or ownership scene, product remains anchored.
- `package_trust`: what is included, accessories, scale, and trust reduction.
- `brand_frame_composite`: accepted generated scene plus brand/frame treatment.

The renderer can map these directions to TemplateCards, SuiteTemplates, prompt
recipes, and composite modules internally.

## Parameter Contract

The UI can send a single `GenerationIntent` object to the workflow runner:

```json
{
  "mode": "puhuo_batch",
  "marketplace_profile": "ozon_wb",
  "language": "en",
  "direction": "ozon_wb_main_card",
  "sku_scope": "single",
  "output_count": 3,
  "style_intensity": "medium",
  "copy_density": "medium",
  "product_fidelity": "strict",
  "use_frame": "optional_after_acceptance",
  "text_strategy": "deterministic_overlay",
  "repair_budget": 1,
  "export_targets": ["png", "contact_sheet", "run_report"]
}
```

For JingPu:

```json
{
  "mode": "jingpu_premium",
  "marketplace_profile": "amazon_ozon_hybrid",
  "language": "en",
  "direction": "amazon_buyer_question_suite",
  "sku_scope": "single",
  "suite_size": 7,
  "style_intensity": "high",
  "copy_density": "slot_specific",
  "product_fidelity": "strictest",
  "use_frame": "after_route_selection",
  "text_strategy": "deterministic_overlay_or_psd",
  "repair_budget": 2,
  "requires_human_checkpoint": true,
  "export_targets": ["png", "contact_sheet", "run_report", "qa_report", "psd_optional"]
}
```

## Generation Stages

### Stage 1: Intake

Inputs:

- product images
- optional listing text
- optional reference images
- optional brand/frame assets
- mode and intent parameters

Outputs:

- `inputs/product_images/*`
- `product_truth_pack.json`
- `generation_intent.json`

### Stage 2: Product Truth

The system extracts and confirms:

- category
- immutable visual traits
- product parts and labels
- safe claims
- forbidden changes
- allowed visual changes
- selling points and visual translations

This powers both PuHuo and JingPu. PuHuo can use a short auto-generated truth
pack. JingPu should ask for confirmation when important claims are uncertain.

### Stage 3: Direction Planning

The runner maps `GenerationIntent.direction` to:

- SuiteTemplate or TemplateCard
- prompt recipe
- text strategy
- composite strategy
- QA scorecard

The output is:

- `shot_plan.json`
- `template_params.json`
- `copy_plan.json`

### Stage 4: Generate First

This stage should push the image generation work, not the frame.

Preferred generation routes:

- background-only generation, then product composite
- reference img2img for commercial scene exploration
- template-driven card render, then optional enhancement
- slot-specific scene generation for suite images

Generation should avoid final text when the text matters. It should reserve
zones for headline, badges, proof cards, and product placement.

### Stage 5: Deterministic Composite

This stage combines:

- preserved product or cutout
- generated background/scene
- deterministic headline and badges
- optional frame/brand treatment
- product shadow/glow
- export crop and marketplace canvas

FrameKit enters here only after the image direction has passed an early visual
check.

### Stage 6: QA and Repair

Minimum QA:

- product is recognizable and not deformed
- product occupies the intended visual weight
- generated background does not fight the product
- selling point is visible in thumbnail
- text zones are readable
- claims are supported by the ProductTruthPack
- frame/brand treatment does not cover the product

Repair should be typed:

- `regenerate_background`
- `adjust_product_scale`
- `reduce_background_clutter`
- `rewrite_badge_copy`
- `move_text_zone`
- `disable_frame_for_this_candidate`
- `rerender_composite`

## Run Folder Shape

Each run should be inspectable by the user:

```text
experiments/YYYYMMDD_generation_modes/<run_id>/
  inputs/
    product_images/
    references/
    generation_intent.json
    product_truth_pack.json
  planning/
    shot_plan.json
    template_params.json
    copy_plan.json
  generation_requests/
    *.json
    *.prompt.md
  generated/
    backgrounds/
    img2img_candidates/
  composites/
    *.png
  qa/
    qa_report.json
    repair_plan.json
  contact_sheet.png
  run_report.md
```

## Next Prototype Target

Do not keep improving border extraction first. Build a small interaction-driven
prototype:

1. Create a `generation_intent` schema for PuHuo and JingPu.
2. Add one runner that accepts a product image plus `generation_intent.json`.
3. For PuHuo, generate or prepare 3 Ozon/WB-style main-card candidates.
4. For JingPu, prepare a 5-slot suite plan and at least one rendered/composited
   candidate per slot.
5. Use the frame only as an optional final composite layer after the main image
   direction is selected.

The success condition is not that the frame looks better. The success condition
is that a user can upload a product, choose PuHuo or JingPu, enter parameters,
and receive candidates whose generation route, composite route, QA result, and
next repair step are all visible.
