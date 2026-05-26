# Case Notes

This file stores richer notes for high-signal cases after the source is added to `sources.csv`.

## High-Signal Cases Added In First Deep Pass

### S023 HN: Nano Banana 2 / Gempix2 playground

Why it matters:

- This is not just a prompt page. It describes an actual SaaS/workflow wrapper around a model endpoint.
- Stack: Next.js, React, TypeScript, Tailwind, Postgres, Drizzle ORM, `@fal-ai/client`, queue API, webhooks, status endpoints, Stripe.
- Workflows mentioned: 4K images, 10-image fusion, product walls, comparison shots, simple storyboards, CJK text inside images.
- Claimed early ecommerce case: three-person team moved from about 8 hours per product to about 45 minutes using 10-image fusion, text-on promo posters in Chinese, and simple infographics.

Extraction:

- Method: queue-backed model wrapper plus prompt library.
- Useful for us: source of architecture and product-wall/multi-angle batch idea.
- Needs verification: actual output quality, product fidelity, and whether 10-image fusion preserves SKU identity.

### S014 Reddit/fal: GPT Image 2 is live

Why it matters:

- Community-facing model launch wrapper with concrete ecommerce claim.
- Calls out labels, logos, packaging, ingredient lists as GPT Image 2 product-photography strengths.
- Gives a rough pricing range from low quality to high quality 4K.

Extraction:

- Method: use GPT Image 2 when text and packaging fidelity matter.
- QA requirement: OCR check after generation; product label should not be trusted blindly.

### S015 Reddit: product image to cat food commercial

Workflow:

1. GPT Image 2 generates a product kit: front, side, 3/4, open package.
2. GPT Image 2 generates a six-panel storyboard.
3. Seedance 2.0 animates selected frames into a commercial-style video.

Why it matters:

- Shows image generation as pre-production for video.
- Product kit and storyboard should become first-class output types, not only single images.

### S028/S030/S031 Bilibili: Chinese no-code ecommerce workflows

Observed from indexed Bilibili results:

- Coze + Nano Banana 2 one-click ecommerce main image + detail page.
- GPT Image 2 one-click cross-border ecommerce main image + detail page.
- One product image + one sentence -> AI marketing scene image.

Why it matters:

- Chinese creators are packaging image generation as workflow automation, not model demos.
- These are likely closer to seller expectations: upload product, select/describe goal, get main image/detail page.

Next action:

- Deep-open the actual Bilibili pages if accessible.
- Capture title, creator, date, duration, steps shown, and screenshot/thumbnail evidence if possible.

### S040 GitHub: DXFNT/dexfinity-product-ads

Why it matters:

- Uses Nano Banana 2 in a concrete multi-client product-ad pipeline.
- Claimed flow: imports from Gmail, generates through FAL Nano Banana 2, uploads to Drive, YAML config per client.

Extraction:

- This is a good reference for business-workflow integration.
- It suggests the input is often not a clean web form; it may arrive by email, shared drive, or client folder.

### S046 GitHub: Brand Shoot Kit

Why it matters:

- The strongest architecture pattern so far:
  `URL -> Scout -> Preserve -> Shot Plan -> Generate -> QA -> Reroll -> Export -> Review Frontend`
- It separates product truth from generation and explicitly makes QA/reroll part of the workflow.

Extraction:

- Copy the architecture, not necessarily the code.
- The review frontend and output manifest are important for seller/agency handoff.

### S049 GitHub: Jewelry Photoshop AI Automation

Why it matters:

- Not a fancy model project, but a real batch-processing shape.
- Upload jewelry board -> split into products -> clean background -> enhance color -> add logo -> compress -> ZIP.

Extraction:

- Many seller workflows need deterministic batch cleanup before any generative model is used.
- Batch export and ZIP handoff are practical requirements.

## Website Case Patterns

### GPT Image 2 commercial tool pages

Sources: S001, S005, S008, S009, S010, S052, S063, S064.

Repeated promises:

- Text-to-image plus image-to-image editing.
- Product photo upload or reference image.
- Product shots, campaign visuals, social ads, ecommerce packshots.
- Multi-ratio output and 4K/2K quality claims.
- Text rendering as a core differentiator.

What to record in next pass:

- Do they show actual before/after product examples?
- Do they expose batch generation controls?
- Do they preserve product or regenerate it?
- Do they offer API, queue, webhooks, Drive/export, or only browser UI?

### Nano Banana 2 commercial tool pages

Sources: S051, S056, S059, S060.

Repeated promises:

- Fast 4K/2K image generation.
- White-background product shots.
- Product catalog and marketing creatives.
- Many aspect ratios.
- Product/lifestyle image use cases.

What to verify:

- Whether they use official Gemini API, fal/gempix wrapper, or unknown proxy.
- Whether product reference image is supported.
- Whether batch/gallery/retry exists.

## Gaps Still To Fill

- Actual YouTube video pages with transcripts or creator steps, not just indexed snippets.
- More Reddit seller threads from AmazonSeller, FBA, ecommerce, productphotography, dropshipping.
- X/Twitter original posts and creator prompt threads, ideally direct URLs.
- Private blogs by creators/indie builders with workflow screenshots.
- Russian Ozon/WB tools and creator videos beyond search snippets.
- Chinese platforms beyond Bilibili: Xiaohongshu/知乎/公众号 may be less indexable and may need manual/browser collection.

## 2026 Amazon Seller Discussion Cluster

Sources: S107-S115.

The most useful fresh Amazon signal is not "AI replaces all product photography." The seller threads are converging on a narrower operating model:

- Main image: sellers are cautious. They either keep it real or use AI only for cleanup/white background if the real SKU remains exact.
- Secondary/lifestyle slots: this is where Gemini/ChatGPT/Midjourney/PhotoRoom style tools are being used heavily.
- A+ and infographic slots: sellers care about story, objection handling, dimensions, USP, trust and country-specific buyer behavior.
- One-product-photo-to-set: tools are appearing that claim to generate full Amazon sets from one product photo: hero, lifestyle, infographic and A+ style assets.
- Customer language mining: one high-value workflow claims to crawl reviews/Rufus/customer questions and convert pain points into image briefs. This is more interesting than prompt-only product photos.
- Video: seller advice is to start from real product visuals plus 3-4 benefit bullets, open with problem-solution in the first 5-8 seconds, and avoid synthetic-looking usage.

Negative/constraint evidence:

- Threads repeatedly warn that misleading product visuals can get listings pulled or damage trust.
- Fake AI humans, bad spelling and no clear real product-in-use image are called out as trust killers.
- For engineering/spec-heavy products, Nano Banana-style image editing can hallucinate exact dimensions, internal structures and cutaways.

## Russian Ozon/Wildberries Case Cluster

Sources: S116-S122.

These are concrete website cases, not just opinions:

- Sozdai: upload photo or paste product URL -> AI analyzes product, audience, objections and SEO -> generates marketplace infographic slides. It positions itself for Wildberries/Ozon/Yandex Market/Avito and supports repeated slide generation for a full card.
- Sozdai examples: apparel, cosmetics, electronics, home goods, food and kids categories. The useful design rule is "one slide, one message" and 3:4 format shared by WB/Ozon.
- Sozdai how-to: AI is fastest when SKU volume is above roughly 10 per month; a full card is usually 5-6 passes, not one giant image. This maps well to a batch pipeline.
- Twin AI Wildberries: gives explicit model routing: Nano Banana Pro for product-preserving edits/on-model, Flux 2 Pro for lifestyle, GPT Image 2 for infographic text, Ideogram 2 for text/price labels, Recraft for icons.
- Twin AI Ozon: maps the output set to Ozon requirements: 700x900 white-background main image, lifestyle scenes, 800x800 rich-content infographic and 5-second video preview.
- Retail.ru/Wildberries: platform itself is moving into AI video and live-photo generation for sellers, which means seller tooling must handle image-to-video as part of the listing media stack.

## Bilibili Chinese Workflow Cluster

Sources: S123-S127.

Bilibili search snippets show a different workflow culture than Reddit:

- Coze + Nano Banana 2: "one workflow" that outputs main product image plus detail page, positioned as a from-zero tutorial.
- ChatGPT/GPT Image 2 + Coze: one-click cross-border main image/detail page; explicitly mentions batch image sets, custom language/region and multi-site listing.
- GPT Image 2 Amazon workflow: supports Japan/US/Europe stations and multilingual output.
- Nano Banana 2 batch reverse engineering: reverse hot-selling main images and output an entire main-image flow.
- RunningHub/ComfyUI/Nano Banana/Gemini: detail-page generation with layered PSD output, which is valuable because sellers can hand-edit final typography and compliance details.

Important caveat: these Bilibili entries are currently recorded from indexed search snippets because direct Bilibili pages are CAPTCHA/API-gated in this environment. Next pass should use browser/video access where available and record exact BV URLs, screenshots and prompts.

## New Website/Tool Case Patterns

Sources: S128-S136.

- Rewarx and Nexscope: GPT Image 2 as Amazon listing text/layout engine. Useful as prompt-method sources, but claims like time reduction need independent verification.
- AuraTuner: workflow taxonomy around Amazon main image checker, A+ content image generator, comparison chart generator and product photo/video. This is a good reference for productizing internal tools.
- Topview GPT Image 2: single product photo to catalog, seasonal themes, A/B variants and transparent cutouts. It explicitly exposes a batch-size idea.
- GPT Image 2 Studio and IMGVID/GPT showcase: useful prompt galleries for ecommerce hero, lifestyle, 360-ready, packaging and comparison ads.
- GitHub Amazon listing simulator: not only generation; it connects PDP preview, A10 scoring, flat-file export and AI image editing. This is a potentially useful architecture pattern for validating listing images against marketplace context.

## Indie Founder and Automation Case Cluster

Sources: S137-S141.

- PixelPanda founder post is valuable because it exposes stack and unit economics, not just marketing copy. The workflow is phone product photo -> many studio-quality shots; stack is FastAPI, Replicate Flux models, Cloudflare R2, MySQL, Stripe, Jinja2/vanilla JS, Ubuntu VPS. It also records failure modes: CAC, low-price trust, free-tool traffic not converting, and commoditization.
- PixelPanda tool site has moved toward product URL input, product scenes, UGC video ads, ad creatives, marketplace coverage and batch API. This is a good website case to track because the founder post and live positioning can be compared.
- Seedance 2 article adds a video-specific model route: Nano Banana Pro for still product/character references, Seedance 2 for reference-driven motion, ElevenLabs/Wan Animate/Topaz as post-production complements.
- n8n template article is useful as workflow architecture: Telegram-triggered product media production, product-page URL scraping, Firecrawl -> video model pipeline, and batch output for 50+ SKUs.

Practical extraction:

- For image tooling, product URL ingestion is becoming as important as raw photo upload.
- For video tooling, the core pattern is "lock references first, then generate motion." This mirrors the product-fidelity rule for still images.
- For SaaS/product design, trust and distribution may be a harder problem than generation quality; website cases should record pricing, free tools, batch/API, and marketplace-specific promises.

## Marketplace Tool Comparison and Prompt Practice Cluster

Sources: S142-S151.

- ReFramedShot, GPT Image 2 wrappers and Product Hunt launch mirrors show common website language: upload image or use reference photo, choose marketplace/channel, generate lifestyle/studio/campaign variants, bulk export.
- Comparison blogs are useful because they force marketplace constraints into the evaluation: Amazon pure-white main image, Etsy disclosure, Shopify integration, API batch processing and per-image cost math.
- Reddit app-builder threads around AiShots and Shopify bulk tools repeat the same input pattern: one rough supplier/phone image -> multiple realistic product images -> chat/edit loop -> preserve product shape/logo/fabric.
- Conversion-oriented Reddit workflow says the slot plan matters more than one cinematic hero: buyer objections, dimensions, features, use cases and trust signals should drive the generated set.
- Lens/camera prompting remains a small but recurring practical method: product prompts specify 85mm/50mm, f-stop, softbox/window light, rim light, realistic shadows and subtle grain to reduce the synthetic look.

## Code and Workflow Implementation Cluster

Sources: S152-S160.

- n8n templates are becoming an actual framework layer for product media automation. The common architecture is trigger -> scrape or receive product input -> prompt generation -> image/video model call -> Drive/object storage -> optional publish.
- Product-page-to-video workflows matter because sellers do not always start from clean creative briefs. They often start from a live PDP or Shopify/Amazon page and want the workflow to infer assets and benefits.
- WooCommerce virtual try-on repo shows a structured batch path: Google Sheets rows provide model/product images, AI generates clothing visuals, output goes to Drive/FTP/WooCommerce.
- Amazon OPC Agent OS links image generation with listing/Rufus/COSMO optimization. That suggests future systems should connect image generation to listing SEO and review intelligence, not keep it isolated.
- Shopify and ComfyUI repos show the lightweight open-source route: background removal, studio-shot generation, FastAPI/ComfyUI backend, and UI wrappers. These are smaller frameworks worth inspecting before building anything heavier.

## Chinese Video Platform Detail-Page Cluster

Sources: S161-S163 plus S123-S127.

New evidence from indexed Bilibili/Douyin pages:

- RunningHub/ComfyUI workflow advertises one-click ecommerce detail page generation in about 100 seconds, using Nano Banana + Gemini 3.0, layered PSD and Taobao/Amazon detail-page framing.
- Douyin topic page aggregates GPT Image 2 ecommerce detail page content: GPT Image 2 + Coze, Amazon product detail image generation, competitor scene replication and one-minute detail-page generation.
- Bilibili indexed results include API batch generation of product main images. That means Chinese creator workflows are moving from manual prompt demos toward API/workflow batch production.

Practical extraction:

- Layered PSD handoff is a serious implementation pattern: AI can generate page sections quickly, while humans keep final control over typography, claims and compliance.
- Chinese workflows put more emphasis on full detail pages and batch template output than Western Reddit threads, which focus more on single listing image sets and AI photography tools.

## X / Prompt Community Cluster

Sources: S164-S167.

- X direct post by Kaan gives a product infographic recipe: product photo/render plus black technical annotations, component labels, material notes, history and multiple product angles. This maps directly to Amazon/Ozon/WB feature-explainer slots.
- Atlabs guide aggregates X-sourced GPT Image 2 prompt templates. Useful patterns include exact-text ecommerce shot, multi-reference merge and preserve-list editing.
- GPT Image 2 launch aggregator is useful mainly as an X index: launch posts emphasize text rendering, API rollout and consistent image generation.
- GPT Image 2 prompt gallery gives repeatable structured prompt examples; this can seed a prompt/template benchmark later.

## Midjourney V8/V8.1 Cluster

Sources: S168-S170 plus S086-S093.

- V8 sources position Midjourney as stronger for product photography, photorealism, speed and readable short text than older versions.
- V8/V8.1 is not automatically better for ecommerce production. The important caveat is reference/control support: some V8.1 API wrappers report no Omni Reference and weaker negative prompt support.
- Practical routing: use Midjourney V8/V8.1 for premium visual exploration, editorial product concepts and ad key visuals; use GPT Image 2 or Nano Banana Pro when exact text, reference-preserving edits or strict product compliance matter.

## New YouTube Queue

Sources: S171-S177.

High-priority videos to watch next:

- S171: Nano Banana Pro prompt secrets for ecommerce and Amazon.
- S172: Amazon Seller University on Amazon AI Studio product photos/videos.
- S173: Russian Wildberries neural-network card infographic tutorial.
- S174: n8n + Nano Banana + Veo3 AI brand launch workflow.
- S175: GPT Image 2 vs Nano Banana UGC tests.
- S176: Nano Banana Pro one-click infographic generation.
- S177: Nano Banana product photography tutorial.

These are marked `needs_watch` because oEmbed/title metadata proves existence, but exact steps/prompts still need video inspection.

## YouTube Transcript Extraction Pass

Sources: S171, S172, S174, S175, S176, S177.

Raw subtitle files were captured under `raw_youtube/` for six high-priority videos. The Russian Wildberries video S173 hit YouTube 429 during subtitle download and remains `needs_watch`.

### S171: Nano Banana Pro prompt secrets for Ecommerce and Amazon

Useful workflow details from transcript:

- The creator frames the output as complete Amazon/ecommerce listing assets, not just standalone product photos.
- Prompting strategy 1: natural-language prompt with final use case and vibe words.
- Prompting strategy 2: ask ChatGPT/Claude/Gemini to write the image prompt, then edit it.
- Listing image slots mentioned: primary image, lifestyle/in-use shots, benefits graphics, feature graphics, competitor comparison, instructional step-by-step and dimensions.
- Strong practical claim: tell the model the final use case, e.g. "used on an Amazon listing"; that lets it infer color, contrast, scale, ratio and composition.
- Important constraint: include "mobile optimized" for graphics because text needs to remain readable on phone screens.
- Reference images matter more than prompt detail for exact product details. The transcript gives a diffuser example where a close-up reference of tiny button engravings helped preserve the detail.
- Reference set should include multiple zoom distances, angles and hand/in-context scale references.

Extraction:

- This is the clearest current Amazon image-slot prompt compiler source in the dataset.
- It supports a method where the image brief starts with slot intent and buyer use case, then adds reference images and only the most important constraints.

### S172: Amazon AI Studio official seller video

Useful workflow details from transcript:

- Amazon Seller University presents AI Studio as a native seller creative tool.
- Seller enters or selects product/ASIN.
- Amazon AI video generator can turn a single product image into videos automatically.
- Positioning is explicitly for small businesses that cannot afford agencies/studios.

Extraction:

- Platform-native generation is now a real branch of the landscape. This should be tracked separately from third-party tools because Amazon may define compliance and distribution constraints.

### S174: n8n/Nano Banana/Veo brand launch system

Useful workflow details from transcript:

- System starts with one generated product/brand image.
- User fills product description, style, lighting, palette, audience, brand essence, promise, tone of voice and positioning.
- System generates avatar options, including detailed age/gender/ethnicity/physical descriptions.
- System generates product asset ideas and then product images with one click.
- Prompts are auto-generated from brand DNA, style and lighting data.
- Same interface can generate UGC video or general product showcase video.

Extraction:

- This supports the "brand DNA -> asset ideas -> image/video fanout" method.
- It is more complete than a plain image generator because it stores structured brand fields and generates media variants from them.

### S175: GPT Image 2 vs Nano Banana UGC tests

Useful workflow details from transcript:

- Compares GPT Image 2, Nano Banana 2 and Nano Banana Pro for UGC/ad-like tasks.
- GPT Image 2 is tested with low/mid/high quality tiers; high quality reduces artifacts but costs more.
- Tests include character consistency, phone selfies, talking-head UGC frames, holding specific objects, background and outfit adherence.
- Multi-reference test includes character references plus object, background and outfit references.

Extraction:

- Useful as a model-benchmark method: run identical prompts and references through each model, compare not only beauty but also instruction adherence and cost.
- UGC learnings are adjacent to ecommerce because these frames often seed product videos and ad creatives.

### S176: Nano Banana Pro infographic generation

Useful workflow details from transcript:

- Tool path: HitPaw Edimakor -> Media AI Image -> Image Generator -> Reference Image -> Nano Banana Pro.
- Upload reference images. The transcript lists product images, fashion photos, screenshots and rough layouts as acceptable references.
- Prompt should describe output type, theme/content, visual style, layout/elements and detail requirements.
- Then choose resolution, aspect ratio and output quantity.
- Built-in templates mentioned: architecture line art, e-commerce sales pie, AI plant infographic, fashion cutout and teaching diagram.

Extraction:

- Relevant to Amazon/Ozon/WB infographic card slots, especially when paired with product facts and OCR/claim QA.

### S177: Nano Banana/Gemini product campaign fanout

Useful workflow details from transcript:

- Starts with one product image and turns it into five campaign images.
- Creator explicitly tests product consistency across outputs.
- Prompts combine product reference plus scene references.
- Repeated constraints: logo should be visible, fingers should not cover logo, product should contrast with background, can/product should remain centered or visually dominant.
- Example campaign patterns: hand punching through wall holding product, lime pile/fresh ingredient scene, balancing product on fingertip, mountain/nature contrast.

Extraction:

- Strong support for the "one product photo -> campaign visual fanout" workflow.
- Product truth controls are mostly prompt/reference based, so this is better for campaign/secondary imagery than strict main images.

## Small Seller Hybrid Workflow Cluster

Sources: S178-S180.

Reddit ecommerce and photography discussions add a practical constraint missing from many tool pages:

- Most small sellers are not replacing the whole shoot. They are taking better source photos with phone/window/lightbox/softbox, then using AI or editing tools for background cleanup, shadows, lighting and lifestyle variation.
- Several comments emphasize catalog consistency: same angle, focal distance, shadow treatment, crop ratio and edit preset across products.
- Gemini/Google Product Studio is repeatedly mentioned as useful for preserving product shape while improving backgrounds.
- PhotoRoom, Canva, remove.bg, AdMake AI, Lume Pics, Runable, PortraitDrop and DropShot appear as practical tools in seller comments.
- Trust warning is recurring: for handmade/art/jewelry and authenticity-sensitive categories, over-polished AI images can backfire.
- One comment reports a private ComfyUI-style Amazon clothing workflow using product pictures, text descriptions and skeletal positioning to generate hundreds of product/model variations. This is unverified but directionally important for apparel.

Extraction:

- For real sellers, the safest production stack is often "real photo as truth anchor + AI for context and consistency", not pure text-to-image.
- This aligns with Ozon/WB/Amazon risk: main image and exact product views need real/ref-anchored assets; AI is more valuable for secondary/lifestyle/infographic/UGC slots.

## Chinese API Batch Tool Cluster

Sources: S181-S187.

Chinese sources show stronger emphasis on high-throughput operational tooling:

- Poify AI: ecommerce image tool from Kuaishou/StreamLake. Claimed capabilities include AI model try-on, background replacement, local redraw, enhancement, visual workflow and API batch. The notable operational detail is folder upload plus API handling around 500 images.
- Tongyi Wanxiang guide: four batch patterns: same product with multiple backgrounds, multi-SKU prompt templates, API task queue, and asset-library derivative generation.
- Alibaba/Qwen developer content: API-oriented ecommerce main image and multi-angle product image generation, with batch efficiency framed as a core differentiator.
- Vmake.ai API integration: product info in backend -> API pulls product images/materials -> generates platform-specific videos/posters -> designers sample-check.
- Bilibili search results continue to show GPT Image 2 batch detail-page generation and tutorials for repairing AI edit blur/structure collapse.

Extraction:

- The Chinese ecosystem is closer to "API factory / workflow factory" than one-off prompt demos.
- The strongest reusable architecture is SKU table or folder input -> prompt/template expansion -> async API task -> callback/download -> designer sampling -> CMS/upload.
- This is directly relevant to batch ecommerce image generation and should influence final recommendations.

## YouTube Transcript Extraction Pass 2

