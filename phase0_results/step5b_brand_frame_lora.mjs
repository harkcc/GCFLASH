// Step 5B: Train LoRA on Excitat brand frame style, then generate new frames
//
// Flow:
// 1. Collect 15-30 Excitat product images with brand frames (user provides)
// 2. Upload to fal.ai storage
// 3. Train Flux LoRA on fal.ai (~10-30 min)
// 4. Use trained LoRA to generate new brand frames
//
// NOTE: You need to place your Excitat product images (with brand frames)
// in the folder: ./lora_training_images/
// The more diverse images you provide (different colors, products), the better.
// Minimum 10 images, recommended 20-30.

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

const TRAINING_DIR = "./lora_training_images";
const OUTPUT_DIR = "./output_brand_frames_lora";

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
// STEP 1: Upload training images to fal.ai
// ============================================================
async function uploadTrainingImages() {
  if (!fs.existsSync(TRAINING_DIR)) {
    console.log(`\n❌ Training image directory not found: ${TRAINING_DIR}`);
    console.log(`\nPlease create the directory and add your Excitat product images:`);
    console.log(`  mkdir -p ${TRAINING_DIR}`);
    console.log(`  # Copy 15-30 Excitat product images with brand frames into this folder`);
    console.log(`  # Supported formats: .jpg, .png, .webp`);
    console.log(`\nTips for best LoRA results:`);
    console.log(`  - Include different color variants (blue, red, purple, green frames)`);
    console.log(`  - Include different products (tools, electronics, accessories)`);
    console.log(`  - All images should clearly show the decorative brand frame`);
    console.log(`  - The EXCITAT logo should be visible in each image`);
    console.log(`  - Minimum 10 images, recommended 20-30`);
    return null;
  }

  const images = fs.readdirSync(TRAINING_DIR)
    .filter(f => /\.(jpg|jpeg|png|webp)$/i.test(f));

  if (images.length < 5) {
    console.log(`\n❌ Only ${images.length} images found. Need at least 10 for LoRA training.`);
    console.log(`   Add more Excitat product images to: ${TRAINING_DIR}`);
    return null;
  }

  console.log(`Found ${images.length} training images. Uploading to fal.ai...`);

  const uploadedUrls = [];
  for (const img of images) {
    try {
      const filePath = path.join(TRAINING_DIR, img);
      const fileData = fs.readFileSync(filePath);
      const ext = path.extname(img).toLowerCase();
      const mimeType = ext === '.png' ? 'image/png' : ext === '.webp' ? 'image/webp' : 'image/jpeg';

      const file = new File([fileData], img, { type: mimeType });
      const url = await fal.storage.upload(file);
      uploadedUrls.push({
        url,
        caption: "EXCITAT brand decorative ornamental border frame, baroque scrollwork, vine patterns, product listing design"
      });
      console.log(`  ✓ Uploaded: ${img}`);
    } catch (err) {
      console.log(`  ✗ Failed: ${img} — ${err.message}`);
    }
  }

  console.log(`\nUploaded ${uploadedUrls.length}/${images.length} images`);
  return uploadedUrls;
}

// ============================================================
// STEP 2: Train Flux LoRA on fal.ai
// ============================================================
async function trainLoRA(trainingImages) {
  console.log(`\n=== Starting LoRA Training ===`);
  console.log(`Training images: ${trainingImages.length}`);
  console.log(`Trigger word: EXCITAT_FRAME`);
  console.log(`Expected training time: 10-30 minutes`);
  console.log(`Estimated cost: ~$3-5\n`);

  try {
    const result = await fal.subscribe("fal-ai/flux-lora-fast-training", {
      input: {
        images_data_url: trainingImages.map(img => img.url),
        // LoRA training config
        trigger_word: "EXCITAT_FRAME",
        steps: 1000,
        learning_rate: 0.0001,
        lora_rank: 16,
        caption_prefix: "EXCITAT_FRAME style, ",
        resolution: "1024",
        // Training images with captions
        images: trainingImages.map(img => ({
          url: img.url,
          caption: img.caption
        }))
      },
      logs: true,
      onQueueUpdate: (update) => {
        if (update.status === "IN_PROGRESS") {
          console.log(`  Training progress: ${update.logs?.map(l => l.message).join(' | ') || 'processing...'}`);
        }
      }
    });

    if (result.data?.diffusers_lora_file?.url) {
      console.log(`\n✓ LoRA training complete!`);
      console.log(`  LoRA weights URL: ${result.data.diffusers_lora_file.url}`);

      // Save the LoRA URL for later use
      const loraInfo = {
        lora_url: result.data.diffusers_lora_file.url,
        trigger_word: "EXCITAT_FRAME",
        training_images: trainingImages.length,
        trained_at: new Date().toISOString()
      };
      fs.writeFileSync(path.join(OUTPUT_DIR, "lora_info.json"), JSON.stringify(loraInfo, null, 2));
      console.log(`  LoRA info saved to ${OUTPUT_DIR}/lora_info.json`);

      return loraInfo;
    }

    console.log(`  ✗ Training completed but no LoRA file in response`);
    console.log(`  Response: ${JSON.stringify(result.data).substring(0, 500)}`);
    return null;
  } catch (err) {
    console.log(`  ✗ Training error: ${err.message}`);
    return null;
  }
}

