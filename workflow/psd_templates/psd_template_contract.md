# PSD Template Contract

PSD is a control and delivery layer. It should not replace image generation, and image generation should not replace editable text.

## Two PSD Modes

### Mode 1: PSD as output package

Use after generation:

```text
imagegen output + real product cutout + deterministic text + badges -> layered PSD + preview
```

Good for:

- final marketplace text
- designer handoff
- localized variants
- replacing badges, icons, or copy later

### Mode 2: PSD as template source

Use before generation:

```text
PSD template -> TemplateCard slots -> product insertion -> imagegen background/style -> deterministic overlay
```

Good for:

- reusing proven layouts
- preserving brand structure
- scaling product suites across SKUs

## Minimum PSDManifest Fields

- `canvas`: width, height, aspect ratio
- `layers`: bottom-to-top layer list
- `layer_type`: background, product, text, badge, icon, inset, frame
- `bbox`: x, y, width, height
- `editable_text`: exact copy or placeholder
- `style_tokens`: font, size, weight, color, alignment
- `replacement_rules`: what can be replaced per SKU
- `locked_rules`: what cannot move
- `source_confidence`: generated, user-provided, extracted, deterministic

## Current Validation Status

The current bggg image2psd test can write real raster-layer PSD files and full-canvas PNG layers. Text is rasterized, not native Photoshop editable text. Therefore production should keep both:

- the PSD file for visual handoff
- the PSDManifest for editable text metadata and automation

