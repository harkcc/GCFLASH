---
name: ozon-image-generator
description: |
  A specialized visual production and prompt engineering skill for generating
  high-conversion, premium e-commerce main product images (主图) tailored for the
  Russian marketplace (OZON). Implements the OpenDesign Design MD spec and the
  three-step SOP: Analysis & Extraction, Prompt Generation, and QA Verification.
triggers:
  - "ozon image"
  - "ozon主图"
  - "电商主图"
  - "主图生成"
  - "OZON design"
od:
  mode: image
  scenario: marketing
  preview:
    type: markdown
    entry: README.md
  design_system:
    requires: true
    sections: [color, typography, layout, components, prompt]
  inputs:
    - name: product_name
      type: string
      required: true
    - name: product_specs
      type: markdown
      required: true
    - name: style_archetype
      type: enum
      values: [tech_dark_green, rugged_grey_orange, appliance_white_blue, custom]
      default: tech_dark_green
  outputs:
    - SKILL.md
    - DESIGN.md
    - compiled_prompts/
    - qa_scorecard.md
---

# OZON High-Conversion Main Image Generator Skill

This skill provides a standardized, high-conversion visual production workflow for generating main product images (主图) on the Russian e-commerce platform **OZON**. It focuses on the psychological browsing habits of Russian consumers (0.5s recognition, 1s click-intent, 3s trust-establishment) and implements a detailed three-step SOP.

---

## 1. SOP: The 3-Step Visual Production Loop

```
  +-------------------------------------------------------------+
  |              1. ANALYSIS & EXTRACTION (分析与提取)           |
  |  - Inspect Source Product Image Before Choosing Background   |
  |  - Identify Core Product Category & Silhouette Shape        |
  |  - Lock Product Physics, Accessory Relations & Support Logic|
  |  - Extract Primary Numeric Value & 2-3 High-Impact Selling  |
  |  - Select Visual Color Archetype based on Ozon Rules        |
  +------------------------------+------------------------------+
                                 |
                                 v
  +------------------------------+------------------------------+
  |              2. PROMPT GENERATION (提示词生成)               |
  |  - Route Background from Product Usage & Object Logic        |
  |  - Choose Product Hero Pose Inside The Fixed Main Layout     |
  |  - Formulate Stable background prompt recipe                 |
  |  - Enforce "Product Giantification" (60%+ canvas area)       |
  |  - Carve out safe zones for overlays & numeric badges        |
  +------------------------------+------------------------------+
                                 |
                                 v
  +------------------------------+------------------------------+
  |               3. CHECK & OPTIMIZE (检查与优化)               |
  |  - Run v3 Guard after Plan and before final image prompt     |
  |  - Remove unsupported numbers, duplicate claims & fake trust |
  |  - Run Mobile Thumbnail Scaling legibility check             |
  |  - Audit typography & text density (max 3-4 words/line)     |
  |  - Verify 3-color palette limit & high-contrast validation   |
  +-------------------------------------------------------------+
```

---

## 2. Step 1: Analysis & Extraction (分析与提取)

Before generating any visual assets, analyze the product metadata to extract the exact selling hooks that fit OZON's user behaviors.

### 2.1 Product Analysis Checklist
1. **Source Image Truth**: What exact object, accessories, colors, ports, support points, and material details are visible in the uploaded product image? These are immutable unless the user explicitly asks for a redesign.
2. **Object Logic**: How does the product physically work or sit in the scene? Identify mounts, handles, charging slots, plugs, cables, hinges, pumps, nozzles, display screens, or support feet that must remain logical.
3. **Silhouette Definition**: What is the physical object? (e.g., handheld vertical vacuum cleaner, pruning shears). It must be easily recognizable within **0.5 seconds**.
4. **Parameter Story**: Decide which verified facts deserve visual emphasis.
   - First ask what the buyer must notice in the first second for this product.
   - Use one hero parameter only when a verified number/unit, compatibility claim,
     model/spec, or kit claim is commercially decisive.
   - Route other facts into secondary parameter rail, part-anchored callouts,
     bundle/accessory area, or trust badge.
   - Omit a hero parameter when no parameter is truly decisive; do not force a
     number just because one exists.
   - Make the selected parameter visually dominant. The first-read hook should be
     a large value island/slab or circle where the value occupies most of the
     container; secondary facts should be medium slabs; only detail notes should
     become small icon callouts.
   - Match parameter block colors to the product category palette in
     `DESIGN.md`. Do not default to black/white value blocks for soft home,
     kitchen, or baby products.
   - Main value islands should sit beside or visually extend from the product
     area. Long leader lines crossing the product are reserved for no case; use
     only adjacent tabs, short connector dots, or compact elbow callouts.
   - For rotating products, use verified RPM/blade speed as a potential hero
     value when supplied; never invent a speed number.
   - *Good role decisions*: memory/game count for a game console, lamp model and
     brightness for auto bulbs, RPM/voltage/battery count for a drill, capacity
     or sterilizing/heating mode for a baby appliance.
   - *Avoid*: regex/unit scoring, category hard-coding, or vague descriptions like
     "super large capacity" and "very long battery life".
