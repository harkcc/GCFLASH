# Text And Typography Rules

Text is a production layer, not a decoration.

## Core Decision

For ecommerce images, final text should usually be deterministic overlay:

```text
image model: product + background + composition + empty text zones
overlay layer: headline + badges + callouts + localized copy + brand frame
```

Use model-rendered text only for rough drafts or very short exact labels.

## Why

Image models can create good commercial composition, but they are still risky
for:

- exact English spelling
- Russian/Japanese/localized text
- consistent font family
- legal/compliance wording
- repeated suite-wide typography
- editable PSD handoff

## TextCopyPlan

Use `workflow/schemas/text_copy_plan.schema.json`.

Each generated slot should have a seed text plan with:

- headline
- subheadline if needed
- 1-3 badges or callouts
- footer/trust strip if needed
- exact placement
- max line count
- max characters
- overlay requirement
- copy source

## Copy Hierarchy

Use this order:

1. One big promise or product identity.
2. One proof number or short trust badge.
3. Two to four secondary callouts only if the template needs them.
4. Footer/package/warranty only if supported by product truth.

Avoid paragraphs. In marketplace thumbnails, large numbers and short words beat
long claims.

## Character Budgets

Default English limits:

- headline: 18-32 characters
- subheadline: 24-48 characters
- badge: 3-14 characters
- callout: 8-24 characters
- footer label: 6-18 characters

For Russian/German, reduce count or enlarge zones because words are longer.

## Font Rules

Default ecommerce typography:

- primary font: neutral geometric sans
- display font: bold geometric sans
- number font: tabular or condensed bold sans
- fallback: system sans

Use:

- bold for one primary headline only
- tabular numerals for wattage, PSI, quantity, size, warranty
- high contrast against the background
- consistent type scale across the suite

Avoid:

- decorative fonts
- thin type on busy backgrounds
- fake handwritten text unless the template explicitly needs Japanese/Rakuten style
- too many font weights
- text over product details

## Overlay Modes

Mode A: HTML/Pillow overlay

- best for repeatable PNG/JPG production
- good for exact copy, batch localization, font consistency

Mode B: PSDManifest overlay

- best for designer handoff and future editing
- keep text metadata even if current PSD writer rasterizes text

Mode C: model exact text

- only for short draft words/numbers
- always review visually

## Scoring Text

Fail if:

- final text is misspelled
- important text is unreadable at thumbnail size
- copy is unsupported by product truth
- text covers product details
- more than 3-4 visual text groups compete
- each suite image uses a different font language

