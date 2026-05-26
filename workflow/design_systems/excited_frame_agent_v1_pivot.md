# EXCITED Frame Agent v1 Pivot

Date: 2026-05-22

## Decision

Stop asking one image model to generate the full eMAG/Ozon-style main image,
border, and EXCITED wordmark in one pass.

The stable pipeline should split the image into four controlled layers:

1. Product layer
   - Use the product cutout or source product image as the protected layer.
   - QA target: product geometry, packaging, and visible text must remain intact.

2. Background and frame texture layer
   - Use inpaint/img2img only for masked edge bands, corner treatments, and
     background blending.
   - Prompt must explicitly request no readable brand text and no extra slogans.
   - The model is allowed to create texture, color, shadows, edge rails, and
     small decorative accents only.

3. Brand slot layer
   - Create the top-right brand zone as a design layer, not as model-generated
     text.
   - Height target on 1024 x 1024: 42-72 px.
   - Width target on 1024 x 1024: 200-330 px.
   - The slot may be a dark tech rail, teal eMAG strip, ornamental tab, or
     text-only rail depending on product category.

4. EXCITED wordmark layer
   - Render as editable vector/text. Do not rely on model text generation.
   - Font family candidates from local system:
     - DIN Condensed Bold
     - Avenir Next Condensed
     - Impact
     - Arial Narrow Bold Italic
   - Effects are controlled in design code/PSD/OpenDesign:
     - italic/skew
     - white/cyan fill
     - dark stroke
     - 1-2 px glow/shadow
     - optional magenta/cyan underline

## Rejected Routes

### Pure Pillow Composition

Rejected. It produces a pasted, low-end look and cannot solve edge blending,
lighting, or material texture.

### Pure Prompt/Img2Img

Rejected for production. It can create decent border texture, but text control
is unstable. In tests it generated extra words, corrupted brand text, and wrote
unwanted slogans inside the top-right slot.

### Large Vector Logo Overlay

Rejected. It is stable for spelling but visually becomes a sticker when it is
too large or when it ignores the generated frame geometry.

## Current Best Direction

Use AI only where it is strong:

- thin frame texture
- category-matched decorative edge details
- background/frame color blending
- empty brand slot surface

Use deterministic design layers where precision is required:

- exact `EXCITED` spelling
- logo size
- logo position
- border thickness
- marketplace-safe output size

## Agent Flow

1. Input product image and mock/product metadata.
2. Pick a frame archetype from the 41-reference library:
   - teal clean strip
   - black/cyan/purple tech rail
   - ornamental/floral/puzzle rail
   - gold premium thin border
   - text-only brand rail
3. Generate masks:
   - product protection mask
   - edge/frame mask
   - optional background enhancement mask
   - brand slot mask
4. Run inpaint on frame/background only.
5. Apply vector brand slot and EXCITED wordmark from a template.
6. Run QA:
   - product body changed: reject
   - extra generated text in frame: reject or cover with design slot
   - brand spelling not exact: reject
   - slot height > 8% of image: reject
   - frame too thick or poster-like: reject
   - right-top slot collides with product/RGB badge/title: reject

## Artifacts From This Pivot

- `experiments/20260522_fal_two_stage_brand_slot/two_stage_result_sheet.jpg`
  shows why model-generated text is rejected.
- `experiments/20260522_fal_two_stage_brand_slot/outputs/tech_stage1_vector_slot_D.png`
  shows the smaller vector-locked slot direction. It is a structure test, not a
  final approved design.
- `experiments/20260522_logo_ratio_analysis/logo_crops_sheet.jpg`
  is the quick crop board for top-right/top-band reference review.

