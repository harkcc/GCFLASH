# Excitat AI 电商套图系统 — 项目背景与关键决策

> 本文档汇总 Session 2 所有讨论成果，供后续 Session 作为上下文参考。
> 生成时间：2026-04-15

---

## 一、项目定义

### 1.1 目标
构建一个 AI 驱动的电商产品 Listing 套图自动生成系统。输入产品信息和白底图，输出一套 7-8 张完整的亚马逊 Listing 图片。

### 1.2 当前产品
Excitat 蓝牙灯音箱（Bluetooth Lantern Speaker），户外露营类目。

### 1.3 核心理念
> **痛点是画图的灵魂。** 不是先想怎么画，而是先想画什么、为什么画。
> **AI 是组合者，不是创造者。** 给它预制的专业知识让它"选"，而不是让它从零生成。
> **模仿人的设计流程，** 把人脑中的"经验"和"直觉"变成结构化约束。

---

## 二、系统架构（修正后）

### 2.1 完整流程

```
产品信息 + 白底图输入
│
├── Step 0: 卖点分析（Gemini）
│   ├── 产品核心卖点
│   ├── 竞品分析（平台搜索 + 网络搜索）
│   ├── 目标人群画像
│   ├── 痛点拆解
│   └── 输出：product_analysis.json
│
├── Step 1: 视觉策略（Gemini）
│   ├── 8图序列分配（每张图的"销售任务"）
│   ├── 色彩方案选择（从类目预设中选）
│   ├── 生成每张图的 Prompt（含约束）
│   └── 输出：image_prompts.json
│
├── Step 2: 产品预处理
│   └── 去背景（BiRefNet）→ 产品遮罩
│
├── Step 3: 图片生成
│   ├── 产品为主的图 → 先生场景 → Kontext Multi 融合产品
│   └── 场景为主的图 → 整体生成
│
├── Step 4: 质量验证（Gemini 打分）
│   ├── 及格 → 进入下一步
│   └── 不及格 → 调整 Prompt 重试（最多 3 次）
│
├── Step 5: 色调统一
│   └── Hero 图色调提取 → 后续图做 histogram matching
│
└── Step 6: 图文合成
    └── 加文字/参数表/对比图（Playwright 或 Canvas）
```

### 2.2 关键架构决策

| 决策 | 结论 | 原因 |
|------|------|------|
| Agent vs Workflow | **Workflow** | 步骤已知且固定，不需要 AI 自主探索 |
| 实现语言 | **Python 为主** | dynamicprompts, OpenCV, PyIQA 等生态都是 Python |
| 知识库方案 | **轻量预设 + Prompt 约束** | 不建重型知识库，用 JSON 预设 + prompt 里写约束 |
| 产品一致性 | **Kontext Multi（首选）→ ControlNet+IP-Adapter（精确）→ LoRA（终极）** | 渐进式方案 |
| 模板素材存储 | **MongoDB**（图片用 GridFS 或存地址引用） | 图片+提示词+标签存一起 |
| 色彩方案 | **类目预设表（JSON）+ prompt 约束** | 不蒸馏 28.6 万字色彩理论 |

### 2.3 Workflow 不需要 Agent 框架的原因

- 流程每一步该做什么都是已知的
- AI 只在每步内部做决策（选色彩方案、选模板），不需要自主决定下一步
- Workflow 更容易调试、可复现
- 简单的 Python 脚本按顺序调 API 即可

---

## 三、8 图序列公式

### 3.1 用户定义的 8 图公式

| 序号 | 任务 | 核心逻辑 | 举例 |
|------|------|----------|------|
| 1 | **抓眼球** | 你是谁 + 核心卖点 | "零下20度不冷，显瘦不臃肿" |
| 2 | **戳痛点** | 触动烦恼，产生共鸣 | "拖地水印、弯腰累、毛发扫不净" |
| 3 | **给方案** | 产品怎么解决痛点 | before/after 对比 |
| 4 | **秀细节** | 面料/材质/做工/芯片/爆炸图 | 科技感细节展示 |
| 5 | **看场景** | 降低想象成本 | "买回家你真的用得上" |
| 6 | **建信任** | 好评返图/虚拟买家秀/资质 | 虚拟买家秀场景 |
| 7 | **选规格** | 规格参数对比表 | 尺寸/容量/颜色对比图 |
| 8 | **促下单** | 优惠/限时/组合装 | 行动号召 |

