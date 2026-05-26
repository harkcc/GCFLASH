# Premium Ecommerce Banner Reference Teardown

Date: 2026-05-24

Scope: `/Users/cc/Desktop/banner`

## What The Folder Contains

The folder is not a clean production asset library. It contains three kinds of references:

- Single wide ecommerce banners that can be analyzed as one pattern.
- Tall tutorial/collection images that contain 2-4 different banner patterns in one file.
- Prompt-explanation screenshots where the lower half is design analysis, not a reusable visual module.

This means the Agent must first classify each file into `single_banner`, `multi_banner_collection`, or `prompt_reference_page`. Do not feed the whole tall image into a generation model as one template.

## Files And Pattern Labels

| File | Size | Type | Extractable pattern |
| --- | ---: | --- | --- |
| `img_v3_02120_03c1cecd-37c4-4b47-bb6f-03da1e34157g.jpg` | 1440x720 | single banner | clean light-blue promo, centered product, discount text left, sparse layout |
| `img_v3_02120_04459b8e-8d34-4ffb-94c3-697b33c9934g.jpg` | 1080x1440 | prompt reference page | industrial black/orange brick wall, neon headline, product cluster right |
| `img_v3_02120_0d0ca852-97a3-416f-8382-91aa74a1d7cg.jpg` | 1156x2510 | page screenshot | mobile product detail page reference, not a banner template |
| `img_v3_02120_18547bf3-9b1a-436f-88a6-6a803ec1289g.jpg` | 1080x1443 | multi banner collection | blue corporate/industrial three-banner layout |
| `img_v3_02120_1e6cf67f-cb1d-4415-8525-5b9f3816aceg.jpg` | 1080x1440 | prompt reference page | dark blue furniture/office brand proof, calm professional tone |
| `img_v3_02120_369bd3e6-bcb5-4ff3-8a69-93bab67c037g.jpg` | 1180x1480 | multi banner collection | light cream phone/product sale; product group left/right with generous whitespace |
| `img_v3_02120_40da3afb-e345-456d-9ead-e7eee20621ag.jpg` | 1080x1440 | prompt reference page | sunset outdoor product group, scenic energy, product in realistic environment |
| `img_v3_02120_4f625c8b-6461-46b6-a045-600f84960b0g.jpg` | 1080x1440 | prompt reference page | black Friday dense product strip, black/orange, discount-driven |
| `img_v3_02120_51a609ff-e007-4513-a825-b71f771912eg.jpg` | 1080x1444 | multi banner collection | effect display examples, likely multiple before/after ad boards |
| `img_v3_02120_5cac50f6-f295-40f4-98b6-5f2764bcbddg.jpg` | 1440x626 | single banner | cinematic seasonal landscape, product anchored in scene, light trail motion cue |
| `img_v3_02120_7920bdf8-70ad-4379-b4c2-e69d730fba0g.jpg` | 1080x1440 | multi banner collection | casino/game promo; not suitable as product-detail style except color/energy study |
| `img_v3_02120_86b6e5e9-66a8-4e56-8504-0ba68049a34g.jpg` | 1200x600 | single banner | green seasonal outdoor product scene, bright air, product cluster right |
| `img_v3_02120_86e9c5a3-a999-4fd0-ad22-bb34544737bg-1.jpg` | 1440x684 | single banner | lawn/home product scene, clean product grouping, left text, right lifestyle setting |
| `img_v3_02120_86e9c5a3-a999-4fd0-ad22-bb34544737bg.jpg` | 1440x684 | single banner | duplicate/sibling of previous |
| `img_v3_02120_8765ee8f-75a8-4e47-8e08-ca536a39719g.jpg` | 1440x566 | single banner | red city/night energy, product group foreground, promotional event tone |
| `img_v3_02120_8ae636f1-d9b8-4597-a1ac-7275017d161g.jpg` | 1080x1444 | text reference | written banner prompt notes, not visual template |
| `img_v3_02120_9cdb5a70-f0a9-48b1-97cc-9d491b9e028g.jpg` | 1080x1440 | prompt reference page | black Friday clean-tech product, dark blue neon, product cluster center |
| `img_v3_02120_9e5f3200-ffb3-4755-9315-870ba360f1bg.jpg` | 1440x684 | single banner | green outdoor earbuds/tech scene, product floating in nature |
| `img_v3_02120_adb52645-701b-4e7b-b465-00b3d6485e8g.jpg` | 1080x1440 | multi banner collection | dense gaming/casino promotional boards; only extract motion/color ideas |
| `img_v3_02120_b2f36d61-b423-4b88-8f55-65307cbcf43g.jpg` | 1080x1440 | prompt reference page | electric Friday home appliance, black/gold product island |
| `img_v3_02120_cac259a2-c92d-41e2-944f-b90d7377d22g.jpg` | 1080x1443 | multi banner collection | leather/accessory manufacturer trust, white card over real factory/product photos |
| `img_v3_02120_cbfbfb5c-7153-415c-9f5f-19dda150caeg.jpg` | 1080x1443 | multi banner collection | corporate blue monitor/tech banners, strong proof panels |
| `img_v3_02120_d6d9bef2-87ce-4327-b5e9-23a0a509f86g.jpg` | 1080x1444 | multi banner collection | effect display examples, headset/product detail boards |
| `img_v3_02120_d79c3944-2615-44b4-8417-a89b9bf60e0g.jpg` | 1080x1350 | multi banner collection | travel/outdoor product scenes, scenic full-width strips |
| `img_v3_02120_dbe7941b-feb6-4250-9d96-c02fbed0c20g.jpg` | 1080x1443 | multi banner collection | industrial blue/white B2B banners, product + factory/photo proof |
| `img_v3_02120_ece06f24-1825-469b-bc29-3c981fd9852g.jpg` | 1080x1443 | multi banner collection | outdoor/industrial blue-green banner set, service/process proof |
| `img_v3_02120_ef02004b-81a6-45a1-a72e-cce5996ae2ag.jpg` | 1080x1440 | prompt reference page | black Friday blue suitcase/audio product, neon product frame |