5. **Trust Elements**: Select 1-2 trust claims to be visualized as badges/shields:
   - `гарантия` (warranty/guarantee)
   - `комплект` (complete kit/accessories included)
   - `оригинал` (original brand guarantee)
   These claims must be verified in the submitted product title, detail text,
   source image notes, or explicit product facts. Do not invent warranty,
   official/original, certification, BPA-free, safety, or compliance language.
6. **Contextual Scenario**: Identify where the product is used (e.g., outdoors for tools, kitchen for pots, wrist for watch). This determines the background before any decorative styling is chosen.

### 2.1a v3 Guard Checkpoint
Before compiling the final image prompt, run a guard pass on the plan.

1. **Fact Guard**: Visible numeric/spec claims must come from submitted facts.
   `5-in-1` or similar combined numbers require explicit source wording; do not
   infer them from a list of features.
2. **Role Guard**: Classify each claim into one role only: hero value,
   secondary slab, part callout, bundle/accessory, or trust badge.
3. **Duplicate Guard**: The same value or selling point must not appear in two
   regions. If `220V` is a value slab, it cannot also appear in the bottom trust
   area.
4. **Connector Guard**: Hero and secondary parameter blocks are freestanding
   value islands/slabs. Only small part callouts may use short connector dots or
   compact elbow lines.
5. **Trust Guard**: Bottom/corner support is for verified trust, kit, brand, or
   accessory information. It cannot repeat functional parameters and cannot
   invent warranty or safety claims.
6. **Report Guard**: Emit a guard report with removals and warnings so the
   strictness can be tuned. Guard should sanitize obvious errors in balanced
   mode, but only strict mode should block generation.

### 2.2 Background Scene Depth Decision
The background must explain the product's real usage context without competing with it. Do not reduce the scene to a decorative wall, table, texture, or gradient.

1. **Support Surface**: Identify the physical surface that carries the product: gaming wall, electronics bench, SUV trunk, study desk, kitchen counter, garden ground, or workshop table.
2. **Category Depth Cue**: Add one or two low-detail background cues that prove the product category: blurred monitor/shelf for gaming gear, PCB/soldering tools for measurement devices, folded seats for car accessories, window/telescope/books for STEM kits.
3. **Product-Derived Lighting Plan**: Before writing scene prose, infer the light from the product and usage context. This is an internal reasoning step, not a rigid label to paste into the final prompt.
   - **Physical light source**: Name where the light comes from: probe tips touching PCB pads, RGB charger dock, glowing STEM sun core, car side windows, room lamps, workbench task light, outdoor sky, or a neutral studio source.
   - **Commercial role**: Decide what the light proves: active function, material texture, product scale, safe installation, cozy usage context, or clean catalog readability.
   - **Visible effect**: Describe the result in natural image language: small controlled sparks, soft RGB wash under controllers, warm highlights on gears, daylight across fabric texture, realistic contact shadows, or a subtle rim separating the silhouette.
   - **Overuse risk**: Remove neon, beams, dramatic rim glow, sparks, or strong color cast unless the product or scene gives them a believable physical source.
4. **No Unjustified Glow**: Glow effects are allowed only when they explain the product or scene. A mattress, soft good, storage item, or simple accessory usually needs clean daylight or soft indoor light, not tech lighting.
5. **Shallow Depth Control**: Category cues must stay blurred, cropped, or pushed to the side/background. They should create depth, not visual noise.
6. **No Empty Wall Default**: A clean wall can be the support surface, but it should still include a subtle scene cue or depth line when the product category benefits from context.

