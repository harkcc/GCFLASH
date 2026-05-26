# OpenAI Image Generation Prompt Contract

Use this route for premium scene exploration or background generation. Do not
ask the model to render final small text.

## Required Fields

```json
{
  "provider": "openai_image",
  "route": "ai_background_plus_composite",
  "brand_display": "EXCITAT",
  "banner_family": "product_scene_banner",
  "canvas": "1200x480 or 1140x456",
  "reference_roles": {
    "product_image": "preserve product identity only",
    "layout_reference": "layout logic only",
    "scene_reference": "mood/background only"
  },
  "text_slot": "left 42 percent, clean low-detail background",
  "product_slot": "right 45 percent, clear product area",
  "negative": [
    "no readable small text",
    "no fake logo",
    "no duplicate product",
    "no warranty, discount, rating or certification marks",
    "no clutter inside text slot"
  ]
}
```

## Post Process

Add EXCITAT, final headline, chips, icons and motion locally. Validate before
using the image in `detail.html`.

