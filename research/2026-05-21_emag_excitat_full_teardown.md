# eMAG / Excitat 41-SKU Image System Teardown

Date: 2026-05-21

Source: `https://www.emag.ro/vendors/vendor/cangswjp?ref=seller-page-see-all-products`

Local sample library:

- Gallery index: `references/user_cases/20260521_emag_cangswjp/index.html`
- Image manifest: `references/user_cases/20260521_emag_cangswjp/image_manifest.csv`
- Scrape summary: `references/user_cases/20260521_emag_cangswjp/scrape_summary.json`
- Contact sheets: `references/user_cases/20260521_emag_cangswjp/contact_sheets/`
- Product folders: `references/user_cases/20260521_emag_cangswjp/products/`

## 1. Capture Result

This sample set is large enough to learn the seller's image system, not just a
few attractive thumbnails.

| Metric | Count |
|---|---:|
| Products | 41 |
| Failed product pages | 0 |
| eMAG platform gallery images | 403 |
| Description/detail images | 420 |
| Product images total | 823 |
| Helper screenshots/contact sheets | 2+ |
| Local folder size after indexing | about 418 MB |

Image-shape pattern:

- Main gallery: almost entirely square. 396 of 403 images are 1:1.
- Main gallery common sizes: 1500x1500, 1300x1300, 1000x1000, 800x800.
- Detail images: mixed square, wide banners, vertical cards, and GIFs.
- Detail common ratios: 1:1, 2.4:1, 1.6:1, 2:1, 4:5.

Implication: our system needs two output tracks:

1. eMAG square gallery suite: primary marketplace image set.
2. Detail-page support assets: wide banners, vertical explanation cards, and
   optional animation/GIF material.

## 2. What This Seller Is Actually Doing

This is not the strict Amazon-style white-background main-image system. It is a
search-card advertising system adapted to eMAG:

`product cutout / source photo -> brand frame -> short proof copy -> category color palette -> supporting detail cards`

The system is strong because it is repeatable across unrelated categories:

- game consoles
- baby appliances
- Arduino kits
- wire stripping machines
- ventilation fans
- filters and safety accessories
- EV charging cables
- hinges, laminators, plugs
- puzzles and toys
- food/baking tools
- camera mounts
- car LED bulbs
- coffee appliances
- robot toys
- gimbals

The seller's real advantage is not one perfect image. It is that every product
quickly receives a coherent commercial image suite.

## 3. Brand-Frame Anatomy

The recurring main-gallery structure:

| Layer | Observed Pattern | Why It Works |
|---|---|---|
| Brand mark | `Excitat` usually in top-right or corner wedge | creates store-level continuity across categories |
| Frame | thin color border, often teal/green/orange/blue/magenta | makes the image feel finished and clickable in search |
| Product anchor | product or bundle large in center/foreground | preserves quick product recognition |
| Proof badge | large number, power, capacity, quantity, compatibility, or size | gives a reason to click |
| Support icons | circles, small cards, check marks, compatibility icons | turns specs into visual proof |
| Bottom/side strip | parameters, package contents, use cases, device compatibility | answers buyer uncertainty |
| Category palette | purple tech, green utility, orange tool, mint baby, black/gold coffee | makes unrelated products feel locally appropriate |

This is why the earlier backpack result felt weak: it likely had a product and
a scene, but not a complete marketplace image system. It lacked stable brand
tokens, buyer-question slots, proof badges, deterministic text zones, and suite
continuity.

## 4. Slot Taxonomy Extracted From The Sample

The seller repeatedly uses these slots:

| Slot | Buyer Question | Sample Behavior | Template Direction |
|---|---|---|---|
| Brand-frame hero | What is it and why click? | big product, logo corner, largest claim | `OzonHighConversionMainCard` derivative |
| Core feature proof | What are the 3-5 key benefits? | icon list, feature cards, parameter badges | `FeatureRightTextCard` |
| Detail proof | Is the material/part reliable? | macro, cutaway, callout line | `DetailMacroCard` |
| Parameter card | Will it fit my need? | wattage, size, capacity, compatibility | `CalloutAroundProductCard` |
| Package contents | What do I receive? | all included items arranged with labels | `PackageTrustCard` |
| Usage / scenario | Where do I use it? | scene grid, home/garage/office/camping | `MultiSceneGridCard` |
| Installation / steps | How do I use/install it? | 4-step panels, arrows, process cards | `MultiSceneGridCard` derivative |
| Comparison / objection | Why better than old/other? | our vs others, problem/solution | gated `BeforeAfterSplitCard` |

The strongest reusable pattern is:

`1 hero + 1 feature card + 1 detail card + 1 parameter/compatibility card + 1 package card + 1 scenario/steps card`

This matches the user's expected range of one main image plus four to eight
secondary images.

## 5. Representative 20-SKU Teardown

These 20 products cover the main style families and should be used as the first
high-value reference set.