### 2.3 Product Hero Pose Decision
The universal Ozon card layout controls the page skeleton, but it does not decide how the product enters the center product zone. Before writing the final image prompt, choose the product's strongest hero pose and staging logic.

1. **Center Dominance Is Fixed**: The product should remain near the visual center and occupy roughly 60-75% of the canvas.
2. **Pose Is Dynamic**: Choose front view, slight side angle, 3/4 angle, hanging, mounted, expanded, plugged-in, or in-use staging based on the product's shape and function.
3. **Function Must Become Visible**: If a product's value is only clear through action, add physically believable active elements. Examples: oscilloscope probes connected to ports and touching a PCB, a charger holding controllers, a mattress fitted inside a car trunk, or a STEM model glowing from its sun core.
4. **Action Needs Contact And Outcome**: Do not describe accessories as merely "near", "toward", or "around" the product. Name the contact point and visible result: probe tips touch PCB pads and create a small controlled spark, a charging dock emits RGB light under the controllers, a pump nozzle connects to the mattress valve, or a support bracket visibly carries the mounted object.
5. **Accessories Must Explain The Product**: Cables, nozzles, pumps, brackets, docks, handles, planets, screws, and support feet should be placed where they make the product easier to understand, not scattered as decoration.
6. **No Default Front-View Bias**: Do not default to a flat catalog front view when a slight side or 3/4 pose better shows depth, function, scale, or usage logic.

### 2.4 Marketplace Color Archetype Matching
Choose one of the three high-conversion Ozon color palettes:
- **Black + Green** (科技/户外 - Tech/Outdoor): For electronic gadgets, power tools, smart devices.
- **Grey + Orange** (工具/汽配 - Hardware/Automotive): For hand tools, car accessories, rugged gear.
- **White + Blue** (家电/百货 - Home Appliances/Daily Goods): For vacuum cleaners, humidifiers, kitchen appliances.

---

## 3. Step 2: Prompt Generation (提示词生成)

Generate a prompt recipe for the AI image generation model (e.g., Midjourney, Stable Diffusion, SDXL, FLUX) to render the premium background, lighting, and product staging environment.

### 3.1 Prompt Synthesis Rules
1. **Product-First Background Routing**: Choose the scene from the source product and its physical use case. Measurement devices belong in lab/workbench contexts, auto comfort products in vehicle interiors, gaming accessories near gaming walls/setups, STEM kits in study/science contexts.
2. **Scene Depth Structure**: State the support surface, one low-detail category depth cue, and the product-derived light source. Avoid flat texture-only backgrounds.
3. **Background Contrast**: Background must be simple, low-key, and high-contrast relative to the product. Use terms like "shallow depth-of-field usage scene, subtle vignette, clean copy space". Avoid busy, chaotic backdrops.
4. **Product Dominance**: The main product shape must occupy **60%+** of the canvas. Use prompt terms like "centered, massive product focus, heroic scale, close-up details".
5. **Object Logic Preservation**: The prompt must explicitly preserve accessory placement, cable/port logic, mounts, charging bases, support points, handles, and other physical relationships.
6. **Hero Pose Expression**: State the chosen product pose and active physical interaction in the prompt. The product should enter the fixed Ozon layout through a product-specific pose, not a generic centered front view.
7. **Parameter Layout Role**: If the planner selected a hero parameter, reserve a first-read slab/circle in the top-left or left-center. If it selected secondary parameters, reserve a side/lower-left rail. If it selected part callouts, anchor them to visible product parts.
8. **Safe Text Zones**: Carve out empty, clean zones for overlays (top-left for title/hero parameter, right side for part callouts or feature badges, bottom for kit accessories/trust). Use prompt terms like "clean copy space, clean composition, minimalist background".
9. **Depth & Shadows**: Avoid floatation unless it fits a tech product. Use product-matched contact shadows, ambient depth, rim separation, reflection, or glow only when the scene has a physical reason for it.

### 3.2 Prompt Template
Use the following structured format to generate prompts:
```text
[Main Product Subject with description] placed at [angle/isometric view], occupying 60% of the canvas. Grounded on [surface description] with realistic contact shadows. Background is a [product-specific usage scene] with [low-detail depth cue]. Light comes from [physical source] and creates [visible effect on product/material/action]. Clean empty zones in top-left and right sides for e-commerce text overlays. Photorealistic, ultra-detailed, commercial advertising style.
```

---

