// Step 1: Use Gemini 3.1 Pro to generate a 7-image prompt plan for a Bluetooth Lantern Speaker
// Rebranded as "Excitat" for testing

import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from "fs";

const geminiKey = process.env.GEMINI_KEY;
if (!geminiKey) {
  throw new Error("Missing GEMINI_KEY environment variable.");
}
const genAI = new GoogleGenerativeAI(geminiKey);

const productInfo = {
  brand: "Excitat",
  product_name: "40W Bluetooth Lantern Speaker with RGB Light",
  category: "Portable Bluetooth Speakers",
  key_features: [
    "40W powerful stereo sound with dual drivers",
    "RGB LED lantern light with 8 color modes",
    "IPX5 waterproof rating",
    "Built-in 8000mAh battery, 20+ hours playback",
    "Bluetooth 5.3 with TWS pairing",
    "USB-C charging + solar panel backup",
    "Retractable handle for hanging/carrying",
    "Built-in microphone for hands-free calls"
  ],
  dimensions: "5.5 x 5.5 x 8.2 inches",
  weight: "2.1 lbs",
  target_audience: "Outdoor enthusiasts, campers, party hosts, garden lovers",
  use_cases: ["Camping", "Backyard BBQ", "Pool party", "Beach trip", "Indoor ambient lighting", "Emergency light"],
  price_range: "$35-55",
  competitors: ["JBL Pulse 5", "Bose SoundLink", "Anker Soundcore Glow"],
  unique_selling_points: [
    "Lantern + Speaker 2-in-1 design",
    "Solar charging capability",
    "40W output (louder than most competitors)",
    "8 RGB color modes synced to music"
  ]
};

const systemPrompt = `You are an expert e-commerce visual content strategist specializing in Amazon/Ozon product listing images.

Your task: Given a product's information, create a detailed 7-image prompt plan for AI image generation. Each image serves a specific psychological purpose in the buyer's journey.

STYLE REFERENCE (target quality benchmark):
- Dark/moody backgrounds (night scenes, outdoor twilight, indoor warm lighting)
- Product's RGB LED glow is the hero element — colorful light effects against dark backgrounds
- White bold sans-serif headlines fused with the scene lighting (not "pasted on")
- Each image conveys exactly ONE core selling point
- Natural human scenes (parties, outdoor social, camping)
- Clean linear icons for feature callouts
- High-end, premium feel — NOT cheap infographic style

IMAGE SEQUENCE (progressive hook logic):
1. Hero/Main Image — "What is this? Looks premium" — Clean product shot, dramatic lighting
2. Lifestyle/Scene — "I can see myself using this" — Emotional connection, real usage
3. Core Benefit — "It solves my problem" — Key feature demonstration
4. Detail/Quality — "The build quality is solid" — Materials, craftsmanship close-up
5. Specs/Parameters — "It fits my needs" — Dimensions, technical specs
6. Differentiator — "Better than alternatives" — Unique advantage highlight
7. Trust/Social — "Others love it too" — Reviews, certifications, gift scenario

For each image, provide a DETAILED generation prompt following these dimensions:
- Subject: exact product description and positioning
- Camera/Lens: camera angle, focal length, depth of field
- Lighting: light sources, direction, color temperature, shadows
- Background: environment, setting, mood
- Composition: rule of thirds, leading lines, negative space
- Material/Texture: surface qualities, reflections, transparency
- Color/Mood: color palette, emotional tone, atmosphere
- Text overlay: exact text to render on the image (headline + subtext)
- Technical: resolution, aspect ratio, rendering quality

Output as a JSON array of 7 objects with fields:
- image_number (1-7)
- image_type (hero, lifestyle, benefit, detail, specs, differentiator, trust)
- psychological_hook (the buyer thought this triggers)
- headline_text (main text overlay, 3-6 words, English)
- subtext (secondary text, 8-15 words, English)
- prompt_flux (optimized prompt for Flux 2 Pro — photorealistic, no text rendering)
- prompt_ideogram (optimized prompt for Ideogram V3 — includes text rendering instructions)
- prompt_qwen (optimized prompt for Qwen-Image — may include text)
- negative_prompt (what to avoid)
- style_notes (additional guidance)`;

async function generatePlan() {
  try {
    // Try gemini-2.5-pro first, fall back to other models
    const modelsToTry = ["gemini-2.5-pro-preview-05-06", "gemini-2.0-flash", "gemini-1.5-pro"];

    let result = null;
    for (const modelName of modelsToTry) {
      try {
        console.log(`Trying model: ${modelName}...`);
        const model = genAI.getGenerativeModel({
          model: modelName,
          generationConfig: {
            temperature: 0.8,
            maxOutputTokens: 8192,
          }
        });

        const prompt = `${systemPrompt}

PRODUCT INFORMATION:
${JSON.stringify(productInfo, null, 2)}

Generate the 7-image prompt plan now. Output ONLY valid JSON (no markdown code blocks, no explanation).`;

        result = await model.generateContent(prompt);
        console.log(`Success with model: ${modelName}`);
        break;
      } catch (e) {
        console.log(`Model ${modelName} failed: ${e.message}`);
        continue;
      }
    }

    if (!result) {
      throw new Error("All models failed");
    }

    const text = result.response.text();

    // Extract JSON from response (handle markdown code blocks)
    let jsonStr = text;
    const jsonMatch = text.match(/```(?:json)?\s*([\s\S]*?)```/);
    if (jsonMatch) {
      jsonStr = jsonMatch[1].trim();
    }
    // Also try to find raw JSON array
    if (!jsonStr.startsWith('[')) {
      const arrayMatch = text.match(/\[[\s\S]*\]/);
      if (arrayMatch) jsonStr = arrayMatch[0];
    }

    const plan = JSON.parse(jsonStr);

    // Save the plan
    const outputPath = "/sessions/happy-busy-wright/test_workspace/image_plan.json";
    fs.writeFileSync(outputPath, JSON.stringify(plan, null, 2));
    console.log(`\nSaved ${plan.length}-image plan to ${outputPath}`);

    // Print summary
    plan.forEach(img => {
      console.log(`\nImage ${img.image_number}: [${img.image_type}] "${img.headline_text}"`);
      console.log(`  Hook: ${img.psychological_hook}`);
      console.log(`  Flux prompt (first 100 chars): ${img.prompt_flux?.substring(0, 100)}...`);
    });

    return plan;
  } catch (error) {
    console.error("Error:", error.message);
    if (error.message.includes("API key")) {
      console.error("Check your Gemini API key");
    }
    process.exit(1);
  }
}

generatePlan();
