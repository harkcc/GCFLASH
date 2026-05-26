# Batch AI Ecommerce Image Generation External Research

Date: 2026-05-22

Scope: 2025-2026 community and open-source research for batch AI image generation, ecommerce product photography, Amazon/Ozon listing images, and seller workflows. This update corrects the model focus to Nano Banana 2 and Image 2 / GPT Image 2. Frameworks are treated as optional implementation vehicles, not the primary criterion.

## Executive read

The useful market pattern is now clear:

```text
real product source
  -> preserve product truth
  -> generate scene / background / campaign visual with Nano Banana 2, GPT Image 2, Midjourney, or specialist model
  -> deterministic text / badge / layout rendering
  -> QA for product fidelity, platform compliance, mobile readability
  -> reroll / repair
  -> batch export
```

The strongest current direction for this project is **not** a pure ComfyUI-style framework and not pure prompt generation. It is a preserve-first ecommerce production loop:

- Use real product photo/cutout as the anchor.
- Use Nano Banana 2 or GPT Image 2 for high-fidelity editing, scene generation, campaign mood, and fast variations.
- Use Midjourney only where its aesthetics/style exploration outperform product fidelity needs.
- Use deterministic template/rendering for text, badges, dimensions, labels, Ozon/WB-style frames, and Amazon compliance.
- Treat frameworks as replaceable adapters: API batch runner, product truth pack, slot planner, prompt compiler, QA/reroll, export manifest.

## Model focus

### Nano Banana 2 / Gemini 3.1 Flash Image

Primary sources:

- Google announcement: https://blog.google/innovation-and-ai/technology/ai/nano-banana-2/
- Google developer post: https://blog.google/innovation-and-ai/technology/developers-tools/build-with-nano-banana-2/

Google positions Nano Banana 2 as Gemini 3.1 Flash Image. Important capabilities for ecommerce:

- Fast iteration with Flash speed.
- Subject consistency and object fidelity: Google claims up to five consistent characters and up to 14 objects in one workflow.
- Better instruction following.
- Native output sizes from 512px to 4K.
- Better text rendering and localization, useful for marketplace card drafts and international content.
- Developer API access through AI Studio / Gemini API and Vertex AI preview.
- Image-search grounding and world knowledge for infographics, diagrams, and context-aware visuals.

Practical ecommerce interpretation:

- Best for quick product-scene variation, multilingual visual drafts, campaign/editorial boards, and high-throughput experiments.
- Strong candidate for Ozon/WB style cards because 3:4, 4K, text rendering, and fast batch iteration matter there.
- Still needs product-fidelity QA. Community examples report that API calls can look different from AI Studio/session workflows when context is missing.

Useful community signal:

- Reddit Nano Banana 2 guide thread emphasizes structured prompts, reference images, aspect ratio/resolution control, thinking mode, search grounding, and product photography at scale: https://www.reddit.com/r/promptingmagic/comments/1rjt2r9/the_ultimate_guide_to_nano_banana_2_how_to/
- Reddit prompt examples for product photography repeatedly mention camera/lens, lighting, negative space, and clean overlay zones: https://www.reddit.com/r/FiddlartAi/comments/1smyhpm/prompt_drop_3_luxury_product_photography_nano/

### Image 2 / GPT Image 2

Primary sources:

- OpenAI launch: https://openai.com/index/introducing-chatgpt-images-2-0/
- OpenAI model docs: https://developers.openai.com/api/docs/models/gpt-image-2
- OpenAI image generation guide: https://developers.openai.com/api/docs/guides/image-generation

OpenAI positions `gpt-image-2` as the state-of-the-art image generation model with text and image input, image output, generation and edit endpoints, flexible image sizes, high-fidelity image inputs, and a pinned snapshot `gpt-image-2-2026-04-21`.

Practical ecommerce interpretation:

- Best current candidate for text-heavy images, editorial listing boards, brand campaign layouts, infographics, packaging/label readability, and multi-panel storyboards.
- More expensive/quality-oriented than lightweight batch systems, but valuable for final candidate renders, hero images, A+ style modules, and images where text fidelity matters.
- Needs cost/latency controls: low/medium/high quality tiering, reroll budget, and strict acceptance gates.

