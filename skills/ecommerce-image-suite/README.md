# Ecommerce Image Suite Skill

This is the project-specific skill for AI ecommerce image production in
`/Users/cc/Desktop/photo_show`.

It is inspired by OpenDesign's `SKILL.md + DESIGN.md + craft + critique`
protocol, but it is not a direct OpenDesign import. The center of this system is
commercial product truth and marketplace conversion.

## Current Status

MVP skeleton is ready.

The first automation layer is also available:

- `scripts/compile_ecommerce_prompt.mjs` compiles one slot.
- `scripts/run_ecommerce_suite.mjs` expands one SKU into a 1-8 image suite and
  writes generation requests plus scoring placeholders.
- Each slot now also writes `text_copy_plan.seed.json` for headline, badge,
  callout, font, placement, and overlay planning.

Existing project assets used by this skill:

- `workflow/template_cards/*.json`
- `workflow/prompt_recipes/*.md`
- `workflow/schemas/*.json`
- `workflow/suite_plans/ecommerce_5_to_8_suite_plan.json`
- `workflow/scorecards/ecommerce_multimodel_scorecard.json`
- `workflow/design_systems/ecommerce_european_premium.DESIGN.md`
- `workflow/psd_templates/psd_template_contract.md`

Prior validation assets:

- `experiments/20260504_img2img_validation/final_validation_report.md`
- `experiments/20260504_img2img_validation/runs/*`
- `experiments/20260504_backpack_mvp/*`

## What This Skill Does

It turns product inputs into a controlled generation run:

```text
ProductTruthPack
  -> SellingPointPlan
  -> SuitePlan
  -> TemplateCard selection
  -> PromptRecipe compilation
  -> image generation / generation request
  -> Scorecard review
  -> repair prompt
  -> optional PSD/text overlay
  -> human review writeback
```

## What It Does Not Do Yet

- It does not yet run a complete automated generation pipeline by itself.
- It does not yet include a prompt compiler script.
- It does not yet scrape competitors.
- It does not yet produce native editable Photoshop text layers.
- It does not yet have the user's final brand-frame assets.

## OpenDesign Mapping

| OpenDesign Concept | Local Equivalent |
| --- | --- |
| `SKILL.md` | `skills/ecommerce-image-suite/SKILL.md` |
| `DESIGN.md` | `workflow/design_systems/ecommerce_european_premium.DESIGN.md` |
| `craft/` | `skills/ecommerce-image-suite/references/*.md` plus future ecommerce craft rules |
| prompt templates | `workflow/template_cards/*.json` + `workflow/prompt_recipes/*.md` |
| critique skill | `workflow/scorecards/ecommerce_multimodel_scorecard.json` |
| tweaks parameters | product weight, text policy, information density, style direction |
| artifact folder | `experiments/<date>_<sku_or_topic>/` |

## Next Build Tasks

1. Extend the suite runner:
   - add explicit template override per slot
   - add marketplace-specific template preference
   - add model/provider routing fields
   - add optional clean template/reference image per slot

2. Add validation for existing TemplateCards:
   - check fields against `workflow/schemas/template_card.schema.json`
   - report missing fields and naming mismatches

3. Add one SKU scoring runner:
   - accept generated candidate image paths
   - create score prompts for each reviewer role
   - write score JSON and repair prompt

4. Add brand-frame support after user provides assets:
   - `workflow/brand_frames/<brand_frame_id>.json`
   - optional PSD/HTML/Pillow overlay template

5. Add competitor keyword extraction later:
   - input: listing URLs, screenshots, or scraped text
   - output: keyword bank and allowed claims

## Recommended First Real Run

Use a simple product with visible structure and limited compliance risk.

Good candidates:

- backpack or bag
- phone stand
- cable/accessory kit
- tire inflator or tool product

Avoid first:

- cosmetics with medical/skin claims
- food/supplement claims
- products where exact certification text matters

## Script Usage

Compile a single slot:

```sh
node scripts/compile_ecommerce_prompt.mjs \
  --truth experiments/20260505_ecommerce_skill_smoke/inputs/pink_backpack.truth.json \
  --template workflow/template_cards/HeroCleanCenterCard.json \
  --out experiments/example_slot_01 \
  --sku pink_backpack \
  --marketplace Amazon \
  --text-policy deterministic_overlay
```

Prepare a 5-image suite:

```sh
node scripts/run_ecommerce_suite.mjs \
  --truth experiments/20260504_img2img_validation/product_truth_packs.json \
  --truth-key pink_backpack \
  --sku pink_backpack \
  --marketplace Amazon \
  --slots 5 \
  --product-image experiments/20260504_img2img_validation/runs/01_pink_backpack_main_HeroCleanCenterCard/source_product.jpg \
  --out experiments/20260505_suite_runner_smoke
```

The suite runner does not call an image model yet. It prepares:

- `suite_plan.selected.json`
- `template_selection.json`
- `slot_*/compiled_prompt.md`
- `slot_*/generation_request.json`
- `slot_*/text_copy_plan.seed.json`
- `scorecards/*.score.json`
- `repair_prompts/*.repair_prompt.md`
- `review_log.md`

## Text And Typography

Treat final ecommerce text as deterministic overlay by default.

Image generation should create:

- product-faithful commercial composition
- clean text-safe zones
- badge/callout areas
- background and lighting

Text overlay should create:

- exact headline
- exact badges and numbers
- localized copy
- consistent fonts
- brand frame and logo placement

The seed schema is `workflow/schemas/text_copy_plan.schema.json`. Current slot
outputs use `text_copy_plan.seed.json`; draft copy must be reviewed before
production.

## Brand Asset Intake

When brand materials arrive, save them under:

```text
references/brand/<brand_name>/
  raw/
  selected/
  brand_frame_notes.md
```

Then produce:

```text
workflow/brand_frames/<brand_name>_frame_v1.json
workflow/design_systems/<brand_name>_ecommerce.DESIGN.md
```

Do not use brand screenshots as direct templates unless they are clean crops.
Extract rules first: palette, frame geometry, logo slot, badge style, safe area,
and anti-patterns.
