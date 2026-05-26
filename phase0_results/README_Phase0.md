# Phase 0 测试套件 — Excitat 蓝牙灯笼音箱

**日期：2026-04-11**
**状态：脚本就绪，需在本地运行**

---

## 为什么没有直接生成图片？

Cowork 沙盒环境的代理限制了对外部 API 的访问（fal.ai、DashScope、Gemini 均被 blocked-by-allowlist）。所有脚本已写好并测试过逻辑，你只需在本地终端运行即可。

---

## 快速开始

```bash
# 1. 进入项目目录
cd phase0_results

# 2. 安装依赖
npm install

# 3. 一键运行全部测试
bash run_all.sh

# 或者分步运行：
node step1_gemini_plan.mjs    # (可选) 用 Gemini 重新生成 prompt plan
node step2_fal_generate.mjs    # fal.ai 4个模型横评
node step3_qwen_generate.mjs   # 通义万相 生图
node step4_gemini_review.mjs   # Gemini 视觉质检打分
```

---

## 文件清单

| 文件 | 用途 |
|------|------|
| `image_plan.json` | 7张图的详细 prompt 方案（含 Flux/Ideogram/Qwen 三版 prompt） |
| `step1_gemini_plan.mjs` | (可选) 用 Gemini API 重新生成 prompt plan |
| `step2_fal_generate.mjs` | fal.ai 生图：Flux 2 Pro + Flux Ultra + Ideogram V3 + Flux Schnell |
| `step3_qwen_generate.mjs` | 通义万相 DashScope 生图 |
| `step4_gemini_review.mjs` | Gemini 视觉质检 — 对每张图打分（7个维度 + 总分） |
| `step5_brand_template.html` | Excitat 品牌边框 HTML 模板（3种变体） |
| `run_all.sh` | 一键运行全部步骤 |
| `package.json` | npm 依赖配置 |

---

## image_plan.json 结构

每张图包含：

- **image_number**: 1-7（递进序号）
- **image_type**: hero / lifestyle / benefit / detail / specs / differentiator / trust
- **psychological_hook**: 触发买家的心理钩子
- **headline_text**: 主标题文字
- **subtext**: 副标题文字
- **prompt_flux**: Flux 2 Pro 用的 prompt（写实，无文字）
- **prompt_ideogram**: Ideogram V3 用的 prompt（含文字渲染指令）
- **prompt_qwen**: Qwen-Image 用的 prompt
- **negative_prompt**: 排除项
- **style_notes**: 风格备注

---

## 模型横评矩阵

| 图片 | Flux 2 Pro | Flux Ultra | Ideogram V3 | Flux Schnell | Qwen |
|------|------------|------------|-------------|--------------|------|
| 1. Hero | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2. Lifestyle | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3. Benefit | ✓ | — | ✓ | ✓ | ✓ |
| 4. Detail | ✓ | — | ✓ | ✓ | ✓ |
| 5. Specs | ✓ | — | ✓ | ✓ | ✓ |
| 6. Differentiator | ✓ | — | ✓ | ✓ | ✓ |
| 7. Trust | ✓ | — | ✓ | ✓ | ✓ |

Flux Ultra 只跑前2张（最贵，先验证效果）。

---

## 预估费用

| 模型 | 单价 | 数量 | 小计 |
|------|------|------|------|
| Flux 2 Pro | ~$0.05/张 | 7 | ~$0.35 |
| Flux Ultra | ~$0.08/张 | 2 | ~$0.16 |
| Ideogram V3 | ~$0.08/张 | 7 | ~$0.56 |
| Flux Schnell | ~$0.003/张 | 7 | ~$0.02 |
| Qwen wanx2.1 | ~¥0.14/张 | 7 | ~¥1.0 |
| Gemini 质检 | ~$0.001/次 | ~30 | ~$0.03 |
| **总计** | | | **~$1.3 + ¥1.0** |

---

## 品牌模板说明

`step5_brand_template.html` 提供3种模板变体：

1. **Standard** — 标准款：顶部渐变遮罩 + 标题文字 + 底部品牌栏
2. **Specs** — 参数款：增加底部特性图标条
3. **Clean** — 极简款：只有品牌角标和底部品牌栏

模板特征（匹配 emag Excitat 店铺风格）：
- EXCITAT 红色金属渐变 Logo
- 深蓝/紫色渐变底栏
- eMAG genius 绿色标签
- 暗色调整体配色

用浏览器打开即可预览，替换 `<img>` 的 src 为生成的图片路径即可。

---

## 质检评分维度

Gemini 会对每张图打7个维度的分（1-10）：

1. Visual Quality（视觉质量）
2. Product Representation（产品还原度）
3. Mood/Atmosphere（氛围感）
4. Text Rendering（文字渲染质量）
5. Composition（构图）
6. Commercial Viability（商业可用性）
7. Benchmark Proximity（与标杆的接近度）

Phase 0 目标：单张图 Overall Score ≥ 7/10 即算通过。
