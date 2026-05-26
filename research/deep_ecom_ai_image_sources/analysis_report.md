# Batch AI Ecommerce Image Generation Report

Updated: 2026-05-22

Status: working report. The collection goal is still active because the requested two-hour collection window has not been reached yet.

## Evidence Base

- Source ledger: `S001`-`S931` in `sources.csv`
- Method ledger: `M001`-`M239` in `methods.csv`
- Website/tool/platform cases: `W001`-`W650` in `website_cases.csv`
- Local evidence: YouTube transcripts in `raw_youtube/`, extracted PDF text in `raw_docs/`
- Notes and query audit: `cases.md`, `queries.md`

## Executive Takeaway

The practical market direction is not pure text-to-image product generation. The strongest workflows are product-reference-first systems that combine:

1. real product photo or cutout as truth anchor;
2. structured product facts, slot intent and brand rules;
3. model routing by task;
4. QA gates for product, text, policy and channel;
5. deterministic layout/export where exact claims matter;
6. post-upload monitoring on Amazon/marketplace feeds.

The recurring failure is product truth: labels, quantities, materials, dimensions, accessories, logos and texture drift. The recurring business need is speed at SKU/catalog scale. The best systems therefore treat AI as a fast creative expansion layer, not as the only source of truth.

## Current Model Roles

### GPT Image 2 / Image 2

Best current fit:

- text-heavy ecommerce cards, infographics and product callouts;
- product extraction/mockup prep where label and edge fidelity matter;
- API workflows with preflight validation, cost estimates and run ledgers;
- Shopify/catalog pipelines and structured prompt templates.

Observed constraints:

- wrapper claims must be checked against official OpenAI docs;
- product detail preservation still needs reference images and OCR/product QA;
- official parameters and snapshot behavior should be logged per run.

Strongest evidence clusters: `S230-S231`, `S238-S241`, `S288`, `S318`, `S327-S331`, `S352-S357`, `S360-S361`, `S365`, `S367`, `S370`, `S371`, `S374-S383`, `S547-S548`, `S553`, `S559`, `S568-S570`, `S572`, `S576`, `S578-S582`, `S590`, `S594-S597`, `S606`, `S610`, `S615`, `S618`, `S623`, `S626`, `S628`, `S632`, `S637-S640`, `S643`, `S650-S651`, `S655`, `S657-S658`, `S675-S676`, `S679`, `S686`, `S688-S691`, `S711-S718`, `S736-S737`, `S788`, `S806-S809`.

### Nano Banana 2 / Nano Banana Pro

Best current fit:

- product-reference lifestyle images;
- CJK product walls, posters and campaign grids;
- workflow-canvas systems such as Coze/Nano Banana 2;
- template photoshoots such as studio, ingredient, in-use and lifestyle shots;
- fashion/product scene generation when product reference is strong.

Observed constraints:

- can change product identity while improving the scene;
- weak for precise logos, fine retouching and exact dimensions;
- free/wrapper routes can introduce watermark or commercial-use issues;
- benchmark before relying on it for labels, small text or material fidelity.

Strongest evidence clusters: `S232-S233`, `S284-S287`, `S289-S291`, `S321-S325`, `S347-S351`, `S362-S363`, `S366`, `S368-S370`, `S512-S525`, `S532-S546`, `S547-S558`, `S560-S564`, `S571-S575`, `S577`, `S583-S589`, `S591`, `S598-S600`, `S605`, `S607-S609`, `S611`, `S617`, `S621-S622`, `S624-S625`, `S627`, `S629-S631`, `S633-S635`, `S641-S642`, `S647-S650`, `S653`, `S656-S657`, `S659-S664`, `S676-S677`, `S679`, `S681`, `S685`, `S687`, `S692-S694`, `S707-S710`, `S725-S727`, `S743-S746`, `S789-S793`, `S797-S799`, `S805-S807`.

### Midjourney V8 / V8.1

Best current fit:

- premium visual direction, moodboards and campaign concepts;
- style/mood exploration before product-preserving compositing;
- non-compliance-critical hero imagery and creative key visuals.

Observed constraints:

- not a standalone SKU-accurate listing-image factory;
- text and exact product identity require external QA or another edit/composite step;
- use official V8/V8.1 pages for current feature boundaries.

Strongest evidence clusters: `S234-S237`, `S305`, `S358-S359`, `S364`, `S551`, `M033`, `M059`, `M079`, `M147`.

## Platform Findings

### Amazon

Amazon splits into two very different realities:

- Amazon Ads / Creative Studio officially supports AI lifestyle/ad creative generation.
- Amazon PDP/listing main images remain a stricter product-truth and catalog-governance surface.

Seller Forum evidence adds a new risk: even after upload, Amazon catalog/image systems may choose or replace images in ways that do not match the seller's actual product. This makes post-upload monitoring mandatory for serious sellers.

Recommended Amazon workflow:

1. Keep real main image and source archive.
2. Use AI for secondary/lifestyle/A+/ad creatives first.
3. Build slot-specific briefs for feature, comparison, dimensions and use-case images.
4. Run product/text/policy QA before upload.
5. Monitor live PDP image changes and customer-return signals after upload.
6. Escalate mismatches with screenshots, source website/product photos and case history.

Key evidence: `S213-S215`, `S221`, `S337-S340`, `S384-S389`, `S395-S396`, `M038`, `M070`, `M085-M087`.

### Shopify

Shopify evidence emphasizes operational integration:

