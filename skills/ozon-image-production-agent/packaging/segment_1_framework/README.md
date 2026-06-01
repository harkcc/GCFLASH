# OZON Main Image Generator Framework

This folder implements a specialized, high-conversion visual design and generation system tailored for the **OZON** marketplace (Russian Region). It helps AI agents and human designers collaborate on creating product main images that maximize click-through rate (CTR) and conversion rate (CVR).

## Files Overview
* [SKILL.md](file:///Users/cc/Desktop/photo_show/skills/ozon-image-production-agent/packaging/segment_1_framework/SKILL.md): Details the 3-step SOP (Analysis & Extraction, Prompt Generation, Check & Optimize).
* [DESIGN.md](file:///Users/cc/Desktop/photo_show/skills/ozon-image-production-agent/packaging/segment_1_framework/DESIGN.md): Defines colors, typography, margins, layouts, and components.

## Universal Layout Grid
```
+--------------------------------------------------------+
|  [TITLE - Large Russian/English Bold Sans-serif]       |
|  (Badge: Numeric Accent)             (Badge: Trust)     |
|         \                                /             |
|          \  +------------------------+  /              |
|             |                        |                 |
|             |     PRODUCT BODY       |                 |
|             |     (Dominant)         |                 |
|             |      60%+ Size         |                 |
|             |                        |                 |
|             +------------------------+                 |
|                                                        |
|                                       [Scenario Inset] |
|  [Kit Accessories / Bottom Badges]    [e.g., watch wrist] |
+--------------------------------------------------------+
```

## How to Execute the SOP
1. **Analysis & Extraction**: Analyze the product specs. Pick one of the three Ozon Color Archetypes (Black/Green, Grey/Orange, White/Blue). Identify the primary numeric selling point.
2. **Prompt Generation**: Build an image generation prompt focusing ONLY on scene, lighting, placement, and shadows. Do not generate text or logos.
3. **Check & Optimize**: Use deterministic Pillow / PSD layers to add overlays (badges, brand shelf, warranty circles). Perform the 160px thumbnail test.
