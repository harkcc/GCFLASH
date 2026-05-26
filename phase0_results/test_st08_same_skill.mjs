// 用 gaming_hero_4k skill 跑 ST08 充气泵（完全不改 skill 代码，只换输入 JSON）
// 证明 1 个 skill 可以跨品类
// 运行: node test_st08_same_skill.mjs

import { fal } from "@fal-ai/client";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, "output_gamestick_test");

const env = Object.fromEntries(
  fs.readFileSync(path.join(__dirname, "..", ".env"), "utf-8")
    .split("\n").filter(l => l.includes("=")).map(l => l.split("=").map(s => s.trim()))
);
fal.config({ credentials: env.FAL_KEY });

const ts = Date.now();

// === ST08 底图 — 用 Nano Banana 2 生工业汽车风 hero 合成 ===
console.log("━━━ ST08 hero 底图生成（同一 skill，换品类） ━━━");

const prompt = `Automotive tool product listing hero composite. Dramatic industrial dark garage background with moody charcoal gray tones and subtle warm amber edge lighting, concrete floor with subtle hex pattern. Center: a sleek black portable digital tire inflator with bright yellow side accents, foldable top handle, bright green LED digital display visible showing "150 PSI", integrated LED work light glowing. Left-center: partially visible sports car tire with wet asphalt reflection. Bottom-center strip: small flat-lay of inflation nozzles, car cigarette lighter plug, and spare fuse arranged horizontally with subtle spacing. Commercial advertising quality, dramatic rim lighting from upper-left, cool shadows, sharp product focus. IMPORTANT: leave top-left corner empty as reserved negative space for large text overlay. Leave top-right corner empty for brand logo. 4K resolution, photorealistic, e-commerce listing aesthetic.`;

const t1 = Date.now();
const result = await fal.subscribe("fal-ai/nano-banana-2", {
  input: { prompt, aspect_ratio: "1:1", num_images: 1, resolution: "1K", output_format: "jpeg" }
});
const bgUrl = result.data.images[0].url;
const bgPath = path.join(OUT, `st08_bg_${ts}.jpg`);
fs.writeFileSync(bgPath, Buffer.from(await (await fetch(bgUrl)).arrayBuffer()));
console.log(`  ✅ ${((Date.now()-t1)/1000).toFixed(1)}s  → ${path.basename(bgPath)}`);

// === 同一 skill，不同输入 ===
const inputs = {
  background_image_url: bgPath,
  hero_number: "150PSI",         // 不是 4K 了，变工业参数
  brand_name: "EXCITAT",
  brand_color: "#FFD500",        // 黄色 brand (ST08 品牌色)，不是红色
  badge_text: "AUTO-STOP",       // 不是 128GB，变功能徽章
  badge_color: "#FF6D00",        // 橙色，不是蓝色
  spec_line_1: "±1.5 PSI ACCURACY",
  spec_line_2: "4 NOZZLES · 3.5M CABLE",
  canvas_size: 1024
};

const inputsPath = path.join(OUT, `st08_inputs_${ts}.json`);
fs.writeFileSync(inputsPath, JSON.stringify(inputs, null, 2));

const finalPath = path.join(OUT, `st08_hero_same_skill_${ts}.png`);
const skillDir = path.join(__dirname, "design_skills", "gaming_hero_4k");

const t2 = Date.now();
execSync(`python3 "${skillDir}/render.py" "${inputsPath}" "${finalPath}"`, { stdio: "inherit" });
console.log(`  ✅ Render ${((Date.now()-t2)/1000).toFixed(1)}s  → ${path.basename(finalPath)}`);
console.log(`\n完成！同一 skill 跨品类: Gaming → Automotive`);