- native/near-native tools such as Tinker, Redeux and Snapshot-like apps;
- one-click listing attach and bulk editing;
- reusable brand looks and model teams;
- product/model image experimentation;
- image ordering/export behavior into Meta catalog feeds.

Recommended Shopify workflow:

1. Start from phone/supplier/real product photo.
2. Remove background and preserve subject.
3. Generate lifestyle/model/background variants.
4. Attach directly to product listing or bulk apply by catalog rules.
5. Track which image is used by storefront, Meta catalog and ad feeds.
6. Define metrics before accepting claims such as model-photo lift.

Key evidence: `S341-S346`, `M071-M072`.

### Ozon / Wildberries / Yandex Market

Russian marketplace tooling is developing as full-card operations rather than single image tools:

- product photo and hero cleanup;
- AI lifestyle/infographic cards;
- SEO title/description/characteristics;
- review analytics and replies;
- marketplace-specific templates;
- video and A/B testing claims.

Ozon and Wildberries also have official/native media tooling and hard image requirements, so external tools should feed into a compliance gate rather than bypass it.

Recommended Ozon/WB workflow:

1. Classify main card vs secondary infographic/lifestyle/video.
2. Preserve real product photo for the main card.
3. Use AI for backgrounds, infographics, benefit slides and video covers.
4. Enforce aspect ratio, safe zones, forbidden overlays and product correspondence.
5. Treat vendor CTR/CVR uplift claims as hypotheses until tested.

Key evidence: `S271-S280`, `S296-S299`, `S333-S336`, `S390-S393`, `S599-S600`, `S675-S684`, `M051`, `M054`, `M069`, `M088`, `M182-M184`.

## Reusable Architecture

The evidence points to this internal architecture:

1. ProductTruthPack
   - original photos, cutouts, close-ups, label/OCR text, dimensions, materials, variants, forbidden changes.

2. SlotBrief
   - platform, slot type, buyer question, visual goal, exact copy, aspect ratio and compliance requirements.

3. ModelRouter
   - GPT Image 2 for text-heavy or API-controlled assets;
   - Nano Banana 2/Pro for reference-driven lifestyle/product scenes;
   - Midjourney V8/V8.1 for concept/moodboard;
   - deterministic layout/compositing for exact text and claims.

4. Generation Runtime
   - API/agent/n8n/Coze/ComfyUI/Shopify app paths;
   - logs prompt, model, version, source refs, output path and cost.
   - for ComfyUI, logs workflow JSON/version, nodes, model pack and SKU benchmark result.

5. QA Gates
   - product geometry, material/color, logo/label/OCR, dimensions/specs, policy, watermark/license, channel export.

6. Expansion
   - variants, formats, languages, campaign versions, marketplace variants.

7. Export and Monitoring
   - Shopify upload/feed mapping, Amazon/PDP monitoring, Ozon/WB card export, Drive/Airtable/gallery.

## Decision Matrix

