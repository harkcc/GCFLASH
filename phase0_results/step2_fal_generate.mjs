// Step 2: Generate images using fal.ai models (Flux 2 Pro + Ideogram V3)
// Reads image_plan.json and calls fal.ai APIs

import { fal } from "@fal-ai/client";
import fs from "fs";
import path from "path";
import https from "https";

// Configure fal.ai
fal.config({
  credentials: "b66420fa-3d16-47f9-8f60-c4369eebcc7a:cf11ed54977c84f01dc2364eeba10806"
});

const OUTPUT_DIR = "./output_fal";
if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

// Read the image plan
const plan = JSON.parse(fs.readFileSync("./image_plan.json", "utf-8"));

// Helper: download image from URL
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

// Generate with Flux 2 Pro (photorealistic, no text)
async function generateFluxPro(imageConfig, index) {
  console.log(`\n[Flux 2 Pro] Image ${index}: ${imageConfig.image_type} — "${imageConfig.headline_text}"`);
  try {
    const result = await fal.subscribe("fal-ai/flux-pro/v1.1", {
      input: {
        prompt: imageConfig.prompt_flux,
        image_size: { width: 1024, height: 1024 },
        num_images: 1,
        safety_tolerance: "5",
        output_format: "jpeg"
      },
      logs: false
    });

    if (result.data?.images?.[0]?.url) {
      const filepath = path.join(OUTPUT_DIR, `img${index}_${imageConfig.image_type}_flux_pro.jpg`);
      await downloadImage(result.data.images[0].url, filepath);
      console.log(`  ✓ Saved: ${filepath}`);
      return { model: "flux_pro", image: index, type: imageConfig.image_type, path: filepath, success: true };
    }
    console.log(`  ✗ No image URL in response`);
    return { model: "flux_pro", image: index, success: false, error: "No image URL" };
  } catch (err) {
    console.log(`  ✗ Error: ${err.message}`);
    return { model: "flux_pro", image: index, success: false, error: err.message };
  }
}

// Generate with Flux Pro v1.1 Ultra (if available)
async function generateFluxUltra(imageConfig, index) {
  console.log(`\n[Flux Ultra] Image ${index}: ${imageConfig.image_type} — "${imageConfig.headline_text}"`);
  try {
    const result = await fal.subscribe("fal-ai/flux-pro/v1.1-ultra", {
      input: {
        prompt: imageConfig.prompt_flux,
        aspect_ratio: "1:1",
        num_images: 1,
        safety_tolerance: "5",
        output_format: "jpeg",
        raw: false
      },
      logs: false
    });

    if (result.data?.images?.[0]?.url) {
      const filepath = path.join(OUTPUT_DIR, `img${index}_${imageConfig.image_type}_flux_ultra.jpg`);
      await downloadImage(result.data.images[0].url, filepath);
      console.log(`  ✓ Saved: ${filepath}`);
      return { model: "flux_ultra", image: index, type: imageConfig.image_type, path: filepath, success: true };
    }
    console.log(`  ✗ No image URL in response`);
    return { model: "flux_ultra", image: index, success: false, error: "No image URL" };
  } catch (err) {
    console.log(`  ✗ Error: ${err.message}`);
    return { model: "flux_ultra", image: index, success: false, error: err.message };
  }
}

// Generate with Ideogram V3 (text rendering)
async function generateIdeogram(imageConfig, index) {
  console.log(`\n[Ideogram V3] Image ${index}: ${imageConfig.image_type} — "${imageConfig.headline_text}"`);
  try {
    const result = await fal.subscribe("fal-ai/ideogram/v3", {
      input: {
        prompt: imageConfig.prompt_ideogram,
        image_size: { width: 1024, height: 1024 },
        num_images: 1,
        style: "REALISTIC",
        rendering_speed: "QUALITY"
      },
      logs: false
    });

    if (result.data?.images?.[0]?.url) {
      const filepath = path.join(OUTPUT_DIR, `img${index}_${imageConfig.image_type}_ideogram_v3.jpg`);
      await downloadImage(result.data.images[0].url, filepath);
      console.log(`  ✓ Saved: ${filepath}`);
      return { model: "ideogram_v3", image: index, type: imageConfig.image_type, path: filepath, success: true };
    }
    console.log(`  ✗ No image URL in response`);
    return { model: "ideogram_v3", image: index, success: false, error: "No image URL" };
  } catch (err) {
    console.log(`  ✗ Error: ${err.message}`);
    return { model: "ideogram_v3", image: index, success: false, error: err.message };
  }
}

