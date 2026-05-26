# eMAG Premium Banner Generation Strategy v1

Date: 2026-05-24

This strategy replaces the loose "make a nice banner" instruction with a stable route selector.

## Model Reality

Do not hard-code "Imagen 2" as the production route. Imagen 1/2 are legacy/deprecated in Google Vertex AI documentation. The Agent should use a provider adapter concept:

- `openai_image`: best when integrated through OpenAI image generation tools/API.
- `google_imagen_current`: Imagen 3/4 family when Google credentials and model access exist.
- `fal_flux_kontext`: useful for image editing, scene adaptation, and reference-preserving exploration.
- `fal_flux_background`: useful for background-only generation followed by deterministic compositing.
- `local_pillow_composite`: deterministic final assembly, text, icons, crop, GIF effects.

The stable pipeline should not depend on one model name. It should depend on route capability: background generation, reference img2img, image edit/inpaint, text rendering, or deterministic overlay.

## Three Routes

### Route A. Pure Composite

Use when product fidelity and text accuracy matter more than scene novelty.

Inputs:

- Real product image or cutout.
- Deterministic background or simple generated background.
- Local text, icon, badge, and frame layers.

Best for:

- Specs boards.
- QA/review boards.
- Brand trust modules.
- Manuals/step diagrams.
- Any module with exact text, numbers, certification, or warranty.

Weakness:

- Can look stiff if background and product lighting are not tuned.

Validator focus:

- product crop quality
- text fit
- mobile readability
- no duplicate visual modules

### Route B. Pure AI Generation

Use only for exploration, moodboards, and non-critical simple text tests.

Inputs:

- Product reference.
- Template reference.
- ProductTruthPack.
- Short prompt with zones and negative constraints.

Best for:

- Style exploration.
- Scene ideation.
- When user explicitly wants to test model typography.

Production limits:

- Fail if product geometry changes.
- Fail if generated claims/text are wrong.
- Fail if product appears twice or gets merged into background.

Validator focus:

- product identity drift
- text correctness
- fake claims
- clutter

### Route C. AI Generation + Composite

Default recommended route.

Steps:

1. Choose a reference pattern from `banner_reference_teardown`.
2. Generate background/scene with clear empty zones.
3. Preserve product using real image/cutout or controlled image-edit route.
4. Add deterministic headline, logo, chips, icons, and proof markers.
5. Optionally add stable GIF effect: `shine_sweep` or subtle light trail.
6. Export `1200x480`, `1280x366`, or `1140`-wide final.
7. Write `media_asset_index` with source, prompt, route, and risks.

Best for:

- First hero banner.
- Product-scene hero.
- Premium dark technical banner.
- Seasonal scene with stable text.

Validator focus:

- no doubled product
- text safe area preserved
- product visual weight 40-70 percent depending module
- only one heavy dark module per sequence
- generated background supports, not fights, the product

## Stable Prompt Contract

Every AI route prompt must have these fields:

```json
{
  "route": "ai_background_plus_composite",
  "banner_family": "industrial_premium_dark",
  "product_type": "ev_charger",
  "reference_pattern": "industrial_black_orange_neon",
  "canvas": "1200x480",
  "product_slot": "right 42 percent, on realistic surface, enough room for shadow",
  "text_slot": "left 45 percent, low-detail background, no generated text",
  "scene": "dark garage or technical workshop",
  "lighting": "single warm rim light plus soft front fill",
  "negative": [
    "no readable text",
    "no fake logo",
    "no duplicate product",
    "no extra ports or cables",
    "no clutter inside text zone"
  ]
}
```

For reference image use, the prompt must state reference roles:

- product image = preserve identity
- template image = layout logic only
- scene reference = mood/camera/background only
- brand reference = palette/frame/logo treatment only

## Route Selection Rules

Use pure composite when:

- exact text or parameters are the core output
- page module is QA/review/spec/manual
- source product image is already strong
- product detail cannot drift

Use pure AI when:

- only testing design direction
- final output is not production
- text is absent or non-critical
- user wants multiple creative candidates

Use AI + composite when:

- banner needs premium atmosphere
- product must stay accurate
- text must be exact
- reference image exists but cannot be used directly

## Layout Stability Rules

- Do not use small boxes by default. Small cards are allowed for specs, steps, comparisons, or first-screen anchors only.
- Do not repeat the same image logic twice in a row. If hero uses a product-scene image, the next module should be short text or cropped proof, not another full product scene.
- Maximum one heavy dark banner before a visual rest module.
- Use at least one clean white text module after any dense visual section.
- Crop images for proof: connector, button, material, package part, safety label, measurement detail.
- If an image already contains many labels, do not add another label layer on top.
- Use line alignment variation: left text block, centered short statement, right image crop, then full-width proof. Do not use the same two-column box pattern repeatedly.

## GIF Stability Rules

Stable:

- black-gold shine sweep
- subtle light trail across background
- step number highlight for true manuals
- small icon pulse in parameter board

Experimental:

- people micro-motion
- product rotation
- edge glow
- particle background
- breathing border

Rule: if motion changes product shape or makes text harder to read, downgrade to static.

## Validation Checklist

Output `banner_validation_report.json` with:

- `route_selected`
- `reference_pattern`
- `product_identity_pass`
- `text_zone_pass`
- `product_weight_estimate`
- `mobile_readability_pass`
- `duplicate_product_detected`
- `unsupported_claims`
- `layout_redundancy_warning`
- `motion_risk`
- `recommended_repair`

Blockers:

- product deformation
- fake certification/discount/warranty/service claim
- unreadable final text
- official/eMAG assets used commercially without rights
- duplicated product caused by background generation

