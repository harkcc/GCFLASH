# Brand Frame Reference Rules

Brand images and door-frame style references should become reusable constraints.

## Extract From Brand References

For each brand reference image, extract:

- palette: main, accent, neutral, forbidden colors
- frame shape: full border, partial border, door-frame, corner marks, ribbon
- line weight and radius
- logo placement
- badge style
- typography feel
- background texture
- safe areas
- examples of what should not be copied

## Brand Frame Spec

Represent the result as:

```json
{
  "brand_frame_id": "example_brand_frame_v1",
  "palette": {
    "primary": "#000000",
    "accent": "#000000",
    "surface": "#ffffff"
  },
  "frame_geometry": {
    "type": "door_frame",
    "line_weight_px": 4,
    "corner_radius_px": 8,
    "safe_margin_px": 72
  },
  "logo_slot": {
    "position": "top_left",
    "max_width_pct": 12
  },
  "badge_style": {
    "shape": "rounded_rect",
    "usage": "numeric proof or trust marker"
  },
  "do_not": [
    "do not cover product silhouette",
    "do not add decorative clutter",
    "do not copy phone screenshot UI"
  ]
}
```

## Application Modes

Mode A: Prompt style control

- Use brand frame as wording in image prompt.
- Good for early direction.
- Low editability.

Mode B: Deterministic overlay

- Generate clean commercial image with reserved margins.
- Add frame, logo, badges, and text with HTML/Pillow/PSD.
- Best default for production.

Mode C: PSD template

- Use brand frame as PSD layer group.
- Keep product slot and text slots editable through PSDManifest.
- Best for template library and repeat SKU production.

## Current Missing Inputs

The framework can start without brand references, but production brand-frame
quality requires:

- clean brand frame images
- logo files
- preferred palette
- examples of approved and rejected image styles
- any platform-specific brand restrictions
