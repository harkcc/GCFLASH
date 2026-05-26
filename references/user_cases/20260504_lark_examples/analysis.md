# User Case Analysis - 2026-05-04

## Important boundary

These files are phone screenshots, not production-ready template reference images.

They should not be passed directly to an image model as visual templates. The useful information is inside the screenshots:

- layout fragments
- prompt-writing patterns
- marketplace rules
- product-size rules
- copy hierarchy
- badge/icon usage
- scoring and iteration logic

When the workflow needs an actual visual reference, extract or recreate the relevant detail as a clean TemplateCard, crop, moodboard, PSD, or generated reference image first.

## Local files

- `01.jpg`: vacuum/pet scene Image-2 comparison, 3000x3000 product image case.
- `02.jpg`: adjustable stand comparison, Image-2 generated structured selling-point image.
- `03.jpg`: GPT Image 2 prompt guidance: structure, concrete visible instructions.
- `04.jpg`: TLDR prompt guidance: be concrete, use structure, separate change/keep, specify text.
- `05.jpg`: Amazon/Walmart purple PSD template post.
- `06.jpg`: Russian marketplace image rule notes, points 1-3.
- `07.jpg`: Russian marketplace image rule notes, points 4-6.
- `08.jpg`: prompt optimization tips: reverse reference image logic, life feeling, visualized selling points.
- `09.jpg`: Amazon layout sharing, multi-scenario board examples.
- `10.jpg`: industrial product detail page, direct suite image generation example.
- `11.jpg`: Ozon product image examples, pet products.
- `12.jpg`: Ozon main image user logic and core rules.
- `13.jpg`: Ozon universal main-image structure and common pitfalls.

## Reusable visual principles

1. The product must be seen first.
   - Product should occupy 60%+ of the visual weight for marketplace main images.
   - Background should support recognition, not compete with the product outline.

2. Use numbers and badges instead of long copy.
   - Examples: `350W`, `170AW`, `360`, `3 Adjustment Points`, `14g`, `10 Minute Auto Off`.
   - Numbers should sit in high-contrast circles, bars, or badges.

3. Structure information into modules.
   - Product = largest module.
   - 2-3 selling-point badges = quick proof.
   - One scene/detail inset = conversion support.
   - Bottom strip = accessories, warranty, package quantity, comparison.

4. Separate what changes and what stays.
   - Keep product identity, shape, color, labels, logo, details.
   - Change scene, lighting, visual metaphor, badge copy, layout style.

5. Text should be controlled.
   - For GPT Image 2/Image-2, text can be attempted when instructions are precise.
   - For production, final marketplace copy should be overlaid or PSD-rendered when accuracy matters.

6. Scene images are conversion accelerators, not decoration.
   - Watch -> outdoor wearing.
   - Kitchenware -> food result.
   - Tool -> usage state.
   - Pet product -> pet using/inside product.

## TemplateCard candidates

### `image2_pet_cleaning_action_v1`

From `01.jpg`.

- Use case: cleaning appliances, tools, pet/home problem solving.
- Layout: product large in action, debris/pain point visible, home scene, 2-4 data badges.
- Value: directly explains what the product solves.

### `adjustment_comparison_blueprint_v1`

From `02.jpg`.

- Use case: stands, brackets, tools, adjustable devices.
- Layout: large product in center-left, numbered callouts, competitor comparison on right, bottom comparison bar.
- Value: high clarity for mechanical selling points.

### `amazon_purple_feature_grid_v1`

From `05.jpg`.

- Use case: Amazon secondary images and infographics.
- Layout: purple brand background, 2x2 feature cards, icons, number badge, before/after.
- Value: PSD/template friendly, good for attachment images.

### `industrial_dark_modular_detail_v1`

From `10.jpg`.

- Use case: industrial tools, electronics, B2B products.
- Layout: dark premium background, multiple horizontal/vertical panels, product detail close-ups, icon specs.
- Value: strong professional trust signal.

### `ozon_high_conversion_main_v1`

From `11.jpg`, `12.jpg`, `13.jpg`.

- Use case: Ozon/Russian marketplace main images.
- Layout: big product, dark/blurred scene, large Russian headline, badges, side icon list, scene inset.
- Value: optimized for thumbnail click and quick understanding.

### `japanese_rakuten_vertical_trust_v1`

From user-provided Japanese prompt examples.

- Use case: beauty, health, household, functional consumer goods.
- Layout: high-density vertical landing banner, badges/ribbons, soft palette, trust cards, icons.
- Value: useful for mobile detail page or long form vertical banner.

## Prompt rules extracted from the cases

Good prompts should include these sections:

1. `Reference role`: explain whether the image is composition reference, product source, or style source.
2. `Keep`: product traits and visual logic to preserve.
3. `Change`: product/category/selling point to replace.
4. `Visible scene`: subject, scene, important details, usage, background.
5. `Layout`: product size, left/right/top/bottom zones, badges, insets.
6. `Text policy`: render exact text or reserve empty text zones.
7. `Negative constraints`: no product deformation, no extra parts, no fake text.

## Production implications

- Do not build a huge template library first.
- Build a small set of high-signal TemplateCards and test them against multiple products.
- Let image generation handle visual concept and atmosphere.
- Let deterministic overlay/PSD handle final copy when text accuracy matters.
- Add review loops that score commercial clarity, not only beauty.
