# 电商产品图 AI 生成提示词(Prompt)最佳实践 — 研究报告

**研究日期：2026-04-12 | 针对项目：Excitat 蓝牙灯笼音箱 Listing 套图生成系统**

---

## 一、提示词的具体写法：框架与模板

### 1.1 公认的五要素框架

| 要素 | 说明 | 灯笼音箱示例 |
|------|------|------------|
| **Subject (主体)** | 产品类型、材质、颜色、独特特征 | "Matte black cylindrical Bluetooth speaker with built-in LED lantern, textured grip handle on top, warm amber light glowing through translucent diffuser" |
| **Lighting (光照)** | 光源类型、方向、硬度、色温 | "Three-point softbox setup with warm key light from upper left, subtle rim light highlighting the handle" |
| **Background (背景)** | 场景、表面、环境 | "On a weathered wooden picnic table, blurred forest campsite in background, golden hour atmosphere" |
| **Camera (相机)** | 角度、景深（不要写具体型号） | "Shot at 45-degree angle, shallow depth of field, sharp focus on speaker body" |
| **Mood/Style (氛围)** | 整体风格、情绪、质量修饰 | "Commercial product photography, warm adventurous mood, clean composition, ultra-realistic" |

### 1.2 各平台 Prompt 写法差异

**Flux 系列（推荐用于 Hero/Lifestyle/Detail 图）**

Flux 对自然语言的理解最强，官方指南明确建议：
- 用完整句子描述，不要用逗号分隔的关键词列表
- **不要使用权重语法** `(keyword:1.5)` — Flux 不支持
- 不要写具体相机型号（Sony A7R IV 对 AI 无意义）
- **Flux 不原生支持 negative prompt** — 用正面描述替代

Flux 示例 prompt：
```
Professional commercial product photography of a cylindrical Bluetooth speaker 
with integrated LED lantern, matte black body with soft amber glow emanating 
from the translucent top section. The speaker sits centered on a polished 
dark slate surface. Two softbox lighting setup creates clean, even illumination 
with subtle shadows on the right side. Shot at 45-degree angle, sharp focus 
throughout, high dynamic range. The background is a smooth dark gradient 
fading to pure black. No text, no watermark, no people.
```

**Ideogram V3（推荐用于 Benefit/Specs 等含文字图）**

核心优势是文字渲染，文字准确率约 90%。
- 文字指令直接写在 prompt 中，用引号括住需要渲染的文字
- Style Reference 功能支持上传最多 3 张参考图
- Style Code：8位字符代码，可复用视觉风格
- Random 风格模式可探索 43 亿种预设组合

Ideogram 示例：
```
Professional product infographic showing a Bluetooth lantern speaker. 
Large bold white text at top reads "3-IN-1 OUTDOOR COMPANION". 
Below the product image, three icons with labels: "360° Sound", 
"12H Battery", "IP65 Waterproof". Dark gradient background with 
subtle warm accent lighting. Clean modern typography, commercial 
product design layout.
```

**Midjourney V6/V7（适合概念探索和创意风格）**

- 短而精的高信号词汇，配合 reference images 最佳
- 参数系统：`--ar 1:1`、`--s 100`、`--style raw`、`--no text`

### 1.3 完整的 Prompt 模板（适用于灯笼音箱项目）

```
Hero 主图 (Flux 2 Pro):
"Commercial product photography of [PRODUCT_DESCRIPTION] centered on 
[SURFACE]. [LIGHTING_SETUP]. Shot at [ANGLE], [DEPTH_OF_FIELD]. 
[BACKGROUND]. [QUALITY_MODIFIERS]. No text, no watermark, no people."

Lifestyle 场景图 (Flux 2 Pro):
"Lifestyle product photography showing [PRODUCT] in use at [SCENE]. 
[PERSON_DESCRIPTION] is [ACTION]. [LIGHTING_CONDITIONS]. [MOOD]. 
[COMPOSITION_RULE]. Warm, inviting atmosphere, authentic moment."

Benefit 卖点图 (Ideogram V3):
"Product infographic design for [PRODUCT]. Large bold text reads 
'[HEADLINE]'. [PRODUCT_POSITION]. [VISUAL_ELEMENTS] illustrating 
[BENEFIT]. [COLOR_SCHEME]. Clean modern typography, professional 
e-commerce layout."

Detail 细节图 (Flux 2 Pro):
"Extreme close-up macro photography of [SPECIFIC_DETAIL] on [PRODUCT]. 
[MATERIAL_DESCRIPTION]. [MACRO_LIGHTING]. Razor-sharp focus on 
[FOCUS_POINT], beautiful bokeh background."

Specs 参数图 (Ideogram V3 + HTML 模板):
"Technical specification diagram of [PRODUCT] on [BACKGROUND]. 
Dimension lines and measurement annotations. Text labels: [SPECS_LIST]. 
Icons for each feature. Clean, professional technical illustration style."
```