Useful community signal:

- fal community launch thread explicitly calls out product photography, labels, logos, packaging, ingredient lists, and ecommerce usability: https://www.reddit.com/r/fal/comments/1srxfj4/gpt_image_2_is_live_on_fal/
- Product-to-commercial example uses GPT Image 2 to create consistent multi-view product kit and storyboard, then sends to video generation: https://www.reddit.com/r/seedance2pro/comments/1stjwq7/from_product_image_to_a_full_cat_food_commercial/
- Open-source prompt dataset claims the post-GPT Image 2 prompt ecosystem has grown around product/brand, poster design, and UI/graphic categories: https://www.reddit.com/r/comfyui/comments/1sypezt/open_source_1446_trending_ai_image_prompts_for/

### Midjourney current path

Primary sources:

- V7 default announcement: https://updates.midjourney.com/v7-is-now-the-default-model/
- Omni-Reference: https://updates.midjourney.com/omni-reference-oref/
- V8 Alpha: https://updates.midjourney.com/v8-alpha/
- V8.1 Alpha: https://updates.midjourney.com/v8-1-alpha/
- V8.1 updates: https://updates.midjourney.com/v8-1-updates/

Current path:

- V7 became default in June 2025 with better prompt understanding, image coherence, Omni-reference for consistent objects/characters, Draft mode, improved SREF/moodboards, and personalization.
- Omni-reference is the key ecommerce-relevant feature: "put this object in my image" for objects, vehicles, characters, and creatures, with `--ow` controlling reference adherence.
- V8/V8.1 Alpha is live in 2026. It improves detailed instruction following, coherent/details, text rendering in quotes, speed, 2K `--hd`, `--q 4`, and stronger SREF/moodboard/personalization. V8.1 restored image prompts and image weights and is available on Discord and midjourney.com.

Practical ecommerce interpretation:

- Midjourney is still valuable for high-aesthetic concept exploration, brand moodboards, campaign backgrounds, visual directions, and style references.
- It is weaker as the only production renderer for exact products because marketplace listing needs true product geometry, label/logo/text accuracy, and repeatable SKU-level consistency.
- Good route: Midjourney generates scene/mood/style/reference boards, then product is preserved through cutout/composite or re-rendered by Nano Banana 2 / GPT Image 2 with a product reference.

## Community discussion patterns

### Reddit seller/community signals

High-signal threads:

- For ecommerce sellers using AI photography, what changed: https://www.reddit.com/r/AIToolsAndTips/comments/1tbn1n7/for_ecom_sellers_using_ai_photography_what/
- Biggest problem with AI product images: https://www.reddit.com/r/AIToolsAndTips/comments/1tcmpv0/for_ecommerce_sellers_using_ai_product_images/
- Paying for product photography vs AI: https://www.reddit.com/r/ecommerce/comments/1pvvywd/do_you_still_pay_for_product_photography_or_you/
- AI product photography actual tests: https://www.reddit.com/r/productphotography/comments/18uu0yw/ai_for_product_photography/
- ComfyUI product photography limits: https://www.reddit.com/r/comfyui/comments/1mcsxoc/testing_the_limits_of_ai_product_photography/
- Amazon listing AI tool discussion: https://www.reddit.com/r/generativeAI/comments/1sqdvr5/what_ai_tools_available_for_amazon_listing_images/
- AI generated listings conversion skepticism: https://www.reddit.com/r/AmazonFBA/comments/1teytpl/are_ai_generated_listings_actually_converting_for/

Repeated lessons:

- Real product photo first. Sellers repeatedly distrust pure AI product images for main/hero slots.
- AI is accepted for background, lifestyle, social/ad variants, cleanup, relighting, and secondary images.
- Product consistency is the biggest bottleneck: color, shape, proportions, texture, labels, logos, and fine product details drift.
- Human QA is not optional before Amazon/Shopify upload.
- Main images should remain compliant and product-clear; lifestyle/infographic slots can be more AI-assisted.
- Buyers punish fake-looking, over-stylized, CGI/AI renders when they cannot tell what they are buying.
- Better product source photos produce better AI outputs.

