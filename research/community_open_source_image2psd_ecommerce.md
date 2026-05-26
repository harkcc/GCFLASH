# AI ecommerce image generation community and open-source research

Date: 2026-05-04

## Executive summary

The most credible direction is not another large workflow framework. The pattern that repeats across open-source projects, Reddit cases, and commercial tools is:

1. Start with a real product photo or clean product cutout.
2. Preserve product identity aggressively: shape, proportions, material, logo, labels, ports, and packaging text.
3. Use image-to-image or reference-image generation for scene/background/style.
4. Use a fixed template or design-system file to control layout, color, safe areas, typography, and repeated brand cues.
5. Export editable deliverables through PSD or layered PNG, even if the AI-generated visual itself is raster.
6. Score and repair in short loops instead of expecting one perfect generation.

For this project, the highest-leverage stack is:

Product truth pack -> DesignMD/TemplateSpec -> prompt compiler -> Nano Banana 2 / GPT Image 2 edit -> PSD manifest assembly with bggg-creator-image2psd -> preview scoring -> human review notes -> repair prompt.

The important point: PSD should be the template and delivery layer, not the generation model. The model produces high-quality raster assets; PSD keeps control, repeatability, and editability.

## Source map

### Open-source and skill projects

| Source | Type | What it does | Useful for us | Limitation |
| --- | --- | --- | --- | --- |
| [binggandata/bggg-skills: bggg-creator-image2psd](https://github.com/binggandata/bggg-skills/tree/main/bggg-creator-image2psd) | Codex skill / PSD writer | Assembles images and raster text into layered PSD, preview PNG, and full-canvas layer PNGs. | Strong base for PSD manifest, template slots, editable handoff. | Raster layers only; text is not editable Photoshop text; no smart objects or layer styles. |
| [kingbootoshi/nano-banana-2-skill](https://github.com/kingbootoshi/nano-banana-2-skill) | CLI / Claude skill | Nano Banana image generation with reference images, size, aspect ratio, transparent mode. | Good reference for agent-executable image generation, reference image routing, transparent asset creation. | Built around Gemini/Nano Banana CLI, not ecommerce-specific scoring. |
| [jau123/MeiGen-AI-Design-MCP](https://github.com/jau123/MeiGen-AI-Design-MCP) | MCP / prompt gallery / generation bridge | Multi-model image/video generation, prompt enhancement, gallery, GPT Image 2 and Nano Banana support. | Useful model-routing and prompt-gallery pattern. | Hosted credits/API dependency; not a PSD/template engine. |
| [jau123/nanobanana-trending-prompts](https://github.com/jau123/nanobanana-trending-prompts) | Prompt dataset | Curated trending prompts from X/Twitter for NanoBanana/GPT Image/Midjourney. | Good source for prompt structure mining and style vocabulary. | Viral prompts are not ecommerce-SKU-safe by default. Need product fidelity filters. |
| [ZeroLu/awesome-gpt-image](https://github.com/ZeroLu/awesome-gpt-image) | Prompt collection | Viral GPT image prompt examples. | Useful for layout, typography, poster, product-marketing prompt patterns. | Needs curation; many examples optimize visual novelty, not SKU accuracy. |
| [MiddleKD/ComfyUI-productfix](https://github.com/MiddleKD/ComfyUI-productfix) | ComfyUI custom node | Preserves text, logos, and product details using latent injection. | Directly targets the hardest ecommerce problem: product identity preservation. | ComfyUI setup and model workflow complexity. |
| [Bria-AI/ComfyUI-BRIA-API](https://github.com/Bria-AI/ComfyUI-BRIA-API) | ComfyUI API nodes | Product shot editing nodes such as ShotByText and ShotByImage. | Good pattern for product background replacement with API-backed nodes. | BRIA API token and commercial model dependency. |
| [shitagaki-lab/see-through](https://github.com/shitagaki-lab/see-through) | Image-to-PSD layer decomposition | Decomposes anime images into semantic PSD layers. | Useful as prior art for layer output and PSD decomposition. | Domain is anime characters, not product listings. |
| [jtydhr88/ComfyUI-See-through](https://github.com/jtydhr88/ComfyUI-See-through) | ComfyUI wrapper | Browser PSD export with ag-psd, depth layers, layer preview. | Useful implementation idea: PNG layers + metadata + browser-side PSD generation. | Same anime-domain limitation. |
| [ag-psd](https://github.com/Agamnentzar/ag-psd) | JS PSD library | Read/write PSD in JavaScript. | Useful if we build a web UI or browser PSD exporter. | PSD feature coverage is partial. |
| [psd-tools](https://github.com/psd-tools/psd-tools) | Python PSD library | Reads/writes/exports PSD data. | Useful for validation and layer inspection. | Editing type layers/smart objects is limited. |
| [Open Design](https://opendesigner.io/) / [nexu-io/open-design](https://github.com/nexu-io/open-design) | AI design environment | Local-first design artifacts, skills, design systems, preview/export loop. | Use its architecture: design systems + artifacts + preview + self-critique. | It is general design tooling, not ecommerce image generation. |
| [Google DESIGN.md ecosystem](https://designmd.app/en/what-is-design-md) and [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) | Design-system files | Markdown design systems with tokens, typography, spacing, anti-patterns. | Strong fit for brand/style control in image prompt and PSD template generation. | Most examples target UI, so ecommerce visual rules must be custom-authored. |

### Model/API references

| Source | What matters |
| --- | --- |
| [fal Nano Banana 2 API](https://fal.ai/docs/model-api-reference/image-generation-api/nano-banana-2) | Exposes Nano Banana 2 edit endpoint; suitable for image-to-image experiments. |
| [OpenAI GPT Image 2 model docs](https://developers.openai.com/api/docs/models/gpt-image-2) | GPT Image 2 is positioned for high-quality generation and editing. |
| [OpenAI image generation guide](https://platform.openai.com/docs/guides/image-generation) | Confirms generation/editing flow and image API constraints. |
| [fal GPT Image 2 prompting guide](https://fal.ai/learn/tools/prompting-gpt-image-2) | Useful product-photography prompting examples and fal edit endpoint references. |
| [fal GPT Image 2 playground](https://fal.ai/models/openai/gpt-image-2/playground) | Mentions ecommerce uses like product photography variations and background replacement. |

### Community evidence

| Source | Repeated lesson |
| --- | --- |
| [Reddit: tried AI for product photos](https://www.reddit.com/r/ecommerce/comments/1jox56d/tried_ai_for_product_photosheres_what_worked_and/) | Hybrid workflow: real hero/product truth, AI for variations and updates. |
| [Reddit: product image consistency](https://www.reddit.com/r/EcommerceWebsite/comments/1s36vkn/we_tried_solving_product_image_consistency_for/) | Consistency across catalog is a workflow problem, not just an image-quality problem. |
| [Reddit: one product photo into 5-10 variations](https://www.reddit.com/r/ecommerce/comments/1rru8mv/how_are_people_making_product_photos_look_so/) | Real product photo + AI backgrounds + consistent crop/shadow can work at low cost. |
| [Reddit: AI product photos setup](https://www.reddit.com/r/ecommerce/comments/1qtmu82/whats_your_setup_for_product_images/) | Users still value color/proportion accuracy and warn against strange AI distortions. |
| [Reddit: AI product photography conversion workflow](https://www.reddit.com/r/ecommercemarketing/comments/1qvkxng/how_to_create_ai_product_photography_that/) | Decide each image's job before choosing scene; avoid treating every image as a hero shot. |
| [Reddit: product detail preservation](https://www.reddit.com/r/comfyui/comments/1mcsxoc/testing_the_limits_of_ai_product_photography/) | Complex products still break; vetted source assets and detail-retention methods matter. |
| [Reddit: GPT Image 2 on fal](https://www.reddit.com/r/fal/comments/1srxfj4/gpt_image_2_is_live_on_fal/) | Community expects GPT Image 2 to improve product labels, logos, and packaging fidelity. |
| [Reddit: Open-source prompt dataset](https://www.reddit.com/r/comfyui/comments/1sypezt/open_source_1446_trending_ai_image_prompts_for/) | Prompt mining and prompt recommendation are becoming reusable assets. |

### Commercial tools worth copying, not rebuilding blindly

| Source | Mechanism to copy |
| --- | --- |
| [Pebblely](https://www.pebblely.com/) | One product image -> multiple marketing assets; templates; bulk generation. |
| [Pebblely reference image workflow](https://www.pebblely.com/blog/reference-image/) | Reference image strongly changes output while product remains central. |
| [Claid AI Background API](https://claid.ai/api-products/generate-background/) | API exposes product position/size/angle control plus templates. This maps directly to PSD slot fields. |
| [Claid scene options](https://docs.claid.ai/ai-background-api/ai-background-options/scene) | Template viewpoint should match product viewpoint; shadows are a distinct generation mode. |
| [Pixelcut Background Generation API](https://www.pixelcut.ai/api/background-generator) | Product-context-aware backgrounds, perspective matching, production-ready batch generation. |
| [Photoroom API docs](https://docs.photoroom.com/) | Reliable background removal/editing API; practical for preprocessing and bulk catalog cleanup. |
| [Photoroom OpenAPI](https://docs.photoroom.com/api-reference-openapi) | Shows simple image edit params: removeBackground, background color, output size, padding. |

## Methods found

### Method 1: True product photo + generated background

Input:
- Real product photo or cutout.
- Prompted background or reference background.

Output:
- Lifestyle scene or studio shot.

Best sources:
- Pixelcut, Claid, Pebblely, Photoroom, Reddit ecommerce threads.

Why it works:
- The product truth stays anchored.
- AI creates the expensive part: environment, props, light, seasonal variation.

Risk:
- Product geometry drift if the model is allowed to redraw the product.

Project use:
- Primary path for hero, scene, and campaign images.

### Method 2: Template-first image-to-image

Input:
- Product image.
- Reference image or template mock.
- DesignMD/TemplateSpec with layout, palette, safe area, text zones.

Output:
- Image that follows a known layout.

Best sources:
- Open Design, DESIGN.md, bggg-creator-image2psd, Claid template controls.

Why it works:
- Reduces randomness.
- Lets us reuse high-performing competitor structures without copying exact visuals.

Risk:
- If the model renders text directly, typos and layout errors remain likely.

Project use:
- Best default for selling-point and detail cards.

### Method 3: Generate visual asset, then PSD落版

Input:
- Background render.
- Product cutout.
- Text content.
- Brand frame.

Output:
- PSD with separate layers and preview PNG.

Best sources:
- bggg-creator-image2psd, ag-psd, psd-tools, OpenDesign artifact loop.

Why it works:
- Keeps final deliverable editable.
- Lets AI do image work while scripts do deterministic layout.

Risk:
- PSD is raster-only unless we invest in Photoshop-specific text/smart-object automation.

Project use:
- Very high priority. This is the shortest path to usable deliverables.

### Method 4: Prompt library + prompt compiler

Input:
- User brief, SKU truth pack, selected image slot.
- Prompt patterns mined from Nano Banana/GPT Image prompt libraries.

Output:
- Model-specific prompt, negative constraints, repair prompt.

Best sources:
- jau123/nanobanana-trending-prompts, ZeroLu/awesome-gpt-image, Promptor, Nano Banana ecommerce prompt libraries.

Why it works:
- Good prompts are structured, not long random descriptions.
- The prompt can be generated repeatedly from the same product truth.

Risk:
- Viral prompt libraries over-index on novelty and stylization.

Project use:
- High priority, but every prompt must include product fidelity rules.

### Method 5: ComfyUI specialist pipeline

Input:
- Product photo, masks, depth/canny/reference.
- Nodes for matting, relight, detail preservation, upscale.

Output:
- More controlled product scene fusion.

Best sources:
- ComfyUI-productfix, BRIA nodes, IC-Light workflows, Qwen Image Edit product workflows.

Why it works:
- Gives finer control over masks, lighting, and reference preservation.

Risk:
- Complexity returns quickly. Harder to maintain than API/image2image flow.

Project use:
- Keep as fallback for difficult SKUs, not first MVP path.

### Method 6: Catalog consistency layer

Input:
- Batch of SKU truth packs.
- Shared brand style, crop, background, shadow, padding.

Output:
- A catalog that feels like one brand.

Best sources:
- Reddit consistency discussions, Pebblely bulk generation, Photoroom/Claid/Pixelcut APIs.

Why it works:
- Many sellers care more about consistent trust signals than one spectacular image.

Risk:
- Over-templating can make images generic.

Project use:
- Important for phase 2 after single-SKU MVP works.

## What to copy from Open Design / DesignMD

Open Design's useful idea is not its UI. The reusable mechanism is:

1. Store taste and constraints as files, not vague chat memory.
2. Separate design system from task prompt.
3. Render artifacts and preview them.
4. Self-critique before final handoff.
5. Keep skills small and composable.

For ecommerce images, this becomes:

- `DESIGN.md`: brand style, colors, typography, border/frame style, forbidden patterns.
- `template_specs/*.json`: image slots, text zones, product slot, shadow rules, output ratio.
- `prompt_recipes/*.md`: hero, selling-point, lifestyle, detail, comparison, package.
- `runs/<sku>/truth_pack.json`: SKU facts and immutable product traits.
- `runs/<sku>/reviews.jsonl`: auto and human review feedback.

## Recommended MVP flow

### Inputs

- Product source image.
- Optional competitor/reference images.
- Brand style image or existing frame.
- Product facts and selling points.

### Step 1: Truth pack

Create:

```json
{
  "sku": "example",
  "category": "gaming controller",
  "immutable_traits": [
    "exact shape",
    "black shell",
    "blue LED ring",
    "button layout",
    "logo position"
  ],
  "allowed_changes": [
    "background",
    "lighting",
    "surface",
    "props",
    "camera framing"
  ],
  "forbidden_changes": [
    "new buttons",
    "wrong logo",
    "changed color",
    "extra accessories",
    "fake text"
  ]
}
```

### Step 2: TemplateSpec

Create one template per image type:

```json
{
  "template_id": "selling_point_right_text_v1",
  "canvas": { "width": 1200, "height": 1600 },
  "product_slot": { "x": 120, "y": 330, "width": 620, "height": 720, "fit": "contain", "scale": 0.95 },
  "text_zones": [
    { "id": "headline", "x": 760, "y": 220, "width": 360, "height": 160 },
    { "id": "bullets", "x": 760, "y": 430, "width": 360, "height": 520 }
  ],
  "background": "premium clean gradient or realistic studio surface",
  "shadow": "soft contact shadow under product",
  "brand_frame": "door-frame style border, restrained, not decorative clutter"
}
```

### Step 3: Prompt compile

Generate prompt with:

- Source-of-truth product lock.
- Image job.
- Slot/layout requirement.
- Background/style.
- Text-space reservation.
- Negative constraints.

### Step 4: Image generation/edit

Use:

- Nano Banana 2 / Pro for fast product scene and prompt-following tests.
- GPT Image 2 for label/text-sensitive product renders and higher-fidelity editing.
- Keep every generation trace: model, endpoint, prompt, refs, output path.

### Step 5: PSD assembly

Use bggg-creator-image2psd with a manifest. Extend manifest to support slot/bbox scale:

```json
{
  "canvas": { "width": 1200, "height": 1600, "composite_background": "#ffffff" },
  "output": "output.psd",
  "preview": "output.preview.png",
  "save_layers_dir": "psd_full_canvas_layers",
  "layers": [
    { "name": "Background", "file": "layer_sources/background.png", "fit": "cover", "remove_background": "none" },
    { "name": "Product", "file": "layer_sources/product_cutout.png", "slot": { "x": 120, "y": 330, "width": 620, "height": 720 }, "fit": "contain", "scale": 0.95, "remove_background": "white-preserve" },
    { "name": "Headline", "type": "text", "text": "Fast Wireless Play", "x": 760, "y": 220, "font_size": 64, "color": "#101820", "max_width": 360 },
    { "name": "Brand Frame", "file": "layer_sources/brand_frame.png", "fit": "cover", "opacity": 1 }
  ]
}
```

### Step 6: Score and repair

Score:

- Product fidelity: 0-10
- Commercial polish: 0-10
- Brand consistency: 0-10
- Template compliance: 0-10
- Text/layout safety: 0-10
- Platform suitability: 0-10

Repair prompt should be short and targeted:

```text
Keep the exact same product and composition. Repair only these issues:
1. Product is too small; enlarge it by 12%.
2. Shadow is too harsh; make a softer contact shadow.
3. Right text area is too busy; clean the background behind it.
Do not change the product shape, logo, color, button layout, or camera angle.
```

## Priority recommendation

### P0: Do now

1. Adopt bggg-creator-image2psd as PSD output foundation.
2. Add slot/bbox scale support to its manifest logic.
3. Create `DESIGN.md` for the brand style.
4. Create 4 template specs: hero, selling point, lifestyle, detail.
5. Run one SKU through Nano Banana 2 and GPT Image 2 with the same prompt and refs.

### P1: After first SKU

1. Build prompt compiler from truth pack + template.
2. Add automatic score JSON and human review JSONL.
3. Add repair-loop prompts.
4. Save all model calls and images as a reproducible run folder.

### P2: Later

1. ComfyUI fallback for difficult products.
2. PSD smart-object/text-layer automation.
3. Catalog-level batch generation.
4. Agent Platform integration for permissions, task history, and review loop.

## Bottom line

The strongest community-backed path is:

Real product photo + prompt/template control + image-to-image model + deterministic PSD assembly.

For this project, a small, sharp MVP is more valuable than a broad agent framework. The first useful artifact should be a single SKU folder containing:

- truth pack
- source images
- generated images
- PSD manifest
- PSD
- preview PNG
- score report
- repair prompts

Once that works for 2-3 products, then move it into Agent Platform as a repeatable workflow.