### 3.2 Amazon 7-Slot 标准策略（行业对照）

- Slot 1: 纯白底主图（必须 RGB 255,255,255，产品占 85%+，无文字）
- Slot 2-4: **权重最高**（桌面只显示前 4-5 张缩略图，其余折叠）
- 有 7+ 张图的 Listing 转化率是单图的 2.4 倍
- 信息图可提升 30% 互动率

### 3.3 主图设计规则（用户定义）

- 产品清晰干净，有卖点，有明显对比优势
- 产品居中，占满画面约 70%
- 光线要亮，颜色要真实
- 文字不超过三行，加粗，颜色对比强
- 远处也能看清楚
- 不用专业术语，要大家看得懂
- 要可视化对比（普通款 vs 加厚款），让客户不动脑就知道选你
- 站在客户角度想问题
- 风格统一，符合平台规则 + 品牌调性 + 类目调性 + 产品调性

---

## 四、色彩系统

### 4.1 王牌三色法

**75/25/5 黄金比例：**
- 75% — 背景色（基础底色，不抢注意力）
- 25% — 产品/主题色（产品本身 + 主色调元素）
- 5% — 点缀/强调色（CTA、价格、核心卖点高亮）

### 4.2 色彩方案选择逻辑

```
输入：产品主色 + 类目 + 目标情绪
│
├── 产品色鲜明？
│   ├── 是 → 以产品色为核心，算法生成和谐配色（互补/类似/分裂互补）
│   └── 否（黑/白/灰/银）→ 从类目预设中选
│
└── 画面中有没有产品？
    ├── 有 → 配色必须跟产品不冲突
    └── 无（纯场景/痛点图）→ 完全由情绪驱动
```

### 4.3 类目色彩预设表（初版）

| 类目 | 方案名 | 主题色 | 背景色 | 字体色 | 情绪 |
|------|--------|--------|--------|--------|------|
| 宠物食品 | 天然健康 | 橙 #FF8C00 + 绿 #4CAF50 | 浅绿 #E8F5E9 | 深棕 #3E2723 | 自然、安心 |
| 儿童餐具 | 清新活泼 | 蓝 #2196F3 | 白 #FFFFFF | 绿 #43A047 | 安全、友好 |
| 母婴玩具 | 温馨安全 | 天蓝 #64B5F6 | 白 #FFFFFF | 明黄 #FFD600 | 温馨、洁净 |
| 手工/编织 | 手作温暖 | 暖橙 #FF9800 | 浅米 #FFF8E1 | 深棕 #4E342E | 手工、温暖 |
| 户外/露营 | 冒险探索 | 军绿 #558B2F + 橙 #FF6D00 | 深灰 #263238 | 白 #FFFFFF | 探索、可靠 |
| 电子/科技 | 高端科技 | 蓝 #1565C0 | 深黑 #121212 | 白 #FFFFFF | 专业、信赖 |
| 家居/枕头 | 舒适柔和 | 米白 #FFF3E0 | 浅灰 #FAFAFA | 深灰 #424242 | 舒适、品质 |
| 健康/保健 | 天然信赖 | 绿 #2E7D32 | 白 #FFFFFF | 深蓝 #1A237E | 健康、可信 |
| 美妆护肤 | 精致轻奢 | 玫瑰金 #E8B4B8 | 白 #FFFFFF | 深灰 #37474F | 精致、高级 |
| 厨房用品 | 食欲活力 | 红 #D32F2F + 橙 #F57C00 | 浅白 #FFFDE7 | 深棕 #3E2723 | 食欲、活力 |

每个类目计划有 2-3 套备选方案，AI 从中选择。

