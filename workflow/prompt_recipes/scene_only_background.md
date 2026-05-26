# Scene Only Background Recipe

Use this when we plan to composite the real product cutout later.

## Prompt

```text
Create an ecommerce background scene only. Do not include the product, product-like objects, silhouettes, placeholders, logos, text, captions, or fake packaging.

The final product will be composited later into this scene, so reserve a clean product area:
{product_slot_description}

Scene:
{scene_description}

Lighting:
{lighting}

Surface and shadow expectation:
Leave a plausible surface where the product can sit. Use soft realistic light and enough empty space around the product slot.

Text zones:
{text_zone_description}

Negative constraints:
No product, no duplicate product, no product-shaped prop, no readable text, no labels, no busy clutter in the text area, no hard shadows that conflict with later compositing.
```

## Why

This prevents the common failure where an AI-generated scene already contains a fake version of the product, and the real product cutout creates a doubled subject after compositing.
