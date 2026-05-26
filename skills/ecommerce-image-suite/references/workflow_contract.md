# Workflow Contract

The ecommerce image workflow is a file-backed production loop:

```text
Product images + Product info + Marketplace target
  -> ProductTruthPack
  -> SellingPointPlan
  -> SuitePlan
  -> TemplateCard selection
  -> PromptRecipe compilation
  -> image generation or generation request
  -> visual scoring
  -> repair prompt
  -> optional PSD/text overlay
  -> human review writeback
```

## Inputs

Minimum viable input:

- one clear product image
- product category
- target marketplace
- intended image role

Production input:

- multiple white-background product angles
- cutout PNG if available
- listing/manufacturer/source copy
- competitor keywords and claims
- brand references
- clean template images or PSD templates
- forbidden claims and compliance constraints

## Non-Negotiables

- The product must remain the same SKU.
- Product truth beats template attractiveness.
- Long text belongs in deterministic overlay, not model-rendered pixels.
- Each image answers one buyer question.
- A suite must progress logically from click, to interest, to proof, to desire,
  to conversion support.

## Run Folder Convention

Use this shape for new experiments:

```text
experiments/<date>_<sku_or_topic>/
  inputs/
  product_truth_pack.json
  selling_point_plan.json
  suite_plan.json
  template_selection.json
  compiled_prompts/
  candidates/
  scorecards/
  repair_prompts/
  psd/
  review_log.md
  run_report.md
```

## Decision Gates

Gate 1: ProductTruthPack complete enough.

- If not, ask for missing facts or mark risky claims as blocked.

Gate 2: Template selected for the correct buyer question.

- If not, create or adapt a TemplateCard.

Gate 3: Generated image passes product truth.

- If not, repair or reject. Do not continue to text overlay.

Gate 4: Text policy safe.

- If final text matters, use PSD/HTML/Pillow overlay.

Gate 5: Human review.

- Human feedback must be written back as concrete next-run constraints.
