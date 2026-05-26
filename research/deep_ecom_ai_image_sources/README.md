# Deep Ecommerce AI Image Source Collection

Started: 2026-05-22

Purpose: collect raw, traceable sources for batch AI image generation and ecommerce product/listing image workflows. This folder is a data ledger first, not a narrative research report.

## Current checkpoint

Last updated: 2026-05-22/23 continuation with n8n creator/template indexes, Bilibili PS/Coze/Nano Banana workflow capture queues, GPT Image 2 flat-output-to-editable-asset discussions and AI+Photoshop product photography community signals.

- Source rows: 931 (`S001`-`S931`)
- Reusable method rows: 239 (`M001`-`M239`)
- Website case rows: 650 (`W001`-`W650`)
- Main new coverage in the latest pass: n8n creator and template-index pages for Nano Banana product creative, UGC ads and product URL ad workflows; GitHub/course indexes for Shopify product video and Nano Banana Pro infographics; Bilibili PS AI plugin and Coze/Nano Banana 2 ecommerce main/detail workflow capture queues; Reddit threads on GPT Image 2 to editable PPTX/SVG/Figma conversion, AI scene plus Photoshop product compositing and platform-formatting product photo editors.
- `needs_watch` means the video/page has been discovered and metadata recorded, but exact prompts, screenshots, and step-by-step workflow still need deeper viewing.
- `verified_snippet` means a search/index snippet or API metadata was sufficient to record the source, but not enough for final claims.

## Files

- `sources.csv`: source-level ledger. One row per website/video/thread/project/tool/case.
- `methods.csv`: method/framework-level ledger. One row per reusable workflow pattern.
- `cases.md`: richer notes for notable website/video/community cases.
- `queries.md`: search queries already run, to avoid repeating shallow searches.
- `raw_youtube/`: downloaded subtitle and metadata evidence for selected YouTube sources. This folder intentionally stores transcripts/metadata only, not video files.
- `website_cases.csv`: structured cross-site/cross-tool case ledger for websites, platform tools, Product Hunt tools, n8n templates, and community-backed tool cases.
- `analysis_report_draft.md`: living synthesis report over the current evidence base. This is not final until the full active goal is complete.
- `analysis_report.md`: cleaner working report intended to become the final deliverable after the full two-hour-plus collection and verification window is satisfied.

## Source fields

- `id`: stable local source id.
- `platform`: YouTube, Reddit, HN, X, Bilibili, GitHub, Gist, Blog, Tool, SellerCommunity, Docs, Marketplace.
- `source_type`: video, thread, repo, gist, blog, docs, tool_site, case_study, prompt_library, marketplace_rule.
- `title`
- `url`
- `published_or_updated`
- `models`: Nano Banana 2, GPT Image 2, Midjourney V7/V8, FLUX, Seedream, Qwen, etc.
- `marketplaces`: Amazon, Ozon, Wildberries, Shopify, Etsy, TikTok Shop, general ecommerce.
- `batch_signal`: none, manual_batch, API_batch, catalog_batch, queue_pipeline, template_batch.
- `product_fidelity_signal`: none, product_reference, cutout_composite, mask/detail_transfer, QA_reroll, marketplace_compliance.
- `method_tags`: short tags such as product_truth_pack, reference_image, prompt_compiler, deterministic_overlay, frame_template, relight, background_replace.
- `case_notes`: factual notes from the source.
- `status`: seed, verified, needs_deep_read, low_signal, excluded_old.

## Status conventions added during continuation

- `verified_transcript`: YouTube subtitle transcript was captured locally and summarized into `cases.md`.
- `verified_page`: page content was opened/read directly enough to support the notes.
- `verified_api`: API metadata was queried directly, typically GitHub search/repo metadata.
- `verified_snippet`: search result or index snippet was useful enough for source discovery, but not enough for final claims.

## Website case fields

- `case_id`, `source_ids`, `website_or_tool`, `url`
- `case_type`, `models_or_stack`, `marketplaces`
- `input_assets`, `workflow_summary`, `batch_or_export`
- `product_truth_or_qa`, `notes`, `status`
