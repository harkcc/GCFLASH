// ST08 Hero 合成全链路测试
// 流程: 生成白底产品图 -> BiRefNet 抠图 -> FLUX 生场景 -> Pillow 合成
// 运行: node test_st08_hero.mjs

import { fal } from "@fal-ai/client";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, "output_st08_test");
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT);

// .env
const env = Object.fromEntries(
  fs.readFileSync(path.join(__dirname, "..", ".env"), "utf-8")
    .split("\n").filter(l => l.includes("=")).map(l => l.split("=").map(s => s.trim()))
);
fal.config({ credentials: env.FAL_KEY });

// 读 plan + config
const plan = JSON.parse(fs.readFileSync(path.join(__dirname, "image_plan_st08.json"), "utf-8"));
const hero = plan.find(p => p.image_type === "hero");
const cfg = JSON.parse(fs.readFileSync(path.join(__dirname, "category_config_auto_accessory.json"), "utf-8"));

const ts = Date.now();
const report = { timestamp: new Date().toISOString(), steps: [] };

async function download(url, outPath) {
  const resp = await fetch(url);
  const buf = Buffer.from(await resp.arrayBuffer());
  fs.writeFileSync(outPath, buf);
  return outPath;
}

function logStep(name, data) {
  report.steps.push({ name, ...data });
  console.log(`\n[${name}] ${JSON.stringify(data, null, 2)}`);
}

// ============ STEP 1: 生成白底产品图（模拟用户上传） ============
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log("STEP 1: 生成白底 ST08 产品图（模拟用户输入）");
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

const productPrompt = "Portable digital tire inflator product photography on pure white seamless background, black body with bright yellow accents, foldable handle on top, digital LED display on front showing '150 PSI' in bright green digits, integrated LED work light on side, multiple chrome nozzle attachments visible, 12V cigarette lighter plug with coiled black cable, front 3/4 angle view, product takes 60% of frame centered, studio lighting with soft shadows beneath, clean commercial catalog style, hyper-realistic material rendering, 8K resolution, no text overlay, no background elements, isolated product shot";

let t = Date.now();
const productGen = await fal.subscribe("fal-ai/flux-pro/v1.1", {
  input: { prompt: productPrompt, image_size: "square_hd", num_images: 1 }
});
const productUrl = productGen.data.images[0].url;
const productPath = path.join(OUT, `hero_00_product_${ts}.jpg`);
await download(productUrl, productPath);
logStep("1_generate_product", { elapsed_s: (Date.now()-t)/1000, url: productUrl, local: productPath, cost: 0.05 });

// ============ STEP 2: BiRefNet 抠图 ============
console.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log("STEP 2: BiRefNet 抠图 -> 前景 + 遮罩");
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

t = Date.now();
const birefnet = await fal.subscribe("fal-ai/birefnet", {
  input: { image_url: productUrl }
});
// birefnet 不同版本字段可能不一样，兼容看一下
const fgUrl = birefnet.data.image?.url || birefnet.data.images?.[0]?.url;
const maskUrl = birefnet.data.mask?.url || birefnet.data.mask_image?.url;

console.log("BiRefNet raw keys:", Object.keys(birefnet.data));
if (!fgUrl) {
  console.error("Could not find foreground URL, raw:", JSON.stringify(birefnet.data, null, 2));
  process.exit(1);
}

const fgPath = path.join(OUT, `hero_01_fg_${ts}.png`);
await download(fgUrl, fgPath);

// 如果没 mask，从 fg 的 alpha 通道提取（稍后 Python 处理）
let maskPath;
if (maskUrl) {
  maskPath = path.join(OUT, `hero_02_mask_${ts}.png`);
  await download(maskUrl, maskPath);
} else {
  console.log("No explicit mask, will extract from fg alpha");
  // 写个小 python 脚本从 alpha 提 mask
  maskPath = path.join(OUT, `hero_02_mask_${ts}.png`);
  execSync(`python3 -c "
from PIL import Image
img = Image.open('${fgPath}').convert('RGBA')
alpha = img.split()[-1]
alpha.save('${maskPath}')
print('mask extracted from alpha:', '${maskPath}')
"`);
}

logStep("2_birefnet", { elapsed_s: (Date.now()-t)/1000, fg: fgPath, mask: maskPath, cost: 0.005 });

// ============ STEP 3: FLUX 生场景底图 ============
console.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log("STEP 3: FLUX 生成 hero 场景底图（带产品位）");
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

// 场景 prompt（从 hero.prompt_flux 衍生，但不包含产品本身的详细描述，只留场景）
const scenePrompt = "Professional studio product photography background, dark charcoal to black gradient surface, dramatic rim lighting from upper-left casting bright highlight band, soft fill light from below, clean empty composition with generous negative space in the center-lower portion for a product to be placed, industrial catalog photography style, subtle subtle subtle reflection surface, 8K resolution, commercial quality, no product in frame, pure empty scene";

t = Date.now();
const scene = await fal.subscribe("fal-ai/flux-pro/v1.1", {
  input: { prompt: scenePrompt, image_size: "square_hd", num_images: 1 }
});
const sceneUrl = scene.data.images[0].url;
const scenePath = path.join(OUT, `hero_03_scene_${ts}.jpg`);
await download(sceneUrl, scenePath);
logStep("3_scene", { elapsed_s: (Date.now()-t)/1000, url: sceneUrl, local: scenePath, cost: 0.05 });

// ============ STEP 4: Pillow 合成 ============
console.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log("STEP 4: Pillow 合成（产品+场景+mask 羽化）");
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

const finalPath = path.join(OUT, `hero_04_final_${ts}.jpg`);
const feather = cfg.mask_params.feather_radius_px || 4;

t = Date.now();
execSync(`python3 ${path.join(__dirname, "composite.py")} "${scenePath}" "${fgPath}" "${maskPath}" "${finalPath}" ${feather}`,
  { stdio: "inherit" });
logStep("4_composite", { elapsed_s: (Date.now()-t)/1000, final: finalPath, feather_px: feather, cost: 0.0 });

// ============ 报告 ============
const totalCost = report.steps.reduce((s, x) => s + (x.cost || 0), 0);
const totalTime = report.steps.reduce((s, x) => s + (x.elapsed_s || 0), 0);
report.total_cost_usd = totalCost;
report.total_elapsed_s = totalTime;
report.final_output = finalPath;

fs.writeFileSync(path.join(OUT, `hero_report_${ts}.json`), JSON.stringify(report, null, 2));

console.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log(`✅ Hero 合成完成`);
console.log(`   总耗时: ${totalTime.toFixed(1)}s`);
console.log(`   总成本: $${totalCost.toFixed(3)}`);
console.log(`   最终图: ${finalPath}`);
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
