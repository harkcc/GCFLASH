# eMAG Detail Banner Agent v1

日期：2026-05-24  
工作目录：`/Users/cc/Desktop/photo_show`

## Purpose

Generate eMAG detail-page banners and HTML modules from live listing evidence, not from a generic ad prompt.

## Current Stable Package

The active production direction is now:

- Agent core: `workflow/agent_core/emag_banner_html_agent_v1_1/`
- Display brand: `EXCITAT`
- Internal slug: `excitat`
- Test output: `output/emag_excitat_banner_html_agent_stable_v1/`
- Validator: `scripts/validate_excitat_banner_agent_outputs.py`

Stable loop:

```text
Plan / DesignSpec -> Generate or Composite -> Validate -> Repair -> Final Export
```

Do not use old display names (`EXIT`, `Excité`, `Exceity`, `EXITE`) in newly
generated visual modules or HTML. Older folders remain historical references.

This agent covers:

- brand trust GIF/static banner
- product-specific technical hero banner
- official eMAG promo-style people/category banner
- FAQ and buyer-question detail copy
- eMAG-safe HTML structure validation

## Required Inputs

- product URL or captured `description_inner.html`
- product title, brand, specs, package contents, source images
- seller/platform service facts if using delivery, return, guarantee, or support language
- optional category reviews/Q&A for FAQ
- optional official eMAG homepage assets as style references only

## Live Evidence Baseline

Captured case:

- shanggvu / BestPlaza vendor page: 46 product cards, 45 detail HTML pages captured, 347 detail images, 42 GIFs.
- Common brand intro banner: source `1200x480`, rendered about `1140x456`.
- Product-tech Qoltec case: first banner source `1280x366`, rendered about `1140x326`.
- Most pages are single-column image stacks; tables and inline styles appear in live detail HTML.
- eMAG official homepage references captured as `420x480` people/category cards and one `1200x225` promo strip.

Artifact paths:

- `references/user_cases/20260524_emag_shanggvu_detail_case_chrome/scrape_summary.json`
- `references/user_cases/20260524_emag_qoltec_d978tdybm/target_summary.json`
- `references/emag_official_assets/20260524_homepage_banners/official_asset_manifest.json`
- `experiments/20260524_emag_banner_css_validation/validation_report.json`

## Behavior Pattern Summary

1. The first visual block does not try to explain everything. It sets emotion and trust quickly.
2. Brand banners use black/dark backgrounds, large brand type, people or parcel scenes, and 3 service anchors.
3. Product-tech banners put product and usage context first, then 2-3 compatibility/safety claims.
4. Body modules use one idea per screen: pain scene, result, proof, spec, usage, FAQ.
5. FAQ blocks are valuable because they replace the buyer's internal doubt sequence before the buyer scrolls back to search for answers.
6. Color bands and repeated symbols are visual-order anchors, not decoration.
7. Complex visual layouts should be generated as images; HTML should stay simple and resilient.

## Banner Families

### A. Premium Dark Brand Trust

Use when the product or seller needs familiarity and credibility.

Prompt framework:

```text
Use case: ads-marketing
Asset type: eMAG detail-page brand trust banner, 1200x480.
Scene: premium black/deep purple ecommerce background, subtle dotted or light trail texture.
Subject: friendly European adults with a plain unbranded parcel, or a clean marketplace package scene.
Composition: left 45-55% reserved for deterministic text overlay; right side has people/package/product context.
Mood: warm, premium, reliable, not luxury fashion.
Text policy: no readable text, no logo, no discount badge, no trademarked marketplace mark in the generated background.
Post-process: add brand, slogan, and up to three service cues with deterministic overlay.
Avoid: fake eMAG logo, unsupported platform guarantees, model-written small text, clutter.
```

Recommended output:

- source: `1200x480`
- rendered test: `1140x456`
- HTML: `<p style="text-align:center;"><img width="1140" ...></p>`
- GIF allowed if it adds brand/story motion; static first frame must still work.

