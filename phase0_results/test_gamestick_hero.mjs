// Game Stick Hero — Nano Banana 2 生底图 + gaming_hero_4k skill 叠字
// 运行: node test_gamestick_hero.mjs

import { fal } from "@fal-ai/client";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, "output_gamestick_test");
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT);

const env = Object.fromEntries(
  fs.readFileSync(path.join(__dirname, "..", ".env"), "utf-8")
    .split("\n").filter(l => l.includes("=")).map(l => l.split("=").map(s => s.trim()))
);
fal.config({ credentials: env.FAL_KEY });

const ts = Date.now();

// ============ STEP 1: Nano Banana 2 生 hero 底图 ============
console.log("━━━ Step 1: Nano Banana 2 生 Game Stick hero 底图 ━━━");

const prompt = `Gaming product listing hero composite. Dramatic cyberpunk racing background with deep purple and electric blue neon gradient, motion blur streaks suggesting high speed, subtle hexagonal grid pattern. Center-right: a large curved gaming monitor floating in isometric 3D perspective, its screen displaying a photorealistic first-person racing game with sports cars on a neon-lit highway. Left-center foreground: a sleek white wireless HDMI dongle Game Stick device, about 15cm long, standing upright with subtle glow. Right-center: two white PS5-style wireless game controllers positioned naturally, one slightly in front, one behind. Bottom-center strip: a small flat-lay of accessories — HDMI cable, USB-C cable, and a USB wireless receiver — arranged horizontally with subtle spacing. Commercial advertising quality, dramatic rim lighting with cool cyan highlights, sharp product focus, floating particles and light leaks for atmosphere. IMPORTANT: leave the top-left corner completely empty (no visual elements) as reserved negative space for large text overlay. Leave the top-right corner empty as reserved space for brand logo. 4K resolution, photorealistic, e-commerce listing aesthetic.`;

const t1 = Date.now();
const result = await fal.subscribe("fal-ai/nano-banana-2", {
  input: {
    prompt,
    aspect_ratio: "1:1",
    num_images: 1,
    resolution: "1K",
    output_format: "jpeg"
  }
});
const bgUrl = result.data.images[0].url;
const bgPath = path.join(OUT, `gamestick_bg_${ts}.jpg`);
const buf = Buffer.from(await (await fetch(bgUrl)).arrayBuffer());
fs.writeFileSync(bgPath, buf);
console.log(`  ✅ ${((Date.now()-t1)/1000).toFixed(1)}s  → ${path.basename(bgPath)} (${(buf.length/1024).toFixed(0)} KB)  $0.08`);

// ============ STEP 2: skill 渲染 ============
console.log("\n━━━ Step 2: gaming_hero_4k skill 渲染 ━━━");

const inputs = {
  background_image_url: bgPath,
  hero_number: "4K",
  brand_name: "EXCITAT",
  brand_color: "#E11111",
  badge_text: "128GB",
  badge_color: "#1E88E5",
  spec_line_1: "31999+ Games",
  spec_line_2: "23 Emulators",
  canvas_size: 1024
};

const inputsPath = path.join(OUT, `gamestick_inputs_${ts}.json`);
fs.writeFileSync(inputsPath, JSON.stringify(inputs, null, 2));

const finalPath = path.join(OUT, `gamestick_hero_final_${ts}.png`);
const skillDir = path.join(__dirname, "design_skills", "gaming_hero_4k");

const t2 = Date.now();
execSync(`python3 "${skillDir}/render.py" "${inputsPath}" "${finalPath}"`, { stdio: "inherit" });
console.log(`  ✅ ${((Date.now()-t2)/1000).toFixed(1)}s  → ${path.basename(finalPath)}`);

console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
console.log(`Background URL: ${bgUrl}`);
console.log(`Final: ${finalPath}`);
