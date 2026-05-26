#!/bin/bash
# Phase 0 Master Runner — Excitat Bluetooth Lantern Speaker
# Run all steps sequentially
# 使用方式：在 phase0_results 目录下运行 bash run_all.sh

set -e
echo "================================================"
echo "  Phase 0: AI E-Commerce Image Generation Test"
echo "  Brand: Excitat | Product: BT Lantern Speaker"
echo "================================================"
echo ""

# Check dependencies
echo "[Pre-check] Verifying Node.js..."
node --version || { echo "Node.js not found! Install from https://nodejs.org"; exit 1; }

# Install deps if needed
if [ ! -d "node_modules" ]; then
  echo "[Pre-check] Installing npm dependencies..."
  npm install
fi

# Create output directories
mkdir -p output_fal output_qwen output_brand_frames

# Step 1: Generate prompt plan (already done, but can regenerate via Gemini)
echo ""
echo "================================================"
echo "  Step 1: Checking image plan..."
echo "================================================"
if [ -f "image_plan.json" ]; then
  echo "✓ image_plan.json exists ($(cat image_plan.json | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))' 2>/dev/null || echo '?') images)"
  echo "  To regenerate via Gemini: node step1_gemini_plan.mjs"
else
  echo "Generating plan via Gemini..."
  node step1_gemini_plan.mjs
fi

# Step 2: fal.ai generation (产品场景图)
echo ""
echo "================================================"
echo "  Step 2: Generating product images via fal.ai"
echo "  Models: Flux 2 Pro, Flux Ultra, Ideogram V3, Flux Schnell"
echo "  Expected: ~28 images (7 images × 4 models)"
echo "  Estimated time: 5-10 minutes"
echo "  Estimated cost: ~$2-4"
echo "================================================"
echo ""
node step2_fal_generate.mjs

# Step 3: Qwen-Image generation
echo ""
echo "================================================"
echo "  Step 3: Generating images via Qwen-Image (DashScope)"
echo "  注意：需要能直连阿里云的网络（非代理）"
echo "  Expected: 7 images"
echo "  Estimated time: 3-7 minutes"
echo "================================================"
echo ""
node step3_qwen_generate.mjs || echo "⚠ Qwen generation had errors (may be network issue, continuing...)"

# Step 4: Brand frame generation
echo ""
echo "================================================"
echo "  Step 4: Generating brand frames via AI"
echo "  4 variants of the Excitat decorative frame"
echo "  Estimated time: 2-3 minutes"
echo "================================================"
echo ""
node step5_brand_frame_gen.mjs || echo "⚠ Brand frame generation had errors, continuing..."

# Step 5: Gemini visual review
echo ""
echo "================================================"
echo "  Step 5: AI Quality Review via Gemini"
echo "  Reviews all generated images and scores them"
echo "  Estimated time: 5-10 minutes"
echo "================================================"
echo ""
node step4_gemini_review.mjs || echo "⚠ Review had errors, continuing..."

# Summary
echo ""
echo "================================================"
echo "  DONE!"
echo "================================================"
echo ""
echo "Generated files:"
echo ""
echo "📁 output_fal/          — fal.ai 模型生成的产品图"
ls output_fal/*.jpg 2>/dev/null | wc -l | xargs -I{} echo "   {} images"
echo ""
echo "📁 output_qwen/         — 通义万相生成的产品图"
ls output_qwen/*.jpg 2>/dev/null | wc -l | xargs -I{} echo "   {} images"
echo ""
echo "📁 output_brand_frames/ — AI 生成的品牌边框"
ls output_brand_frames/*.png 2>/dev/null | wc -l | xargs -I{} echo "   {} frames"
echo ""

if [ -f "review_report.json" ]; then
  echo "📄 review_report.json   — Gemini 质检评分报告"
fi

echo ""
echo "Next steps:"
echo "  1. 查看 output_fal/ 和 output_qwen/ 中的生成图片"
echo "  2. 查看 output_brand_frames/ 中的品牌框"
echo "  3. 查看 review_report.json 的 AI 质检打分"
echo "  4. 选出每个位置最佳的图 + 最佳品牌框"
echo "  5. 下一步：用 Playwright 合成（品牌框 + 产品图 + 文字）"
