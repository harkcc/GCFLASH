// Step 5 (revised): Generate brand frame using AI + composite with product images
// Strategy: Generate the decorative frame as a separate transparent PNG,
// then overlay it on product images using Playwright/Canvas

import { fal } from "@fal-ai/client";
import fs from "fs";
import path from "path";
import https from "https";

fal.config({
  credentials: "b66420fa-3d16-47f9-8f60-c4369eebcc7a:cf11ed54977c84f01dc2364eeba10806"
});

const OUTPUT_DIR = "./output_brand_frames";
if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

function downloadImage(url, filepath) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(filepath);
    https.get(url, (response) => {
      if (response.statusCode === 301 || response.statusCode === 302) {
        downloadImage(response.headers.location, filepath).then(resolve).catch(reject);
        return;
      }
      response.pipe(file);
      file.on("finish", () => { file.close(); resolve(filepath); });
    }).on("error", (err) => { fs.unlink(filepath, () => {}); reject(err); });
  });
}

// ============================================================
// APPROACH 1: Pure AI generation of brand frame
// ============================================================

const framePrompts = [
  {
    name: "baroque_blue_v1",
    model: "fal-ai/flux-pro/v1.1",
    prompt: `A decorative ornamental product image border frame design on a pure white background. The frame has an elegant baroque style with flowing blue and navy scrollwork, vine patterns, and ornate corner flourishes. The border is approximately 40-50 pixels wide on each side of a square frame. The interior of the frame is completely empty/white. The decorative elements include: curving acanthus leaves, flowing organic vine tendrils, and small floral rosettes at the corners. Color scheme: royal blue (#1a3a8a) to navy blue (#0d1b4a) gradient on the ornamental elements with subtle gold accent highlights. The frame has a slight 3D embossed effect with shadows. Top-right corner has space for a brand logo. Top-left corner has a small rectangular badge area. Professional product packaging border design, vector-quality rendering, clean crisp edges, isolated on white background, PNG style with potential for transparency.`,
  },
  {
    name: "baroque_blue_v2",
    model: "fal-ai/ideogram/v3",
    prompt: `Ornate decorative square border frame for product photography. Royal blue baroque scrollwork with flowing vine and leaf patterns along all four edges. Ornate corner flourishes with acanthus leaf motifs. The text "EXCITAT" appears in the top-right corner in a bold red decorative serif font with slight metallic sheen. A small pink/magenta "genius" badge label appears in the top-left corner. The center of the frame is completely empty white space for a product image. The overall style is elegant, premium e-commerce packaging border. Blue color range from royal blue to navy. Clean vector-like rendering quality on white background.`,
  },
  {
    name: "baroque_blue_v3",
    model: "fal-ai/flux-pro/v1.1",
    prompt: `Professional e-commerce product listing decorative border frame, square format, isolated on pure white background. Ornate blue baroque-style border with flowing organic scrollwork patterns, vine tendrils, small leaf clusters, and elegant corner pieces. The border runs along all four edges with slightly more elaborate decoration at the corners. Color: deep royal blue to sapphire blue gradient. The ornamental elements have a slightly raised, embossed appearance with subtle shadows. The center area is completely empty white space (for product placement). The frame width is about 5% of the total image on each side. Art nouveau meets baroque style. Clean, crisp rendering suitable for commercial use. No text, no logos — just the decorative frame.`,
  },
  {
    name: "modern_blue_v1",
    model: "fal-ai/flux-pro/v1.1",
    prompt: `Modern premium product border frame design on white background. A sleek blue border with subtle geometric patterns and organic flowing curves at the corners. The border combines clean straight lines with decorative corner elements featuring stylized leaves and abstract scrolls. Color: electric blue (#2563eb) with darker navy accents. Thin outer line with thicker inner decorative band. Contemporary luxury product packaging feel. Square format, empty white center. Minimal but sophisticated. High-end e-commerce aesthetic.`,
  }
];

async function generateFrame(frameConfig) {
  console.log(`\n[Frame Gen] ${frameConfig.name} via ${frameConfig.model}`);
  try {
    const input = {
      prompt: frameConfig.prompt,
      image_size: { width: 1024, height: 1024 },
      num_images: 1,
      output_format: "png"
    };

    // Add model-specific params
    if (frameConfig.model.includes("ideogram")) {
      input.style = "DESIGN";
      input.rendering_speed = "DEFAULT";
    } else {
      input.safety_tolerance = "5";
    }

    const result = await fal.subscribe(frameConfig.model, { input, logs: false });

    if (result.data?.images?.[0]?.url) {
      const filepath = path.join(OUTPUT_DIR, `frame_${frameConfig.name}.png`);
      await downloadImage(result.data.images[0].url, filepath);
      console.log(`  ✓ Saved: ${filepath}`);
      return { name: frameConfig.name, path: filepath, success: true };
    }
    console.log(`  ✗ No image URL`);
    return { name: frameConfig.name, success: false, error: "No URL" };
  } catch (err) {
    console.log(`  ✗ Error: ${err.message}`);
    return { name: frameConfig.name, success: false, error: err.message };
  }
}

