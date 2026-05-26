// Taygeer 女士背包 — 完整 8 图套测试 + bbox 修复验证
// 运行: node test_backpack_full_set.mjs

import { fal } from "@fal-ai/client";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, "output_backpack_test");
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT);

const env = Object.fromEntries(
  fs.readFileSync(path.join(__dirname, "..", ".env"), "utf-8")
    .split("\n").filter(l => l.includes("=")).map(l => l.split("=").map(s => s.trim()))
);
fal.config({ credentials: env.FAL_KEY });

const plan = JSON.parse(fs.readFileSync(path.join(__dirname, "image_plan_backpack.json"), "utf-8"));
const cfg = JSON.parse(fs.readFileSync(path.join(__dirname, "category_config_backpack_women.json"), "utf-8"));
const feather = cfg.mask_params.feather_radius_px;

const ts = Date.now();
const report = { run: "backpack_full_set", timestamp: new Date().toISOString(), images: [] };

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

async function birefnet(imageUrl) {
  return fal.subscribe("fal-ai/birefnet", { input: { image_url: imageUrl } });
}

function compositeBbox(scenePath, fgPath, maskPath, outPath, bbox) {
  const bboxArg = bbox ? `"${bbox.join(",")}"` : "";
  execSync(`python3 ${path.join(__dirname, "composite.py")} "${scenePath}" "${fgPath}" "${maskPath}" "${outPath}" ${feather} ${bboxArg}`, { stdio: "inherit" });
}

// ============ STEP 0: 生成白底产品主源图 ============
console.log("━━━ STEP 0: 生成白底 Taygeer 背包主源图 ━━━");

const productPrompt = "Product photography of a pink women's travel backpack on pure white seamless background, 3/4 front angle, soft studio lighting with subtle ground shadow, water-resistant oxford fabric with visible weave texture, gold-tone YKK zippers, main compartment and side water bottle pocket visible, shoe pouch on bottom, padded back panel with dual shoulder straps, top grab handle, clean modern women's travel bag design, dusty rose pink color #E8A5B8, product fills 65% of frame centered, no text overlay, 8K commercial catalog photography, hyper-realistic";

let t = Date.now();
const prodGen = await fluxPro(productPrompt);
const productUrl = prodGen.data.images[0].url;
const productPath = path.join(OUT, `00_product_${ts}.jpg`);
await download(productUrl, productPath);
console.log(`  ✅ ${((Date.now()-t)/1000).toFixed(1)}s  → ${path.basename(productPath)}`);

// BiRefNet 抠图（全套复用）
t = Date.now();
const bg = await birefnet(productUrl);
const fgUrl = bg.data.image?.url;
const fgPath = path.join(OUT, `00_fg_${ts}.png`);
await download(fgUrl, fgPath);

// 从 alpha 提 mask
const maskPath = path.join(OUT, `00_mask_${ts}.png`);
execSync(`python3 -c "from PIL import Image; Image.open('${fgPath}').convert('RGBA').split()[-1].save('${maskPath}')"`);
console.log(`  ✅ birefnet ${((Date.now()-t)/1000).toFixed(1)}s  → fg+mask cached`);

// ============ Handlers ============

async function directHandler(spec) {
  const gen = await fluxPro(spec.prompt_flux);
  const finalPath = path.join(OUT, `img${spec.image_number}_${spec.image_type}_final_${ts}.jpg`);
  await download(gen.data.images[0].url, finalPath);
  return { final_path: finalPath, cost: 0.05, method: "flux_direct" };
}

async function compositeBboxHandler(spec) {
  const sceneGen = await fluxPro(spec.prompt_flux + " , leave empty negative space in the composition for a product to be placed, no backpack visible in the scene");
  const scenePath = path.join(OUT, `img${spec.image_number}_${spec.image_type}_scene_${ts}.jpg`);
  await download(sceneGen.data.images[0].url, scenePath);

  const finalPath = path.join(OUT, `img${spec.image_number}_${spec.image_type}_final_${ts}.jpg`);
  compositeBbox(scenePath, fgPath, maskPath, finalPath, spec.bbox_hint);
  return { final_path: finalPath, cost: 0.05, method: `flux_scene + composite_bbox${spec.bbox_hint ? ' '+JSON.stringify(spec.bbox_hint) : ''}` };
}

