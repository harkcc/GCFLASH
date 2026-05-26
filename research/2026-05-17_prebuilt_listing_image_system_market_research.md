# Prebuilt Listing Image Production System: Market-Proven Research

Date: 2026-05-17
Status: working research notes

## Positioning

The goal is not to invent a new free-form AI design tool. The goal is to build a
prebuilt listing image production system for cross-border ecommerce sellers,
starting with Amazon and keeping Ozon / European marketplaces in scope.

The implementation should start from market-proven workflows, open-source
frontend/template systems, and community-tested image processing pipelines. The
system should only customize around our own runtime after those patterns are
clear.

## Stable Direction

Use a hybrid production chain:

`product evidence -> brand/style packet -> marketplace slot plan -> template or
reference layout -> product-preserving generation -> deterministic text/layout
rendering -> vision QA -> targeted repair -> batch export`.

This is the pattern repeated across the stronger references:

- GreenOnion: one upload to 9 Amazon image slots, feature assignment, design
  plans, copy editing, settings, batch generation.
- Ribbi: first generate a main image / style-setting poster, confirm the style,
  then generate 6 secondary images and A+ modules with unified style.
- OpenCreator: product analysis, prompt generation, 6 Amazon-standard images,
  and batch generation.
- Brand Shoot Kit: scout, preserve, shot plan, prompt pack, generation, QA,
  reroll, export, review frontend.

## Reference Systems To Borrow From

### 1. Amazon listing-suite products

#### GreenOnion

Source: https://greenonion.ai/use-cases/amazon-bulk-listing-images

Observed workflow:

1. Upload product image.
2. Optional product description.
3. Analyze product and assign features.
4. Generate design specifications.
5. Generate listing copy.
6. User edits copy.
7. Configure settings.
8. Generate 9 images.

Slot taxonomy:

- Main / Hero
- Core value proposition
- Key features
- Usage scenario
- Quality / origin
- Detail / close-up
- Size / quantity
- Comparison
- Lifestyle

What to borrow:

- The 9-slot Amazon suite structure.
- Copy editing before image generation.
- Feature-to-slot assignment as an explicit intermediate step.
- Batch catalog mode as a first-class product promise.

Important warning from HN discussion:

- The product's moat is not "prompting"; it is the constraint system that makes
  outputs production-ready and brand-consistent.

#### Ribbi Amazon Product Image Set

Source: https://ribbi.ai/zh/skills/create-amazon-product-image-set

Observed workflow:

1. Upload product image and provide selling points / target audience.
2. Confirm a main image and style-setting poster.
3. Generate 6 secondary images and 8 A+ modules in parallel.

What to borrow:

- Add a style-confirmation checkpoint before batch generation.
- Use one "style anchor" image to lock color, typography, and layout direction.
- Treat A+ modules as the same family as listing images, not a separate product.
- Keep user correction points at stage boundaries.

#### OpenCreator Amazon Product Photo Set

Source: https://opencreator.io/zh/template-amazon-product-photo-set

Observed workflow:

1. Upload one product reference image and short description.
2. GPT-4o analyzes product features and creates image plans.
3. Nano Banana Pro generates 6 images.

Slot taxonomy:

- Lifestyle scene
- Detail close-up
- Size annotation
- Function demonstration
- Selling-point infographic
- Packaging / unboxing

What to borrow:

- Small 6-image entry suite for MVP.
- Model split: MLLM for analysis and prompt planning, image model for generation.

#### Lovart Amazon listing generator

Source: https://www.lovart.ai/zh/features/amazon-listing-image-generator

What to borrow:

- Element/layer decomposition as a frontend editing affordance.
- Main image compliance helper: remove background and export pure white.

What not to copy first:

- A broad free-form design canvas as the first product surface. It is powerful
  but too open-ended for reliable batch production.

### 2. Open-source agent / workflow systems

#### TheMattBerman/brand-shoot-kit

Source: https://github.com/TheMattBerman/brand-shoot-kit

Openness: MIT, code and Skill contracts are open.

Observed workflow:

`URL -> Scout -> Preserve -> Shot Plan -> Generate -> QA -> Reroll -> Export ->
Review Frontend`.

Artifacts:

- `scout.json`
- `preservation.json`
- `visual-gaps.json`
- `shoot-plan.json`
- `prompts.json`
- generated images
- QA results
- reroll manifest
- channel exports
- `index.html` review frontend

What to borrow:

- Product preservation before any generation.
- QA and reroll as a production gate.
- Packet-based deliverable with provenance.
- Static review frontend as the output surface.
- Ratio/channel metadata in every generated asset.

Why it matters:

This is the strongest open end-to-end reference found so far. It should anchor
our backend workflow design more than generic AI-image SaaS pages.

#### tryclair/amazon-listing-images-plugin

