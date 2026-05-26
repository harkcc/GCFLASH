# EXITE Brand Frame Design System

Purpose: stabilize the EXITE brand-frame layer before full product-card
generation.

## Core Identity

The frame should feel like a printed marketplace brand sleeve:

- large top-right slanted `EXITE` wordmark
- colored paper shard behind the wordmark
- thin category-colored outer frame
- white or lightly textured inner product field
- 1-2 expressive corners, not four heavy corners
- optional bottom band for short title/specs

The frame is a brand container. It should support the product, not compete with
the product.

## Logo / Brand Lockup

Default lockup:

- position: top-right
- size: 30-45% canvas width
- style: art-word first, frame second
- default shape: angular speed/sport wordmark, wide and low
- fill: white
- stroke/shadow: thick black outline, grey/black extrusion, category accent edge
- backing: slanted paper shelf, category color, often with dark underside
- motion detail: first-letter lightning spear and right-side triangular cap
- optional small icon: category icon only when it adds meaning

Secondary lockups:

- bottom-right brand for technical line-frame cards
- centered top brand for classic/clean single-product cards
- mid-sidebar brand only for dense infographic layouts

Logo variants:

- angular: default for tools, tech, auto, gaming, appliances
- clean cut-out: white logo on teal/mint shelf for baby/home
- chromatic angular: cyan/magenta or orange/purple edge for tech/gaming
- bubble: rounded kid/toy logo with small icon accents
- serif ornamental: fashion/soft goods or gift-like categories

Avoid plain italic text. The mark must read as a designed logo before any
product or border is added.

Recommended open-source font bases for prototyping:

- `Racing Sans One`: default speed/angular base
- `Bungee`: blocky tool/hardware or bold retail base
- `Bungee Shade`: kids/toy bubble-outline base
- `Russo One`: stable home/green/premium base
- `Audiowide`: secondary electronics base

Do not use `Black Ops One` or `Faster One` as the default mark. They are useful
experiments, but the stencil/speed-line detail weakens thumbnail readability.

Expanded case library:

- generator: `scripts/generate_excited_brand_case_library.py`
- sheet: `experiments/20260522_excited_brand_case_library/brand_case_library_sheet.jpg`
- index: `experiments/20260522_excited_brand_case_library/brand_case_index.csv`

Preferred cases for production exploration:

- `01 Racing White Cut`: clean/home/baby/appliance
- `02 Racing Neon Cyan`: tech/auto
- `03 Racing Magenta Game`: gaming/RGB
- `04 Bungee Tool Block`: hardware/tool
- `18 Bungee Shade Kids`: kids/toy
- `22 Georgia Gold Classic`: gift/classic
- `23 Chrome Auto`: auto/metal
- `24 Teal Compatibility`: compatibility/electronics

## Frame Families

### Paper Sleeve

Best for home, baby, clean appliance, simple electronics.

- teal/mint/cyan outer frame
- white inner panel
- top-right EXITE shard
- bottom title strip if needed
- subtle paper texture or faint line pattern

Reference IDs: 02, 05, 07, 22, 25, 27.

### Tool Poster

Best for tools, hardware, auto accessories.

- orange/red/brown top brand band
- thin side frame
- black or gray bottom information band
- right-side inset proof boxes

Reference IDs: 04, 13, 29, 33, 39.

### Tech / Gaming Poster

Best for gaming, EV charging, RGB, sci-fi toy.

- dark or neon interior
- top-right brand shard remains visible
- outer frame may be stronger, but still not generic chrome
- bottom spec chips or arcade-style strip

Reference IDs: 01, 12, 20, 23, 31, 36.

### Ornamental Gift / Craft

Best for puzzle, craft, fashion, gift.

- black/pink or mint ornamental border
- white inner product canvas
- top-right or bottom-right EXITE lockup
- decorative line art may run behind the brand tab

Reference IDs: 15, 19, 28, 30, 40.

### Clean Infographic

Best for parameter-heavy accessories or appliances.

- less decorative border
- side or bottom panel grid
- EXITE appears as brand header or side marker
- color blocks carry brand system more than frame strokes

Reference IDs: 06, 10, 14, 17, 18, 35, 37, 38, 41.

## Product-Following Rule

The frame should react to product geometry:

- large vertical products: keep top-right brand, leave side frame thin
- horizontal products: use top band plus bottom strip
- dense kit products: use inner white panel and small edge accents
- dark products: choose lighter frame and strong white field
- white products: use colored outer band and shadowed inner field

Optional product brackets can be used around the product safe area, but they
should be thin and partial.

The logo shelf should also react to product geometry:

- if product reaches the top-right, move the shelf slightly upward/right but do
  not crop the wordmark
- if product is tall and centered, keep the logo wide and shallow
- if the category needs more energy, strengthen the shadow/extrusion before
  thickening the outer border
- if the category is clean/home, reduce outline contrast but keep the art-word
  silhouette

Scale rule from full product cards:

- main logo width: 32-45% of canvas width
- main logo height: 7-13% of canvas height
- top shelf height: 11-16% of canvas height
- outer border thickness: roughly 1.5-3% of canvas width
- inner product-safe inset: roughly 3-5% of canvas width
- bottom information band, when used: roughly 8-12% of canvas height
- gaming/tech can sit at the high end of the range
- clean home/baby should keep the shelf shallow and the logo face white

Avoid the presentation-card error: do not let the shelf or border consume a
third of the frame. The product must still own the main canvas.

## Palette Rules

- `teal_clean`: default EXITE clean product frame
- `cyan_blue_tech`: electronics and compatibility cards
- `orange_tool`: hardware, tool, warning, proof cards
- `green_home`: home/garden/nature/comfort
- `black_premium`: office, classic, gift, premium
- `pink_beauty`: beauty, fashion, personal care
- `red_magenta`: sterilization, urgency, health-tech
- `purple_neon`: gaming/RGB only

## QA Checklist

- Top-right EXITE is readable at marketplace thumbnail size.
- The border is not thicker than the product hierarchy allows.
- The frame color is explainable from product/category.
- The product remains the first visual anchor.
- Text and brand do not collide with product edges.
- At least one corner or band carries the paper-shard identity.
- The frame can be rendered as a reusable layer without rerunning image generation.

## Current Implementation

- Study script: `scripts/analyze_excitat_brand_frames.py`
- Manual review: `research/2026-05-22_excitat_exite_frame_manual_review.md`
- Output folder: `experiments/20260522_excitat_frame_study`

The current generator is a stable first pass. Production should replace the
procedural art-word with a proper EXITE logo asset or vectorized wordmark.