### 4.4 蓝牙灯音箱专用候选方案

| 方案 | 背景 | 主题色 | 字体色 | 调性 |
|------|------|--------|--------|------|
| 户外自然 | 深棕 #3D2B1F 或 森绿 #2D4A22 | 暖琥珀 #FFB347 | 白 #FFFFFF | 露营、自然 |
| 高端科技 | #232F3E → #131A22 渐变 | 天蓝 #08AAE3 | 白 #FFFFFF | 专业、信赖 |
| 温暖生活 | 暖色渐变 | 产品本色 | 米白 #FFF8E7 | 生活、温馨 |

### 4.5 Amazon 品牌色参考

| 颜色 | Hex | 适用场景 |
|------|-----|----------|
| Amazon Orange | #FF9900 | CTA、促销高亮 |
| Ebony Clay | #232F3E | 科技类深色背景 |
| Cool Black | #131A22 | 电子产品暗调主图 |
| Highlighter Blue | #2DBFF8 | 科技感点缀 |

**关键数据：** 文字/背景对比度的影响是颜色选择本身的 3.2 倍（来自 2,847 个 A/B 测试）。

---

## 五、模型选型与 API

### 5.1 模型分工

| 用途 | 模型 | API | 价格 |
|------|------|-----|------|
| 卖点分析 + Prompt 生成 + 质量评估 | Gemini 2.5 Pro | Google AI | — |
| 主力生图 | FLUX 2 Pro | fal-ai/flux-2-pro | ~$0.05/张 |
| 产品融合（多参考图编辑） | FLUX Kontext Multi | fal-ai/flux-pro/kontext/multi | ~$0.04/张 |
| ControlNet + IP-Adapter | FLUX.1 Dev (General) | fal-ai/flux-general | $0.075/MP |
| 中文文字渲染 | Qwen-Image-2.0 | fal-ai/qwen-image-2 | $0.035/张 |
| 连贯套图（实验性） | Wan2.7 Sequential | fal-ai/wan-2.1 | 待测试 |
| 去背景 | BiRefNet | fal-ai/birefnet | 低成本 |

### 5.2 关键 API 限制

- **FLUX 不支持 negative_prompt**（只有 Ideogram 支持）
- **ControlNet 在 fal.ai 只能用 FLUX.1 Dev**（不能用 FLUX 2 Pro）
- **Gemini 当前最新版本是 2.5 Pro**（GA 稳定版，无 3.0/3.1）
- 当前代码中的 model ID `gemini-2.5-pro-preview-05-06` 已过期，需更新为 `gemini-2.5-pro`

### 5.3 现有代码问题（Phase 0 审计）

- API key 硬编码在 step1_gemini_plan.mjs 中，需迁移到 .env
- step1 输出路径写死错误
- 使用过期的 Gemini SDK `@google/generative-ai`，需升级到 `@google/genai`
- image_plan.json 中有无意义的相机型号引用（"Sony A7R IV"）
- negative_prompt 字段对 FLUX 无效
- 整体代码是 Node.js (mjs)，计划迁移到 Python

---

## 六、知识维度与预制策略

### 6.1 什么预制 vs 什么交给 AI

| 维度 | 预制程度 | 具体做法 |
|------|---------|---------|
| **色彩搭配** | 预设表 + Prompt 约束 | 类目预设 JSON（2-3 套/类目），写进 prompt |
| **8图序列** | 已定义 | 固定公式，写进系统 prompt |
| **产品不变量** | 每次写进 Prompt | 形状/颜色/比例/关键元素 |
| **构图** | 模板里已包含 | 不单独死板规定，好模板自带构图 |
| **场景道具** | AI 自主 + 类目方向 | AI 常识足够，prompt 里提方向即可 |
| **文字排版** | 方向性约束 | ≤3行、加粗、对比强，细节后期积累 |
| **卖点话术** | AI 生成 + 格式约束 | AI 文字能力够强，加约束即可 |
| **光线方案** | 后期再加 | 重要但非 Phase 1 优先 |