// Generate with Flux 2 Pro (latest model, best quality)
async function generateFlux2Pro(imageConfig, index) {
  console.log(`\n[Flux 2 Pro] Image ${index}: ${imageConfig.image_type} — "${imageConfig.headline_text}"`);
  try {
    const result = await fal.subscribe("fal-ai/flux-2-pro", {
      input: {
        prompt: imageConfig.prompt_flux,
        image_size: { width: 1024, height: 1024 },
        num_images: 1,
        safety_tolerance: "5",
        output_format: "jpeg"
      },
      logs: false
    });

    if (result.data?.images?.[0]?.url) {
      const filepath = path.join(OUTPUT_DIR, `img${index}_${imageConfig.image_type}_flux2_pro.jpg`);
      await downloadImage(result.data.images[0].url, filepath);
      console.log(`  ✓ Saved: ${filepath}`);
      return { model: "flux2_pro", image: index, type: imageConfig.image_type, path: filepath, success: true };
    }
    console.log(`  ✗ No image URL in response`);
    return { model: "flux2_pro", image: index, success: false, error: "No image URL" };
  } catch (err) {
    console.log(`  ✗ Error: ${err.message}`);
    return { model: "flux2_pro", image: index, success: false, error: err.message };
  }
}

// Generate with Flux Schnell (fast drafts)
async function generateFluxSchnell(imageConfig, index) {
  console.log(`\n[Flux Schnell] Image ${index}: ${imageConfig.image_type} — "${imageConfig.headline_text}"`);
  try {
    const result = await fal.subscribe("fal-ai/flux/schnell", {
      input: {
        prompt: imageConfig.prompt_flux,
        image_size: { width: 1024, height: 1024 },
        num_images: 1,
        num_inference_steps: 4
      },
      logs: false
    });

    if (result.data?.images?.[0]?.url) {
      const filepath = path.join(OUTPUT_DIR, `img${index}_${imageConfig.image_type}_flux_schnell.jpg`);
      await downloadImage(result.data.images[0].url, filepath);
      console.log(`  ✓ Saved: ${filepath}`);
      return { model: "flux_schnell", image: index, type: imageConfig.image_type, path: filepath, success: true };
    }
    console.log(`  ✗ No image URL in response`);
    return { model: "flux_schnell", image: index, success: false, error: "No image URL" };
  } catch (err) {
    console.log(`  ✗ Error: ${err.message}`);
    return { model: "flux_schnell", image: index, success: false, error: err.message };
  }
}

// Main execution
async function main() {
  console.log("=== Phase 0: fal.ai Model Comparison ===");
  console.log(`Processing ${plan.length} images across 5 models\n`);

  const results = [];

  // Process images sequentially to avoid rate limits, but run models in parallel per image
  for (const img of plan) {
    const i = img.image_number;
    console.log(`\n${"=".repeat(60)}`);
    console.log(`IMAGE ${i}/${plan.length}: [${img.image_type}] "${img.headline_text}"`);
    console.log(`${"=".repeat(60)}`);

    // Run 5 models in parallel for this image
    const modelResults = await Promise.allSettled([
      generateFlux2Pro(img, i),       // 最新最强
      generateFluxPro(img, i),        // 经典稳定
      generateIdeogram(img, i),       // 文字渲染强
      generateFluxSchnell(img, i),    // 快速草稿
      // Only run Ultra for hero and lifestyle images (saves cost)
      (i <= 2) ? generateFluxUltra(img, i) : Promise.resolve({ model: "flux_ultra", image: i, success: false, error: "skipped" })
    ]);

    modelResults.forEach(r => {
      if (r.status === "fulfilled") results.push(r.value);
      else results.push({ success: false, error: r.reason?.message || "Unknown error" });
    });
  }

  // Summary
  console.log(`\n\n${"=".repeat(60)}`);
  console.log("GENERATION SUMMARY");
  console.log(`${"=".repeat(60)}`);

  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success && r.error !== "skipped");
  const skipped = results.filter(r => r.error === "skipped");

  console.log(`Total attempts: ${results.length}`);
  console.log(`Successful: ${successful.length}`);
  console.log(`Failed: ${failed.length}`);
  console.log(`Skipped: ${skipped.length}`);

  if (failed.length > 0) {
    console.log(`\nFailed details:`);
    failed.forEach(f => console.log(`  - Image ${f.image} (${f.model}): ${f.error}`));
  }

  console.log(`\nGenerated files:`);
  successful.forEach(s => console.log(`  ${s.path}`));

  // Save results manifest
  fs.writeFileSync(path.join(OUTPUT_DIR, "results.json"), JSON.stringify(results, null, 2));
  console.log(`\nResults manifest saved to ${OUTPUT_DIR}/results.json`);
}

main().catch(err => {
  console.error("Fatal error:", err);
  process.exit(1);
});