---

## 二、提示词的使用方式：结构、格式与技巧

### 2.1 结构化 JSON → 模型原生格式

推荐在内部使用结构化数据，由 Gemini 转换为各平台原生格式：

```json
{
  "subject": {
    "product": "Bluetooth lantern speaker",
    "material": "matte black aluminum body, translucent frosted PC diffuser",
    "color": "black body, warm amber LED glow",
    "key_features": ["grip handle on top", "speaker grille at bottom", "mode button"]
  },
  "scene": {
    "surface": "rustic wooden camping table",
    "background": "blurred pine forest, evening sky with warm sunset tones",
    "props": ["enamel camping mug", "folded trail map"]
  },
  "lighting": {
    "type": "golden hour natural light + product's own LED glow",
    "direction": "warm light from upper left",
    "quality": "soft, diffused, no harsh shadows"
  },
  "camera": {
    "angle": "slightly elevated 30-degree angle",
    "focus": "sharp on product, soft background bokeh",
    "depth_of_field": "shallow"
  },
  "style": {
    "mood": "adventurous, warm, inviting",
    "quality": "commercial product photography, ultra-realistic",
    "exclude": "no text, no watermark, no people's faces"
  }
}
```

### 2.2 Negative Prompt 最佳实践

**电商产品图专用 negative prompt 模板（SDXL/ComfyUI 用）：**
```
blurry, low quality, low resolution, bad lighting, harsh shadows, 
overexposed, underexposed, text overlay, watermark, cluttered background, 
distorted perspective, color inaccurate, soft focus, out of focus, 
pixelated, jpeg artifacts, deformed product, floating product
```

**注意：Flux 不原生支持 negative prompt。** 用正面描述替代。

### 2.3 权重标记用法

| 平台 | 语法 | 建议 |
|------|------|------|
| SDXL/ComfyUI | `(keyword:1.2)` 增强 | 不超过 1.4 |
| Midjourney | `::2` 分段权重 | 用 `--no` 替代负面词 |
| Flux | **不支持权重语法** | 用词序和详细程度控制 |
| Ideogram | 无显式权重 | 依靠 Style Reference |

---

## 三、产品一致性方案

### 3.1 商业工具的做法

**共同模式：所有商业工具都采用"实拍抠图 + AI 换背景"策略，产品本体来自真实照片，绝不让 AI 凭空生成产品。**

- **Photoroom**：上传产品图 → 自动抠图 → 选择/生成背景 → 智能光影匹配
- **Pebblely**：上传图片 → 自动背景移除 → 90+ 预设主题 → AI 自动阴影和反射
- **Flair AI**：上传产品图后可拖放到 AI 生成的场景中
- **美间AI**：三步流程（上传→描述→下载），预设垂直行业模板库
- **LinkFox**：自动识别品牌元素保持出图风格一致性

### 3.2 ControlNet + IP-Adapter + LoRA 三驾马车

**ControlNet — 控制结构**
- Canny Edge：提取产品轮廓线条，确保生成图保持产品精确形状
- Depth Map：保持空间层次关系
- 组合使用：Canny + Depth 同时启用可最大程度保留原图细节

**IP-Adapter — 控制风格**
- 权重建议：与文字 prompt 配合时设 0.3-0.6
- 配合 ControlNet Lineart 使用效果最佳：IP-Adapter 管风格，ControlNet 管结构

