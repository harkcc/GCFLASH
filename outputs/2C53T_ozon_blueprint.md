# English Main Image Blueprint: Oscilloscope 2C53T (3-in-1)

This blueprint documents the analysis, prompt generation, and visual layout plan for the 2C53T Portable Digital Oscilloscope, translated and optimized for English-speaking marketplaces (e.g., Amazon, Walmart).

---

## Phase 1: Analysis & Extraction

### 1. Product Core Information
* **Product Type**: Portable Digital Oscilloscope
* **Model**: 2C53T
* **Multi-functionality**: 3-in-1 (Oscilloscope, Multimeter, Signal Generator)
* **Key Specs**:
  * 50MHz Bandwidth
  * 250MS/s Sampling Rate
  * 3000mAh Battery
  * Type-C Interface
  * 2.8-inch LCD screen
  * 19999 counts Multimeter
* **Color Trim**: Blue bumpers

### 2. Information Hierarchy & Brand Integration (English)
* **Brand Wordmark (Top-Right Shelf)**: Large bold **`EXCITAT`** in an athletic, blocky e-commerce font, placed on a top-right slanted dark charcoal/cyan paper shard shelf (slanted at -6 degrees, 35% canvas width).
* **Primary Title (Top-Left)**: `OSCILLOSCOPE`
* **Subtitle**: `3-in-1 Portable Digital`
* **Core Numeric Badge (Click Catch)**: **50 MHz** (Bandwidth, inside a cyan rounded square badge in the top-left).
* **Secondary Feature Badges (Right column)**:
  1. `3000 mAh` (🔋 Battery capacity)
  2. `250 MS/s` (⚡ Sampling rate)
  3. `Type-C` (🔌 Quick charge)
* **Branded Trust Badge (Right Side Circular Badge)**:
  * A clean cyan circular badge on the right carrying: **`1-Year Warranty`** (large bold "1-Year" in the center, "Warranty" below). No generic shields.
* **Bottom Info Bar**: `Probe Kit Included` (Muted grey overlay text at the bottom).

### 3. Color & Styling Archetype
* **Theme**: Modern Tech / Industrial Lab
* **Palette**: Charcoal/Concrete Grey + White + Vibrant Neon Cyan (matching the product bumpers and the brand accents).
* **Composition**: Product dominant (65%), angled 3D standing pose via its kickstand, active measuring state (red/black probes plugged into ports), screen glowing, neon signal waves in the air.

---

## Phase 2: AI Background & Staging Prompt

Use this prompt to generate the product background, lighting, and scene:

```text
High-end commercial e-commerce advertising photography. The background is a professional electronics engineering laboratory workbench, highly relevant to the product. A desk scattered with out-of-focus circuit boards, soldering stations, electronic components, and diagnostic tools, with a shallow depth-of-field blur creating a technical, authentic atmosphere. Centered in the frame is the portable digital oscilloscope with blue rubber bumpers, standing upright via its kickstand, occupying 65% of the frame. A red and a black test probe cable are plugged into its bottom BNC ports, with the wires looping dynamically on the worktable. At the probe tips, glowing cyan electric sparks and a bright neon sine wave signal pulsate through the air. Photorealistic, high-contrast, dramatic studio rim lighting with cyan highlights, 8k resolution, crisp details. Clean empty margins in top-left, top-right, and right sides for badges and brand shelf.
```

---

## Phase 3: Visual Mockup Layout (English)

Below is the layout template mapping for the English canvas overlays:

```
+-------------------------------------------------------------+
|  [OSCILLOSCOPE]                               [ EXCITAT ]  |
|  <- Title (White Bold, 45pt)               <- Brand Shelf   |
|                                                (Slanted -6°) |
|  +--------------+                            +-----------+  |
|  |   50 MHz     |                            | 3000 mAh  |  |
|  |  (Bandwidth) |                            | (Battery) |  |
|  +-------+------+                            +-----+-----+  |
|          |                                         |        |
|          |    +----------------------------+       |        |
|          |    |                            |       |        |
|          +--->|      OSCILLOSCOPE          |       |        |
|               |      2C53T BODY            |<------+        |
|               |      (65% Scale)           |                |
|               |                            | +-----------+  |
|               |   [Glow Waveform Screen]   | | 250 MS/s  |  |
|               |                            | | (Sampling)|  |
|               +--------------+-------------+ +-----+-----+  |
|                              |                     |        |
|                              |                     v        |
|                              |               +-----------+  |
|                              |               |  Type-C   |  |
|                              v               +-----------+  |
|                       (Grounded Shadow)            |        |
|                                                    v        |
|                                              (( 1-Year ))   |
|                                              ((Warranty))   |
|  [ Probe Kit Included ]                      (Cyan Circle)  |
+-------------------------------------------------------------+
```



---

## Phase 4: Self-Check & Optimization

- **Legibility at 160px**: The contrast between the matte dark background and the vibrant blue bumper ensures the oscilloscope contour is extremely sharp. The numbers `50 MHz` and `3000 mAh` are instantly readable as a mobile search result snippet.
- **Cognitive Budget**: The visual design uses only **2 main colors** for text and badges (Cyan accent + White text), keeping it clean and readable.
- **Language**: Completely localized to **English** for international e-commerce platforms.

---

## Phase 5: Production Composite Workflow (防止产品变形)

E-commerce main images require **100% product fidelity**. AI generators (like Midjourney, SD, or Flux) inevitably deform buttons, ports, logos, and dimensions when attempting to draw the product directly.

To prevent deformation, the actual image production pipeline must use a **Layered Composite Workflow (分层合成流)**:

```
  +-----------------------------------------------------------+
  |              LAYER 4: Text & Badges (PSD/vector)          |
  |              - Overlaid cleanly on top, zero distortion   |
  +-----------------------------+-----------------------------+
                                |
                                v
  +-----------------------------+-----------------------------+
  |              LAYER 3: Real Product Cutout (Matting)       |
  |              - 100% exact pixels from the source photo    |
  +-----------------------------+-----------------------------+
                                |
                                v
  +-----------------------------+-----------------------------+
  |              LAYER 2: Ground Staging & Shadows (Pillow/PSD)|
  |              - Contact shadow underneath original product  |
  +-----------------------------+-----------------------------+
                                |
                                v
  +-----------------------------+-----------------------------+
  |              LAYER 1: AI Generated Background              |
  |              - Clean charcoal grey wall & blue neon glow   |
  +-----------------------------------------------------------+
```

### Layer Breakdown
1. **Background Layer (AI Generated)**: We only generate the empty scene (charcoal grey table, soft blue neon lighting). The prompt is modified to exclude the product subject and only describe the environment.
2. **Product Cutout Layer (Source Image)**: We extract the exact cutout of your original `2C53T` device (preserving buttons, Hantek markings, input ports, and screen proportions perfectly) using a transparent PNG mask.
3. **Contact Shadow Layer**: A dark soft ellipse is painted beneath the cutout feet and bumpers to anchor the device to the charcoal surface.
4. **Overlay Badge Layer**: Text like `50 MHz`, `3000 mAh`, and icons are placed on top as vector elements or font layers to prevent pixelation.

