# eMAG Listing + Image Suite Direction

Date: 2026-05-17
Status: direction update after eMAG-specific research

## Verdict

The current research is enough to start building a skeleton and a single-SKU
prototype, but not enough to claim production quality.

Do both in parallel:

1. Start building the file-backed V1 production loop.
2. Continue targeted research only around platform-specific constraints and
   proven workflows.

The reason is practical: more broad research will not change the core
architecture. The remaining unknowns are platform profiles, template families,
and QA details.

## Why eMAG Changes The System Shape

Amazon experience is still useful, but eMAG should not be treated as "Amazon
with another export size".

eMAG documentation emphasizes consistency between:

- product name
- product images
- characteristics
- description
- package/accessory information
- safety / compliance information

Therefore, the system should generate listing text and image suite from the same
source of truth.

Do not build:

`image generator` and `listing generator` as separate flows.

Build:

`ProductUnderstandingPack -> ListingPlan + ImageSuitePlan`.

## eMAG Rules And Implications

### Main image

Research source:

- eMAG Marketplace errors guide
- eMAG product image documentation pages
- eMAG Marketplace API documentation

Main image implications:

- Product should be centered.
- Product should be visible from the front.
- Product should show the entire product.
- Product should cover more than 80% of the image.
- White background is expected for the main image.
- No other items or accessories should be added unless they are included and
  appropriate to the product package.
- Reflections/shadows and poor editing can trigger rejection.

System implication:

Main image should be a deterministic cleanup/compliance path:

`source product image -> background cleanup -> crop/center -> white background ->
size/file validation -> QA`.

It should not be a creative image-generation path by default.

### Secondary images

Research source:

- eMAG secondary image standards
- manual product creation guide
- rejected documentation guide

Secondary image implications:

- eMAG recommends at least 3-5 secondary images; another eMAG page recommends at
  least 4.
- Secondary images should provide details that the main image cannot highlight.
- They must present the same version of the product as the main image.
- Background can differ from white.
- Avoid other products, logos, watermarks, collages, excessive text, and
  language mismatch.

System implication:

Secondary images should be explanatory but conservative:

- angle/detail image
- material/texture close-up
- package/accessory image
- usage/scale image
- before/after or comparison only when factual and safe

Text-heavy infographic templates need stricter QA on eMAG than Ozon/WB.

### Listing text

Research source:

- eMAG manual product creation guide
- eMAG rejected documentation guide
- eMAG marketplace guide from eCommerce Today

Listing implications:

- Title should be descriptive, short, concrete.
- Recommended formula: product type + brand + model + 1-3 relevant attributes.
- Description must match title, characteristics, and images.
- Description should be grammatically correct in the target country language.
- Do not include price, stock, delivery, contact details, website, email, or
  promotional messages.
- Objective product qualities, contents, capacity, components, storage, usage,
  and package details are valid.
- Category characteristics are critical because many eMAG shoppers filter by
  attributes.

System implication:

The listing generator must be fact-gated:

- title
- short description
- long description
- bullet-like feature blocks
- category characteristics
- package contents
- safety/compliance notes

The image suite should consume the same approved facts.

## Updated Core Artifact

Replace the previous mental model:

`ProductTruthPack`

with a broader:

`ProductUnderstandingPack`

Minimum fields:

- product identity: type, brand, model, SKU, EAN if available
- source images: white background, side angle, detail, package, label
- visual truth: shape, color, material, visible parts, labels, accessories
- text truth: title source, manufacturer specs, package contents, claims
- marketplace facts: target platform, category, language, required attributes
- prohibited claims: unsupported numbers, promotions, superlatives
- approved claims: facts safe for listing and image copy
- buyer objections: size, compatibility, durability, use case, included items

Then fan out into:

- `ListingPlan`
- `ImageSuitePlan`
- `QAPlan`

## Updated VLM Fanout Flow

```text
Product images + product text
  -> VLM product understanding
  -> ProductUnderstandingPack
  -> marketplace validation
  -> ListingPlan
  -> ImageSuitePlan
  -> slot-specific prompts
  -> deterministic text overlays
  -> QA across listing + images
  -> export package
```

Important:

The VLM does not just describe the image. It reconciles image facts and listing
facts. If image and text disagree, the system should flag it before generation.

Example:

- Listing says black backpack.
- Product image shows beige backpack.
- System should block final generation or mark as human review required.

## eMAG Slot Taxonomy V1

Use Amazon as the base experience but adapt for eMAG.

### Required / default slots

1. Main image compliance
   - Purpose: pass platform validation and search/listing clarity.
   - Output: white background, centered, front, full product, >80%.

2. Alternate angle / full view
   - Purpose: show same product from another useful angle.
   - Text: none or very light.

3. Detail / material / component
   - Purpose: show what main image cannot show.
   - Text: short labels only, deterministic overlay if needed.

4. Package / included items
   - Purpose: reduce purchase uncertainty and returns.
   - Must match package contents in listing.

5. Usage / scale
   - Purpose: show size or realistic use.
   - Must avoid misleading scale.

6. Feature / benefit explanation
   - Purpose: visually explain one approved selling point.
   - Must avoid excessive text and unsupported claims.

### Optional slots

- comparison
- before/after
- instruction/how-to-use
- safety/warning visual
- size chart for fashion or dimensional categories

These optional slots should be category-gated.

## Platform Profiles

V1 needs separate marketplace profiles:

### AmazonProfile

- main image strict white background
- no text, border, watermark, extra graphics on main image
- secondary images can be more creative
- A/B test thinking from Amazon Manage Your Experiments should influence later
  evaluation

### eMAGProfile

- main image compliance and documentation validation first
- secondary images detail the same product/version
- listing fields and images must match
- attributes are high importance because shoppers filter heavily
- Romanian/Hungarian/Bulgarian language/localization matters later

### OzonWBProfile

- template adaptation and high-conversion card style
- 3:4 cards
- competitor/reference template analysis
- higher information density than Amazon/eMAG

## Research Still Needed

More broad search is not needed now. Continue only targeted research:

1. eMAG official documentation
   - main image standard
   - secondary image rules
   - description/title/characteristic validation
   - API upload/update behavior

2. eMAG competitor examples
   - top categories already relevant to our business
   - image count
   - main image style
   - secondary image style
   - text density
   - common rejection risks

3. Listing + image coupling
   - papers and production cases where MLLM generates listing text from product
     photos
   - attribute extraction from product images and OCR
   - cross-checking image facts against title/description/attributes

4. Template systems
   - how Canva/Supa/Fabric/PSD templates handle bulk product replacements
   - which UI pattern works best for non-designers

## Implementation Recommendation

Start building now, but limit scope:

### V1 prototype

- one SKU
- one eMAG category
- 1 main image + 4 secondary images
- listing text plan generated from the same `ProductUnderstandingPack`
- no full batch mode
- no free canvas
- deterministic text overlay only
- static review UI

### V1 output

- `product_understanding_pack.json`
- `listing_plan.json`
- `image_suite_plan.json`
- `template_selection.json`
- `compiled_prompts/`
- `text_overlay_plan.json`
- `qa_report.json`
- `export_manifest.json`
- final image previews

### QA gates

- product-image consistency
- image-listing consistency
- eMAG main image compliance
- secondary image same-product validation
- text language and promotion filter
- unsupported claim filter
- file size / dimensions / format

## Main Decision

The system should be framed as:

`AI Listing + Image Suite Production System`

not:

`AI Image Suite Generator`.

For marketplaces like eMAG, image generation and listing generation are one
combined documentation problem. The images persuade; the listing text and
attributes validate, rank, and reduce returns.