## 4. Step 3: Check & Optimize (检查与优化)

Review the generated candidate layout against the Ozon QA Scorecard before final output.

### 4.0 Plan/Prompt Guard Verification
- [ ] **Guard Report Exists**: The run writes `guard_report.json` and the
  report status is reviewed.
- [ ] **No Unsupported Combined Numbers**: Claims like `5-in-1`, `3-in-1`, or
  `100% fit` are present only when explicitly supplied.
- [ ] **No Cross-Region Repetition**: Hero value, secondary slabs, feature
  badges, trust badge, and support area do not repeat the same value or claim.
- [ ] **No Fake Trust Claims**: Warranty, official/original, BPA-free, safety,
  CE/FDA, food-grade, or medical claims are verified before display.
- [ ] **Value Blocks Stay Freestanding**: Numeric value islands/slabs do not use
  long connector lines. Only part callouts use short connectors.

### 4.1 Mobile Verification Checklist
- [ ] **Legibility at 160px**: Shrink the image to mobile preview size. Is the product outline clearly identifiable? Are the key numbers legible?
- [ ] **First-Sight Focus**: When looking at the image for 1 second, does the eye land directly on the product and its primary numeric selling point?
- [ ] **No Overlaps (Zero-Obstruction)**: Is there a minimum 15px gap between the product edges and any text overlays, badges, or icons?
- [ ] **Color Budget Check**: Does the overall layout (excluding the product itself) contain at most **3 colors** (Primary background, text color, highlight accent)?
- [ ] **Language & Text Policy**: Are all words short (max 3-4 words per line)? If using Russian, ensure correct localization and translation (e.g. `гарантия` instead of english warranty).

---

## 5. E-commerce Production Advanced Methodologies

To ensure professional quality, our pipeline integrates three advanced techniques based on real production experience:

### 5.1 Product Geometry & Fidelity Preservation (保证原图不变)
To guarantee the product does not deform under AI diffusion:
1. **High-Fidelity Alpha Matting**: Extract the exact product shape from the source image using an alpha-channel mask (transparency PNG).
2. **Untouched Mask Inpainting (局部重绘锁定)**: In image generation models, define an inpainting mask matching the product bounding box, setting the mask's `denoising_strength` to `0` or locking the latent codes within the mask. The background, wires, and lighting are generated around the product, but the product body itself remains mathematically unchanged.
3. **Rigid 3D Projections**: For pose changes, use rigid transform matrices (scaling, translation, shear, rotation) on the original product cutout to warp it in 3D perspective rather than letting AI draw the shape.

### 5.2 Contextual Motion & State Changes (添加动效与形态改变)
To add energy and active states to a static product:
1. **Interface Node Tracking**: Map the coordinate points of interface ports (e.g. BNC input ports, multimeter jack inputs) on the product cutout.
2. **Context-Guided Wires (AI Path Rendering)**: Initiate lines extending from these interface nodes, and instruct the AI (using ControlNet or regional inpainting) to render thick, flowing, looping cables that wrap dynamically on the table.
3. **High-Energy FX Overlay (光影与能量流叠加)**: Overlay a transparent neon effect layer (electrical sparks, glowing sine waves, magnetic fields) aligned directly with the probe tips or screen grid lines to simulate real-time active measurements.

### 5.3 Brand Identity Integration (品牌特性注入)
For Ozon marketplace listings, brand visualization builds long-term customer trust. For the **EXCITAT** brand, we enforce the following rules:
1. **EXCITAT Custom Trust Seal**: Replace generic "1-Year Warranty" or "Premium Quality" badges with a unified brand warranty shield containing the **EXCITAT** logo or text (e.g., `EXCITAT Premium Guarantee`, `EXCITAT / 1 Year Warranty`).
2. **Brand Frame & Color Synergy**: Accent color accents (e.g. Ozon Blue `#005bff` or custom brand orange) must flow into the badge borders. The badge must feel integrated into the brand's aesthetic.

---

## 6. Verification Command Example
To perform a complete analysis, run the local analysis and scorecard compiler script:
```bash
node scripts/compile_ecommerce_prompt.mjs \
  --truth inputs/ozon_vacuum.truth.json \
  --template workflow/template_cards/OzonHeroCard.json \
  --out outputs/ozon_run_01 \
  --sku ozon_vacuum \
  --marketplace Ozon \
  --text-policy deterministic_overlay
```