// ============================================================
// STEP 3: Generate new brand frames using trained LoRA
// ============================================================
async function generateWithLoRA(loraInfo) {
  console.log(`\n=== Generating Brand Frames with LoRA ===`);
  console.log(`LoRA URL: ${loraInfo.lora_url}`);
  console.log(`Trigger word: ${loraInfo.trigger_word}\n`);

  const frameRequests = [
    {
      name: "blue_frame",
      prompt: `EXCITAT_FRAME style decorative ornamental product border frame, royal blue and navy color scheme, baroque scrollwork with flowing vine and leaf patterns, EXCITAT text in top-right corner, empty center for product, premium e-commerce listing design`,
    },
    {
      name: "red_warm_frame",
      prompt: `EXCITAT_FRAME style decorative ornamental product border frame, warm red orange and gold color scheme, baroque scrollwork with flowing vine patterns, EXCITAT text in top-right corner, empty center for product, premium quality`,
    },
    {
      name: "purple_gaming_frame",
      prompt: `EXCITAT_FRAME style decorative ornamental product border frame, deep purple and violet gradient, neon-tinged baroque scrollwork, EXCITAT text in top-right corner, empty center, gaming tech aesthetic`,
    },
    {
      name: "green_outdoor_frame",
      prompt: `EXCITAT_FRAME style decorative ornamental product border frame, forest green and emerald color scheme, natural vine baroque scrollwork, EXCITAT text in top-right corner, empty center, outdoor adventure feel`,
    },
    {
      name: "black_gold_frame",
      prompt: `EXCITAT_FRAME style decorative ornamental product border frame, black and gold luxury color scheme, elegant baroque scrollwork with gold leaf accents, EXCITAT text in top-right corner, empty center, premium luxury feel`,
    },
  ];

  const results = [];

  for (const req of frameRequests) {
    console.log(`\n[LoRA Gen] ${req.name}`);
    try {
      const result = await fal.subscribe("fal-ai/flux-lora", {
        input: {
          prompt: req.prompt,
          lora_url: loraInfo.lora_url,
          lora_scale: 0.85, // How strongly to apply the LoRA style
          image_size: { width: 1024, height: 1024 },
          num_images: 2, // Generate 2 variants per color
          num_inference_steps: 28,
          guidance_scale: 3.5,
        },
        logs: false
      });

      if (result.data?.images) {
        for (let i = 0; i < result.data.images.length; i++) {
          const imgUrl = result.data.images[i].url;
          const filepath = path.join(OUTPUT_DIR, `frame_lora_${req.name}_v${i + 1}.jpg`);
          await downloadImage(imgUrl, filepath);
          console.log(`  ✓ Saved: ${filepath}`);
          results.push({ name: req.name, variant: i + 1, path: filepath, success: true });
        }
      }
    } catch (err) {
      console.log(`  ✗ Error: ${err.message}`);
      results.push({ name: req.name, success: false, error: err.message });
    }
  }

  return results;
}

// ============================================================
// MAIN
// ============================================================
async function main() {
  console.log("=== Excitat Brand Frame LoRA Training & Generation ===\n");

  // Check if we already have a trained LoRA
  const loraInfoPath = path.join(OUTPUT_DIR, "lora_info.json");
  if (fs.existsSync(loraInfoPath)) {
    const loraInfo = JSON.parse(fs.readFileSync(loraInfoPath, "utf-8"));
    console.log(`Found existing LoRA: ${loraInfo.lora_url}`);
    console.log(`Trained on ${loraInfo.training_images} images at ${loraInfo.trained_at}\n`);

    const answer = process.argv.includes("--retrain") ? "retrain" : "generate";
    if (answer === "generate") {
      console.log("Using existing LoRA. (Pass --retrain to retrain)\n");
      const results = await generateWithLoRA(loraInfo);

      console.log(`\n${"=".repeat(50)}`);
      console.log("GENERATION SUMMARY");
      const successful = results.filter(r => r.success);
      console.log(`Generated: ${successful.length} frames`);
      successful.forEach(s => console.log(`  ✓ ${s.path}`));
      return;
    }
  }

  // Upload training images
  const trainingImages = await uploadTrainingImages();
  if (!trainingImages) {
    console.log("\n⚠ Cannot proceed without training images.");
    console.log("Please add Excitat product images to: lora_training_images/");
    process.exit(1);
  }

  // Train LoRA
  const loraInfo = await trainLoRA(trainingImages);
  if (!loraInfo) {
    console.log("\n⚠ LoRA training failed.");
    process.exit(1);
  }

  // Generate frames
  const results = await generateWithLoRA(loraInfo);

  // Summary
  console.log(`\n${"=".repeat(50)}`);
  console.log("FINAL SUMMARY");
  console.log(`${"=".repeat(50)}`);

  const successful = results.filter(r => r.success);
  console.log(`Generated: ${successful.length} brand frames`);
  successful.forEach(s => console.log(`  ✓ ${s.path}`));

  console.log(`\nLoRA weights saved for reuse: ${loraInfo.lora_url}`);
  console.log(`Trigger word: ${loraInfo.trigger_word}`);
  console.log(`\nTo generate more frames later:`);
  console.log(`  node step5b_brand_frame_lora.mjs`);
}

main().catch(err => {
  console.error("Fatal error:", err);
  process.exit(1);
});
