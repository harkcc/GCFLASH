# OZON Marketplace Design System (DESIGN.md)

> Category: Marketplace E-commerce (Russian Region)
> A high-conversion visual framework optimized for OZON's fast-browsing customer psychology (0.5s recognition, 1s click-intent, 3s trust-establishment).

---

## 1. Visual Theme & Atmosphere
OZON is a fast-paced, high-competition marketplace. Visual designs must be **direct, punchy, and structured**.
- **Product-First Atmosphere**: The product is the absolute focal point. Do not hide it behind smoke, overly complex glowing grids, or massive overlay banners.
- **Low-Key Backgrounds**: Backgrounds must use subtle, muted gradients or shallow depth-of-field scenes. The background's only job is to push the product forward.
- **Atmosphere Guidelines**:
  - *Tech/Electronics*: Matte graphite slate, dark anodized metal, subtle neon glows.
  - *Garden/Tools*: Light wooden chopping blocks, concrete tables, blurred forest green.
  - *Home Appliances*: Neutral warm plaster, beige tiles, soft studio window shadow.

---

## 2. Color Palette & Roles
The design operates on a strict **3-color palette limit** (excluding product body colors) to reduce cognitive load and avoid making the image look like a cluttered poster.

### 2.1 Color Palette Roles
- **Base (Canvas Background)**: `#12151a` (Dark Tech), `#f0f2f5` (Light Appliance), `#2b2d31` (Muted Grey Tool).
- **Ink (Text & Structure)**: `#ffffff` (on dark backgrounds) or `#17202a` (on light backgrounds).
- **Accent (Highlight Color)**: Highly saturated colors used ONLY for numeric badges and callouts.
  - *Tech/Outdoor Accent*: `#00ff88` (Vibrant Green) or `#00e5ff` (Cyan).
  - *Tool/Automotive Accent*: `#ff6b00` (Safety Orange).
  - *Home Appliance Accent*: `#005bff` (OZON Blue) or `#ffb800` (Warm Gold).

### 2.2 Accent Distribution Budget
- **Hero Main Image**: Max 1 main numeric badge (Accent Color) + 1 minor trust badge (Muted Accent/White).
- **Function/Selling-Point Image**: Max 3 badges or detail markers.

---

## 3. Typography Rules
- **No Model-Generated Text**: All text must be added as clean overlays (PSD/HTML/Pillow layers).
- **Hierarchy & Size**:
  - **Main Title**: Very large, bold sans-serif. Max 3-4 words (e.g. `ПЫЛЕСОС РУЧНОЙ`, `СЕКАТОР САДОВЫЙ`).
  - **Numeric Value**: Enormous, bold numbers. Set sizes to **2.5x to 3x** larger than the accompanying unit or explanation (e.g., `30` in 80pt, `дней` in 24pt).
  - **Badge Text**: Small, highly readable text inside a solid background shape. Max 2-3 words.

---

## 4. Component Stylings
All overlays and info badges must use unified, professional e-commerce shapes:

- **Numeric Badge**:
  - Solid rectangular badge with rounded corners (4px radius) or a perfect circle.
  - Filled with high-contrast color (Accent color or Dark Grey).
  - Wrapped around the number and unit to keep text together (e.g., `[ 960 mAh ]`, `[ x6 шт ]`).
- **Trust Badge & Branded Seal**:
  - Shield-shaped or checkmark badge.
  - For the **EXCITAT** brand, trust shields must not be generic. They must feature the **EXCITAT** brand text inside the badge (e.g., `EXCITAT Warranty / 1 Year` or `EXCITAT Quality`).
  - Styled with a premium metallic gold or neon cyan border matching the archetype, using high-readability sans-serif font.
  - Clean icons (e.g., 🛡️, ⚙️, 🔋, 📦) paired with short labels:
    - `EXCITAT Гарантия 1 год` (EXCITAT 1-Year Warranty)
    - `комплект` (accessories set)
    - `оригинал` (original brand guarantee)
- **Detail Connector Lines**:
  - Thin, 1px straight lines at a 45-degree angle.
  - Ends with a small solid circle pointing to the product feature. No arrowheads.
- **Scenario Inset**:
  - A small rounded square or circle in a bottom corner (max 20% width of canvas) showing the product in real-world use. Must have a thin white border (`2px`) to separate it from the main scene.

---

## 5. Layout Principles
OZON main images must strictly follow the **Universal Main Image Structure**:

```
+--------------------------------------------------------+
|  [CORE TITLE]                                          |
|  [SUBTITLE]                                            |
|                                                        |
|  (Badge: 960 mAh)                    (Badge: 2 года)   |
|         \                                /             |
|          \  +------------------------+  /              |
|             |                        |                 |
|             |     PRODUCT BODY       |                 |
|             |     (Dominant)         |                 |
|             |      60% Size          |                 |
|             |                        |                 |
|             +------------------------+                 |
|                                                        |
|                                       [Scenario Inset] |
|  [Kit Accessories / Bottom Badges]    [e.g., watch wrist] |
+--------------------------------------------------------+
```

- **Product Weight**: The product must occupy **60% to 75%** of the canvas. It must be placed centrally or diagonally, commanding the visual space.
- **Safe Margins**: Maintain a minimum **15px safe margin** around all text overlays, badges, and the canvas edge. No text or badges should touch the product contour.
- **Reading Order**: Eye should travel: Product Main Body (0.5s) -> Large Numeric Accent (1s) -> Detail/Trust Badges (3s).

---

## 6. Depth & Elevation
- **Contact Shadows**: All products must be visually grounded with soft, realistic contact shadows. Do not let products float in empty air unless it is a high-tech theme with visible light rays projecting upward.
- **Reflection**: If using a reflective surface, the reflection must be blurred (`50% opacity / heavy blur`) to prevent visual noise under the product.
- **Backdrop Vignette**: Use a subtle vignette (darker edges) to draw the eye directly to the center of the image.

---

## 7. Responsive Behavior
- **160px Legibility Check**: The final main image will be viewed as a tiny mobile thumbnail on search result pages.
- **Silhouette Validation**: If you blur your eyes or look from 2 meters away, you must still immediately recognize what the product is.
- **Badge Legibility**: The main numeric badge must remain readable at a distance. If it is too small, increase the number size and reduce the description text.

---

## 8. Do's and Don'ts

### Do:
- [x] Make the product massive (60%+ canvas area).
- [x] Use a maximum of 3 visual colors in the template design.
- [x] Use short Russian copy (max 3-4 words per label).
- [x] Pair feature text with clean international icons (🔌, 🔋, 🛠️, 🛡️).
- [x] Use large numbers with high-contrast color backing.
- [x] Put a realistic shadow beneath the product to ground it.

### Don't:
- [ ] Do not write long paragraphs of text (Keep it to single words or short phrases).
- [ ] Do not overlay text or badges directly on top of the product body.
- [ ] Do not use generic rainbow gradients or neon backgrounds that look like movie posters.
- [ ] Do not use English text for trust badges unless it is a globally recognized brand name or unit (e.g. `Type-C`, `SK5`).
- [ ] Do not let the product float without a physical shadow or floor.
