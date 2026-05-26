# Ecommerce Image Agent v0

This is the lightweight agent flow to run before building a full Agent Platform integration.

## Inputs

- product image
- listing/manufacturer text when available
- marketplace target
- suite size: 5-8 images
- optional clean template image or PSD
- brand/design system

## Files

- `ProductTruthPack`
- `EcommerceDesignMD`
- `SuitePlan`
- `TemplateCard`
- `PromptRecipe`
- `PSDManifest`
- `Scorecard`
- `ReviewLog`

## Loop

1. Extract product truth.
2. Analyze selling points from listing/source text.
3. Pick suite slots from `ecommerce_5_to_8_suite_plan`.
4. Pick TemplateCard per slot.
5. Compile prompts.
6. Generate candidates.
7. Score with 2-3 reviewer roles.
8. If below threshold, generate repair prompt and retry once.
9. If text is important, rebuild text with PSD/HTML/Pillow.
10. Write human review result back into next iteration.

## OpenDesign-Inspired Rules

- Treat Markdown files as the product contract.
- Treat visual style as `DESIGN.md`, not scattered prompt adjectives.
- Treat skills as self-contained workflows with examples and checklists.
- Show an early visible result before deep platform work.
- Run a self-critique before declaring an output usable.

## eMAG Detail Route

When `marketplace target = eMAG detail page`, route through:

- [emag_detail_banner_agent_v1.md](/Users/cc/Desktop/photo_show/workflow/agent_flows/emag_detail_banner_agent_v1.md)
- [emag_detail_module_catalog.v2.json](/Users/cc/Desktop/photo_show/workflow/emag_detail_module_catalog.v2.json)
- [EMAG_DETAIL_SCALE_CONTRACT.md](/Users/cc/Desktop/photo_show/workflow/EMAG_DETAIL_SCALE_CONTRACT.md)

Additional loop for eMAG:

1. Capture or load live PDP description HTML before designing the page.
2. Parse live dimensions, image hosts, tables, GIFs, and module order.
3. Choose one banner family: `premium_dark_brand_trust`, `product_tech_context`, or `official_blue_people_category`.
4. Generate background imagery separately from text whenever exact text matters.
5. Add text, chips, service cues, and specs through deterministic HTML/Pillow overlay.
6. Render an eMAG-compatible HTML snippet with single-column images and table-backed text bands.
7. Run `validate_emag_detail_html.py`; warnings are allowed only when documented in the review log.

Hard rules:

- Do not fabricate named reviews, dates, star ratings, platform guarantees, or service promises.
- Do not use official eMAG homepage assets directly in production unless reuse rights are confirmed; use them as style/reference material.
- Treat `1140px` as the current live desktop detail width; keep `800px` only as a fallback/mobile-safe export size.
