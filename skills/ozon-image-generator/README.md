# OZON Main Image Generator Skill

This folder implements a specialized, high-conversion visual design and generation skill tailored for the **OZON** marketplace (Russian Region). It is designed to help AI agents and human designers collaborate on creating product main images (主图) that maximize click-through rate (CTR) and conversion rate (CVR).

## Folder Structure
- [SKILL.md](file:///Users/cc/Desktop/photo_show/skills/ozon-image-generator/SKILL.md): The core instruction file. It details the 3-step SOP (Analysis & Extraction, Prompt Generation, Check & Optimize).
- [DESIGN.md](file:///Users/cc/Desktop/photo_show/skills/ozon-image-generator/DESIGN.md): The design system file. It defines typography rules, high-contrast color palettes (Tech, Tool, Appliance), badge styles, layout composition margins, and the mobile legibility guidelines.

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
1. **Analysis & Extraction**: Analyze the product specs. Pick one of the three Ozon Color Archetypes (Black/Green, Grey/Orange, White/Blue). Identify the primary numeric selling point (e.g. `1200W`, `6 шт`, `2 года`) and trust features.
2. **Prompt Generation**: Construct a prompt highlighting product dominance (60%+ canvas), low-key high-contrast background, clean overlay zones, and soft studio lighting.
3. **Check & Optimize**: Perform the self-check checklist (readability at 160px width, zero-obstruction margin, max 3 colors, native Russian localization).