Sources: S066, S074, S075, S082, S088, S090.

Additional raw subtitle files were captured under `raw_youtube/` for six more videos. `5HpR4sTBkGI` hit YouTube 429 and `8rycEe5EFYQ` had no requested subtitles available.

### S066: Nano Banana Pro step-by-step Amazon listing set

Useful workflow details from transcript:

- The creator explicitly positions Nano Banana Pro as a way to create a full Amazon listing image set from phone-camera product photos.
- Input collection matters: multiple angles, close-ups of buttons/ports/engravings/display, and hand/scale references.
- The workflow starts from a real physical product in the user's space, not pure text-to-image.
- The creator shows primary Amazon listing image generation and says roadblocks are expected; iteration is part of the workflow.

Extraction:

- This reinforces that the highest-fidelity ecommerce workflows collect a mini ProductTruthPack before prompting.
- For Amazon, the "phone camera + multiple reference angles" route is more practical than trying to generate the product from text.

### S074: n8n product photography automation

Useful workflow details from transcript:

- Front end can be Lovable or native n8n form.
- Upload accepts JPG, PNG, WEBP, JPEG.
- HTTP request uploads the image to Cloudinary.
- OpenAI analyzes the image into structured metadata: product identity, physical attributes, colors, materials, shape, labels, branding, context, brand positioning and target emotion.
- Prompt generation is JSON-based and category-agnostic.
- Results and prompts are stored in an Airtable backend; creator generated about eight images per run.
- Caveat: intricate details and lots of text are not always consistent.

Extraction:

- This is a concrete automation architecture: form/webhook -> Cloudinary -> product-analysis JSON -> prompt JSON -> Nano Banana Pro -> Airtable/gallery.
- It is useful for building an internal product photography system, but needs QA around text/labels.

### S082: Shopify GPT Image 2 automation

Useful workflow details from transcript:

- Treats visual production as a software-engineering pipeline rather than chat prompting.
- Separates brand logic from throughput: a custom GPT/brand spec stores hex codes, font stacks and photography recipes.
- Uses 16 image reference arrays and explicit reference indexing so the prompt specifies which trait comes from which image.
- Uses exact quoted text and negative constraints to prevent duplicate text or watermark artifacts.
- Shopify upload path uses GraphQL staged upload: `stagedUploadsCreate`, direct upload to Google Cloud Storage, then `fileCreate`, then polling file status.
- Mentions periodic audits every 50 generations to tighten the brand spec and reduce drift.

Extraction:

- This is one of the most implementation-specific Shopify catalog workflows collected so far.
- It should become a major architecture option in the final report, though pricing/capability claims must be verified against official API docs before production.

### S090: 1000 AI product images lessons

Useful workflow details from transcript:

- Creator says common failures are bad generators, overcomplicated prompts and images that look obviously AI.
- Fake-looking textures, bent labels, unnatural lighting, impossible shadows and near-brand text kill trust.
- Recommends a product-reference workflow so AI locks onto uploaded product instead of guessing.
- Uses Flux Dev/Omni Reference in OpenArt and advises turning off auto-enhance for product photos because it can invent unwanted details.
- First run should generate multiple variations, then choose the best direction.

Extraction:

- This is a practical trust/QA source: simple prompts plus product-reference mode outperform long prompt stuffing.
- It adds a concrete warning that auto-enhancement can damage product truth.

### S075: Nano Banana 2 downgrade complaint

Useful workflow details from transcript:

- Creator argues Gemini app routing now forces Nano Banana 2 first and makes Nano Banana Pro harder to access on the first prompt.
- For ecommerce/Amazon product images, he claims Nano Banana 2 is materially worse than Pro.
- Important not because the claim is universally proven, but because it records model-routing instability and version drift as a business risk.

Extraction:

- Production systems should not hard-code "Nano Banana" as a single stable capability.
- Record exact provider/model route and add regression tests against a known product-image benchmark.

### S088: Real photography over AI

Useful workflow details from transcript:

- Brand chose a real underwater set with fish and real lighting instead of AI.
- Creator says AI production is not always a solution.
- Some imperfections were intentionally not retouched to preserve authenticity.

Extraction:

- This supports a decision gate: high-trust/hero campaigns may need real set photography even when AI could approximate the scene.
- Useful for final recommendations because not every ecommerce image should be AI-generated.

## Gist / Product Hunt / HN Expansion

Sources: S188-S199.

- Gist sources add lightweight reusable prompt frameworks. The Midjourney V8 guide is especially useful because it recommends `--raw` for product photography, consistency and literal control, while keeping text short and using `--hd` for final renders only.
- Nano Banana prompt skill gist reinforces "purpose/use case" and "edit, do not reroll" as prompt principles.
- HN sources are mostly risk/limitation signals: AI ecommerce photos can fabricate fit/space, masking/fine-detail preservation remains hard, and product placement can mismatch references.
- Product Hunt tools show the current productization pattern: one product photo -> complete photoshoot -> studio/lifestyle/model shots -> optional video/UGC -> export to Shopify/Amazon/Etsy/TikTok.
- New productization angle from KREV/Adject: ad signals, tracked brand data, upload-once product asset reuse, visual iteration instead of restarting every generation.

Extraction:

- Product Hunt confirms the market is converging on persistent product assets and brand/ad-signal guidance, not only prompt boxes.
- HN confirms trust and product truth must be treated as first-class constraints in the final framework.

## Platform And Seller Community Expansion

Sources: S200-S212.

### Amazon Seller Forum and platform-native tools

- Amazon Seller Forum official-style content promotes an AI-Powered Image Generator in Amazon Ads Console.
- Claimed workflow: select ASIN -> generate multiple lifestyle images -> choose from 50+ thematic backgrounds -> use in Sponsored Brands, Sponsored Brands video, Sponsored Display, A+ Content and Stores.
- Seller question in the same context asks whether AI-generated lifestyle imagery can be used as the listing main image. This is important because it shows the boundary is not obvious to sellers.
- Separate seller forum case says Amazon inserted an AI-generated 360 image that displaced one of the seller's intended image slots. This is a platform-control risk, not just a generator capability.
- Amazon listing-generation announcement shows another branch: generative AI for product listing creation from direct-to-consumer websites, with seller concern about AI-generated labeling/badging.

Extraction:

- Amazon native tooling is now part of the workflow landscape and should be treated separately from third-party tools.
- Main image eligibility, automatic media insertion and seller control are active risk areas.

### Shopify seller/community signals

- Shopify community apparel thread shares AI human-model photo testing and claims category-specific lift for t-shirts and jeans/pants. The data comes from an AI tool/app context, so treat it as a lead, not proof.
- Shopify product-photo quality thread highlights a non-AI but critical constraint: close-up details of fabric/buttons/materials/condition matter, and sellers may need supplier photos or their own sample shoots.
- Shopify CDN/downscaling thread shows technical image-quality risk: fashion sellers care about detail visibility and compression/downscaling can degrade listing quality.

Extraction:

- Shopify workflows should not only generate images; they must preserve detail and upload/display quality through Shopify CDN/theme constraints.
- For apparel, AI model photos are promising but detail shots remain a product-truth requirement.

### Ozon/Wildberries Russian seller ecosystem

- Ozon official seller content says AI can improve image quality, remove old backgrounds and generate new backgrounds in the seller media step.
- The same Ozon content says product cards must include real photos so buyers understand actual product appearance. This is a major boundary for pure AI generation.
- VC.ru WB/Ozon examples show virtual try-on and card creation from reference photos, including replacing clothing on a model while preserving pose/face/details.
- Russian card guides repeat a practical listing pattern: main image should be clear, realistic and neutral; secondary cards can be more stylized/infographic-heavy.
- Another VC.ru tool roundup frames 2026 WB/Ozon image work as photos + backgrounds + infographics + descriptions + SEO + Telegram bots.

Extraction:

- Ozon/WB workflows are strongly card/infographic oriented, but still anchored by real product photos.
- Russian sources reinforce a two-layer model: conservative main image + more aggressive secondary selling cards.

### X-indexed and blog workflow additions

- Twstalker-indexed X profile snippets around Miguel/angryPenguinPNG show Nano Banana Pro + JSON prompting for UGC from product photos, with Wan 2.2 Animate for video.
- Stork AI blog describes a more explicit automation route: reverse-engineer high-performing X visuals into JSON prompt templates, trigger Nano Banana Pro from CRM/Airtable, then push to Buffer/Hypefury.
- AI Clothes Changer adds a fashion-specific virtual try-on case using Nano Banana Pro, GPT-4O, Flux and Seedream.

Extraction:

- X-origin workflows are often prompt/style innovation sources, but direct X access is weak. Aggregators can help discover leads, while final claims need direct capture when possible.
- JSON prompting is recurring across n8n, X creator workflows and prompt-engineering gists.

## Website Case Ledger Added

Created `website_cases.csv` as a dedicated cross-site comparison table. It records:

- website/tool URL
- case type
- model or stack
- marketplaces
- input assets
- workflow summary
- batch/export mechanism
- product truth / QA boundary
- current verification status

Initial rows cover Amazon AI tools, Ozon Seller AI, Sozdai, Twin AI, Poify, Tongyi/Qwen workflows, Product Hunt tools, n8n workflow templates, Shopify GPT Image 2 pipeline, PixelPanda, AuraTuner, Topview, SellerPic, KREV, Adject, Stork AI and fashion virtual try-on cases.

## Official Platform and Research Architecture Expansion

Sources: S213-S229.

### Amazon Ads official pages

- Amazon Creative Studio/Creative Agent is more advanced than a single image generator. The official page says the agent asks for product webpages, Amazon PDPs, relevant audiences, brand guidelines and previous brand ads/images.
- The workflow then proposes concepts/taglines, creates storyboard visuals, generates images, animates scenes, creates voiceover/music and can deliver video/display ads across Amazon Ads placements.
- Amazon Image Generator official pages emphasize actual product images plus product descriptions/customer reviews as input to generate lifestyle images.
- Amazon frames this as ad creative, not as blanket permission for listing main images. This distinction matters because seller-community threads show confusion about main-image eligibility.

Extraction:

- Amazon native tooling is a platform creative stack: product/audience research -> concepts -> storyboard -> generated assets -> Creative Asset Library -> ad placements.
- For final recommendations, treat Amazon Creative Studio as ad/lifestyle creative infrastructure, while keeping listing-main-image policy as a separate compliance gate.

### Research systems: CreativeAds and T-Stars-Poster

- CreativeAds paper identifies the core scaling issue: GenAI images can look realistic, but ecommerce ads need authentic product representation at scale, and manual intervention is usually required.
- Its architecture separates product pairing, layout generation and background generation, plus UI oversight and per-generation controls.
- T-Stars-Poster starts from product foreground image, taglines and target size. It uses four stages: prompt generation, layout generation, background image generation and graphics rendering.
- T-Stars-Poster is especially relevant because it treats foreground/product and graphic rendering as controlled stages instead of asking one model to do everything at once.

Extraction:

- These papers validate the direction emerging from community tooling: split product truth, layout, background and text/graphics into separate steps.
- Internal production should prefer product foreground/cutout anchors and deterministic layout/rendering when text, taglines, SKU accuracy or marketplace compliance matters.

### Conversion and trust discussion expansion

- AmazonFBA conversion thread warns that AI images can look clean but lose raw product clarity, which reduces purchase confidence.
- PPC thread recommends 3-4 base concepts and 10-15 variations each, with real product cutout placed into AI-generated scenes.
- Amazon Vine discussion adds buyer/reviewer backlash: misleading AI product photos should be called out, especially where compatibility or physical details are misrepresented.

Extraction:

- The repeated advice is not "make prettier images"; it is "answer buyer questions fastest while preserving real product clarity."
- This strongly supports a testing matrix: isolate variables, test one image at a time, and keep real product/cutout as truth anchor.

### Open-source implementation stack notes

GitHub README/API inspection added these concrete implementation details:

- ProductFlow: Python/FastAPI backend, SQLAlchemy/Alembic, Dramatiq, Redis, PostgreSQL, Pillow, OpenAI SDK; React 19/Vite/TypeScript/TanStack/Tailwind front end. It stores product records, references, copy nodes, image sessions, gallery and settings.
- dexfinity-product-ads: Claude Code plugin; Gmail XLSX/XLSM import, FAL nano-banana-2 generation, OpenAI vision analysis, Google Drive upload, Google Sheets logging, multi-client YAML config and domain hard constraints for shoes.
- ai-ads-autopilot: CLI, Gemini Nano Banana 2 for stills, Claude for briefs/scripts, HeyGen for UGC video, product/creator photo inputs, autopilot loop.
- static-ads: product image + brand URL + CTA -> brand voice -> copy angles -> art direction -> layout -> copy review -> GPT Image 2 edit -> visual review -> format/language expansion. It has two explicit review gates.
- Witi Photo Studio: Shopify Polaris/Node app for Shopify product photography using background removal and Replicate SDXL.
- Aura Studio: FastAPI + ComfyUI/Stable Diffusion product-photo engine for constrained hardware.

Extraction:

- The serious small frameworks converge on queues, stored prompts, reference assets, status/galleries, review gates and deterministic expansion after one approved visual direction.
- The strongest reusable pattern is not a single prompt; it is an ops system with source ingestion, product analysis, prompt generation, model call, review, expansion, export and logging.

## Official Model Boundary Sources and YouTube Transcript Pass 3

Sources: S068, S069, S073, S083, S084, S085, S086, S091, S092, S230-S237.

### Official model boundary pass

- OpenAI GPT Image 2 official docs are now recorded as the capability source for GPT Image 2 ecommerce pipelines. The model page identifies text/image input, image output, high-fidelity image inputs, image generation/editing and snapshot `gpt-image-2-2026-04-21`.
- Google's Nano Banana 2 official launch/developer posts are now recorded as the capability source for the Google route. Relevant ecommerce signals are subject/object consistency, text rendering/localization, precise instruction following, native aspect ratios, 512px-to-4K resolution tiers, Google AI Studio/Gemini API access and paid API-key requirement.
- Midjourney V8/V8.1 official updates are recorded as the current Midjourney route. Useful ecommerce signals are `--raw` for more controlled photographic looks, moodboards/style references, HD/2K, faster V8.1 iteration and improved SREF/Moodboard quality.
- Midjourney Omni-Reference is recorded separately because it is a 2025 reference feature, not a 2026 model launch. It can inform object-reference workflows, but it is older, experimental and should not be treated as the main production route.

Extraction:

- Before choosing a model, the production system needs an "official boundary registry": model, date, supported inputs/outputs, size/aspect support, reference/edit controls, snapshot/version, known limitations and last verification date.
- GPT Image 2 and Nano Banana 2 are stronger candidates for API/batch image generation. Midjourney V8.1 is still strongest as a creative direction/moodboard/lifestyle concept tool unless product truth is anchored by another reference/edit/compositing step.

### YouTube transcript pass 3: product photo and video workflows

- Recraft + Nano Banana workflow (S068): use Recraft/style reference to define the look, use ChatGPT for prompt ideas, then use Nano Banana to place a real product into the scene. This is a practical "style lock + product reference" workflow for small teams.
- Freepik Spaces + Nano Banana 2 workflow (S069): Freepik Spaces acts as a node-based continuous workflow. An assistant/GPT node converts instructions into prompts, Nano Banana image nodes generate product shots, and video nodes can expand the result toward 360-style product video.
- Gemini/Nano Banana Pro phone-snapshot workflow (S073): rough phone images or multiple product angles become higher-end studio/luxury product photos. The useful part is not the phone snapshot itself; it is turning weak seller input into a structured product-reference request.
- Product/background replacement short demo (S083): fast background replacement is still a common small workflow. It should be classified as a secondary-image tool, not a full listing-factory method.
- ChatGPT/script-cloning product video workflow (S084): clone a winning ad structure, transcribe or summarize it, adapt the script with ChatGPT, plan scenes and generate product video ads. This belongs in ad-creative automation, not marketplace main-image generation.
- FLIK AI one-photo commercial workflow (S085): one product photo plus Q&A becomes a visual style document, asset/location plan, film grammar and commercial output. It is useful for product video and UGC-style ads.
- Midjourney + X-Design workflow (S086): Midjourney creates background/scene concepts with lighting, mood and camera settings; X-Design integrates the product. This is another version of the "AI background + real product insert" pattern.
- Midjourney + Photoshop agency workflow (S091): Midjourney supports brand-aligned product visuals when paired with Photoshop cleanup/compositing. It is better framed as an agency creative workflow than direct automated SKU generation.
- Midjourney product shot / moodboard workflow (S092): Midjourney product shots remain useful for website concepts, brand moodboards and early visual direction, but exact product, label and compliance checks remain external.

Extraction:

- Third-batch YouTube evidence reinforces three reusable patterns: style-reference lock, real-product insertion, and one-photo-to-video commercial generation.
- The recurring failure boundary is product truth: labels, dimensions, scale, material and marketplace claims still need OCR/VLM/manual QA even when the generated scene looks good.
- For Amazon/Ozon/WB listing production, the safest route remains: real product photo/cutout -> AI lifestyle/secondary scene -> deterministic text/layout overlays -> platform-specific QA/export.

## Community and Tool Expansion: GPT Image 2, Nano Banana 2, Bilibili and Amazon Seller Threads

Sources: S238-S256.

### GPT Image 2 ecommerce wrapper and prompt-guide cases

- Image2 (S238) positions GPT Image 2 as an ecommerce wrapper for rough product photo -> white-background listing image, lifestyle placement, multi-angle variations and packaging/text readability.
- Nexscope (S239) frames GPT Image 2 product photography as a brief-writing workflow rather than classic shoot/retouch. It explicitly mentions main images, ad creatives and localized versions.
- ImageGen2 (S240) gives a compact workflow: choose asset type, prompt like a creative brief, use reference image when accuracy matters, generate variations and refine in small steps.
- Atlas Cloud (S241) provides current prompt templates, including Amazon-style studio white-background product photography with soft lighting and drop shadow.

Extraction:

- GPT Image 2 ecommerce prompting is converging on slot-led briefs: asset type, setting, lighting, camera angle, style, must-keep product details and exact quoted text.
- The wrapper pages are useful for workflow taxonomy, but final capability claims should be bounded by official OpenAI docs and visual QA.

### Nano Banana 2 / Gempix2 small-framework cases

- Morphed (S242) is useful because it includes a product-fidelity caution: exact-match products should use real primary photography, while AI is better for supplementary lifestyle and campaign imagery.
- Show HN Gempix2 (S248) is a strong small-framework lead: Next.js + React + TypeScript + Tailwind, Next.js API routes, Postgres + Drizzle, fal-ai/Gempix2 queue API/webhooks and credit accounting.
- The HN case specifically calls out 10-image fusion for product walls, comparison shots and storyboards, plus CJK text rendering for posters/infographics.

Extraction:

- Nano Banana 2 appears especially interesting for CJK ecommerce posters, multi-image product walls and infographic-like assets.
- Product-wall workflows still need SKU-level verification because multi-image fusion can preserve overall identity while drifting small details.

### Amazon seller thread expansion

- AmazonFBA May 2026 thread (S244) confirms active seller use of AI for lifestyle shots, staging, mockups and angle testing. The recurring caution is main-image safety and product accuracy.
- AmazonFBATips thread (S245) adds concrete operational pressure: a full image set takes 4-6 hours, sellers value comparison charts and lifestyle shots, and generic AI outputs are rejected.
- Builder thread (S246) describes a more complete Amazon image system: 5 listing images, 5-6 A+ modules, desktop/mobile variants, hero banners, brand identity, style reference, global instructions and per-image edit/regenerate.
- FulfillmentByAmazon thread (S247) shows a hybrid practice: professional listing/main images, Nano Banana for A+ content, Canva for cleanup and an Amazon-tailored tool such as Saharan AI.
- A+ thread (S256) is a large-catalog case: a home-decor seller with roughly 500 ASINs tests no-prompt generation of A+ and 5 product images from a product image plus bullet points.

Extraction:

- Sellers do not just want "better images"; they want complete, coordinated slot sets that reduce production time while preserving control.
- A useful Amazon framework must model the whole image set: main, lifestyle, feature, comparison, dimension/detail, A+, mobile variants, alt text/export, and per-slot editability.

### Bilibili indexed Chinese ecommerce workflow leads

- Coze + Nano Banana 2 (S250): indexed as a 2026 tutorial for one workflow that generates ecommerce main images and detail pages from scratch.
- GPT Image 2 cross-border ecommerce (S251): indexed as one-click product main image + detail page generation for cross-border ecommerce.
- Nano Banana 2 hot-main-image reverse engineering (S252): indexed as a workflow that reverse-engineers bestselling product main images and outputs a complete batch flow.
- ComfyUI 100-second detail page (S253): indexed as a one-click ComfyUI workflow for ecommerce detail pages and main images.
- Ozon AI product picture tutorial (S254): indexed Chinese seller content on using AI for Ozon product pictures without Photoshop.
- Jimeng/Doubao/DeepSeek ecommerce design (S255): indexed workflow combining Chinese tools for main images, product visuals, detail pages and ad material.

Extraction:

- Chinese community workflows are more "agent/workflow canvas + batch detail-page factory" than single-image prompt collections.
- These need the next direct-video pass: exact BV IDs, screenshots, node graphs, prompts, output examples and whether the product body is preserved.

## X-Origin, GitHub Skill and Prompt-as-Code Expansion

Sources: S257-S270.

### Twitter/X-access workaround

- Direct X search is still unreliable, so current collection uses pages that embed or link original X posts.
- GPT Image 2 launch digest (S257) links OpenAI/OpenAIDevs X posts around launch, text rendering, reasoning/web search, API timing and model specs. These are useful leads, but official OpenAI docs remain the capability authority.
- Atlabs guide (S258) credits X creators and includes ecommerce prompt templates: simple sell-ready product ad, exact-label ecommerce shot and other reusable patterns.
- ZeroLu prompt repo (S266) also says prompts come from top X creators and includes Chinese ecommerce UI/product waterfall examples.

Extraction:

- X-origin content is most useful for discovering fresh prompt patterns, not for proving model capability.
- The safe ingestion rule is: capture original link -> tag use case -> extract prompt structure -> benchmark on a real SKU -> only then promote to method library.

### GitHub/MCP/Skill cases

- EvoLinkAI awesome GPT Image 2 repo (S263) is a large prompt/API pattern index with ecommerce, ad creative, poster, UI and comparison categories.
- shinpr/mcp-image (S264) is an MCP server for AI image generation/editing from Cursor, Claude Code and Codex, powered by Nano Banana 2/Pro with optional GPT Image support.
- YouMind prompt skill (S265) is a prompt-bank skill with Product Marketing and E-commerce Main Image categories, plus update automation.
- GitHub GPT Image 2 topic page (S267) shows a fast-growing ecosystem of prompt libraries, desktop apps, agent skills, local-first tools and OpenAI-compatible gateways.
- nanobanana-skill (S268) shows the "agent skill wrapping Gemini image tools" pattern, including reference-image composition, character consistency and product mockups.

