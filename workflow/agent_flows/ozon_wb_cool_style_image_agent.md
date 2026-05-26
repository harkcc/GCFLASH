# Ozon/WB Cool-Style Product Image Agent

This flow is for high-impact marketplace cards where the target is closer to
Ozon/Wildberries visual selling images than clean eMAG catalog cards.

## Target

Generate a 3:4 product card with:

- large preserved product cutout
- generated category-specific atmosphere and props
- strong brand frame
- short art-text headline
- 2-4 proof badges
- deterministic final copy and claims

The generator should be used for scene, lighting, energy, product-related
motifs, and background only. The real product and marketplace text stay locked
in compositing layers.

## Product Truth Pack

Minimum fields:

- product title
- product category
- visible source image
- verified specs and safe claims
- forbidden claims
- marketplace profile
- target language

For SSD example:

- category motifs: circuit traces, speed light, chip geometry, SATA connector
- safe claims: 1TB, SATA III 6Gb/s, 535 MB/s read speed if product fact exists
- avoid: fake warranty, fake certifications, fake accessories

## Generation Stage

Use an image model for background-only prompts.

Prompt rules:

- no product
- no package
- no logo
- no readable text
- no numbers
- reserve clean product stage
- reserve badge and headline zones
- use marketplace thumbnail contrast
- include category motifs

Current implementation:

- `scripts/fal_generate_ozon_backgrounds.mjs`
- model: `fal-ai/flux-pro/v1.1`
- output: two 3:4 backgrounds per bounded repair loop

## Composite Stage

Use deterministic rendering for:

- real product cutout
- product glow and shadow
- outer frame and corner shards
- art headline
- numeric badge
- proof badges
- bottom trust strip

Current implementation:

- `scripts/run_ozon_style_agent_generation_mvp.py`
- output run: `experiments/20260521_ozon_style_agent_mvp/sandisk_ssd_flux_composite`

## Repair Loop

Limit the loop to 2-3 passes unless a human approves more spend.

Repair checks:

- product is not cropped or deformed
- product remains the visual center
- headline and badges do not overlap the product label
- text remains short and readable in a marketplace grid
- background is energetic but not so busy that it hides the product
- claims are supported by ProductTruthPack

## Suite Expansion

After the hero card passes, adapt the same route to:

1. feature callout card
2. detail proof card
3. multi-use or compatibility card
4. package/trust card
5. parameter/spec card

Each slot reuses the same product truth and brand style pack, but changes the
background prompt and overlay template.
