# Scale Template Validation Prototype

Date: 2026-05-17

This prototype implements the new three-Scale validation plan as a file-backed
runner. It deliberately avoids making the old route (`Image2 + keywords + simple
PIL/HTML overlay`) the default production path.

## What It Validates

The prototype validates the artifact chain:

```text
Product image
  -> ProductTruthPack
  -> ScaleBaseline
  -> SuiteTemplate
  -> TemplateCard mapping
  -> BrandStylePack / font system
  -> ShotPlan + TemplateParams + CopyPlan
  -> candidate render / generation request
  -> QAReport
  -> typed RepairPlan
  -> contact sheet and run report
```

It does not claim that the local `template_render_mvp` images are final
commercial-grade artwork. The rendered images are structural candidates used to
test whether template parameters, font rules, buyer questions, and QA routing are
carried correctly before using Image2, ComfyUI, Fabric, PSD, or another renderer.

## Implemented Scales

### Scale A: Nexscope/Amazon 7 Image Strategy

Files:

- `workflow/scale_baselines/scale_a_nexscope_amazon_7.json`
- `workflow/suite_templates/amazon_nexscope_7_suite.json`

Test product:

- `pink_backpack`

Validated slots:

- main image click
- core benefit infographic
- size/scale reference
- show everything / packaging logic
- detail zoom
- lifestyle use case
- objection/comparison

### Scale B: Ozon/WB Template Adaptation

Files:

- `workflow/scale_baselines/scale_b_ozon_wb_template_adaptation.json`
- `workflow/suite_templates/ozon_wb_template_5_suite.json`

Test product:

- `portable_tire_inflator`

Validated logic:

- 3:4 card canvas
- large product ratio
- short badges
- high-conversion main-card structure
- template adaptation rather than free-form generation

### Scale C: Brand Shoot Kit QA/Reroll Route

Files:

- `workflow/scale_baselines/scale_c_brandshootkit_qa_reroll.json`
- `workflow/suite_templates/brandshootkit_route_comparison_suite.json`

Test product:

- `usb_cable_accessory_set`

Validated route comparison:

- legacy loose Image2 keyword route
- template-reverse route
- preserve-first composite route

Scale C intentionally fails the legacy route to prove that QA returns typed
repair actions instead of generic regenerate advice.

## Three Template Product Types

Template product catalog:

- `workflow/template_products/template_product_catalog.json`

Supported template products:

- `single_image_template`: one good image reverse-engineered into layout, product zone, text zone, badge, typography, and QA parameters.
- `suite_template`: a full image sequence with slot order, buyer question, image job, TemplateCard, and copy density.
- `psd_template`: a layered control/delivery template with product slot, text layers, badge layers, brand frame, and export targets.

## How To Run

```bash
cd /Users/cc/Desktop/photo_show
python3 scripts/run_scale_template_validation.py
```

Default output:

```text
experiments/20260517_scale_template_validation/
```

Main report:

```text
experiments/20260517_scale_template_validation/scale_comparison_report.md
```

Each run folder contains:

- `inputs/product_truth_pack.json`
- `shot_plan.json`
- `template_params.json`
- `copy_plan.json`
- `generation_requests/*.generation_request.json`
- `candidates/*.png`
- `manifests/*.manifest.json`
- `qa/qa_report.json`
- `repair_plan.json`
- `contact_sheet.png`
- `run_report.md`

## Current Prototype Limits

- The local renderer is intentionally simple. It validates structure, not final design taste.
- Product cutout is heuristic. Production should use a real mask/cutout pipeline.
- Font rendering is currently local system font based. Production should use a real font registry and Fabric/PSD/HTML renderer.
- Image2/ComfyUI routes are prepared as generation requests and route metadata, not called by this runner.
- Ozon/WB cards still need stronger visual polish after user template examples arrive.

## Next Upgrade

When user-provided brand requirements and collected template images arrive:

1. Add each good image as a `single_image_template` extraction.
2. Add complete good galleries as `suite_template` variants.
3. Add PSD/Fabric templates as `psd_template` manifests.
4. Re-run this same script and compare Scale A/B/C scores before making UI or platform integration decisions.

