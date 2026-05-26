# eMAG Excitat Reference Design System

> Category: eMAG marketplace reference, derived from the 2026-05-21
> `NexusTech / Excitat` vendor sample set. Use as a learning reference and
> template direction, not as copied artwork.

## Positioning

This is not a strict eMAG compliance-white-background system. It is a
marketplace search-card advertising system: high product visibility, repeatable
brand frame, short proof copy, and dense buyer-question coverage.

Our target is to keep the useful structure while improving fidelity, language,
spacing, and claim safety.

## Stable Brand Tokens

- Top-right or corner `Excitat`-style brand signature area.
- Thin full-image border, usually teal, green, orange, blue, or magenta
  depending on category.
- Angled corner wedge or diagonal accent on many cards.
- Product occupies the visual center and usually 45-75% of the square canvas.
- 1-3 high-signal proof badges on the first image.
- Repeated icon circles or small feature badges on support images.
- Bottom or side strip for parameters, package contents, compatibility, or
  included items.

## Palette Families

- `tech_gaming`: black / purple / electric blue / cyan, high glow, strong
  contrast.
- `industrial_tool`: black / graphite / orange / gold, metallic highlights,
  close-up detail panels.
- `green_utility`: white / light gray / green, leaves or airflow motif, safety
  and eco-style badges.
- `baby_home`: white / mint / teal / orange, soft background, rounded icons,
  warm usage scenes.
- `gift_toy`: colorful subject art, orange or black frame, package and contents
  emphasis.
- `coffee_lifestyle`: black / cream / brown / gold, warm cup scene, parameter
  proof badges.

## Layout Families

### Brand Frame Hero

- 1:1 square.
- Brand mark in top-right corner.
- Product large and recognizable at thumbnail size.
- Largest proof point visible within one second.
- Category-specific border and diagonal accent.
- Works for search result click-through, but must be claim-checked.

### Feature Proof Grid

- Product left or center.
- 3-6 icon/proof modules around it.
- Short labels only.
- Best for appliances, electronic accessories, and tools.

### Detail Proof Card

- Macro detail or cutaway occupies the center.
- Text headline at top.
- Callout line points to a real product part.
- Small locator/full product image when needed.

### Parameter Strip Card

- Product stays visible.
- Bottom/side strip lists wattage, capacity, quantity, dimensions, compatibility,
  or package count.
- Best for eMAG categories where attributes affect filtering.

### Package Contents Card

- Shows all included items with labels.
- Reduces return risk.
- Must match listing facts exactly.

### Use Case / Scenario Grid

- 2x2 or 3x2 scene panels.
- One buyer scenario per panel.
- Useful for compatibility, environments, or age/use-case segmentation.

## What To Improve Beyond The Sample

- Fewer text blocks per image; keep one image to one buyer question.
- Use deterministic overlays for final text; do not rely on generated text.
- Use Romanian copy when targeting Romanian eMAG listings.
- Normalize typography: one heading style, one numeric badge style, one icon
  style per suite.
- Avoid duplicate first images and redundant benefit cards.
- Preserve product truth: no invented ports, buttons, accessories, claims, or
  certifications.
- Make detail crops come from the real product image or approved source.
- Keep frame/brand tokens consistent without copying the original brand mark.

## Generation Guidance

Use this order:

1. ProductTruthPack with listing facts, source images, included items, and
   forbidden claims.
2. `emag_excitat_reference_6_suite` or a category-specific derivative.
3. Brand frame tokens from this design system, but replace the logo and palette
   with our own brand style.
4. Image model for product-preserving background, lighting, and scene support.
5. Deterministic renderer for text, badges, icons, and border frame.
6. QA checks for product fidelity, copy correctness, platform fit, and thumbnail
   readability.

## QA Rules

- At 160px width, product silhouette and the largest proof point must remain
  readable.
- Main gallery should be square and export at 1500x1500 when possible.
- Text density limit:
  - hero: 1 large proof + 1-2 short labels
  - feature card: 3-5 short modules
  - detail card: 1 headline + 2-4 labels
  - package card: labels only, no paragraph
- Every suite must contain distinct buyer questions, not repeated visual claims.
- Any number, certification, compatibility, or package count must come from
  ProductTruthPack.