Source: https://github.com/tryclair/amazon-listing-images-plugin

Openness: Skill workflow and Gemini image CLI are open.

Observed workflow:

1. Brand setup from website, logo, product photo, hex codes, or brand text.
2. Write `brands/<slug>/DESIGN.md`.
3. Generate Amazon image type by reading `DESIGN.md`.
4. Save outputs by slot slug.

Slot taxonomy includes 23 types:

- hero
- lifestyle
- main features
- main benefits
- us-vs-them
- what's included
- use cases
- size guide
- size comparison
- guarantee
- ingredient origin
- ingredient list
- nutrition facts
- product line
- certifications
- how-to-use
- before-after
- step-by-step
- compatibility
- material quality
- reviews
- brand story

What to borrow:

- `DESIGN.md` as a simple, human-readable brand system.
- Slot slugs as output names.
- Image type library as our slot catalog seed.

Gap:

- It is one-shot generation; it does not solve batch QA or suite-level
  consistency by itself.

### 3. Open-source frontend / template editors

#### Fabric.js

Source: https://fabricjs.com/

Why it is mature:

- Object model on top of Canvas.
- Text editing.
- SVG import/export.
- Image filters.
- Clipping.
- Controls.
- Grouping.
- Serialization.

Use in our system:

- The most mature base for editable listing templates if we choose a Canvas
  editor.
- Strong fit for deterministic text overlays, callouts, arrows, badges, and
  exportable JSON template state.

#### vue-fabric-editor / Kuaitu

Source: https://github.com/ikuaitu/vue-fabric-editor

Community proof:

- 7.9k+ GitHub stars, 1.4k+ forks.
- Chinese frontend community articles and V2EX posts reference it as a common
  open-source image editor baseline.

Capabilities:

- Custom fonts.
- Materials.
- Design templates.
- Canvas size.
- Background color.
- Alignment.
- Crop.
- Filters.
- Export.

Use in our system:

- Strong Chinese-community validated reference for a web image editor.
- Useful if we want a later "精修模式" where users can edit text, badges,
  product placement, and templates.

#### dromara/yft-design

Source: https://github.com/dromara/yft-design

Community proof:

- Dromara project.
- 1.5k+ stars.
- MIT.

Capabilities:

- Poster and image design.
- PSD import restoration.
- PDF import.
- SVG import.
- Image / SVG / PDF export.
- Page templates.
- Fabric.js + Vue3 + TypeScript + Element Plus.

Use in our system:

- Important because PSD import is directly relevant to marketplace templates.
- Strong candidate to study before building any template editing UI ourselves.

#### LvHuaiSheng/gzm-design

Source: https://github.com/LvHuaiSheng/gzm-design

Community proof:

- 800+ GitHub stars.
- MIT.

Capabilities:

- PSD import and parsing.
- Group/layer handling.
- Text parsing and font loading.
- JSON import.
- Multi-page support.
- Template import.
- Layer management.
- PNG/JPG/WEBP export.
- Masking, cropping, shadows, text overflow controls.

Use in our system:

- Best reference for PSD-template ingestion and browser-side design tooling.
- Good fit for the "preset PSD/template -> batch fill product/copy" direction.

#### sleepy-zone/fabritor-web

Source: https://github.com/sleepy-zone/fabritor-web

Community proof:

- 1.2k+ stars.
- MIT.

Capabilities:

- Text effects.
- Local/remote images.
- Crop and filters.
- Shapes, arrows, polygons.
- QR code and emoji.
- Canvas size / background.
- Layer operations.
- Export JPG/PNG/SVG/template JSON.

Use in our system:

- Good lightweight React/Fabric reference if Electron frontend is React-based.
- Template JSON export is valuable for building a preset template library.

#### Konva

Source: https://konvajs.org/

Why it matters:

- Mature 2D Canvas framework.
- Used by Polotno and other production visual editors.
- Strong React/Vue/Svelte support.

Use in our system:

- Alternative to Fabric.js if we need better React integration and build more
  custom structured design surfaces. Fabric has stronger existing design-editor
  examples; Konva has strong framework ergonomics.

### 4. Product fidelity / image pipeline references

#### MiddleKD/ComfyUI-productfix

Source: https://github.com/MiddleKD/ComfyUI-productfix

Openness: MIT, ComfyUI custom nodes and workflows are open.

Why it matters:

It targets ecommerce product deformation directly: preserving text, logos, and
details while generating new product images.

Important techniques:

- Latent Injection.
- OCR-based text masks.
- Detail transfer.
- IC-Light.
- IP-Adapter.
- ControlNet depth.

Use in our system:

- Product fidelity should be a dedicated stage.
- Product text/logo should use masks/detail transfer, not prompt-only control.
- For open-source local generation, this is one of the strongest technical
  references.

