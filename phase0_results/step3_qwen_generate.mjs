// Step 3: Generate images using Qwen-Image (通义万相) via DashScope API
// Async task submission + polling

import fs from "fs";
import path from "path";
import https from "https";

const API_KEY = "sk-a4924ee576b84496baa1330c8c0414dc";
const BASE_URL = "https://dashscope.aliyuncs.com";
const OUTPUT_DIR = "./output_qwen";

if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

const plan = JSON.parse(fs.readFileSync("./image_plan.json", "utf-8"));

// Helper: make HTTP request
function apiRequest(method, urlPath, body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(urlPath, BASE_URL);
    const options = {
      hostname: url.hostname,
      port: 443,
      path: url.pathname + url.search,
      method,
      headers: {
        "Authorization": `Bearer ${API_KEY}`,
        "Content-Type": "application/json",
        ...(body ? {} : {}),
        "X-DashScope-Async": "enable"
      }
    };

    const req = https.request(options, (res) => {
      let data = "";
      res.on("data", chunk => data += chunk);
      res.on("end", () => {
        try { resolve(JSON.parse(data)); }
        catch { resolve(data); }
      });
    });

    req.on("error", reject);
    req.setTimeout(30000, () => { req.destroy(); reject(new Error("Request timeout")); });
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

// Helper: poll for task completion
async function pollTask(taskId, maxWait = 120000) {
  const startTime = Date.now();
  while (Date.now() - startTime < maxWait) {
    const result = await apiRequest("GET", `/api/v1/tasks/${taskId}`);

    if (result.output?.task_status === "SUCCEEDED") {
      return result;
    } else if (result.output?.task_status === "FAILED") {
      throw new Error(`Task failed: ${JSON.stringify(result.output)}`);
    }

    console.log(`  Polling task ${taskId}: ${result.output?.task_status || "UNKNOWN"}...`);
    await new Promise(r => setTimeout(r, 5000));
  }
  throw new Error("Task polling timeout");
}

// Download image
function downloadImage(url, filepath) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith("https") ? https : require("http");
    protocol.get(url, (response) => {
      if (response.statusCode === 301 || response.statusCode === 302) {
        downloadImage(response.headers.location, filepath).then(resolve).catch(reject);
        return;
      }
      const file = fs.createWriteStream(filepath);
      response.pipe(file);
      file.on("finish", () => { file.close(); resolve(filepath); });
    }).on("error", (err) => { fs.unlink(filepath, () => {}); reject(err); });
  });
}

// Generate with Qwen Image (wanx-v1 / wanx2.1-t2i-turbo)
async function generateQwenImage(imageConfig, index) {
  console.log(`\n[Qwen-Image] Image ${index}: ${imageConfig.image_type} — "${imageConfig.headline_text}"`);

  // Try multiple models
  const models = [
    { name: "wanx2.1-t2i-turbo", model: "wanx2.1-t2i-turbo" },
    { name: "wanx-v1", model: "wanx-v1" }
  ];

  for (const modelInfo of models) {
    try {
      console.log(`  Trying model: ${modelInfo.name}`);

      const body = {
        model: modelInfo.model,
        input: {
          prompt: imageConfig.prompt_qwen
        },
        parameters: {
          size: "1024*1024",
          n: 1,
          seed: Math.floor(Math.random() * 999999)
        }
      };

      // Submit async task
      const submitResult = await apiRequest(
        "POST",
        "/api/v1/services/aigc/text2image/image-synthesis",
        body
      );

      if (submitResult.output?.task_id) {
        console.log(`  Task submitted: ${submitResult.output.task_id}`);

        // Poll for result
        const taskResult = await pollTask(submitResult.output.task_id);

        if (taskResult.output?.results?.[0]?.url) {
          const imgUrl = taskResult.output.results[0].url;
          const filepath = path.join(OUTPUT_DIR, `img${index}_${imageConfig.image_type}_${modelInfo.name}.jpg`);
          await downloadImage(imgUrl, filepath);
          console.log(`  ✓ Saved: ${filepath}`);
          return { model: modelInfo.name, image: index, type: imageConfig.image_type, path: filepath, success: true };
        }
        console.log(`  ✗ No image URL in task result`);
      } else {
        console.log(`  ✗ Submit failed: ${JSON.stringify(submitResult).substring(0, 200)}`);
      }
    } catch (err) {
      console.log(`  ✗ ${modelInfo.name} error: ${err.message}`);
    }
  }

  return { model: "qwen", image: index, success: false, error: "All models failed" };
}

// Main
async function main() {
  console.log("=== Phase 0: Qwen-Image (DashScope) Generation ===");
  console.log(`Processing ${plan.length} images\n`);

  const results = [];

  // Process sequentially to manage async tasks
  for (const img of plan) {
    const result = await generateQwenImage(img, img.image_number);
    results.push(result);
  }

  // Summary
  console.log(`\n${"=".repeat(60)}`);
  console.log("QWEN GENERATION SUMMARY");
  console.log(`${"=".repeat(60)}`);

  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);

  console.log(`Total: ${results.length}`);
  console.log(`Successful: ${successful.length}`);
  console.log(`Failed: ${failed.length}`);

  successful.forEach(s => console.log(`  ✓ ${s.path}`));
  failed.forEach(f => console.log(`  ✗ Image ${f.image}: ${f.error}`));

  fs.writeFileSync(path.join(OUTPUT_DIR, "results.json"), JSON.stringify(results, null, 2));
  console.log(`\nResults saved to ${OUTPUT_DIR}/results.json`);
}

main().catch(err => {
  console.error("Fatal error:", err);
  process.exit(1);
});
