# Reference Img2Img Base Recipe

Use this when the input includes:

- one product image or product cutout
- one visual template/reference image
- one TemplateCard
- one ProductTruthPack

## Prompt Structure

```text
TASK
Create a marketplace-ready ecommerce image for {marketplace}. The image role is {image_role}: {template_job}.

REFERENCE ROLES
- Product image: source of truth for the product.
- Visual template image: composition, visual hierarchy, color mood, lighting direction, and commercial layout reference.

KEEP FROM PRODUCT IMAGE
Keep the exact product identity:
{immutable_traits}

KEEP FROM VISUAL TEMPLATE
Keep the template's commercial logic:
{template_core_pattern}
Keep the overall layout rhythm, product/text zone relationship, background depth, lighting mood, and number/icon/badge hierarchy where applicable.

CHANGE / ADAPT
Replace the template product with this product: {category}.
Adapt all visual metaphors and scene details to these selling points:
{selling_points_visualized}

LAYOUT
{layout_zones}
Product should be visually dominant: {product_weight}.
Use 1-3 focus points only. Avoid visual clutter.

TEXT POLICY
{text_policy_instruction}

STYLE
Palette: {palette}
Lighting: {lighting}
Background: {background}
Typography mood if text is rendered: {typography}

NEGATIVE CONSTRAINTS
Do not change product shape, color, material, proportions, label/logo position, buttons, ports, seams, package structure, or visible product details.
Do not add extra product parts or fake accessories.
Do not render unreadable fake text.
Do not create a poster that ignores the ecommerce layout.
Do not make the product too small.

OUTPUT
Sharp, commercial, marketplace-ready image with clear product recognition and high conversion visual structure.
```

## Model Notes

### GPT Image 2

Use the most structured prompt. Be precise about visible objects, zones, text placement, and exact words if asking it to render text. Prefer overlay-later for production copy.

### Flux / Flux Kontext

Emphasize reference preservation and change boundaries. Use it for product-scene fusion and visual drama. Use composite fallback if product details drift.

### Nano Banana

Use for quick multi-reference exploration. Keep prompt shorter and more literal. Use for style direction and candidate mood, not final text-heavy outputs.

### Midjourney

Use only to create visual language and moodboards. Do not depend on it for SKU-faithful production or exact copy.