Extraction:

- A practical small-framework direction is agent-triggered image generation: MCP/Skill -> prompt optimization -> model route -> output path -> metadata log -> review/export.
- Prompt-as-code libraries are useful only if kept fresh and benchmarked. Their real value is slot taxonomy and reusable prompt structure, not copy-paste prompts.

## Russian Marketplace and Real-Photo Service Workflow Expansion

Sources: S271-S283.

### Ozon/Wildberries/Yandex card tools

- Prodiger (S271) adds a Telegram-bot-like workflow: product-card photos, videos and descriptions for WB/Ozon, 5 photo variants per session and SEO descriptions.
- Ozon official docs (S272) reinforce that images are moderated and photos are required for sale in many categories. This remains the compliance boundary for AI-generated assets.
- Creator AI (S273) is one of the clearest full-card pipelines: upload 1-5 photos, Claude Vision analyzes product material/color/features, background removal creates a clean hero, image models create lifestyle photos and a spec infographic, then titles/descriptions/specs/SEO are exported as ZIP or preview link.
- Sozdai (S275) focuses on marketplace infographics and claims awareness of WB/Ozon 3:4 aspect ratio, product focus and safe zones.
- WildScan (S277) is more analytics-led: competitor article/SKU, SEO/card analysis, review data and optimized WB titles/descriptions/keywords.
- Kartinka (S278) expands into a broader marketplace-card factory: product photo or connected store -> background removal/replacement, model try-on, infographics, SEO descriptions and exports for WB/Ozon/Yandex.

Extraction:

- Russian marketplace tools are converging on a full-card factory: product photo -> vision analysis -> hero cleanup -> lifestyle/infographic -> copy/SEO -> ZIP/share/export.
- Compared with Amazon seller threads, WB/Ozon tools emphasize card-as-a-single-commercial-unit more than slot-by-slot A+ systems.
- The key QA gates are real photo anchor, 3:4 format, product focus, safe zones, generated copy/spec accuracy and marketplace moderation.

### Real-photo PDP/video service workflow

- Reddit automation thread (S281) adds a useful framing: use real photos, write tight prompts like API calls, and generate AI backgrounds/models plus 6-9 second product demo clips.
- AmazonFBA/AI-in-ecommerce threads (S282-S283) show continued demand for complete listing sets from one product photo: hero, lifestyle and infographics.

Extraction:

- Service workflows hide the underlying stack, so the evaluation should be output-led: product match, repeatability, editability, speed, cost and platform acceptance.
- For our internal framework, treat these as "real-photo-to-PDP/video creative brief services": useful as market proof, not architecture truth.

## Direct Bilibili BV, YouTube Transcript Batch 4 and Official WB/Ozon Media Rules

Sources: S076, S284-S299.

### Direct Bilibili BV capture

- Coze + Nano Banana 2 main/detail workflow (S284, BV1ykXVB1Eom): direct Bilibili API result says a Coze workflow can generate ecommerce main image plus detail page, with zero-to-one build demo.
- Feishu multidimensional table + Banana + Sora2 workflow (S285, BV1kgvSBaE2Q): direct BV result suggests spreadsheet/table rows can serve as batch-control plane for ecommerce image/video generation.
- Nano Banana Pro Amazon prompt tutorial (S286, BV1bYftB6EKK): direct BV result targets Amazon ecommerce images with Nano Banana Pro prompts.
- Coze + Nano Banana2 hit-main-image recreation (S287, BV1uwXQBtEs8): direct BV result says the workflow recreates hit ecommerce product main images and aims to improve click-through.

Extraction:

- Chinese workflow content is shifting from single prompt tutorials into workflow-canvas and spreadsheet-driven batch systems.
- The next required step is direct video watching/screenshot extraction for node graphs, prompts, input/output screenshots and product-fidelity checks.
- Hot-main-image recreation should be treated as a design-risk zone: it may help learn layout patterns, but direct copying of competitor visuals is unsafe.

### YouTube transcript batch 4

- GPT Image 2 product ads comparison (S288): transcript captured. The creator compares GPT Image 2 with Nano Banana Pro for product photography and product ads, focusing on text labels and the model's biggest weakness.
- Nano Banana Pro ecommerce/product graphics secrets (S289): transcript captured. The video positions prompt tricks as necessary for products with many parts or labels.
- Nano Banana Pro ecommerce/Amazon masterclass (S290): transcript captured. Uses difficult labeled product bottles and real-world use visualization as stress cases.
- Nano Banana 2 product photos (S291): transcript captured. Uses simple iPhone/reference images and explicitly shows the limit that exact product detail and taglines can drift.
- Amazon listing images, 360 video and thematic photography (S292): transcript captured. The workflow claims primary/secondary images, 360-degree view and A+ content without writing prompts, framing the real value as an agent around the model.
- GPT Image 2 Chinese ecommerce main/detail generator (S294): short transcript captured. User selects platform/category, uploads product photos, generates matching main/detail pages, copies competitor style and gets credits refunded if product mismatch happens.
- AM/PM Amazon AI product image podcast (S295): long transcript captured. Useful seller-service/agency evidence for AI Amazon product images in minutes, still needs deeper segmentation.

Extraction:

- The new videos strengthen two method families: no-prompt listing agents and reference-image model-comparison stress tests.
- "No prompt" should be understood as hidden prompt orchestration: the system infers slot briefs from product/category/platform inputs.
- Several videos mention refund/credit rules for product mismatch. This is a market signal that product-fidelity failure is common enough to need commercial guarantees.

### Official Wildberries and Ozon media rules

- Wildberries Photostudio (S296) is an official native neural-network photo tool. It supports two scenarios: put clothing on a virtual model, or replace the model/background in an existing photo. It includes monthly generation limits and input requirements.
- Wildberries card creation docs (S297) say cards can include up to 30 photos and one video. They list photo requirements, forbidden content such as prices/QR/discounts/contacts/evaluative claims/review rewards/calls to action, and native media tools such as photo editor, Photostudio, video covers, rich content and A/B tests.
- Ozon AI image editor (S298) officially supports AI edge extension, background generation/removal/deletion and quality improvement, with effect-specific requirements and limits.
- Ozon image requirements (S299) remain the hard QA gate: main photo must match product name/description, show the product clearly, have no watermarks and follow format/resolution/aspect guidance; infographics are allowed under rules.

Extraction:

- WB and Ozon now have native AI/media tooling, so seller workflows should not only compare external tools; they should also route some tasks through platform-native editors when compliance friction matters.
- For Ozon/WB, model output is not complete until it passes marketplace media requirements, moderation constraints, aspect-ratio expectations and product-truth checks.

## Bilibili Node Details, Reddit Production Signals and Open-Source Prompt/Media Frameworks

Sources: S284-S287, S300-S310.

### Coze/Nano Banana 2 node-level details

- BV1ykXVB1Eom description exposes a concrete Coze workflow skeleton:
  - inputs: product reference image `img_ref`, competitor/reference image `img_db`, product name `name`, `mihe_key`;
  - branch A: reverse-engineer competitor reference prompt -> generate product selling points -> generate ecommerce main-image prompt -> optimize prompt -> format conversion -> generate main image;
  - branch B: cutout/product crop -> format conversion -> generate detail-page image prompt -> generate detail-page image.
- BV1uwXQBtEs8 is a related Coze + Nano Banana2 hit-main-image recreation workflow. Its description emphasizes building the workflow by hand so sellers understand Coze nodes/plugins.
- BV1kgvSBaE2Q points to a Feishu wiki, suggesting another Chinese pattern: spreadsheet/wiki as batch-control surface for Banana/Sora2 image-video workflows.
- BV1bYftB6EKK says it covers two prompt strategies, reference-image impact and 22 image types for Amazon PDP optimization.

Extraction:

- The strongest Chinese workflow pattern now looks like: product reference + benchmark reference + product name -> prompt reverse-engineering -> selling-point extraction -> main image/detail page generation.
- This is more agentic than a prompt library and more structured than pure ComfyUI. It should be modeled as a two-branch pipeline: main-image branch and detail-page branch.
- Competitor-reference reverse engineering is useful for layout/style learning but carries design/IP risk if copied too directly.

### YouTube model-stress details

- GPT Image 2 comparison transcript (S288) focuses on text-label rendering and product ad graphics, with GPT Image 2 tested against Nano Banana Pro.
- Nano Banana Pro/Nano Banana 2 transcripts (S289-S291) repeatedly stress hard products: bottles with tiny labels, products with many parts, food packaging, brand graphics and exact taglines.
- The useful method is not just "use better prompt"; it is multi-reference stress testing with close-up product details, exact label checks and side-by-side comparison against source photos.

Extraction:

- A production model router should contain a benchmark gate before bulk use: test on small text, label placement, material/texture, multi-part products, and in-use visualization.
- Aesthetic quality is not enough. The image must survive zoom/OCR/product-detail comparison.

### Reddit production signals

- n8n workflow (S300) is a concrete small-framework shape: Telegram image input -> download -> background removal -> alignment/resize -> edge cleanup -> AI enhancement -> return clean ecommerce-ready product image.
- AIToolsAndTips thread (S301) says current production use is base product photo plus AI background/lighting polish; one commenter reports 3000-5000 new SKUs per month using AI-generated image sets.
- Consistency-bottleneck thread (S302) says one impressive hero image is easy; the hard part is 20 images for one SKU where shape, logo, material, color, stitching, shadows and packaging stay aligned.
- Conversion-oriented workflow thread (S303) proposes six prompt inputs: style, subject, action, scene, camera and brand. It also argues that boring-but-useful listing images can be better than a cinematic hero that does not answer buyer objections.
- Ecommerce thread (S304) reinforces real-photo-first for texture/material/trust and AI for lighting/background/model/environment optimization.

Extraction:

- The next architecture should bind generation to SKU/card facts and buyer objections, not isolated prompts.
- Real product photo remains the trust anchor. AI is strongest for cleanup, context, lighting, variants and secondary visuals.

### GitHub/Gist framework signals

- Midjourney V8 Gist (S305) recommends `--raw` for product/photoreal control, short double-quoted text, standard-grid exploration and `--hd` only for finals. It supports Midjourney as a concept/style loop rather than exact SKU engine.
- Open Design (S306) shows a local-first media pipeline with GPT Image 2 for stills, Seedance 2.0 for product films and HyperFrames for HTML-to-MP4 motion graphics.
- Cliprise prompt repo (S307) adds a broad prompt/workflow library covering Nano Banana 2, GPT Image, Flux, Seedream and Midjourney, with ecommerce/product photography workflow guides.
- GitHub Copilot skills listing (S308) is another signal that image generation is moving into agent/IDE skills, including GPT Image 2 and Nano Banana support.

Extraction:

- Small frameworks are splitting into three buckets: self-hosted workflow automation, prompt-as-code libraries and agent/MCP/media pipelines.
- For ecommerce, all three need an added product-truth layer: source refs, SKU attributes, prompt/version logs, QA gates and export targets.

## X Aggregators, Product Hunt and Wrapper Tool Expansion

Sources: S311-S325.

### X/Twitter evidence via aggregators

- Techmeme Nano Banana 2 digest (S311) preserves X-linked launch discussion from Google, DeepMind, AI Studio, Vertex and other accounts around Nano Banana 2/Gemini 3.1 Flash Image, API rollout, Image Search and real-time grounding.
- Ethan Holland Nano Banana 2 digest (S312) preserves many X links/snippets around launch and third-party analysis, including Artificial Analysis/Arena-style capability discussion.
- Ethan Holland GPT Image 2 digest (S313) preserves X-linked Arena/leaderboard discussion around GPT Image 2/Image 2, including product/branding and image-edit categories.

Extraction:

- X is best used as a freshness radar: launch signals, creator prompts, benchmark chatter and workflow experiments.
- Aggregated X evidence should never override official docs or controlled SKU tests. It should populate a watchlist and lead list.

### Product Hunt and independent tools

- Nano Banana 2 Product Hunt (S314) summarizes the launch/adoption surface: Google Ads, Vertex AI, AI Studio/Gemini, 4K, text/localization and subject/object consistency claims.
- ProductAI (S315) is an older but still relevant one-product-shot-to-scenes Product Hunt case.
- TraceUI (S316) adds a website-URL-to-on-brand-ads pattern: brand extraction from website colors/fonts/logos into campaign visuals.
- Duct Tape AI (S317) is a GPT Image 2 wrapper positioning itself for product listings, packaging mockups, ads and native text.
- Devoured GPT Image 2 guide (S318) contributes a concrete extraction/mockup prompt pattern: centered product, crisp edges, opaque background, label legibility and no halos.
- Bananai (S320) is a Nano Banana-family wrapper for product photo variations and image-to-video workflows.

Extraction:

- Independent wrappers increasingly hide prompt work behind template/preset/product-page inputs.
- The real reusable framework is not the wrapper itself; it is input normalization, model routing, product-reference persistence, output metadata and QA/export.

### Failure-mode and readiness signals

- GeminiAI thread (S321) is important because it shows Nano Banana 2 can change product identity while improving context, even if it may handle some detail-heavy tire sidewall text well.
- PromptingMagic guide (S322) provides product Photoshoot templates: Studio, Floating, Ingredient, In Use and Lifestyle.
- Bard thread (S324) points out watermark/free-plan constraints when using Nano Banana outputs in product images and video ads.
- Stylaquin fashion handout (S325) is a fashion-specific seller training lead and should be extracted later as PDF text.

Extraction:

- Commercial readiness is a separate gate from visual quality: watermark, license, tool plan, marketplace rules and brand/IP safety must be checked before upload or ad use.
- Product-preservation failure should be treated as expected, not exceptional, in any catalog-scale workflow.

## PDF Extraction, Benchmark Rigs and Russian Full-Cycle Marketplace Ecosystem

Sources: S325-S336.

### Stylaquin PDF extraction

The Stylaquin fashion-store handout was downloaded to `raw_docs/stylaquin_ai_product_images_handout.pdf` and extracted to text locally.

Useful extracted points:

- Nano Banana can create product images for ads, emails, websites and social media, but it is frustrating when prompts are vague.
- Prompt structure should specify: product shot, subject, place/context, style/medium, composition/camera, lighting, brand details and negative instructions.
- For product shots, upload the actual product photo as a reference and check carefully that the rendered image matches it.
- The guide explicitly says not to ask Nano Banana to add a logo because it is weak with text/logo placement; add logos as separate layers.
- Nano Banana does not do dimensions or fine retouching well. It can remove/replace backgrounds, but not precise cleanup.
- If a result does not work after roughly three attempts, restart with a changed prompt/reference name rather than endlessly editing the same generation.

Extraction:

- This is a practical seller-facing QA doctrine: reference images, no AI logos, separate retouching, restart policy and hallucination checks.
- It supports a fashion-specific workflow where AI handles scene/style while product identity and brand marks remain controlled layers.

### Open-source benchmark and workbench frameworks

- `nateherkai/gpt-image-2-vs-nano-banana-2` (S328) is a reusable evaluation architecture: 30 matchups, source-image uploads, resumable state file, model API calls, Claude-as-judge and a dashboard.
- `image-battle` and `gpt-image2-vs-nano-banana2` (S329-S330) add lighter UI patterns: blind comparison, hidden model names, randomized left/right, vote rate limiting and leaderboard.
- `StartripAI/gpt-image-2.0-workbench` (S331) is especially relevant for production: executable YAML templates, prompt-only/API/Skill paths, preflight validation, cost estimates, batch dry-run and local ledger.
- `lucaswalter/n8n-ai-automations` (S332) includes Nano Banana ad workflows: on-brand ad generation, competitor Facebook/Instagram ad scraping, Firecrawl brand-guideline extraction, 10 A/B variations and Google Drive export.

Extraction:

- Model selection should be benchmarked as an internal system, not debated by screenshots.
- The best framework pattern now combines spec-first prompt templates, preflight validation, cost modeling, run ledger, product/source references and human/model judge rubrics.
- n8n ad workflows show a separate pattern: competitor ad -> brand guideline extraction -> controlled single-variable variants -> review/export.

### Russian marketplace ecosystem expansion

- Habr guide (S333) describes an AI Berry Telegram bot optimized for Yandex Market, Megamarket, Ozon and Wildberries. Workflow: choose marketplace, upload product photo, provide characteristics, receive image and description. The same bot/service family includes video, UTP, branding/naming, reviews/analytics, infographics and SEO.
- vc.ru marketplace-card guide (S334) frames 2026 AI card tools as full-cycle ecosystems, not just image generators: image generation, infographics, background generation, review replies, SEO fields, templates and A/B testing/analytics.
- vc.ru photo/video guide (S335) claims video content affects WB/Ozon behavior/ranking signals, and positions AI video/photo generation as a card-content operation.
- vc.ru infographic guide (S336) claims one-minute six-slide infographics and CTR/CVR uplift, but the source is marketing-like and should be treated as directional.

Extraction:

- Russian marketplace tooling is now clearly a full-card ops stack: photo, infographic, video, text, SEO, review analytics, marketplace templates and A/B tests.
- Performance uplift claims in these articles are weak unless backed by platform data. Keep them as market claims, not evidence.

## Amazon and Shopify Seller Community Expansion

Sources: S337-S346.

### Amazon Seller Forum: catalog image risk

- Seller Forum main-image overwrite case (S337): seller reports Amazon automatically replaced the main image with a wrong white-background image. The wrong image mismatched product quantity, material, design and shape, and the seller could not edit/restore it through normal image tools.
- Seller Forum image-change case (S339): refurbished console seller reports product images/titles changing to random seller images with extra accessories, causing returns because customers expect the pictured item.
- Older listing AI thread (S340): seller says listing AI caused picture update problems and resolution required support to compare seller website images against Amazon listing images.

Extraction:

- Amazon image work needs a monitoring layer after upload. The risk is not just model hallucination during generation; platform catalog systems may choose or alter images later.
- Amazon workflows need source-photo archives, PDP monitoring, mismatch detection and escalation packets with screenshots/source website references.

### Amazon Seller Forum: AI image generator and slot ambiguity

- Seller Forum AI Image Generator promo/discussion (S338) describes Amazon Ads Console image generation for lifestyle visuals and placements such as Sponsored Brands, A+ Content, Stores and Sponsored Display.
- A seller asks whether AI lifestyle images can be used as main product photo or only for other listing/ad creatives.

Extraction:

- Amazon slot taxonomy must stay explicit: main image, secondary/lifestyle, A+, Stores and ad placements are not the same compliance surface.
- Treat Amazon AI Image Generator as ad/lifestyle infrastructure unless current policy specifically proves a listing-main use case.

### Shopify Community: native tools and app workflows

- Shopify Tinker (S341): Shopify community announcement for a free AI creative suite with 100+ tools, plain-language generation and character generator for consistent model characters.
- Redeux (S342): Shopify app launch aimed at catalog-scale product photography: existing product photos -> consistent brand looks -> lifestyle scenes/model shots/background swaps -> reusable model teams -> bulk catalog application -> recommendations/stats.
- AI product photography thread (S343): Snapshot workflow is concrete: upload phone/supplier product photo, remove background, select theme or describe scene, return 4 photorealistic results and attach to product listing; bulk editing and Shopify integration are key.
- Picjam/model-photo thread (S344): AI model photos allegedly improved apparel listings across 110 products, but the metric is unspecified and questioned.
- Product photography cost thread (S345): small clothing stores consider AI model images/virtual try-on because flat lay, model shoot and lifestyle shoot costs accumulate quickly.
- Meta catalog image-order thread (S346): the image shown in ad feeds can differ from storefront intention because Meta takes the first Shopify gallery image unless feed override/reordering is used.

Extraction:

- Shopify's operational bottleneck is not only generation quality. It is integration: bulk edit, one-click listing attach, reusable model/team style, recommendations, stats and feed export.
- Channel-specific image order matters. An AI-generated model photo can be useful for Meta ads while a product-only image remains preferred for PDP or marketplace compliance.

## Bilibili Direct Video Expansion: ComfyUI, RunningHub, Feishu, GPT Image 2

Sources: S347-S359.

### ComfyUI/RunningHub detail-page factories

- `BV1weoXBFEp1` (S347) is a ComfyUI-focused video claiming one-click ecommerce detail-page/main-image output in about 100 seconds. It is not yet a node-export proof, but it is a strong signal that Chinese creators are packaging detail-page generation as reusable workflow products.
- `BV16QiQBKEyX` (S348) is more concrete: RunningHub link, Nano Banana + Gemini 3.0 + ComfyUI, local 8-screen detail page, 100-second claim and layered PSD output. The PSD point matters because it gives a practical human correction layer before upload.
- `BV13SdhB1E7M` (S351) is an 8-part ecommerce design course: text-to-image, image-to-image, image washing workflow, product retouching, model try-on, product/model lighting workflow and transparent-background assets.

Extraction:

- The Chinese workflow direction is moving from “single hero image” to “long detail page factory”: multi-screen detail modules, transparent assets, relighting, retouching and layered export.
- RunningHub/ComfyUI should be evaluated as workflow packaging and operator UX, not only as model choice.
- Claims like “100 seconds” are useful lead indicators but require local SKU benchmark and node graph capture.

### Feishu table as prompt/control plane

- `BV17DcSzxEHJ` (S349) uses Feishu multidimensional table as a control plane: massive prompt library, demand input, AI drawing nodes, batch remix output, review flow and local deployment.
- This matches the earlier Feishu + Banana/Sora2 signal (S285), but gives a more explicit operational frame: table rows are demand objects and prompt/status/review records.

Extraction:

- For high-SKU ecommerce, a spreadsheet/table layer may matter as much as the image model.
- Useful columns for a practical implementation: SKU, marketplace slot, product reference URL, prompt template id, source prompt, output folder, reviewer, product-fidelity pass/fail, claim-compliance pass/fail and publish status.

### GPT Image 2 Chinese ecommerce adoption

- `BV13ho4BKEMD` (S352) reports real ecommerce scene tests: lamp product suite, Amazon hanging-lamp main image + A+ detail page, and Samsung earbuds detail page in Apple-like style. The description emphasizes set-level consistency, text clarity and product/logo fidelity.
- `BV1RvRuBQEFm` (S353) frames GPT Image 2 as one-click cross-border ecommerce main image + detail page generation, with a workflow document distributed through comments/private messages.
- `BV1Cz5r6ZEj5` (S354) explicitly connects GPT Codex, batch image generation and ecommerce detail-page efficiency, recommending manual migration to Image 2.
- `BV1h6oYBWEjo` (S355) shows a Photoshop-plugin path: GPT Image 2 in PS for ecommerce poster layout from one sentence, with self-supplied API.
- `BV1sARxBUEFz` (S356) is an Amazon main-image prompt/formula distribution case.
- `BV1cWLq6jEBq` (S357) claims free unlimited concurrent GPT Image 2 generation; this is useful as a wrapper/distribution signal, but a security/license risk rather than a production recommendation.