### Hacker News / technical community signals

High-signal threads:

- FLUX.1 Kontext thread: https://news.ycombinator.com/item?id=44128322
- FLUX.1 Kontext tools thread: https://news.ycombinator.com/item?id=44169890
- Nano Banana examples: https://news.ycombinator.com/item?id=45215869
- Nano Banana editor discussion: https://news.ycombinator.com/item?id=45059708
- ByteDance Seedream 4 comparison: https://news.ycombinator.com/item?id=45274860
- Comflowy / ComfyUI tutorial: https://news.ycombinator.com/item?id=38855346

Technical lessons:

- Community sees modern multimodal image models as replacing many older glue workflows for common tasks.
- But detail-preserving editing, local/inpainting control, cost, speed, censorship, and batch reliability still matter.
- GPT Image and Nano Banana improve instruction following and text rendering, while FLUX/Kontext/Seedream/Qwen remain relevant for local, cheaper, or specialist editing paths.
- ComfyUI remains useful as a specialist workflow environment, but not necessarily the product experience sellers want.

## GitHub / open-source findings

### Highest-value ecommerce-specific references

- Brand Shoot Kit: https://github.com/TheMattBerman/brand-shoot-kit
  - Best architecture reference. Product URL -> Scout -> Preserve -> Shot Plan -> Generate -> QA -> Reroll -> Export -> Review Frontend.
  - Core lesson: product truth and QA/reroll are first-class, not optional prompt notes.

- AI E-Commerce Media Studio: https://github.com/ronchen0927/AI-E-Commerce-Media-Studio
  - API-first/local-fallback architecture with background removal, image editing, async queue, storage, rate limiting, and video generation.
  - Useful implementation idea: production path through queue + cloud API, local fallback for dev/debug.

- Jewelry Photoshop AI Automation: https://github.com/DEEGANT2010/Jewelry-photoshop-AI-automation
  - Local Node.js batch workflow for jewelry boards: split, clean, enhance, logo branding, compress, ZIP.
  - Useful because it is not model-centric. It solves a real seller batch-processing shape.

- AI Product Placement Tool: https://github.com/imansarwar/AI-Product-Placement-Tool
  - Streamlit + rembg + Pillow product-background placement.
  - Simple but clarifies the baseline: remove background, position product, choose/upload background, download.

- Product placement / product image enhancer family:
  - https://github.com/Avishin0418/Generative-AI-product-placement
  - https://github.com/amitdeo28/ai-product-image-enhancer
  - https://github.com/rahuljoshi1814/GenerativeAI-Product-Placement
  - https://github.com/matte1782/product-image-optimizer
  - https://github.com/Manoj-bp/Snap-to-Sell

These small projects converge on the same primitives: matting, crop/center, background replacement, shadow/lighting, resizing, presets, marketplace export.

### Broader model/tooling references

- Open Generative AI: https://github.com/Anil-matcha/Open-Generative-AI
- imaginAIry: https://github.com/brycedrennan/imaginAIry
- Awesome GPT4o / GPT Image prompts: https://github.com/jamez-bondos/awesome-gpt4o-images
- Nano Banana editor: https://github.com/markfulton/NanoBananaEditor
- ComfyUI QwenVL: https://github.com/1038lab/ComfyUI-QwenVL
- ComfyUI IF AI tools: https://github.com/if-ai/ComfyUI-IF_AI_tools
- Replicate image MCP server: https://github.com/gomcpgo/replicate_image_ai
- bulkai: https://github.com/igolaizola/bulkai

Use these as adapters/tooling references, not as final product architecture.

## Amazon and Ozon platform implications

### Amazon

Community consensus:

- Main image: use real product photo or product-faithful render on pure white. Avoid AI lifestyle/background for the main image unless it remains compliant and accurate.
- Secondary images: AI is most useful for lifestyle, infographics, dimensions, use cases, comparison, A+ content, and ad variants.
- Product clarity beats beauty. Over-stylized fake-looking AI images can reduce trust.

