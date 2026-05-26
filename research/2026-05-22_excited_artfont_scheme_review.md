# EXCITED Art-Font Scheme Review

Date: 2026-05-22

## Scope

This pass rechecks the full product images, not only logo crops. The goal is to
control logo size, art-font choice, and frame detail as one product-card system.

Outputs:

- `experiments/20260522_excited_artfont_schemes/artfont_logo_candidates.jpg`
- `experiments/20260522_excited_artfont_schemes/scheme_contact_sheet.jpg`
- `experiments/20260522_excited_artfont_schemes/*.png`
- `scripts/generate_excited_artfont_schemes.py`

## Full-Image Logo Scale

Observed from representative full product cards:

- default top-right brand width: about 32-45% of canvas width
- default brand height: about 7-13% of canvas height
- top shelf / top band height: about 11-16% of canvas height
- tech/game cards can push the logo larger, but it must stay in the upper
  shelf and not cover the product's primary silhouette
- clean home/baby cards should use a larger white cut-out mark with less dark
  outline
- hardware/tool cards can use a wide top band because the product is usually
  technical and detail-heavy
- kids/toy cards should switch to bubble logo, not force the angular mark

## Font Candidate Judgment

Downloaded open-source Google Fonts candidates:

| Font | Judgment | Use |
|---|---|---|
| Racing Sans One | best default | speed/angular main logo; clean, tech, game, auto |
| Bungee | useful | hardware/tool block logo, bold simple categories |
| Bungee Shade | useful but narrow | kids/toy bubble-outline variant |
| Russo One | useful | stable home/green/premium logo |
| Audiowide | secondary | sleek electronics, less close to Excitat |
| Black Ops One | not default | too stencil-heavy for main marketplace logo |
| Faster One | not default | speed lines are interesting but weak at thumbnail size |

## New Scheme Set

1. `01_clean_teal_racing`
   - full product base: baby steamer/blender
   - font: Racing Sans One
   - logo style: clean white cut-out
   - key rule: product is light/white, so the logo should be white on teal with
     only a soft shadow

2. `02_tool_orange_bungee`
   - full product base: folding hinge hardware
   - font: Bungee
   - logo style: block
   - key rule: top bar can be wider; border and proof panels can be stronger

3. `03_auto_neon_racing`
   - full product base: LED auto light
   - font: Racing Sans One
   - logo style: neon angular
   - key rule: dark shelf, cyan/magenta edge, but logo face must stay white

4. `04_kids_bubble_bungee`
   - full product base: bath toy
   - font: Bungee Shade
   - logo style: bubble
   - key rule: use playful icon accents instead of aggressive lightning spear

5. `05_green_home_russo`
   - full product base: exhaust fan
   - font: Russo One
   - logo style: clean white cut-out
   - key rule: leaf/paper border should support the product, not turn into a
     full decorative wallpaper

6. `06_game_magenta_racing`
   - full product base: game stick
   - font: Racing Sans One
   - logo style: neon angular
   - key rule: largest brand ratio is acceptable here, but face must remain
     high contrast white

## Border Detail Adjustments

Compared with the previous failed pass:

- old reference logo area is now covered by an opaque brand shelf before the
  new logo is drawn
- clean/home logo no longer uses heavy dark outline
- neon/game/auto logo uses white face plus chromatic offset, not dark filled
  letters
- product category controls shelf color and border detail
- internal scheme labels were removed from final individual cards

## Current Recommendation

Use `Racing Sans One` as the default EXCITED/EXITE brand font base, then apply
category-specific rendering:

- clean: white cut-out, soft shadow
- tech/game/auto: white face, black stroke, cyan/magenta edge
- tool: Bungee block or Racing Sans with orange band
- kids: Bungee Shade or Bungee bubble
- green/home: Russo One or Racing Sans, white mark on green shelf

This still should not be the final logo asset. For production, create a fixed
brand-vector logo and only let the generator vary color, shelf, shadow, and
placement.