### 6.2 场景生成策略

| 场景类型 | 生成方式 | 适用 |
|---------|---------|------|
| 产品为主的图 | **分步**：先生场景→融合产品 | 主图、细节图、规格图 |
| 场景为主的图 | **整体**：一起生成 | 生活图、痛点图 |
| 无产品的图 | 整体生成，不放产品 | 痛点图、对比图 |

---

## 七、GitHub 开源项目参考

### 7.1 最值得参考的项目

| 项目 | Stars | 核心价值 | URL |
|------|-------|---------|-----|
| **geongeorge/picture-it** | 新 | CLI 链式管道：去背景→生场景→文字→产品叠加→调色。有 Claude Skill 集成 | github.com/geongeorge/picture-it |
| **vallessergi/creative-automation-pipeline** | 低 | 完整营销管道：Flux Dev 生图→AI 审核→多变体→指标跟踪 | github.com/vallessergi/creative-automation-pipeline |
| **rudreshmehta/Creative-Automation-Pipeline** | 低 | 品牌合规管道：Vertex AI→3比例→9语言→K-means 色彩检测→Logo 检测 | github.com/rudreshmehta/Creative-Automation-Pipeline |
| **FotographerAI/ZenCtrl** | 352 | 基于 FLUX.1 的产品图：保前景+换背景+去模糊+色彩校正 | github.com/FotographerAI/ZenCtrl |
| **jflournoy/image-gen-pipe-v2** | 低 | 迭代优化：GPT-4 精炼 prompt→生图→GPT-4V 打分→循环 | github.com/jflournoy/image-gen-pipe-v2 |

### 7.2 其他有价值的项目

| 项目 | Stars | 用途 |
|------|-------|------|
| brycedrennan/imaginAIry | 8,100 | Python 图像生成库，CLI+API，ControlNet/inpainting/upscale |
| tencent-ailab/IP-Adapter | 6,500 | 22M 参数的图像提示适配器，兼容 ControlNet |
| adieyal/sd-dynamic-prompts | 2,300 | Prompt 模板语法 `{A|B|C}` + wildcard + 组合模式 |
| MiddleKD/ComfyUI-productfix | — | Latent Injection 解决产品 Logo/文字变形 |
| yahoo/photo-background-generation | 74 | CVPR 2024，显著物体感知背景生成 |
| 302ai/302_ecom_image_generator | 7 | 电商场景图+重新打光，中英日三语 |
| aws-samples/product-catalog | 8 | AWS Step Functions 编排完整 listing 管道 |
| Dabble-Studio/3d-to-photo | 429 | 3D 模型→AI 场景 |
| CTDave001/automated_mockups | — | 模板驱动 mockup 批量生成 |
| lambortao/PixPro | 320 | AI 图像后处理：去背景/擦除/扩展/放大 |
| dagthomas/comfyui_dagthomas | 278 | 多 LLM prompt 生成+视觉分析 |
| Bria-AI/ComfyUI-BRIA-API | 67 | 商用级背景生成（100%授权数据训练） |

### 7.3 色彩理论结构化数据（GitHub）

| 资源 | 内容 | 格式 |
|------|------|------|
| meodai/skill.color-expert | 28.6 万字色彩专家知识，144 文件 | Markdown + JSON |
| antvis/color-schema | 语义化色板 JSON Schema 标准 | JSON Schema |
| VladislavKorecky/color-psychology-database | 情绪→颜色映射+重要性评分 | JSON + YAML |
| meodai/pro-color-harmonies | 算法生成和谐配色（OKLCH 色彩空间） | TypeScript |
| meodai/color-names | 18,000+ 命名颜色 | JSON/CSV/API |
| josh-ashkinaze/Emotion-Colors | 264 种情绪→主色映射 | 数据集 |

### 7.4 行业关键发现

