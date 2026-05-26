# eMAG Stable Component Contract v1

目标不是让 Agent 每次自由发挥，而是把详情页拆成可复用、可验证、可替换的稳定组件。每个组件必须先吃同一套输入，再输出固定形态的 HTML 或图片/GIF 模块，最后用 validator 和移动端预览确认。

稳定组件规范不只是颜色设计，它至少包含六层：

- 输入 schema：组件能吃什么，缺什么要 blocked。
- 设计 token：颜色、字体、字号层级、间距、圆角、留白。
- 组件代码接口：renderer 函数怎么接参数，怎么输出 asset/html/metadata。
- 资产与图标库：图片、GIF、icon_id、授权和尺寸怎么管理。
- HTML 输出边界：允许标签、灰区标签、禁用标签、移动端宽度。
- 验收规则：validator、claim evidence、移动端截图、失败模式。

## 1. 输入契约

### ProductTruthPack

必须包含：

- `product_type`: 产品类型，例如 baby, ev, cleaning, beauty, tool。
- `core_result`: 用户买完之后得到的结果。
- `pain_points`: 用户受够了什么场景。
- `features`: 功能列表。
- `benefits`: 功能对应的实际好处。
- `specs`: 参数和值，必须可追溯。
- `package_contents`: 包装/配件。
- `usage_scenes`: 使用场景。
- `constraints`: 不能夸大的内容。
- `evidence_refs`: 每条强 claim 对应来源。

规则：

- 没证据的内容只能进入 angle，不进入 fact。
- 物流、退货、保修、评分、review、平台背书，没有证据一律不能写成承诺。
- 产品图里如果有旧品牌水印或旧 Logo，标记为 `needs_image_cleanup`，HTML 只能临时预览，不能当最终生产图。

### BrandKit

必须包含：

- `brand_name`: 当前固定为 `EXCITAT`。
- `category_tone`: baby/tech/home/beauty 等品类调性。
- `primary_color`, `accent_color`, `neutral_dark`, `neutral_light`。
- `logo_policy`: 文字 Logo、是否允许图形 Logo、旧品牌替换策略。
- `motion_policy`: 允许的品牌动效。

稳定规则：

- baby 类：暖白、浅绿、柔橙、少量青色/橙色品牌强调；不能做过重科技黑。
- tech/EV 类：黑、深蓝、青绿/电光蓝；参数模块可以更硬朗。
- 品牌模块可以黑金或黑色高级感，但底部 CTA 不能做成粗糙大黑框。

字体规则：

- 品牌字统一输出英文大写 `EXCITAT`，不能再输出 `EXIT`、`Excité`、`Exceity` 或旧的带重音拼写。
- 图片模块内部使用确定性字体，不依赖模型写字。
- 字号比例必须分层：品牌字最大，主标题次之，说明文字明显小一档；不能出现标题和副标题都很大的失衡布局。
- 标题字重可以强，但参数说明和正文保持清爽，不使用错误 italic face。

### AssetInventory

必须包含：

- `product_images`: 主图、细节图、场景图。
- `scene_images`: 真实使用场景优先。
- `existing_gifs`: 已有 GIF。
- `generated_assets`: AI 生成或本地合成图。
- `asset_rights`: own/captured/reference/unknown。
- `dimensions`: 宽高。
- `cleanup_flags`: old_brand, watermark, low_resolution, text_baked。

规则：

- eMAG 官方素材只能作为 reference，未确认授权前不能直接商业使用。
- AI 生图禁止直接生成文字，文字必须由本地确定性叠加。
- 产品主体如果需要精准，优先用真实产品图或抠图；模型只负责背景、场景、气氛。

### IconLibrary

核心参数图标必须来自图标库，不在每个产品里临时重画。

字段：

- `library_id`
- `icon_id`
- `style`
- `source_path`
- `allowed_components`
- `color_tint_rule`

规则：

- 参数组件只引用 `icon_id`，例如 `bolt`, `cup`, `steam`, `shield`, `ruler`, `plug`。
- 换图标风格时升级整个 icon library 版本，不逐个改组件。
- 图标必须在 390px 移动端仍可识别。

### EvidencePack

必须包含：

