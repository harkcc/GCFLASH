# EXCITAT eMAG Banner + HTML 稳定路线对话留痕

日期：2026-05-24  
状态：阶段性沉淀，不是最终版本  
范围：`/Users/cc/Desktop/photo_show` 内的稳定路线实验；尚未迁移到 `agent-platform` 内置 Agent

## 1. 当前结论

这轮讨论不是在确认最终视觉风格，而是在把可稳定复用的生成路线先沉淀下来。当前真正跑通的是“稳定路线”：

```text
Plan / DesignSpec -> Generate or Composite -> Validate -> Repair -> Final Export
```

核心判断：

- 品牌视觉统一使用大写 `EXCITAT`；`excitat` 只作为内部 slug。
- 稳定生产不依赖模型直接写小字、参数、QA、Review 或服务承诺。
- 复杂模块优先做成图片或 GIF，再用 eMAG 详情 HTML 的 `<img width="1140">` 嵌入。
- AI 更适合做背景、氛围、人物/场景底图；精准文字、产品图、参数、标签、卡片必须本地确定性拼接。
- 当前输出只是稳定组件路线的样例，不代表最终 Design MD、最终 Banner 库或最终详情页质量。

## 2. 已锁定的讨论决策

### 品牌与命名

- 展示品牌：`EXCITAT`。
- 禁止在新视觉中继续使用：`EXIT`、`Excité`、`Exceity`、`EXITE`、`BestPlaza`。
- 旧品牌名只允许作为历史参考或反例出现，不能进入新生产 HTML。

### QA 和 Review 分离

- QA 是买家问题模板，用来回答购买前疑问。
- Review 是评价模板，必须来自真实评论、真实评分、真实日期和真实来源。
- 没有真实评论时，可以做 `Review preview` 或 `Feedback preview`，但必须明显标记为概念预览，不能伪造姓名、日期、星级。

### eMAG HTML 与动效

- eMAG 里“左边会动”的效果按预渲染 GIF/WebP 理解：先把动效做进图，再通过 `<img>` 嵌入。
- 不依赖 JS、iframe、form 或复杂交互。
- 当前稳定动效只保留：
  - `shine_sweep`：黑金/蓝光扫过，适合品牌 Banner、Review Banner、Brand closer。
  - `step_highlight`：步骤编号依次亮起，适合使用步骤和操作流程。
- 人物微动、产品微动、粒子特效、边缘发光、复杂呼吸边框先归为实验层，不能默认进稳定生产。

### 素材权利与官方素材

- eMAG 官方素材可以作为构图、气氛、色彩和人物风格 reference。
- 未确认授权前，官方素材不能直接作为商业生产图复用。
- 产品结合类 Banner 必须依赖真实 Listing 图、详情图、产品抠图或已确认可用素材。

### 页面节奏

- 不要连续堆黑色重模块。
- 不要每个模块都加小框。
- 小框只适合首屏三锚点、参数、步骤、对比、手册说明。
- 如果上一段已经是大图，下一段应改成短文本、裁切 proof 图、参数板、QA 或视觉缓冲。
- 白底、浅色块、简洁文字模块是必要的视觉休息区，不是“低级”。

## 3. 当前稳定路线组件

### A. QA 稳定 Banner

用途：

- 放在 FAQ/购买前疑问区域。
- 用清爽背景、短问题、短答案帮助用户不返回顶部找答案。

稳定做法：

- 背景可白底、浅灰、浅蓝、浅绿，避免重黑。
- 只放 3-4 个真实买家问题。
- 每个问题只回答一个疑虑。
- 不做 Review 样式，不加头像、星级、日期。

适合拼接方式：

- `pure_composite`。
- 本地叠字、本地图标、本地卡片。

### B. Review / Feedback 视觉模板

用途：

- 展示评论区设计形态。
- 生产时必须替换成真实 review。

稳定做法：

- 参考最早的 Client Feedback 深色 Banner：左侧大标题，右侧多张评论卡片，带引号视觉符号。
- 如果没有真实评论，标题必须写 `Feedback preview` 或同义说明。
- 备注必须写清：生产时替换为真实 review、来源、日期、rating。

