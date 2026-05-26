# External ecommerce frame and brand-badge reference scan

Date: 2026-05-22

Goal: stop inventing the EXCITED frame from scratch and build the next version from current marketplace-card, product-banner, template, and design-tool patterns.

## Why the previous corner badge failed

The v2/v3 tests treated the top-right mark as a decorative corner object. Strong ecommerce cards usually treat brand and frame as a system:

- product photo remains central and readable;
- brand mark is integrated into a plate, header, sticker, ribbon, stamp, or scene surface;
- frame thickness and brand mark are driven by thumbnail visibility, not by decorative complexity;
- visual richness comes from controlled depth: shadow, bevel, gloss, layered material, podium/plate, and product-specific atmosphere;
- production systems keep templates editable and parameterized, instead of relying on one-shot pixel generation.

## Search sources

### Marketplace-card AI / template tools

1. Picaz
   - Source: https://picazai.com/
   - Useful points:
     - competitor analytics, smart image editor, infographics, video covers;
     - product photo + description + optional style reference / brand guide;
     - template-based bulk production;
     - brand colors, logo, and guidelines kept consistent;
     - A/B test winners, then roll out winning design.
   - What we should copy:
     - treat our frame as a BrandStylePack + template family;
     - keep brand/logo locked;
     - generate several variants and review them against a thumbnail QA step.

2. Marketplace Hero
   - Source: https://marketplacehero.ru/
   - Useful points:
     - built for Wildberries, Ozon, Yandex Market;
     - examples are grouped as marketplace product cards and infographics;
     - editable control over headline, text, blocks, icons, tables, logo, and scenes;
     - workflow: upload photo -> choose scene -> download 2K card.
   - What we should copy:
     - define "main photo" and "infographic" as separate slot types;
     - top-right logo should be a controlled block/plate, not just decorative text;
     - product category should choose scene/plate style.

3. Kartochka WB
   - Source: https://www.kartochka-wb.ru/
   - Useful points:
     - WB/Ozon/Yandex templates;
     - background AI, 5000+ icons/elements, ready templates;
     - export as PNG/JPG/PDF;
     - design elements adapted for marketplaces.
   - What we should copy:
     - build a local element library: badges, corner plates, product-benefit icons, material strips;
     - do not rely on a single universal frame.

4. Orshot
   - Source: https://orshot.com/use-cases/t/auto-generate-e-commerce-images
   - Useful points:
     - design a template once, render ecommerce images at scale;
     - parameterize text, images, colors;
     - API, n8n, spreadsheets, dynamic URLs;
     - import brand logos, colors, fonts.
   - What we should copy:
     - our generator should treat product image, brand name, category color, badge style, copy, and overlay as parameters;
     - Playwright/SVG is a valid local equivalent for this.

5. Bannerbear
   - Source: https://www.bannerbear.com/help/articles/15-what-is-a-template/
   - Useful points:
     - reusable template editor;
     - dynamic objects: text boxes, image placeholders, simple shapes, custom SVGs, gradients, shadows, ratings, charts.
   - What we should copy:
     - EXCITED wordmark and border should be custom SVG objects;
     - product image and background should be placeholders;
     - shadows/gradients should be template parameters.

6. Figma Buzz
   - Source: https://help.figma.com/hc/en-us/articles/31271589645079-Create-marketing-assets-in-Figma-Buzz
   - Useful points:
     - templates for marketing assets;
     - update text and image fields without touching the design;
     - bulk create from CSV/XLSX;
     - useful for teams that need brand-consistent variations.
   - What we should copy:
     - lock design-sensitive layers;
     - expose only safe fields to the generation agent.

### Design/moodboard sources

1. Pinterest marketplace-card references
   - Searches:
     - `Wildberries Ozon product card design infographic marketplace`
     - `marketplace product card infographic Wildberries Ozon design`
     - `ecommerce product poster 3d badge label frame`
   - Example public pin surfaced:
     - https://www.pinterest.com/pin/wildberries-infographic-marketplace-card-wildberries-ozon-design-idea-logo-card-wildberries-product-card-design--282249101638978820/
   - Useful points:
     - WB/Ozon cards often use high-contrast product cards, badges, labels, icons, gradient panels, and dense but readable benefit zones.
   - What we should copy:
     - collect thumbnails by category;
     - crop only structural inspiration: badge type, logo placement, label geometry, frame thickness, icon density.

