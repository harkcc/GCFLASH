# Agent Internal Banner Generation Templates

These templates are designed for the AI Agent's internal `generate_image` tool to produce ecommerce banners that respect the standard 1140x456 (2.5:1 ratio) format.

Because typical image generators output square canvases by default, these templates instruct the model to render the active content inside a **central horizontal band (height 410px on a 1024x1024 square)**, allowing the post-processing script [crop_banner.py](file:///Users/cc/Desktop/photo_show/scripts/crop_banner.py) to extract a clean banner without clipping.

---

## Template 1: Glassmorphism Style (科技拟物玻璃)

### Input Attributes:
- **Product Image**: EV charging cable (or any product)
- **Product Title**: `[PRODUCT_TITLE]` (e.g., Premium EV Charging Cable)
- **Bullets**: `[SPEC_1]`, `[SPEC_2]`
- **Color Theme**: `[COLOR_1]` (e.g., dark navy), `[COLOR_2]` (e.g., deep violet), `[ACCENT_COLOR]` (e.g., neon cyan)

### Agent Prompt:
```text
Create a premium commercial advertising banner on a 1024x1024 square canvas. The active banner content must be designed strictly within a central horizontal band (aspect ratio 2.5:1, width 1024, height 410, between y=307 and y=717). The top 300 pixels and bottom 300 pixels must be solid [COLOR_1] space with no content. 

Within this central active band:
- Place the product from the input image on the right side, keeping its exact silhouette, details, and colors, with a soft realistic shadow.
- On the left side of this active band, render the text layout:
  1. A small rounded brand tag with the text 'EXCITAT'.
  2. A large premium bold headline '[PRODUCT_TITLE]'.
  3. A clean bullet-point list: '• [SPEC_1]', '• [SPEC_2]'.
- Background: A modern frosted glassmorphism stage floating on a [COLOR_1] and [COLOR_2] gradient background with soft blurred neon [ACCENT_COLOR] light circles.

Keep all active elements inside the central band so they will not be cropped.
```

---

## Template 2: Premium Industrial Dark Style (黑金金属工业)

### Input Attributes:
- **Product Image**: SSD Drive (or any tech product)
- **Product Title**: `[PRODUCT_TITLE]` (e.g., 22kW Ultra-Fast EV Charger)
- **Bullets**: `[SPEC_1]`, `[SPEC_2]`
- **Color Theme**: `[COLOR_1]` (e.g., charcoal black), `[COLOR_2]` (e.g., cobalt blue), `[ACCENT_COLOR]` (e.g., electric gold)

### Agent Prompt:
```text
Create a premium commercial advertising banner on a 1024x1024 square canvas. The active banner content must be designed strictly within a central horizontal band (aspect ratio 2.5:1, width 1024, height 410, between y=307 and y=717). The top 300 pixels and bottom 300 pixels must be solid [COLOR_1] space with no content.

Within this central active band:
- Place the product from the input image on the right side, preserving its exact geometry, shape, and colors, with a realistic drop shadow.
- On the left side of this active band, render the text layout:
  1. A small rounded brand tag with the text 'EXCITAT'.
  2. A large premium bold headline '[PRODUCT_TITLE]'.
  3. A clean bullet-point list: '• [SPEC_1]', '• [SPEC_2]'.
- Background: A dark [COLOR_1] brushed metal surface, diagonal carbon fiber grid patterns, with sharp glowing lines of [ACCENT_COLOR] and [COLOR_2] cutting across.

Keep all active elements inside the central band so they will not be cropped.
```

---

## Template 3: Organic Lifestyle Style (木纹生活肌理)

### Input Attributes:
- **Product Image**: Eco-friendly or home goods
- **Product Title**: `[PRODUCT_TITLE]` (e.g., Organic Bamboo Organiser)
- **Bullets**: `[SPEC_1]`, `[SPEC_2]`
- **Color Theme**: `[COLOR_1]` (e.g., soft beige), `[COLOR_2]` (e.g., natural oak wood), `[ACCENT_COLOR]` (e.g., olive green leaves)

### Agent Prompt:
```text
Create a premium commercial advertising banner on a 1024x1024 square canvas. The active banner content must be designed strictly within a central horizontal band (aspect ratio 2.5:1, width 1024, height 410, between y=307 and y=717). The top 300 pixels and bottom 300 pixels must be solid [COLOR_1] space with no content.

Within this central active band:
- Place the product from the input image on the right side, preserving its exact shape and colors, with a soft organic shadow.
- On the left side of this active band, render the text layout:
  1. A small rounded brand tag with the text 'EXCITAT'.
  2. A large premium bold headline '[PRODUCT_TITLE]'.
  3. A clean bullet-point list: '• [SPEC_1]', '• [SPEC_2]'.
- Background: A light [COLOR_1] travertine stone or terrazzo table surface next to a warm natural [COLOR_2] wood wall, with soft afternoon sunlight casting delicate diagonal shadows of [ACCENT_COLOR] across the scene.

Keep all active elements inside the central band so they will not be cropped.
```
