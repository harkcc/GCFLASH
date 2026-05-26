// Nano Banana 2 实测：人+产品+场景 — 3 种场景对比 FLUX 管道
// 运行: node test_nanobanana_person.mjs

import { fal } from "@fal-ai/client";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, "output_nanobanana_test");
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT);

const env = Object.fromEntries(
  fs.readFileSync(path.join(__dirname, "..", ".env"), "utf-8")
    .split("\n").filter(l => l.includes("=")).map(l => l.split("=").map(s => s.trim()))
);
fal.config({ credentials: env.FAL_KEY });

// 找之前合成的白底粉背包，用 fal 上传
const PRODUCT_IMG = path.join(__dirname, "output_backpack_test", "00_product_1776392227406.jpg");
console.log("📦 上传参考产品图到 fal storage...");
const productFalUrl = await fal.storage.upload(fs.readFileSync(PRODUCT_IMG));
console.log("   ✅", productFalUrl);

const tests = [
  {
    id: "01_back_view_airport",
    prompt: "A young woman seen from behind (back view, face not visible) wearing the exact same pink backpack from the reference image on both her shoulders, walking through a modern airport terminal at golden hour sunrise, warm natural light streaming through tall windows, a rolling suitcase beside her, editorial travel photography, shot on Hasselblad medium format, 85mm, shallow depth of field, candid aspirational moment, commercial product photography for women's travel bag listing",
    aspect: "1:1"
  },
  {
    id: "02_side_view_cafe",
    prompt: "A stylish woman in her late 20s sitting at a cafe window seat with the exact same pink backpack from the reference image placed on the chair next to her, side profile candid shot, morning coffee and laptop on the table, warm natural window light, Scandinavian minimalist cafe interior with plants, shot in the style of Away Travel editorial campaign, Hasselblad medium format, 50mm, 8K commercial quality",
    aspect: "1:1"
  },
  {
    id: "03_hero_studio",
    prompt: "A professional studio product photograph of the exact same pink women's backpack from the reference image, standing upright on cream linen surface with soft dried pampas grass in a white ceramic vase beside it, gold-rimmed coffee cup and open notebook in frame, soft natural daylight from the left, editorial composition in the style of Everlane product photography, no text, Phase One IQ4 medium format camera look, 8K",
    aspect: "1:1"
  }
];

for (const t of tests) {
  console.log(`\n━━━ ${t.id} ━━━`);
  const t0 = Date.now();
  try {
    const result = await fal.subscribe("fal-ai/nano-banana-2", {
      input: {
        prompt: t.prompt,
        image_urls: [productFalUrl],      // 传参考产品图
        aspect_ratio: t.aspect,
        num_images: 1,
        resolution: "1K",
        output_format: "jpeg"
      },
      logs: false
    });

    const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
    const imgUrl = result.data.images[0].url;
    const outPath = path.join(OUT, `${t.id}.jpg`);
    const buf = Buffer.from(await (await fetch(imgUrl)).arrayBuffer());
    fs.writeFileSync(outPath, buf);
    console.log(`  ✅ ${elapsed}s  → ${path.basename(outPath)}  (${(buf.length/1024).toFixed(1)} KB)`);
    if (result.data.description) console.log(`  📝 ${result.data.description.slice(0, 120)}...`);
  } catch (e) {
    console.error(`  ❌ Failed: ${e.message}`);
    if (e.body) console.error(JSON.stringify(e.body, null, 2).slice(0, 500));
  }
}

console.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log(`结果存放: ${OUT}`);
