// FLUX Kontext Multi 测试 — 3 张参考图 → 赛博 hero 场景
// 和 Nano Banana 对比
// 运行: node test_flux_kontext_multi.mjs

import { fal } from "@fal-ai/client";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, "output_flux_kontext_test");
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT);

const env = Object.fromEntries(
  fs.readFileSync(path.join(__dirname, "..", ".env"), "utf-8")
    .split("\n").filter(l => l.includes("=")).map(l => l.split("=").map(s => s.trim()))
);
fal.config({ credentials: env.FAL_KEY });

const ts = Date.now();

async function download(url, outPath) {
  const buf = Buffer.from(await (await fetch(url)).arrayBuffer());
  fs.writeFileSync(outPath, buf);
  return outPath;
}

async function uploadToFal(localPath) {
  return await fal.storage.upload(fs.readFileSync(localPath));
}

// ============ STEP 1: 用 Nano Banana 生 3 张干净白底参考图 ============
console.log("━━━ Step 1: 生 3 张白底游戏机参考图 ━━━");

const refPrompts = [
  {
    id: "ref1_gamestick_front",
    prompt: "Product photography on pure white seamless background: a sleek white wireless HDMI Game Stick Pro dongle device, small rectangular shape about 12cm long, glossy white plastic body with subtle LED indicator, HDMI connector visible on one end, USB-C port on the other, standing upright vertically centered, soft studio lighting with subtle shadow beneath, hyper-realistic product shot, 8K, no text on product, isolated on white"
  },
  {
    id: "ref2_controllers",
    prompt: "Product photography on pure white seamless background: two white PS5-style wireless game controllers, modern gaming gamepad design with dual analog sticks, d-pad, face buttons, triggers, arranged side by side at slight angle, soft studio lighting, subtle ground shadow, 8K commercial product shot, no text, isolated on white"
  },
  {
    id: "ref3_accessories",
    prompt: "Product photography on pure white seamless background: a flat-lay of gaming device accessories including one black HDMI cable coiled neatly, one black USB-C cable, and one small USB wireless receiver dongle, arranged horizontally, soft studio lighting, 8K commercial, isolated on white, no text"
  }
];

const refLocalPaths = [];
const refFalUrls = [];
for (const r of refPrompts) {
  const t1 = Date.now();
  const gen = await fal.subscribe("fal-ai/nano-banana-2", {
    input: { prompt: r.prompt, aspect_ratio: "1:1", num_images: 1, resolution: "1K", output_format: "jpeg" }
  });
  const localPath = path.join(OUT, `${r.id}_${ts}.jpg`);
  await download(gen.data.images[0].url, localPath);
  refLocalPaths.push(localPath);

  const falUrl = await uploadToFal(localPath);
  refFalUrls.push(falUrl);
  console.log(`  ✅ ${r.id} ${((Date.now()-t1)/1000).toFixed(1)}s  → ${path.basename(localPath)}`);
}

// ============ STEP 2: FLUX Kontext Multi 置入赛博场景 ============
console.log("\n━━━ Step 2: FLUX Kontext Multi 合成 hero ━━━");

const kontextPrompt = `Create a gaming product listing hero composite. Use the exact same white Game Stick Pro dongle device from reference image 1, the exact same two white PS5-style controllers from reference image 2, and the exact same accessories (HDMI cable, USB-C cable, USB receiver) from reference image 3. Preserve the exact product design, shape, proportions, and white color — do not modify the products.

Compose them in a dramatic cyberpunk racing scene: deep purple and electric blue neon gradient background with motion blur streaks, subtle hexagonal grid pattern on the floor. Place a large curved gaming monitor in the center-right displaying a photorealistic first-person racing game with sports cars on neon-lit highway. Place the Game Stick Pro dongle prominently in the left-center foreground. Place the two controllers positioned naturally on the right-center. Place the accessories in a small flat-lay at the bottom-center.

Commercial advertising quality, dramatic cool rim lighting, sharp product focus, floating particles. Leave top-left corner empty as reserved negative space for text overlay. Leave top-right corner empty for brand logo.`;

const t2 = Date.now();
const kontextResult = await fal.subscribe("fal-ai/flux-pro/kontext/multi", {
  input: {
    prompt: kontextPrompt,
    image_urls: refFalUrls,
    aspect_ratio: "1:1",
    num_images: 1,
    guidance_scale: 3.5,
    output_format: "jpeg"
  }
});
const kontextPath = path.join(OUT, `flux_kontext_hero_${ts}.jpg`);
await download(kontextResult.data.images[0].url, kontextPath);
console.log(`  ✅ ${((Date.now()-t2)/1000).toFixed(1)}s  → ${path.basename(kontextPath)}`);

// ============ STEP 3: 同 prompt 用 Nano Banana 2 多参考跑一次做对比 ============
console.log("\n━━━ Step 3: Nano Banana 2 多参考 (对照组) ━━━");

const t3 = Date.now();
const nbResult = await fal.subscribe("fal-ai/nano-banana-2", {
  input: {
    prompt: kontextPrompt,
    image_urls: refFalUrls,
    aspect_ratio: "1:1",
    num_images: 1,
    resolution: "1K",
    output_format: "jpeg"
  }
});
const nbPath = path.join(OUT, `nano_banana_multi_ref_${ts}.jpg`);
await download(nbResult.data.images[0].url, nbPath);
console.log(`  ✅ ${((Date.now()-t3)/1000).toFixed(1)}s  → ${path.basename(nbPath)}`);

console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
console.log(`参考图:     ${refLocalPaths.map(p => path.basename(p)).join(", ")}`);
console.log(`FLUX Kontext 输出: ${path.basename(kontextPath)}`);
console.log(`Nano Banana 输出:  ${path.basename(nbPath)}`);
console.log(`\n成本估算:`);
console.log(`  Nano Banana refs (3): $0.24`);
console.log(`  FLUX Kontext:         $0.04`);
console.log(`  Nano Banana multi:    $0.08`);
console.log(`  总计: ~$0.36`);
