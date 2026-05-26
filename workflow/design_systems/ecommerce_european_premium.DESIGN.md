# Ecommerce European Premium

> Category: Marketplace Ecommerce
> A restrained European/Ozon/eMAG visual direction for high-conversion product images: practical, clean, trust-forward, and product-first.

## Visual Theme & Atmosphere

Commercial, concrete, and proof-driven. The product is always the first thing the viewer sees. Backgrounds are clean white, cool gray, muted workshop dark, or realistic usage scenes. Avoid social-media clutter, ornate decorations, and over-stylized AI atmospheres.

Premium does not mean always dark, always bordered, or always card-based. The stronger ecommerce references use controlled emptiness, one dominant visual idea, and product-scene integration. A page should breathe: dense banner, clean white copy, cropped proof, then a fact board.

## Color Palette & Roles

- `--bg`: `#f6f7f8` cool off-white
- `--surface`: `#ffffff` card and text-panel surface
- `--fg`: `#17202a` primary text
- `--muted`: `#667085` secondary text
- `--border`: `#d8dee6` dividers and card lines
- `--accent`: `#1f6feb` blue proof/action accent
- `--accent-2`: `#f5b000` yellow numeric badge accent
- `--dark`: `#14171c` industrial background
- `--success`: `#17a34a` trust/check accent

Accent budget:

- main image: 1 large numeric badge + 1 secondary accent strip maximum
- selling-point image: 2-4 badges/icons maximum
- detail board: yellow/blue linework only, no rainbow palette

## Typography Rules

- Final production text should be rendered by PSD/HTML/Pillow, not by the image model.
- Use a neutral geometric sans for English/Roman text.
- Use tabular numerals for wattage, PSI, quantity, size, and warranty.
- Use short phrases, not paragraphs.
- Product badges should be 1-3 words or a number + unit.

## Component Stylings

- Numeric badge: high contrast, large, usually top-left or top-right.
- Proof card: white surface, 6-8px radius, light border, icon + one short claim.
- Callout line: thin, angular or radial, connects to a real visible product part.
- Detail inset: crop from real product when possible, not model-invented.
- Bottom strip: included items, warranty, package quantity, compatibility.

## Layout Principles

- Main image product weight: 55-70%.
- Selling-point image product weight: 40-60%.
- Detail/comparison image product weight: 30-55%.
- Max 3 visual focus groups per image.
- Use clear reading order: product -> number/proof -> detail/scene.
- Every image in a suite must answer one different buyer question.

Detail-page rhythm:

- Do not stack two heavy dark modules consecutively.
- Do not use small cards in every module. Cards are for specs, manual steps, comparisons, and first-screen anchors.
- After a large visual banner, use a short clean text block or cropped proof detail before the next large image.
- Use source image crops when they prove a point better than a full image.
- Avoid repeating the same layout pattern more than twice in one page.
- Alternate alignment deliberately: left text / right product, centered statement, full-width crop, then simple table.

Banner hierarchy:

- One big idea per banner.
- One product or product cluster, not many unrelated floating objects.
- One headline zone and at most three proof chips.
- Leave a clean text zone if final text is added later.
- If the product scene already tells the story, do not add extra mini boxes just for decoration.

## Depth & Elevation

- Use realistic contact shadows under products.
- Industrial images may use dark reflective floors, but reflections must not obscure product details.
- Avoid floating products unless the category benefits from high-energy tech advertising.

## Do's and Don'ts

Do:

- keep product outline exact
- use real product details as proof
- reserve editable text zones
- use icons for trust and features
- keep palette consistent across the suite
- generate scene/background separately when product fidelity matters
- add deterministic text, icons, and specs after generation
- treat reference screenshots as layout logic, not as direct production assets

Don't:

- invent specifications
- add ports, cables, wheels, buttons, or accessories
- use long generated text
- flood image with badges
- copy phone screenshot UI
- use default purple-blue AI gradients
- add a second full product image immediately after a product-heavy banner unless it answers a new buyer question
- add step-number overlays unless the module is actually a usage/manual sequence
- rely on image models for legal, warranty, specification, or review text

## Responsive Behavior

Marketplace images must remain readable as small thumbnails. Product silhouette and largest badge should be legible at 160px wide.

## Agent Prompt Guide

Use this order:

1. ProductTruthPack
2. SuitePlan slot
3. TemplateCard
4. Marketplace scale
5. Keep/change constraints
6. Text-zone policy
7. Negative constraints
8. Scorecard and repair loop

## Banner Route Guide

Default to `AI background + deterministic composite`.

- Use `pure_composite` for spec boards, QA, review, and manual modules.
- Use `pure_ai_generation` only for exploration or when final text/product fidelity is non-critical.
- Use `ai_background_plus_composite` for premium hero banners, product-scene banners, and brand atmosphere banners.

Always specify:

- product slot
- text safe zone
- reference image role
- no duplicate product
- no generated text unless explicitly testing model text
- exact final text handled by deterministic overlay
