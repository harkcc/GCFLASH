# EXITE FrameKit: Market Pattern And Architecture

Date: 2026-05-22

Scope: analyze the 41 extracted Excitat/eMAG frame references, compare current
market approaches, and decide whether our production system should be prompt
knowledge, PSD files, product-driven modules, or a hybrid workflow.

## Short Answer

Do not build this as a pure prompt library, and do not build it as PSD files
only.

The right architecture is a hybrid:

1. **Frame knowledge base**: chooses frame family, layout, prompt modifier, and
   QA rules.
2. **Editable design masters**: PSD/Figma files for human refinement of brand
   wordmark, border, ornaments, and module proportions.
3. **Product-driven renderer**: programmatically uses product mask, bbox,
   category, and metadata to place the product and select modules.
4. **AI generation only for controlled zones**: texture, background, ornaments,
   secondary scene energy. Do not let AI redraw the product.
5. **Review loop**: score the output against the 41-reference rubric before
   accepting it.

This matches how commercial systems solve the same problem: deterministic
templates for structure, AI for image editing/backgrounds, and product masks or
smart image slots for product preservation.

## What The 41 Frames Tell Us

The 41 references are not one border style. They are a product-card system:

- top-right brand art word
- category-colored outer sleeve
- product-safe inner field
- bottom strip or spec chips
- side proof cards or compatibility panels
- corner ornaments
- occasional dark poster stage
- product overlap rules

The extracted assets are useful as **reference layers**, not as final assets:

- source folder: `experiments/20260522_excitat_41_frame_extract`
- design frame layers: `design_frame_layers/*.png`
- strict edge layers: `strict_edge_layers/*.png`
- manifest: `frame_extract_manifest.csv`

Because extraction is region-based, some product pixels remain where the product
touches the frame. That is acceptable for study: those collisions show how the
reference system handles product/frame depth.

## Market Pattern

### 1. Template Automation APIs

Examples: Placid, Bannerbear, Creatomate, Canva Autofill.

Pattern:

- designer builds a template with layers
- API receives structured data
- runtime swaps text, colors, images, and media
- result is predictable and scalable

Relevant evidence:

- Placid defines templates as layered layouts whose text, shapes, media, and
  colors can be changed through API data:
  https://placid.app/docs/2.0/templates
- Bannerbear supports image generation from templates and lets effects be set
  at template level or per API request:
  https://developers.bannerbear.com/v2/
- Creatomate uses template IDs plus `modifications` for text, colors, images,
  videos, and bulk spreadsheet-style rendering:
  https://creatomate.com/
- Canva Brand Template + Autofill APIs can apply brand templates without manual
  editing, but image fields require uploaded Canva asset IDs:
  https://www.canva.dev/blog/developers/applying-canva-brand-templates/

Lesson for us:

Use this pattern for deterministic EXITE layout: brand area, border, product
slot, bottom bar, side cards, and export sizes.

### 2. PSD / Smart Object Workflows

Examples: Adobe Photoshop API, Photopea, PSD automation libraries.

Pattern:

- product goes into a Smart Object or image slot
- layer effects, masks, shadows, and blending remain stable
- designers can still edit PSD source files

Relevant evidence:

- Adobe Photoshop API v2 includes background removal, Smart Objects, and product
  crop services:
  https://developer.adobe.com/firefly-services/docs/photoshop/
- Adobe Smart Object workflow can replace content inside a PSD layer while
  preserving bounds and aspect ratio:
  https://developer.adobe.com/firefly-services/docs/photoshop/guides/smart-objects-and-the-api/
- Photopea exposes an API and supports PSD formats, useful as a lower-cost
  editing surface:
  https://www.photopea.com/api/
- PhotoshopAPI exposes smart object replacement concepts in a programmatic PSD
  workflow:
  https://photoshopapi.readthedocs.io/en/v0.6.0/python/layers/smart_object.html

Lesson for us:

PSD is excellent as an authoring and high-fidelity handoff format, especially
for the EXITE wordmark and layer effects. But PSD alone is not enough for
category selection, product bbox avoidance, and batch decision-making.

