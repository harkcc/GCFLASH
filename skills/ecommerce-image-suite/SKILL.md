---
name: ecommerce-image-suite
description: |
  Build and review marketplace ecommerce image suites from product images,
  product facts, competitor keywords, TemplateCards, prompt recipes, optional
  PSD templates, and multi-model scoring. Use for Amazon/Ozon/Rakuten/eMAG
  main images, selling-point images, lifestyle scenes, comparison images,
  detail boards, and full 5-8 image suites.
triggers:
  - "ecommerce image suite"
  - "电商套图"
  - "商品详情图"
  - "主图"
  - "卖点图"
  - "PSD模板"
  - "TemplateCard"
  - "图生图"
od:
  mode: image
  scenario: marketing
  preview:
    type: markdown
    entry: run_report.md
  design_system:
    requires: true
    sections: [color, typography, layout, components, prompt]
  craft:
    requires: [color, anti-ai-slop]
  inputs:
    - name: product_images
      type: file[]
      required: true
    - name: product_info
      type: markdown
      required: false
    - name: marketplace
      type: enum
      values: [Amazon, Ozon, Rakuten, eMAG, Walmart, Shopify, Other]
      default: Amazon
    - name: suite_size
      type: integer
      default: 5
      min: 1
      max: 8
    - name: brand_reference
      type: file[]
      required: false
    - name: psd_template
      type: file
      required: false
  parameters:
    - name: product_weight
      type: enum
      values: [compact, balanced, dominant]
      default: dominant
    - name: text_policy
      type: enum
      values: [no_text, reserve_text_zone, deterministic_overlay, model_exact_text]
      default: deterministic_overlay
    - name: information_density
      type: enum
      values: [low, medium, high]
      default: medium
    - name: style_direction
      type: enum
      values: [european_premium, ozon_high_conversion, amazon_clean, rakuten_trust, industrial_dark, lifestyle_soft]
      default: european_premium
outputs:
  primary: run_report.md
  secondary:
    - product_truth_pack.json
    - selling_point_plan.json
    - text_copy_plan.json
    - suite_plan.json
    - compiled_prompts/
    - scorecards/
    - review_log.md
---

# Ecommerce Image Suite Skill

This skill is the project-specific production workflow for AI ecommerce images.
It borrows OpenDesign's file-backed skill pattern, but the commercial logic is
specific to marketplace product images.

## Required Local Assets

Read these files before planning a run:

- `workflow/agent_flow/ecommerce_image_agent_v0.md`
- `workflow/design_systems/ecommerce_european_premium.DESIGN.md`
- `workflow/suite_plans/ecommerce_5_to_8_suite_plan.json`
- `workflow/schemas/product_truth_pack.schema.json`
- `workflow/schemas/template_card.schema.json`
- `workflow/schemas/text_copy_plan.schema.json`
- `workflow/scorecards/ecommerce_multimodel_scorecard.json`
- all matching files under `workflow/template_cards/`
- relevant prompt recipes under `workflow/prompt_recipes/`
- this skill's `references/*.md`

Do not treat phone screenshots as clean templates. Use them only to extract
methodology, layout logic, scoring rules, and prompt-writing patterns.

For the newer three-Scale prototype, also read
`references/scale_template_validation.md`. It treats Image2 as one candidate
generator, not the fixed production route, and validates ScaleBaseline,
SuiteTemplate, BrandStylePack, TemplateCard, QAReport, and typed RepairPlan
artifacts before model-specific generation.

## Core Contract

Never start from a beautiful scene alone. Start from product truth.

The run order is:

1. Build `ProductTruthPack`.
2. Build `SellingPointPlan`.
3. Build `TextCopyPlan` for headlines, badges, callouts, and overlay policy.
4. Select the 5-8 suite slots.
5. Match one `TemplateCard` per slot.
6. Compile model-specific prompts.
7. Generate candidates or prepare generation requests.
8. Score with commercial, product-truth, and layout/text reviewer roles.
9. Repair failed dimensions only.
10. Use PSD/HTML/Pillow overlay when final text, localization, or editability matters.
11. Write human review findings back into `review_log.md`.

