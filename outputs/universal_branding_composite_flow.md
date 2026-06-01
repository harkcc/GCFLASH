# Universal E-commerce Branding & Technical Composite Workflow

This document details the universal e-commerce design system architecture, the brand design language for **EXCITAT**, and the step-by-step technical implementation of the Alpha Matting Layer and Inpaint Masking pipeline.

---

## Part 1: Universal & Generic Design Architecture (通用化系统架构)

This solution is **not** a custom design for a single product; it is a **dynamic layout template system** that routes styles based on product categories:

```
                  [ SKU Product Input: Metadata & Image ]
                                     |
                                     v
                       [ Categorization Router ]
                                     |
      +------------------------------+------------------------------+
      |                              |                              |
      v                              v                              v
  [Tech/Gadgets]              [Garden/Outdoors]             [Home Appliances]
  - Matte slate / Neon glow   - Concrete / Forest green     - Warm plaster / Soft shadow
  - Slanted Speed Shelf       - Hexagonal Shield Shelf      - Clean Cut-out Logo
  - Cyber Cyan / Magenta      - Safety Orange / Grey        - Soft Blue / Gold
```

Every product uploaded to the pipeline goes through this classifier, which dynamically maps it to a specific **Frame Family** and **Ambient Staging Background**, ensuring consistent brand style across the entire store catalogue of 41+ items.

---

## Part 2: EXCITAT Brand Wordmark Matrix & Cool Visual Styling (EXCITAT 品牌字标矩阵)

The **EXCITAT** brand represents **energy, high performance, speed, and technical precision**. To make the brand wordmark look significantly cooler and more premium, we define three modular stylistic variants:

### 1. Speed Lightning Variant (速度闪电切角款) - *Recommended for Gadgets & Tech*
* **Visual Styling**: Flat-slanted geometric typography (`-6°` slant) with custom lightning cuts (lightning bolt shapes clipped from the letters `E` and `A`).
* **Material**: Semi-transparent dark glassmorphism backplate with a vibrant neon cyan stroke (`2px`) and chromatic aberration outlines (subtle red/cyan offset).
* **Backing**: Slanted double-layered speed shard (one layer dark graphite grey, one layer bright cyan).

### 2. Anisotropic Chrome Variant (各向异性金属拉丝款) - *Recommended for Tools & Hardware*
* **Visual Styling**: Heavy, blocky, three-dimensional extruded letters with sharp bevels.
* **Material**: Brushed stainless steel texture with anisotropic highlights. High contrast rim lighting.
* **Backing**: Matte black rubber-textured wedge with a safety orange underline.

### 3. Cyber Shard Variant (赛博能量碎片款) - *Recommended for Gaming & Audio*
* **Visual Styling**: Glowing laser-etched font outline with particle dust dispersing from the right side of the wordmark.
* **Material**: Pulse wave glowing letters with color-shifting cyan-to-purple gradient.
* **Backing**: Holographic projection plate with technical coordinate crosshairs.

---

## Part 3: Technical Implementation: Cutout Locking & Inpaint Masking

Here is the exact technical execution sequence showing how we maintain **100% product fidelity** while dynamically generating wires, scenes, and shadows.

```
Step 1: Product Matting          Step 2: Empty AI Background      Step 3: Staging & Shadows
   [Original Product]               [No Product in Prompt]           [Product Composite]
   +----------------+               +----------------+               +----------------+
   |  Original SVG  |               |  Studio Desk   |               |  Original SVG  |
   |  Cutout (PNG)  |               |  & Neon Lights |               | on Studio Desk |
   +----------------+               +----------------+               +----------------+
                                                                             |
                                                                             v
Step 5: Final Layout             Step 4: Regional Inpainting     [Inpaint Masking Applied]
   [Badges & Brand]                 [Ports & Cables]                 [Denoise = 0 inside Mask]
   +----------------+               +----------------+               +----------------+
   | EXCITAT Shelf  |               | Cable plugs    |               |  Mask lock on  |
   | & Specs Over   |<--------------| drawn into the |<--------------|  product body  |
   +----------------+               | BNC ports      |               +----------------+
```

### 1. High-Resolution Cutout Locking (高清抠图层锁定)
* **How it works**: When a product image is uploaded, we pass it through a high-precision matting model (e.g., BiRefNet or Segment Anything SAM 2) to generate a binary alpha mask.
* **Locking Logic**: The product cutout is stored as a high-resolution lossless transparent PNG. In the rendering stage (Pillow or Photoshop script), this cutout is layered on top of the generated canvas at its exact scale. The pixels of the product body are **never** passed into a diffusion sampler, ensuring 100% geometry, button, text, and texture preservation (0% deformation).

### 2. Local Inpaint Masking (局部重绘遮罩锁定)
To add interactive elements (like cables connecting to ports) or ground the product:
1. **Generating Wires**: We identify the coordinate points of the ports (BNC inputs).
2. **Creating the Mask**: We draw a small bounding box mask around the port socket area (extending slightly outside the port).
3. **Inpainting Setup**:
   * The area *inside the product contour* has `denoising_strength = 0` (strictly locked, no change).
   * The area *inside the port bounding box mask* has `denoising_strength = 0.6` (allowing the model to draw the male cable connector inserting into the port).
   * The area *outside the product* has `denoising_strength = 1.0` (fully generating the wires looping on the table).
4. **Result**: The cable connectors look physically plugged into the real device sockets, but the device sockets themselves remain perfectly intact.

---

## Part 4: Dynamic Staging Scenarios (场景化应用规范)

Instead of a generic marble slab, backgrounds are routed by context:

| Category | Recommended Staging Scenario | Ambient Lighting Accent |
| :--- | :--- | :--- |
| **Measurement / Lab Tech** | Electronics workbench with out-of-focus PCBs, soldering irons, components, tools | Cyan Neon (`#00e5ff`) |
| **Power Tools / Outdoors** | Workshop wooden bench, logs, concrete floors, forest foliage | Safety Orange (`#ff6b00`) |
| **Kitchen / Home Good** | Warm kitchen counter with blurred food ingredients, soft kitchen tiles | Sunbeam Warm Gold (`#ffb800`) |
| **Smart TV / Living Room** | Modern living room wall with out-of-focus TV console, soft plants | Ambient White / Soft Blue |