// ============================================================
// APPROACH 2: Use existing brand images as reference (img2img)
// If user provides existing product images with the brand frame,
// we can extract and reference the frame style
// ============================================================

async function generateFrameFromReference(referenceImagePath) {
  console.log(`\n[Frame Ref] Generating frame variant from reference: ${referenceImagePath}`);

  if (!fs.existsSync(referenceImagePath)) {
    console.log(`  ✗ Reference image not found: ${referenceImagePath}`);
    return { success: false, error: "Reference not found" };
  }

  try {
    // First upload the reference image to fal.ai
    // For now, skip this — needs fal storage upload
    // In production: use IP-Adapter or ControlNet with the reference

    // Alternative: Use Flux Redux (image-to-image variation)
    console.log(`  Note: img2img reference-based frame generation`);
    console.log(`  requires uploading reference to fal.ai storage first.`);
    console.log(`  For Phase 0, use the pure generation approach.`);
    console.log(`  Phase 1 will add IP-Adapter for style consistency.`);

    return { success: false, error: "img2img not yet implemented for Phase 0" };
  } catch (err) {
    return { success: false, error: err.message };
  }
}

// ============================================================
// APPROACH 3: HTML/Playwright composite
// After generating the frame image, composite with product image
// ============================================================

function generateCompositeHTML(framePath, productImagePath, headline, subtext) {
  return `<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 0; }
  .container {
    width: 1200px;
    height: 1200px;
    position: relative;
    overflow: hidden;
  }
  .product-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    position: absolute;
    top: 0; left: 0;
    z-index: 1;
  }
  .brand-frame {
    width: 100%;
    height: 100%;
    object-fit: contain;
    position: absolute;
    top: 0; left: 0;
    z-index: 10;
    /* Frame should have transparent center */
    /* If not transparent, use mix-blend-mode */
    mix-blend-mode: multiply;
  }
  .brand-name {
    position: absolute;
    top: 18px;
    right: 28px;
    z-index: 20;
    font-family: 'Georgia', serif;
    font-size: 36px;
    font-weight: 900;
    font-style: italic;
    color: #cc2222;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    letter-spacing: 3px;
  }
  .genius-badge {
    position: absolute;
    top: 16px;
    left: 16px;
    z-index: 20;
    background: #e91e8c;
    color: white;
    font-family: Arial, sans-serif;
    font-size: 14px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 4px;
  }
</style>
</head>
<body>
  <div class="container">
    <img class="product-image" src="${productImagePath}" alt="Product">
    <img class="brand-frame" src="${framePath}" alt="Brand Frame">
    <span class="brand-name">EXCITAT</span>
    <span class="genius-badge">genius</span>
  </div>
</body>
</html>`;
}

// Main
async function main() {
  console.log("=== Brand Frame Generation ===\n");

  // Generate multiple frame variants
  const results = [];
  for (const config of framePrompts) {
    const result = await generateFrame(config);
    results.push(result);
  }

  // Summary
  console.log(`\n${"=".repeat(50)}`);
  console.log("BRAND FRAME GENERATION SUMMARY");
  console.log(`${"=".repeat(50)}`);

  const successful = results.filter(r => r.success);
  console.log(`Generated: ${successful.length}/${results.length} frames`);
  successful.forEach(s => console.log(`  ✓ ${s.path}`));

  // Generate composite HTML templates for each successful frame
  if (successful.length > 0) {
    console.log(`\nGenerating composite HTML templates...`);
    successful.forEach(frame => {
      const html = generateCompositeHTML(
        frame.path,
        "YOUR_PRODUCT_IMAGE.jpg",  // Replace with actual path
        "Sound Meets Light",
        "40W Bluetooth Lantern Speaker"
      );
      const htmlPath = path.join(OUTPUT_DIR, `composite_${frame.name}.html`);
      fs.writeFileSync(htmlPath, html);
      console.log(`  ✓ ${htmlPath}`);
    });
  }

  // Save results
  fs.writeFileSync(path.join(OUTPUT_DIR, "results.json"), JSON.stringify(results, null, 2));

  console.log(`\nNext steps:`);
  console.log(`  1. Review generated frames in ${OUTPUT_DIR}/`);
  console.log(`  2. Pick the best frame or provide your own as reference`);
  console.log(`  3. Use composite HTML to overlay frame on product images`);
  console.log(`  4. For Playwright rendering: npx playwright screenshot composite_xxx.html`);
}

main().catch(err => {
  console.error("Fatal error:", err);
  process.exit(1);
});