async function compositeX4GridHandler(spec) {
  const scenes = [
    "modern office lobby interior with large windows and natural morning light, minimalist pastel decor, clean polished floor, generous empty foreground space for a woman with backpack, editorial photography, 8K, no backpack visible",
    "airport terminal departure area at sunrise with warm light through large windows, a rolling suitcase visible in the mid-ground, empty floor space in foreground, clean modern airport architecture, 8K, no backpack visible",
    "gym entrance interior with yoga mat and clean sneakers on polished floor, bright soft morning light, minimalist wellness aesthetic, empty foreground space, 8K, no backpack visible",
    "hospital nurse locker room with clean metal lockers, stethoscope on a hook, clinical soft natural lighting, empty hook at foreground, 8K, no backpack visible"
  ];
  const bboxes = [
    [350, 300, 650, 900],
    [300, 280, 600, 880],
    [320, 320, 620, 880],
    [350, 260, 650, 860]
  ];

  const panelPaths = [];
  for (let i = 0; i < 4; i++) {
    const sg = await fluxPro(scenes[i]);
    const sPath = path.join(OUT, `img5_panel${i+1}_scene_${ts}.jpg`);
    await download(sg.data.images[0].url, sPath);

    const pPath = path.join(OUT, `img5_panel${i+1}_${ts}.jpg`);
    compositeBbox(sPath, fgPath, maskPath, pPath, bboxes[i]);
    panelPaths.push(pPath);
  }

  const finalPath = path.join(OUT, `img5_scene_multi_use_final_${ts}.jpg`);
  execSync(`python3 ${path.join(__dirname, "grid_compose.py")} ${panelPaths.map(p => `"${p}"`).join(" ")} "${finalPath}"`);
  return { final_path: finalPath, cost: 0.20, method: "composite_x4 + grid (consistent product)" };
}

// ============ Run ============

console.log(`\n🚀 Backpack Full Set — 8 images with bbox fix\n`);
const t0 = Date.now();

for (const spec of plan) {
  const t1 = Date.now();
  console.log(`\n━━━ #${spec.image_number} ${spec.image_type} ━━━`);
  try {
    let result;
    if (spec.tool_chain.includes("pillow_composite_bbox")) {
      result = await compositeBboxHandler(spec);
    } else if (spec.tool_chain.includes("composite_x4_grid")) {
      result = await compositeX4GridHandler(spec);
    } else {
      result = await directHandler(spec);
    }
    const elapsed = ((Date.now() - t1) / 1000).toFixed(1);
    console.log(`  ✅ ${elapsed}s [${result.method}]  → ${path.basename(result.final_path)}`);
    report.images.push({
      image_number: spec.image_number,
      image_type: spec.image_type,
      elapsed_s: parseFloat(elapsed),
      final_path: result.final_path,
      cost_usd: result.cost,
      method: result.method,
      status: "OK"
    });
  } catch (e) {
    console.error(`  ❌ Failed: ${e.message}`);
    report.images.push({ image_number: spec.image_number, status: "FAIL", error: e.message });
  }
}

const totalS = ((Date.now() - t0) / 1000).toFixed(1);
const totalCost = report.images.reduce((s, x) => s + (x.cost_usd || 0), 0).toFixed(3);
report.total_elapsed_s = parseFloat(totalS);
report.total_cost_usd = parseFloat(totalCost);

fs.writeFileSync(path.join(OUT, `report_${ts}.json`), JSON.stringify(report, null, 2));

console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
console.log(`✅ Done`);
console.log(`   Images: ${report.images.filter(i => i.status === "OK").length}/${plan.length}`);
console.log(`   Total: ${totalS}s  /  $${totalCost}`);
console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
