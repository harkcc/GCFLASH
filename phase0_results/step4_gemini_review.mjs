// Step 4: Use Gemini to visually review generated images and score them
// Reads images from output directories and sends to Gemini for quality assessment

import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from "fs";
import path from "path";

const genAI = new GoogleGenerativeAI("AIzaSyBNAAGlS6etxXgcijR-aTzbOU56QaCPZLI");

const plan = JSON.parse(fs.readFileSync("./image_plan.json", "utf-8"));

const reviewPrompt = `You are an expert e-commerce visual content reviewer for Amazon/Ozon product listings.

CONTEXT: This is an AI-generated product image for a Bluetooth Lantern Speaker (brand: Excitat).

TARGET BENCHMARK: High-end Amazon A+ listing images with these characteristics:
- Dark/moody backgrounds with RGB light effects as hero element
- White bold text naturally fused with scene lighting
- Each image delivers exactly ONE clear selling point
- Natural, aspirational lifestyle scenes
- Premium, professional quality

EVALUATE THIS IMAGE on the following criteria (1-10 each):

1. **Visual Quality** (sharpness, resolution feel, artifacts, overall polish)
2. **Product Representation** (does it look like a real bluetooth lantern speaker?)
3. **Mood/Atmosphere** (dark moody vibe, premium feel, RGB glow as hero)
4. **Text Rendering** (if text present: readability, integration, font quality. If no text: N/A)
5. **Composition** (balance, rule of thirds, negative space for text overlay)
6. **Commercial Viability** (would this work as an actual product listing image?)
7. **Benchmark Proximity** (how close is this to high-end Amazon A+ quality?)

Also provide:
- **Overall Score** (1-10, weighted average)
- **Strengths** (2-3 bullet points)
- **Weaknesses** (2-3 bullet points)
- **Improvement Suggestions** (2-3 specific, actionable items)

Output as JSON:
{
  "visual_quality": 7,
  "product_representation": 6,
  "mood_atmosphere": 8,
  "text_rendering": 5,
  "composition": 7,
  "commercial_viability": 6,
  "benchmark_proximity": 5,
  "overall_score": 6.3,
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "suggestions": ["...", "..."]
}`;

async function reviewImage(imagePath, imageConfig) {
  const modelsToTry = ["gemini-2.5-pro-preview-05-06", "gemini-2.0-flash", "gemini-1.5-pro"];

  for (const modelName of modelsToTry) {
    try {
      const model = genAI.getGenerativeModel({ model: modelName });

      // Read image as base64
      const imageData = fs.readFileSync(imagePath);
      const base64Image = imageData.toString("base64");
      const mimeType = imagePath.endsWith(".png") ? "image/png" : "image/jpeg";

      const result = await model.generateContent([
        {
          inlineData: {
            data: base64Image,
            mimeType
          }
        },
        `${reviewPrompt}\n\nIMAGE CONTEXT:\n- Image #${imageConfig.image_number}: ${imageConfig.image_type}\n- Intended headline: "${imageConfig.headline_text}"\n- Intended subtext: "${imageConfig.subtext}"\n- Model used: ${path.basename(imagePath).split("_").pop().replace(".jpg", "")}\n\nReview this image now. Output ONLY valid JSON.`
      ]);

      const text = result.response.text();
      let jsonStr = text;
      const jsonMatch = text.match(/```(?:json)?\s*([\s\S]*?)```/);
      if (jsonMatch) jsonStr = jsonMatch[1].trim();
      if (!jsonStr.startsWith("{")) {
        const objMatch = text.match(/\{[\s\S]*\}/);
        if (objMatch) jsonStr = objMatch[0];
      }

      return { ...JSON.parse(jsonStr), model_used: modelName };
    } catch (err) {
      console.log(`  ${modelName} failed: ${err.message}`);
    }
  }
  return { overall_score: -1, error: "All models failed" };
}

async function main() {
  console.log("=== Phase 0: Gemini Visual Quality Review ===\n");

  const outputDirs = ["./output_fal", "./output_qwen"];
  const allReviews = [];

  for (const dir of outputDirs) {
    if (!fs.existsSync(dir)) {
      console.log(`Directory ${dir} not found, skipping`);
      continue;
    }

    const files = fs.readdirSync(dir).filter(f => f.endsWith(".jpg") || f.endsWith(".png"));
    console.log(`Found ${files.length} images in ${dir}`);

    for (const file of files) {
      const filepath = path.join(dir, file);

      // Extract image number from filename (e.g., img1_hero_flux_pro.jpg)
      const match = file.match(/img(\d+)_(\w+)/);
      if (!match) continue;

      const imgNum = parseInt(match[1]);
      const imageConfig = plan.find(p => p.image_number === imgNum) || plan[0];

      console.log(`\nReviewing: ${file}`);
      const review = await reviewImage(filepath, imageConfig);

      allReviews.push({
        file,
        directory: dir,
        image_number: imgNum,
        image_type: imageConfig.image_type,
        ...review
      });

      if (review.overall_score >= 0) {
        console.log(`  Score: ${review.overall_score}/10`);
        console.log(`  Strengths: ${review.strengths?.join("; ")}`);
        console.log(`  Weaknesses: ${review.weaknesses?.join("; ")}`);
      } else {
        console.log(`  Review failed: ${review.error}`);
      }

      // Small delay between API calls
      await new Promise(r => setTimeout(r, 2000));
    }
  }

  // Generate summary report
  console.log(`\n\n${"=".repeat(60)}`);
  console.log("REVIEW SUMMARY");
  console.log(`${"=".repeat(60)}`);

  // Group by model
  const byModel = {};
  allReviews.filter(r => r.overall_score >= 0).forEach(r => {
    const model = r.file.split("_").slice(-1)[0].replace(".jpg", "").replace(".png", "");
    if (!byModel[model]) byModel[model] = [];
    byModel[model].push(r.overall_score);
  });

  console.log("\nAverage scores by model:");
  Object.entries(byModel).forEach(([model, scores]) => {
    const avg = (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1);
    console.log(`  ${model}: ${avg}/10 (${scores.length} images)`);
  });

  // Group by image type
  const byType = {};
  allReviews.filter(r => r.overall_score >= 0).forEach(r => {
    if (!byType[r.image_type]) byType[r.image_type] = [];
    byType[r.image_type].push({ model: r.file, score: r.overall_score });
  });

  console.log("\nBest model per image type:");
  Object.entries(byType).forEach(([type, entries]) => {
    entries.sort((a, b) => b.score - a.score);
    console.log(`  ${type}: ${entries[0].model} (${entries[0].score}/10)`);
  });

  // Save full report
  fs.writeFileSync("./review_report.json", JSON.stringify(allReviews, null, 2));
  console.log(`\nFull report saved to ./review_report.json`);

  // Find best image per position
  console.log("\nRecommended best image per position:");
  for (let i = 1; i <= 7; i++) {
    const candidates = allReviews.filter(r => r.image_number === i && r.overall_score >= 0);
    if (candidates.length > 0) {
      candidates.sort((a, b) => b.overall_score - a.overall_score);
      const best = candidates[0];
      console.log(`  Image ${i} (${best.image_type}): ${best.file} — ${best.overall_score}/10`);
    }
  }
}

main().catch(err => {
  console.error("Fatal error:", err);
  process.exit(1);
});
