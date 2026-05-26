// ST08 冒烟测试 — 调一次 fal flux-pro 验证管道通不通
// 用 image_plan_st08.json 里 image #2 (pain_point) 的 prompt，因为它不需要产品图输入
// 运行: node test_st08_smoke.mjs

import { fal } from "@fal-ai/client";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// 从 .env 读取 FAL_KEY（父目录）
const envPath = path.join(__dirname, "..", ".env");
const env = Object.fromEntries(
  fs.readFileSync(envPath, "utf-8")
    .split("\n")
    .filter(l => l.includes("="))
    .map(l => l.split("=").map(s => s.trim()))
);

fal.config({ credentials: env.FAL_KEY });

// 读 image_plan_st08.json
const plan = JSON.parse(fs.readFileSync(path.join(__dirname, "image_plan_st08.json"), "utf-8"));
const painPoint = plan.find(p => p.image_type === "pain_point");

console.log("📦 Testing fal.ai with ST08 pain_point image");
console.log("   Prompt:", painPoint.prompt_flux.slice(0, 120) + "...");
console.log("");

const t0 = Date.now();

try {
  const result = await fal.subscribe("fal-ai/flux-pro/v1.1", {
    input: {
      prompt: painPoint.prompt_flux,
      image_size: "square_hd",
      num_images: 1,
      enable_safety_checker: true
    },
    logs: true,
    onQueueUpdate: (update) => {
      if (update.status === "IN_PROGRESS") {
        console.log(`   [${Date.now() - t0}ms] still generating...`);
      }
    }
  });

  const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
  console.log(`\n✅ Generated in ${elapsed}s`);
  console.log("   Image URL:", result.data.images[0].url);
  console.log("   Seed:", result.data.seed);

  // 下载到本地
  const outputDir = path.join(__dirname, "output_st08_test");
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir);
  const outputPath = path.join(outputDir, `st08_pain_point_${Date.now()}.jpg`);

  const resp = await fetch(result.data.images[0].url);
  const buf = Buffer.from(await resp.arrayBuffer());
  fs.writeFileSync(outputPath, buf);
  console.log("   Saved to:", outputPath);
  console.log("   File size:", (buf.length / 1024).toFixed(1), "KB");

  // 写测试结果
  const reportPath = path.join(outputDir, "smoke_test_report.json");
  fs.writeFileSync(reportPath, JSON.stringify({
    timestamp: new Date().toISOString(),
    image_tested: "pain_point",
    model: "fal-ai/flux-pro/v1.1",
    elapsed_seconds: parseFloat(elapsed),
    image_url: result.data.images[0].url,
    local_path: outputPath,
    seed: result.data.seed,
    cost_usd_est: 0.05,
    status: "SUCCESS"
  }, null, 2));

  console.log("\n🎯 Smoke test PASSED. Pipeline is wired up.");
  console.log("   Next: add product composite for hero/detail/solution images.");

} catch (err) {
  console.error("\n❌ Smoke test FAILED");
  console.error("   Error:", err.message);
  if (err.body) console.error("   Body:", JSON.stringify(err.body, null, 2));
  process.exit(1);
}
