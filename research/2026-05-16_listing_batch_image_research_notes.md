# Amazon/Ozon Listing Batch Image Research Notes

Date: 2026-05-16
Status: working notes, not a final solution

## Current Product Target

The target workflow is one product image, or a small product image set such as
one white-background image plus one side/detail image, to a complete
marketplace-ready listing image suite.

The core requirement is not one-off image quality. The core requirement is a
stable prebuilt system that can produce brand-consistent, production-usable
outputs at catalog scale.

## Preserved Findings From Previous Pass

1. GreenOnion is currently the closest found reference for Amazon listing batch
   image generation. It claims one product photo to 9 Amazon images, including
   hero, value prop, feature, usage, quality, detail, size, comparison, and
   lifestyle slots. The important pattern is not "prompt to image"; it is upload,
   optional product description, product analysis, slot feature assignment,
   design specs, editable copy, configuration, and batch generation.

2. VisualForge is a compact "analysis plus generation" miniapp pattern:
   product upload, Claude analyzes category/material/use case, optimized scene
   prompts are generated, and Nano Banana Pro renders ecommerce, lifestyle, and
   ad-ready visuals. This is useful as a small Skill-app reference.

3. SellShots represents the Product Hunt small-seller pattern: one product image
   to a full photoshoot for Shopify, Amazon, and Etsy, including studio,
   lifestyle, model shots, and several variations. It optimizes for speed and
   seller simplicity, not a complex design canvas.

4. Mersel.ai is a Hacker News reference for batch photo/video generation. It
   highlights the real batch pain point: creating or editing a full set in one
   click, while preserving style consistency across many generated assets.

5. CatalogCut is a pragmatic batch editing reference. It focuses on background
   removal, hand/person reduction, marketplace resizing, watermarking, and
   reusable presets. This suggests the first batch workflow may need a cleanup
   and compliance layer before full creative generation.

6. Nexscope Amazon Skills is a strong Skill-oriented reference. Its
   `amazon-listing-images` skill covers 7-image strategy, white-background main
   image optimization, infographic layout, lifestyle scene planning, size/scale
   reference images, mobile readability, and A/B testing. This aligns closely
   with our intended system.

7. Community seller feedback consistently points to a hybrid rule: real product
   photos should anchor the main image and core angles, while AI is more accepted
   for secondary lifestyle images, infographics, tests, seasonal variations, and
   campaign assets. The production system must prevent product drift,
   misleading material/size/color changes, broken logos, and unreadable or
   incorrect text.

## Immediate Research Directions

- Find open-source small projects where the workflow is open, even if the model
  calls are hosted APIs.
- Prioritize projects where code and settings are fully open.
- Search specifically for Amazon automated batch listing image generation.
- Search specifically for Ozon/Ozone batch image generation and automated main
  image or secondary image tooling.
- Build a later competitor teardown table covering inputs, batch support, suite
  slots, Amazon/Ozon compliance, brand consistency, copy editing, refinement UI,
  A/B testing support, pricing, technical architecture clues, reusable ideas,
  and gaps.

## Second Pass: Open Source / Open Workflow Candidates

### 1. TheMattBerman/brand-shoot-kit

Source: https://github.com/TheMattBerman/brand-shoot-kit

Openness: MIT, code and skill contracts are open.

Why it matters: this is the closest fully open production-loop reference found
so far. It is not Amazon-only, but it has the right system shape:

`URL or product image -> scout -> preservation brief -> visual gap audit -> shot
plan -> prompt pack -> generate -> QA -> reroll -> export -> static review UI`.

It ships as cooperating Skills with runnable scripts:
`brand-scout`, `product-preservation`, `visual-gap-audit`, `shoot-director`,
`prompt-factory`, `qa-reroll`, `export-packager`, and `memory-writer`.

Reusable ideas for our system:

- Treat product truth and brand cues as first-class artifacts before generation.
- Produce a reviewable packet, not just images.
- Score outputs with explicit QA criteria, then reroll only failed shots.
- Keep ratio/channel export metadata in the manifest.
- Use a static `index.html` gallery as the human review surface.

Caveat: this is closer to a broad ecommerce brand shoot than a strict Amazon/Ozon
listing suite. We should adapt its control loop, not copy its default 12-shot
taxonomy directly.

