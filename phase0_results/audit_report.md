# Excitat 电商套图 AI 生成系统 — 技术审核报告

**审核日期：2026-04-12**
**审核范围：Phase 0 全部架构文档 + 6 个执行脚本 + 图片规划数据**

---

## 综合评估总表

| 维度 | 评分 | 最高优先级问题 | 核心风险 |
|------|------|--------------|---------|
| A. 架构完整性 | 6/10 | P0: 素材评估层缺失，合成层缺失 | 流程断链，无法端到端运行 |
| B. 提示词质量 | 5/10 | P0: negative_prompt 未使用 | 生成质量达不到预期 |
| C. 一致性机制 | 3/10 | P0: 产品外形一致性为零 | 7张图的产品长得不一样 — 商业不可用 |
| D. 评审闭环 | 6/10 | P1: 无自动迭代反馈回路 | 评审只能看不能改 |
| E. 模型路由 | 7/10 | P1: 代码中无智能路由 | 全量轰炸浪费成本 |
| F. 成本控制 | 4/10 | P1: 无分级生成策略 | 调试阶段成本失控 |
| G. 竞品学习 | 2/10 | P0: 竞品分析未结构化注入 | 生成的图缺乏市场竞争力 |
| H. 代码 Bug | 4/10 | P0: API Key硬编码、路径不一致 | 安全风险 + 无法运行 |

**综合评分: 4.6/10**

---

## A. 架构完整性 — 评分: 6/10

### A1. 素材评估层 (Step 1) 在代码中完全缺失 [P0]

`workflow_architecture.md` 描述了一个三档分级 (A/B/C) 的素材评估流程，但实际的 `step1_gemini_plan.mjs` 完全跳过了这一步 — 它直接硬编码了 `productInfo` 对象，没有任何"素材完备度检查"的代码。

### A2. 合成层 (Playwright/Canvas) 没有可执行代码 [P0]

架构图明确标注了"合成层"，但整个项目里没有任何 Playwright 截图/渲染的代码。`step5_brand_frame_gen.mjs` 只生成 HTML 字符串，不做渲染。

### A3. 端到端串联缺失 [P1]

Step 1-5 是独立脚本，step1 的输出路径写的是 `/sessions/happy-busy-wright/test_workspace/image_plan.json`，而 step2 读的是 `./image_plan.json` — 路径不一致，无法直接串联。

### A4. 输出尺寸不一致 [P2]

架构说最终输出 1200x1200，但所有脚本用 1024x1024，没有放大步骤。

---

## B. 提示词质量 — 评分: 5/10

### B1. 无意义的相机参数占大量篇幅 [P1]

`"shot with Sony A7R IV, 85mm f/1.4 lens"` — Flux/Ideogram 不理解相机型号，浪费 token 空间。

### B2. negative_prompt 完全未使用 [P0] ⚠️ 严重 Bug

image_plan.json 精心编写了 negative_prompt，但 step2 的所有模型调用都没有传入此字段。

### B3. style_notes 完全未使用 [P1]

重要的创作指导（如"This is the hero shot. Maximum visual impact."）从未被读取。

### B4. prompt 结构未按模型特性优化 [P2]

prompt_flux/prompt_ideogram/prompt_qwen 三者内容大量重复，没有发挥各模型差异化优势。

---

## C. 一致性机制 — 评分: 3/10

### C1. 产品外形一致性完全没有保障 [P0] ⚠️ 最严重缺陷

7张图全部是 text-to-image，没有任何参考图输入。"cylindrical bluetooth lantern speaker" 在每次生成中被理解成完全不同的产品。

### C2. 风格一致性锚点未被使用 [P1]

没有共享的风格前缀或 style_consistency_anchors 注入机制。

### C3. seed 未记录 [P1]

无法复现和微调生成结果。

---

## D. 评审闭环 — 评分: 6/10

### D1. step4_gemini_review.mjs 代码完整 [正面]

7维度评分体系与架构文档一致，是做得最好的部分。

### D2. 评审结果没有反馈回路代码 [P1]

overall_score < 7 时只打印分数，不触发重新生成。

### D3. 评审不读取 style_notes 和 negative_prompt [P2]

评审无法判断"是否符合设计意图"。

---

## E. 模型路由 — 评分: 7/10

### E1. 代码中没有智能路由 [P1]

step2 对所有 7 张图无差别跑 5 个模型，不根据 image_type 选择。Image 5 (specs) 应该主要用 Ideogram + HTML 模板，但也跑了 Flux 2 Pro 等，浪费费用。

---

## F. 成本控制 — 评分: 4/10

### F1. 没有分级生成策略 [P1]

当前单次套图 ~$1.28（5模型 x 7图）。合理做法：先 Schnell 验证方向 → 再用 1-2 个贵模型。

### F2. 迭代成本爆炸 [P1]

每轮迭代 $1.28，30 个 SKU x 3 轮 = ~$115/月。

---

## G. 竞品学习 — 评分: 2/10

### G1. 竞品分析只存在于人脑中 [P0]

标杆图的分析结论没有以结构化数据注入 Gemini 的 system prompt。

### G2. Gemini 没有"看过"竞品图 [P1]

没有 Gemini Vision 自动分析竞品构图的步骤。

---

## H. 代码 Bug — 评分: 4/10

### H1. API Key 硬编码 [P0 安全]

所有脚本明文写入 API Key（Gemini、fal.ai、Qwen），应改用环境变量。

### H2. step1 输出路径错误 [P0]

输出到 `/sessions/happy-busy-wright/...`，与 step2 的 `./image_plan.json` 不一致。

### H3. step5a 引用不存在的路径 [P1]

`"../mnt/photo_show/photo"` 是 Docker 路径，本地运行会崩溃。

### H4. step2 同时跑新旧 Flux Pro [P1]

`fal-ai/flux-pro/v1.1`（旧）和 `fal-ai/flux-2-pro`（新）同时跑，旧版应去掉。

---

## P0 紧急修复清单

1. **API Key 外部化** — 改用 process.env
2. **negative_prompt 传入修复** — step2/step3 所有生成函数加入 negative_prompt
3. **产品一致性机制** — 实现 Flux Redux 参考图注入
4. **step1 输出路径修复** — 改为 `./image_plan.json`
5. **合成层实现** — Playwright 截图脚本
6. **竞品分析结构化** — 标杆图分析注入 system prompt

---

## 总评

架构设计文档质量很高，但**代码实现严重落后于文档设计**，大约只实现了 30-40%。最关键的三个缺陷：
1. 产品外形一致性机制为零
2. negative_prompt 等精心设计的字段未被使用
3. 合成层和素材评估层只有文档没有代码

建议优先补齐 P0 项，特别是产品一致性机制 — 这是从"技术 demo"到"商业可用"的分水岭。