适合拼接方式：

- `pure_composite`。
- 背景可以固定，卡片和文字本地确定性叠加。

### C. 固定品牌 / 品类 Banner

用途：

- 品牌介绍、质量保证、售后信任、品类固定信任模块。
- 不依赖具体产品图，适合多 SKU 复用。

稳定做法：

- 黑金、黑蓝、深色高端感可保留，但不能整页连续使用。
- 左上或左侧放 `EXCITAT` 艺术字。
- 只放可证据化或中性的品牌表达，例如“清晰信息、简短证明、购买前说明”。
- 服务承诺如果没有证据，不能写成物流、退货、保修保证。

适合拼接方式：

- `AI background + deterministic composite` 或纯拼接。
- `shine_sweep` 是当前最稳的 GIF 方案。

### D. 产品结合类 Banner

用途：

- 首屏 Hero、中段产品说明、产品场景 proof。

前提：

- 必须有真实产品图、详情图、Listing 图、场景图或可用产品抠图。
- 如果没有产品素材，只能先输出 Banner 需求，不应强行生成产品结合图。

稳定做法：

- 背景用真实使用场景或 AI 生成场景底图。
- 产品主体使用真实产品图嵌入。
- 品牌 Logo/艺术字放在左上、右下或留白处。
- 不要简单把主图塞进模板；产品、场景、文字位置要形成完整构图。

适合拼接方式：

- 默认 `AI background + deterministic composite`。
- 产品不能变形时，禁用纯 AI 重绘产品。

### E. 产品中段 Proof Banner

用途：

- 用裁切的产品细节证明功能，比如接口、按钮、材质、容量、配件、线缆、屏幕、使用动作。

稳定做法：

- 不是重复首屏大图。
- 裁切要为证据服务。
- 一图只证明一个核心判断。
- 可搭配短标题和 2-3 条说明。

适合拼接方式：

- `pure_composite` 或 `AI background + deterministic composite`。

### F. Step Highlight GIF

用途：

- 使用步骤、安装步骤、操作流程。

稳定做法：

- 固定四格或三格步骤图。
- 步骤编号依次高亮。
- 不让产品本体大幅动，避免变形。
- 适合“加水、放食材、选择模式、清洁”等顺序说明。

适合拼接方式：

- 本地确定性生成 GIF。
- HTML 嵌入单张 GIF。

## 4. 方法模板

### 4.1 BannerPlan 模板

每张 Banner 先写计划，不能直接生成：

```json
{
  "banner_id": "string",
  "route": "pure_composite | pure_ai_generation | ai_background_plus_composite",
  "family": "qa | review | brand | category | product_scene | proof | step",
  "reference_pattern": "string",
  "product_slot": "none | required | optional",
  "brand_tag_slot": "top_left | top_right | bottom_right | left_panel",
  "text_slots": [
    {
      "role": "headline | subhead | chip | note",
      "max_chars": 48,
      "source": "ProductTruthPack | EvidencePack | BrandKit"
    }
  ],
  "motion_effect": "none | shine_sweep | step_highlight",
  "risk_notes": []
}
```

### 4.2 AI 生成底图 Prompt 模板

AI 底图只负责氛围和空间，不负责最终小字：

```text
Create a premium ecommerce banner background for [category].
Canvas: [1200x480 or 1280x366].
Mood: [premium / clean / warm / technical / family-friendly].
Composition: reserve [left/right/top] clean empty space for deterministic text overlay.
Subject: [scene/person/context], no readable text, no logos, no fake marketplace marks.
Product area: leave a natural slot for a real product cutout to be composited later.
Style: high-end retail detail page, balanced negative space, not crowded.
Avoid: tiny text, fake badges, fake platform guarantees, distorted products, overfilled layout.
```

### 4.3 本地拼接模板

需要精准的内容全部本地拼接：

```text
Input:
- background image or solid background
- product cutout / proof image
- EXCITAT brand text or tag
- exact headline/subhead/chips from ProductTruthPack
- icons from IconLibrary

Process:
1. normalize canvas size
2. crop or place product/proof image
3. place brand tag
4. overlay headline and short copy with deterministic font
5. overlay icons/chips only when useful
6. export PNG/JPG or GIF
7. write media_asset_index
```

