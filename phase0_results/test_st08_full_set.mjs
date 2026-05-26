// ST08 完整 8 图套测试 (图 3-8 批量生成; 图 1/2 已在 T1/T2 跑完)
// 运行: node test_st08_full_set.mjs

import { fal } from "@fal-ai/client";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, "output_st08_test");

const env = Object.fromEntries(
  fs.readFileSync(path.join(__dirname, "..", ".env"), "utf-8")
    .split("\n").filter(l => l.includes("=")).map(l => l.split("=").map(s => s.trim()))
);
fal.config({ credentials: env.FAL_KEY });

const plan = JSON.parse(fs.readFileSync(path.join(__dirname, "image_plan_st08.json"), "utf-8"));
const cfg = JSON.parse(fs.readFileSync(path.join(__dirname, "category_config_auto_accessory.json"), "utf-8"));

// 找缓存的 T2 产品 fg + mask
const files = fs.readdirSync(OUT);
const fgFile = files.find(f => f.startsWith("hero_01_fg_"));
const maskFile = files.find(f => f.startsWith("hero_02_mask_"));
if (!fgFile || !maskFile) {
  console.error("找不到 T2 缓存。先跑 test_st08_hero.mjs");
  process.exit(1);
}
const cachedFgPath = path.join(OUT, fgFile);
const cachedMaskPath = path.join(OUT, maskFile);
console.log(`📦 复用 T2 缓存: ${fgFile}`);

const ts = Date.now();
const report = { run: "full_set_images_3_to_8", timestamp: new Date().toISOString(), images: [] };
const feather = cfg.mask_params.feather_radius_px;

async function download(url, outPath) {
  const buf = Buffer.from(await (await fetch(url)).arrayBuffer());
  fs.writeFileSync(outPath, buf);
  return outPath;
}

async function fluxPro(prompt) {
  return fal.subscribe("fal-ai/flux-pro/v1.1", {
    input: { prompt, image_size: "square_hd", num_images: 1 }
  });
}

function composite(scenePath, fgPath, maskPath, outPath) {
  execSync(`python3 ${path.join(__dirname, "composite.py")} "${scenePath}" "${fgPath}" "${maskPath}" "${outPath}" ${feather}`);
}

async function runImage(spec, handler) {
  const t0 = Date.now();
  console.log(`\n━━━ Image #${spec.image_number} ${spec.image_type} ━━━`);
  try {
    const result = await handler(spec);
    const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
    console.log(`  ✅ ${elapsed}s  →  ${path.basename(result.final_path)}`);
    report.images.push({
      image_number: spec.image_number,
      image_type: spec.image_type,
      elapsed_s: parseFloat(elapsed),
      final_path: result.final_path,
      cost_usd: result.cost,
      method: result.method,
      status: "OK"
    });
    return result;
  } catch (e) {
    console.error(`  ❌ Failed: ${e.message}`);
    report.images.push({
      image_number: spec.image_number,
      image_type: spec.image_type,
      status: "FAIL",
      error: e.message
    });
  }
}

// ============ Handlers ============

async function compositeHandler(spec) {
  const sceneGen = await fluxPro(spec.prompt_flux + " , composition must leave empty space for a product to be placed in the lower-center area, no product visible in the scene");
  const scenePath = path.join(OUT, `img${spec.image_number}_${spec.image_type}_scene_${ts}.jpg`);
  await download(sceneGen.data.images[0].url, scenePath);

  const finalPath = path.join(OUT, `img${spec.image_number}_${spec.image_type}_final_${ts}.jpg`);
  composite(scenePath, cachedFgPath, cachedMaskPath, finalPath);
  return { final_path: finalPath, cost: 0.05, method: "flux_scene + composite" };
}

async function directHandler(spec) {
  const gen = await fluxPro(spec.prompt_flux);
  const finalPath = path.join(OUT, `img${spec.image_number}_${spec.image_type}_final_${ts}.jpg`);
  await download(gen.data.images[0].url, finalPath);
  return { final_path: finalPath, cost: 0.05, method: "flux_direct" };
}

async function gridHandler(spec) {
  const panelPrompts = [
    "Portable tire inflator in black and yellow connected to a silver sedan front tire in a clean home garage, warm overhead lighting, product in focus middle of frame, realistic car maintenance scene, 8K, no text",
    "Portable tire inflator in black and yellow with nozzle attached to a sport motorcycle tire at golden hour outdoor, natural sunset lighting, product in focus, 8K, no text",
    "Portable tire inflator in black and yellow on ground with nozzle on a mountain bike tire in a park, dappled morning sunlight through trees, product in focus, 8K, no text",
    "Portable tire inflator in black and yellow with needle nozzle inflating an orange basketball on wooden indoor court floor, bright sports arena lighting, product in focus, 8K, no text"
  ];
  const panelPaths = [];
  for (let i = 0; i < 4; i++) {
    const g = await fluxPro(panelPrompts[i]);
    const p = path.join(OUT, `img5_panel${i+1}_${ts}.jpg`);
    await download(g.data.images[0].url, p);
    panelPaths.push(p);
  }
  const finalPath = path.join(OUT, `img5_scene_multi_use_final_${ts}.jpg`);
  execSync(`python3 ${path.join(__dirname, "grid_compose.py")} ${panelPaths.map(p => `"${p}"`).join(" ")} "${finalPath}"`);
  return { final_path: finalPath, cost: 0.20, method: "4x flux_direct + pillow_grid" };
}

// ============ Main ============

const specs = plan.filter(p => p.image_number >= 3);

console.log(`\n🚀 ST08 Full Set Test — ${specs.length} 张图\n`);
const t0 = Date.now();

for (const spec of specs) {
  const id = spec.image_number;
  if (id === 3) await runImage(spec, compositeHandler);         // solution
  else if (id === 4) await runImage(spec, directHandler);        // detail (macro)
  else if (id === 5) await runImage(spec, gridHandler);          // multi_use grid
  else if (id === 6) await runImage(spec, directHandler);        // trust (flat lay)
  else if (id === 7) await runImage(spec, compositeHandler);     // specs
  else if (id === 8) await runImage(spec, compositeHandler);     // cta_gift
}

const totalS = ((Date.now() - t0) / 1000).toFixed(1);
const totalCost = report.images.reduce((s, x) => s + (x.cost_usd || 0), 0).toFixed(3);
report.total_elapsed_s = parseFloat(totalS);
report.total_cost_usd = parseFloat(totalCost);

fs.writeFileSync(path.join(OUT, `full_set_report_${ts}.json`), JSON.stringify(report, null, 2));

console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
console.log(`✅ Full set done`);
console.log(`   Images: ${report.images.filter(i => i.status === "OK").length}/${specs.length}`);
console.log(`   Total time: ${totalS}s`);
console.log(`   Total cost: $${totalCost}`);
console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