### 2. tryclair/amazon-listing-images-plugin

Source: https://github.com/tryclair/amazon-listing-images-plugin

Openness: workflow, Skill file, and Gemini image CLI are open. Repository does
not appear to define a full batch runner or QA gate.

Why it matters: this is a small seller-oriented Amazon Listing Skill. It builds
a brand `DESIGN.md`, then generates branded Amazon listing images from product
photos using Gemini image models.

It defines 23 image types, including hero, lifestyle, main features, benefits,
us-vs-them, what's included, use cases, size guide, certifications, how-to-use,
compatibility, material/quality, reviews, and brand story.

Reusable ideas:

- Brand setup writes a reusable `brands/<slug>/DESIGN.md`.
- Image generation reads the brand design system and selected slot type.
- Multiple product images are passed first to the image model, then prompt text.
- Final output names are slot slugs such as `hero.jpg`, `main-benefits.jpg`,
  and `us-vs-them.jpg`.

Caveat: it is one-shot generation. For production quality, we would need our own
suite-level consistency, review, deterministic text overlay, and batch controls.

### 3. nexscope-ai/Amazon-Skills

Source: https://github.com/nexscope-ai/Amazon-Skills/tree/main/amazon-listing-images

Openness: open Skill workflow and strategy docs. This is not a full generator
implementation, but the process design is highly relevant.

Why it matters: this is still one of the best references for Amazon-specific
slot thinking: white-background main image, infographic layout, lifestyle scene,
size reference, mobile readability, and A/B testing.

Reusable idea: use it as a marketplace rules and slot-plan reference, then bind
it to our own `ProductTruthPack`, `TemplateCard`, and scoring pipeline.

### 4. MiddleKD/ComfyUI-productfix

Source: https://github.com/MiddleKD/ComfyUI-productfix

Openness: MIT, Python custom nodes, assets, and ComfyUI workflows are open.

Why it matters: it focuses on the exact model-layer failure we care about:
preserving ecommerce product text, logos, and details while changing scene,
lighting, or background. It uses ideas like latent injection and OCR text masks.

Reusable ideas:

- Use OCR/text masks or product masks to protect labels and logos.
- Combine relighting/background generation with preservation constraints.
- Treat product-detail preservation as a separate technical stage, not just a
  negative prompt.

Caveat: this is a ComfyUI node/workflow layer, not a listing-suite product.

### 5. Bria-AI/ComfyUI-BRIA-API

Source: https://github.com/Bria-AI/ComfyUI-BRIA-API

Openness: ComfyUI API nodes are open, but generation depends on BRIA API.

Why it matters: it exposes product-shot editing nodes such as background removal,
background replacement, `ShotByText`, and `ShotByImage`. This is useful as a
reference for controlled product-background generation and batch cleanup.

Caveat: API-dependent and not marketplace-suite oriented.

### 6. cliprise/awesome-ai-product-photography-prompts

Source: https://github.com/cliprise/awesome-ai-product-photography-prompts

Openness: open prompt/workflow resource, not production code.

Why it matters: useful as a lightweight checklist reference. It emphasizes
specific placement, viewer, aspect ratio, accuracy constraints, source asset QA,
safe zones, and manual review of generated text.

Caveat: mostly educational/prompt material.

### 7. ntrukhachev/ozon-infographic-detector

Source: https://github.com/ntrukhachev/ozon-infographic-detector

Openness: code is open as a single browser HTML app.

Why it matters: this is not an image generator, but it is a useful Ozon batch
workflow reference. It reads an Ozon XLSX template, extracts main/additional
photo URLs, runs Claude Vision in parallel, detects whether each image is an
infographic, extracts English text, and exports CSV/XLSX.

Reusable ideas:

- Batch intake from marketplace XLSX template.
- Per-image status table, progress bar, concurrency selector, retry errors, and
  export.
- Ozon-specific column handling for main photo and additional photos.
- Vision-based compliance/QA pass as a post-generation or audit stage.

Caveat: it calls Anthropic directly from the browser with a user key and should
not be copied as-is for our product security model.

### 8. krusemediallc/uni1-image-ad

