#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { createRequire } from "module";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const requireFromPhase0 = createRequire(path.join(repoRoot, "phase0_results", "package.json"));
const { fal } = requireFromPhase0("@fal-ai/client");

function parseArgs(argv) {
  const args = { outDir: null, force: false, model: "fal-ai/flux-pro/v1.1" };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--out-dir") args.outDir = argv[++i];
    else if (arg === "--force") args.force = true;
    else if (arg === "--model") args.model = argv[++i];
  }
  if (!args.outDir) {
    throw new Error("Missing --out-dir <path>");
  }
  return args;
}

function readDotEnv(filePath) {
  if (!fs.existsSync(filePath)) return {};
  const env = {};
  const text = fs.readFileSync(filePath, "utf8");
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const eq = line.indexOf("=");
    if (eq < 0) continue;
    const key = line.slice(0, eq).trim();
    let value = line.slice(eq + 1).trim();
    value = value.replace(/^['"]|['"]$/g, "");
    env[key] = value;
  }
  return env;
}

async function download(url, outPath) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`download failed ${response.status} ${response.statusText}`);
  }
  const buffer = Buffer.from(await response.arrayBuffer());
  fs.writeFileSync(outPath, buffer);
}

async function generateOne({ model, prompt, outPath }) {
  const attempts = [
    { prompt, image_size: { width: 1200, height: 1600 }, num_images: 1, safety_tolerance: "5", output_format: "jpeg" },
    { prompt, image_size: "portrait_4_3", num_images: 1, safety_tolerance: "5", output_format: "jpeg" },
  ];

  let lastError = null;
  for (const input of attempts) {
    try {
      const result = await fal.subscribe(model, { input, logs: false });
      const url = result?.data?.images?.[0]?.url;
      if (!url) throw new Error("fal returned no image url");
      await download(url, outPath);
      return { model, outPath, url, input };
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError;
}

const variants = [
  {
    id: "v1",
    filename: "ozon_ssd_bg_v1_flux.jpg",
    prompt: [
      "Premium high-impact ecommerce product-card background for a 2.5 inch internal SSD upgrade.",
      "Ozon and Wildberries marketplace visual language: dark industrial tech stage, high contrast, glossy commercial design.",
      "Electric cyan and cobalt blue with hot amber-gold accents, circuit board traces, data-speed light streaks, floating memory-chip geometry, SATA connector silhouette motifs.",
      "3:4 vertical composition, central lower-right clean empty hero area for a real product cutout to be pasted later, top-left empty badge area, right-side empty callout area.",
      "Dramatic rim lighting, diagonal energy frame, sharp premium ad background, controlled density, no product, no package, no logo, no numbers, no text, no watermark, no fake readable glyphs."
    ].join(" ")
  },
  {
    id: "v2",
    filename: "ozon_ssd_bg_v2_flux.jpg",
    prompt: [
      "Aggressive Ozon Wildberries high-conversion marketplace card background for an internal SATA SSD.",
      "Make it cooler and more premium than a clean catalog template: neon tech tunnel, speed burst, circuit traces, carbon fiber texture, gold-blue energy shards, subtle memory-chip props.",
      "Leave a large clean center product stage with strong glow and shadow, reserve top-left for a huge numeric badge and top headline, reserve lower strip for trust badges.",
      "3:4 vertical advertising composition, bright diagonal border energy, thumbnail-readable contrast, no actual product, no product box, no brand logo, no text, no letters, no numbers, no watermark."
    ].join(" ")
  }
];

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const env = { ...readDotEnv(path.join(repoRoot, ".env")), ...process.env };
  if (!env.FAL_KEY) throw new Error("FAL_KEY is missing from .env or process env");
  fal.config({ credentials: env.FAL_KEY });

  const outDir = path.resolve(repoRoot, args.outDir);
  fs.mkdirSync(outDir, { recursive: true });

  const manifest = {
    generated_at: new Date().toISOString(),
    route: "fal_flux_background_only_then_local_product_text_composite",
    model: args.model,
    variants: []
  };

  for (const variant of variants) {
    const outPath = path.join(outDir, variant.filename);
    if (fs.existsSync(outPath) && !args.force) {
      manifest.variants.push({ ...variant, path: outPath, status: "cached" });
      console.log(`cached ${variant.id}: ${outPath}`);
      continue;
    }
    console.log(`generating ${variant.id} with ${args.model}`);
    const result = await generateOne({ model: args.model, prompt: variant.prompt, outPath });
    manifest.variants.push({
      ...variant,
      path: outPath,
      status: "generated",
      model: result.model,
      input_shape: result.input.image_size
    });
    console.log(`saved ${variant.id}: ${outPath}`);
  }

  fs.writeFileSync(path.join(outDir, "background_generation_manifest.json"), JSON.stringify(manifest, null, 2));
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