Extraction:

- GPT Image 2 adoption is being framed by creators as a suite generator: main image, lifestyle scene, close-up, A+ layout, poster and brand-style transfer.
- The safer production interpretation is “draft and layout accelerator” until product truth, policy compliance and wrapper provenance are verified.

### Midjourney 2026 signal

- `BV1VyQBBtERd` (S358) covers Midjourney V8 Alpha experience after the rating party and talks about workflow changes.
- `BV1AjLU6DEoo` (S359) is a very recent product-image/image-prompt tutorial.

Extraction:

- Midjourney remains relevant for product concept/taste and image-prompt workflows, but not as the first choice for exact SKU-preserving Amazon main images.

## 2026 Blog, HN and Reddit Expansion

Sources: S360-S370.

### GPT Image 2 ecommerce workflow blogs

- Nexscope (S360) gives a structured GPT Image 2 ecommerce prompt frame: product + scene + action + atmosphere. It also frames ad testing as 15-20 directions followed by CTR validation and localized variants by market.
- UGCFast (S361) describes API batch generation for hundreds of products, Shopify/WooCommerce integration and downstream UGC video creation from approved GPT Image 2 stills.
- Rewarx (S365) positions GPT Image 2 as useful for large-catalog consistency and seasonal/platform variations, while recommending integration with specialized ecommerce photography tools for standardization.

Extraction:

- GPT Image 2 should be captured as a structured brief engine: one prompt per slot, not one generic prompt per product.
- The high-volume pattern is: product reference -> slot brief -> API/template batch -> review -> platform upload -> optional UGC/video expansion.

### Multi-model router and benchmark signals

- Ropewalk (S362) is a useful model-router article because it names task buckets: Recraft V4 for clean catalog, Seedream 4 for lifestyle, FLUX 2 Pro for luxury/editorial, Nano Banana Pro for edits, GPT Image 2 for text-on-pack.
- PhotoWorkout (S370) ran a hands-on API comparison on April 22, 2026. Their split is operationally useful: Gemini/Nano Banana 2 faster and stronger for preserving existing-photo detail; GPT Image 2 better for structured layouts, infographics and text-heavy graphics.
- HN Nano Banana 2 discussion (S366) adds engineering constraints: 0.5K/1K/2K/4K pricing tiers, configurable thinking, slow generation under load, prompt-adherence failures on tricky grid prompts and input-image overfit.
- HN ChatGPT Images 2.0 discussion (S367) reminds us to distinguish ChatGPT app behavior from `gpt-image-2` API model behavior.

Extraction:

- The correct production architecture is a model router with task-specific benchmarks, not a single-model bet.
- For ecommerce, the router should consider product preservation, text/label accuracy, layout structure, background control, speed, cost and platform policy separately.

### Reddit automation and video-pipeline methods

- Reddit n8n thread (S363) gives a concrete fashion automation: form with product name, product image and model description; Nano Banana Pro t2i generates model shots; i2i puts clothes onto the model; outputs nine poses into local folders grouped by product name.
- Reddit GPT Image 2 vs Nano Banana 2 routing post (S368) is useful as community evidence that identical prompts can produce different “tone”, so routing cannot rely on aesthetic screenshots alone.
- Reddit generativeAI video thread (S369) describes a first-frame pipeline: prompt enhancer splits user intent into static first-frame and motion/context descriptions; GPT Image 2 or Nano Banana 2 makes the first frame; Grok Imagine animates it.

Extraction:

- For clothing/fashion, the method stack is converging on batch forms, local product folders, t2i base model shots and i2i garment placement.
- For video ads, still-image generation becomes a first-frame control step. The image QA gate must happen before animation, otherwise product errors propagate through the video.

### Midjourney prompt framework

- Promptolis (S364) is a prompt-builder case for Midjourney product photography. Inputs: product description and intended use such as Etsy listing, Amazon, website hero or social. Outputs: prompts with studio setup language, material specificity, lighting direction and background control.

Extraction:

- Midjourney remains a taste/concept tool for product photography and campaign visuals.
- The useful framework is not “Midjourney as SKU truth”; it is “LLM-generated Midjourney prompts for art direction, then product QA or compositing.”

## Open-Source, Prompt Gallery and Wrapper Website Expansion

Sources: S371-S383.

### GitHub ecosystem: prompt-as-code and Skills

- GitHub `gpt-image-2` topic (S371) shows the ecosystem moving quickly toward prompt libraries, Codex/Claude Skills, local desktop tools, OpenCode plugins, gateways/CLIs and prompt-as-code template engines.
- The most relevant pattern is not a single repo. It is the packaging format: prompt templates as code, agent-callable skills, local-first image tools and model-access wrappers.
- Cliprise prompt repos (S383) and the GitHub ad-creative topic (S373) show product photography and ad creative becoming named prompt categories rather than ad hoc examples.

Extraction:

- A production ecommerce image factory should not store prompts as loose documents. It should store them as versioned templates with variables, test SKUs, output examples and QA notes.
- Treat GitHub prompt libraries as seed material, then normalize them into the local ProductTruthPack/SlotBrief/ModelRouter structure.

### Vertical category: jewelry

- `awesome-jewelry-ai` (S372) is valuable because jewelry exposes the hard edge of product fidelity: reflections, gems, metal type, setting geometry, scale and worn/unworn placement.
- It links ComfyUI product placement workflows, RunningHub jewelry workflows, jewelry LoRAs and specialized tools such as FormaNova, Tashvi, NeuroViz and Claid AI.

Extraction:

- Category-specific tooling matters. A generic product-photo workflow that works for mugs can fail badly for rings, gemstones or watch faces.
- Jewelry/luxury categories need a stricter QA rubric and often specialized model/tool routes.

### GPT Image 2 wrappers and prompt galleries

- IMGVID (S374) provides product-image/storyboard prompt templates. Its ecommerce hero prompt explicitly includes “no fake brand logo” and “no invented claims”, which is exactly the right compliance habit for listing/ad creative.
- Bananai (S375), Got Image 2 (S377), GPT Img 2 App (S379), gptsImage (S378) and GPT Image 2 Tech (S376) all package GPT Image 2 as an ecommerce/product/marketing wrapper, often with claims around 4K, commercial use, prompt galleries, reference editing, transparent backgrounds, product angles or multi-model comparison.
- Nemovideo (S380) adds text-in-image prompt discipline: short copy, explicit font color/style and limited line count.
- IMA Studio (S381) is useful for the campaign side: same product in different environments, Shopify color variants, localized ads and UGC-style product-in-hand statics.
- YouMind (S382) links creator/X prompt examples and “Shortcuts” style one-click generation from user materials.

Extraction:

- Wrapper sites are useful for discovering prompt patterns and user-facing UX, not for proving model capability.
- A practical intake process should log wrapper URL, claimed model, prompt pattern, output target, license claim, pricing claim and whether it supports reference images, video handoff or model comparison.
- The recurring ecommerce prompt grammar is: real product/ref -> target slot -> scene/context -> lighting/material -> exact short copy if needed -> forbidden changes/claims -> export format.

## Platform And Conversion Evidence Expansion

Sources: S384-S396.

### Amazon official/native ad generation

- Amazon Ads guide (S384) confirms Image generator is a free generative AI tool inside ad console/DSP contexts, creating lifestyle and brand-themed images from product details, refined by short prompts or seasonal/lifestyle themes.
- Amazon says outputs can be integrated into Amazon DSP, Sponsored Brands, display ads and Brand Stores, and that creative variants can be stored in the creative assets library and measured by CTR, ACOS and ROAS.
- Amazon news article (S385) says Image Generator uses the actual product image plus product descriptions/customer reviews to create ad-ready images, and reports aggregate lift claims for campaign submissions and GMS.

Extraction:

- Amazon’s native AI image generation is clearly strongest for ad creatives and Brand Stores, not automatically for PDP main image replacement.
- Any Amazon workflow should keep ad creative, A+ content, secondary gallery and main image as separate surfaces with different QA gates.

### Amazon seller/community full-listing builders

- Reddstudio build log (S387) is a concrete full-listing pipeline: one product photo -> vision analysis -> design framework -> visual scripts for five image types -> coordinated generation -> custom A+ desktop/mobile canvas compositor.
- AmazonFBA builder thread (S395) adds richer workflow details: AI design director writes a full color/typography/layout script before generation; output includes 5 listing images, 5-6 A+ modules, desktop/mobile versions and hero banners; prior module edge/context is used to make A+ modules flow seamlessly.
- AmazonFBA A+ test thread (S396) shows a no-prompt agent direction: one product image plus product info/bullets -> full A+ and five product images in minutes. Wording remains a known failure.
- FulfillmentByAmazon discussion (S388) adds buyer-objection workflow: crawl reviews, PSP/Rufus questions and brand guidelines to guide visual content, instead of making generic attractive scenes.

Extraction:

- The emerging Amazon system is not just “generate five images”. It is a coordinated visual-system generator with product analysis, design script, A+ layout, desktop/mobile variants and seller-editable outputs.
- The next useful implementation boundary is input quality and editability: ASIN import, product facts, claim source, alt text, module export and Seller Central handoff.

### Conversion skepticism and anti-hype signal

- AmazonFBA conversion thread (S389) is important because it pushes against AI aesthetics: polished AI images can lose raw product clarity and buyer trust.
- Sellers in the thread emphasize that main image should answer what the product is in under a second, lifestyle shots must feel real, and testing should change one image at a time with PPC splits.

Extraction:

- “Better looking” is not a valid success metric. For ecommerce, the QA target includes buyer clarity, trust, product texture visibility and controlled conversion tests.

### WB/Ozon/Yandex tool stack

- Oimok (S390) turns one phone photo into WB/Ozon-style AI try-on, infographics and video cards, claiming output packs in 3-5 minutes.
- Twin AI (S391) offers Wildberries product photos, lifestyle shots and infographics from one phone shot.
- Seller ART (S392) uses product photos as references, product characteristics/badges/text as inputs and creates unified-style cards for Ozon, Wildberries and Yandex Market.
- ProductPhotoAI (S393) is a Telegram-bot pattern: product card generation, clothing-on-model, background removal, retouch, lighting correction and defect removal in about 30 seconds.

Extraction:

- Russian marketplace tools are converging on “phone photo -> full marketplace card pack”: try-on, infographic, lifestyle, video card and edit/retouch modes.
- Their marketing claims should be separated from reusable workflow structure. The reusable structure is strong; CTR claims require testing.

### Academic modular ad pipeline

- CreativeAds (S394) is useful because it decomposes ad generation into product pairing, layout generation and background generation, with UI oversight and per-image adjustment.

Extraction:

- For scalable product ads, modular generation is safer than one giant prompt. Product pairing, layout and background each need their own controls and checks.

## ComfyUI, Brand Profile And Conversion-Shot Expansion

Sources: S397-S407.

### ComfyUI as local/versioned backend

- NVIDIA (S397) provides a stronger technical foundation for ComfyUI than most creator videos: prebuilt local node graphs for layer decomposition, object removal/inpainting and photo-to-3D, with clear hardware/model requirements.
- Rewarx ComfyUI product-photo guide (S398) gives the ecommerce pattern: batch/folder loading, preprocessing, quality checks and version-controlled JSON workflows for hundreds/thousands of product images.
- Rewarx lighting guide (S399) breaks relighting into modular steps: base image, lighting analysis, shadow simulation, ambient occlusion and compositing.
- ComfySearch (S405) is relevant for future automation: agentic search over ComfyUI component space with validation-guided workflow construction.

Extraction:

- ComfyUI’s value is control and repeatability, not ease. It should be treated as a backend for teams that can version node graphs and run product benchmarks.
- For ecommerce, the strongest ComfyUI modules are cutout/layering, lighting/shadow, product placement, background replacement and batch preprocessing.

### Brand profile and shot types

- NovaBrand (S400) makes the brand-profile concept explicit: one clean product photo, persistent brand context and shot type selection such as PDP hero, lifestyle, UGC-style or ad creative.
- This matches the broader evidence that prompt-only generation drifts; persistent brand/category context is the control layer sellers need when they scale beyond a few shots.

Extraction:

- A practical image factory should not ask the operator to rewrite brand identity every prompt. Store brand profile and slot type as first-class structured inputs.

### Community workflow comparisons and UGC packaging

- ComfyUI subreddit comparison (S401) pits Photoroom, OpenAI GPT-4o image generation and an AI workflow against each other for ecommerce product photos; the discussion centers on realism, remaining manual edits and cost.
- Dropshipping ComfyUI workflow thread (S402) packages three workflows: UGC talking-head video, product placement with model traits and macro close-ups for beauty/skincare.
- AIToolsAndTips thread (S403) repeats the operational reality: most sellers use base product photo + AI background/lighting polish, not pure generation. One company claims 3000-5000 SKUs/month with AI-generated image sets.

Extraction:

- There are two separate product lines emerging: seller-friendly wrappers for quick product-photo polish, and technical ComfyUI workflow packs for UGC/product placement/video.
- Both need a product-fidelity gate, but ComfyUI adds workflow/version control while wrappers add usability.

### Conversion-shot taxonomy

- Ecommerce marketing thread (S404) gives a concise slot taxonomy: main image for clarity/compliance, detail image to remove doubt, lifestyle image to show use, comparison/benefit image to explain the choice.
- The same thread stresses that research before generation and A/B testing volume matter more than one cinematic result.

Extraction:

- This taxonomy should become the default planning layer before image generation. Every image slot needs a job, buyer question and metric hypothesis.

### GitHub ecommerce GPT Image 2 README pattern

- Maynor996 repository (S408) is a lightweight but directly relevant prompt-workflow README: use GPT Image 2 as an ecommerce image generator, preferably starting from an existing product image; state which product attributes must remain accurate; adjust background, lighting and scene mood; generate variants; judge by product recognizability, conversion support, ecommerce cleanliness and cleanup needs.

Extraction:

- Even tiny repos are converging on the same control language: fixed product shape/material/color, image-to-image for controlled production and business criteria over visual excitement.

## Heartbeat Expansion: n8n Shopify, Catalog Onboarding And Regional Marketplaces

Sources: S409-S416.

### Shopify and n8n product-photo automations

- CreateWith / n8n deAPI case (S409) adds a direct Shopify trigger pattern: new product appears -> product details extracted -> prompt boosted -> AI image generated -> background removed -> asset uploaded back to Shopify.
- GrowwStacks (S411) adds a Drive-folder trigger pattern: upload smartphone product photo -> Foul.ai creates 1-4 studio variations and a short panning video -> original and generated assets are stored together.
- n8n-template product photography workflow (S413) adds a spreadsheet control pattern: Sheet image URLs -> product analysis -> human-model photography prompts -> generation -> Drive output links back into Sheet.

Extraction:

- Shopify image automation is converging on event triggers, product-detail extraction, generation, cleanup, asset storage and catalog writeback.
- The most practical control point is not the model prompt alone; it is the trigger/storage/status system around the prompt.

### Image-to-listing catalog onboarding

- n8n image-to-CSV template (S410) turns raw images into a Shopify-ready CSV using AI image analysis, category detection, generated product copy and Google Sheets orchestration.
- n8n UploadToURL workflow (S416) goes further into store creation: mobile upload or remote URL -> hosted asset -> GPT-4o Vision copy/category/SEO -> Shopify/WooCommerce draft/product.

Extraction:

- Some “AI ecommerce image” workflows are actually image-to-product-data onboarding systems. Keep them separate from image-generation systems.
- These pipelines are valuable because they connect visual input to catalog metadata, but they need attribute/category/fact review before publish.

### One-photo video ad studio

- Reddit n8n AI Ad Studio (S415) is a useful video workflow: product photo + aspect ratio + vibe -> Gemini 2.5 Pro YAML product analysis -> AI creative director JSON prompt -> Veo 3.1 via Kie.ai -> Drive/Baserow logging.

Extraction:

- The reusable framework is `product visual DNA -> creative direction -> video prompt -> generation -> logged output`.
- Video pipelines must inherit the product-truth gate from still-image pipelines, then add key-frame review.

### Regional marketplace generators

- Aidentica (S414) expands the WB/Ozon tool cluster into Kazakhstan marketplaces: Kaspi and Halyk Market. It handles phone-photo input, background removal, studio/model/flatlay/interior/street styles, infographics and video cards.

Extraction:

- The Russian/Kazakhstan stack is clearly marketplace-card-first: image, infographic, video, format and style packed together.
- These tools are good workflow cases, but actual seller use still needs moderation/fidelity verification.

## Heartbeat Expansion: Shopify App Store And Amazon Seller Tool Threads

Sources: S417-S423.

### Shopify bulk product-media apps

- CatalogShot (S417) is a clean Shopify App Store example: existing product photos -> AI lifestyle images -> reusable approved scenes -> bulk catalog variants -> apply approved images back to Shopify product media. It is explicitly focused on non-apparel catalogs.
- DONDO (S422) expands the Shopify pattern beyond images: product photos, lifestyle/studio/social/ad visuals, SEO optimization, compliance, brand voice, pricing intelligence, monitoring and one-click publishing.
- Fitz (S423) is the apparel/try-on side: ChatGPT/Gemini image generation, AI models, bulk product imagery, virtual try-on widget and BYO Gemini API key.

Extraction:

- Shopify’s ecosystem is shifting from “generate a nice product photo” to “bulk media operations embedded in catalog workflows.”
- Reusable criteria: product-media writeback, approved-scene reuse, brand consistency, bulk controls, model/try-on fidelity and whether outputs remain editable.

### Nano Banana Pro instruction-based ecommerce editing

- Banana Pro (S418) frames Nano Banana/Nano Banana Pro as an instruction-following product editor for Amazon, Shopify, Etsy and TikTok Shop. The page claims product packaging, proportions and labels should be preserved while backgrounds, lighting, shadows and A+ style outputs change.

Extraction:

- The useful method pattern is natural-language edit control over a real product image, not pure text-to-image.
- Wrapper claims should be treated as hypotheses until the exact model version, commercial terms and SKU fidelity are tested.

### Amazon seller tools and community feedback

- GenerateProductPhotos subreddit intro (S419) frames an Amazon FBA/Shopify/Etsy community around single-upload generation of white hero, lifestyle and infographic/A+ visuals.
- EasyAI Picture thread (S420) targets a narrower Amazon problem: turn rough phone product photos into clean Amazon main images.
- Seller Studio thread (S421) is useful because commenters ask for brand persona and competitor-informed visuals, while the builder pushes back toward actual product and seller-provided context.

Extraction:

- Amazon main-image tools should stay conservative: phone photo cleanup, white background and product truth first.
- Competitor/brand signals are useful for A+/secondary images, but should not overwrite product identity or invent brand facts.

## Heartbeat Expansion: Amazon Listing Suites, GPT Image 2 Shopify Apps And Seller Central AI Context

Sources: S424-S433.

### Amazon one-photo listing suites

- Snaply (S424) uses one phone product photo plus product description to generate four Amazon image styles and listing copy/search terms in one flow.
- zonfy (S428), Snapsible (S429) and Amazon Listing Generator (S430) all package the same direction: product photo -> main image, lifestyle/infographic/A+ images and listing copy/keywords.
- Snapsible is notable because it explicitly warns that badges, price or feature text on the main image can trigger listing suppression.
- Amazon Listing Generator adds scale features: ASIN import, up to 14 reference images, 9 image variants, bulk upload of 10 products and inline editing.

Extraction:

- Amazon seller tools are converging on a “single product photo to full listing pack” workflow.
- The core QA boundary remains slot taxonomy: main image must stay clean and factual; secondary/A+/Brand Store images can use lifestyle, text and infographics with claim checks.

### GPT Image 2 / Nano Banana Pro Shopify apps

- Photoniex (S425) is a Shopify App Store case that explicitly names `gpt-image-2` and Nano Banana Pro. It supports background replacement, scene generation, virtual try-on, outpainting and media-library saveback.
- Image2 ecommerce page (S427) positions GPT Image 2 for white-background cleanup, lifestyle placement, multi-angle consistency and readable packaging/overlay text.

Extraction:

- GPT Image 2 is being packaged into Shopify workflows as an editor/media operation, not only a standalone generator.
- Shopify saveback and media-library integration are increasingly important as production signals.

### Seller Central planning and Amazon store modules

- GeekWire (S431) covers Amazon’s AI-generated Seller Central dynamic canvas. It is not image generation, but it provides AI-driven performance/scenario planning that can inform which image/video assets sellers should create.
- AmazonFBA AI photos vs real photoshoot thread (S432) repeats the important compliance rule: Amazon cares about accurate representation of material, dimensions and color, so tools anchored on actual product photos are safer.
- Shoppable Collections thread (S433) adds a Brand Store module angle: raw white-background shots can feed AI agents that generate lifestyle scenes and 15-second b-roll video for store experiences.

Extraction:

- Amazon AI image generation should be linked to seller planning signals but still separated from compliance approval.
- Brand Store / Shoppable Collections need image plus video modules, so still-image pipelines should preserve product truth before video expansion.

## Heartbeat Expansion: Google, TikTok, Adobe Platform-Native Creative Systems

Sources: S434-S441.

### Google Product Studio and Merchant Center risk

- Google Product Studio (S434) is the most direct native Google product-media tool: change background, remove background, increase resolution, create/edit images and generate product videos from product images.
- It is available in Merchant Center and through the Google & YouTube app for Shopify, and generated images can be added to Merchant Center or even marked as the main image.
- Google’s own docs state experimental limits, reviewer process, product/category limitations and regulated-goods exclusions.
- Shopify community thread (S435) adds a publishing-risk signal: AI-generated image metadata on the `image_link` URL may trigger Merchant Center disapproval.

Extraction:

- Google Product Studio should be treated as platform-native generation plus feed publishing, not just an image editor.
- The QA gate extends beyond visual product truth into feed metadata, image URLs, Merchant Center diagnostics and main-image selection.

### TikTok Symphony

- TikTok Symphony official blog (S436) covers product URL/account-asset to video generation, AI-enhanced display cards from selling points/images and AI-enhanced carousel product images via crop/extend/background fill.
- TikTok Shop community thread (S437) asks whether AI-generated but accurate product photos can hurt listing traffic; evidence is unresolved, especially because TikTok is actively promoting Symphony.

Extraction:

- TikTok’s native route is video/card generation from product assets, not marketplace-style static image compliance.
- For TikTok Shop, track both product accuracy and traffic/listing behavior. AI generation itself is not enough to infer suppression.

### Adobe Firefly Services

- Adobe Firefly API docs (S438) are important because Composite Operations are explicitly product-photo friendly: upload product photo/object, generate scene, improve masking, edge accuracy, harmonization, lighting/shadow and upscaling.
- Firefly Services docs (S439) add enterprise batch infrastructure: Creative Production API can run published workflows over many assets with progress tracking and per-asset results.

