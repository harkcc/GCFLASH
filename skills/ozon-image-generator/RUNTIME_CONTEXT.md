# Ozon Main Image Runtime Context

This file distills the stable late-stage runs from the original Antigravity
conversation `photo_show / Creating Ozon Main Image Skill` into
prompt-compilation rules. It is not a gallery reference file and must not be used
as a fixed visual template. Use it to decide what context the prompt compiler
must load and how that context should influence a new product-specific prompt.

Do not mix in later PS5 v6 iterations from other conversations when using this
file. The extraction target here is only the original conversation that produced
the oscilloscope, SUV mattress, PS5 wall mount, and solar-system stable outputs.

## Locked Runtime Version

Use `fusion_v1` as the current default prompt compiler.

The local comparison had three meaningful versions:

1. `strict_original`: direct replay of the original stable Antigravity prompt
   shape.
2. `current_sop`: the local SOP interpretation before the final merge.
3. `fusion`: the selected version after square-size control and product-lighting
   routing were compared.

`fusion_v1` means the planning model may analyze the product, but the final
image prompt is compiled by the fusion skeleton. Do not use the planner's raw
final paragraph as the production prompt, because that path can drop selected
badges or invent extra modules such as bottom STEM/SKILL panels.

## Context Sources That Influence The Prompt

The final image prompt must be compiled from these layers, in this order:

1. **Source product truth**
   - Treat the uploaded product image as the visual ground truth.
   - Identify immutable features: shape, material, ports, controls, accessories,
     colors, labels, relative scale, and all physical connections.
   - Explicitly forbid deformed product geometry, invented accessories, wrong
     port placement, wrong cable paths, and category-incompatible props.
   - Do not choose the background first. The product image determines the scene,
     lighting, props, badges, and physical support logic.

2. **Object and physical logic**
   - Decide how the product stands, hangs, plugs in, opens, inflates, charges,
     glows, supports weight, or connects to accessories.
   - The final prompt must preserve believable relationships between parts:
     mounts support consoles, chargers hold controllers, pumps/nozzles belong
     with mattresses, probes connect to ports, planetary arms attach to gears.
   - Remove or forbid scene elements that would make the product functionally
     confusing, such as floating support brackets, disconnected cables, wrong
     accessory scale, or decorative props that imply the wrong use case.

3. **Hero pose and staging decision**
   - The universal Ozon layout fixes the page skeleton, not the product pose.
   - Keep the product dominant in the center zone, but choose the pose per SKU:
     front view, slight side angle, 3/4 angle, mounted state, expanded state,
     plugged-in state, or accessory-connected action.
   - Prefer the pose that makes the product's function and physical logic most
     visible. Do not default to a flat front catalog view when a side or 3/4
     angle better explains depth, cables, charging, mounting, support, or scale.
   - Active elements need both a contact point and a visible result. Avoid vague
     wording such as "toward the PCB" or "near the dock"; say what touches what
     and what visual outcome proves the function.

4. **Product facts and commercial hooks**
   - Extract the primary numeric click hook, 2-3 feature badges, trust badge,
     compatibility, kit/accessory contents, and the main usage scenario.
   - Use product-specific hooks, not generic "premium quality" filler.

5. **Category router and background depth**
   - Map each product to a frame family, accent palette, and ambient staging
     scene before writing the image prompt.
   - Tech/gaming: dark slate, cyber cyan, magenta/cyan neon, backlight glow.
   - Measurement/lab tech: electronics workbench, PCB/tools bokeh, cyan signal
     energy only where it physically belongs.
   - Auto comfort/outdoor: real vehicle trunk or outdoor utility scene, warm
     sunlight or rugged teal/orange accents.
   - STEM/creative kit: study desk, educational/gift atmosphere, warm science
     lighting, category-relevant background details.
   - The scene must explain the product. Do not use a generic studio slab when a
     scenario-specific environment makes the object easier to understand.
   - Backgrounds work best as three layers: physical support surface, low-detail
     category depth cue, and functional/product-matched light source. For PS5,
     the wall is only the support surface; the blurred gaming room, monitor/shelf
     glow, or side neon line creates category depth.