| Job | Recommended route | Avoid | QA gate | Evidence |
| --- | --- | --- | --- | --- |
| Amazon main image | real product photo + deterministic cleanup; GPT Image 2 only for draft/extraction tests | fully synthetic product replacement | white background, exact product, no extra props, live PDP monitor | `S337-S340`, `S356`, `M070` |
| Amazon secondary/A+ | GPT Image 2 structured slot briefs; product ref + text/layout review | one generic prompt for full listing | logo/text/OCR, dimensions, claim truth, policy | `S352-S353`, `S360-S361`, `M075` |
| Shopify catalog refresh | Shopify app/native workflow or API batch; bulk attach/export mapping | manual download/upload per SKU at scale | product fidelity, feed image order, channel metrics | `S341-S346`, `M071-M072` |
| Ozon/WB cards | native marketplace editor or Russian card-stack tools; AI backgrounds/infographics/video | bypassing marketplace moderation rules | aspect ratio, overlays, product correspondence, category rules | `S296-S299`, `S333-S336`, `M069` |
| Russian WB/Ozon prompt-pack cards | product photo + localized prompt template -> GPT Image 2/Nano Banana Pro card variants | copying global prompts without Cyrillic/card rules | product correspondence, Cyrillic proofing, WB/Ozon moderation | `S675-S677`, `S683`, `M182` |
| URL-to-card visual prompt workspace | product URL -> extracted facts/images -> visual prompt/card generation | generating from URL without source trace | extraction accuracy, source URL log, variant/spec checks | `S678`, `S673`, `M183` |
| Ozon/WB rich-content tool workflow | SKU facts/photo -> localized tool -> card/rich-content/SEO assets -> marketplace editor | treating generated rich content as factual | characteristics, rich content structure, moderation, text/icon proofing | `S680`, `S682`, `S684`, `M184` |
| Fashion model/lifestyle | n8n/form batch + Nano Banana Pro/i2i + local product folders | trusting try-on without garment verification | fabric pattern, logo, color, fit, accessory count | `S363`, `S342-S344`, `M077` |
| Long detail page | ComfyUI/RunningHub/Coze workflow with layered PSD or editable modules | flat generated image with no edit layer | product truth per module, copy/spec verification, PSD/layer review | `S284`, `S347-S351`, `M073` |
| Text-heavy card/label | GPT Image 2 or deterministic layout after image generation | asking weaker photo model to invent exact text | OCR, typography, copy lock, language check | `S360-S362`, `S370`, `M078` |
| Premium campaign concept | Midjourney V8/V7 prompt-builder loop, then product composite/QA | using Midjourney output as SKU proof | product identity, label/logo, licensing | `S358-S359`, `S364`, `M079` |
| Video ads | generate approved first frame, then animate or hand to UGC creator | animating unreviewed hallucinated product | first-frame product QA, key-frame review, claims | `S369`, `S361`, `M080` |
| Full Amazon listing+A+ | product analysis -> design script -> coordinated modules -> desktop/mobile export | random unrelated image set from one prompt | #FFFFFF slot, wording, A+ breakpoint, product facts, editability | `S387-S388`, `S395-S396`, `M086-M087` |
| WB/Ozon phone-photo cards | phone photo -> try-on/infographic/lifestyle/video card pack | accepting CTR claims without test | product-description match, fabric/cut/logos, marketplace moderation | `S390-S393`, `M088` |
| ComfyUI backend | versioned node graph for cutout/layer/lighting/product placement | using raw graph with no SKU benchmark | workflow JSON version, product preservation, GPU/model constraints | `S397-S399`, `S402`, `S405`, `M090`, `M093` |
| Conversion-shot planning | buyer research -> slot job -> variant test | making every image a cinematic hero | buyer objection answered, one-variable test, CTR/CVR | `S404`, `S389`, `M092` |
| Shopify automation | product trigger/image URL -> AI image/copy generation -> catalog writeback | unreviewed auto-publish | source image quality, draft review, product attributes, asset mapping | `S409-S413`, `S416`, `M094-M095` |
| One-photo video ad | product photo -> YAML visual DNA -> creative director -> video model -> logged asset | video without key-frame QA | product drift, claims, aspect ratio, Drive/DB logging | `S415`, `M096` |
| Shopify bulk media apps | existing catalog photos -> app-generated lifestyle/model/try-on/media -> product-media writeback | treating app output as verified product truth | approved scenes, try-on fidelity, product-media mapping, app terms | `S417`, `S422-S423`, `M098` |
| Amazon main-image cleanup | phone product photo -> clean white main image -> seller review | competitor/brand style overriding product truth | Amazon main-image policy, product match, conversion test | `S419-S421`, `M100` |
| Amazon one-photo listing suite | product photo -> listing images + A+ + copy/search terms -> Seller Central review | direct auto-publish without slot QA | main-image suppression rules, copy fact check, A+ claim review | `S424`, `S428-S430`, `M101` |
| Seller Central planning to creative | Seller Assistant/canvas + store module requirements -> image/video asset plan | treating planning AI as compliance approval | accurate representation, module requirements, b-roll key frames | `S431-S433`, `M103` |
| Google Merchant Center native media | Product Studio -> background/upscale/image/video -> Merchant Center/Shopify feed | ignoring metadata/feed approval behavior | AI metadata, image_link, main image checkbox, regulated goods | `S434-S435`, `M104` |
| TikTok product creative | product URL/images/selling points -> Symphony video/display card/carousel | using static marketplace assumptions for TikTok Shop | product accuracy, traffic behavior, key frames, ad policy | `S436-S437`, `M105` |
| Adobe enterprise composite | product photo/object -> Composite API + Creative Production batch | treating composite realism as marketplace compliance | mask/edge, harmonization, batch logs, product label QA | `S438-S439`, `M106` |
| Meta/Pinterest ad backgrounds | real product cutout/catalog image -> generated backgrounds -> platform label/toggle review | platform auto-enhancements left unchecked | AI label, automatic background toggle, product cutout integrity, placement preview | `S442-S444`, `S449-S450`, `M108` |
| Etsy/eBay compliance | final product photo/actual item photo -> limited AI edits -> disclosure/accuracy review | AI mockups replacing final/used item photos | Etsy AI disclosure, eBay accurate representation, no text/watermark/borders | `S445-S447`, `S451`, `M109-M110` |
| Walmart listing optimization | actual product photo + GenAI listing copy -> Walmart image/content review | pure synthetic main image or unreviewed GenAI content | actual-product image, truthfulness, rights, white background | `S452-S454`, `M112` |
| Cross-border supplier photo cleanup | rough supplier/AliExpress photo -> natural compliant main image -> conversion test | overdone AI polish that changes SKU | product match, natural look, marketplace style standards | `S455`, `S459`, `M113` |
| Shopee/SEA actual-item workflow | actual item photo + model/use/variation shots + platform AI assist | assuming AI platform tools replace product photos | actual item, lighting, clean background, swatches, try-on truth | `S456-S457`, `M114` |
| Furniture visual commerce | one furniture photo -> catalog/room/multi-angle/video/A+ modules | random room scenes with material drift | scale, wood/fabric/reflection lock, reusable room/crop templates | `S460-S464`, `M116` |
| Image-to-3D/AR | product photos + dimensions -> 3D model/AR catalog -> scan analytics | photorealism without dimension accuracy | scale, geometry, material texture, size variants | `S462`, `S465`, `M117` |
| Fashion virtual try-on | flat garment/customer photo -> try-on widget/output -> usage/failure tracking | treating try-on as ordinary model shot | garment texture, drape, logo, customer identity, failed-output cost | `S466-S469`, `M118-M119` |
| Vertical product studios | product ref + category/channel router -> studio/lifestyle/cards/video variants | one generic prompt for all categories | material/geometry/logo/label QA by vertical | `S470-S474`, `M120` |
| Packaging/mockups | package/product/artwork -> cleanup/scene/mockup with warping and lighting review | treating mockup as manufactured-product proof | OCR label, print distortion, material reflection, package shape | `S472`, `S474-S475`, `M121` |
| Hard-category benchmark | reflective skincare/jewelry/furniture/garment tests -> model route | generic aesthetic leaderboard | reflection, wood grain, matte metal, shadow, texture, text fidelity | `S476`, `S372`, `S469`, `M122` |
| Visual Syntax lifestyle prompts | product ref + structured style/subject/action/scene brief -> slot variants | vague vibe prompts | product identity, action plausibility, brand consistency | `S477`, `S481`, `S489`, `M123` |
| Chinese GPT Image 2 suites/video | product info/photo -> GPT Image 2 prompt pack -> Coze suite or ComfyUI/RunningHub video | isolated prompt with no workflow state | Chinese text, product truth, platform slot, key frames | `S478-S480`, `M124` |
| Preset virtual photoshoot | product upload + scene/style picker -> bulk standalone/lifestyle/in-use images | hand-written long prompt for every angle | scale, material, human interaction, generic style drift | `S485`, `S487`, `S489`, `M125` |
| Human-in-use trust QA | generated human scene -> scale/function/trust checklist | using pretty people as proof of realism | product size, grip/use direction, buyer trust, physical logic | `S486-S488`, `M126` |
| MCP/media router | task intent + product ref -> image/video/audio model route -> logged asset | router without product-truth metadata | model/cost log, product QA, policy review | `S482`, `S474`, `M127` |
| Amazon Brand Registry proof | real physical product photos with permanent logo -> application evidence | AI/computer-generated brand proof | permanent mark, close-up, product-in-hand proof | `S491-S492`, `M128` |
| Supplier-photo creative testing | raw supplier photo -> product-preserving lifestyle/mockup tests | Midjourney-style design drift | source product match, material/light preservation, sample-cost decision | `S493`, `S495`, `M129` |
| Feishu/Coze batch ops | table/form row -> AI prompt -> Nano Banana/Seedream/Coze outputs -> review | one-off manual prompt work | row metadata, product match, channel slot, Chinese text | `S496-S499`, `M130` |
| UGC/product-video automation | product image + skill prompt -> Higgsfield/Seedance video/product 360 -> session log | video without key-frame QA | product drift, claim truth, aspect ratio, session recovery | `S500-S501`, `M131` |
| Scene-variable prompt workbench | product variables + scene template -> product card/hero/marketplace prompt | generic prompt gallery with no reference QA | model/rights check, product detail, originality | `S502`, `M132` |
| Russian WB/Ozon card factory | product photo -> marketplace card visuals + SEO text/description -> export/review | image-only generation without marketplace copy/moderation | real characteristics, banned phrases, marketplace size, text truth | `S503-S504`, `S271`, `S392`, `M133` |
| Shopify bulk catalog media | Shopify catalog -> bulk studio/lifestyle/on-model/video/ads -> product-media sync | auto-publish without SKU review | fabric detail, model realism, product identity, app data access | `S507-S511`, `M134` |
| Amazon one-photo listing suite | single product photo -> coordinated listing images + A+ modules | generic generator that changes product shape | product geometry lock, brand style, A+ text/icons, main-image boundary | `S505-S506`, `S246`, `M135` |
| One-upload product media suites | one product photo or URL -> PDP, ad, social, UGC and video asset pack | treating outputs as final without slot-level QA | product URL/photo truth anchor, saved scenes, approval gates, text/logo/hand checks | `S512-S519`, `M136-M137` |
| Small-framework automation | Telegram/n8n or scheduled queue -> deterministic cleanup -> model jobs -> logs/publish | synchronous one-shot generation or auto-publish | rembg/Sharp preprocessing, job polling/backoff, Sheets ledger, human approval | `S521-S523`, `M138-M139` |
| Open-source/CLI image ops | CLI/SDK/API loops around Nano Banana/Nano Banana Pro and fashion try-on | manual SaaS-only workflow | reference images, promptgen, provider routing, 4K output, batch shell/API loops | `S524-S525`, `M140` |
| Amazon-native creative ops | ASIN/reference product -> Amazon creative generation -> campaign/A+ asset library -> split tests | using ad/lifestyle outputs as proof/main images | Amazon slot separation, product-reference review, seller-side "do not alter product" prompts, ad compliance check | `S532-S534`, `S546`, `M142-M143` |
| Russian rich-card factory | product facts/photo -> SEO text, Rich Content, infographic, FAQ/reviews -> marketplace card | only generating pretty cards without factual fields | factual characteristic source, Rich Content structure, product-photo infographic QA | `S535-S538`, `M144` |
| n8n video factories | Shopify/Sheets/product image -> prompt/script -> image enhancement -> video/voice/lip sync -> export/log | no async waits/logs or no image filtering | text-overlay filtering, wait/poll nodes, Sheets rows, output ledger, human approval | `S539-S542`, `M145` |
| Official model surfaces | Firefly/Photoshop/Slides/Vids/API -> mockups/infographics/refinement | treating design-surface output as batch-ready | app-surface refinement plus API/CLI for batch, generated-set versioning | `S543-S545`, `M146` |
| Seller-cost replacement | routine catalog photos -> lightbox/phone -> AI cleanup/background/lifestyle variants -> outsource only hero shots | paying per image for repetitive white-background work or auto-publishing AI ads | product source photo, style guide, redo rate, trust/product-drift QA | `S062`, `S559`, `S568-S570`, `M150` |
| Wildberries native AI media | card data/photo -> neural rich content, video cover, live photo, autoplay | treating generated rich content/video as factually correct | generated text/icons/photos review, subscription/region limits, moderation | `S565-S566`, `M151` |
| Prompt-library as SKU brief | prompt pack -> SKU facts + marketplace slot + negative constraints -> variants -> QA | copy-pasting generic prompts with no product facts | reference product, marketplace rules, OCR/label/color/shape QA | `S560-S564`, `S567`, `M152` |
| Open-source CMS/agent layer | media library or agent skill -> prompt search/model route -> draw/edit/batch -> saved asset/cost log | SaaS-only one-off generation with no trace | API keys, output metadata, product reference, watermark/license checks | `S572-S577`, `S580`, `S582`, `M153` |
| Creative-volume testing | product source + brand/ICP brief -> 4-50 differentiated variants -> score/polish winners | raw image count with no review rubric | click/readability/product-emphasis score, product drift rejects, cost per usable winner | `S578-S579`, `S581`, `S585`, `S588`, `M154` |
| Vision-to-prompt assistant | raw product image -> VLM analyzes lighting/composition -> technical prompt -> image-to-image variants | asking sellers to become prompt engineers | product truth constraints, technical lighting prompt, label/color/material QA | `S583-S587`, `M155` |
| Static-first video | approved still set -> short motion/video model -> reject melting/drift -> social/PDP video | generating video from scratch with no still approval | first/last-frame product match, label drift, motion artifact review | `S589`, `S015`, `S556`, `M156` |
| Agent Skill image packs | product ref + buyer reason + style lock -> 5 main images + 7-9 detail panels -> saved prompts/assets | monolithic prompt or untraceable SaaS output | reference image, Campaign Style Lock, per-slot prompts, optional compliance pass | `S594-S597`, `M157` |
| n8n multi-platform ad factory | one product photo -> 4K scene masters -> auto-crop platform ratios -> S3/ZIP export | manual resizing and disconnected exports | source-photo anchor, crop review, storage/export ledger | `S591`, `S605`, `M158` |
| Russian Ozon/WB model router | product photo + Russian prompt -> choose Nano Banana/GPT Image 2 by text/complexity -> card variants | generic global prompts with no marketplace rules | white background, center product, Cyrillic text proofing, SKU-by-SKU QA | `S599-S600`, `S609`, `M159` |
| Amazon hybrid compliance | real main image or compliant white-background output -> AI secondary images -> manual design QA | fully synthetic unverified listing set | RGB255/coverage checks, material/color/dimension verification, manual fixes | `S601-S604`, `S432`, `M160` |
| Prompt-CSV batching | source image + 10-50 prompt rows -> bulk outputs -> ZIP -> accept/reject log | treating batch count as success | reference anchors, reject reasons, cost per usable image | `S605`, `M161` |
| Text-heavy promo/PDP prompts | product + promo theme + exact copy + hierarchy -> GPT Image 2 variants -> proof/crop | assuming text rendering is automatically correct | OCR/manual proofing, margin/layout review, source product inclusion | `S590`, `S606`, `S610`, `M162` |
| Shopify-native AI media apps | Shopify product/customer upload -> app generation -> attach listing/POD/social/video output | exporting files through disconnected SaaS only | app bulk editor, one-click attach, customer preview, app credit/log review | `S614-S618`, `S620-S621`, `M163` |
| Trust-first product photo QA | AI variants -> community/design critique -> retouch/reject -> publish only believable outputs | using raw AI output as final ad/listing | focal-point check, scene relevance, product detail trust, Photoshop/Canva cleanup | `S612-S613`, `S619`, `M164` |
| Batch photo-and-video tools | product photo + batch jobs -> stills/videos -> export full set | one-by-one generation with no asset set concept | approved still anchors, video drift review, cost/failure logs | `S611`, `S589`, `S591`, `M165` |
| Seed-set full listing gallery | strong product seed -> hero/alternate/close-up/lifestyle/channel crops | poor input to batch automation | source standardization, readable label/material, slot-level reject log | `S622`, `S624-S625`, `S627`, `M166` |
| Prompt-gallery campaign workspace | prompt gallery -> product page/mockup/campaign creative -> ratios/editor export | generic prompt copy-paste without refs/proof | product reference, exact-copy proofing, export resolution/licensing checks | `S623`, `S626`, `S628`, `M167` |
| Agency R&D delivery | client photo -> R&D prompt loops -> manual retouch -> selected deliverables | promising no-effort automation | dimensions/material/text review, Photoshop stop-loss, client feedback | `S629-S630`, `S585`, `M168` |
| Amazon seller hybrid decision | phone/pro photo -> AI listing pack -> manual approval or studio fallback | using AI for every category and main image | category risk, over-rendered look, packaging/textile/food review, Amazon approval risk | `S631`, `S633-S635`, `S602`, `M169` |
| Structured prompt/model benchmark routing | benchmark category + reference roles -> model choice -> scored variants | choosing models from hype posts only | prompt accuracy, realism, text, scale, product consistency, reference-role labels | `S632`, `S637-S640`, `S643`, `M170` |
| Local detail-page workspace | product image -> product analysis -> detail-page sections -> regenerate modules | one-shot long prompt for PDP | section versioning, product facts, copy/image prompt review | `S636`, `S592`, `S596-S597`, `M171` |
| Prompt-gallery product-shot templates | prompt template + SKU facts + product ref -> product-shot variants | copy-paste prompt without product QA | labels/materials/scale, marketplace background, rights/model access | `S641-S642`, `S557-S558`, `M172` |
| Buyer-trust negative-evidence QA | generated/edited product image -> real measurement/spec review -> reject misleading outputs | treating photoreal edits as proof | scale, measurements, material, received-product match, return risk | `S645-S646`, `S613`, `M173` |
| Chinese PS/API PDP workflow | product image -> prompt/API/PS plugin -> editable detail-page modules | flat one-shot prompt with no editable state | PS layers/API logs, Chinese text proof, product facts | `S648-S650`, `S590`, `S636`, `M174` |
| Wrapper-led one-photo product media | one product photo -> wrapper/tool variants -> listing/ad/video export | trusting wrapper marketing claims | model access, watermark/rights, reference fidelity, output trial | `S647`, `S651-S653`, `S643`, `M175` |
| GPT Image 2 prompt-as-code corpus | prompt repo/X corpus -> SKU rewrite -> API/CLI/tool generation -> provenance log | treating community prompt as product truth | source attribution, SKU facts, exact-copy/product QA | `S688-S691`, `S655`, `M185` |
| HN/community model-risk intake | release thread/quality link -> failure taxonomy -> QA checklist update | using HN hype as production benchmark | text/composition/random-edit risk mapped to SKU tests | `S685-S687`, `S006`, `M186` |
| Nano Banana 2 speed-tier product studio | product ref -> fast NB2 variants -> Pro/hero route only for critical shots | choosing model tier by hype or price alone | scale, text, material, provider/resolution verification | `S692-S694`, `S310`, `M187` |
| Chinese Coze/Feishu/Nano batch | competitor ref + SKU facts -> table rows -> Nano/Coze image generation -> review | one-off prompt work with no row ledger | source photo, prompt row, Chinese text, product match | `S695`, `S697-S698`, `M188` |
| Zero-prompt template product studio | product photo -> style/template -> batch outputs -> store push | hiding model assumptions behind presets | product geometry, scale, label, platform rules | `S700`, `S702-S703`, `M189` |
| Vertical fashion/jewellery image-video studio | catalog/product photo -> on-model/flat-lay/jewellery/video route -> store/social publish | generic product photo model for detail-heavy categories | fabric drape, jewellery reflection, model fit, video drift | `S701`, `S704-S705`, `M190` |
| Open-source image workbench/media suite | product ref + prompt assets + provider endpoint -> batch/edit/history -> media library | one-off SaaS output with no asset memory | SKU refs, provider logs, cost/history, language/platform QA | `S711`, `S713`, `M191` |
| GPT Image 2 async API/agent skill | prompt/ref image -> task id -> polling/webhook -> run ledger -> QA status | blocking scripts or unowned callbacks | idempotent webhooks, task ownership, exact model route, output QA | `S714-S718`, `S712`, `M192` |
| Prompt-guide plus benchmark routing | prompt guide/benchmark -> SKU test set -> model choice -> scale only winners | choosing from prompt hype alone | label/text/material/geometry check, benchmark replication | `S707-S710`, `S242`, `M193` |
| Shopify seller AI-media shortlist | seller thread/app lead -> job classification -> small SKU trial -> catalog decision | trusting app-store or forum claims directly | product identity, Shopify permissions, analytics proof, return risk | `S719-S724`, `M194-M195` |
| Nano Banana 2 cost/control tiering | NB2/Pro/GPT2 comparison -> cost/quality tier -> routine vs hero route | treating cheaper/faster tier as universal | Chinese text, hallucination, quota/model identity, product fidelity | `S725-S727`, `S692-S694`, `M196` |
| Dedicated ecommerce studio consistency test | source photos + 20-50 SKU set -> style lock/store writeback check -> reject-rate log | judging tools from one hero image | product preservation, catalog drift, marketplace specs, manual edit count | `S728-S733`, `S747`, `M197` |
| Amazon listing stack generator | product source -> hero/alt/A+/ad/video stack -> QA/auto-fix -> Seller Central export | mixing main-image compliance and ad/lifestyle freedom | RGB255/85% hero check, generated slot log, ASIN policy review | `S734-S735`, `S742`, `S733`, `M198` |
| Marketplace trust compliance gate | generated image -> real-source/edit-type classification -> misrepresentation review | assuming AI acceptance means any synthetic product image is safe | source-photo proof, label/material/dimension comparison, appeal evidence | `S738-S741`, `S739`, `M199` |
| GPT Image 2 text/API routing | exact copy + product reference -> GPT Image 2/text model -> proof -> API ledger | using image model output as final copy proof | OCR/manual proof, claim validation, provider/model logging | `S736-S737`, `S714-S717`, `M200` |
| Open model/framework watchlist | new model/framework -> SKU benchmark -> license/integration review -> promote or reject | adopting demo-quality models without product tests | subject preservation, text rendering, license, batch orchestration | `S743-S746`, `M201` |
| Russian WB/Ozon full-card production | product facts + SEO + product-card/infographic/video covers -> aspect/platform check | generating only decorative image cards | Russian copy, false-claim check, platform ratios, moderation outcome | `S748-S749`, `S751`, `S754-S755`, `M202` |
| Russian prompt-pack/designer-reference | prompt pack/portfolio -> SKU prompt -> Nano Banana/GPT route -> design finish | treating prompts/portfolio as fidelity proof | product dimensions, labels, Russian text, prompt provenance | `S750`, `S752-S753`, `S679`, `M203` |
| Bilibili cross-border tutorial harvesting | search cluster -> direct BV IDs -> metadata/subtitles -> workflow taxonomy | treating search pages as verified tutorials | direct URL, transcript, model/workflow tags, resource links | `S756-S759`, `S528`, `S590-S591`, `M204` |
| Brand-system-first Amazon listing generation | brand file -> Amazon slot type -> product-photo generation/edit loop | rebuilding each image as a fresh prompt | brand colors/type/mood, slot taxonomy, copy proof, main-image compliance | `S761-S763`, `S767-S768`, `M205` |
| AI scene plus real-product composite | AI background/human scene -> real product/logo composite -> optional video animation | letting AI invent the exact product/logo | lighting/perspective/scale match, real logo, frame-by-frame video QA | `S764-S766`, `S769`, `M206` |
| Nano Banana 2 CMS/prompt-library production | locked category prompts/API -> CMS media write -> SEO/provenance/review | freeform prompt gallery copy-paste | provider/model log, SynthID/disclosure, alt/schema, review checkpoint | `S770-S775`, `M207` |
| Bilibili direct-video capture queue | search cluster -> BV capture -> transcript/resources -> workflow taxonomy | treating Bilibili snippets as verified workflows | direct BV URL, subtitle/resource files, cost claim and output type | `S776-S778`, `S756-S759`, `M208` |
| Multi-angle product ad grid | object reference -> six-slot grid prompt -> split/regenerate slots | shipping a low-res collage as final listing media | product geometry, label text, crop, per-slot QA | `S779`, `S322`, `S774-S775`, `M209` |
| Official preset-tool evaluation | seller tool mentions -> official pages -> same-SKU benchmark | trusting Reddit or vendor claims alone | no-prompt UX, batch export, product lock, video/infographic support | `S780-S785`, `S485`, `S583`, `M210` |
| Amazon buyer-intent JSON experiments | Brand Analytics/search intent -> JSON image spec -> variants -> experiment log | prettier images without buyer question or product invariants | product truth, slot policy, forbidden inventions, CTR/CVR split test | `S786`, `S388`, `S659`, `M211` |
| Complex product consistency | multi-angle dataset -> LoRA/adapters/ComfyUI -> manual finish | expecting one prompt/reference to preserve tiny details | screws/logos/patterns/material, matching angle refs, reject log | `S787`, `S790-S793`, `M212` |
| ComfyUI API-node orchestration | workflow JSON + provider endpoint + refs -> grids/video/preflight -> logged outputs | SaaS-only black-box generation | provider parameter exposure, reference_image passthrough, cost, graph version | `S789-S793`, `M213` |
| X/Twitter prompt-corpus mining | public GPT Image 2 posts/repos -> cluster -> SKU rewrite -> provenance log | copying viral prompts as product truth | source URL, rights, C2PA/provenance loss, SKU QA | `S788`, `S690`, `S775`, `M214` |
| Agentic prompt-gallery CLI/MCP | natural-language prompt search -> source/reference retrieval -> CLI/MCP generation -> logged variants | prompt copy-paste without source or SKU facts | prompt provenance, reference image, model/provider log, rights | `S655-S657`, `S017`, `S260`, `M176` |
| Amazon seven-image reference chain | primary anchor -> lifestyle + typography baseline -> dual-reference graphics | independent per-slot generations with drifting product/design | main-image policy, mobile readability, OCR/copy, product scale | `S659`, `S644`, `S631`, `M177` |
| Nano Banana 2 edit-first product workflow | product photo -> one edit/fusion goal -> draft iteration -> high-res export/batch | pure text-to-product generation for identity-critical assets | shape/material/color preservation, provider rights, watermark, batch limits | `S660-S662`, `S658`, `S511`, `M178` |
| Shopify-native product-media app | product/supplier photo -> app-generated scenes/model shots -> direct product-media save | disconnected export/import or unreviewed publish | app data access, product detail, fabric/label, product-media mapping | `S665-S667`, `S674`, `M179` |
| Form/sheet n8n approval workflow | Jotform/Drive input -> model generation -> QC approval -> Sheets/CMS/Shopify output | no structured specs or no approval ledger | color/material/angle checks, output links, crop/platform review | `S668`, `S411`, `S591`, `M180` |
| Product-link/fashion catalog pipeline | product URL or garment photo -> product understanding -> images/copy/model shots/page modules | generating images before understanding product facts | product fact extraction, garment texture/pattern, marketplace slot compliance | `S671-S673`, `S419`, `M181` |