**LoRA — 控制品牌风格**
- 训练数据：10-20 张品牌风格一致的图片即可
- Multi-LoRA 组合：品牌风格 LoRA + 产品材质 LoRA + 场景风格 LoRA

**三者协同工作流：**
```
产品白底图 
  → BiRefNet 抠图（去除背景）
  → ControlNet Canny（锁定产品轮廓）
  → ControlNet Depth（锁定空间关系）
  → IP-Adapter（注入风格参考图，权重 0.4）
  → LoRA（品牌风格微调）
  → Flux/SDXL 生成（文字 prompt 描述背景场景）
  → IC-Light 重新打光（使产品光影与新背景匹配）
  → 输出
```

### 3.3 "实拍抠图 + AI 换背景" 具体工作流

```
步骤 1: 产品抠图
  工具: BiRefNet / RMBG-2.0 / SAM2
  输出: 透明背景 PNG

步骤 2: 背景生成
  输入: 文字 prompt 描述目标场景
  模型: Flux 2 Pro（写实场景）/ Ideogram V3（含文字的图）

步骤 3: 产品置入 + 光影匹配
  工具: IC-Light（智能重打光）
  参数: denoise 0.35-0.45（0.42 是电商行业经验值）

步骤 4: 边缘融合
  工具: Inpainting（对产品与背景交界处做局部重绘）
```

### 3.4 灯笼音箱的特殊挑战

产品自身会发光（LED灯笼部分），意味着：
- IC-Light 重打光时需保留产品自身的发光效果
- 场景图中产品的光晕会影响周围环境
- prompt 中加入："warm amber glow from the lantern illuminating the surrounding surface"

---

## 四、模板系统：电商套图的构图规则

### 4.1 七张套图的固定构图规则

**图1 — Hero 主图**
- 产品居中，占画面 75-85%
- 纯白或渐变深色背景
- 正面略偏 15-30 度
- 无文字、无道具、无人物（Amazon 主图要求）

**图2 — Lifestyle 场景图**
- 三分法则，产品在三分线交叉点
- 真实使用环境（露营/阳台/花园派对）
- 灯笼音箱场景矩阵：露营夜景 / 后院BBQ / 阳台晚餐 / 海滩日落

**图3 — Benefit 卖点图**
- 左右分栏或上下分栏
- 一图一卖点（"radical simplicity"）
- 大标题 3-5 词，副文字 8-15 词

**图4 — Detail 细节图**
- 微距特写，浅景深
- 材质纹理、做工细节、按钮/接口

**图5 — Specs 参数图**
- 产品全貌 + 标注线 + 参数文字
- 技术图解风

**图6 — Differentiator 差异化图**
- 左右对比或多场景拼接
- check/cross 图标突出优势

**图7 — Trust 信任图**
- 温馨场景，礼盒开箱或赠礼
- 包装展示、配件全家福

---

## 五、风格控制：统一风格方案

### 5.1 Ideogram Style Code
- 生成一张满意的"风格基准图"→ 记录 Style Code → 后续图复用
- 仅 Ideogram 内有效，不跨模型

### 5.2 Flux Redux / Kontext
- **Redux**：图生图变体生成器，适合从基准图生成风格相似的变体
- **Kontext**（推荐）：支持自然语言指令编辑，如"Change the background to a beach sunset while keeping the product exactly the same"

### 5.3 Seed 的正确用法
- 调试阶段：固定 seed，只改 prompt 细节，观察每次改动的影响
- 变体生成：固定 prompt，改变 seed，获得不同构图
- **不要依赖 seed 做跨图一致性** — 用 Style Code / IP-Adapter / LoRA

### 5.4 统一风格的综合策略

```
层级1: 风格锚点定义（Gemini 方案设计阶段）
  - style_consistency_anchors: ["暗色背景", "RGB光晕", "白色粗体标题"]
  - 色彩规范: 产品主色 HEX、强调色 HEX
  - 光照基准: 统一光源方向和色温

层级2: 模型内一致性
  - Flux 系列: 共享相同的 lighting/camera/mood 段落
  - Ideogram 系列: 使用同一 Style Code

层级3: 跨模型一致性
  - 品牌框作为统一视觉元素
  - Gemini Vision 评审中加入"风格一致性"维度
```

