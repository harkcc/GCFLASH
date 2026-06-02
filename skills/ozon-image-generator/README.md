# OZON Main Image Generator Skill

This folder implements a specialized, high-conversion visual design and generation skill tailored for the **OZON** marketplace (Russian Region). It is designed to help AI agents and human designers collaborate on creating product main images (主图) that maximize click-through rate (CTR) and conversion rate (CVR).

## Folder Structure
- [SKILL.md](file:///Users/cc/Desktop/photo_show/skills/ozon-image-generator/SKILL.md): The core instruction file. It details the 3-step SOP (Analysis & Extraction, Prompt Generation, Check & Optimize).
- [DESIGN.md](file:///Users/cc/Desktop/photo_show/skills/ozon-image-generator/DESIGN.md): The design system file. It defines typography rules, high-contrast color palettes (Tech, Tool, Appliance), badge styles, layout composition margins, and the mobile legibility guidelines.
- [RUNTIME_CONTEXT.md](file:///Users/cc/Desktop/photo_show/skills/ozon-image-generator/RUNTIME_CONTEXT.md): Prompt compiler context distilled from the original stable Antigravity Ozon conversation. It enforces product-first analysis, object logic, category-routed backgrounds, and EXCITAT brand shelf behavior without turning prior outputs into fixed visual references.

## Quick Reference: The Universal Layout
```
+--------------------------------------------------------+
|  [TITLE - Large Russian Bold Sans-serif]                |
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
1. **Analysis & Extraction**: Analyze the source product image first, then product specs. Identify immutable product geometry, accessories, physical support/connection logic, the primary numeric selling point (e.g. `1200W`, `6 шт`, `2 года`) and trust features.
2. **Hero Pose Decision**: Keep the universal layout fixed, but choose how the product enters the center zone: front view, 3/4 angle, side angle, mounted, expanded, plugged-in, or actively interacting with accessories when that better explains the product.
3. **Lighting & Scene Plan**: Infer the physical light source from the product and usage context. Decide whether light proves product function, material texture, scale, installation, or simple clean readability; do not paste rigid lighting labels into the final prompt.
4. **Prompt Generation**: Route the background from the product's category and physical usage logic, then construct a prompt highlighting product dominance (60%+ canvas), product-specific pose/action, low-key high-contrast background, product-derived lighting, and clean overlay zones.
5. **Check & Optimize**: Perform the self-check checklist (readability at 160px width, zero-obstruction margin, max 3 colors, native Russian localization).
