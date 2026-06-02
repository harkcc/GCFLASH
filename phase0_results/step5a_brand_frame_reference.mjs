// Step 5A: Generate brand frame using existing product images as reference
// Uses IP-Adapter / Flux Redux for style-consistent frame generation
// Strategy: Feed existing Excitat product images → generate new frames in same style

import { fal } from "@fal-ai/client";
import fs from "fs";
import path from "path";
import https from "https";

const falKey = process.env.FAL_KEY;
if (!falKey) {
  throw new Error("Missing FAL_KEY environment variable.");
}
fal.config({
  credentials: falKey
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

// Upload a local image to fal.ai storage
async function uploadToFal(localPath) {
  console.log(`  Uploading ${path.basename(localPath)} to fal.ai storage...`);
  const file = new File(
    [fs.readFileSync(localPath)],
    path.basename(localPath),
    { type: "image/jpeg" }
  );
  const url = await fal.storage.upload(file);
  console.log(`  ✓ Uploaded: ${url}`);
  return url;
}

// ============================================================
// METHOD 1: Flux Redux (image variation)
// Takes a reference image → generates variations that keep the style
// Good for: "make me more frames that look like this one"
// ============================================================
async function generateViaRedux(referenceUrl, productColor, index) {
  console.log(`\n[Flux Redux] Generating frame variant #${index} (color: ${productColor})`);
  try {
    const result = await fal.subscribe("fal-ai/flux-pro/v1.1/redux", {
      input: {
        image_url: referenceUrl,
        prompt: `Same decorative ornamental product border frame design with EXCITAT brand logo in top-right corner, but change the color scheme to ${productColor}. Keep the baroque scrollwork vine pattern style, corner flourishes, and overall composition identical. The center should be empty for product placement. High quality e-commerce product frame.`,
        image_size: { width: 1024, height: 1024 },
        num_images: 1,
        guidance_scale: 3.5,
        num_inference_steps: 28
      },
      logs: false
    });

    if (result.data?.images?.[0]?.url) {
      const filepath = path.join(OUTPUT_DIR, `frame_redux_${productColor.replace(/\s+/g, '_')}_v${index}.jpg`);
      await downloadImage(result.data.images[0].url, filepath);
      console.log(`  ✓ Saved: ${filepath}`);
      return { method: "redux", path: filepath, success: true };
    }
    return { method: "redux", success: false, error: "No image URL" };
  } catch (err) {
    console.log(`  ✗ Error: ${err.message}`);
    return { method: "redux", success: false, error: err.message };
  }
}

// ============================================================
// METHOD 2: IP-Adapter (style transfer)
// Uses reference image as style guide + text prompt for specifics
// Good for: "keep this visual style but generate for a different product"
// ============================================================
async function generateViaIPAdapter(referenceUrl, productColor, productDesc, index) {
  console.log(`\n[IP-Adapter] Generating frame #${index} for: ${productDesc}`);
  try {
    // fal.ai Flux with IP-Adapter
    const result = await fal.subscribe("fal-ai/flux-general/image-to-image", {
      input: {
        image_url: referenceUrl,
        prompt: `Decorative ornamental product border frame for e-commerce listing. ${productColor} color scheme baroque scrollwork with vine and leaf patterns. EXCITAT brand logo text in top-right corner in complementary color. Empty center area for product placement. Premium quality, professional design. Product category: ${productDesc}.`,
        strength: 0.65, // How much to follow reference (0.5-0.8 good range)
        image_size: { width: 1024, height: 1024 },
        num_images: 1,
        num_inference_steps: 28
      },
      logs: false
    });

    if (result.data?.images?.[0]?.url) {
      const filepath = path.join(OUTPUT_DIR, `frame_ipadapter_${productColor.replace(/\s+/g, '_')}_v${index}.jpg`);
      await downloadImage(result.data.images[0].url, filepath);
      console.log(`  ✓ Saved: ${filepath}`);
      return { method: "ip_adapter", path: filepath, success: true };
    }
    return { method: "ip_adapter", success: false, error: "No image URL" };
  } catch (err) {
    console.log(`  ✗ Error: ${err.message}`);
    return { method: "ip_adapter", success: false, error: err.message };
  }
}

// ============================================================
// METHOD 3: Ideogram V3 direct generation with text
// Describe the frame in detail → Ideogram renders the EXCITAT text
// ============================================================
async function generateViaIdeogram(productColor, index) {
  console.log(`\n[Ideogram V3] Generating frame #${index} (${productColor})`);
  try {
    const result = await fal.subscribe("fal-ai/ideogram/v3", {
      input: {
        prompt: `A premium e-commerce product listing decorative border frame. Ornate ${productColor} baroque scrollwork border with flowing vine and leaf patterns along all four edges, elaborate corner flourishes with acanthus motifs. The bold stylized text "EXCITAT" appears in the top-right corner in an italic serif font with metallic sheen. The center of the frame is completely empty white space for product placement. Professional premium quality, clean vector-like rendering. No other text.`,
        image_size: { width: 1024, height: 1024 },
        num_images: 1,
        style: "DESIGN",
        rendering_speed: "DEFAULT"
      },
      logs: false
    });

    if (result.data?.images?.[0]?.url) {
      const filepath = path.join(OUTPUT_DIR, `frame_ideogram_${productColor.replace(/\s+/g, '_')}_v${index}.jpg`);
      await downloadImage(result.data.images[0].url, filepath);
      console.log(`  ✓ Saved: ${filepath}`);
      return { method: "ideogram", path: filepath, success: true };
    }
    return { method: "ideogram", success: false, error: "No image URL" };
  } catch (err) {
    console.log(`  ✗ Error: ${err.message}`);
    return { method: "ideogram", success: false, error: err.message };
  }
}

// ============================================================
// MAIN: Run all methods
// ============================================================
async function main() {
  console.log("=== Brand Frame Generation: Reference-Based ===\n");

  // Define color variants to test
  const colorVariants = [
    { color: "royal blue and navy", product: "grommet plier tool" },
    { color: "red orange and warm gold", product: "coffee machine parts" },
    { color: "deep purple and violet", product: "PS5 gaming accessories" },
    { color: "dark green and emerald", product: "outdoor bluetooth speaker" },
  ];

  const results = [];

  // Check if we have reference images to upload
  const photoDir = "../mnt/photo_show/photo";
  const referenceImages = fs.readdirSync(photoDir)
    .filter(f => f.endsWith(".jpg") || f.endsWith(".png"))
    .slice(0, 3); // Use first 3 as references

  let referenceUrl = null;

  if (referenceImages.length > 0) {
    console.log(`Found ${referenceImages.length} reference images`);
    console.log(`Using: ${referenceImages[0]} as primary reference\n`);

    try {
      referenceUrl = await uploadToFal(path.join(photoDir, referenceImages[0]));
    } catch (err) {
      console.log(`Failed to upload reference: ${err.message}`);
      console.log("Falling back to Ideogram-only generation\n");
    }
  }

  // Generate frames for each color variant
  for (let i = 0; i < colorVariants.length; i++) {
    const { color, product } = colorVariants[i];
    console.log(`\n${"=".repeat(50)}`);
    console.log(`Color Variant: ${color} (${product})`);
    console.log(`${"=".repeat(50)}`);

    // Always try Ideogram (doesn't need reference)
    const ideogramResult = await generateViaIdeogram(color, i + 1);
    results.push(ideogramResult);

    // If we have a reference image, also try Redux and IP-Adapter
    if (referenceUrl) {
      const reduxResult = await generateViaRedux(referenceUrl, color, i + 1);
      results.push(reduxResult);

      const ipResult = await generateViaIPAdapter(referenceUrl, color, product, i + 1);
      results.push(ipResult);
    }
  }

  // Summary
  console.log(`\n${"=".repeat(50)}`);
  console.log("BRAND FRAME GENERATION SUMMARY");
  console.log(`${"=".repeat(50)}`);

  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);

  console.log(`Total: ${results.length} attempts`);
  console.log(`Successful: ${successful.length}`);
  console.log(`Failed: ${failed.length}`);

  successful.forEach(s => console.log(`  ✓ [${s.method}] ${s.path}`));
  failed.forEach(f => console.log(`  ✗ [${f.method}] ${f.error}`));

  fs.writeFileSync(path.join(OUTPUT_DIR, "frame_results.json"), JSON.stringify(results, null, 2));
  console.log(`\nResults saved to ${OUTPUT_DIR}/frame_results.json`);
}

main().catch(err => {
  console.error("Fatal error:", err);
  process.exit(1);
});