#### Photoroom / Claid / Pebblely / CatalogCut

Sources:

- https://www.photoroom.com/api
- https://docs.claid.ai/ai-background-api/ai-background-options/scene
- https://pebblely.com/docs/
- https://catalogcut.com/

Pattern:

- Background removal.
- White background compliance.
- Brand look / template consistency.
- Batch processing.
- Marketplace resizing.
- API-first workflows.

Use in our system:

- The market-proven batch path starts with cleanup and standardization before
  creative generation.
- We should include a deterministic cleanup/compliance stage for main image:
  background removal, pure RGB white, product crop/fill, shadow policy, export
  size.

### 5. Ozon / European marketplace references

#### Ozon official image requirements

Source: https://docs.ozon.com/global/products/requirements/media/image-requirements/

Relevant rules:

- Ozon has moved to a universal 3:4 product tile area.
- Main image is one image.
- Product must match name/description.
- Product should be shown fully and clearly.
- No watermarks.
- Infographics are allowed.
- Infographics should communicate characteristics, benefits, and advantages.

Implication:

Ozon differs from Amazon: it allows more information-rich visual treatment even
on the main image. This supports keeping an `OzonHighConversionMainCard` path
separate from strict Amazon white-background hero generation.

#### Ozon / Russian marketplace SaaS pattern

References:

- https://pixsora.ru/
- https://sellerart.ru/
- https://sellerden.ai/generator-opisania/generator-kartochek-marketplejsov/generator-kartochek-ozon/
- https://sellovio.com/
- https://www.oimok.com/en

Shared pattern:

- Upload product photos.
- AI extracts product/category/benefits.
- Select or infer style/template.
- Generate card images / infographics.
- Export marketplace-ready PNGs.
- Some tools add photo audit, A/B testing, SEO, or reference-infographic transfer.

Implication:

For Ozon, template-driven infographic cards are more central than Amazon's pure
white main image. We should keep marketplace profiles independent:

- Amazon: strict main image compliance + secondary infographics.
- Ozon: high-conversion main card + additional infographic slides + 3:4 format.

## Core Problems And Proven Solutions

### Problem 1: Product consistency and brand consistency

Market-proven answer:

- Use real product reference images as anchors.
- Extract a product preservation brief before generation.
- Use masks / detail transfer / reference selectors for product fidelity.
- Use a brand design system artifact for colors, typography, border, icons, and
  layout language.
- Confirm a style anchor before batch generation.
- Run suite-level QA after generation.

Concrete reusable pieces:

- Brand Shoot Kit: `preservation.json`, reference selector, QA/reroll.
- ComfyUI-productfix: OCR masks and latent/detail transfer.
- tryclair plugin: `brands/<slug>/DESIGN.md`.
- Ribbi: style-setting poster checkpoint.

Our implementation stance:

- Do not let each slot freely invent product appearance or brand style.
- Generate from `ProductTruthPack + BrandDesignSystem + SuiteStyleAnchor`.

### Problem 2: Text embedding and processing

Market-proven answer:

- Do not rely on image models for final production text.
- Let image models reserve text areas or generate draft backgrounds.
- Render final text, parameters, badges, arrows, tables, and dimension labels
  with deterministic template rendering.

Concrete reusable pieces:

- Fabric.js / yft-design / gzm-design / fabritor: browser template editing,
  text rendering, layer management, export.
- PSD import in yft/gzm: designer-made templates can become fillable assets.
- GreenOnion and Ribbi: copy generation/editing happens before final image set.

Our implementation stance:

- `CopyPlan` and `TemplateCard.text_zones` should be generated first.
- Final text should be rendered by template engine, not by the image model.
- Vision QA should check text correctness and mobile readability.

### Problem 3: Composition and aesthetics

Market-proven answer:

- Use reference layouts or template cards.
- Keep a slot taxonomy.
- Do not rely on generic "make it beautiful" prompts.
- Use competitive / successful examples as templates, then adapt copy and
  product.

Concrete reusable pieces:

- GreenOnion: fixed 9 Amazon slots.
- OpenCreator: fixed 6 Amazon slots.
- tryclair: 23 Amazon slot types.
- uni1-image-ad: reverse-engineer a reference creative into reusable prompt
  templates.
- yft/gzm/fabritor: template JSON / PSD / layer-based editing.

Our implementation stance:

- Build `TemplateCard` library first.
- Later add `template_extractor` that converts successful examples into
  TemplateCard candidates.
- The UI should start with slot/template selection, not a blank canvas.

### Problem 4: Large-model approval and optimization

Market-proven answer:

- QA should be a gate, not an optional comment.
- Score each image by concrete dimensions.
- Repair should target the failed dimension.

Concrete reusable pieces:

