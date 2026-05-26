# Ecommerce Image Suite Next Actions

Date: 2026-05-05

## Current Verdict

The project can proceed now. Waiting for the user's full brand/template package
is not necessary.

What is ready:

- TemplateCard library
- prompt recipe library
- suite plan
- scorecard
- text copy plan schema
- PSD boundary contract
- OpenDesign-inspired Skill skeleton
- next-session prompts
- single-slot prompt compiler
- suite runner for generation request preparation
- text copy seed generation per slot

What is missing for production quality:

- real brand-frame assets
- clean PSD templates
- multiple product angles and cutouts
- listing/manufacturer truth sources
- competitor keyword bank
- automated prompt compiler and run orchestrator

## Immediate Implementation Sequence

1. Add template override and model routing to `scripts/run_ecommerce_suite.mjs`.
2. Add a visual scoring runner for generated candidate images.
3. Add PSD/HTML/Pillow overlay scaffolding for deterministic text using
   `text_copy_plan.seed.json`.
4. Add brand-frame support when assets arrive.
5. Add competitor keyword extraction later.
6. Convert accepted human review notes into next-run constraints.

## Current Smoke Test

The suite runner has prepared a 5-slot backpack suite at:

`experiments/20260505_suite_runner_smoke`

Prepared slots:

- search-stop hero: `HeroCleanCenterCard`
- primary selling point: `FeatureRightTextCard`
- proof detail: `IndustrialDarkDetailCard`
- lifestyle scene: `HeroLifestyleSceneCard`
- comparison/before-after: `BeforeAfterSplitCard`

This smoke test did not call an image model. It only produced generation
requests and scoring placeholders.

## Parallel Research Track

Do not block implementation on research. Run it in parallel.

Research targets:

- OpenDesign upstream projects
- image-to-image reference workflows
- ControlNet / reference-control methods
- PSD automation and manifest formats
- ecommerce creative scoring
- marketplace listing keyword extraction

## OpenDesign Decision

Use OpenDesign as a sub-framework reference, not as the product core.

Keep:

- `SKILL.md` convention
- `DESIGN.md` visual system
- `assets/` and `references/` pattern
- critique and repair loop
- parameter/tweak idea

Do not import blindly:

- generic web prototype skills
- dashboard/mobile app skills
- deck/PPT workflow
- full daemon/runtime
- generic design systems without ecommerce adaptation

## User Material Intake Checklist

When the user sends more materials, classify each file:

- `brand_reference`: brand frame, logo, color, border style
- `template_reference`: clean template, PSD, layout example
- `methodology_reference`: phone screenshot, article, prompt tutorial
- `product_source`: white-background product image, cutout, angle shot
- `truth_source`: listing copy, factory ad, purchase page, spec sheet
- `competitor_reference`: competitor image/listing/keyword source

Phone screenshots should usually be `methodology_reference`, not direct image
templates.
