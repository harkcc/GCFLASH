---
name: gaming_hero_4k
version: 0.1.0
description: Gaming / tech product listing hero image with bold 4K-style typography, brand stroke text, spec badges, and cyber aesthetic background. Mimics high-engagement gaming listing style (reference: EXCITAT Game Stick Pro).
---

# gaming_hero_4k

## When to use
- `image_type`: hero
- `category`: gaming / electronics / tech_gadgets / streaming_devices
- `mood`: high-energy, bold, cyber, advertising
- Alternative when product needs visible "number + spec badge" display (4K / 150PSI / 20000mAh etc.)

## Not suitable for
- Soft lifestyle products (fashion, beauty, home decor) — use `lifestyle_hero_editorial`
- Industrial tool / automotive — use `automotive_hero_industrial`

## Design elements
1. Big stroke hero number (top-left, 200+ pt, white fill + black stroke)
2. Brand wordmark (top-right, italic, colored stroke)
3. Primary spec badge (slanted, bold background color)
4. Secondary spec lines (right side, stroked white)
5. Central composition: generated background + product + supporting elements
6. Bottom accessory strip (optional)

## Inputs (schema.json)
- `background_image_url` (string, required): Pre-generated hero composite background (usually from Nano Banana 2). Should have empty top-left and top-right corners.
- `hero_number` (string, required): The big spec number (e.g., "4K", "150PSI", "128GB")
- `brand_name` (string, required): Brand wordmark (e.g., "EXCITAT")
- `brand_color` (string, default #E11): Brand stroke color in hex
- `badge_text` (string, optional): Primary badge text (e.g., "128GB")
- `badge_color` (string, default #1E90FF): Badge background color
- `spec_line_1` (string, optional): Right-side spec label (e.g., "31999+ Games")
- `spec_line_2` (string, optional): Right-side spec label 2 (e.g., "23 Emulators")

## Output
- Final PNG at 1024×1024 (default) or 2048×2048 (high-res)

## Example
```bash
python3 render.py inputs.json output.png
```

See `examples/` for reference output.