Extraction:

- Adobe is a strong enterprise backend for product compositing and batch creative production.
- It is not marketplace-native. The production system still needs ProductTruthPack, policy QA and export/publishing adapters.

### Product-data-bound design workflows

- Reddit ecommerces thread (S440) highlights the limitation of Canva/Figma/AI image tools for catalog scale and points toward binding product data such as title/price directly into layers, then pushing outputs to Shopify product media/metafields.
- FacebookAds thread (S441) repeats the small-brand cost bottleneck and single-product-image-to-floating/white-background/layout graphic direction.

Extraction:

- Another emerging layer is product-data-to-design: bind SKU data into layouts, then generate multi-format graphics and publish into product media/metafields.
- This complements model generation, especially for infographics, sale cards and channel-specific formats.

## Heartbeat Expansion: Meta, Pinterest, Etsy, eBay And Reseller Cleanup

Sources: S442-S451.

### Social-ad platform background generation

- Meta Advantage+ Creative (S442) is a native ad-platform case for generated product backgrounds and full-image variations. Direct access was login-blocked, so the source is recorded as official snippet plus Meta transparency evidence.
- Meta transparency docs (S443) are important because AI-generated or significantly edited ad images/videos may receive labels next to Sponsored or in the three-dot menu, depending on edit significance and whether photorealistic humans are involved.
- Pinterest (S444) is explicit: Pinterest Canvas can generate backgrounds on product images for ads; Pinterest also uses metadata-driven AI modification/generation disclosure in ad explanations.
- Meta community threads (S449-S450) add operator risk: automatic backgrounds can appear in catalog ads, and high-performing AI ad setups usually preserve the real product cutout while generating many background/lighting variations.

Extraction:

- Social ad AI workflows need a platform-preview gate: product truth, disclosure/label behavior, automatic enhancement toggles and placement previews.
- For ad conversion testing, the reusable method is real product cutout + AI scene variants, not pure synthetic products.

### Etsy and eBay policy boundaries

- Etsy Creativity Standards (S445) separate seller-prompted AI creations from physical/final product representation. AI-created designs may be allowed if disclosed, but made/handpicked items must use original photo/video content of the final product.
- eBay picture policy (S446) does not name AI, but it governs AI edits through accuracy: no images that misrepresent the item, no stock photos for used/damaged/defective items, no added text/artwork/borders/watermarks.
- eBay AI background tool coverage (S447) and Nightjar/eBay compliance notes (S444/S446 context) show that AI backgrounds can fit the platform if the item remains accurate.
- eBay used-item warning (S451) is the failure case: AI-generated-only pictures for retro/used items undermine buyer trust and accuracy.

Extraction:

- Etsy/eBay are not primarily “AI model” problems; they are representation and disclosure systems.
- Used/vintage/handmade goods require stricter original-photo discipline than new retail goods.

### Bulk cleanup for resellers

- PartPix (S448) adds a non-fashion reseller/tool category: auto parts and dismantlers who need bulk cleanup, enhancement, watermarking, resizing and marketplace presets across eBay/Amazon/Shopify/Etsy/Allegro/Ovoko.

Extraction:

- For resellers, bulk cleanup and preset export may matter more than lifestyle generation.
- The QA concern is preserving condition defects, scratches, exact color/material and item-specific details.

## Heartbeat Expansion: Walmart, AliExpressLocal, Shopee And Cross-Border Supplier Photos

Sources: S452-S459.

### Walmart

- Walmart Success Hub (S452) confirms GenAI content suggestions in Seller Center for product names, descriptions and key features, with accuracy, truthfulness, rights and policy compliance review.
- Nightjar Walmart AI image policy guide (S453) is useful because Walmart does not appear to publish a separate AI-image rule: the operative boundary is whether the image is an actual, accurate product image.
- PixelPanda Walmart page (S454) adds the tool workflow: optimize or generate product photos around Walmart-specific white-background/product-focus requirements, with batch/API positioning.

Extraction:

- Walmart should be modeled like Amazon/eBay in terms of main-image discipline: real product source, white-background cleanup, no misrepresentation.
- Walmart GenAI evidence is stronger for listing copy than image generation; AI image workflows should be kept in the compliance/optimization layer.

### AliExpressLocal and supplier-photo cleanup

- AliExpressLocal press release (S455) says local US sellers gained an AI-enabled image tool for product listing images.
- AmazonSeller thread (S459) captures the cross-border reality: supplier images from AliExpress are often poor, and sellers want one-click AI cleanup that looks natural while matching Amazon standards.

Extraction:

- There is a distinct workflow for cross-border sellers: supplier photo -> marketplace-compliant cleanup -> optional secondary/lifestyle expansion.
- This differs from a brand campaign workflow; the first goal is credible baseline listing imagery.

### Shopee

- Shopee AI article (S456) reports platform AI tools for brands: virtual fitting room, AI scripts, comment assistant, stream manager and product-detail highlighting.
- Shopee Feed seller deck (S457) gives visual baseline rules: good lighting, clear angle, clean background, actual item in photo, held/model shots and variation swatches.

Extraction:

- Shopee coverage currently supports an actual-item photo baseline plus AI assistance around scripts, livestream and fitting-room experiences.
- For SEA marketplaces, do not assume AI listing images are accepted just because platform AI exists; keep actual product photo as the base.

### Small-seller governance

- SmallBusinessSellers thread (S458) adds a fairness/governance angle: sellers compare their real product photos against competitors’ AI-generated product listings and question regulation.

Extraction:

- Monitoring misleading competitor AI listings is now part of marketplace image governance, alongside internal product QA.

## Heartbeat Expansion: Furniture Visual Commerce, AR And Virtual Try-On

Sources: S460-S469.

### Furniture and home decor

- Furnea (S460), OmniRoom (S461) and Stuv AI (S463) all focus on one raw furniture/product photo becoming catalog shots, room scenes, videos, material/color variants and marketplace/ad modules.
- OmniRoom is especially explicit about furniture-commerce specificity: lifestyle room scenes, multi-angle perspectives, white-background catalog shots, A+ modules and product descriptions, while claiming preservation of color, texture, proportion and material.
- Furniture community discussion (S464) adds the operating method: reuse strict scene templates, crop/camera presets and material locks so A/B tests isolate the product variable rather than changing everything at once.

Extraction:

- Furniture AI photography needs a stricter material/scale rubric than generic product photography.
- The useful workflow is not random rooms; it is reusable room/camera templates tied to metadata and channel formats.

### Image-to-3D and AR

- Spatiq (S462) converts product photos into textured 3D models and browser/QR AR catalogs with scan analytics.
- Furniture/decor AR founder thread (S465) says business owners cared about real scale and multiple size variants, not just photorealistic perfection.

Extraction:

- For furniture/decor, image generation and AR are adjacent workflows: scene images sell mood, while AR/3D answers fit and scale.
- Dimension accuracy becomes a first-class QA gate.

### Virtual try-on

- Provalo (S466) and A&A Virtual Try-On (S467) cover customer-facing try-on from flat product/customer photos.
- StyleLab thread (S468) is useful operational evidence: bad input images and model failures make pay-on-success or failure-aware billing relevant.
- Tstars-Tryon 1.0 paper (S469) gives an evaluation target: preserve garment texture, material properties, structure, person identity and background across up to six reference images and eight fashion categories.

Extraction:

- Virtual try-on should be treated as a product-fidelity-critical workflow, not just a nice model image generator.
- The production benchmark should separate garment texture, drape, cut, logo, model/customer identity, privacy/latency and failed-output cost.

## Heartbeat Expansion: Vertical Product Studios, Packaging Mockups And Hard-Category Benchmarks

Sources: S470-S476.

### Vertical ecommerce studios

- Tasweera (S470) adds a store-publish pipeline: bulk product upload, background removal, lifestyle scenes, virtual model photography, video creation, marketplace optimization and Shopify/WooCommerce publishing.
- Luminify (S471), StudioMode (S472) and Pixora (S473) show the more vertical direction: apparel, cosmetics, jewelry, food, electronics, home and collectibles each need different presets, material handling and output formats.
- StudioMode is especially explicit about 4-50 variants per upload, front/3/4/macro/lifestyle/ad layouts, packaging/logo/brand-color preservation and 4K/8K exports.

Extraction:

- Category vertical should be a first-class input before the prompt is compiled.
- A practical batch system needs channel output and vertical QA together: Amazon/Shopify/TikTok/Meta requirements plus product material/label checks.

### Multi-model routing

- GenMix (S474) is useful because it names a current multi-model route: GPT Image 2 for label/logo fidelity and white background, Nano Banana Pro for textiles/lifestyle, Seedream for hero images and Qwen Image Edit for faster bulk edits.

Extraction:

- This matches the pattern already emerging from the broader ledger: model choice should be routed by job, not by brand preference.
- For Amazon/Ozon/WB, the router should put label/logo/OCR-critical images through stricter review than general lifestyle variants.

### Packaging, mockups and cleanup

- ProductShot (S475) separates Scene Wizard, Cleanup and Mockups, including Amazon-style white-background cleanup and wrapping designs onto apparel/packaging/products with realistic warping and lighting.
- StudioMode and GenMix add packaging/logo preservation and label fidelity evidence from adjacent tool claims.

Extraction:

- Packaging workflows need geometry, print distortion, label/OCR and material reflection gates.
- Mockups are useful for ads and secondary images, but they should not be treated as manufactured-product proof for strict main-image slots.

### Product-specific benchmarks

- AIToolTesting (S476) argues that generic image-generation benchmarks do not reveal ecommerce product-photo failure modes.
- The cited benchmark approach uses reflective skincare bottles and furniture material differentiation such as wood grain, matte metal and plausible shadows.

Extraction:

- Before selecting a tool/model for batch production, build category-specific benchmark SKUs: reflective cosmetics, jewelry, garment texture/drape, furniture wood/metal, transparent/glossy packaging and text-heavy labels.
- Rerun the benchmark when Nano Banana/Image 2/Midjourney or wrapper model versions change.

## Goal Continuation: Community Workflows, Chinese GPT Image 2 Pipelines And Multi-Model Routers

Sources: S477-S490.

### Prompt frameworks and no-prompt presets

- Reddit Visual Syntax workflow (S477) is useful because it reframes AI ecommerce product photography as photography direction: define style, subject, action and scene instead of asking for vague "beautiful lifestyle" output.
- Preset-tool discussion (S485) captures a seller pain point: long prompts do not scale for everyday listing/client work, so upload-product-plus-scene-picker tools become practical.
- Lumiet (S489) adds a Shopify-specific version: visual anchor/reference-chain, hero/lifestyle/collection banner slots and A/B testing.
- ZeroLu prompt library (S481) provides reusable Nano Banana Pro product-isolation and virtual try-on prompts.

Extraction:

- A production UI should offer both structured prompt fields and preset workflows.
- Product reference/visual anchor should be retained across slot generation, not rediscovered by every prompt.

### Chinese GPT Image 2 ecommerce workflows

- Bilibili 618 opus (S478) gives fresh GPT Image 2 prompt templates for Chinese ecommerce: main image, poster, detail-page image, livestream cover and category-specific promotional graphics.
- Bilibili GPT-image2 + ComfyUI video tutorial (S479) links product-image generation to ecommerce video, RunningHub and digital-human components.
- Bilibili ChatGPT Image 2 + Coze tutorial (S480) claims one-click Taobao/Amazon main-image plus detail-page suite generation.

Extraction:

- Chinese seller workflows are moving from isolated prompt examples into workflow builders: Coze for image-suite automation and ComfyUI/RunningHub for product-to-video.
- The QA gate must include Chinese text, platform slot, product truth and synthetic-video disclosure.

### Human-in-use and trust QA

- DropshippingTips feedback (S486) flags practical failures: cartoonish people, product size wrong in hand, in-use action physically wrong and buyer trust risk.
- Neck-massager discussion (S487) shows why health/wellness in-use images are hard: the seller has a product sample but no model shoot, and prompting Nano Banana for realistic use is difficult.
- Fresh dropshipping discussion (S488) says the bottleneck is becoming taste, direction and brand consistency, not execution.

Extraction:

- Human/in-use product images need a separate QA checklist: scale, function direction, plausible grip/pose, product material and trust.
- AI-looking people may hurt ecommerce trust even when standalone product shots are acceptable.

### GitHub/Gist/X/HN signal

- Kie.ai MCP server (S482) shows a multi-model media API/MCP direction: Nano Banana Pro, video, audio and other models exposed to agents with intent routing.
- Gist tool comparison (S483) is a quick 2026 landscape index for AdCreative.ai, Freepik, CLAID.AI, WeShop AI, Dezgo and Phot.AI.
- X prompt (S484) provides a concise luxury perfume Nano Banana Pro prompt; useful as prompt-gallery signal, not a workflow.
- HN Show HN Sellshots (S490) adds an indie-tool launch signal for AI product photography aimed at ecommerce stores.

Extraction:

- For a batch ecommerce studio, multi-model API/MCP routing should carry product-truth metadata, not just prompt text.
- Tool-comparison and prompt-gallery sources are discovery inputs; they should feed benchmark candidates rather than final vendor claims.

## Goal Continuation: Amazon Compliance Boundaries, Feishu Batch Ops And UGC Automation

Sources: S491-S502.

### Amazon proof-image boundary

- Amazon Seller Forum spotlight advice (S491) explicitly separates Brand Registry proof from AI creativity: use real product images only, no AI/computer-generated images, with the brand/logo permanently fixed to the product.
- Brand Registry rejection thread (S492) repeats the same boundary: physical products with brand name permanently affixed, computer-generated images not accepted. Amazon reply asks for closer product images and product-in-hand photos.

Extraction:

- Amazon Brand Registry proof images should be treated as a stricter class than listing secondary/ad images.
- The generation system should label these slots as `real_photo_only` and block AI replacement.

### Dropshipping and supplier-photo testing

- Dropshipping conversion thread (S493) says AI product shots can work if they match the real product; local Stable Diffusion gives more control, while flat-rate tools help test many products quickly.
- Supplier-photo thread (S495) records a recurring issue: Midjourney changed actual product design, while product-aware lifestyle-scene tools are valued because they preserve lighting/material cues from raw supplier photos.
- Small-brand setup thread (S494) adds a style risk: AI product images can look similar across stores and feel off.

Extraction:

- Initial creative testing can use supplier photos, but the first QA is product match, not aesthetics.
- A catalog system should watch for generic prompt-library sameness across stores.

### Chinese batch/workflow ops

- Feishu Bitable workflow (S496) is a concrete batch-ops pattern: SKU table + Doubao prompt field + Nano Banana/Seedream model call + team form intake, producing 20 main images in about one minute.
- Coze ecommerce workflow page (S497), one-photo Amazon main image video (S498) and Nano Banana Pro + Coze detail-page workflow (S499) extend the same idea into Amazon main/detail pages and selling videos.

Extraction:

- For Chinese ecommerce teams, spreadsheet/workflow tools are becoming the orchestration layer before model selection.
- The useful object is a job row with product fields, prompt, output URLs, review status and channel slot.

### UGC/video automation and prompt workbenches

- Higgsfield/Claude Code gist (S500) and repo (S501) show a more technical route: browser automation plus skills for ecommerce ads, product 360, social hooks, Seedance video and session-resume handling.
- Image2Studio (S502) adds a lighter prompt-workbench route: choose an ecommerce scene, fill product variables and generate prompt-ready product shots/cards/heroes.

Extraction:

- Product-image generation is increasingly tied to image-to-video and UGC ad pipelines.
- Browser automation needs explicit key-frame QA and failure recovery; prompt workbenches need product-reference QA and rights/model verification.

## Goal Continuation: Russian WB/Ozon Card Factories And Shopify 2026 Bulk Apps

Sources: S503-S511.

### Russian marketplace card factories

- Racurs (S503) is a no-prompt WB/Ozon/Yandex card generator: upload product photo, it cuts background, picks scene, adds infographics and supports AI try-on/video.
- Wildberries AI description report (S504) is useful because it shifts AI from third-party card design into seller-cabinet content generation: product photo -> title, description, characteristics and search keywords.
- These complement earlier Prodiger/SellerART/Pixorion sources: Russian tools are converging on photo reference, card design, SEO text, marketplace sizing and sometimes video.

Extraction:

- Russian WB/Ozon workflows should be modeled as card factories, not only image generators.
- A job row should include product photo, marketplace, card size, SEO fields, generated text, generated visuals, moderation notes and review status.

### Amazon image-suite community signals

- ProductPhotography megathread (S505) adds another builder signal: one product photo -> five coordinated Amazon listing images plus A+ modules.
- GenerativeAI Amazon listing thread (S506) captures the core model-routing risk: generic tools such as Midjourney may hallucinate or change product shape.

Extraction:

- Amazon suites need product-lock QA across the whole set, not per-image beauty checks.
- Secondary/A+ images can use AI more aggressively than proof/main-image slots, but product geometry must still be locked.

### Shopify app-store 2026 bulk wave

- Rewarx (S507), StudioShot (S508), Comera (S509), Rokon (S510) and Modelize (S511) show the current Shopify direction: apps embedded in admin, bulk generation, catalog queues, on-model/fashion outputs, videos, avatars and auto-publish/sync.
- Comera is the strongest scale claim in this pass: review says 7000+ product backgrounds changed in 15 minutes and videos generated for products.
- Modelize explicitly names Gemini 3.1 / Nano Banana 2 and supports catalog-wide on-model/lifestyle/studio/flat-lay generation plus auto-publish.

Extraction:

- Shopify workflows are becoming catalog-media operations: app connects to products, processes products/collections, and writes generated media back.
- Auto-publish must be gated by SKU fidelity checks, especially for apparel fabric detail, try-on/model realism, background edits and generated videos.

## Goal Continuation: Productized SaaS, n8n Workflows And Open-Source Automation

Sources: S512-S531.

### One-upload SaaS product studios

- PhotoFox (S512-S513), SellShots (S514), CatalogShot (S516), GreenOnion (S518) and Selluna (S519) all converge on `one product photo or URL -> product page, ad, social and sometimes video assets`.
- CatalogShot is the clearest Shopify-specific pattern: analyze real product, suggest fitting scenes, generate options, save reusable scenes, approve winners and publish back to Shopify.
- Selluna is a useful URL-first pattern: paste product URL, pull images/details/data, generate Amazon main, A+ Content, ads, social and UGC-style images, then spot-edit.

Extraction:

- The useful abstraction is no longer single image generation; it is a platform image pack with product anchor, target slots, export format and review gate.
- Product URL intake can reduce seller friction but needs claim/text and competitor-style legal review.

### No-prompt and autopilot workflows

- BrightCut (S515), SnapSell (S517), GreenOnion (S518) and Selluna (S519) show a no-prompt UX trend: upload product, choose platform/output, let the tool pick shot types and templates.
- SnapSell's Autopilot is especially explicit: analyze product, choose shot type, remove background and produce listing-ready output.

Extraction:

- No-prompt tools are useful for non-technical sellers, but they hide the prompt/debug layer.
- QA must include material, label, logo, transparency/reflectivity and marketplace slot rules.

### n8n automation and UGC ad factories

- The Telegram product-photo workflow (S521) is actionable: Telegram intake -> rembg -> Sharp cleanup/resize -> OpenAI gpt-image-1 enhancement -> Telegram return.
- The UGC ad workflow (S522) adds queue architecture: scheduled trigger -> prompt agent -> Nano Banana Pro job -> polling/backoff -> Sora 2 video -> ffmpeg merge -> Sheets -> Blotato.
- The GitHub issue (S523) gives a traceable workflow artifact: a Product Content Creator JSON attachment linked from the Reddit thread.

Extraction:

- Deterministic preprocessing before AI generation is the strongest small-framework pattern for preserving product truth.
- Async model APIs need job IDs, wait nodes, retry/backoff, logs and human review before any publishing step.

### Open-source build blocks

- `gemini-nano-banana-tool` (S524) is an agent-friendly CLI around Gemini/Nano Banana/Nano Banana 2 and Imagen 4 with promptgen, JSON output, shell-loop batching and multi-image composition.
- OpenTryOn (S525) is a fashion-specific API/SDK stack with virtual try-on and model-swap agents, using provider routing and Nano Banana Pro-style 4K output.

Extraction:

- Internal systems can combine CLI/SDK generation, prompt generation, product references and shell/API batch loops instead of depending only on SaaS wrappers.
- Apparel workflows need outfit preservation and model-disclosure review, not just product-background replacement.

### Trust and failure-mode signals

- EtsyCommunity (S526) shows buyer/seller discomfort with AI or stock mockups when they make a handmade/listing product feel fake; simple background cleanup is perceived differently.
- Dropshipping feedback (S527) shows public QA issues even when images look premium: product text errors, hand/nail realism, promptless output control and weak product differentiation.
- Bilibili and Chinese blog leads (S528-S531) continue to point toward Amazon main/detail-page workflows using GPT Image 2, Doubao/Jimeng and Nano Banana Pro; these still need direct video capture before extracting exact prompts.

Extraction:

- The review rubric should add buyer-trust risk, hands/model realism and text-label diff checks.
- Chinese cross-border workflows should be tracked as prompt/workflow templates first, then converted to SOP only after direct transcript/video capture.

## Goal Continuation: Amazon Native Creative, Ozon/WB Rich Cards And n8n Video Templates

Sources: S532-S546.

### Amazon-native and seller-side creative workflows

- Titan Network's Amazon AI Image Generator SOP (S532) adds a seller-operator pattern around Amazon Creative Studio/Campaign Manager: upload product reference, generate multiple scene variations, organize assets, and A/B test inside campaigns.
- Sellers Ask Sellers (S533) is practical seller evidence: a seller used Gemini to redo catalog images/videos from real product photos, but had to repeatedly tell the model not to alter the uploaded product and still review every detail.
- AmazonFBA image-semantics thread (S534) adds the current SEO/Rufus/COSMO angle: sellers are thinking about whether images answer buyer intent, not just whether they look good.
- SellerBites (S546) is a seller-community policy lead for AI-generated Amazon ad creatives/video ads: acceptable use is framed around compliance, product accuracy, claim discipline and category rules, not generation quality alone.

Extraction:

- Amazon workflows need separate slot policies: Brand Registry/proof/main image stays strict, while Sponsored Brands/A+/Stores/lifestyle can use AI with product-reference review.
- The review gate should score product clarity and buyer-question coverage, not just visual polish.

### Russian Ozon/Wildberries rich-content cards

- Ozon guide (S535) documents a full card-content workflow: title, annotation, long description, attributes, Rich Content, FAQ, reviews and keyword groups.
- Ozon infographic guide (S536) adds the visual/card layer: technical specs on photo, usage diagrams, comparison blocks and icon/text overlays.
- Marketplace tools list (S537) records Neiro Card AI-style one-photo-to-infographic workflows for Ozon/Wildberries.
- Wildberries guide (S538) focuses on WB SEO title, description, bullets, keywords and reviews/questions.