6. **Product-derived lighting**
   - The original stable prompts did not paste a fixed lighting category into
     the final prompt. They converted product logic into natural image language.
   - Infer five internal fields before writing the final prompt:
     `physical_light_source`, `lighting_role`, `lighting_effect_on_scene`,
     `shadow_and_depth_behavior`, and `lighting_overuse_risk`.
   - The final prompt should describe the visible light, not the internal label.
     Say "warm sunlight streams through the SUV side windows" rather than
     "practical_natural"; say "the central Sun sphere glows warmly" rather than
     "product_emissive".
   - Do not add glow just to make the image look premium. Glow, sparks, beams,
     RGB washes, and strong rim light must come from a believable object or
     scene source.

   Stable-case lighting map:

   | Product | Physical light source | Commercial role | Visible effect | Overuse risk |
   | --- | --- | --- | --- | --- |
   | Oscilloscope | Screen glow, probe tips touching PCB pads, lab task/rim light | Prove live electrical measurement and make the side/3D pose feel active | Small cyan sparks at probe tips, subtle waveform/screen glow, cool highlights on blue bumpers and lab bench | Do not turn sparks into fantasy lightning or fill the whole background with neon |
   | SUV mattress | Sunlight through car side windows and soft car interior ambient light | Show real fit, fabric texture, and comfortable travel use | Warm daylight across grey flocked surface, soft shadows on trunk carpet, clean accessory flat-lay strip | Do not add gaming-style neon, beams, or dramatic colored rim light |
   | PS5 wall mount | RGB charger dock, cyan/magenta room strips, subtle monitor/shelf glow | Show charging/RGB function and gaming-room relevance | Controlled RGB wash under controllers, cyan side glow behind wall mount, clean dark wall separation | Do not make the wall busy or flood the product with rainbow light |
   | Solar-system kit | Glowing central Sun sphere plus warm study-room ambient light | Make the STEM object feel educational, magical, and mechanically premium | Warm orange highlights on gears and planetary arms, soft reflection on walnut desk, starry-window depth | Do not overexpose the Sun or replace the model with abstract cosmic effects |

7. **Ozon main-card layout**
   - The product occupies 60-75% of the canvas and remains the first focal point.
   - Top-left: short title and primary numeric badge.
   - Top-right: EXCITAT brand shelf.
   - Right side: vertical feature badge stack.
   - Bottom or corner area: product-specific support information such as kit
     accessories, trust badge, or a small scenario/detail inset when it actually
     improves object comprehension.
   - Trust badge: branded or product-specific, placed without touching product
     contour.
   - Maintain clear safe margins around every overlay.

8. **EXCITAT brand lockup**
   - For tech, gaming, and audio products, prefer the Speed Lightning Shelf:
     slanted dark brushed-metal or glass backplate, cyan neon boundary glow,
     bold white EXCITAT wordmark, energetic speed/lightning details.
   - For tools/hardware, adapt the shelf toward darker metal and safety orange.
   - For STEM/gift/science products, adapt the shelf accent to warm solar-gold
     or category-compatible energy colors.
   - The brand lockup must look like part of the e-commerce card, not a pasted
     sticker.

9. **Rendering mode**
   - For Antigravity `default_api:generate_image`, write one full image-to-image
     prompt that includes product preservation, staging, layout, text badges,
     brand shelf, and trust/accessory area without production-layer terminology.
   - For explicit exact-SKU production workflows only, split the task into
     background generation, product cutout locking, local overlays, and visual
     QA. Do not let that production route leak into one-shot prompt tests.
   - Do not accidentally send a background-only prompt to a one-shot full-card
     image model.

10. **Language routing**
   - Follow the user's requested output language or the product/source context.
   - The original stable Antigravity Ozon examples used English/Latin text
     (`WALL MOUNT KIT`, `5-in-1`, `Dual Charger`, etc.). Do not automatically
     switch to Russian/Cyrillic just because the marketplace is OZON.
   - Keep language consistent within the image. Do not mix Russian, Romanian,
     and English unless the user explicitly asks for multilingual output.

## Upstream Local Memory To Preserve