- `source_specs`: 原始参数来源。
- `source_package`: 包装/配件来源。
- `source_qa`: 真实 Q&A 或类目问题。
- `source_reviews`: 真实 review，若无则只能生成 review preview 或转成 QA。
- `seller_service_facts`: 卖家/平台服务事实。

规则：

- QA 是 QA，review 是 review，不能混用。
- Review preview 可以用于设计预览，但必须带 production note。
- 任何星级、姓名、日期都必须来自真实 review，否则 fail。

## 2. 处理规则

### Step A. 分类与 SOP 链路

先按产品类型选择 SOP：

- EV/tech: `manner_scenario_banner -> first_screen_anchor_triplet -> mixed_image_text -> visual_buffer -> step_gif -> spec_icon_board -> package -> qa -> review_or_qa -> brand_closer`
- baby: `warm_scene_banner -> safety_anchor_triplet -> mixed_usage_blocks -> green_visual_buffer -> step_gif -> spec_icon_board -> package -> qa -> review_preview -> brand_closer`
- cleaning/home: `pain_scene_banner -> result_anchor_triplet -> feature_benefit_mix -> before_after_or_usage -> spec_icon_board -> package -> qa -> trust_closer`
- brand/store trust: `brand_trust_banner -> service_fact_band -> product_range_familiarity -> buyer_objection_qa -> brand_closer`

### Step B. 组件选择

组件只能从稳定 catalog 里选。每个组件要写清：

- `buyer_question`: 回答哪个买家问题。
- `required_inputs`: 需要什么输入。
- `output_type`: html/image/gif。
- `invariants`: 稳定不变的结构。
- `allowed_variations`: 可变的颜色、文案、图片槽位。
- `failure_modes`: 常见失败方式。

### Step B2. 组件代码接口

每个稳定组件必须有明确 renderer 形态：

```ts
type StableComponentInput = {
  component_id: string;
  product_truth_pack: ProductTruthPack;
  brand_kit: BrandKit;
  asset_inventory: AssetInventory;
  evidence_pack: EvidencePack;
  props: Record<string, unknown>;
};

type StableComponentOutput = {
  html_snippet: string;
  asset_paths: string[];
  media_asset_records: MediaAssetRecord[];
  validation_notes: string[];
};
```

代码规范：

- renderer 边界先做 props normalization，例如颜色统一转 RGBA tuple，长文本先测宽换行。
- 组件不能直接读取全局随机素材，必须从 `AssetInventory` 或 `IconLibrary` 取。
- 文案不能直接写死事实，必须回指 `ProductTruthPack` 或 `EvidencePack`。
- 复杂图文组件先生成图片/GIF，再用稳定 HTML 嵌入。
- 每个组件必须生成 `media_asset_index` 记录，包括尺寸、风险、证据来源和生产注意事项。

### Step C. 图片与 GIF 生成边界

稳定策略：

- Banner、QA board、review board、brand closer 优先做成图片/GIF，再用 `<img width="1140">` 嵌入。
- 复杂图文排版不要交给 HTML 自由排版，避免移动端崩。
- 字体、边框、卡片、icon、文字全部本地确定性叠加。
- 当前稳定 GIF 只使用 `shine_sweep` 和 `step_highlight`。
- Banner 默认采用 `AI 生成底图 + 本地确定性嵌入`，而不是把完整文字和产品都交给模型自由生成。
- `纯拼接` 用于参数、QA、review、步骤、手册等需要准确文字的模块。
- `纯 AI 生成` 只用于探索方向或用户明确要求测试模型文字能力的场景，不能直接当稳定生产路线。
- `AI + 拼接` 用于首屏 hero、产品场景 banner、品牌氛围 banner。

关于人/产品动效：

- eMAG HTML 里不是用 JS 让人动，而是把“人物微动/产品微动”预先做成 GIF/WebP，再用 `<img>` 嵌入。
- v1 稳定路线只接受现成 GIF 或本地生成的简单帧动画。
- 人物微动的生产路径是：静态人物图 -> 动作帧/视频 -> 压缩 GIF/WebP -> eMAG 详情 HTML 嵌入。
- 产品图也可以动，但前提是产品主体不能变形；更适合做高光扫过、局部亮点、步骤高亮，而不是大幅旋转。

暂不稳定：

- 产品边缘发光、复杂呼吸边框、人物微动、产品旋转、粒子背景，先标为 experimental。
- 产品图片动起来需要单独 motion pipeline：抠图/分层 -> 轻微位移或光效 -> 压缩 GIF/WebP -> 移动端检查。