### B. Product Tech Context

Use for EV chargers, tools, electronics, measurement devices, safety devices.

Prompt framework:

```text
Use case: ads-marketing
Asset type: eMAG detail-page product technical hero, 1280x366.
Scene: deep navy or purple technical background, light grid, subtle energy lines.
Subject: product cutout or realistic product render centered; usage context on the right.
Composition: left has 2-3 deterministic feature chips; center product; right buyer-result phrase.
Mood: precise, safe, high-confidence.
Text policy: no generated text except large abstract UI shapes; overlay exact copy later.
Avoid: fake certifications, dense spec tables, unsupported compatibility claims.
```

Recommended output:

- source: `1280x366` or `1400x400`
- rendered test: `1140x326`
- HTML: one centered image; specs below in table or question-answer block.

### C. Official Blue People/Category

Use when the product benefits from app-like, category-rich energy.

Prompt framework:

```text
Use case: ads-marketing
Asset type: eMAG promo-inspired detail banner, 1200x480.
Scene: bright marketplace blue background, circular motion lines, floating rounded category tiles.
Subject: one smiling person plus product/category objects.
Composition: left has hook area; right has person and 2-3 product tiles.
Mood: energetic, friendly, app-first, mainstream retail.
Text policy: no official eMAG logo or discount text unless rights and campaign facts are confirmed.
Avoid: overcrowded floating products, unreadable text, direct copying of official assets for commercial deployment.
```

Recommended output:

- source: `1200x480`
- rendered test: `1140x456`
- use official homepage captures as style references only.

## Detail Copy SOP

1. Start with the buyer result: what improves after purchase.
2. Name the annoying scene the buyer is trying to escape.
3. Map each feature to one practical benefit.
4. Put specs after the result and scene modules.
5. Use FAQ to answer doubts that would otherwise make the buyer leave the page.
6. Use real reviews/Q&A when available; otherwise label the module as common questions, not testimonials.
7. Close with support/process language only when backed by actual seller or platform facts.

Romanian copy principle:

- Prefer direct result language: `Rezultatul: ...`, `Scapi de ...`, `Potrivit pentru ...`
- Avoid price, discount, unsupported shipping, unsupported warranty, and contact wording.

## HTML Format SOP

Allowed core:

- `p`, `h1`, `h2`, `h3`, `strong`, `br`, `img`, `ul`, `li`

Live-proven gray zone:

- `table`, `tr`, `td`, `div`, `blockquote`, inline `style`, GIF image

Default pattern:

```html
<p style="text-align:center;">
  <img src="..." alt="..." width="1140" />
</p>
```

Use table-backed color bands only for simple text grouping:

```html
<table width="1140" cellpadding="0" cellspacing="0" style="background-color:#eef8f0;">
  <tr>
    <td style="padding:32px;">
      <h3>...</h3>
      <p><strong>...</strong><br />...</p>
    </td>
  </tr>
</table>
```

## Validation Checklist

- Run `python3 scripts/validate_emag_detail_html.py <snippet> --out <report.json>`.
- `status` must be `pass`.
- GIF, tables, external hosts, and 1140-width images can remain warnings if the review log explains why.
- Open the generated banners and check text does not clip at `1200x480`, `1280x366`, and rendered `1140` widths.
- Any service promise must trace to product/seller/platform evidence.

## Current Test Outputs

- `output/emag_banner_generation_tests/01_brand_trust_dark_package_1200x480.png`
- `output/emag_banner_generation_tests/02_ev_charger_product_tech_1280x366.png`
- `output/emag_banner_generation_tests/03_official_people_category_style_1200x480.png`
- `output/emag_banner_generation_tests/04_ai_brand_trust_background_overlay_1200x480.png`
- `references/emag_official_assets/20260524_homepage_banners/official_asset_contact_sheet.png`

Regenerate:

```bash
python3 scripts/build_emag_banner_test_assets.py
```
