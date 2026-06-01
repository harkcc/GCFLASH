# Segment 3: Prompt Generation & API Pipeline Flow

This document details the step-by-step visual synthesis pipeline, explaining how the AI agent compiles background prompts and invokes local/cloud models to guarantee **100% product geometry fidelity** while generating premium e-commerce staging.

---

## 1. Prompt Generation Methodology

To ensure stability and safe zones, prompts are generated in two parts: **Product Staging Constraints** and **Category Environment Prompts**.

### 1.1 Prompt Ingredients
- **Focal Point Scale**: Prompt must specify that the product is the "heroic focus, centered, occupying 60-70% of the canvas."
- **Lighting Dynamics**: Direct the model using high-end commercial descriptors: "dramatic studio rim lighting, volumetric rays, soft contact shadows."
- **Safe Zones Allocation**: The prompt must declare empty quadrants: "clean empty space in top-left, top-right, and right margin for e-commerce badges."
- **Text Negative Prompting**: Model-rendered text and watermarks must be strictly forbidden in the prompt to prevent "AI gibberish" labels.

---

## 2. Two-Stage Composite Pipeline Architecture

To prevent the product from deforming under AI diffusion (which is highly unstable), the production pipeline divides rendering into two stages:

```
                  [ Original Product Image ]
                              |
                              v
                 [ Stage 1: Local Pre-processing ]
                 - High-fidelity Alpha Matting (remove bg)
                 - Coordinate alignment (bounding box extraction)
                              |
                              v
                 [ Stage 2: Cloud Inpainting (Fal.ai) ]
                 - Reference cutout + inpaint mask uploaded
                 - Denoise weights: Product (0.0) | Interface (0.6) | Backdrop (1.0)
                 - API Model: fal-ai/flux-pro/v1.1 or flux-redux
                              |
                              v
                 [ Stage 3: Local Post-processing ]
                 - Secondary pixel-perfect贴合 alignment
                 - Render slanted EXCITAT Brand Shelf (Top-Right)
                 - Render numeric circles & feature badges (Pillow/Canvas)
                 - Mobile 160px Legibility Check
```

### 2.1 Stage 1: High-Fidelity Alpha Matting
The agent runs a local segmentation model (e.g., `BiRefNet` or `SAM 2` via a python script) to strip the background and generate a transparency PNG cutout (`product_cutout.png`) along with a black-and-white binary mask (`product_mask.png`).

### 2.2 Stage 2: Inpainting Mask & Denoising Controls
When calling the cloud API (e.g., Fal.ai `flux-pro/v1.1/inpaint` or `flux-pro/v1.1/redux`):
1. The original cutout is uploaded.
2. A coordinate-locked mask is applied over the product body.
3. The `denoising_strength` parameter is set dynamically:
   - **Product Area**: `0.0`. Absolutely no pixels inside the product bounding box are allowed to shift, keeping button placements, logos, and proportions mathematically locked.
   - **Interface Nodes (Connectors/Ports)**: `0.6`. Allows the model to render connecting wires or accessories (like probes or cords) emerging seamlessly from the sockets.
   - **Background Area**: `1.0`. Full denoising to allow creative atmosphere and photorealistic staging (e.g., lab workbench, SUV trunk, star study desk).

### 2.3 Stage 3: Local Deterministic Overlays (Pillow / Canvas)
Once the API returns the stage-2 base image, the local Python/Node script overlays the final e-commerce framework elements:
1. **EXCITAT Brand Shelf**: Drawn at a slanted `-6 degree` angle in the top-right corner with a cyan/orange glow stroke. The brand wordmark is overlayed using a bold sans-serif font (Arial Bold or custom font).
2. **Numeric Badge**: Placed in the top-left (e.g. `1098 pcs` or `50 MHz`), styled with a high-contrast circle or rounded rectangle.
3. **Feature Badges**: Formatted with high-signal short labels and clean unicode icons, aligned on the right.
4. **Trust Badges**: A flat circular warranty seal (e.g., `EXCITAT Guarantee`) placed on the right side.