### Step C2. 高级感布局与去冗余规则

页面高级感来自节奏，不是来自不断加框。

规则：

- 小框不是默认样式，只能用于首屏三锚点、参数、步骤、对比、手册说明。
- 如果上一模块已经是产品场景大图，下一模块不能再放一个相似的大图；应改成短文本、裁切细节图、参数板或 QA。
- 每段连续页面最多一个黑金/深色重模块，后面必须接白底、浅色或简洁文本模块。
- 图片要裁切为证据：接口、按钮、材质、容量、包装、配件、使用动作，而不是把所有原图重复堆上去。
- 图文比例根据问题决定：图片已经说明清楚时，文字只做标题/短句；图片证据不足时，才加解释文字。
- 对齐方式要变化：左对齐说明、居中短句、右侧产品裁图、全宽 proof 图，不允许整页重复同一种两栏盒子。
- 不要为了装饰添加多余产品图、重复品牌图、重复服务图。

### Step C3. Banner 路线选择

三条路线：

- `pure_composite`: 使用真实产品图、固定背景、确定性文字和图标。适合 QA、review、spec、manual、package。
- `pure_ai_generation`: 用于探索 moodboard。适合快速看方向，不直接进生产。
- `ai_background_plus_composite`: 先生成无文字、无产品或弱产品底图，再嵌入真实产品、Logo、文字、icon、GIF 光效。作为默认生产路线。

选择条件：

- 产品外观不能漂移：选 `pure_composite` 或 `ai_background_plus_composite`。
- 需要高级氛围：选 `ai_background_plus_composite`。
- 需要精准参数/评论/服务：选 `pure_composite`。
- 只是测试模型审美或新 prompt：选 `pure_ai_generation`。

每个 Banner 输出必须记录：

- `route_selected`
- `reference_pattern`
- `product_slot`
- `text_slot`
- `motion_effect`
- `validator_status`
- `repair_instruction`

### Step D. HTML 输出边界

允许：

- `p`, `h2`, `h3`, `strong`, `br`, `ul`, `li`, `img`。
- 灰区可用：`table`, `tr`, `td`, `div`, `blockquote`, inline style, GIF。

禁止：

- `script`, `iframe`, `form`, 外部 CSS, 复杂交互 JS。
- 伪造 eMAG 背书、伪造 review、无证据服务承诺。

移动端规则：

- 源图可用 1140 宽，但必须在 390px 预览下可读。
- HTML 文字模块单段不超过 3 行。
- 长参数用图标 board 先解释，再保留 source table 作为证据层。
- 一屏内不要连续出现超过 2 个大黑模块。

## 3. 输出契约

每次生成必须输出：

- `detail.html`: eMAG 可嵌入 HTML。
- `preview_mobile.html`: 本地移动端预览。
- `DESIGN_SPEC.json`: 产品级设计 SPEC。
- `validation_report.json`: HTML/claim/module/asset 检查。
- `media_asset_index.json`: 资产来源、尺寸、用途、风险。

每个组件输出必须包含：

- `component_id`
- `component_version`
- `buyer_question`
- `input_refs`
- `asset_path`
- `html_snippet`
- `dimensions`
- `evidence_refs`
- `risk_level`
- `mobile_preview_status`
- `production_notes`

## 4. 稳定组件验收

一个组件进入 stable 前必须满足：

- 至少 2 个不同品类产品跑通。
- 390px 移动端截图无明显文字溢出、重叠、低对比。
- HTML validator pass，只有已知灰区 warning。
- claim evidence 检查 pass。
- 组件的失败模式已经写进 catalog。

## 5. 当前稳定优先级

P0 稳定组件：

- `first_screen_anchor_triplet`
- `spec_icon_board`
- `manner_brand_closer`
- `shine_sweep_gif`
- `step_highlight_gif`
- `mixed_image_text_block`
- `qa_buyer_question_board`
- `excitat_trust_banner`

P1 候选组件：

- `manner_review_preview_board`
- `testimonial_feedback_board`
- `warm_visual_buffer`
- `manner_scenario_banner`

P2 实验组件：

- product edge glow
- border breathing
- particle background
- people micro-motion
- product motion GIF