## Chinese Workflow Addendum

The strongest newly added Chinese signals are not just model demos. They are workflow packaging patterns:

- Coze branch workflow: product/competitor refs -> prompt reverse-engineering -> selling points -> main image -> cutout/detail-page prompt -> detail-page images.
- RunningHub/ComfyUI: product image -> detail-page workflow -> 8-screen/long-page output -> layered PSD for correction.
- Feishu table: SKU/demand/prompt rows -> AI drawing nodes -> batch output -> review status.
- Photoshop plugin: designer keeps the PS canvas while GPT Image 2 drafts poster/detail-page layouts.

The practical implication is that a production system should have a table/workflow/control layer before model choice becomes the bottleneck.

## Strong Small Frameworks To Study

- `S331` StartripAI image2-workbench: spec-first YAML templates, preflight, cost, ledger and Skill path.
- `S328` GPT Image 2 vs Nano Banana 2 benchmark rig: resumable model comparison pipeline.
- `S332` lucaswalter n8n automations: competitor-ad-to-variant Nano Banana workflows.
- `S300` Reddit n8n product studio: phone photo -> cleanup -> AI enhancement.
- `S284` Coze + Nano Banana 2 two-branch workflow: main-image and detail-page generation.
- `S306` open-design: GPT Image 2 plus video/product-film media pipeline.
- `S371` GitHub topic: fast-moving GPT Image 2 Skills, local tools, prompt-as-code libraries and plugins.
- `S372` awesome-jewelry-ai: vertical-category product photography workflows and detail-critical QA.
- `S383` Cliprise prompt repos: GPT Image 2/Nano Banana Pro prompt collections for product photography and ad creative.
- `S394` CreativeAds: modular product-pairing/layout/background architecture for scalable multi-object ads.
- `S397-S399` ComfyUI production/lighting workflows: local versioned backend for controllable product-photo pipelines.
- `S405` ComfySearch: validation-guided agentic workflow generation for ComfyUI.