1. **没有单一项目做到了我们要做的全部。** 市面上最多做到"单张图换背景"
2. **行业主流管道：** 去背景→生成遮罩→Inpainting/ControlNet 生场景→后处理
3. **产品一致性三条路：** LoRA 微调（最强）、IP-Adapter 零训练（灵活）、Prompt 模板+种子（最轻）
4. **质量控制是最薄弱环节。** 大多数项目不做自动验证
5. **fal.ai Workflow JSON** 支持多模型链式调用，节点间用 `$node-id.field` 传值

---

## 八、设计知识参考

### 8.1 光线方案（11 种，含 AI Prompt 关键词）

| 灯光风格 | Prompt 关键词 | 适用 |
|---------|-------------|------|
| 伦勃朗光 | `Rembrandt lighting, dramatic triangle shadow, 45-degree key light` | 高端主图 |
| 蝶形光 | `butterfly lighting, beauty lighting, frontal key light, glamour` | 美妆护肤 |
| 轮廓光 | `rim lighting, backlit, edge glow, halo effect` | 科技/LED 产品 |
| 高调光 | `high-key lighting, bright studio, minimal shadows, clean` | 标准电商白底 |
| 低调光 | `low-key lighting, dark background, dramatic shadows` | 高端暗调 |
| 自然光 | `soft natural window light, warm tone, golden hour` | 场景/生活图 |
| 三点光 | `three-point lighting, professional studio, balanced` | 通用产品图 |
| 蛤壳光 | `clamshell lighting, fill from below, soft shadow` | 商业摄影 |
| 环形光 | `loop lighting, soft portrait, natural shadow` | 自然亲切 |
| 分割光 | `split lighting, half shadow, dramatic contrast` | 戏剧感 |
| 宽光 | `broad lighting, open bright` | 明亮开阔 |

### 8.2 构图法则

| 规则 | 适用图类型 | Prompt 关键词 |
|------|-----------|-------------|
| 居中填满 | 主图（Slot 1） | `centered product, filling 85% of frame` |
| 三分法 | 场景图、生活图 | `rule of thirds composition` |
| F 型 | 信息图（文字多） | `F-pattern layout` |
| Z 型 | 图片为主 | `Z-pattern visual flow` |
| 黄金比例 | 高端产品图 | `golden ratio composition, phi grid` |
| 对角线 | 运动/动感 | `diagonal composition, dynamic angle` |

### 8.3 文字排版规则

- 推荐字体：Montserrat（标题）、Open Sans / Roboto（正文）、Lato（亲切感）
- 层级：标题 Bold 30px+ / 副标题 Medium 24px+ / 正文 Regular 18px+
- 对比度 6:1 以上（转化率高 3.2 倍）
- 左对齐=结构感，居中=高端感

### 8.4 场景道具选择规则

1. 道具必须是配角，不抢产品风头
2. 道具颜色与产品和谐（类似色或中性色）
3. 道具逻辑合理（场景里该有的东西）
4. 至少一个道具提供尺寸参照
5. 每场景最多 3-5 个道具

### 8.5 推荐设计书籍

| 书名 | 用途 |
|------|------|
| 葱爷 "19大设计调性，160种配色方案" | 19 种调性 × 8-9 套配色，可直接提炼成预设 |
| 伊达千代 《色彩设计的原理》 | "色彩抽屉"方法论：按用途找色彩方案 |
| 张修 "电商设计解析与案例教程" | 10 年电商设计经验 |
| Josef Albers "Interaction of Color" | 色彩相对性理论（有数字版互动版） |

### 8.6 Itten 七种色彩对比法则（可做验证规则）

1. **色相对比** — 不同颜色放一起
2. **明暗对比** — 亮色与暗色（文字可读性）
3. **冷暖对比** — 科技感(冷) vs 家居感(暖)
4. **互补对比** — 色环对面的颜色
5. **类似对比** — 色环相邻的颜色
6. **饱和度对比** — 高饱和 vs 低饱和
7. **面积对比** — 颜色占比（= 75/25/5）

---

## 九、模板素材库方案

### 9.1 存储架构

