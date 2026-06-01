# OZON High-Conversion Main Image Generator SOP

This skill provides a standardized, high-conversion visual production workflow for generating main product images (主图) on the Russian e-commerce platform **OZON**. It focuses on the psychological browsing habits of Russian consumers (0.5s recognition, 1s click-intent, 3s trust-establishment) and implements a detailed three-step SOP.

---

## 1. SOP: The 3-Step Visual Production Loop

```
  +-------------------------------------------------------------+
  |              1. ANALYSIS & EXTRACTION (分析与提取)           |
  |  - Identify Core Product Category & Silhouette Shape        |
  |  - Extract Primary Numeric Value & 2-3 High-Impact Selling  |
  |  - Select Visual Color Archetype based on Ozon Rules        |
  +------------------------------+------------------------------+
                                 |
                                 v
  +------------------------------+------------------------------+
  |              2. PROMPT GENERATION (提示词生成)               |
  |  - Formulate Stable background prompt recipe                 |
  |  - Enforce "Product Giantification" (60%+ canvas area)       |
  |  - Carve out safe zones for overlays & numeric badges        |
  +------------------------------+------------------------------+
                                 |
                                 v
  +------------------------------+------------------------------+
  |               3. CHECK & OPTIMIZE (检查与优化)               |
  |  - Run Mobile Thumbnail Scaling legibility check             |
  |  - Audit typography & text density (max 3-4 words/line)     |
  |  - Verify 3-color palette limit & high-contrast validation   |
  +-------------------------------------------------------------+
```

---

## 2. Step 1: Analysis & Extraction (分析与提取)

### 2.1 Product Analysis Checklist
1. **Silhouette Definition**: What is the physical object? (e.g., handheld vertical vacuum cleaner, pruning shears). It must be easily recognizable within **0.5 seconds**.
2. **Numeric Sell Point**: Identify the highest-impact number + unit.
   - *Good*: `960 mAh`, `30 дней` (30 days), `6 шт` (6 pieces), `30 мм` (30mm cut capacity), `95000 PA`.
   - *Avoid*: Vague descriptions like "super large capacity", "very long battery life".
3. **Trust Elements**: Select 1-2 trust claims to be visualized as badges/shields:
   - `гарантия` (warranty/guarantee)
   - `комплект` (complete kit/accessories included)
   - `оригинал` (original brand guarantee)
4. **Contextual Scenario**: Identify where the product is used (e.g., outdoors for tools, kitchen for pots, wrist for watch). This will be shown in a minor scenario inset/badge.

### 2.2 Marketplace Color Archetype Matching
Choose one of the three high-conversion Ozon color palettes:
- **Black + Green** (科技/户外 - Tech/Outdoor): For electronic gadgets, power tools, smart devices.
- **Grey + Orange** (工具/汽配 - Hardware/Automotive): For hand tools, car accessories, rugged gear.
- **White + Blue** (家电/百货 - Home Appliances/Daily Goods): For vacuum cleaners, humidifiers, kitchen appliances.

---

## 3. Step 2: Prompt Generation (提示词生成)

### 3.1 Prompt Synthesis Rules
1. **Background Contrast**: Background must be simple, low-key, and high-contrast relative to the product. Use terms like "studio background, subtle gradient, minimalist staging, soft vignette". Avoid busy, chaotic backdrops.
2. **Product Dominance**: The main product shape must occupy **60%+** of the canvas. Use prompt terms like "centered, massive product focus, heroic scale, close-up details".
3. **Safe Text Zones**: Carve out empty, clean zones for overlays (top-left for core numeric badge, right side for feature badges, bottom for kit accessories). Use prompt terms like "clean copy space, clean composition, minimalist background".
4. **Depth & Shadows**: Avoid floatation unless it fits a tech product. Use "realistic contact shadow, grounded staging, studio lighting, volumetric shadows" to establish trust and physical quality.

### 3.2 Prompt Template
Use the following structured format to generate prompts:
```text
[Main Product Subject with description] placed at [angle/isometric view], occupying 60% of the canvas. Grounded on [surface description] with realistic contact shadows. Background is a [background description with 2-color gradient/subtle textures], creating a strong contrast with the product. High-end studio lighting, volumetric light rays, highlighting details of [key product parts]. Clean empty zones in top-left and right sides for e-commerce text overlays. Photorealistic, ultra-detailed, commercial advertising style.
```

---

## 4. Step 3: Check & Optimize (检查与优化)

### 4.1 Mobile Verification Checklist
- [ ] **Legibility at 160px**: Shrink the image to mobile preview size. Is the product outline clearly identifiable? Are the key numbers legible?
- [ ] **First-Sight Focus**: When looking at the image for 1 second, does the eye land directly on the product and its primary numeric selling point?
- [ ] **No Overlaps (Zero-Obstruction)**: Is there a minimum 15px gap between the product edges and any text overlays, badges, or icons?
- [ ] **Color Budget Check**: Does the overall layout (excluding the product itself) contain at most **3 colors** (Primary background, text color, highlight accent)?
- [ ] **Language & Text Policy**: Are all words short (max 3-4 words per line)? If using Russian, ensure correct localization and translation (e.g. `гарантия` instead of english warranty).

---

## 5. E-commerce Production Advanced Methodologies

### 5.1 Product Geometry & Fidelity Preservation (保证原图不变)
1. **High-Fidelity Alpha Matting**: Extract the exact product shape from the source image using an alpha-channel mask (transparency PNG).
2. **Untouched Mask Inpainting (局部重绘锁定)**: Define an inpainting mask matching the product bounding box, setting the mask's `denoising_strength` to `0` or locking the latent codes within the mask. The background and lighting are generated around the product, but the product body itself remains mathematically unchanged.
3. **Rigid 3D Projections**: For pose changes, use rigid transform matrices (scaling, translation, shear, rotation) on the original product cutout to warp it in 3D perspective rather than letting AI draw the shape.

### 5.2 Contextual Motion & State Changes (添加动效与形态改变)
1. **Interface Node Tracking**: Map the coordinate points of interface ports (e.g. BNC input ports, multimeter jack inputs) on the product cutout.
2. **Context-Guided Wires (AI Path Rendering)**: Initiate lines extending from these interface nodes, and instruct the AI (using ControlNet or regional inpainting) to render thick, flowing, looping cables that wrap dynamically on the table.
3. **High-Energy FX Overlay (光影与能量流叠加)**: Overlay a transparent neon effect layer (electrical sparks, glowing sine waves, magnetic fields) aligned directly with the probe tips or screen grid lines.

### 5.3 Brand Identity Integration (品牌特性注入)
1. **EXCITAT Custom Trust Seal**: Replace generic badges with a unified brand warranty shield containing the **EXCITAT** logo or text (e.g., `EXCITAT Premium Guarantee`, `EXCITAT / 1 Year Warranty`).
2. **Brand Frame & Color Synergy**: Accent color accents (e.g. Ozon Blue `#005bff` or custom brand orange) must flow into the badge borders.
