---
name: ozon-image-production-agent
description: |
  Deep production workflow for OZON/e-commerce main images using the local
  ozon-image-generator README, SKILL, and DESIGN files as one source contract.
  Use when the user wants a product image generated from uploaded product specs
  or a source image through analysis, prompt compilation, deterministic overlay
  planning, image generation, and QA rather than a one-off prompt.
---

# OZON Image Production Agent

This skill wraps the existing Gemini-created `skills/ozon-image-generator/`
documents into a production workflow. Treat these three files as one contract:

1. `skills/ozon-image-generator/README.md` - execution order and universal layout.
2. `skills/ozon-image-generator/SKILL.md` - SOP, product analysis, prompt rules,
   product-fidelity rules, and brand integration.
3. `skills/ozon-image-generator/DESIGN.md` - visual system, typography, badges,
   icon usage, margins, and mobile QA.

If product-specific blueprints exist under `outputs/*_blueprint.md`, read the
matching blueprint too. The blueprint can override generic routing for category,
scene, copy slots, brand shelf, and feature badges.

## Required Workflow

Do not jump directly to image generation. Execute in this order:

1. **Read source contract**
   - Read the three source files above.
   - Read any product blueprint that matches the product or user request.
   - If the user supplied an image, inspect it visually before writing claims.

2. **Analyze the product**
   - Identify product category and silhouette.
   - Extract one primary numeric/click-catch value.
   - Select 2-3 feature badges and 1 trust badge.
   - Choose marketplace archetype and relevant staging background.
   - Separate verified product facts from inferred copy.

3. **Compile generation assets**
   - Generate a base-image prompt with no model-rendered text.
   - Generate an overlay plan for title, numeric badge, feature badges, icons,
     trust seal, brand shelf, connector lines, and safe zones.
   - Generate a QA checklist for 160px legibility, overlap, palette, and text.
   - Prefer running:
     ```bash
     python skills/ozon-image-production-agent/scripts/compile_ozon_production_run.py \
       --product-name "<name>" \
       --product-specs "<facts>" \
       --out outputs/ozon_image_generator/<run_id>
     ```

4. **Generate the base image**
   - Use the current image generation tool available in Codex.
   - Do not claim a specific model such as Imagen unless the tool explicitly
     exposes that model. Say which path was actually used.
   - Prompt for a clean base image with safe zones and no text/logos.

5. **Compose deterministic overlays**
   - Add all text, icons, and badges with code, HTML, PSD, or Pillow layers.
   - Do not rely on the model to spell brand names, Russian/English copy, or
     numeric claims.
   - For EXCITAT tech/gaming products, use the top-right slanted Speed
     Lightning/Shelf wordmark unless the blueprint says otherwise.

6. **QA and repair**
   - Create a 160px thumbnail.
   - Check product silhouette, primary click-catch, no badge/product overlap,
     and 3-color visual budget.
   - Repair once if text is clipped, unsafe, or unreadable.

## Production Rules

- Product fidelity takes priority over style. For high-stakes or SKU-accurate
  work, use a source-product cutout and generate only the background and lighting.
- Background must be category-relevant. Avoid generic dark studio backgrounds
  when the source contract or blueprint provides a real usage scene.
- Keep text short. Main title max 3-4 words per line. Feature badges should be
  icon plus short label.
- Use deterministic overlays for typography, brand marks, icons, badges, and
  connector lines.
- Report final paths for base image, final composite, 160px check, and run spec.

## Output Contract

Each run should produce:

- `analysis.md`
- `base_prompt.txt`
- `overlay_plan.json`
- `qa_checklist.md`
- generated base image
- final composite image
- 160px thumbnail

