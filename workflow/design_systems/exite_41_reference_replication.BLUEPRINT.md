# EXITE 41 Reference Replication Blueprint

Date: 2026-05-22

Purpose: reproduce the visual effect of the 41 Excitat/eMAG reference main
images as a controllable EXITE product-image system. The target is to reproduce
the design mechanism and commercial effect, not to copy source image assets
pixel-for-pixel.

## Current Verdict

The existing EXITE frame cases only reproduce the skeleton:

- 1:1 marketplace canvas
- thin or medium outer border
- top-right slanted brand shelf
- early art-word exploration
- category color variants

They do not yet reproduce the finished reference effect. Missing parts:

- category-specific border families
- product-aware product/border collision handling
- real bottom bands, chips, proof panels, and inset cards
- richer art-word treatment
- paper, floral, technical-line, neon, and ornamental edge details
- per-product composition density

## Non-Negotiable Canvas Rules

- Output canvas: 1200 x 1200 px.
- Product must remain the first visual anchor.
- Outer frame: 18-36 px for most cards, up to 44 px only for gaming/toy poster
  variants.
- Inner product-safe inset: 42-70 px.
- Top-right brand shelf: 132-180 px tall.
- Brand shelf width: 500-650 px.
- Brand wordmark width: 380-520 px.
- Brand wordmark height: 82-145 px.
- Brand angle: slight italic or slanted shelf, normally -4 to -8 degrees.
- Bottom band when used: 90-145 px tall.
- Do not let the brand shelf plus border consume more than 18% of the full
  canvas height unless the image is intentionally a dark poster layout.

## Frame Families To Reproduce

### 1. Teal Paper Sleeve

Reference IDs: 02, 07, 22, 25.

Use for: baby, home appliance, light electronics, compatibility accessories.

Visual formula:

- teal or aqua outer sleeve
- white or very light cyan inner field
- large top-right white EXITE wordmark on teal/black shard
- one small product/category icon near a corner or bottom strip
- bottom title band in teal, cyan, or teal plus black
- optional inset detail circles or compatibility mini grid
- subtle paper texture, very low contrast

Composition:

- main product centered slightly left or centered
- brand shelf floats above product, never collides with product head
- product shadow soft and short
- detail panels live bottom-left, bottom-right, or right side

### 2. Green Botanical / Functional Home

Reference IDs: 05, 16, 27, 38.

Use for: garden, ventilation, household, comfort, food-related appliance.

Visual formula:

- green frame with leaf or plant line pattern
- white inner field
- top-right EXITE mark can be white, yellow, or green-tinted depending on
  contrast
- bottom green metric strip or functional badge row
- small leaf strokes in 1-2 corners, not a full busy wallpaper

Composition:

- product can overlap slightly into the patterned frame
- callouts should be small rounded rectangles or simple metric chips
- bottom strip should carry only short specs, not long copy

### 3. Orange / Red Tool Poster

Reference IDs: 04, 13, 29, 33, 39.

Use for: tools, hardware, safety, security, repair, measurement, accessories.

Visual formula:

- orange, red, or brown-orange top wedge or top band
- black underside behind the EXITE wordmark
- thin orange/red side frame
- black, grey, or orange bottom information band
- diagonal corner strokes, small proof cards, or right-side inset boxes
- stronger shadows than paper sleeve cards

Composition:

- product should sit in a clean white or pale warm field
- small detail boxes can sit along right edge or bottom edge
- use diagonal lines and sharp corners, not rounded cute cards
- title/spec text blocks should feel like tool packaging

### 4. Dark Neon / Tech Poster

Reference IDs: 01, 12, 20, 23, 31, 34, 36.

Use for: gaming, RGB, EV, auto, sci-fi toys, strong electronics.

Visual formula:

- dark interior or dark side panels
- cyan, magenta, purple, red, or electric blue glow
- top-right EXITE mark remains big and readable
- frame can be thicker and more energetic
- bottom spec chips, arcade strip, road strip, or neon badge row
- light streaks or angular shard background behind product

Composition:

- product may sit on a lit stage or dark gradient panel
- preserve a bright product outline or rim light
- use high contrast, but avoid turning every product into the same generic
  cyber frame

### 5. Ornamental Gift / Beauty / Craft

Reference IDs: 15, 19, 26, 28, 30, 32, 40.

Use for: beauty, kids, puzzle, gift, soft goods, decorative products.

Visual formula:

- pink, mint, black-pink, or black-white ornamental border
- white or very soft inner product field
- floral, pearl, bow, puzzle silhouette, or soft icon accents
- EXITE mark can be bubble, serif, or softer angular
- brand may be top-right, bottom-right, or partly integrated into ornament

Composition:

- product can be framed like a gift poster
- decorative border should be visible but not cover the product
- for kids/toy, use bubble type and soft icon accents
- for premium gift, use black/gold or black/white ornamental lines

### 6. Clean Technical Infographic

Reference IDs: 03, 06, 10, 14, 17, 18, 35, 37, 41.

Use for: kits, component sets, appliances with many parameters, accessories
with compatibility claims.

Visual formula:

- border can be secondary; panel layout carries the image
- top-right, top-center, or bottom-right EXITE marker
- geometric corner lines or thin technical strokes
- product grid, accessory inventory, side panel, or right info column
- bottom strip or side module for core parameters

Composition:

- product and accessories can be arranged as a catalog layout
- avoid over-decorating the edge
- use exact alignment, small labels, and modular panels

## Replication Algorithm

1. Classify product into one frame family.
2. Extract product mask and product bounding box from the white-background
   product image.
3. Choose a template layout from the frame family:
   - single hero product
   - product plus bottom detail strip
   - product plus right proof cards
   - product plus accessory grid
   - dark poster stage
4. Compute product-safe area:
   - tall product: center-left, keep top-right shelf shallow
   - wide product: lower center, use top band plus bottom strip
   - dense kit: use clean infographic or orange tool poster
   - dark product: use white inner field or bright rim light
   - white product: use stronger color sleeve and soft grey shadow
5. Generate or render the frame layer separately:
   - outer sleeve
   - inner field
   - corner details
   - top-right brand shelf
   - optional bottom band
   - optional side/detail panels
6. Composite the product above the inner field and below selected foreground
   frame accents.
7. Add category decoration:
   - leaves for botanical
   - diagonal lines for tool
   - neon shards for tech
   - pearls/bows/floral/puzzle accents for gift/beauty
   - technical lines for infographic
8. Add short commercial text only after layout passes:
   - max 1 title line on main image
   - max 3-5 spec chips
   - avoid long paragraph copy
9. Run QA at full size and thumbnail size.

## Prompt Skeleton For AI Frame Generation

Use this only for generating the decorative background/frame layer, not for
recreating the product itself:

```text
1200x1200 e-commerce marketplace product main image frame, EXITE brand sleeve
system, large slanted top-right EXITE art-word logo on angular paper shard,
category-colored outer frame, clean product-safe center area, refined commercial
Amazon/eMAG/Ozon style, high-conversion product poster, sharp edges, controlled
layout density, premium printed packaging feeling, subtle texture, clear bottom
spec strip and small inset proof cards where appropriate, no product collision,
no messy long text, no generic plain border
```

Negative constraints:

```text
no tiny brand logo, no simple empty border, no full-frame generic cyber border
for clean products, no random decorative blobs, no excessive paragraphs, no
brand text distortion, no product hidden by the frame, no thick frame that
overpowers the product
```

Family modifier examples:

- teal paper sleeve: `teal paper sleeve, white inner panel, baby/home appliance,
  soft paper grain, teal bottom title band`
- green botanical: `green botanical frame, leaf line pattern, white inner
  panel, functional metric chips`
- orange tool poster: `orange hardware poster frame, black underside brand
  shelf, diagonal safety lines, bottom black spec band, small proof cards`
- dark tech poster: `dark neon stage, cyan magenta rim light, angular sci-fi
  frame, bottom spec chips`
- ornamental gift: `black pink ornamental border, soft white inner card,
  floral/puzzle/pearl accents, premium gift poster`
- clean infographic: `technical line frame, accessory grid, right information
  panel, precise catalog layout`

## QA Rubric

Score each generated image out of 100:

- Brand wordmark readability: 15
- Correct frame family selected: 15
- Border proportion matches references: 15
- Product remains primary anchor: 15
- Product/frame collision handling: 10
- Category-specific decoration quality: 10
- Bottom strip/detail panel usefulness: 10
- Thumbnail impact: 10

Do not accept below 75. A useful target for first production pass is 82+.

## First Six Anchor Templates

Build these first before expanding:

1. Ref 02 style: teal baby/home paper sleeve.
2. Ref 05 style: green botanical functional sleeve.
3. Ref 13 style: orange hardware poster with proof panels.
4. Ref 20 or 36 style: dark neon toy/tech poster.
5. Ref 30 style: black/pink ornamental craft frame.
6. Ref 41 style: clean technical infographic with right panel.

These six anchors cover most of the 41-image system. After the anchors are
stable, derive minor variants for the remaining references.

## Implementation Priority

1. Replace the current generic case sheet with six family templates.
2. Build a proper vector-like EXITE wordmark layer first.
3. Add product-mask aware layout calculation.
4. Add family-specific corner/bottom/side modules.
5. Generate one real product card per family and score against the 41-image
   rubric.
6. Only then expand to 20+ variants.