## Website And Tool Cases To Track

- Amazon Creative Studio / Image Generator.
- Shopify Tinker, Redeux, Snapshot-style apps.
- Ozon AI editor, Wildberries Photostudio.
- Sozdai, Creator AI, Kartinka, WildScan, Prodiger, AI Berry.
- ProductAI, Bananai, TraceUI, Duct Tape AI, Sellshot.
- GPT Image 2 wrapper/prompt sites: Image2, ImageGen2, Atlas Cloud, Devoured.
- Prompt galleries/wrappers added in latest pass: IMGVID, Bananai GPT Image 2, Got Image 2, gptsImage, GPT Img 2 App, GPT Image 2 Tech, Nemovideo, IMA Studio, YouMind.
- Vertical product studios and benchmarks: Tasweera, Luminify, StudioMode, Pixora, GenMix, ProductShot, AIToolTesting.
- Community/workflow additions: Visual Syntax Reddit workflow, Bilibili GPT Image 2 618 prompt pack, GPT-image2 + ComfyUI product-to-video, ChatGPT Image 2 + Coze Taobao/Amazon suite, Kie.ai MCP router, Lumiet Shopify prompt templates, HN Sellshots.
- Compliance and automation additions: Amazon Brand Registry real-photo/no-AI evidence, Feishu Bitable batch main-image workflow, Coze/Nano Banana Pro ecommerce videos/details, Claude Code + Higgsfield UGC/product-360 automation, Image2Studio scene-variable prompts.
- Russian/Shopify latest additions: Racurs, Wildberries AI description news, ProductPhotography/Reddstudio thread, Rewarx, StudioShot, Comera, Rokon and Modelize.
- Russian WB/Ozon prompt and rich-content additions: VC.ru GPT Image 2 and Nano Banana Pro card workflows, Habr URL-to-card Visual Prompting workspace, Sostav model comparison, Universus Ozon guide, WildAI and DTF/Sostav marketplace-card tool lists.
- HN/GitHub/Nano Banana 2 latest additions: HN GPT Image 2 and Nano Banana Pro discussions, Prompt-as-Code and X-attributed GPT Image 2 prompt repositories, Lumiet Nano Banana 2 model page, YourRender NB2 product-photo tier test and Plykit NB2 product studio.
- Russian/Bilibili continuation additions: Loonia Ozon/WB card generator, Epokha full-listing AI cards, Texblog/VEO4YOU Russian prompt packs, Sostav 15-service comparison, Behance Nano Banana Pro card design case, AI-Electronic and MashaGPT workflows, Bilibili GPT Image2/Coze/Nano Banana 2 cross-border tutorial clusters and frontier image-risk evidence.
- Reddit/HN/YouTube/Bilibili continuation additions: WorkFx Amazon/Shopify listing workflow, Claude brand-system listing images, Clair Claude Skill, AmazonFBA 3D/AI debate, YouTube Amazon product-photography lead, Amazon image-to-video composite workflow, HN/GreenOnion pricing and constraint-system thread, Promptolis logo-trap composite workflow, Biteabyte CMS/SynthID route, PicassoIA/Vofy Nano Banana 2 prompt guides, Aino NB2 wrapper, GPT Image 2 prompt galleries and new Bilibili Coze/GPT Image2/Nano Banana layered-PSD capture targets.
- Chinese/tool-studio latest additions: KatuAI, XinianAI, Juejin Coze/Feishu workflow, Bilibili Feishu/Nano batch lead, Qovai, Cheeppy, Kotoor, ShopYa, AIMS, PhotoIQ and Orniva.

## Evidence Quality Notes

High confidence:

- official model/platform docs;
- locally captured YouTube transcripts;
- extracted PDF text;
- directly opened GitHub repos and official marketplace docs.

Medium confidence:

- Reddit, HN, Shopify/Amazon forums, Bilibili API metadata;
- Product Hunt and tool-site workflows;
- X aggregators that preserve source links/snippets.

Low confidence until tested:

- CTR/CVR uplift claims;
- wrapper claims about marketplace readiness;
- exact model pricing/cost claims from non-official pages;
- Bilibili search/index snippets without direct video review.

## Remaining Gaps

- More direct X original post captures.
- Full direct Bilibili video watching/screenshots for node graphs and prompts.
- Controlled SKU benchmark across GPT Image 2, Nano Banana 2/Pro and Midjourney V8.1.
- Real conversion data with defined metrics.
- More official policy checks for Amazon main image, Ozon/WB moderation and Shopify/Meta feed behavior.