The original stable conversation was not isolated from prior local design-rule
work. When restarting this agent, preserve the following upstream context as
rules, not as visual references:

1. **Pure Ozon scan logic**
   - Use the 0.5s / 1s / 3s funnel: instant product recognition, one dominant
     numeric reason to click, then trust/accessory reassurance.
   - Structure the card in three information layers: dominant product body,
     2-3 side selling points, and bottom/corner trust or accessory information.
   - Keep copy short, icon-like, and mobile readable. Avoid paragraph claims.

2. **Dynamic layout routing**
   - Do not let one successful card become a fixed template.
   - Select layout from product category and physical form: tech/gadget dynamic
     poster, soft home/appliance clean card, rugged industrial/garden scene, or
     product-specific EXCITAT frame family when the 41-reference system applies.
   - The route must be chosen after source-image analysis, not from a default
     brand skin.

3. **EXCITAT 41-reference design system**
   - Reuse the mechanism: brand shelf/shard, category-specific frame family,
     numeric badge, feature icon stack, bottom spec/accessory band, and optional
     detail inset.
   - Do not copy any prior product image, SKU composition, or fixed case layout.
   - Do not import earlier "Pure OZON has no brand shelf" exclusions into this
     skill. The final original conversation explicitly stabilized around an
     EXCITAT top-right brand shelf.

4. **Product-fidelity production route**
   - Use original cutout + generated background + deterministic overlay only
     when exact SKU production fidelity is explicitly required.
   - If using Antigravity's one-shot `generate_image` path for quality testing,
     the prompt must still name the product-locking and object-logic priorities
     explicitly because the tool may redraw the full card.
   - Do not include matting, inpaint, PSD, HTML, or deterministic overlay
     language in the one-shot prompt compiler.

5. **Debug context to exclude**
   - Exclude failed or middle-stage modes: generic odd/fixed template cards,
     over-heavy borders, inherited batch-image styling, language mixing, and
     coordinate/style instructions that can leak as visible text.
   - Exclude later PS5 v6 iterations from other conversations.

## Stable Prompt Shape

Use this sequence when compiling the model prompt:

1. Extract/preserve the source product, naming immutable features.
2. Reason about the product's physical logic, usage state, and accessory
   relationships.
3. Choose the strongest hero pose and product action inside the fixed center
   product zone.
4. State the category-specific scene and why it fits the product.
5. Specify the 1:1 Ozon main-card composition and product scale.
6. Specify lighting, shadows, backlight, material contrast, and depth.
7. Specify the EXCITAT brand shelf style.
8. Specify title, numeric badge, feature badges, trust/accessory area, and any
   scenario/detail inset only when useful for that product.
9. Specify the exact language/script for all visible text.

## Information Not Strongly Enforced In The Original Skill

These rules were present in stable late-stage context but were not strong enough
inside the initial Skill file:

- Category-specific scene routing is more important than a generic dark/light
  palette choice.
- Background quality comes from support surface plus shallow category depth cue
  plus functional light source. Do not collapse a product scene into a bare wall,
  texture, or gradient.
- Product pose is a product-specific decision inside the fixed main-card
  skeleton. Center dominance does not mean default front-view staging.
- EXCITAT needs a reusable wordmark/shelf system, not only a trust-seal mention.
- The prompt compiler must choose product-specific text and badge content from
  product facts before writing any visual prose.
- The bottom/corner support area should be product-specific. In the original
  stable cases it could be an accessory strip, a fit badge, a warranty badge, or
  a detail/scenario inset; it should not be forced into one fixed component.
- One-shot image tools need a complete full-card prompt; compositing tools need
  separated background/product/overlay instructions.
- Product fidelity must include object logic: accessories, charging bases,
  cables, ports, hinges, handles, mounts, and physical support points must make
  sense.
- Background choice must be downstream of product understanding. The stable
  original outputs matched the background to the product category and object
  state rather than applying one universal decorative scene.
- The full-card generation prompt must explicitly name all visible overlay copy.
  A short background/brand prompt is insufficient for reproducing the stable
  Antigravity route.
- Exact production repeatability may require a separate layer split, but that is
  not the default route for reproducing the original one-shot Antigravity
  exploration quality.