---

## 六、视觉吸引力：转化率最佳实践

### 6.1 高转化率电商图的共性

**构图原则**
- 移动端优先：70%+ 的购买来自手机
- 一图一信息：每张图只传达一个核心卖点
- 留白策略：避免杂乱
- 三分法则

**配色心理学**
- 科技/电子：蓝色和灰色（信任+专业）
- 户外/运动：绿色和棕色（自然+冒险）
- 灯笼音箱建议：暖琥珀色 + 深色背景 = 高端感 + 温暖氛围

**信息层级**
- 第一层（0.5秒）：产品轮廓和主色调 — "这是什么"
- 第二层（2秒）：核心卖点标题 — "为什么要买"
- 第三层（5秒+）：细节参数 — "符合我的需求"

### 6.2 A+ Content 设计要点

- Premium A+ Content 可带来 20% 销售提升
- 图片上文字最多 3-5 个词
- 混合使用真实产品照片和 AI 增强图片

### 6.3 灯笼音箱转化率优化建议

```
1. Hero 图突出"发光效果" — 灯笼的暖光是最大视觉差异点
2. Lifestyle 图场景多样化 — 露营/阳台/派对覆盖多个购买动机
3. "3合1" 可视化 — 用一张图清晰展示灯+音箱+充电宝
4. 尺寸参照 — 放常见物品（如手掌）做大小参照
5. 防水演示 — IP65 视觉化展示（水溅效果）
```

---

## 七、ComfyUI 工作流架构（Phase 2 参考）

```
[输入层] LoadImage（产品白底图）
    ↓
[抠图层] BiRefNet / RMBG-2.0（背景移除）
    ↓
[控制层] ControlNet Canny (0.7-0.9) + Depth (0.5-0.7) + IP-Adapter (0.3-0.5)
    ↓
[生成层] Flux 2 Pro / SDXL（denoise 0.35-0.45）
    ↓
[打光层] IC-Light（匹配光影）
    ↓
[后处理层] Inpainting（边缘融合）+ Upscale
    ↓
[输出层] SaveImage（2000x2000）
```

---

## 八、具体可操作的建议

### Phase 0 立即可用
1. Prompt 模板化（五要素框架 + 模型差异化）
2. 风格锚点注入所有 prompt
3. Ideogram Style Code 复用
4. 产品一致性采用"抠图+换背景"

### Phase 1 流程固化
5. 建立 Prompt 模板库（7类型 x 4模型 = 28 模板）
6. Flux Kontext 集成（指令式修改背景）
7. 评审增加"风格一致性"维度

### Phase 2 长期建设
8. 训练 Excitat 品牌 LoRA
9. ComfyUI 节点工作流搭建
10. A/B 测试闭环

---

## Sources

- Claid.ai - How to write prompts for AI product photos
- Apatero - AI Product Photography Prompts 2025
- flux-ai.io - How to Create Product Photography with Flux AI
- Black Forest Labs - FLUX.2 Prompting Guide
- fal.ai - Flux 2 Prompt Guide & Developer Guide
- Rajat AI - Automate Product Photography with ComfyUI
- ComfyUI.org - Mastering Image Retouching for E-commerce
- Hugging Face - IP-Adapter Documentation
- Medium - The Ultimate Combo: LoRA + ControlNet + IP-Adapter
- Ideogram - 3.0 Features & Style Reference Docs
- Photoroom - 50 AI image prompts for e-commerce
- Sider.ai - 30 Prompt Templates for E-Commerce Product Photos
- Amazon Seller Central - A+ Content Design Guide
- EcomClips - A+ Content Tips That Boost Conversions 2025
- Pebblely - AI Product Photography
- 美间AI - 电商设计平台
- 知乎 - 主流AI图像生成模型提示词工程深度解析
- Runware - FLUX.1 Kontext
- Stable Diffusion Art - Flux Redux for Image Variation
