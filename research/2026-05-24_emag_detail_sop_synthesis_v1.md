# eMAG Detail SOP Synthesis v1

Date: 2026-05-24

This note consolidates three local seller/reference lines and current public PDP guidance into one execution order for the eMAG HTML Detail Agent.

## 1. Local Evidence Summary

### A. Excitat / cangswjp

Local evidence:

- `research/2026-05-21_emag_excitat_full_teardown.md`
- `output/emag_detail_html_live_batch/summary.md`
- `output/emag_detail_html_live_batch/constraints_summary.md`

What it proves:

- The strong seller pattern is not a single image. It is a repeatable suite: hero, feature proof, detail proof, parameter/compatibility, package, scene/steps.
- Detail pages are mobile-first single-column flows.
- In the 30 live detail HTML sample, all products have one image per row and all products include GIF.
- The practical HTML pattern is simple: centered image, short text block, blockquote, table, FAQ, GIF.

SOP takeaway:

- Use one visual module per buyer question.
- Do not write dense paragraphs before product proof.
- Use GIF when it explains action, installation, product use, or brand familiarity.

### B. BestPlaza / shanggvu

Local evidence:

- `research/2026-05-24_emag_bestplaza_banner_parse_and_sop.md`
- `research/2026-05-24_emag_shanggvu_bestplaza_detail_upgrade_plan.md`
- `references/user_cases/20260524_emag_shanggvu_detail_case_chrome/`

What it proves:

- 46 product cards were collected; 45 detail HTML pages were captured.
- 347 detail images and 42 GIFs were captured.
- 40/45 captured detail pages use tables.
- Brand trust banner size is typically 1200x480 rendered near 1140x456.
- The black brand-trust banner works because it combines premium dark background, people, package, and only three service cues.

SOP takeaway:

- Brand trust is a module system, not repeated logo placement.
- Service claims, return claims, warranty, seller rating, and review cards require evidence.
- If review evidence is missing, use FAQ or buyer-question framing instead of fake testimonial.

### C. Qoltec EV charger

Local evidence:

- `references/user_cases/20260524_emag_qoltec_d978tdybm/`
- `output/emag_banner_generation_tests/02_ev_charger_product_tech_rendered_1140x326.png`

What it proves:

- Technical products benefit from a product-tech hero: product cutout, technical background, usage context, and a small set of compatibility/safety proof points.
- A 1280x366 source banner can render as about 1140x326 in the eMAG detail area.

SOP takeaway:

- For technical products, first-screen information should answer fit, control, and safety before emotional copy.
- Specs table should confirm after visual context, not act as the page opening.

## 2. External PDP Guidance Used

Source strength:

- Google Merchant Center landing page requirements: strong compliance-style source.
- Shopify product page guidance: platform/ecommerce practice source.
- Nielsen Norman Group mobile image guidance: UX research source.

Extracted rules:

- Product page content must clearly match the product, images, title, description, variant, and language expected by the user.
- Mobile pages must work cleanly on mobile devices.
- High-quality product images and lifestyle/use images should help buyers imagine real use.
- Product descriptions should be simple, benefit-focused, and scannable.
- Reviews, UGC, and ratings build trust, but must be real.
- FAQ and live support are separate from reviews; FAQ answers specific objections, reviews provide social proof.
- Decorative mobile images should be avoided; every image should add information.

## 3. Component Added: `first_screen_anchor_triplet`

Files:

- `workflow/emag_detail_module_catalog.v2.json`
- `workflow/template_cards/FirstScreenAnchorTriplet.json`
- `output/emag_html_detail_agent_v1_3_mobile_reference/component_anchor_triplet_variants.html`

Purpose:

- This component sits immediately after the banner.
- It turns the first scroll screen into three clear decision anchors.
- It is not a decorative card group and not internal SOP copy.

Visual default:

- Three stacked full-width mobile cards.
- Light background.
- Colored left rail.
- Bold `01 / 02 / 03` title.
- One short support sentence.

Content rule:

- Exactly three anchors.
- Each anchor must map to one buyer decision role.
- The three anchors must set up the next modules.

Recommended anchors by product type:

| Product type | Anchor 1 | Anchor 2 | Anchor 3 |
|---|---|---|---|
| EV / technical | Compatibility | Control | Safety / proof |
| Tool / auto | Fit | Strength / material | Usage scene |
| Home cleaning | Pain scene | Portability | Accessory purpose |
| Beauty | Comfort | Material/contact | Routine/cleaning |
| Baby | Safety | Simple steps | Hygiene |
| Coffee/kitchen | Result | Ease of use | Cleaning |
| Brand trust | Familiarity | Evidence | Service/support |

Bad use:

- Internal planning copy like "specs come after image".
- Long paragraphs.
- Unsupported service claims.
- More than three anchors.

## 4. Other Comfortable Micro-Components

These are safe candidates for the component library if the validator allows the tags/styles.

