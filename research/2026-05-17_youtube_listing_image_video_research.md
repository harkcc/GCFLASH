# YouTube Research: Marketplace Listing Image Suites

Date: 2026-05-17
Status: first-pass video source screening

## Why YouTube Should Be Included

YouTube is worth adding to the research stack because many seller workflows are
shown as screen recordings rather than written as blogs or open-source repos.
This is especially true for Amazon listing images, Ozon/Wildberries product
cards, Canva/Photoshop templates, and AI product photography tools.

Use YouTube for:

- discovering practical seller workflows
- extracting slot taxonomy and image-type names
- seeing how tools guide non-designers
- finding repeated pain points around product consistency, text, and templates
- identifying candidate UI patterns for our production workspace

Do not treat YouTube videos as final technical authority. They are workflow and
market signal references. Official marketplace rules, open-source projects, and
local experiments still need to validate implementation choices.

## Amazon Listing Image / Suite Videos

### 20 Types of Amazon Images That Convert MORE SALES

Source: https://www.youtube.com/watch?v=ioUgFhvgA_U

Why it matters:

This is one of the most useful slot-taxonomy references. The video description
and chapters list practical Amazon image types:

- multi-use callout
- scannable infographic
- main image props
- show packaging
- show everything
- show variations
- add color
- optimize for mobile
- zoom into details
- us vs them
- address sticking points
- size reference image
- show, do not tell
- benefits over features
- before and after
- show your customers
- instructional images
- 3D rendered images
- custom ad images
- leverage AI

Reusable idea:

Use this as a secondary slot taxonomy map. Our `SlotPlan` should not only be
hero/lifestyle/infographic; it should encode buyer objections and conversion
jobs such as "address sticking points", "size reference", and "show packaging".

### Amazon AI Studio: Create Product Photos & Videos in Minutes

Source: https://www.youtube.com/watch?v=KDI73nLbYk4

Why it matters:

This is seller-education style content around Amazon AI Studio. The visible
positioning is professional-quality product images and videos in minutes, lower
cost than traditional production, and scaled visual asset production.

Reusable idea:

Amazon itself is moving toward an agentic creative surface where sellers provide
product context and AI generates creative variations. We should expect sellers
to understand "AI-assisted listing creative" as a normal workflow, but our
differentiation should be control, templates, QA, and cross-platform exports.

### AI got wild... I redesigned Coca-Cola's Amazon Listing in 7 min

Source: https://www.youtube.com/watch?v=4Kf2yfTcLNA

Why it matters:

Good reference for quick AI redesign storytelling. Useful for UI pacing and the
"fast visible result" expectation.

Caveat:

Not a production-quality system reference. It should not drive architecture.

### Nano Banana Pro for Product Photography

Source: https://www.youtube.com/watch?v=12pQ0W2bCDE

Why it matters:

Useful for understanding current YouTube creator workflows around Nano Banana
style product photography.

Reusable idea:

Video creators are already framing product photography as a guided workflow.
This supports using a step-by-step UI instead of exposing raw prompts.

### How To Create Product Photos For Amazon Listings

Source: https://www.youtube.com/watch?v=u6qWNAnYyis

Why it matters:

Traditional product-photo tutorials still matter because they define what AI
should imitate: clean setup, white background, lighting, product scale, and
Canva/GIMP cleanup.

Reusable idea:

Our system should keep a "main image cleanup/compliance" step separate from
creative AI generation.

## Ozon / Wildberries / Marketplace Product Card Videos

### Product Card Design on Wildberries with AI

Source: https://www.youtube.com/watch?v=AlnHcJvrWJg

Why it matters:

The description explicitly describes a seller-manager workflow:

- create selling infographics without design skills
- copy competitor design through ChatGPT
- adapt ready-made templates on Supa
- remove background
- edit text and layout
- increase marketplace card conversion

Reusable idea:

For Ozon/WB-style marketplaces, the strongest workflow is not "generate from
scratch"; it is "competitor/reference analysis + ready template adaptation +
text/layout editing". This reinforces `TemplateCard` and `template_extractor`.

### Ozon Product Card Through Neural Network: Full Guide

Source: https://www.youtube.com/watch?v=67t9QlI8pkg

Why it matters:

Direct Ozon seller workflow reference. Add to the watchlist for detailed
Russian marketplace-specific steps.

Reusable idea:

Ozon should have its own high-conversion card path rather than inheriting Amazon
white-background logic.

### Product Card in 3 Minutes in ChatGPT

Source: https://www.youtube.com/watch?v=19SQhBg9Xz4

Why it matters:

Represents the "fast no-designer card generation" trend for WB/Ozon.

Reusable idea:

Our UI should make the first card appear quickly, then move into controlled
review and repair.

### Nano Banana Pro for Ozon and Wildberries 2026

Source: https://www.youtube.com/watch?v=euQGgJyhGDk

Why it matters:

Relevant for current Russian seller adoption of Nano Banana-style image models.

Reusable idea:

Treat model choice as replaceable. The real product value is the marketplace
workflow, template system, and review loop.

### Infographic Styles for Wildberries and Ozon

Source: https://www.youtube.com/watch?v=B6JH7250Uzc

Why it matters:

Useful style reference for marketplace card templates and Ozon/WB visual
patterns.

Reusable idea:

Extract template families and visual density rules for Ozon/WB.