### 4.4 HTML 嵌入模板

复杂视觉模块默认变成图：

```html
<p style="text-align:center;">
  <img src="assets/example.jpg" alt="EXCITAT detail banner" width="1140" />
</p>
```

简单文本模块保留 HTML：

```html
<h2>...</h2>
<p><strong>...</strong><br />...</p>
```

规格参数可用 HTML/table，但核心参数更适合用图标参数板：

```html
<table width="1140" cellpadding="0" cellspacing="0" style="background-color:#f7f9fb;">
  <tr>
    <td style="padding:28px;">
      ...
    </td>
  </tr>
</table>
```

## 5. 验证与返工闭环

当前稳定路线必须有 BDD 式质量门：

```text
Plan -> Execute -> Validate -> Repair -> Validate -> Final
```

### 必检项

- `brand_policy`: 新输出只能显示 `EXCITAT`。
- `qa_review_separation`: QA 和 Review 不混用。
- `review_truth_policy`: 无真实 review 时必须标记 preview。
- `claim_evidence_policy`: 物流、退货、保修、评分、平台背书必须有证据。
- `asset_rights_policy`: 官方素材无授权不能直接商用。
- `mobile_readability`: 390px 移动端不溢出，文字可读。
- `layout_rhythm`: 不连续堆黑色重模块，不滥用小框，不重复大图。
- `product_integrity`: 产品不变形、不漂移、不多出错误结构。
- `text_rendering`: 重要文字不能交给模型生成；最终文字必须可读。
- `motion_risk`: GIF 不影响可读性，不造成产品变形。

### 返工映射

- 产品漂移：改用真实产品图拼接。
- 文字错乱：禁用模型文字，改本地叠字。
- 页面太乱：减少卡片、badge、边框，换白底短文或裁切 proof 图。
- 移动端不可读：减少文字、扩大字号、改为单列。
- 黑色模块过多：插入白底/浅色视觉缓冲。
- Review 证据不足：降级为 Feedback preview 或改成 QA。
- GIF 风险高：降级静态图，只保留 `shine_sweep` 或无动效。

## 6. 当前已有文件与产物

Agent core 草稿：

- `/Users/cc/Desktop/photo_show/workflow/agent_core/emag_banner_html_agent_v1_1/README.md`
- `/Users/cc/Desktop/photo_show/workflow/agent_core/emag_banner_html_agent_v1_1/DESIGN.md`
- `/Users/cc/Desktop/photo_show/workflow/agent_core/emag_banner_html_agent_v1_1/DESIGN_FD.md`
- `/Users/cc/Desktop/photo_show/workflow/agent_core/emag_banner_html_agent_v1_1/data/banner_patterns.jsonl`
- `/Users/cc/Desktop/photo_show/workflow/agent_core/emag_banner_html_agent_v1_1/data/tag_library.jsonl`
- `/Users/cc/Desktop/photo_show/workflow/agent_core/emag_banner_html_agent_v1_1/data/validation_cases.jsonl`
- `/Users/cc/Desktop/photo_show/workflow/agent_core/emag_banner_html_agent_v1_1/prompt_contracts/openai_image_generation.md`
- `/Users/cc/Desktop/photo_show/workflow/agent_core/emag_banner_html_agent_v1_1/prompt_contracts/fal_flux_kontext.md`
- `/Users/cc/Desktop/photo_show/workflow/agent_core/emag_banner_html_agent_v1_1/prompt_contracts/google_imagen_adapter.md`
- `/Users/cc/Desktop/photo_show/workflow/agent_core/emag_banner_html_agent_v1_1/validators/VALIDATION_RULES.md`

稳定路线脚本：

- `/Users/cc/Desktop/photo_show/scripts/generate_excitat_banner_html_agent_v1.py`
- `/Users/cc/Desktop/photo_show/scripts/validate_excitat_banner_agent_outputs.py`

设计与流程文档：