| Component | Best position | Role | Notes |
|---|---|---|---|
| `first_screen_anchor_triplet` | after banner | first 3 decision anchors | added in v1 |
| `soft_number_blocks` | after banner or before specs | calmer sequential explanation | good for baby/beauty |
| `question_led_blockquotes` | before FAQ or proof section | buyer question -> short answer | useful when product requires explanation |
| `color_band_feature_stack` | after first product image | feature -> benefit group | already in catalog |
| `spec_table_clean` | after proof modules | rational confirmation | table gray-zone but live-proven |
| `package_contents_table` | after specs | what arrives in box | especially useful for kits/accessories |
| `review_evidence_board` | after usage/proof or before trust closer | real social proof | must require real review data |
| `seller_signal_strip` | near trust closer | seller rating/service facts | optional, only with source evidence |
| `motion_gif_banner` | top or late trust section | brand/action proof | GIF accepted in live samples |

## 5. Seller Rating Policy

Seller好评率 can be useful, but it is a trust claim and must be evidence-gated.

Use only when input includes:

- seller name
- rating value
- rating count or source timestamp
- source URL or captured DOM evidence

Placement:

- Not in the first three anchors unless seller trust is the primary buyer concern.
- Usually after review evidence or before the closing confidence block.

Fallback:

- If there is no evidence, use neutral support-process copy.
- Do not invent percentages, badges, "top seller", "guarantee", "free return", or "24 months" statements.

## 6. Unified SOP Order

### Step 0. Input audit

Create `input_audit.json`.

Check:

- product type
- title/language
- specs
- product images
- package contents
- review/Q&A availability
- seller/service evidence
- available banner/GIF/reference assets

### Step 1. ProductTruthPack

Create `product_truth_pack.json`.

Fields:

- core result
- buyer pain scenes
- features
- benefits
- specs
- usage scenes
- package contents
- constraints
- evidence references

Rule:

- Strong claims must come from this pack.
- Unsupported angles stay as "angle", not "fact".

### Step 2. Buyer-question route

Create `buyer_question_map.json`.

Default question order:

1. What result do I get?
2. Does it fit my situation?
3. What pain scene does it solve?
4. Why should I believe the feature?
5. How do I use it?
6. What exactly do I receive?
7. What specs must I verify?
8. What objections remain?
9. Can I trust the seller/brand?

### Step 3. Template family selection

Create `module_plan.json`.

Recommended chains:

- Technical / EV:
  - `product_tech_hero -> first_screen_anchor_triplet -> product_proof_image -> feature_proof_band -> specs_table -> install_or_usage_scene -> faq_objection -> review_evidence_if_real -> trust_close`
- Home cleaning:
  - `pain_or_brand_banner -> first_screen_anchor_triplet -> usage_scene_image -> feature_benefit_band -> accessory_board -> specs_table -> package_table -> faq -> review_evidence_if_real -> trust_close`
- Beauty:
  - `people_category_banner -> first_screen_anchor_triplet -> model_use_image -> comfort_safety_band -> routine_steps -> specs -> faq -> review_evidence_if_real -> trust_close`
- Baby:
  - `soft_people_banner -> first_screen_anchor_triplet -> safety_band -> routine_image -> hygiene_image -> specs -> faq -> trust_close`
- Coffee / kitchen:
  - `lifestyle_result_banner -> first_screen_anchor_triplet -> result_scene_image -> feature_proof_band -> cleaning_board -> specs -> faq -> review_evidence_if_real -> trust_close`
- Brand trust:
  - `brand_trust_banner -> first_screen_anchor_triplet -> people_package_image -> service_evidence_band -> product_range_board -> review_evidence_if_real -> faq -> trust_close`

### Step 4. Banner and image jobs

Create `image_requirements.json`.

Rules:

- Banner can be direct asset if already generated.
- Product/detail images stay as explicit requirements until the image agent runs.
- Text in generated images should be avoided unless deterministic overlay handles it.
- GIF is allowed for brand motion, product action, installation, before/after, or usage proof.

### Step 5. HTML rendering

Render `detail.html`.

Preferred HTML:

- centered image: `p + img width=1140`
- simple text: `h2`, `p`, `strong`, `br`, `ul`, `li`
- gray-zone but live-proven: `table`, `tr`, `td`, `blockquote`, `div`, inline style, GIF
- no JS, no iframe, no forms, no external CSS

### Step 6. Review and FAQ separation

FAQ:

- Answers buyer objections.
- Can come from Q&A, category questions, or ProductTruthPack.
- Must not use fake customer identity.

Review/testimonial:

- Uses real review data only.
- Can include star ratings, names, dates only if sourced.
- If data is missing, omit or leave as pending evidence slot.

### Step 7. Trust closer

Use one of:

- brand trust banner
- seller signal strip
- neutral support process
- black/gold closing confidence block

Evidence gate:

- seller rating, return, delivery, warranty, platform claims require source evidence.

### Step 8. Validation

Create `validation_report.json`.

Must check:

- tag policy
- mobile width / no overflow
- GIF policy
- image path and dimensions
- claim evidence
- review evidence
- seller/service evidence
- module chain
- text density

### Step 9. ReviewLog

Create `review_log.md`.

Record:

- selected chain
- why each module exists
- which claims are factual
- which slots are pending image generation
- which review/seller signals are omitted due to missing evidence
- accepted validator warnings

## 7. Final Rule

The page should feel like:

`one mobile scroll, one buyer question at a time`

not:

`a decorative landing page pasted into a marketplace description`.