### 3. AI Product Photo APIs

Examples: Photoroom, Pebblely, Claid, Pixelcut.

Pattern:

- remove product background
- preserve product as subject
- generate or replace background
- add shadows, relight, resize, or position object
- provide templates, style images, colors, or prompt fields

Relevant evidence:

- Photoroom API separates subject from background, can relight, shadow, replace
  background, resize, and warns to validate outputs when product accuracy is
  important:
  https://docs.photoroom.com/
- Pebblely flow is product-first: add product, extract visible text, choose
  template/custom prompt/style image/color, generate, and bulk download:
  https://pebblely.com/how-to/
- Claid AI Background API expects a transparent/no-background product and has
  placement controls such as position, scale, and rotation:
  https://docs.claid.ai/ai-background-api/ai-background-options/object
- Pixelcut API offers background removal, upscaling, and generated background
  endpoints:
  https://www.pixelcut.ai/api

Lesson for us:

Use AI for background/texture/style generation, but keep product preservation
and layout deterministic. Our target is not generic lifestyle product photos;
it is a branded marketplace card system.

### 4. Figma / Visual Template Workflows

Pattern:

- product image is stored as an image fill
- plugin/API can create or replace image fills
- variables/styles can manage design tokens
- designers can inspect and adjust the layout visually

Relevant evidence:

- Figma plugin docs describe images as fills on nodes and show loading images
  from URLs through `createImageAsync`:
  https://developers.figma.com/docs/plugins/working-with-images/
- Figma Variables REST API can sync design-token-like values, but REST write
  access has Enterprise requirements:
  https://developers.figma.com/docs/rest-api/variables/

Lesson for us:

Figma is good for editable templates and design review. It is not the best
runtime renderer unless we build a plugin or rely on third-party automation.

### 5. Open Design / Open-Source Design Workflows

Examples: Penpot, open-source design editors, AI design canvases, local
OpenDesign-style tools.

Pattern:

- use a visual design canvas to explore layout systems
- export SVG/PNG/JSON/CSS-like design information
- keep design logic inspectable instead of hiding it inside prompts
- allow human design review before production rendering

Relevant evidence:

- Penpot positions itself as an open-source design platform with design systems,
  design tokens, code inspection, SVG/JSON/CSS-style handoff, and AI workflow
  direction:
  https://penpot.app/
- Open-source design editors such as Draftila show the same direction:
  reusable components, frames/layout, layers, image support, and export:
  https://draftila.com/
- Figma-style plugin workflows show that design images can be represented as
  fills on nodes and programmatically replaced:
  https://developers.figma.com/docs/plugins/working-with-images/

Lesson for us:

Open Design is useful as a **design exploration and template-authoring layer**.
It can help us design the six EXITE frame families, inspect proportions, and
export editable artifacts. It should not become the final generation engine by
itself unless it can expose stable layer coordinates, image slots, and export
automation.

Best use in EXITE FrameKit:

1. Explore family layouts visually.
2. Export the design as SVG/PNG/JSON if supported.
3. Convert the design into our FrameKit module spec.
4. Let the product-driven renderer place real product cutouts.
5. Use Open Design again for human review and template refinement.

Do not use Open Design as a pure prompt-to-image black box. If it cannot expose
layer structure, product slots, or reusable design tokens, it is only useful for
inspiration, not for production.

### 6. ComfyUI / Open-Source AI Workflows

Pattern:

- load product image
- remove background or use mask
- generate background through inpainting/fill
- preserve product by compositing product over generated area
- optionally use IPAdapter, IC Light, or detail-retention workflows

Relevant evidence:

- ComfyUI product-editing workflows typically load product and background,
  require masks, then use inpainting/outpainting or style/reference control:
  https://comfyui.org/en/product-image-editing-workflow-solution
- Open-source background replacement workflows show the same structure:
  product image, mask, prompt, generated background, then composite:
  https://github.com/meap158/ComfyUI-Background-Replacement

Lesson for us:

ComfyUI is useful for experimentation and style generation, but should not be
the only production path. It is too variable for exact eMAG/Ozon-style branded
frames unless wrapped with deterministic template layers and QA.