## Reusable Design Patterns

### 1. Product Scene Hero

Use for first banner when the product has a clear usage context.

Pattern:

- Realistic or AI-generated scene fills the full width.
- Product sits inside the scene, not on top of a generic card.
- Text occupies one clean safe zone, usually left or centered top.
- One CTA/badge maximum; eMAG detail pages can omit CTA.
- Strong depth: foreground product, midground surface, background environment.

Best categories: EV, outdoor, home appliance, kitchen, tools.

### 2. Industrial Premium Dark

Use when the product benefits from technical confidence.

Pattern:

- Black/dark wall, workshop, or tech environment.
- Warm neon/rim light creates one attention line.
- Product cluster on the right or center-right.
- Headline is large, but supporting text is very short.
- Texture does the premium work; avoid adding many boxes.

Best categories: EV, electronics, tools, audio.

### 3. Clean Cream Product Sale

Use when the product is lifestyle, baby, beauty, or consumer electronics.

Pattern:

- Cream/off-white background.
- Product cluster uses soft shadows and light decorative arcs.
- Text block is black, clean, and small.
- Product color provides the accent.
- Lots of whitespace; no heavy frame.

Best categories: baby, beauty, kitchen, lightweight electronics.

### 4. Manufacturer Trust Strip

Use for brand/seller proof, not normal product features.

Pattern:

- Real factory/workshop/design-process image as background.
- White or translucent foreground panel.
- 3-4 numeric proof chips only when evidence exists.
- Certifications/logos only when real.
- Keep it as one proof banner, not repeated across the page.

Best categories: B2B, tools, OEM, specialized electronics.

### 5. Scenic Energy Motion Cue

Use when stable GIF is desired.

Pattern:

- Scene is static.
- A light trail, shine sweep, or glow line passes across the composition.
- Product does not deform or move.
- Text remains deterministic and static.

Best stable motion: black-gold shine sweep, light trail shimmer, subtle product highlight.

## What To Change In Our Current eMAG Output

- Do not stack a dark review banner and a dark brand banner back-to-back. Pick one heavy dark module per page segment.
- Do not add small boxes by default. Use them only for specs, manual steps, comparison, or three first-screen anchors.
- Do not place a second large product image immediately below an already image-heavy banner unless it answers a different buyer question.
- Crop source product images into proof details instead of inserting full screenshots repeatedly.
- Mix rhythm: `wide image -> short white text -> cropped proof -> clean specs -> QA -> one social/brand proof`.
- Use white background modules intentionally. Premium is often whitespace + hierarchy, not always black/gold.

## Reference Links Used For Current Strategy

- Google Vertex AI Imagen API docs: https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/imagen-api
- Google image generation docs: https://cloud.google.com/vertex-ai/generative-ai/docs/image/generate-images
- OpenAI image generation guide: https://platform.openai.com/docs/guides/image-generation
- fal.ai model docs: https://fal.ai/models
- Nielsen Norman Group ecommerce UX articles: https://www.nngroup.com/topic/ecommerce/
- Baymard product page UX research: https://baymard.com/research/product-pages