- `/Users/cc/Desktop/photo_show/workflow/emag_stable_component_contract.v1.md`
- `/Users/cc/Desktop/photo_show/workflow/emag_stable_component_catalog.v1.json`
- `/Users/cc/Desktop/photo_show/workflow/agent_flows/emag_detail_banner_agent_v1.md`

测试输出：

- `/Users/cc/Desktop/photo_show/output/emag_excitat_banner_html_agent_stable_v1/preview_mobile.html`
- `/Users/cc/Desktop/photo_show/output/emag_excitat_banner_html_agent_stable_v1/detail.html`
- `/Users/cc/Desktop/photo_show/output/emag_excitat_banner_html_agent_stable_v1/DESIGN_SPEC.json`
- `/Users/cc/Desktop/photo_show/output/emag_excitat_banner_html_agent_stable_v1/media_asset_index.json`
- `/Users/cc/Desktop/photo_show/output/emag_excitat_banner_html_agent_stable_v1/validation_report.json`
- `/Users/cc/Desktop/photo_show/output/emag_excitat_banner_html_agent_stable_v1/repair_log.md`
- `/Users/cc/Desktop/photo_show/output/emag_excitat_banner_html_agent_stable_v1/run_report.md`
- `/Users/cc/Desktop/photo_show/output/emag_excitat_banner_html_agent_stable_v1/contact_sheet.jpg`

## 7. 当前没有完成的事

- 还没有形成最终 Design MD。
- 还没有把这套 `EXCITAT Banner + HTML Agent` 迁移到 `/Users/cc/projects/agent-platform`。
- 还没有做成熟组件库 UI 或组件检索界面。
- 还没有跑完整的 OpenAI/FAL/Google provider adapter 真实生图对比。
- 还没有形成 10-20 套固定 Manner/Banner 模板。
- 还没有形成完整品类色调系统，例如母婴、科技、家居、清洁、美妆分别的稳定风格。
- GIF 库目前只确认 `shine_sweep` 和 `step_highlight` 稳定；其他效果需要另开对话慢慢调。
- 产品结合类 Banner 必须等真实产品图/详情图准备好，不能靠空想生成最终图。
- 当前输出里有些图只是路线证明，不代表最终审美标准。

## 8. 后续推荐路线

### Phase 1. 稳定组件库

- 把 QA、Review、Brand closer、Spec icon board、Step GIF、Proof banner 收进组件库。
- 每个组件记录：
  - 输入字段
  - 适用品类
  - 禁用场景
  - 输出尺寸
  - HTML 嵌入方式
  - 验证规则
  - 示例图

### Phase 2. 固定 Banner / Manner 图库

- 先做 10-20 套固定 Banner。
- 每套都保留空白区域、品牌位置、产品槽位、文字槽位。
- 分类包含：
  - 品牌信任
  - QA
  - Review preview
  - 品类介绍
  - 产品场景
  - proof 裁切
  - 使用步骤
  - 质量/安全/售后

### Phase 3. AI 底图 + 拼接

- 先生成无字底图。
- 再本地嵌入真实产品、`EXCITAT`、标题、参数、图标。
- 对模型只要求氛围、构图、留白，不要求精准产品和小字。

### Phase 4. 迁移到 agent-platform

- 把当前 `photo_show` 里的 Agent core、数据、validator、脚本迁移成真正的内置 Agent。
- 接入 profile、Skill、reference DB、validator、examples。
- 建立 unit test、fixture test、visual smoke test。

### Phase 5. 视觉验证与返工自动化

- 增加 390px 移动端截图检查。
- 增加文字溢出检查。
- 增加重复大图/连续黑模块检查。
- 增加 review/QA 语义检查。
- 增加 `repair_log`，明确每次返工原因。

## 9. 这份留痕的定位

这份文件不是最终方案，也不是完整组件库。它的作用是：

- 记录当前对话里已经明确的稳定路线。
- 防止后续把实验图误认为最终生产标准。
- 防止把 QA、Review、品牌 Banner、产品 Banner 混成一个模板。
- 给后续 agent-platform 迁移、组件库搭建、AI 生图 provider 测试提供明确起点。