Source: https://github.com/krusemediallc/uni1-image-ad

Openness: MIT, Skill workflow and scripts are open.

Why it matters: not Listing-specific, but it has a valuable pattern for creative
systems: reverse-engineer a reference image into a parameterized prompt template,
validate against the original, then reuse the template with another brand/product
image.

Reusable idea: later, for Ozon/Amazon competitor image references, build a
`template_extractor` that turns reference layouts into `TemplateCard` candidates
instead of hand-authoring every template.

## Second Pass: Ozon / Marketplace SaaS Patterns

The Ozon/WB/Russian marketplace side has many commercial products but very few
fully open image-generation repos. The public product pages are still useful
because they expose the user flow and packaging.

### PixSora

Source: https://pixsora.ru/

Pattern: upload up to 6 product photos, AI analyzes product/category/benefits,
generates up to 6 slides, exports PNG ready for Wildberries, Ozon, Megamarket,
and Yandex Market.

Useful for our UI: simple 4-step flow: upload photos -> AI analysis -> slide
generation -> PNG export.

### SellerArt

Source: https://sellerart.ru/

Pattern: AI generates professional marketplace cards for Ozon, Wildberries, and
Yandex Market in a unified style. Public claims emphasize 30-60 second generation,
brand style memory, multiple AI models, and conversion-oriented cards.

Useful for our product target: brand consistency is marketed as a core feature,
not a nice-to-have.

### SellerDen AI

Source: https://sellerden.ai/generator-opisania/generator-kartochek-marketplejsov/generator-kartochek-ozon/

Pattern: Ozon card generator surrounded by adjacent tools: infographic AI,
product photoshoot, background generator, photo A/B testing, background removal,
photo audit, SEO text, review replies, and Ozon assistant. It also mentions using
a reference infographic so AI can transfer the composition and visual direction
to the user's product.

Useful for our roadmap: "reference template -> transfer to my product" and
"photo audit/A-B testing" should be treated as first-class later modules.

### Sellovio

Source: https://sellovio.com/

Pattern: upload product photos, choose marketplace and style, generate studio,
lifestyle, or infographic cards, auto-resize for Amazon, Etsy, eBay,
Wildberries, Ozon, Shopify, etc. The pitch emphasizes high throughput and
marketplace sizing.

Useful for our batch mode: marketplace selection and style selection are simple
front-door controls; resizing/export can be deterministic.

### Loonia / Oimok / Pixorion / UZ Gen

Sources:
- https://www.loonia-ozon.ru/
- https://www.oimok.com/en
- https://pixorion.ai/
- https://uzgen.app/

Shared pattern: upload product photo, choose or infer style/template, produce
marketplace card images or infographics for Ozon/WB/Yandex-style marketplaces.
Some add try-on, audit, SEO copy, or interactive product cards.

Useful for our decomposition: the market is converging on a bundle, not a single
image editor:

- main image / cover image
- infographic slides
- lifestyle or model/try-on image
- background replacement
- audit / scoring
- A/B testing
- SEO/listing text
- export to marketplace formats

## Second Pass Assessment

The open-source search confirms the system direction:

1. A stable production system should be artifact-driven, not prompt-driven.
2. Open examples with real code usually solve one slice: brand design system,
   prompt generation, product preservation, batch XLSX audit, or review UI.
3. The strongest open end-to-end reference is `brand-shoot-kit`.
4. The strongest Amazon-specific small Skill reference with code is
   `tryclair/amazon-listing-images-plugin`.
5. The strongest low-level fidelity reference is `ComfyUI-productfix`.
6. Ozon-specific open-source generation is sparse. Ozon references are mostly
   commercial SaaS and one-off audit tools, but their flow maps cleanly to our
   existing `OzonHighConversionMainCard` template.

For our first implementation, avoid building a general Lovart-like canvas first.
The better MVP is:

`ProductTruthPack + BrandDesignSystem + MarketplaceProfile + SlotPlan +
TemplateCard + GenerationManifest + QAReport + ReviewUI`.

The UI should let the user correct these artifacts before generation, then batch
fan out. The deterministic parts should own text, layout overlays, dimensions,
file naming, and export. The image model should own product-preserving scene,
background, lighting, and visual style.