## Product Truth Rules

- Preserve visible product geometry, colors, materials, logos, labels, ports,
  buttons, wheels, connectors, handles, and included parts.
- Claims must come from listing, manufacturer copy, or user-provided facts.
- Unsupported claims can be framed as visual benefits only if they avoid
  numbers, certifications, medical claims, safety guarantees, or warranty terms.
- If product facts are weak, use generic visual language and reserve risky
  copy for human approval.

## Template Matching Rules

Choose templates by the buyer question, not by visual taste alone.

- Slot 1: click-stop hero.
- Slot 2: pain-solution or primary selling point.
- Slot 3: proof, detail, material, or trust.
- Slot 4: lifestyle or ownership scene.
- Slot 5: comparison or before/after.
- Slot 6: package/trust/included items.
- Slot 7: dense platform-style attachment.
- Slot 8: white-background algorithm ticket.

If no template fits, create a new `TemplateCard` first. Do not force a mismatched
template just because it looks attractive.

## Prompt Compilation Rules

Every prompt must explicitly separate:

- `KEEP`: product identity and immutable details.
- `CHANGE`: background, lighting, scene, camera, props, composition.
- `TEXT`: no text, reserved zones, exact text, or deterministic overlay.
- `COPY`: headline, badges, callouts, footer text, and whether each item is locked.
- `LAYOUT`: product weight, product zone, badge zones, inset zones.
- `STYLE`: design system, marketplace tone, color budget, lighting.
- `NEGATIVE`: forbidden product changes, invented claims, clutter, fake text.

For image-to-image runs, explain the role of each reference image:

- product reference: preserve identity
- template reference: preserve layout logic only
- brand reference: extract frame/palette/badge style only
- scene reference: transfer mood/camera/background only

## PSD Boundary

Use PSD as a control and delivery layer, not as the entire generation strategy.

Use PSD when:

- final English/Russian/Japanese text must be accurate
- the user needs Photoshop/Photopea editability
- brand frame, badges, text zones, or product placement must be repeatable
- imagegen produces a strong background/composition but weak text

Do not use PSD as the default during early visual exploration. First test the
prompt/template direction, then package the winning layout into PSD.

## Text And Font Boundary

Do not rely on image generation for production typography. For final ecommerce
copy, create a `TextCopyPlan` and render text with PSD/HTML/Pillow after the
image model creates the composition.

Use model text only when:

- the text is short and exact
- it is not legally/commercially critical
- a reviewer will inspect it before use

Text layout must specify:

- copy source: user approved, listing, manufacturer, competitor inspired, or draft
- role: headline, badge, callout, proof, footer, inset label
- placement and safe area
- maximum lines and characters
- font family/weight/case
- overlay requirement
- translation requirement

## Score And Repair

Use `workflow/scorecards/ecommerce_multimodel_scorecard.json`.

Fail fast if:

- product details changed
- unsupported specs appear
- text is unreadable but intended as final text
- product is not recognizable at thumbnail size
- the image answers the wrong buyer question

Repair prompts must repeat product invariants and modify only failed dimensions.
Do not rewrite the whole prompt unless the ProductTruthPack was wrong.

## Output Format

Each run should create a run folder with:

- `product_truth_pack.json`
- `selling_point_plan.json`
- `text_copy_plan.json`
- `suite_plan.json`
- `template_selection.json`
- `compiled_prompts/<slot>.md`
- `generation_request.json`
- generated candidate images when available
- `scorecards/<slot>.json`
- `repair_prompts/<slot>.md`
- `review_log.md`
- optional `psd_manifest.json` and PSD preview

End every run with a short verdict:

- what is usable now
- what needs repair
- where PSD/overlay is required
- what new brand/template facts should be collected next