```
MongoDB templates collection:
{
  "_id": "hero_dark_dramatic",
  "type": "hero",                    // 图片类型
  "scope": "single" | "set",        // 单张 or 套图
  "description": "深色背景戏剧感主图",
  "tags": ["dark", "dramatic", "LED", "premium"],
  "match_conditions": {
    "product_categories": ["electronics", "speakers"],
    "features_required": ["LED"]
  },
  "prompt_template": "A {{product_shape}} {{product_color}} ...",
  "compatible_models": ["flux-2-pro", "ideogram-v3"],
  "reference_images": [
    { "role": "style_reference", "url": "gridfs://..." }
  ],
  "style_anchor": {
    "color_temperature": "cool",
    "dominant_hues": ["#1A1A1A", "#FFB800"],
    "contrast": "high"
  },
  "generation_strategy": "together" | "composite",
  "scene_elements": ["bonfire", "wooden table"],
  "quality_score": 8.5
}
```

### 9.2 Workflow 工具接口

```python
search_templates(tags, type)          # 查 MongoDB，返回匹配模板
get_template(template_id)             # 取完整模板
render_prompt(template_id, vars)      # 填充变量输出最终 prompt
generate_image(prompt, model)         # 调用 fal.ai
validate_quality(image, criteria)     # Gemini 评分
adjust_tone(image, target_palette)    # 色调统一
```

---

## 十、分阶段执行计划

### 阶段 A：MVP 跑通（最优先，1-2 周）

```
目标：端到端跑通，产出第一批图，记录问题

任务：
1. Python Workflow 脚本
2. Gemini 卖点分析（一个 prompt）
3. Gemini 生成 7 张图的 Prompt（含色彩预设 + 8图公式 + 产品不变量约束）
4. fal.ai FLUX 2 Pro 生图
5. 人工评估 → 记录问题清单

交付物：能跑的脚本 + 第一批结果 + 问题清单
```

### 阶段 B：质量提升（基于 A 的问题清单）

```
可能的问题和对应方案：
- 产品变形 → 加 Kontext Multi 融合步骤
- 色彩不一致 → 加色彩预设选择 + 后处理 histogram match
- 文字模糊 → 换 Qwen 或后期合成
- 质量不稳定 → 加 Gemini 评分 + 重试循环
- 缺乏参考 → 开始收集模板素材库

交付物：优化后的 Workflow + 效果对比
```

### 阶段 C：模板驱动 + 规模化

```
- 收集 50-100 套优秀案例 → 素材库
- 模板匹配逻辑
- 图文合成（文字排版）
- 更多品类适配
- 考虑是否需要升级到 Agent
```

---

## 十一、方案审核结论

### 11.1 风险与反思（基于《人月神话》）

| 风险 | 应对 |
|------|------|
| 第二系统效应（过度设计） | 砍到 3 个阶段，先跑 MVP |
| 知识库维护成本过高 | 改为 Prompt 约束 + 轻量预设表 |
| 忽视执行层难题（产品变形、文字模糊） | 先跑 MVP 暴露真实问题 |
| 系统耦合太紧 | Workflow 线性流程，每步独立 |

### 11.2 核心原则

1. **先跑通，再优化** — 先看裸跑能产出什么
2. **按问题加东西，不按理论加** — 色彩不行才加预设，不是因为理论重要就加
3. **Workflow 不是 Agent** — 步骤已知，用函数调用
4. **知识用 Prompt 约束传递** — 直到约束不够用了再升级

---

## 十二、深度参考项目（技术实现细节）

### 12.1 picture-it — 链式图像管道

**项目:** github.com/geongeorge/picture-it（TypeScript, MIT）
**核心理念:** "Photoshop for AI agents" — 每个命令只做一件事，输入图→处理→输出图，像 Unix 管道一样串起来。

**16 个 CLI 命令:**
- AI 类：`generate`（文生图）、`edit`（多图编辑）、`remove-bg`、`replace-bg`、`upscale`
- 本地处理：`crop`、`grade`（调色）、`grain`、`vignette`、`text`、`compose`、`template`、`info`
- 编排类：`pipeline`（JSON 步骤）、`batch`（并行多管道）