2. Dribbble product banner
   - Source: https://dribbble.com/search/product%20banner
   - Useful points:
     - product banners are tagged with ecommerce, social, branding, background, typography;
     - strong work usually combines product, background, typography, and brand system.
   - What we should copy:
     - frame should be integrated with background/podium/plate, not isolated.

3. Behance ecommerce banner
   - Source: https://www.behance.net/search/projects/e-commerce%20banner?locale=en_US
   - Useful points:
     - useful for higher-fidelity product advertising systems and campaign visuals.
   - What we should copy:
     - layered campaign language: hero surface, product stage, offer/brand plate, material lighting.

4. Freepik / Envato / GraphicsFamily
   - Sources:
     - https://www.freepik.com/psd/3d-e-commerce-banner
     - https://www.freepik.com/premium-psd/minimalist-e-commerce-sale-banner-with-3d-product-podiums_422132437.htm
     - https://elements.envato.com/best-seller-badge-6WWFEPC
     - https://graphicsfamily.com/downloads/3d-metallic-frame-modern-logo-mockup
   - Useful points:
     - common commercial assets use 3D podiums, metallic frames, sticker badges, best-seller labels, bevels, and glossy material.
   - What we should copy:
     - build controlled 3D-like SVG/CSS materials first;
     - use AI/image generation only for local texture and background, not for final text.

5. Canva listing-template sellers
   - Source: https://www.designries.com/product-page/designries-essential-oils-product-listing-templates-editable-canva-images
   - Useful points:
     - square 2000 x 2000 listing templates;
     - editable colors, branding, product photos;
     - made for Amazon/Etsy/eBay/Walmart/Shopify sellers.
   - What we should copy:
     - create several slots per listing suite, but keep the main image template strict.

## Visual patterns to test next

### Pattern A: Integrated Header Rail

Structure:

- thin outer frame;
- top-right brand is part of a horizontal rail;
- rail has a bevel and small underside shadow;
- left edge of rail is a dynamic notch/fold, not random shards.

Why it fits:

- closest to EXCITAT references;
- brand stays readable in thumbnails;
- easy to combine with product background.

### Pattern B: Die-Cut Sticker Badge

Structure:

- sticker-like top-right badge with folded corner;
- white or chrome wordmark;
- small offset shadow below;
- one accent edge, no noisy shards.

Why it fits:

- more ecommerce and commercial;
- works with clean product categories.

### Pattern C: Metallic Nameplate

Structure:

- small 3D plate with beveled metal/glass material;
- brand sits inside the plate;
- border color echoes the plate material;
- optional screw/shine should be extremely subtle.

Why it fits:

- better for tools, electronics, automotive, appliance products;
- more premium than flat color.

### Pattern D: Category Podium Frame

Structure:

- product stands on a subtle 3D base/podium;
- frame is thin;
- brand plate is connected to podium by light/shadow, not by heavy border.

Why it fits:

- solves the "border and product do not fuse" problem;
- Image2 can help generate the local background/podium atmosphere.

### Pattern E: Ribbon Seal

Structure:

- diagonal or horizontal ribbon tucked under product/edge;
- EXCITED appears as a seal or speed mark;
- border becomes secondary.

Why it fits:

- can feel more artistic than a pure rectangle;
- risky for main image if too much product area is consumed.

## Proposed next workflow

1. Collect reference board:
   - Pinterest/WB/Ozon pins;
   - Dribbble product banners;
   - Behance ecommerce banners;
   - Freepik/Envato badge and 3D product banner templates.

2. Annotate each reference by modules:
   - frame thickness;
   - brand placement;
   - badge/plate geometry;
   - material style;
   - product-background fusion;
   - category fit.

3. Build only three v4 prototypes:
   - Integrated Header Rail;
   - Die-Cut Sticker Badge;
   - Metallic Nameplate.

4. Test with one real product image:
   - deterministic SVG/HTML compose;
   - optional low-denoise Image2 for background/contact blending;
   - final deterministic overlay pass.

5. Thumbnail QA:
   - full 1500 px;
   - 300 px marketplace card preview;
   - compare against EXCITAT 41-crop sheet and Pinterest/WB/Ozon references.

## Guardrails for the next generation

- Do not invent the corner mark without a reference class.
- Do not add random spikes, dots, lines, or cyber UI marks.
- Do not let AI regenerate `EXCITED`.
- Do not make border thicker than the product area can tolerate.
- Prefer one strong material idea over several decorations.
- Every visual effect must map to a module: plate, fold, bevel, shadow, gloss, rail, ribbon, or product-stage surface.
