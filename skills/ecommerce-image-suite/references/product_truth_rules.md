# Product Truth Rules

Product truth is the main anti-hallucination layer.

## ProductTruthPack Fields

Use `workflow/schemas/product_truth_pack.schema.json` as the schema.

Required concepts:

- SKU or temporary product id
- category
- marketplace
- language
- source images
- immutable traits
- allowed changes
- forbidden changes
- selling points
- exact text copy if approved

## Immutable Traits

Record visible facts:

- color and finish
- material impression
- shape and silhouette
- handle, wheels, straps, hinges, buttons, ports, connectors
- logo and label placement
- transparent parts
- included accessories
- package contents

These must be repeated in every prompt under `KEEP`.

## Allowed Changes

Usually allowed:

- background
- lighting
- camera angle within product-recognition limits
- crop and scale
- supporting props
- lifestyle scene
- graphic badges and callout lines
- empty text zones

## Forbidden Changes

Usually forbidden:

- changing SKU geometry
- adding missing ports, buttons, cables, wheels, screws, handles, lights
- changing brand/logo
- changing material from plastic to metal or fabric to leather
- inventing capacity, power, warranty, certification, safety, medical, or
  compatibility claims
- turning a product into a premium version that is not sold

## Selling Point Translation

Translate product facts into visual evidence.

Examples:

- `360 degree rotation` -> arrow ring plus hinge callout
- `portable` -> hand scale or bag/travel context
- `waterproof` -> splash scene only if source confirms water resistance
- `quiet` -> sleeping baby/decibel meter only if source supports it
- `durable metal` -> macro material detail only if visible or sourced

If source proof is missing, use softer copy:

- use `built for everyday use`, not `industrial-grade`
- use `easy to carry`, not `14g` unless confirmed
- use `organized setup`, not `complete 12-piece kit` unless confirmed
