# Product Image Agent MVP Notes

Date: 2026-05-21

Run folder:

`experiments/20260521_emag_style_agent_mvp/sandisk_ssd_public_api_mvp`

## Goal

Validate whether the newly extracted eMAG / Excitat image logic can be turned
into an Agent-style generation loop on a fresh product that was not part of the
Excitat reference set.

## Product Source

For this first controlled run, the product source is a public product API:

- API: `https://fakestoreapi.com/products/10`
- Product: `SanDisk SSD PLUS 1TB Internal SSD - SATA III 6 Gb/s`
- Source image: white-background product image from the API response

Aoxia was not used in this run because the local `photo_show` workspace does not
contain an Aoxia credential/config. Prior project memory indicates the available
Aoxia path is a market-phase supplier search REST endpoint:

`/ai.select.provider.search/1.0`

with a body like:

```json
{
  "intention": "SEARCH_OFFER",
  "query": "satin hair bonnet",
  "language": "en"
}
```

That path can become a `source_adapter`, but this MVP uses a public API so the
visual loop can be tested without auth or anti-bot setup.

## Open-Source Workflow References Checked

These references reinforce the same architecture:

| Source | Useful Pattern |
|---|---|
| ComfyUI BiRefNet background-removal workflow (`https://docs.comfy.org/tutorials/utility/remove-background-birefnet`) | Load image, remove background, output RGBA image and mask for downstream compositing. |
| `d3cker/comfyui_remove_background` (`https://github.com/d3cker/comfyui_remove_background`) | A ComfyUI custom node wraps `rembg` + Pillow and outputs image plus alpha mask; this maps directly to our cutout stage. |
| OpenTryOn (`https://github.com/tryonlabs/opentryon`) | Uses APIs/SDKs/models for photoshoots and mentions template-based prompt generation; useful for parameterized prompt/shot planning. |
| Existing `photo_show` docs | The local architecture already points to `ProductTruthPack -> TemplateCard -> prompt/render -> scoring -> repair`. |

The practical takeaway: the core open-source pattern is not "one prompt makes a
finished product suite." It is:

`source product -> cutout/mask -> template/shot plan -> generated or composed scene -> deterministic text/layout -> score -> repair`

## Implemented MVP Loop

Script:

`scripts/run_emag_style_agent_mvp.py`

Artifacts:

- `inputs/source_product_api.json`
- `inputs/source_product.png`
- `inputs/product_cutout.png`
- `inputs/product_truth_pack.json`
- `v1/*.jpg`
- `v2/*.jpg`
- `v3/*.jpg`
- `v1_contact_sheet.jpg`
- `v2_contact_sheet.jpg`
- `final_contact_sheet.jpg`
- `qa_report.json`
- `run_report.md`

## Iterations

| Iteration | Score | Result |
|---|---:|---|
| v1 | 76 | first structural attempt; too much text and weaker hierarchy |
| v2 | 88 | cleaner and passable, but hero still too quiet |
| v3 | 91 | best local-render candidate; stronger hero and better slot order |

The score is a deterministic proxy based on the project scorecard. It is not a
VLM product-fidelity review.

## Final Suite Structure

The v3 suite uses the new `emag_excitat_reference_6_suite`:

1. Hero / search-card main image
2. Feature proof card
3. Detail proof card
4. Product parameters card
5. Package contents card
6. Usage scenarios card

This matches the user's expected production shape: one main image plus four to
eight secondary images.

## Self Review

### What already works

- The visual language is recognizably derived from the Excitat/eMAG reference:
  corner brand zone, cyan frame, dark tech background, numeric badge, feature
  cards, parameter blocks, package card, usage card.
- It is cleaner than many reference examples in text density and slot
  separation.
- The output is repeatable from structured inputs, not hand-made one-off art.
- Text is deterministic overlay, which is safer than asking the image model to
  render marketplace copy.

### What is still below production quality

- Only one source product image was available; real suites need multiple angles,
  package images, detail crops, and accessories.
- Package contents and warranty are mocked; production must fact-gate these.
- No VLM review has checked product identity, parts, and claim truth yet.
- The local renderer is good enough for structure but not enough for final
  premium design polish.
- Romanian copy/localization is not implemented in this run.

## Agent Flow To Build Next

```text
SourceAdapter
  -> ProductTruthPackBuilder
  -> CategoryPaletteSelector
  -> SuiteTemplateSelector
  -> ShotPlanCompiler
  -> RenderRouter
      - local deterministic template render
      - optional image-model background generation
      - optional PSD/Fabric assembly
  -> QAReview
      - deterministic checks
      - VLM product-fidelity review
      - text/copy/language review
  -> RepairPlanner
  -> limited rerun
  -> final export manifest
```

## Adapter Boundary

The current script uses:

`public_fakestore_api`

The same interface should support:

- `aoxia_supplier_search`
- `excitat_internal_api`
- `emag_product_page`
- `amazon_serpapi_product`
- `manual_upload`

The important point is that generation should not care where the product came
from. It should consume a normalized `ProductTruthPack`.

## Next Controlled Experiment

Run the same Agent flow on one product from each visual family:

1. small appliance
2. electronics accessory
3. tool / auto
4. toy / gift
5. backpack / storage

For each product, limit to:

- 3 iterations maximum
- 1 final contact sheet
- one `qa_report.json`
- one human review note

This keeps cost controlled while building a real template benchmark.
