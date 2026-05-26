# EXCITED / EXITE Art-Word Brand Case Library

Date: 2026-05-22

## Purpose

Build a reusable art-word brand case library before applying the brand layer to
more product main images. These cases are not final logos. They are direction
samples for choosing category-specific brand typography, shelf shape, stroke,
shadow, and border detail.

## Outputs

- Case sheet: `experiments/20260522_excited_brand_case_library/brand_case_library_sheet.jpg`
- Individual cases: `experiments/20260522_excited_brand_case_library/cases`
- Case index CSV: `experiments/20260522_excited_brand_case_library/brand_case_index.csv`
- Case index JSON: `experiments/20260522_excited_brand_case_library/brand_case_index.json`
- Generator: `scripts/generate_excited_brand_case_library.py`

## V2 Proportion Correction

The first case sheet used a horizontal presentation-card layout. That was wrong
for marketplace main-image proportions. The current version has been corrected
to square main-image proportions:

- canvas: `1200 x 1200`
- outer border: `22 px`, about `1.8%` of canvas width
- inner product-safe inset: `42 px`, about `3.5%`
- top-right brand shelf height: `132-146 px`, about `11-12%`
- top-right brand shelf width: `540-610 px`, about `45-51%`
- brand logo width: `35-40%`
- bottom information band: only for hard-sell/block variants, about `9%`

The border should now read as a main-image brand sleeve, not a UI card or
template preview.

## Added Font Sources

The case library now covers these local font bases:

- Racing Sans One
- Bungee
- Bungee Shade
- Russo One
- Orbitron
- Audiowide
- Black Ops One
- Bebas Neue
- Teko
- Anton
- Staatliches
- Rubik Mono One
- Rubik Glitch
- Faster One
- Monoton
- Knewave
- Fascinate Inline
- Bowlby One SC
- Georgia Bold system fallback

Most downloaded web fonts are from the Google Fonts repository and have local
OFL license files in `assets/fonts/google_fonts`.

## Best Directions

Strong candidates:

- `01 Racing White Cut`: default clean EXCITED/EXITE direction for home,
  baby, appliance, and light-background cards.
- `02 Racing Neon Cyan`: tech/auto dark shelf direction. Strong, readable, and
  close to the Excitat angular identity.
- `03 Racing Magenta Game`: gaming/RGB direction. Good for high-energy product
  categories.
- `04 Bungee Tool Block`: hardware/tool direction with a strong orange band.
- `06 Russo Green Shelf`: calmer green/home direction.
- `12 Anton Heavy Retail`: very readable at marketplace thumbnail size.
- `18 Bungee Shade Kids`: kids/toy bubble logo direction.
- `22 Georgia Gold Classic`: classic/gift/luxury direction.
- `23 Chrome Auto`: auto/metal direction.
- `24 Teal Compatibility`: clean compatibility/electronics direction.

Secondary candidates:

- `07 Orbitron Future`: good for thin technical layouts, less close to the
  Excitat main identity.
- `08 Audiowide Sleek`: usable for slim electronics, but weaker impact.
- `10 Bebas Tall Poster`: good when the logo must sit in a tall poster bar.
- `11 Teko Speed Label`: useful for sports/tools but needs careful spacing.
- `13 Staatliches Label`: clean infographic label.
- `14 Rubik Mono Tech`: compact tech/toolkit option.
- `19 Knewave Sticker`: young/playful category.
- `20 Fascinate Inline Gift`: craft/fashion/gift variant.
- `21 Bowlby Premium Pop`: heavy premium retail.

Use sparingly:

- `09 Black Ops Industrial`: stencil feel can become too military/rugged.
- `15 Rubik Glitch RGB`: only for gaming/glitch categories.
- `16 Faster Motion`: interesting speed lines, but weak unless the logo is large.
- `17 Monoton Retro Arcade`: retro game only.

## Design Rules Learned

- The logo face should stay readable first. Special effects must sit behind or
  around the letters.
- Border thickness must stay close to marketplace main-image proportions. A
  thick display-card frame breaks the Excitat reference language.
- For clean/home categories, use a white cut-out logo and reduce heavy black
  outline.
- For tech/game/auto, use white face, dark stroke, chromatic cyan/magenta edge,
  and a dark underside shelf.
- For tools/hardware, block fonts and orange/red bands work better than thin
  futuristic fonts.
- For kids/toy, do not force the angular racing mark. Use bubble/outline
  typography and small icon accents.
- For gift/classic categories, serif or inline decorative typography can be a
  controlled exception.
- The top-right shelf should still connect into the right border. A standalone
  logo floating in space does not match the reference system.

## Current Recommendation

Use `Racing Sans One` as the primary procedural font base for EXCITED/EXITE,
then branch by category:

- clean/home: `01 Racing White Cut`
- tech/auto: `02 Racing Neon Cyan` or `23 Chrome Auto`
- gaming/RGB: `03 Racing Magenta Game`
- tool/hardware: `04 Bungee Tool Block`
- kids/toy: `18 Bungee Shade Kids`
- gift/classic: `22 Georgia Gold Classic` or `20 Fascinate Inline Gift`

For production quality, convert the final chosen directions into fixed vector
brand assets. The generator should then control palette, shelf, border, shadow,
and placement rather than inventing the letterform every time.
