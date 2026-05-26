# Excitat / EXITE Logo Detail Review

Date: 2026-05-22

This pass focuses only on the brand mark. The source crops are exported under:

- `experiments/20260522_excitat_logo_study/top_right_logo`
- `experiments/20260522_excitat_logo_study/header_band`
- `experiments/20260522_excitat_logo_study/right_upper_quarter`

## Correction To Previous Pass

The previous generator captured the top-right tab and frame, but the logo was
too much like ordinary italic text. The reference identity depends first on an
art-word logo, then on the frame around it.

## Default Angular Logo Anatomy

Most strong examples use an angular speed/sport wordmark:

- uppercase compressed but wide brand word
- forward slant, with rightward motion
- white fill on dark or colored frame
- thick black outline
- secondary grey/black extrusion below and to the right
- occasional cyan, magenta, yellow, or teal chromatic edge
- sharp left lightning spear from the first letter
- long triangular right cap from the last letter/top stroke
- logo overlaps the paper shelf instead of sitting politely inside it

Good reference examples:

- 01: white angular logo over dark magenta/black shelf
- 05: white logo, black shadow, green botanical shelf
- 12: white logo over dark EV poster shelf
- 22: white logo on teal/black compatibility shelf
- 23: white logo over red retro band
- 29: white logo over red tool band
- 34: white logo with cyan/red chromatic edge on auto lighting poster
- 37: white logo over magenta sterilizer band

## Category Variants

The logo changes with category, but keeps brand force.

- Clean baby/home: white cut-out logo on teal band, sometimes no black outline
  or a softer outline. Examples: 02, 07, 25.
- Botanical/home: white or yellow logo, dark shadow, patterned green/blue
  border. Examples: 05, 16, 27.
- Tool/hardware: white logo on orange/red top bar, black shadow underneath.
  Examples: 04, 13, 29, 39.
- Tech/gaming/auto: black shelf, neon or chromatic edge, stronger shadow.
  Examples: 01, 12, 20, 31, 34, 36.
- Kids: rounded bubble logo with icon accents, not angular. Example: 32.
- Fashion/soft goods: serif ornamental EXCITAT, fine line decoration. Example:
  15.
- Premium/gift: angular logo can sit inside ornamental black/pink frame or move
  to bottom-right. Examples: 19, 28, 30, 40.

## Frame Details Connected To Logo

The frame detail is usually built around the logo, not separate from it:

- top-right logo shelf connects into the right border
- shelf often has a dark underside strip
- left edge of shelf is cut, curved, or torn like paper
- a lighter folded paper shard sits behind or before the main shelf
- product may cover part of the shelf, but the logo stays readable
- border corners echo the shelf color and angle
- decorative pattern is low contrast and stays behind product

## EXITE Generator Requirements

Required for the next stable layer:

- do not draw EXITE as plain italic text
- use a reusable art-word layer before drawing product composition
- default logo: white angular fill, black outline, grey extrusion, category
  accent offset, lightning first-letter spear
- keep the logo wide and low, not tall and condensed
- right top placement should be aggressive but not cropped
- allow category-specific logo style switches: angular, clean cut-out, kids
  bubble, serif ornamental

## Current Implementation Notes

Implemented in:

- `scripts/analyze_excitat_brand_frames.py`

New support script for logo crops:

- `scripts/extract_excitat_logo_study.py`

Current generated examples:

- `experiments/20260522_excitat_frame_study/generated_frames/teal_clean.png`
- `experiments/20260522_excitat_frame_study/generated_frames/cyan_blue_tech.png`
- `experiments/20260522_excitat_frame_study/generated_frames/orange_tool.png`
- `experiments/20260522_excitat_frame_study/generated_frames/green_home.png`
- `experiments/20260522_excitat_frame_study/generated_frames/black_premium.png`
- `experiments/20260522_excitat_frame_study/generated_frames/pink_beauty.png`

Remaining production gap: this is still a procedural approximation. A final
production system should export an official EXITE vector/PNG art-word mark and
let the generator colorize, shadow, and place it.