- Brand Shoot Kit: QA scores and reroll queue.
- ntrukhachev/ozon-infographic-detector: batch vision inspection over Ozon XLSX
  image URLs, progress table, retry errors, CSV/XLSX export.
- Commercial tools: photo audit and A/B testing are usually adjacent modules.

Our implementation stance:

Use a structured `QAReport`:

- product_fidelity
- brand_consistency
- marketplace_compliance
- slot_fit
- text_correctness
- mobile_readability
- composition_quality
- commercial_clarity
- artifact_risk

Repair actions should be typed:

- `regenerate_scene_keep_product`
- `replace_text_overlay`
- `adjust_crop_or_white_background`
- `switch_template_card`
- `rerender_brand_frame`
- `manual_review_required`

## Frontend Product Shape

The more stable first screen is not a Lovart-style blank canvas. It should be a
suite production workspace:

1. Product intake
   - Upload white-background image.
   - Upload optional side/detail images.
   - Paste product title, bullet points, specs, target marketplace.

2. Product truth review
   - Product name, material, color, dimensions, package quantity.
   - Must-preserve / can-vary / never-change fields.

3. Brand/style setup
   - Import brand website/logo/colors.
   - Generate or select `BrandDesignSystem`.
   - Confirm one style anchor.

4. Slot plan
   - Choose Amazon 6/7/9 image suite or Ozon 3:4 card suite.
   - Assign selling points to slots.
   - Edit generated copy.

5. Template selection
   - Select preset `TemplateCard` per slot.
   - Optionally use PSD/template reference.

6. Generate
   - Run background/scene generation.
   - Render deterministic text/layout overlays.

7. QA and repair
   - Show pass/fail per slot.
   - Allow one-click typed repair.

8. Export
   - ZIP with marketplace-ready filenames.
   - Include manifest and QA report.

Precision editing / canvas mode should be secondary:

- Used only after generation when a specific slot needs manual correction.
- Built from a mature editor stack such as Fabric.js + vue-fabric-editor /
  yft-design / gzm-design / fabritor.

## Candidate Architecture

```text
Intake
  -> ProductTruthPack
  -> BrandDesignSystem
  -> MarketplaceProfile
  -> SlotPlan
  -> CopyPlan
  -> TemplateCard selection
  -> GenerationPlan
  -> ModelGeneration
  -> DeterministicOverlayRender
  -> QAReport
  -> RepairPlan
  -> ExportPackage
```

Minimum persisted artifacts:

- `product_truth.json`
- `brand_design_system.md`
- `marketplace_profile.json`
- `slot_plan.json`
- `copy_plan.json`
- `template_cards/*.json`
- `generation_manifest.json`
- `qa_report.json`
- `repair_log.json`
- `export_manifest.json`

## Implementation Bias

Start with the proven pieces:

1. Use Brand Shoot Kit as workflow skeleton.
2. Use tryclair's `DESIGN.md` idea for brand setup.
3. Use GreenOnion / Ribbi / OpenCreator as suite UX references.
4. Use Amazon / Ozon official rules as marketplace profiles.
5. Use Fabric.js ecosystem for deterministic text/template editing.
6. Use ComfyUI-productfix ideas for product/logo/text preservation when local
   generation is needed.

Avoid:

- Starting from a blank-canvas editor.
- Letting a model render final parameter text.
- One prompt per image with no shared suite state.
- Generating all slots without a style anchor checkpoint.
- Treating QA as natural-language feedback only.

## Follow-up Research Queue

Search communities and examples by specific problem, not broad AI-image terms:

- "Amazon listing image generator complete set one product photo"
- "Amazon A+ content image generator workflow"
- "product photo consistency AI background generation"
- "ComfyUI product logo text preservation OCR mask"
- "Fabric.js ecommerce template image editor PSD"
- "Ozon infographic generator card template AI"
- "Wildberries Ozon AI infographic product card"
- "电商 商品图 套图 AI PSD 模板"
- "亚马逊 listing 图片 AI 套图 工作流"
- "前端 Fabric.js 图片编辑器 PSD 导入 电商产品图"
- "V2EX fabric.js 图片编辑器 电商"
- "掘金 图片编辑器 Fabric.js PSD 模板"

Domestic sources to keep scanning:

- V2EX: frontend canvas / seller tool self-recommendations.
- 掘金: Fabric.js / Konva / PSD import implementation notes.
- SegmentFault: Fabric.js editor architecture articles.
- 微信公众号 / 微头条: seller-operation case writeups and tool comparisons.
- 小红书 / 知乎 / 跨境卖家论坛: real seller feedback on AI listing image quality.

Current evidence from V2EX / 掘金 / SegmentFault points strongly toward
Fabric.js-based editors for practical template/image editing in Chinese frontend
communities.