**Pipeline JSON 示例:**
```json
[
  { "op": "generate", "prompt": "dark cosmic background", "size": "1200x630" },
  { "op": "text", "title": "Hello World", "font": "DM Serif", "fontSize": 72 },
  { "op": "grade", "name": "cinematic" },
  { "op": "vignette", "opacity": 0.3 }
]
```

**调色预设（Sharp 实现）:**
- cinematic: RGB 矩阵重映射（青色阴影+暖色高光）
- moody: 降饱和度 + 压暗黑色
- vibrant: 饱和度 ×1.3
- warm-editorial: 暖色色温叠加
- cool-tech: 冷蓝色调 + 对比度提升

**模型路由（15 个模型，$0.003-$0.25）:**
- 生成默认: flux-schnell ($0.003)
- 单图编辑: kontext ($0.04)
- 多图编辑: seedream ($0.04)
- 高质量: recraft-v4 ($0.25)

**Zone 定位系统:** 12 个预定义区域（hero-center, title-area, top-bar 等），百分比→像素转换。

**对我们的价值:** 每张 listing 图 = 一个 pipeline JSON。`remove-bg + compose` 模式（而非让 AI 编辑）专门推荐用于需要保留 Logo/细节的产品图。

### 12.2 image-gen-pipe-v2 — 评估循环机制

**项目:** github.com/jflournoy/image-gen-pipe-v2（Node.js + Python）
**核心理念:** Beam Search 束搜索 — 生成多张→打分→淘汰差的→改进好的→再生成→再打分。

**Prompt 双维度分离:**
- **WHAT**（内容）：什么东西、什么场景、什么动作
- **HOW**（风格）：什么光线、什么构图、什么色调
- 奇数轮改 WHAT，偶数轮改 HOW，改一个时另一个不变
- **防止"改风格时内容跑偏"的问题**

**评分系统（GPT-4V）:**
```
promptFidelity (0-1) → alignmentScore (0-100)
aestheticScore (0-10) → 归一化到 0-100
totalScore = 0.7 × alignment + 0.3 × aesthetic
（内容还原 70%，美感 30%）
```

**评分校准标准:**
- 0.5-0.6: 典型初次生成水平
- 0.7-0.8: 好的精炼后水平
- 0.9-1.0: exceptional

**分数→改进建议:**
- ≥80: "表现良好，做细微调整"
- 60-79: "需要中等程度改进"
- <60: "需要大幅修改"

**默认参数:** N=4 候选、M=2 保留、2 轮迭代、固定轮数不做收敛判断。

**对我们的简化应用:**
```python
async def generate_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        image = await fal_generate(prompt)
        score = await gemini_evaluate(image, prompt)
        if score >= 70: return image
        prompt = await gemini_refine_prompt(prompt, score.feedback)
    return best_image
```

### 12.3 Creative-Automation-Pipeline — 品牌合规检查

**项目:** github.com/rudreshmehta/Creative-Automation-Pipeline（Python）
**核心理念:** 生成后验证品牌合规 — 色彩是否正确、Logo 是否存在。

**完整流程:**
```
品牌规范 JSON → 法律合规检查（禁词）→ 翻译文案 → 生成产品图 → 合成广告（3 比例）→ 品牌合规检查 → 上传 → 报告
```

**色彩验证算法（11 色阶 + 欧几里得距离）:**
```python
# 把品牌色生成 11 个明暗变体（±5 级，每级 RGB 偏移 15）
# 对每个像素计算与 11 个变体的欧几里得距离
# 距离 ≤ 40 的像素算"匹配"
# 匹配像素 ≥ 0.1% 总像素 → 通过
shade_range = 5, shade_step = 15, tolerance = 40, threshold = 0.001
```

**Logo 检测:**
```python
cv2.matchTemplate(image_gray, logo_gray, cv2.TM_CCOEFF_NORMED)
# confidence ≥ 0.7 → 通过
```