| SKU | Product Type | Visual Family | What To Learn | What We Should Improve |
|---|---|---|---|---|
| DMJHW83BM | game stick console | dark purple gaming | high-energy hero, numeric badge, platform/game proof | reduce text clutter and fake UI feel |
| D5YN6S3BM | baby steamer/blender | mint baby appliance | soft palette, icon benefits, food process cards | make copy language consistent and cleaner |
| DV2XYC3BM | Arduino kit | dense kit/contents | component inventory and package proof | avoid overwhelming first image |
| DWLFYC3BM | wire stripper | black/orange industrial | macro detail, blade proof, drill-use step | make callouts less crowded |
| DZ9JSS3BM | exhaust fan | green utility/industrial | airflow visualization, parameter strip, application scenes | more disciplined hierarchy |
| DZ63HS3BM | mask filters | blue/teal safety accessory | compatibility and material detail cards | clearer certification/fact gate |
| DR990W3BM | WiFi antenna | black tech accessory | frequency/gain proof, compatibility text | reserve readable text zones |
| D6MHW43BM | EV charging cable | purple/blue tech | large power proof, cable product weight, specs strip | avoid over-glow and simplify badges |
| DC2ZLS3BM | wall plug cube | white/teal electronics | CE/power/port badges, multi-use scenarios | improve layout polish |
| DYKFJW3BM | wooden cat puzzle | art/gift | product art as hero, package/assembly/use cards | make brand frame less intrusive |
| D5ZHSW3BM | solar system toy | black/orange STEM | premium toy drama, package contents, detail proof | typography consistency |
| DMF1PY2BM | bread proofing set | warm home/baking | package contents and use-step visuals | avoid beige sameness with stronger contrast |
| D0HYFS3BM | neck camera mount | light blue accessory | compatibility matrix and use-case grid | ensure real device scale |
| D9S4DV3BM | handheld retro console | blue gaming | suite-level game/lifestyle/feature sequence | reduce over-saturated generated look |
| DDD60W3BM | PS5 wall mount | dark RGB electronics | premium dark hero, installation steps, package proof | stronger geometry and alignment |
| DCNYHS3BM | bath toy | pastel baby toy | cute product-first baby palette and parent-child scene | avoid overly busy character collage |
| D346JS3BM | car LED bulbs | dark automotive | comparison beam, chip detail, plug-and-play proof | claim safety and technical accuracy |
| D0RH0S3BM | portable espresso | coffee lifestyle | black/gold premium appliance, extraction proof | reduce repeated claims; improve Romanian copy |
| D263HS3BM | robot dog toy | sci-fi toy | purple frame, action scene, function proof | avoid product deformation / over-fantasy |
| DBCC7C3BM | smartphone gimbal | technical blue/black | feature modules, app/gesture/extension proof | unify icon system and spacing |

## 6. Full 41-SKU Coverage Notes

The full sample set covers these design routes:

- `dark_tech_gaming`: 01, 12, 23, 31, 36, 41
- `industrial_tool_auto`: 04, 05, 13, 25, 27, 29, 34
- `electronics_utility`: 03, 08, 09, 10, 14, 17, 18, 22, 33, 37, 38, 39, 40
- `baby_home_soft`: 02, 07, 11, 21, 26, 32, 35
- `toy_gift_color`: 15, 19, 20, 24, 30, 36
- `fashion_accessory`: 28

This confirms that the brand-frame system is category-adaptive, not a single
static border.

## 7. Weaknesses We Can Beat

The sample is useful, but not the final quality bar.

Main weaknesses:

- Many images contain too much text for mobile scanning.
- Text language is mixed: English, Romanian, and awkward machine-translated
  phrases appear together.
- Some claims need stronger fact gating: wattage, lumens, certifications,
  compatibility, age ranges, battery life.
- Product fidelity varies; some scene images look generated or composited with
  weak physical realism.
- Typography and spacing are inconsistent between SKUs.
- Some suites repeat similar claims instead of answering new buyer questions.
- Main image is often strong as an ad card, but not always clean enough for
  strict platform-compliance interpretation.

Our advantage should be:

`same repeatability + better product truth + cleaner copy + better typography + stronger QA`

## 8. How To Use This In Our System

Add the sample as a reference pack, not a copied asset pack.

New artifacts created from this teardown:

- `workflow/design_systems/emag_excitat_reference.DESIGN.md`
- `workflow/suite_templates/emag_excitat_reference_6_suite.json`

Recommended generation route:

1. Build `ProductTruthPack` from product images, title, specs, package contents,
   and target eMAG category.
2. Select category palette:
   - tech/gaming
   - industrial/tool
   - baby/home
   - toy/gift
   - food/coffee
   - automotive
3. Generate or preserve the product visual with product-fidelity constraints.
4. Compose the brand frame, badges, labels, and border using deterministic
   overlay, not final image-model text.
5. Produce 6 default slots:
   - hero
   - feature proof
   - detail proof
   - parameter/compatibility
   - package contents
   - usage/scenario or instructions
6. Run QA:
   - thumbnail readability
   - product fidelity
   - no invented claims
   - no extra accessories
   - copy language consistency
   - suite non-redundancy
   - eMAG square image export

## 9. Next Reference Expansion

The next eMAG research should not scrape random products blindly. Use this
seller as the baseline, then collect stronger competitors by category:

1. Backpacks / bags / storage: because the previous backpack result exposed the
   gap most clearly.
2. Small appliances: coffee, baby food, kitchen tools.
3. Electronics accessories: chargers, gimbals, mounts, WiFi/BT devices.
4. Tools / auto: LED bulbs, cutters, hinges, repair devices.
5. Toys / gifts: visually rich products with package and use-case pressure.

For each category, collect:

- 10-20 high-quality eMAG products.
- 1 main image + 4-8 gallery images per product.
- description/detail images when available.
- product title/spec facts for claim checking.

Then compare against this seller on:

- brand-frame consistency
- product fidelity
- text density
- Romanian localization
- slot coverage
- claim safety
- thumbnail click strength

## 10. Practical Conclusion

The user's point is correct: this kind of eMAG image system is a much better
target than a generic AI scene image. It shows why a single backpack render can
look "nice" but still fail as marketplace creative.

The target should be:

`eMAG-ready image suite production`

not:

`one attractive generated image`

The production system should generate a controlled suite that is at least as
coherent as this Excitat sample, while being cleaner, more factual, more
localized, and easier to repair.