Extraction:

- For Ozon/WB, the target artifact is a rich card, not only a generated product image.
- A batch job row should include factual characteristics, generated SEO text, infographic layout, product photo, review status and marketplace-specific moderation notes.

### n8n and spreadsheet video factories

- Shopify product video template (S539) is concrete: scrape up to 50 products from a Shopify store, filter images with overlaid text, generate scripts/prompts and create short product/UGC videos with Seedance/ElevenLabs/Latentsync.
- Aireiter (S540) gives a product-image-to-UGC ad flow: n8n form -> Google Drive public link -> OpenAI image analysis -> NanoBanana enhancement -> Veo3 video.
- GrowwStacks (S541) uses Google Sheets rows as the production ledger for UGC/product testimonial videos with NanoBanana Pro and Veo 3.1.
- AI Agents A-Z repo (S542) provides traceable GitHub folders for Shopify product videos, Nano Banana UGC videos and Nano Banana Pro infographics.

Extraction:

- The strongest reusable pattern is spreadsheet/workflow orchestration plus async model job handling.
- Product images with text overlays should be filtered or handled separately because text preservation remains a frequent failure mode.

### Official model surfaces and technical signals

- Adobe Firefly (S543) positions Nano Banana 2/Pro inside Firefly and Photoshop for product mockups, accurate text and refinement via Generative Fill.
- Google Workspace update (S544) confirms Nano Banana Pro in Slides/Vids/NotebookLM, including infographic generation, multi-turn image refinement and Vertex AI/Gemini Enterprise access.
- HN Nano Banana Flash discussion (S545) is useful for architecture and operations: conversational editing, multi-image composition, product variation consistency, SynthID and version-control concerns.
- Earlier Snapshot Shopify builder evidence (S192) reinforces the exact fidelity risk: Flux/Stable Diffusion struggled with product/background fit and preserving text/fine details; newer OpenAI image model improved quality but masking remained a blocker.

Extraction:

- Official design surfaces are useful for A+ infographics/mockups, while APIs/CLI are better for batch.
- Generated-set versioning and image diffing should become a first-class requirement when outputs are iterative and conversational.

## Goal Continuation: 2026 Model Routing, Shopify Phone Prompts And Product-Photo-To-Video

Sources: S547-S558.

### Model-routing evidence

- MindWiredAI (S547) is useful because it compares GPT Image 2 and Nano Banana 2 with identical prompts across product mockups, lifestyle shots, infographics and posters; the actionable split is GPT Image 2 for editorial/detail-heavy interpretation and Nano Banana 2 for stricter literal composition.
- Pilio (S548) adds a concrete GPT Image 2 workbench case for multilingual typography, packaging, infographics and product rendering, while also documenting Nano Banana 2 as better for realism/multi-reference exploration.
- Floatboat (S551) pulls Midjourney V8 back into the current routing frame: GPT Image 2 for readable text and production layouts, Midjourney for aesthetic voice, Nano Banana 2 for fast/cheap ideation.
- MotionifyAI (S553) adds the batch angle: GPT Image 2 thinking mode plus up-to-10 image variants is being positioned for ecommerce product shots and advertising variant pipelines.

Extraction:

- Route by artifact slot: typography/packaging/infographic -> GPT Image 2; strict flat-lay or fast ideation -> Nano Banana 2; high-style hero/moodboard -> Midjourney V8.
- Third-party workbench claims should become test cases, not accepted facts: record model snapshot, output size, watermark/provenance, reference-image limits and batch behavior.

### Prompt libraries and Shopify seller practice

- Ilisai (S549) gives structured Nano Banana Pro prompt categories: catalog-ready product photography, virtual try-on, background cleanup and targeted edits, with 1:1/4:5 4K guidance for Amazon/Etsy/Shopify.
- Shopify Reddit (S550) is practical seller evidence: a mobile product photo can be turned into a 2048 square white-background main image or lifestyle scene with explicit constraints for realistic color, focus, product fill ratio and no extra text/logos/watermarks.
- Skywork (S557) records a broader marketplace prompt library: Amazon-safe white-background main images, Shopify 2048 square images, lifestyle/secondary frames and specialty product setups with fill-ratio, lighting and no-text constraints.
- Media.io (S558) contributes a prompt-card workflow: choose image-to-image, upload product, lock product shape/label, vary background/props/camera angle and generate Amazon/Shopify/ad variants.

Extraction:

- Mobile-photo-first workflows are viable for small sellers only if label/color/shape QA is explicit.
- Prompt libraries are most useful as slot templates; they still need product-truth packs and marketplace-specific compliance checks. The earlier Reddit one-prompt layout thread remains tracked as S112, not a new source here.

### Nano Banana Pro product sets and video

- Banana AI Pro (S555) shows a reusable multi-scene prompt: one product rendered across studio, wood table, home interior and outdoor contexts, with centered product and consistent branding for Amazon/Shopify.
- Reelmation (S556) connects still product generation to video: use reference images for label/text and multi-angle consistency, then turn an approved still into a Veo 3.1 product video.
- Morphed (S552) adds current Nano Banana 2 capability claims around 4K, 14 aspect ratios, image search grounding, improved hands/object consistency and product-label prompts.
- Instant (S554) maps Shopify-specific tooling, especially packshots, AI avatar models and direct Shopify integration.

Extraction:

- Product-photo-to-video should inherit approved stills instead of regenerating from text; this reduces product drift.
- Nano Banana wrappers must be checked for watermarking, commercial terms, true export resolution and whether reference-image behavior matches the claimed model.

## Goal Continuation: Seller Cost Replacement, WB Native AI Media And Prompt Libraries

Sources: S559-S570, plus earlier S062 for AmazonFBA cost context.

### Seller cost and ad-creative replacement

- Ecommerce ad/product-image thread (S559) adds a practical seller workflow: start from one clean product photo and build lifestyle/ad variants for product pages and paid traffic with Pixup AI, Nano Banana, Midjourney, Photoroom or RotateProduct.
- Earlier AmazonFBA cost thread (S062) gives concrete operating pressure: 40-50 photos/month, Fiverr 4-5 EUR per basic white-background image and 20-30 EUR for lifestyle shots. The community route is lightbox/phone source shots, batch background removal, AI mockups/lifestyle variants, and outsource only high-polish hero images.
- BuildInPublic fashion thread (S568) reframes the same cost problem for apparel: the product idea is not one Nano Banana edit but product -> model shots -> lifestyle/editorial variations -> matching video ads -> reusable templates, with consistency across shots as the core value.
- Ecommerce ad creative thread (S569) is a demand/risk signal: sellers want alternatives to $800-$1000 shoots, but AI ad creatives that "feel off" still hurt trust.
- AI_UGC_Marketing thread (S570) adds a practical model-routing caution: Nano Banana Pro is used for background removal and touch-ups, but some community feedback routes final store-ready presentation toward Seed Edit and stresses improving the original product photo first.

Extraction:

- The usable production split is routine catalog cleanup and variant generation in AI, with professional/manual effort reserved for hero, premium or difficult shots.
- Track cost per usable image, redo rate, product-drift failures and trust failures; raw generation count is not enough.

### Wildberries official AI media stack

- Wildberries video-cover docs (S565) confirm the platform-native path: generate video covers from 2-5 photos, animate an infographic, create AI video from one product/person photo, or make live photos; generated covers can be added to cards and may autoplay depending on limits/subscription.
- Wildberries rich-content docs (S566) confirm neural rich-content generation from card data: photos, title, category and characteristics produce 10 blocks with text, photos and icons.

Extraction:

- WB/Ozon-style platforms are moving AI media into the seller portal, so external tools need to understand native slots, limits and moderation rather than just output images.
- Generated text/icons/video covers need review gates because platform AI can still misread products or produce factually wrong blocks.

### Prompt libraries, Chinese guides and small frameworks

- PromptCentral (S560), Bilibili Nano Banana guide (S561), Bilibili 100+ case pack (S562), devanshug GitHub prompt repo (S564), EQ4C (S567), Skywork (S557) and Media.io (S558) all reinforce prompt libraries as reusable production inputs.
- NanoBananaAI repo (S563) is a small NextJS/resource app case for product placement, background replacement, lifestyle photography and A/B product presentation testing.

Extraction:

- Prompt packs should be converted into structured SKU briefs: product facts, slot, marketplace constraints, aspect ratio, negative constraints, reference photo and QA checklist.
- Chinese Bilibili/API-pack evidence remains useful, but exact prompt capture should be upgraded later with direct video/article extraction where possible.

## Goal Continuation: Open-Source Layers, YouTube/HN Evidence And Seller Workflow Threads

Sources: S571-S589.

### YouTube and HN current signals

- Chris Rawlings YouTube/Glasp transcript (S571) is a useful Amazon-specific lead: the video claims a complete Amazon listing image set built with Nano Banana Pro, intentionally using a product with label text and difficult feature visualization. This should be prioritized for full transcript/video capture later because it directly matches Amazon listing-image production.
- HN pricing/capability thread (S574) gives current builder-side claims around Nano Banana Pro/Gemini 3 Pro Image: low per-image pricing, native 4K, text rendering, multi-object consistency and studio-physics prompts. Treat this as a claim surface, not verified pricing.
- Show HN playground thread (S575) is useful because the builder explicitly asks for feedback from production creative/UGC pipeline builders and lists desired controls: aspect ratios, typography/layout, prompt engineering and editing workflows.

Extraction:

- HN is weaker as production evidence but strong for current technical vocabulary, pricing sensitivities and desired workflow controls.
- YouTube/Glasp sources are high-priority when they include marketplace-specific walk-throughs; the next pass should capture full transcript/metadata where possible.

### Open-source CMS, prompt-search and agent layers

- WP Banana (S572) is a concrete CMS-native pattern: bring your own OpenAI/Google/Fal/Replicate key, generate/edit images inside WordPress Media Library, and use outputs in WooCommerce/Elementor workflows.
- gemimg (S573) adds a useful batch trick: Nano Banana Pro can produce a grid of variants in one high-resolution generation, then the wrapper slices cells into separate files. This is more useful for ideation/variation than exact product-proof output.
- YouMind GPT Image 2 and Nano Banana Pro prompt skills (S576-S577) turn prompt libraries into searchable agent skills with category routing, prompt remix and frequent community-sync updates.
- Chaitali/Maynor/SimonHuang sources (S578-S582) expand the small-framework map: ecommerce visual-engine concepts, ad/marketing visual workflow READMEs, batch review workflow and agentic draw-batch/cost tracking.

Extraction:

- The practical framework layer is not a single monolithic app. It is CMS/plugin integration plus prompt search plus lightweight batch runners plus cost/run metadata.
- These repos should be treated as patterns and source-discovery maps until installed or tested. Key validation points: model access, export resolution, watermarking, license/commercial terms, prompt-data quality and product-truth QA.

### Reddit seller methods and demand signals

- AI_UGC_Marketing realism thread (S583) shows the tool stack sellers are comparing: Nano Banana Pro, Seedream 4.5, Pikes AI, Higgsfield, Tagshop AI and ProductPose. Strong repeated constraints are reference uploads, consistent lighting, clean angles, text distortion and hallucinated product details.
- Dropship thread (S584) is dropshipping-specific: AI creates unique lifestyle shots from supplier images, but poor source images, logos, small text and exact packaging remain limiting factors.
- MakeMoneyHacks agency post (S585) frames the commercial driver as creative volume: mid-sized ecommerce brands need many paid-ad statics quickly and may pay for brand-specific concepts instead of learning prompt workflows.
- Image-to-image prompt-builder thread (S586) is a fresh workflow demand signal: sellers want a VLM/prompt-builder to read raw product photos and produce technical studio prompts for Nano Banana rather than writing camera/lighting prompts manually.
- Dropshipping software/tool thread (S587), savings thread (S588) and product-photo/video thread (S589) reinforce three production ideas: simplified wrappers, high-volume static generation, and static-first short video to reduce product melting.

Extraction:

- Seller evidence keeps converging on one clean product photo as the minimum truth anchor, then AI for white background, lifestyle, detail shots and short videos.
- Prompt builders and no-prompt scene pickers are valuable because the seller bottleneck is not only model quality; it is translating product photos into repeatable technical prompts and reviewable variants.
- Measure cost per usable image/video, not generation volume. Bulk statics only matter if product-truth rejection rates and trust failures are tracked.

## Goal Continuation: Bilibili Batch Workflows, Agent Skills, Ozon/WB Routes And Amazon Seller QA

Sources: S590-S610.

### Chinese Bilibili and open-source Agent Skill signals

- Bilibili GPT-Image 2 detail-page demo (S590) is a Chinese designer-market signal: GPT Image 2 is being framed for PDP/detail-page layout generation, especially where text and hierarchy matter.
- Nano Banana Pro+n8n Bilibili workflow (S591) is one of the clearest batch architecture leads: one product photo -> two 4K scene masters -> automatic crop into multiple channel sizes -> compression -> S3 upload -> download link. This is directly relevant to Amazon/Shopee/TikTok/Instagram asset fanout.
- 1click-ecom-detailpage blog/forum/repo cluster (S592-S593, S596) and ecom-details-image (S597) shift the Chinese open-source pattern from prompt lists into Agent Skills: buyer reason cards, Campaign Style Lock, 5 main images, 7-9 detail panels, independent prompts and structured output folders.
- gpt-image2-ecommerce (S594-S595) is the cleanest GPT-Image-2 skill-template example in this batch: 25 scene templates, template matching, reference-image consistency and Codex/Claude Code execution.

Extraction:

- The emerging small-framework shape is `Skill.md + prompt templates + imagegen script + output folder contract`, not a large SaaS clone.
- For production, keep the Agent Skill useful but add missing hard gates: product reference, text OCR, policy/claims review, output manifest and cost/retry log.

### Russian Ozon/WB and localized model-router evidence

- Neuroscribe WB/Ozon guides (S599-S600) provide concrete Russian marketplace prompt taxonomy: white background, ghost mannequin, flat lay, lifestyle, category-specific prompts, and model choice between Nano Banana 2, Nano Banana Pro and wrapper access.
- Aijora (S609) is a localized Russian model-router reference with GPT Image 2, Nano Banana 2/Pro and other models, explicit WB/Ozon card/ad use cases, Russian prompts and no-VPN browser positioning.

Extraction:

- Russian Ozon/WB sellers care about local access, Russian text, commercial rights and marketplace-card compliance as much as raw model quality.
- GPT Image 2 should be considered for text-heavy infographics and layouts; Nano Banana 2/Pro for product-scene generation and reference-based photo editing.

### Amazon seller QA and tool-builder feedback

- Finnito Vision Studio thread (S601) shows an Amazon-specific platform-builder data-collection approach: ask for product photo/ASIN, brand colors, competitor references and style direction; return five Amazon-ready images.
- AmazonFBA product-photo cost thread (S602) captures the current alternative set: Seller Central imaging services, under-$100 AI image sites, Rendery3D-style complete listing sets, and ProductPose-style bundle staging from phone photos.
- White-background tool concept (S603) is a narrow but important compliance micro-tool: pure RGB255 background and product visibility coverage.
- AI cat-toy feedback thread (S604) is useful negative evidence: community feedback focused on background, contrast and positioning, showing that AI generation plus manual processing is still not automatically listing-ready.

Extraction:

- Amazon workflows should stay hybrid: compliant main image and product-truth anchor first; AI secondary/lifestyle/infographic panels second; manual design QA last.
- The QA rubric needs design quality as well as product truth: contrast, scale, positioning, clutter, text readability, and whether the visual answers customer questions.

### Batch tool and workflow references

- Nano Banana Batch (S605) is a strong batch UX reference: one image, up to 50 prompts, CSV prompt upload, templates, ZIP export, credit billing and failed-generation refunds.
- GPT Image2 workspace (S606) gives a GPT Image 2 browser-tool pattern with reference upload, product photo/ad creative use cases, multi-output and explicit credit tiers.
- Nano Banana PS plugin and ComfyUI Bilibili videos (S607-S608) show designer-stack integration: keep work inside Photoshop or ComfyUI while using Nano Banana Pro/API wrappers for reference-based generation and limited batch output.
- MarketGuru seller-channel post (S610) is a localized WB/Ozon model-routing signal: GPT Image 2 is framed as stronger for infographics, readable text/layout and face transfer, while small details still need explicit prompt fixation and review.

Extraction:

- The practical batch interface should accept both prompt CSV and reusable slot templates, then export ZIP/S3 plus metadata.
- Measure accepted outputs, human retouch time and rejected failure reasons; raw generation speed is secondary.
- For Russian marketplace cards, separate text-heavy infographic slots from pure product-scene slots because sellers are already comparing GPT Image 2 and Nano Banana Pro by slot type.

## Goal Continuation: Shopify-Native Apps, Batch Photo/Video And Trust-First QA

Sources: S611-S621.

### HN and batch photo/video tools

- Mersel Show HN (S611) is a useful early product signal: the builder explicitly uses Nano Banana and Veo 3.1 APIs to batch-create or edit product photos and videos for ecommerce sellers.
- The website behind Mersel has shifted toward AI-visibility positioning, so the HN thread itself is the evidence for the product-photo/video batch concept.

Extraction:

- Batch still+video production is becoming a separate tool category, not just a feature inside image generators.
- The important implementation detail is set-level generation: sellers want a complete usable asset pack, not individual outputs.

### Shopify-native app and community workflows

- Shopify community product-photography thread (S614) maps the Shopify app ecosystem: Snapshot for bulk AI product photos/backgrounds, SellerPic for AI ads/video/try-on, WearView for flat-lay to on-model fashion photos, plus Booth.ai, Pixc, LightX and PhotoRoom.
- Shopify personalization thread (S615) adds a storefront-side workflow: customer uploads photo -> chooses GenAI style/effect -> preview on product mockup -> checkout. It also notes custom app/API routes with Nano Banana, Flux Kontext, ChatGPT/DALL-E/Midjourney/Stable Diffusion-style services.
- Snapshot App Store listing (S616) confirms core product-listing integration: bulk editor, background removal, custom backgrounds/prompts, generative fill and one-click attach to product listing.
- SellerPic App Store listing and Gist review (S617, S620) show a broader multi-modal workflow: product visuals, AI ads, model swap, virtual try-on, background edits and image-to-video for Shopify/TikTok/Amazon.
- Teeinblue App Store listing (S618) is important for POD/personalization: Gen AI effects, remove background, face cutout, bulk upload, auto sync and print-ready production files.
- Shopify lifestyle thread (S621) shows the current seller-side mix: DIY micro-shoots plus AI tools such as Pikes AI for realistic on-brand bulk updates and Nano Banana for moodboards/visual direction.

Extraction:

- Shopify workflows increasingly value native attachment, preview, bulk editing and production-file automation over standalone image generation.
- For apparel/POD, customer-upload and on-model/try-on flows are as important as listing hero images.

### Trust-first seller critique and service productization

- Dropshipping ad critique thread (S612) shows why raw AI output is not enough: community feedback focused on lighting, product focal point, composition, distracting scenes and visible AI feel.
- Ecommerce “what worked/didn’t” thread (S613) reinforces hybrid usage: AI is useful for social assets and middle-SKU updates when anchored by high-quality product images, while hero or brand-defining shots often still need real shoots.
- Build-in-public service thread (S619) shows prompt iteration becoming a service business: the founder solved AI product photos for their own Shopify store, then packaged the workflow around realistic lighting, consistency and lower seller decision fatigue.

Extraction:

- The seller bottleneck is increasingly QA/taste/decision fatigue, not access to an image model.
- A useful production system should surface reject reasons like `distracting scene`, `product not focal`, `AI feel`, `bad lighting`, `wrong material/detail`, and `needs retouch`.

## Goal Continuation: Tool Workflows, Seed-Set Discipline And Agency R&D Evidence

Sources: S622-S630.

### Tool and workflow-site evidence

- ImagineArt AI product photography (S622) and Lumiet/BananaAI (S624) both reinforce the one-clear-product-photo pattern: upload a usable product image, then generate white-background, lifestyle, seasonal, campaign and social variants.
- Invideo's guide (S625) is useful because it stresses seed-set discipline rather than magic prompts: each SKU needs a strong standardized product input before generating hero, alternate angle, close-up, lifestyle and channel-specific crops.
- imagev2, gptimage.tools and Filmora GPT Image 2 (S623, S626, S628) show the current GPT Image 2 wrapper/editor surface: prompt galleries, product-page examples, packaging mockups, multi-ratio campaign assets and video-editor assisted export.
- Nano Banana Batch ecommerce case studies (S627) add a concrete batch-case taxonomy: one master product photo to dozens of marketplace backgrounds, props, lighting scenarios, furniture showrooms and channel-tested ad variants.

Extraction:

- Strong inputs matter more than generator count. A poor or inconsistent source image creates downstream QA cost across every batch output.
- Tool pages are useful for UX and workflow design, but claims about fidelity, commercial use, exact model access and export quality still need SKU testing.

### Agency and service-workflow evidence

- Reddit AI UGC realistic product photography thread (S629) is a useful caution: realistic client-grade product photography can involve hours of R&D, hundreds of generations and manual Photoshop retouch, and some products still require real photography.
- Bertranddo's workflow index (S630) is a map for deeper follow-up: full AI ecommerce photography workflow, visual syntax research, client photo prep, paid-client delivery, outreach and portfolio building.

Extraction:

- A production system should include an explicit `R&D -> select -> retouch -> deliver` path, not only batch generation.
- Record failure reasons and stop-loss points: wrong dimensions, altered material, bad text/logo, client photo too weak, too many generations per usable result, and cases that should move back to real photography.

## Goal Continuation: Amazon Seller Threads, Benchmarks And Small Prompt/Workspace Frameworks

Sources: S631-S643.

### Amazon seller decision evidence

- AmazonFBA listing photo thread (S631) keeps the cost-replacement pattern alive: sellers mention Nano Banana Pro, Rendery3D and Photoroom as alternatives to Fiverr or pro shoots, but still call out design sense and packaging second passes.
- AmazonFBATips creative hub thread (S633) adds a useful caution: some sellers want all-in-one brand analysis + prompt writing + 8K listing images, while others warn that overly rendered images can create Amazon risk.
- AmazonFBATips no-prompt thread (S634) is a direct no-prompt workflow signal: one product photo -> automatic product analysis -> hero/lifestyle/infographic listing set.
- DIY/360/pro studio thread (S635) gives a category heuristic: hard goods can often use phone photos plus AI; textiles and organic/food products remain harder and may still justify real photography.

Extraction:

- Amazon image generation should be a make/buy/category decision, not a model-only decision.
- The QA layer should explicitly flag `over-rendered`, `packaging needs second pass`, `textile/food realism risk`, `main image risk`, and `needs real shoot`.

