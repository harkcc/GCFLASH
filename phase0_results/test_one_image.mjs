// 快速测试脚本 — 只生成1张图，验证 API 连通性和效果
// 用 Image #1 (Hero) 测试 3 个模型

import { fal } from "@fal-ai/client";
import fs from "fs";
import https from "https";

fal.config({
  credentials: "b66420fa-3d16-47f9-8f60-c4369eebcc7a:cf11ed54977c84f01dc2364eeba10806"
});

const OUTPUT_DIR = "./output_test";
if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

function downloadImage(url, filepath) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(filepath);
    https.get(url, (res) => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        downloadImage(res.headers.location, filepath).then(resolve).catch(reject);
        return;
      }
      res.pipe(file);
      file.on("finish", () => { file.close(); resolve(filepath); });
    }).on("error", reject);
  });
}

// Hero image prompt — 蓝牙灯笼音箱主图
const heroPrompt = `Professional product photography of a cylindrical portable bluetooth lantern speaker, matte black body with brushed metal accents, glowing with vibrant rainbow RGB LED light emanating from the top diffuser, placed on a dark slate surface, dramatic low-key lighting from the side, the RGB glow illuminates surrounding mist creating colorful light rays, shot with 85mm f/1.4 lens, shallow depth of field, dark moody background fading to black, hyper-realistic material rendering, cinematic color grading, 8K resolution, commercial product photography`;

async function testModel(modelId, modelName, extraInput = {}) {
  console.log(`\n[${modelName}] Generating hero image...`);
  const start = Date.now();

  try {
    const result = await fal.subscribe(modelId, {
      input: {
        prompt: heroPrompt,
        image_size: { width: 1024, height: 1024 },
        num_images: 1,
        ...extraInput
      },
      logs: false
    });

    const elapsed = ((Date.now() - start) / 1000).toFixed(1);

    if (result.data?.images?.[0]?.url) {
      const filepath = `${OUTPUT_DIR}/hero_${modelName.replace(/\s+/g, '_').toLowerCase()}.jpg`;
      await downloadImage(result.data.images[0].url, filepath);
      console.log(`  ✓ 成功! 耗时 ${elapsed}s → ${filepath}`);
      return { model: modelName, success: true, time: elapsed, path: filepath };
    }
    console.log(`  ✗ 无图片URL (${elapsed}s)`);
    return { model: modelName, success: false, time: elapsed };
  } catch (err) {
    const elapsed = ((Date.now() - start) / 1000).toFixed(1);
    console.log(`  ✗ 错误 (${elapsed}s): ${err.message}`);
    return { model: modelName, success: false, error: err.message };
  }
}

async function main() {
  console.log("=== 快速测试: 1张Hero图 × 3个模型 ===\n");

  const results = await Promise.allSettled([
    testModel("fal-ai/flux-pro/v1.1", "Flux_1.1_Pro", { safety_tolerance: "5", output_format: "jpeg" }),
    testModel("fal-ai/flux-2-pro", "Flux_2_Pro", { safety_tolerance: "5", output_format: "jpeg" }),
    testModel("fal-ai/ideogram/v3", "Ideogram_V3", { style: "REALISTIC", rendering_speed: "QUALITY" }),
  ]);

  console.log(`\n${"=".repeat(50)}`);
  console.log("测试结果:");
  console.log(`${"=".repeat(50)}`);

  results.forEach(r => {
    if (r.status === "fulfilled" && r.value.success) {
      console.log(`  ✓ ${r.value.model} — ${r.value.time}s → ${r.value.path}`);
    } else if (r.status === "fulfilled") {
      console.log(`  ✗ ${r.value.model} — ${r.value.error || "failed"}`);
    } else {
      console.log(`  ✗ ${r.reason}`);
    }
  });

  console.log(`\n生成的图片在 ${OUTPUT_DIR}/ 目录下，请查看效果。`);
  console.log(`如果测试通过，运行完整生成: node step2_fal_generate.mjs`);
}

main();