## Product Consistency / ComfyUI / Batch Variation Videos

### One Image - 6 Consistent Shots | Nano Banana + Gemini VLM in ComfyUI

Source: https://www.youtube.com/watch?v=587IOqfqMMw

Why it matters:

The workflow described in the video metadata is directly relevant:

- one reference image as input
- Gemini VLM analyzes the subject
- writes 6 distinct prompts
- varies camera angle, shot type, and framing
- Nano Banana Edit renders 6 variations in one batch
- positioned for product photography, ecommerce listings, and marketing assets

Reusable idea:

This confirms our "one product image -> multiple controlled slot prompts" flow.
The model stack can be interchangeable, but the orchestration pattern is strong:
VLM analysis -> prompt fanout -> consistent batch generation.

### ComfyUI Advanced Tutorial 11 - Product Photography V1

Source: https://www.youtube.com/watch?v=o3F3gCXIv4U

Why it matters:

Reference for product photography workflows in ComfyUI.

Reusable idea:

Use only as a specialist pipeline, not as the default MVP path.

### ComfyUI Advanced Tutorial 13 - Product Photography V2

Source: https://www.youtube.com/watch?v=rDGonsH1C8Q

Why it matters:

Follow-up product photography workflow. Add to watchlist for product placement,
relight, and consistency techniques.

### Relight and Preserve Any Detail with Stable Diffusion

Source: https://www.youtube.com/watch?v=3N0vvmAoKJA

Why it matters:

Relevant to product consistency and detail preservation.

Reusable idea:

Preservation and relighting should be separated from final text/template
rendering.

## Canva / Photoshop / Template Videos

### Easy Guide to Amazon Product Images - Pre-Built Templates for All Amazon Images

Source: https://www.youtube.com/watch?v=Byp-3Yduc6I

Why it matters:

This aligns strongly with our prebuilt-system direction. It reinforces that
non-designers want ready template packs rather than blank-canvas design.

Reusable idea:

V1 should ship template presets per image type.

### How to Design Amazon Listing Images with Canva

Source: https://www.youtube.com/watch?v=K4CMdBiARfk

Why it matters:

Useful practical reference for how sellers use templates and manual editing.

Reusable idea:

Precision editing should feel like Canva-style slot editing, not raw Photoshop.

### Bulk Edit Product Photos With Canva

Source: https://www.youtube.com/watch?v=PV49jL6rYHg

Why it matters:

Relevant for the later batch mode. Sellers already understand bulk photo editing
through Canva-like workflows.

Reusable idea:

Batch mode should reuse the same template slots and allow bulk replacement of
product images, copy, and badges.

### Amazon Listing Infographic Design + Canva Template

Source: https://www.youtube.com/watch?v=zLYUWWdvmLo

Why it matters:

Template-pack and infographic style reference.

Reusable idea:

Good source to classify common Amazon infographic blocks: headline, product
cutout, benefit callouts, icon rows, detail zoom, trust footer.

## Design Implications For Our System

### 1. Add YouTube to ongoing research, but classify it correctly

YouTube should be used for:

- practical workflows
- seller language
- slot taxonomy
- UI pacing
- visual examples
- candidate template families

It should not be used as:

- marketplace compliance authority
- proof that a technical method is reliable
- final architecture source

### 2. Reinforce the prebuilt-system direction

Most useful videos converge on the same pattern:

1. Start from product photo.
2. Remove/clean background.
3. Choose marketplace image type or template.
4. Generate or adapt layout.
5. Edit text manually or with template tools.
6. Export platform-ready image.

This matches our intended:

`ProductTruthPack -> SlotPlan -> TemplateCard -> Generation -> DeterministicOverlay -> QA -> Export`.

### 3. Expand SlotPlan taxonomy

Add or map these slot types into our catalog:

- scannable infographic
- packaging shot
- show everything / included items
- variation comparison
- mobile-readable benefit card
- zoom/detail card
- us-vs-them comparison
- objection/sticking-point card
- size reference card
- before/after
- instructional/how-to-use
- customer/user scene

### 4. Ozon/WB needs template adaptation, not Amazon cloning

The Russian marketplace videos emphasize:

- competitor card analysis
- template adaptation
- fast text/layout editing
- high information density
- neural-network support for non-designers

So Ozon/WB mode should prioritize:

- `OzonHighConversionMainCard`
- reference-template extraction
- 3:4 card support
- Russian text overlay
- visual density controls

### 5. Product consistency videos support VLM fanout

The ComfyUI/Nano Banana videos support:

- one reference image
- VLM analysis
- prompt fanout
- consistent multi-shot generation

This is a strong fit for our Agent runtime. The image model can change, but the
workflow should remain:

`analyze product -> generate slot-specific prompts -> batch render -> QA`.

## Next Watchlist

Prioritize watching these end-to-end next:

1. https://www.youtube.com/watch?v=ioUgFhvgA_U
2. https://www.youtube.com/watch?v=AlnHcJvrWJg
3. https://www.youtube.com/watch?v=587IOqfqMMw
4. https://www.youtube.com/watch?v=KDI73nLbYk4
5. https://www.youtube.com/watch?v=Byp-3Yduc6I
6. https://www.youtube.com/watch?v=67t9QlI8pkg

The first pass used YouTube search pages and video metadata/descriptions. A
second pass should watch these videos in full and extract screenshots, exact
steps, tool names, and template categories.