### Benchmark and model-routing evidence

- AMALYTIX benchmark (S632) is one of the strongest structured sources in the current set: seven Amazon products by seven image scenarios, with GPT Image 2 leading overall but macro details, size ratios and photorealism still requiring manual validation.
- AdDogs (S640) is ad-focused but useful for the same routing question: product photo + logo + reference ad + brand colors points toward multimodal ad workflows rather than pure text-to-image.
- Bananai GPT Image 2 page (S643) shows current wrapper positioning: GPT Image 2 for text-heavy product graphics, packaging, infographics, structured layouts and 4K export options, with Nano Banana family as comparison routes.

Extraction:

- Model routing should be by asset type: infographic/application/scale/text-heavy cards are different from lifestyle scenes, macro details and final render shots.
- Benchmarks should be used to define QA categories, not to remove human review.

### Small framework and prompt-system evidence

- Banana Mall (S636) is a strong local-first small framework: product image -> product analysis -> structured detail page -> section-level regeneration/versioning, with OpenAI-compatible multi-provider support.
- AI Image Bible (S637) generalizes the prompt/payload layer across GPT Image 2, Midjourney V8.1 and Nano Banana Pro, including JSON prompting and interleaved reference-image patterns.
- GPT Image 2 Prompt Framework (S638) contributes reusable reference-role language, especially `object/product anchor` for shape, label, materials and proportions.
- Prompt Director (S639) is thin but useful as a UX reference for guided creative briefs before image generation.
- Nano Banana Pro prompt gallery and Morphic guide (S641-S642) extend product-shot template taxonomy: white background, macro, knolling/labeled parts, skincare, jewelry, packaging, product ads and common mistakes.

Extraction:

- The most reusable architecture emerging from small frameworks is `product analysis -> structured brief -> prompt/payload compiler -> slot/module generation -> versioned review`.
- Prompt galleries are useful seed libraries, but every template must be filled with SKU facts and checked against real product references.

## Goal Continuation: Buyer-Trust Threads, Chinese PDP Workflows And Wrapper Leads

Sources: S644-S654. Website cases: W363-W373. Methods: M173-M175.

- `S644` / `W363` records an AmazonSellercentral thread asking what AI tools sellers use for Amazon listing images. It is useful as a demand-side seller workflow lead: one product photo, then hero/lifestyle/infographic listing sets for Amazon.
- `S645` / `W364` and `S646` / `W365` add negative buyer/reviewer evidence from EcommerceWebsite and AmazonVine. These are not model benchmarks; they are QA failure-mode evidence showing why product size, measurements, material, texture, color and received-product match must be checked before publishing edited or generated listing images.
- `S647` / `W366` records Piccc as a Chinese product-image generator/tool surface for one-click ecommerce product visuals and scene/main-image generation.
- `S648` / `W367` records StartAI's Photoshop/Nano Banana ecommerce detail-page tutorial. The important pattern is not only image generation, but keeping the designer in Photoshop with editable layers/modules.
- `S649` / `W368` records APIYI's Nano Banana Pro ecommerce detail-page guide. It is useful for API/batch-oriented prompt patterns around Chinese product detail pages.
- `S650` / `W369` records Aicodehub's AI ecommerce image workflow tutorial, which adds Chinese/cross-border product main-image and detail-page prompt workflow coverage across GPT Image 2/Nano Banana-style routes.
- `S651` / `W370`, `S652` / `W371` and `S653` / `W372` add wrapper/tool leads around GPT Image 2, AI product photography/video and localized Chinese Nano Banana access. These are useful for mapping what small sellers actually encounter, but still need real-SKU trials before treating model access, rights, watermark and fidelity claims as proven.
- `S654` / `W373` adds BrandGene's ecommerce AI product photography guide as a DTC/brand-consistency workflow reference.

Reusable methods added:

- `M173`: buyer-trust negative-evidence QA. Use edited/generated image complaints as a risk taxonomy for scale, measurement, color, material, texture and return-risk checks.
- `M174`: Chinese PS/API ecommerce PDP workflow. Use Nano Banana/GPT Image routes through Photoshop plugin/API/local workspace, retain editable modules, and proof Chinese text/product facts.
- `M175`: wrapper-led one-photo product media workflow. Use one product photo or prompt to generate listing/ad/video variants, then verify provider/model rights, watermark, product fidelity and export quality.

## Goal Continuation: Prompt/MCP Frameworks, Amazon Reference Chains And Nano Banana 2 Edit Workflows

Sources: S655-S664. Website cases: W374-W383. Methods: M176-M178.

- `S655` / `W374` records `wuyoscar/GPT-Image2-Skill`, a prompt-gallery plus Codex/Claude skill and CLI surface for GPT Image 2. It matters because it packages Product & Food, Brand Systems, Photography and Infographics prompts into a reusable local agent workflow rather than only a webpage.
- `S656` / `W375` records `jau123/nanobanana-trending-prompts`, which mines X prompt examples and ranks them by engagement. It adds prompt-source/provenance evidence, but virality is not the same as marketplace compliance.
- `S657` / `W376` records `MeiGen-AI-Design-MCP`, a small open-source MCP layer that routes GPT Image 2, Nano Banana 2, Seedream, Midjourney and local ComfyUI routes from agent clients. This is a useful framework lead for prompt search, provider routing and parallel variation generation.
- `S658` / `W377` records fal's GPT Image 2 review and Nano Banana 2 comparison. The useful method detail is model/cost routing: low-quality drafts, upscaling, 4K cost, reference limits and mask-edit support should be part of production planning.
- `S659` / `W378` records Lumiet's Amazon seven-image Nano Banana Pro workflow. It uses a primary visual anchor, lifestyle references, typography baseline and dual-reference graphics instead of independent unrelated prompts for each listing slot.
- `S660` / `W379`, `S661` / `W380` and `S662` / `W381` add Nano Banana/Nano Banana 2 product-image wrapper and prompt-guide evidence around edit-first workflows: keep a real product anchor, change one thing at a time, then scale only after SKU tests.
- `S663` / `W382` records a Bilibili Nano Banana Pro 2026 tutorial collection with an indexed ecommerce detail-page lead. It is currently a search/page evidence item and needs episode-level capture before final workflow claims.
- `S664` / `W383` records a broad multi-model prompt repository with JSON product-photography prompts. It is useful for prompt corpus coverage, but not proof of product fidelity.

Reusable methods added:

- `M176`: agentic prompt-gallery CLI/MCP workflow. Search prompt corpora, retrieve prompt/source/reference context, rewrite for SKU facts, generate through CLI/MCP/provider routes and log provenance.
- `M177`: Amazon seven-image reference-chain workflow. Use one product anchor and typography baseline across main, lifestyle, benefits, instruction and comparison slots to reduce drift.
- `M178`: Nano Banana 2 edit-first product workflow. Start from real product/cutout, make a narrow edit/fusion, iterate cheaply, upscale/export winners, then batch only after SKU-level QA.

## Goal Continuation: Shopify-Native Apps, Form/Sheet n8n Approval And Product-Link Catalog Pipelines

Sources: S665-S674. Website cases: W384-W393. Methods: M179-M181.

- `S665` / `W384` and `S666` / `W385` record ImageDream from both Shopify Community launch feedback and the App Store page. The useful signal is Shopify-native product upload, preset backgrounds, bulk image generation and claimed preservation of packaging text/fine details.
- `S667` / `W386` records the official AiShots Shopify app page to complement the earlier Reddit builder thread. It confirms direct Shopify product-media save, lifestyle scenes, virtual models, chat/edit-like workflow and Gemini/OpenAI API positioning.
- `S668` / `W387` records a GrowwStacks n8n template that uses Jotform submissions, Gemini Nano Banana, quality/approval routing and Google Sheets output links. This is a stronger structured approval pattern than a raw model-call workflow.
- `S669` / `W388` records Marktech's D2C guide. It reinforces the operating model: start from a real product photo, use AI for the world around it, then use n8n to pull Shopify assets, resize for Meta/Amazon and upload outputs back.
- `S670` / `W389` records a SellShots Reddit launch thread. It is useful mainly because the first feedback focuses on product accuracy, label/logo/text consistency, marketplace-safe outputs and batch controls.
- `S671` / `W390` and `S672` / `W391` record Emagify as both a Reddit side-project case and official site. The current pattern is no-prompt fashion/catalog generation: garment photo to model-wearing image, product catalog templates, bulk processing and try-on.
- `S673` / `W392` records a dropshipping product-link-to-landing-page pipeline. The important claim is product understanding before image generation, because boring/electronics/kitchen products often fail when image generation starts from a generic prompt.
- `S674` / `W393` records a Shopify AI and Automations AMA thread where a merchant says Shopify admin image generation can create product images and people wearing/using products for product-media/lookbook tests. This adds a native Shopify direction alongside third-party app dashboards.

Reusable methods added:

- `M179`: Shopify-native product-media generation workflow. Generate scenes/model shots inside Shopify native surfaces or apps and save to product media/lookbooks, with manual review before publish.
- `M180`: form-or-folder n8n product photography approval workflow. Use Jotform/Drive/Telegram inputs, model generation, QC, human approval and Sheets/CMS/Shopify output ledgers.
- `M181`: product-link and fashion catalog generation workflow. Extract product facts or garment identity first, then generate images/copy/model shots/page modules with marketplace and trust QA.

## Goal Continuation: Russian WB/Ozon GPT Image 2, Nano Banana Pro And URL-To-Card Workflows

Sources: S675-S684. Website cases: W394-W403. Methods: M182-M184.

- `S675` / `W394` records a VC.ru GPT Image 2 guide for creating Wildberries/Ozon product cards. It is useful as a localized Russian card-prompt source, especially for product-reference-first GPT Image 2 marketplace visuals.
- `S676` / `W395` adds a Wildberries/Ozon prompt-pack article. The main value is not that prompts are universally reliable, but that it captures Russian card copy, benefit layouts, infographic intent and localized marketplace prompt structure.
- `S677` / `W396` records a Nano Banana Pro workflow for expensive-looking marketplace cards. This extends the Russian card stack toward product-reference lifestyle and premium thumbnail direction.
- `S678` / `W397` records the Habr URL plus Visual Prompting workspace pattern. This is a stronger architecture lead: product page URL -> extracted facts/images -> visual prompt/card brief -> generated marketplace card, with source traceability as the required QA boundary.
- `S679` / `W398` records a Sostav comparison of Nano Banana Pro versus GPT Image 2 for marketplace card creation. It supports model routing by task rather than treating one model as the universal answer.
- `S680` / `W399` records a Universus Ozon guide around AI product cards and Rich Content. This expands the Ozon line from image generation into listing/rich-content operations.
- `S681` / `W400`, `S683` / `W402` and `S684` / `W403` add DTF/Sostav Russian tutorials and tool-list coverage for marketplace product photos and cards.
- `S682` / `W401` records WildAI as a localized WB/Ozon workspace/tool surface for marketplace cards and rich content. It should be tested with real SKUs before treating claims about output quality or moderation readiness as proven.

Reusable methods added:

- `M182`: Russian WB/Ozon prompt-pack card workflow. Use product photo, category, card type, Russian copy and marketplace-specific prompt templates, then proof Cyrillic text and moderation constraints.
- `M183`: URL-to-card visual-prompt workspace workflow. Ingest a product URL, extract facts/images, compose a visual prompt/card brief and generate variants with source URL logging and SKU fact checks.
- `M184`: Russian marketplace rich-content tool workflow. Generate product-card visuals, rich-content blocks and SEO assets through localized tools, then review characteristics, generated text/icons and platform moderation fit.

## Goal Continuation: HN Model Discussions, GPT Image 2 Prompt Corpora And Nano Banana 2 Product Studio Routes

Sources: S685-S694. Website cases: W404-W413. Methods: M185-M187.

- `S685` / `W404` records the Hacker News Nano Banana Pro discussion. It is useful for model-release sentiment, especially community claims around legible text and compositionality, but also for verification and geometry failure notes.
- `S686` / `W405` records the HN ChatGPT Images 2.0 discussion. The value here is source discovery: it links to GPT Image 2 prompt showcases, GitHub prompt corpora and standardized quality checks.
- `S687` / `W406` records a HN Nano Banana prompt-engineering/failure-mode thread. The important extraction is product-risk oriented: random edits, scale drift and subtle detail changes are exactly what listing/product QA must catch.
- `S688` / `W407`, `S689` / `W408`, `S690` / `W409` and `S691` / `W410` add GitHub prompt-corpus and Prompt-as-Code sources. These are not product-fidelity proof; they are reusable prompt/template infrastructure for product posters, ecommerce app UI, skincare hero posters, packaging/detail-page structures and X-attributed examples.
- `S692` / `W411` records Lumiet's Nano Banana 2 model page, including white-background product photography, Amazon/Shopify/catalog positioning, 4K output, rapid iteration, text rendering and background replacement.
- `S693` / `W412` records YourRender's community test of Nano Banana 2 for product photography. The operational signal is tiering: use NB2 for fast/routine product visuals and reserve Pro for critical hero shots.
- `S694` / `W413` records Plykit's Nano Banana 2 product-studio page, adding edit/create modes, reference images, trend/web-search language and ecommerce product-photo workflow positioning.

Reusable methods added:

- `M185`: GPT Image 2 prompt-as-code corpus workflow. Search prompt repos, rewrite with SKU facts, generate through API/CLI/tool routes, and log source prompt plus QA notes.
- `M186`: HN/community model-risk intake workflow. Turn release-thread comments and linked quality checks into model-risk categories and QA checklist updates rather than treating them as benchmark truth.
- `M187`: Nano Banana 2 speed-tier product studio workflow. Use NB2 for fast routine product variants and Pro/higher-cost routes for critical hero shots, with provider/resolution/product-fidelity checks before scaling.

## Goal Continuation: Chinese Coze/Feishu Batch, Zero-Prompt Studios And Vertical Image-Video Tools

Sources: S695-S706. Website cases: W414-W425. Methods: M188-M190.

- `S695` / `W414` records KatuAI as a Chinese Nano Banana 2/Nano Banana Pro toolbox with ecommerce main-image optimization, white-background product images, creative product scenes, AI try-on, marketing images and banner design.
- `S696` / `W415` records a XinianAI review. The useful workflow detail is image-to-video consistency: generate a nine-grid set of product views first, then use Sora2/Veo3.1 to create product videos while reducing product deformation.
- `S697` / `W416` records a Juejin Coze workflow lead for bestselling ecommerce main images: competitor reference -> selling points -> prompt -> Nano image plugin -> Feishu Bitable batch operation.
- `S698` / `W417` records a Bilibili-indexed Feishu Bitable + Nano Banana batch tutorial claiming 20 ecommerce main images per minute. It needs direct video capture later, but is a useful Chinese workflow discovery node.
- `S699` / `W418` adds Qovai as a Product Hunt-style social-media product-photo workflow: upload product image, choose reference style/library and schedule product visuals to social.
- `S700` / `W419`, `S702` / `W421`, `S703` / `W422` and `S706` / `W425` expand the zero-prompt/template tool group: Cheeppy, ShopYa and AIMS use product upload + template/style/channel choices rather than heavy prompt engineering, with some store integration and batch claims.
- `S701` / `W420`, `S704` / `W423` and `S705` / `W424` add vertical image/video studio cases: Kotoor catalog-to-campaign, PhotoIQ on-model/flat-lay/product-video routes, and Orniva jewellery-specific batch/Shopify/WooCommerce publishing.

Reusable methods added:

- `M188`: Chinese Coze/Feishu/Nano ecommerce batch workflow. Use table rows as the batch ledger, with source photos, competitor references, prompt rows, generated outputs and review status.
- `M189`: zero-prompt template product-photo studio workflow. Product photo + style/template + channel target replaces prompt writing, but product geometry, label and platform checks still remain.
- `M190`: vertical fashion/jewellery image-and-video batch studio workflow. Route by category and review material-specific details such as garment drape, jewellery reflections, gem transparency and video drift.

## Goal Continuation: Open-Source GPT Image 2 Workbenches, API Skills, Shopify Seller Threads And Fresh Model-Tier Signals

Sources: S707-S727. Website cases: W426-W446. Methods: M191-M196.

- `S707` / `W426`, `S709` / `W428` and `S710` / `W429` expand the prompt/tool page layer for Nano Banana Pro: prompt packs for product photography, packaging labels, ecommerce ad prompts, uploaded product-photo edits, 4K output and batch queueing.
- `S708` / `W427` adds a 2026 product-photography benchmark source. It is useful for model routing, especially packaging text and complex object detail, but should be replicated on the target SKU categories before adoption.
- `S711` / `W430` records GPT Image Playground as a small open-source workbench: prompt templates, reference editing, history, provider configuration, costs, multi-model routes and Tauri/self-hosting.
- `S713` / `W432` records RedBox as a Chinese open-source media/content workspace. The notable ecommerce update is brand/product/platform/language organization for AI-generated cross-border detail-page images.
- `S712`, `S714-S718` and `W431`, `W433-W437` add the API/agent layer: Codex/OpenAI Images skill, APIDotAI examples, RunAPI SDK and skill, HiAPI prompt gallery and HiAPI GPT Image 2 skill. The common operational pattern is async generation with task IDs, polling/webhooks or agent skills, plus prompt-gallery adaptation.
- `S719-S724` / `W438-W443` add Shopify seller-community workflow evidence: Snappyit flat-lay to ghost mannequin and cleanup, Pikes AI visual enhancement, Trayve AI model shots, Bloom AI fashion photos/videos, Modelfy phone-photo to studio/model/campaign/video content, and a 500-SKU catalog-content scaling thread.
- `S725-S727` / `W444-W446` add fresh Bilibili signals around Nano Banana 2 control/cost, Nano Banana 2 versus Pro economics, and GPT Image 2 versus Nano Banana 2 creator sentiment. These are leads for direct testing, not final benchmarks.

Reusable methods added:

- `M191`: open-source image workbench and media-suite workflow. Use a self-hosted workbench or local app to manage provider endpoints, prompts, references, history, cost and product media libraries.
- `M192`: GPT Image 2 async API and agent-skill workflow. Submit jobs through SDK/API/skill, persist task IDs, poll or handle webhooks, and keep a run ledger with QA status.
- `M193`: prompt-guide plus benchmark product-photo workflow. Treat prompt guides as reusable grammar and benchmark claims as routing hypotheses; replicate on real product references before scaling.
- `M194`: Shopify seller AI-media shortlist workflow. Mine seller-community/app signals, classify by job type, trial on a small SKU set and check permissions, product identity and analytics.
- `M195`: 500-SKU catalog content stack comparison workflow. Choose routes per content slot and separate primary product-truth images from supplementary ad/lifestyle variants.
- `M196`: Nano Banana 2 cost-tier and control validation workflow. Use NB2 for low-cost routine tests only after checking current quota, routing, Chinese text, hallucination and product fidelity against Pro/GPT Image 2.

## Goal Continuation: Dedicated Ecommerce Studio Systems, Platform Trust Threads And New Model Watchlist

Sources: S728-S747. Website cases: W447-W466. Methods: M197-M201.

- `S728` / `W447` and `S729` / `W448` add Nightjar's 2026 production framing: evaluate AI product-photo tools by catalog consistency, product preservation and marketplace readiness; use real phone/iPhone capture as the truth layer and AI recipes for scalable variants.
- `S730` / `W449`, `S731` / `W450`, `S732` / `W451` and `S733` / `W452` add dedicated ecommerce studio/workflow pages: Caspa, Pixair and Snappyit. The strongest signal is not generic generation but slot-specific output: PDP master images, variant covers, model shots, video, Shopify app pushback, Amazon hero/alt/A+/Sponsored Brand slot matrices and platform crops.
- `S734` / `W453`, `S735` / `W454` and `S742` / `W461` add Rendery3D as an Amazon/Shopify full listing-stack case, including automated 9-image sequences, A+ content, marketplace resizing and an Automatic Feedback Loop claim.
- `S736` / `W455` and `S737` / `W456` extend the GPT Image 2 line into text-heavy product assets and API routing: packaging text, A+ content, Shopify hero images, commercial mockups, provider failover and OpenAI-compatible access.
- `S738-S741` / `W457-W460` add trust and compliance evidence from Amazon Seller Forum, eBay Community and Reddit. These are not generation methods; they are guardrails around misleading images, actual item photos, AI-edited return risk and source-photo proof.
- `S743-S746` / `W462-W465` add a watchlist for new models/frameworks: HiDream-O1-Image, Vercel AI SDK Image Generator, Bria FIBO and Backblaze's image-generation API list. These require ecommerce-specific benchmarking before adoption.
- `S747` / `W466` adds Nightjar's help desk as a current platform-policy and production-risk index across AI disclosure, misleading content, shape preservation, negative prompts and consistency controls.

Reusable methods added:

- `M197`: dedicated ecommerce studio consistency evaluation workflow. Test tools on a representative SKU set and measure product preservation, visual drift, export/store writeback and manual edit rate.
- `M198`: Amazon listing stack generator workflow. Build full Amazon image sets while keeping main-image compliance separate from lifestyle/A+/ad assets.
- `M199`: marketplace trust and AI-image compliance workflow. Classify each generated image by edit type and require real-source proof for main/trust-sensitive slots.
- `M200`: GPT Image 2 text-heavy commercial asset routing workflow. Use GPT Image 2-style models for labels, callouts and A+ modules, but OCR/manual-proof every claim and log provider route.
- `M201`: open model and multi-provider framework watchlist workflow. Promote new open models/frameworks only after SKU-level product-fidelity, license and orchestration benchmarks.
## Goal Continuation: Russian Ozon/WB Card Tooling, Bilibili Cross-Border Tutorial Clusters And Frontier Risk Evidence

Sources added: `S748`-`S760`. Website cases added: `W467`-`W479`. Methods added: `M202`-`M204`.

- Russian Ozon/WB card-tooling cluster: Loonia, Epokha, Sostav, AI-Electronic and MashaGPT all point to a full listing-card workflow, not just image generation. The reusable structure is product facts plus SEO copy, product-card/infographic/video-cover generation, marketplace-specific aspect ratios, and final review for false claims or incorrect product characteristics.
- Russian prompt and portfolio cluster: Texblog, VEO4YOU and Behance add Nano Banana Pro prompt-pack and designer-reference evidence for WB/Ozon/Yandex/Kaspi cards. Treat these as prompt/design references; exact product dimensions, labels, Cyrillic text and marketplace claims still need manual or OCR review.
- Bilibili cross-border cluster: current indexed Chinese leads are useful as discovery nodes for GPT Image 2 one-click Amazon/cross-border main images, Coze batch image sets, and Nano Banana 2 competitor/bestseller reverse-engineering. These rows stay at `verified_search` until direct BV pages, metadata or subtitles are captured.
- Frontier risk evidence: the arXiv risk preprint is not an ecommerce workflow, but it supports the review gate around realism, legible text, reference consistency, provenance and misleading synthetic visual evidence.
## Goal Continuation: Reddit Seller Workflows, Claude/GreenOnion Amazon Systems, Composite QA And New Video Leads