**关键 Prompt 技巧:**
> "Leave empty space at the top-right corner area (clear space for logo)"
> AI 做创意构图，代码精确贴 Logo — 分工明确。

**外部化 Prompt 模板:** `prompts/*.txt` 用 `{placeholder}` 变量替换，非技术人员可修改。

**对我们的价值:**
1. 色彩验证逻辑可直接复用
2. "AI 留白 + 代码精贴" 模式用于文字/Logo
3. 合规检查作为 pipeline 步骤，不及格可触发重生成

### 12.4 fal.ai 社区新发现

**新发现的 fal.ai 产品图专用 API:**

| API | 功能 | 价格 |
|-----|------|------|
| `fal-ai/image-apps-v2/product-photography` | 产品摄影专用，输出 4K (4096×4096) | $0.04/张 |
| `fal-ai/bria/product-shot` | 商用安全（100%授权数据），可指定产品位置/大小 | 待确认 |
| `fal-ai/flux-kontext-lora/inpaint` | Kontext + LoRA 修复式编辑 | 待确认 |
| `fal-ai/flux-pro/v1/fill` | 高级 inpainting | 待确认 |

**fal.ai Workflow JSON 系统:**
```json
{
  "nodes": {
    "remove-bg": { "type": "run", "app": "fal-ai/birefnet", "input": {"image_url": "$input.product_image"} },
    "gen-scene": { "type": "run", "depends": ["remove-bg"], "app": "fal-ai/flux-2-pro", "input": {"prompt": "$input.scene_prompt"} },
    "compose": { "type": "run", "depends": ["remove-bg","gen-scene"], "app": "fal-ai/flux-pro/kontext/multi" }
  }
}
```
- 只有 `run` 和 `display` 两种节点
- `$node-id.field` 引用前步输出
- 不支持字符串拼接（需用 `fal-ai/text-concat`）

**fal-ai-community/skills（Claude Code 可用）:**
- fal-generate / fal-image-edit / fal-workflow / fal-train / fal-upscale / fal-vision
- 可直接安装到 Claude Code：`npx skills add fal-ai-community/skills -g`

**HuggingFace 关键模型:**
- **Finegrain Product Placement LoRA** — 基于 FLUX Kontext，产品图+场景图+边界框→自然融合，开源权重
- **In-Context-LoRA (ali-vilab)** — 从一张产品图生成多种光线变体
- **FLUX Realism LoRA** — 增强照片真实感

**ComfyUI 产品图 Workflow（OpenArt.ai 可下载）:**
- 产品换背景 / 产品重新打光(IC-Light) / 精准放置+细节保持 / 电商模特换装

**n8n 自动化流程模板:**
- 奢侈品广告自动化 / AI 广告图 / AI 产品摄影+Instagram 发布
- fal.ai 官方 n8n 集成文档: docs.fal.ai/model-apis/guides/n8n

**Civitai 产品摄影 LoRA:**
- Product Photography SDXL / Outdoor Product Photography / Majicproduct_v4 / Beauty Product Photo

**案例参考:**
- DEV.to: 30+ 模型管道案例（Next.js + Express + Replicate/fal.ai）

---

## 十三、待解决的遗留问题

1. API key 硬编码 → 需迁移到 .env
2. Gemini model ID 过期 → 需更新为 `gemini-2.5-pro`
3. Gemini SDK 过期 → 需从 `@google/generative-ai` 升级到 `@google/genai`
4. Node.js → Python 迁移（整个代码库）
5. 模板素材收集标准和流程待定义
6. Prompt 模板具体格式待设计
7. 色彩预设表需要扩充到更多类目
8. 图文合成技术方案待确认（Playwright vs Canvas vs Pillow）
9. 测试 `fal-ai/bria/product-shot` 和 `fal-ai/image-apps-v2/product-photography` 新 API
10. 评估是否引入 Finegrain Product Placement LoRA
11. 设计评估循环的具体评分标准（参考 image-gen-pipe-v2 的双维度打分）
12. 色彩验证逻辑实现（参考 Creative-Automation-Pipeline 的色阶距离算法）