Recommended Amazon slots:

- Main white-background product shot.
- Benefit card.
- Detail zoom.
- Size/scale reference.
- In-use/lifestyle.
- What is included / packaging.
- Comparison or objection-handling card.
- A+ brand story/module.

### Ozon / WB

Useful external signals:

- Ozon 3:4 marketplace-card shift discussed on vc.ru: https://vc.ru/id1660400/1792155-novyi-format-izobrazhenii-34-na-ozon-chto-eto-znachit-dlya-prodavcov
- Ozon/WB rich-content and AI discussion: https://vc.ru/marketing/1949397-rich-kontent-na-ozon-chto-eto
- Banana Pro / Ozon clothing-card case: https://vc.ru/id5396315/2284143-kak-uluchshit-foto-odezhdy-na-ozon-s-pomoshchyu-banana-pro

Practical implication:

- Ozon/WB are more template-card-heavy than Amazon. Strong borders, product-dominant 3:4 framing, short claim text, badges, icons, category color, and brand frames matter.
- AI generation should not redraw product. It should generate background energy, texture, props, and local decoration, then deterministic template layers should place product/text/badges.

## What to exclude

Exclude or downgrade:

- SD1.5-only workflows unless they demonstrate a still-useful preservation primitive.
- Pure Midjourney Discord automation that does not preserve exact product identity.
- Prompt-only ecommerce guides with no QA, no product reference, no batch export, and no compliance control.
- Generic "AI product photography tool list" SEO articles unless they expose workflow mechanics.
- Beautiful images with product drift.

## Recommended benchmark plan

Run a small, strict benchmark before choosing a production route:

### Inputs

- 3 SKUs:
  - hard-label product: supplement/packaging with fine text.
  - reflective/material product: jewelry or glossy accessory.
  - shape-sensitive product: electronics/auto accessory with ports/buttons.

### Models

- Nano Banana 2.
- GPT Image 2.
- Midjourney V8.1 or V7 with Omni-reference.
- Optional: FLUX.2/Kontext or Seedream only if cost/local control becomes important.

### Tasks

- Amazon white-background main image.
- Amazon lifestyle secondary image.
- Amazon infographic card with deterministic text overlay.
- Ozon/WB 3:4 high-impact card with frame/badge.
- Product kit: front/side/3-4/detail.

### Scoring

- Product fidelity: shape, color, label, logo, count, ports, material.
- Text correctness: direct model text vs deterministic overlay.
- Marketplace compliance.
- Mobile readability.
- Batch consistency across 6 outputs.
- Cost and latency.
- Human repair effort.

## Suggested system architecture

```text
ProductTruthPack
  source images, cutout, bbox, OCR, label/logo facts, forbidden changes

MarketplaceProfile
  Amazon / Ozon / WB constraints, aspect ratios, slot rules, copy density

SlotPlan
  buyer question, image job, slot type, reference style, required facts

PromptCompiler
  model-specific prompt for Nano Banana 2 / GPT Image 2 / Midjourney

GenerationAdapter
  model call, batch queue, retry, budget, output manifest

DeterministicRenderer
  product placement, text, badges, frame, icons, dimensions, export size

QAReport
  VLM/product checks, OCR/text checks, marketplace checks, artifact checks

RepairLoop
  reroll prompt, local edit, deterministic fix, human review
```

## Current recommendation

For `photo_show`, the model route should be:

1. **Default exploration:** Nano Banana 2 for fast product-background/style variants and Ozon/WB-style visual directions.
2. **High-fidelity candidate/final render:** GPT Image 2 when label/text/editorial composition matters.
3. **Aesthetic exploration:** Midjourney V8.1/V7 for moodboard, background, style reference, and high-impact campaign language, then preserve product through composite or a second model.
4. **Delivery layer:** deterministic frame/template renderer, not model-rendered text as final.
5. **Production gate:** product fidelity QA before any image is accepted.

The key product decision: build around **ProductTruthPack + SlotPlan + QA/reroll**, not around a specific framework. Models will keep changing, but product truth, marketplace slot logic, and QA remain stable.