Sources added: `S761`-`S778`. Website cases added: `W480`-`W497`. Methods added: `M205`-`M208`.

- Brand-system-first Amazon listing generation: Reddit and Clair evidence now shows a pattern where the model/agent first creates a reusable brand file from site/logo/product photos, then generates named Amazon slots such as Hero, Benefits, Features, Us vs Them, What is Included, Use Case and Brand Story. This is stronger than prompt-by-prompt generation because it preserves brand decisions across SKUs.
- GreenOnion/WorkFx complete listing sets: new rows capture one-photo-to-9-image Amazon workflows, feature assignment, generated listing copy and Amazon-specific slot mapping. These are useful as product UX references, but the claims need real SKU tests for product fidelity, text accuracy and main-image compliance.
- AI scene plus real product composite: Promptolis and the Amazon image-to-video Reddit thread both converge on the same rule: let AI create the scene, but composite the real product and real logo/text in Figma/Photoshop/Canva/Photopea. This is the safer route for branded products, handmade goods, labels and video ads.
- Nano Banana 2 CMS/prompt-library route: Biteabyte, PicassoIA, Vofy, Aino, GPT Image 2 Prompt Gallery and BuildWay add a pipeline from category prompt templates to Gemini/Vertex/CMS media writes, SEO metadata and SynthID/provenance review. Prompt galleries are sources for pattern mining, not final product truth.
- New Bilibili capture queue: `S776`-`S778` are still `verified_search`, but they point to specific tutorial clusters: Coze+GPT Image2 compliant ecommerce main/detail workflow, GPT Image2 Amazon main-image formula, and Nano Banana/Gemini/ComfyUI layered PSD detail-page output. Next deepening step is direct BV capture plus metadata/subtitles/resources.

## Goal Continuation: Prompt Grid Workflow And Official Preset Tool Counterparts

Sources added: `S779`-`S785`. Website cases added: `W498`-`W504`. Methods added: `M209`-`M210`.

- `S779` / `W498` records a PromptingMagic Universal Product Ad Grid thread. The useful pattern is a six-angle visual board from an object reference image: hero, closeup, lifestyle/in-use, detail and ad/comparison directions. It should be treated as concept planning, not final production media, because a single generated grid can lose resolution or drift product details.
- `S780` / `W499` records Pikes AI as the official tool counterpart for multiple seller-community mentions. This adds a product-upload, preset/no-prompt, product-photo/video workflow to benchmark against Shopify/Amazon needs.
- `S781` / `W500`, `S782` / `W501`, `S783` / `W502` and `S784` / `W503` add MagicShot, WizStudio, WaveSpeed and Eshot official product-photo pages. These are useful because they convert scattered community tool mentions into concrete benchmark candidates with URLs, workflow claims and marketplace fit.
- `S785` / `W504` adds Tagshop as a combined product-photo, UGC video and brand-ad creative hub lead. It needs model/provider verification, but is relevant because it sits at the image-plus-video frontier that sellers are discussing for ad creative.

Reusable methods added:

- `M209`: multi-angle product ad grid prompt workflow. Use a product reference plus structured six-slot prompt as a planning board, then regenerate or composite each slot separately with product/text/crop QA.
- `M210`: official preset product-photo tool evaluation workflow. Triangulate tools named by sellers with official pages, then run a same-SKU benchmark across Pikes, MagicShot, WizStudio, WaveSpeed, Eshot and Tagshop, measuring no-prompt UX, batch export, product lock, video/infographic support and marketplace readiness.

## Goal Continuation: Amazon JSON Experiments, Complex Product QA, ComfyUI Nodes And X Dataset

Sources added: `S786`-`S796`. Website cases added: `W505`-`W515`. Methods added: `M211`-`M214`.

- `S786` / `W505` records a high-signal AmazonFBA thread: raw phone product photo as truth, Brand Analytics/search intent, then a structured JSON spec for product invariants, Amazon slot rules, buyer question and forbidden inventions. This is a stronger pattern than ordinary prompt writing because it makes image testing measurable against CTR/CVR experiments.
- `S787` / `W506` records a fresh failure thread for $1000 sunglasses. The useful lesson is that consumer prompt/reference workflows still fail on tiny details such as screws, patterns, frame thickness and material. The recommended production route is multi-angle source data, optional product LoRA/adapters in ComfyUI and manual Photoshop finish.
- `S788` / `W507` records a GPT-Image-2 X/Twitter dataset paper. It is not ecommerce-specific, but it gives a defensible route for mining X-origin GPT Image 2 prompts and a strong provenance warning: C2PA credentials can disappear once social platforms re-host images.
- `S789`-`S793` / `W508`-`W512` expand the ComfyUI orchestration layer: official Nano Banana 2 partner-node docs, ru4ls custom nodes, gateway ComfyUI-Kie-API, a walkthrough with grid slicing/prompt JSON/preflight utilities and a 200-image provider comparison across Fal, WaveSpeed and Atlas. The operational signal is provider parameter exposure, especially `reference_image`, not just model name.
- `S794` / `W513` records the RunningHub resource URL linked from the indexed Bilibili layered-PSD workflow, separating the reusable workflow/online-experience link from the older Bilibili list row.
- `S795` / `W514` and `S796` / `W515` extend Russian WB/Ozon/Yandex coverage through a Nano Banana Pro API guide and a Telemetr-indexed Telegram/SyntxAI community lead.

Reusable methods added:

- `M211`: Amazon buyer-intent JSON image experiment workflow. Turn search intent and product invariants into a strict image spec, generate variants, then log experiment outcomes.
- `M212`: high-fidelity complex product consistency workflow. Use multi-angle product datasets, matching camera-angle references, ComfyUI/LoRA/adapters and manual finish when exact details matter.
- `M213`: ComfyUI partner/API node ecommerce orchestration workflow. Use ComfyUI graphs for Nano Banana 2/Pro, GPT Image 2, grid slicing, video preflight, provider comparison and cost/credit logging.
- `M214`: X/Twitter GPT Image 2 corpus mining and provenance workflow. Mine public prompt/image corpora for patterns, rewrite with SKU facts and preserve source/provenance/rights notes.

## Goal Continuation: Product Video Workflows, Tool Websites, Bilibili Clusters And Skill/CLI Frameworks

Sources added: `S797`-`S818`. Website cases added: `W516`-`W537`. Methods added: `M215`-`M218`.

- `S797`-`S799` / `W516`-`W518` record fresh Reddit product-video workflows where Nano Banana Pro or Nano Banana 2 creates a controlled first frame/product-placement image and Kling 2.6 animates it. The useful pattern is image model for product identity, video model for motion, then product-shape and ad-disclosure review.
- `S800`-`S804` / `W519`-`W523` add community/tool leads around EcomShot, Polymuse, Ecomtent and Ozor. EcomShot and Ecomtent are general ecommerce photo/video or marketplace-image tools; Polymuse is a stronger vertical case because furniture variants benefit from 3D/configurator truth rather than pure prompt generation.
- `S805` / `W524` adds a Bilibili search cluster for ComfyUI + Seedream/Kling/NanoBananaPro ecommerce detail-page and 15s promo-video workflows. This is still a capture queue: individual BV pages, resource links and subtitles need deeper extraction.
- `S806`-`S809` / `W525`-`W528` add small framework/open workflow evidence: smixs visual-skills for model-aware prompt routing, Higgsfield skills/CLI for agent/CLI execution, and EvoLink's GPT Image 2 + Seedance 2 product-image-to-video workflow.
- `S810`-`S818` / `W529`-`W537` expand the template-first product-photo benchmark set with Pixelshot, ShotPack, ShotPro, Prontoshoot, Flyshot, Somake, Product Scene, StagedAI and ProdShot. These are not proof of fidelity; they are benchmark candidates with concrete URLs and workflow claims.

Reusable methods added:

- `M215`: product image to social commerce video workflow. Generate a product-faithful first frame with Nano Banana Pro/2 or GPT Image 2, animate with Kling/Seedance, then QA product truth and ad policy.
- `M216`: vertical furniture and configurable-product visualization workflow. Prefer reusable 3D/product assets, configurators and catalog memory when variants, materials and dimensions matter.
- `M217`: agent skill and CLI packaged visual-production workflow. Package model routing, prompts, API calls and logs into reusable skills, CLIs or ComfyUI graphs.
- `M218`: template-first AI product photography tool benchmark workflow. Run the same SKU set across upload/template tools and measure export behavior, speed, image dimensions and product-fidelity drift.

## Goal Continuation: Multi-Model Creative Studios, Consistency Benchmarks And Ad Automation

Sources added: `S819`-`S837`. Website cases added: `W538`-`W556`. Methods added: `M219`-`M221`.

- `S819`, `S821`, `S823`, `S825` and `S827` / `W538`, `W540`, `W542`, `W544` and `W546` expand the current multi-model ecommerce studio pattern. These products increasingly package Nano Banana Pro for identity-preserving product imagery, GPT Image 2 for text-heavy listing/ad modules, and Kling/Seedance/Veo for animating approved stills.
- `S820`, `S824`, `S826`, `S828` and `S829` / `W539`, `W543`, `W545`, `W547` and `W548` add GPT Image 2/Nano Banana prompt and wrapper evidence: SKU-scale ecommerce playbooks, stable prompt structures, readable social-ad text, X/Twitter launch reaction summaries and exact-prompt galleries.
- `S830`-`S832` / `W549`-`W551` deepen the seller/community evidence around product truth. The strongest signal is not "which image looks best", but whether the tool preserves identity across source-photo, lifestyle and video steps. Threads mention Weavy + Nano Banana Pro, 50-tool consistency scores, Krea/ComfyUI masking, Photoroom and still-first animation with Kling/Veo.
- `S833`-`S835` / `W552`-`W554` add China-side workflow leads: a Bilibili ComfyUI commercial course covering ecommerce product cutout/background replacement and Nano Banana Pro/Seedream/Qwen modules, plus search clusters for Feishu+n8n ecommerce photoshoot pipelines and GPT Image2 relay/batch workflows.
- `S836`-`S837` / `W555`-`W556` add two open-source ad automation leads: an AI ad studio for product ad concepts/short-form vertical creatives, and a Figma display-ad variant generator that can act as a deterministic layout/export layer after AI image generation.

Reusable methods added:

- `M219`: multi-model ecommerce creative-studio routing workflow. Route identity, text, video and export jobs across Nano Banana Pro, GPT Image 2, Kling/Seedance/Veo and wrapper editing/upscale tools while logging model/version/cost.
- `M220`: community consistency benchmark and product-identity repair workflow. Convert anecdotal community tool rankings into controlled same-SKU tests, then use masks/reference locking/compositing when product identity drifts.
- `M221`: deterministic ad-template expansion after AI image generation. Generate or composite the product visual once, then vary copy, CTA and sizes through Figma/template automation rather than re-rendering the product.

## Goal Continuation: n8n Automation Templates, Russian Marketplace Rules And Edit-Degradation QA

Sources added: `S838`-`S853`. Website cases added: `W557`-`W572`. Methods added: `M222`-`M224`.

- `S838`-`S847` / `W557`-`W566` add n8n official workflow templates. These are high-value because they encode real pipeline shape: product image or URL intake, product analysis, script/persona/ad concept generation, image/video generation, Google Drive/Sheets storage, Telegram input, Blotato publishing and batch loops.
- `S845` / `W564` is especially direct for batch image generation: one product image in Google Drive triggers 50 UGC prompts and 50 Nano Banana/Fal.ai generations saved back to Drive.
- `S839` / `W558` and `S843` / `W562` are strong static-image automation references: product page plus logo/image to ecommerce ad, and multiple reference images to scalable NanoBanana Pro product photos.
- `S846` / `W565` shows the broader idea-to-images-to-video-to-auto-publish pattern across NanoBanana, Seedream, ChatGPT Image, Veo 3 and Blotato. This needs an approval gate before real ad publishing.
- `S848`-`S851` / `W567`-`W570` expand Russian marketplace compliance and slot routing. Pixyn splits main photo, lifestyle photo and infographic work by model; SellerArt provides dimensions/rule references; APIYI adds a GPT Image 2 method for compressing long product descriptions into short visual copy.
- `S852` / `W571` and `S853` / `W572` add QA risk evidence: a product-retouching PDF shows Nano Banana Pro can distort labels/logos/icons during retouching, and Banana100 shows multi-turn edit quality degradation can escape automated quality metrics.

Reusable methods added:

- `M222`: n8n ecommerce product media automation workflow. Treat product media generation as an explicit graph with intake, product analysis, prompt/script generation, image/video creation, storage, metadata logging and approval before publishing.
- `M223`: Russian marketplace AI card slot and compliance routing workflow. Route main photos, lifestyle photos and infographics to different models/tools, then validate dimensions, crop, text and product truth against WB/Ozon/Yandex rules.
- `M224`: multi-turn product image edit degradation and retouch QA workflow. Cap edit chains, save intermediates, compare labels/logos/materials to source and use OCR/human review when exact product details matter.

## Goal Continuation: Nano Banana 2 Seller Guides, Bilibili Coze Clusters And Localization Workflows

Sources added: `S854`-`S876`. Website cases added: `W573`-`W595`. Methods added: `M225`-`M228`.

- `S854`-`S858`, `S863`, `S864` and `S866` / `W573`-`W577`, `W582`, `W583` and `W585` expand the current Nano Banana 2 / GPT Image 2 routing evidence. The useful operational split is speed/cost/API batch for high-volume secondary images and campaign variants, with Pro or GPT Image 2 reserved for more valuable hero, text-heavy or brand-controlled slots.
- `S859`, `S869` and `S870` / `W578`, `W588` and `W589` add seller-community signals around Amazon image realism, A+ localization and small-business product-photo tool cost. The recurring pain point is not only generation quality, but editable localization, buyer trust and repeat SKU processing.
- `S860` and `S861` / `W579` and `W580` add HN evidence from both sides: Nano Banana AdKit as a small one-click preset framework for ads/product photos, and a negative report that one-photo multi-angle product views can fail. That reinforces the need for multi-view source assets before claiming catalog-truth coverage.
- `S862` / `W581` adds a brand workflow where Claude is used as art director/prompt compiler and GPT Image 2 generates the product photography. This is useful as a method pattern, but labels and claims still need OCR and human review.
- `S865`, `S867` and `S868` / `W584`, `W586` and `W587` add Russian prompt guidance and research evidence for retouching/restoration roles. These are relevant to cleanup/background/product-photo workflows, but should not be treated as marketplace compliance proof.
- `S871`-`S876` / `W590`-`W595` add a new Bilibili capture queue: Coze + Nano Banana 2 one-click ecommerce main images, detail pages, product/model fusion, hit-main-image reverse engineering, Prodfill/Figma batch production, Ozon examples and GPT Image 2 domestic access/tutorial leads. These rows are search clusters and should be followed by individual BV/subtitle/resource capture.

Reusable methods added:

- `M225`: Nano Banana 2 catalog-speed routing workflow. Use Nano Banana 2 for speed/cost-sensitive catalog and social variants, reserve Pro/GPT Image 2 for stricter hero/text-heavy slots, and log source photo/model/version/cost.
- `M226`: LLM art-director plus image-model brand product workflow. Convert product facts and brand direction into structured prompts with Claude/GPT, generate with GPT Image 2 or Nano Banana Pro, then OCR and compare against source.
- `M227`: Chinese Coze and Bilibili ecommerce workflow capture pipeline. Treat search clusters as discovery queues, capture individual videos/resource links, and normalize Coze/Feishu/Figma/RunningHub workflows into runnable recipes.
- `M228`: product-image localization and editable-text overlay workflow. Keep product pixels stable while moving localized copy into editable design/template layers; use image translation only as a draft and proofread with OCR/native review.

## Goal Continuation: n8n Evidence, LangGraph Alternatives, Editable Layers And Photoshop QA

Sources added: `S877`-`S897`. Website cases added: `W596`-`W616`. Methods added: `M229`-`M232`.

- `S877`-`S883` / `W596`-`W602` add fresh n8n workflow evidence around the exact disputed point: Jotform/Sheets intake, Google Drive output, status logging, rate-limit waits, human Telegram approval and community claims of 50-100 weekly variants or 500+ daily product images. The evidence supports n8n as an orchestration shell, not as a guarantee of image quality.
- `S884` / `W603` adds an open-source n8n workflow repository with Nano Banana ad creative, competitor-ad reskinning and static A/B variation JSON workflows. This is useful because it gives importable workflow shapes beyond vendor landing pages.
- `S885`-`S887` / `W604`-`W606` answer the n8n-alternative question: LangGraph/MCP and interrupt templates can implement prompt approval, checkpointed human review, over-generation, vision pair selection and retry fallback. This makes n8n optional; it is a fast validation tool rather than the only valid architecture.
- `S888`-`S892`, `S894` and `S895` / `W607`-`W611`, `W613` and `W614` add editable-layer and deterministic-design evidence. Mujo, Autophoto, Clipzest and AuraFx all point toward layered or workspace-based ecommerce production rather than flat JPG-only output; the GPT Image 2 + Figma community thread says GPT Image 2 is useful for visual direction while Figma remains the finished editable file.
- `S893`, `S896` and `S897` / `W612`, `W615` and `W616` add Photoshop/ComfyUI evidence. Photoshop Generative Fill official docs confirm non-destructive generative layers; community threads show Nano Banana/FLUX model picker and Photoshop + ComfyUI + Nano Banana Pro reference-image workflows, supporting the精铺 repair path.

Reusable methods added:

- `M229`: low-code ecommerce product-photo request and approval workflow. Use n8n/Sheets/Drive/forms as an operations shell and keep QA/approval as first-class statuses.
- `M230`: code-first graph alternative to n8n for image QA and human review. Use LangGraph/MCP for checkpointed state, over-generation, candidate selection, retries and human review.
- `M231`: editable-layer ecommerce creative production workflow. Use image models for visual direction/backgrounds, then final text/badges/layout/export in editable layers.
- `M232`: Photoshop and ComfyUI human-retouch hybrid workflow. Use masks, non-destructive generative layers and reference-image workflows for product-label/background/contact-shadow repair rather than whole-image rerendering.

## Goal Continuation: Platform Rules, Native AI Creative, Prompt-Free Studios And Product Video

Sources added: `S898`-`S918`. Website cases added: `W617`-`W637`. Methods added: `M233`-`M236`.

- `S898` and `S899` / `W617` and `W618` add Amazon-native AI creative evidence. Amazon Ads itself now frames product-to-lifestyle image generation as a campaign/brand-store workflow, which supports the idea that AI imagery is real in the ad stack. It does not prove Seller Central main-image compliance.
- `S900`, `S905`-`S908` / `W619`, `W624`-`W627` add Amazon compliance and seller discussion signals. The stable pattern is main image = stricter real/compliant product clarity, secondary/A+/ads = more room for AI lifestyle, but all surfaces still need non-misleading scale, color, function and claim checks.
- `S901`-`S903` and `S909` / `W620`-`W622` and `W628` add Russian platform-native evidence. Wildberries official docs provide photo rules and virtual fitting; Ozon's ML copyright check makes source photos and layered editor files operational proof, not optional archival hygiene.
- `S904` / `W623` adds AI-generated-image detection risk context. This does not solve product fidelity, but it matters for provenance and disclosure planning as marketplaces get better at detecting generated assets.
- `S910`-`S913` / `W629`-`W632` add prompt-free/control-panel product studio signals. These are candidates for a same-SKU benchmark because they sell a different operator model: camera/pose/lighting/background controls instead of only text prompts.
- `S914`-`S917` / `W633`-`W636` deepen the n8n product-video route: Nano Banana setup tutorials, Telegram product-video creation with Veo 3.1, fashion campaign batch automation and clean studio photo + 360 video threads.
- `S918` / `W637` records broader product-photography industry adoption discussion around Aldi/large-company AI use. The useful point is not that AI is automatically acceptable, but that human-checked inpainting and cost-reduction workflows are already part of the photography conversation.

Reusable methods added:

- `M233`: marketplace-native AI creative and compliance split workflow. Separate Amazon main-image compliance from Amazon Ads/Brand Store lifestyle generation.
- `M234`: WB/Ozon provenance and native-tool QA workflow. Preserve original photos, layered editor files and rights proof while validating against official marketplace rules.
- `M235`: prompt-free product studio benchmark workflow. Compare control-panel tools against prompt workflows with the same SKU set and export/layer QA.
- `M236`: image-to-video product automation with first-frame QA. Approve product-faithful stills first, then animate and sample key frames for drift.

## Goal Continuation: Workflow Indexes, Bilibili PS/Coze Capture And Editable-Asset Conversion

Sources added: `S919`-`S931`. Website cases added: `W638`-`W650`. Methods added: `M237`-`M239`.

- `S919`-`S923` / `W638`-`W642` add workflow-index and creator evidence. These sources do not all provide direct runnable artifacts, but they identify repeatable patterns to capture: Nano Banana product creative via Defapi, infinite UGC ads with n8n/Veo/Nano Banana, product URL to Meta ads, Shopify product videos and Nano Banana Pro infographics.
- `S924`-`S927` / `W643`-`W646` extend the Bilibili capture queue beyond generic search: PS AI plugin with ComfyUI/model calling, Coze + Nano Banana 2 ecommerce main/detail workflows, free AI product-main-image comparisons and ecommerce template/source-file clusters. These should be converted into exact BV/resource captures before production claims.
- `S928` and `S930` / `W647` and `W649` add a clearer answer to the editable-output problem: GPT Image 2 can make strong flat visuals, but communities still discuss OCR, text removal, SVG/PPTX/Figma reconstruction and manual domain review because flat PNG outputs are not production files.
- `S929` / `W648` adds another photography-community signal for the hybrid route: generate scenes or use AI for bulk marketing backgrounds, then composite the real product in Photoshop. This aligns with the product-body preservation constraint.
- `S931` / `W650` adds a platform-formatting product photo editor lead that explicitly mentions background removal, color correction, lighting optimization and platform-specific output for Amazon/Shopify/Etsy/social channels.

Reusable methods added:

- `M237`: workflow-index capture and importability audit. Treat n8n creator/template pages as discovery leads, then capture JSON/node lists and test importability before relying on them.
- `M238`: Chinese video workflow to executable recipe pipeline. Convert Bilibili PS/Coze/ComfyUI/RunningHub tutorials into normalized inputs-nodes-outputs-QA recipes.
- `M239`: flat AI output to editable production asset workflow. Use OCR/text removal/vector/PPTX/Figma reconstruction when GPT Image 2 produces useful visuals but not editable deliverables.