## Recommended System For EXITE

Build **EXITE FrameKit** with four layers.

### Layer 1: Knowledge Pack

File type: JSON/YAML plus prompt snippets.

Purpose:

- map product category to frame family
- define layout constraints
- choose modules
- choose AI prompt modifier
- define QA rules

Example fields:

```yaml
family_id: teal_paper_sleeve
refs: [02, 07, 22, 25]
category_triggers: [baby, home_appliance, clean_accessory]
canvas: 1200
brand_slot:
  x: 610
  y: 24
  width: 560
  height: 150
product_safe_area:
  x: 90
  y: 190
  width: 760
  height: 700
modules:
  - outer_sleeve
  - brand_shard
  - bottom_title_bar
  - side_icon_stack
ai_prompt_modifier: teal paper sleeve, white inner product panel, subtle paper grain
negative_prompt: no tiny logo, no simple empty border, no product collision
qa:
  brand_readability_min: 0.9
  product_area_min_ratio: 0.48
  thumbnail_check: true
```

### Layer 2: Editable Masters

Create one source file per family:

- `EXITE_teal_paper_sleeve.psd`
- `EXITE_green_botanical.psd`
- `EXITE_orange_tool_poster.psd`
- `EXITE_dark_neon_tech.psd`
- `EXITE_ornamental_gift.psd`
- `EXITE_clean_technical_info.psd`

Suggested PSD layer contract:

```text
FRAME_BG/
FRAME_OUTER/
FRAME_INNER_FIELD/
BRAND/
  BRAND_SHARD
  BRAND_WORDMARK
  BRAND_SHADOW
PRODUCT/
  PRODUCT_SMART
  PRODUCT_SHADOW
FOREGROUND_OVERLAP/
BOTTOM_BAR/
RIGHT_PANEL/
CORNER_ORNAMENTS/
DETAIL_CHIPS/
QA_GUIDES/
```

PSD should be the designer-editable source. Runtime should not depend on manual
Photoshop unless we decide to use Adobe/Photopea/PhotoshopAPI as renderer.

### Layer 3: Product-Driven Renderer

Inputs:

- white-background product image
- transparent product cutout/mask
- product bbox
- product category
- product dimensions/features
- target marketplace size

Renderer steps:

1. classify product family
2. compute product-safe placement
3. choose frame modules
4. render deterministic frame layers
5. optionally generate background/ornament texture
6. composite product with shadow
7. add bottom chips/cards
8. export final image and QA preview

This can be implemented locally with Python/Pillow/SVG/HTML Canvas first. PSD
or Figma can remain the authoring format.

### Layer 4: AI Prompt Pack

Use prompts only for:

- background texture
- ornamental pattern
- tech glow
- paper sleeve texture
- secondary decorative elements
- optional product-adjacent scene elements

Do not rely on prompt-only generation for:

- brand wordmark
- product position
- product integrity
- border dimensions
- final text placement

Prompt packs should be family-specific, short, and structured. The renderer
should pass product category, color, and module choices into the prompt.

## Why This Is Better Than PSD-Only

PSD-only is strong for fixed layouts, but the 41 references change based on the
product:

- tall product vs wide product
- dark product vs white product
- kit/collage vs single hero product
- clean home item vs gaming/tech item
- bottom bar needed vs no bottom bar
- side panel needed vs no side panel

Those decisions require product metadata and bbox logic. PSD should hold the
visual craftsmanship; the renderer should make the product-specific decisions.

## Why This Is Better Than Prompt-Only

Prompt-only will keep failing on:

- exact brand wordmark
- consistent border proportion
- product not being modified
- small text accuracy
- repeated batch consistency
- marketplace thumbnail readability

AI can make images attractive, but it should not own the whole layout.

## Next Build Step

Build a pilot with six families:

1. convert extracted reference frames into clean module targets
2. create six JSON family specs
3. create six clean template renders from code
4. run 1 real product through each family
5. score against the 41-reference QA rubric
6. only then create PSD/Figma masters

This order avoids spending time polishing PSD files before the product-driven
layout rules are correct.
