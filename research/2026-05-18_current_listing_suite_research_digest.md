# 电商 Listing 套图预制系统调研资料总档

日期：2026-05-18  
范围：整理当前对话和本地文件中已经收集到的资料、视频线索、社区/开源项目、博客/商业产品参考、以及前面实验得到的可用结论。  
边界：这是资料归档和方法总结，不是最终方案。YouTube 部分目前主要来自搜索页、标题、描述、章节和第一轮筛选；后续仍需逐条观看并截图拆解。

## 0. 当前核心判断

这轮调研真正支持的方向不是“图片加文字”的简单合成，也不是把旧的 `Image2 + 关键词 + HTML/PIL 叠字` 当主路线。更稳的路线是：

```text
产品图/产品信息
  -> ProductTruthPack
  -> BrandStylePack / DESIGN.md
  -> MarketplaceProfile
  -> SlotPlan / SuiteTemplate
  -> TemplateCard / PSD/Fabric template
  -> 产品保真生成或 preserve-first composite
  -> 字体/徽章/参数/品牌框确定性渲染
  -> VLM QA
  -> typed repair / reroll
  -> Review UI / Export
```

目前最有价值的三条经验线：

1. **Amazon 线：** 用来建立完整套图顺序和 slot taxonomy，重点是每张图回答一个买家问题。
2. **Ozon/WB 线：** 用来建立模板适配路线，重点是竞品分析、去背景、3:4 卡片、短文字、大产品、强徽章。
3. **Brand Shoot Kit / QA-reroll 线：** 用来建立生产闭环，重点是产品保真、shot plan、QA、reroll、review frontend。

## 1. P0 资料：应直接影响方案的来源

| 来源 | 类型 | 链接 | 核心可借鉴点 | 对我们的含义 |
|---|---|---|---|---|
| GreenOnion Amazon bulk listing images | 商业产品 | https://greenonion.ai/use-cases/amazon-bulk-listing-images | 一张产品图生成 9 张 Amazon 图；先分析产品、分配 features、生成 design specs，再编辑 copy 和批量生成 | 说明“套图系统”的核心不是 prompt，而是 feature-to-slot 分配和批量控制 |
| Ribbi Amazon Product Image Set | 商业产品 | https://ribbi.ai/zh/skills/create-amazon-product-image-set | 先确认主图/风格海报，再生成 6 张副图和 A+ 模块 | 需要 style anchor / 风格确认点，不能直接一次性盲跑全套 |
| OpenCreator Amazon Product Photo Set | 商业产品 | https://opencreator.io/zh/template-amazon-product-photo-set | GPT-4o 分析产品，Nano Banana Pro 生成 6 张 Amazon 标准图 | 支持 VLM 分析产品 -> slot prompt fanout -> batch render 的流程 |
| Brand Shoot Kit | 开源端到端工作流 | https://github.com/TheMattBerman/brand-shoot-kit | `Scout -> Preserve -> Shot Plan -> Generate -> QA -> Reroll -> Export -> Review Frontend` | 这是当前最接近“生产闭环”的开源参考，应该借它的 artifact 和 QA/reroll 机制 |
| tryclair Amazon listing images plugin | 开源 Skill | https://github.com/tryclair/amazon-listing-images-plugin | `DESIGN.md` 品牌系统 + 23 类 Amazon slot 类型 | 可作为 slot catalog 和品牌文件结构参考，但需要补 QA 和批量一致性 |
| Nexscope Amazon Listing Images | Skill/流程参考 | https://www.nexscope.ai/fr/skillhub/skill/amazon-listing-images | 7 图策略、主图优化、信息图、生活方式、尺寸参考、移动端可读、A/B testing | Scale A 的核心参考 |
| Nexscope GPT Image 2 Amazon workflow | 博客/流程参考 | https://www.nexscope.ai/blog/ai-product-photography-amazon-gpt-images-2-guide | 产品参考、图片任务、事实锁定、生成方向、review、最后进入可编辑工具 | 支持“先规划再生成，最后可编辑化”的路线 |
| MiddleKD/ComfyUI-productfix | 开源保真技术 | https://github.com/MiddleKD/ComfyUI-productfix | Latent Injection、OCR mask、detail transfer、IC-Light、IP-Adapter、ControlNet depth | 产品保真不能只靠负面词，需要 mask/detail transfer 或 preserve-first 路线 |
| Fabric.js | 前端模板引擎 | https://fabricjs.com/ | Canvas 对象模型、文本编辑、SVG、filters、grouping、serialization | 适合做确定性文字、徽章、图标、模板 JSON |
| vue-fabric-editor / Kuaitu | 开源编辑器 | https://github.com/ikuaitu/vue-fabric-editor | 中文社区验证较多，支持模板、自定义字体、素材、导出 | Electron 精修模式可以参考，不要从零写画布 |
| yft-design | 开源编辑器 | https://github.com/dromara/yft-design | PSD/PDF/SVG import，Fabric + Vue3，模板和导出 | 对 PSD 模板导入和模板适配很关键 |
| gzm-design | 开源编辑器 | https://github.com/LvHuaiSheng/gzm-design | PSD 解析、分组/图层、文本解析、字体加载、多页、模板导入 | 很适合研究“PSD 模板 -> 可填充模板”的前端路线 |
| fabritor-web | 开源编辑器 | https://github.com/sleepy-zone/fabritor-web | React/Fabric，文本效果、图层、模板 JSON、导出 | 如果 HermPlan4/Electron 前端是 React，可作为轻量参考 |
| Bitypixel | Ozon/WB 模板产品 | https://bitiypixel.ru/ | 上传产品图、去背景、套 12 个 3:4 模板、改文字/图标/徽章 | Scale B 的典型模板适配路线 |
| Sozdai examples | Ozon/WB 案例库 | https://sozdai.app/blog/infografika-primery | 一个 slide 一个卖点；4-6 张卡片；按品类拆 slot | 很适合做 Ozon/WB 的 TemplateCard 样本池 |

## 2. P1 资料：适合补样本和扩展模块

| 来源 | 类型 | 链接 | 主要价值 |
|---|---|---|---|
| Seller Studio examples | 商业案例 | https://sellerstudio.us/examples.html | 一张产品图到 8 张图的公开示例，包含 Main Image、Lifestyle、Dimension Callout、Three-Strip Infographic、Callout Diagram |
| Jungle Scout Amazon infographic guide | 博客指南 | https://www.junglescout.com/resources/articles/amazon-product-infographic/ | 解释 Amazon 信息图为什么要承担卖点、场景、品牌一致性、字体一致性 |
| Behance Amazon A+ / Listing portfolio | 设计案例 | https://www.behance.net/gallery/153196069/Amazon-A-Content-Listing-Lifestyle-Infographics | 可拆 Main、Dimensional、Infographics、Features、Lifestyle、A+ 的完整顺序 |
| Behance Amazon infographic search | 案例搜索 | https://www.behance.net/search/projects/amazon%20infographics?locale=en_US | 持续扩充美妆、宠物、工具、健身、水杯、家居等品类案例 |
| Parials Amazon listing image design | 服务商案例 | https://www.parials.com/amazon-listing-image-design/ | 看服务商如何组织 9 图、信息图、对比表、利益图 |
| Delightful Design Studio listing images | 服务商案例 | https://www.delightfuldesignstudio.com/listing-images | 偏品牌化和高审美的 Amazon 副图参考 |
| Ischenko Design | Ozon/WB 服务商 | https://ischenkodesign.ru/ | 俄语平台首图、竞品分析、CTR、搜索卡片视觉 |
| Behance Ozon/WB card project | 设计案例 | https://www.behance.net/gallery/229053767/kartochki-tovarov-s-infografikoj-Ozon-i-Wildberries | 同一市场下不同品类的品牌一致性和图标/色块系统 |
| Ozon image requirements | 官方规则 | https://docs.ozon.com/global/products/requirements/media/image-requirements/ | Ozon 3:4、主图、产品匹配、无水印、允许信息图等规则 |
| PixSora | 商业产品 | https://pixsora.ru/ | 上传最多 6 张产品图，AI 分析产品/品类/利益点，生成最多 6 张 slides |
| SellerArt | 商业产品 | https://sellerart.ru/ | 强调统一品牌风格、30-60 秒生成、Ozon/WB/Yandex 卡片 |
| SellerDen AI | 商业产品 | https://sellerden.ai/generator-opisania/generator-kartochek-marketplejsov/generator-kartochek-ozon/ | 图片生成、背景生成、图审、A/B、SEO、评论回复、Ozon 助手等套件化趋势 |
| Sellovio | 商业产品 | https://sellovio.com/ | marketplace + style 选择，自动 resize/export |
| Oimok | 商业产品 | https://www.oimok.com/en | Ozon/WB/Yandex 风格的卡片/信息图工具参考 |

## 3. 开源和社区技术资料

### 3.1 生成、保真和 PSD/模板

| 项目 | 链接 | 可借鉴点 | 限制 |
|---|---|---|---|
| bggg-creator-image2psd | https://github.com/binggandata/bggg-skills/tree/main/bggg-creator-image2psd | manifest -> layered PSD、preview PNG、全画布图层 PNG | 当前更偏 raster layer，文字未必是真 Photoshop 可编辑文字 |
| nano-banana-2-skill | https://github.com/kingbootoshi/nano-banana-2-skill | Agent 可执行的参考图生图、尺寸、透明图能力 | 不是电商专用，需要套我们的 QA 和 ProductTruthPack |
| MeiGen-AI-Design-MCP | https://github.com/jau123/MeiGen-AI-Design-MCP | 多模型桥接、prompt gallery、GPT Image 2/Nano Banana 支持 | 依赖外部 API/credit，不是模板引擎 |
| nanobanana-trending-prompts | https://github.com/jau123/nanobanana-trending-prompts | prompt 结构和风格词汇挖掘 | 病毒式 prompt 不等于 SKU 安全 |
| awesome-gpt-image | https://github.com/ZeroLu/awesome-gpt-image | GPT image prompt 案例库 | 需要过滤 novelty 和不保真的写法 |
| ag-psd | https://github.com/Agamnentzar/ag-psd | JS 读写 PSD，可用于浏览器侧 PSD export | PSD 特性覆盖有限 |
| psd-tools | https://github.com/psd-tools/psd-tools | Python 侧 PSD 检查/导出 | 编辑 type layer/smart object 有限制 |
| Open Design | https://github.com/nexu-io/open-design | 设计系统、artifact、preview、自评、文件化约束 | 是通用设计工具，不是电商专用 |
| DesignMD | https://designmd.app/en/what-is-design-md | 用 Markdown 固化设计 token 和禁忌 | 需要写我们自己的电商视觉规则 |
| awesome-design-md | https://github.com/VoltAgent/awesome-design-md | DESIGN.md 生态参考 | 主要面向 UI，需要改造成商品图规则 |
| Bria-AI/ComfyUI-BRIA-API | https://github.com/Bria-AI/ComfyUI-BRIA-API | background removal/replacement、ShotByText、ShotByImage | API 依赖强，不是 listing suite 产品 |

### 3.2 社区反复出现的经验

| 来源 | 链接 | 反复出现的经验 |
|---|---|---|
| Reddit: tried AI for product photos | https://www.reddit.com/r/ecommerce/comments/1jox56d/tried_ai_for_product_photosheres_what_worked_and/ | 真产品图做锚点，AI 做变体和更新 |
| Reddit: product image consistency | https://www.reddit.com/r/EcommerceWebsite/comments/1s36vkn/we_tried_solving_product_image_consistency_for/ | 目录一致性是 workflow 问题，不只是模型质量问题 |
| Reddit: one product photo into variations | https://www.reddit.com/r/ecommerce/comments/1rru8mv/how_are_people_making_product_photos_look_so/ | 真产品图 + AI 背景 + 统一 crop/shadow 是低成本有效路径 |
| Reddit: AI product photos setup | https://www.reddit.com/r/ecommerce/comments/1qtmu82/whats_your_setup_for_product_images/ | 颜色、比例准确性仍然是卖家最在意的点之一 |
| Reddit: AI product photography conversion workflow | https://www.reddit.com/r/ecommercemarketing/comments/1qvkxng/how_to_create_ai_product_photography_that/ | 先决定每张图的 job，再选场景 |
| Reddit: product detail preservation | https://www.reddit.com/r/comfyui/comments/1mcsxoc/testing_the_limits_of_ai_product_photography/ | 复杂产品仍然容易崩，必须做细节保真 |
| Reddit: GPT Image 2 on fal | https://www.reddit.com/r/fal/comments/1srxfj4/gpt_image_2_is_live_on_fal/ | 社区期待 GPT Image 2 改善 logo/label/packaging fidelity |
| Reddit: prompt dataset | https://www.reddit.com/r/comfyui/comments/1sypezt/open_source_1446_trending_ai_image_prompts_for/ | prompt mining 和 prompt recommendation 正在变成可复用资产 |

## 4. YouTube 资料与可用信息

YouTube 的作用不是技术权威，而是看真实卖家/设计师怎么操作、怎么命名、怎么组织模板和 UI 节奏。

| 视频 | 链接 | 可抽取信息 |
|---|---|---|
| 20 Types of Amazon Images That Convert MORE SALES | https://www.youtube.com/watch?v=ioUgFhvgA_U | slot taxonomy 很有价值：multi-use、scannable infographic、show packaging、show everything、optimize for mobile、detail zoom、us-vs-them、address sticking points、size reference、before/after、instructional 等 |
| Amazon AI Studio: Create Product Photos & Videos in Minutes | https://www.youtube.com/watch?v=KDI73nLbYk4 | Amazon 自己也在把卖家创意做成 agentic creative surface；我们的差异应是控制、模板、QA、跨平台 |
| AI got wild... redesigned Coca-Cola Amazon Listing | https://www.youtube.com/watch?v=4Kf2yfTcLNA | 有助于理解“快速可见结果”的 UI 预期，但不能作为生产系统参考 |
| Nano Banana Pro for Product Photography | https://www.youtube.com/watch?v=12pQ0W2bCDE | 说明当前创作者已把产品摄影当成 step-by-step AI workflow |
| How To Create Product Photos For Amazon Listings | https://www.youtube.com/watch?v=u6qWNAnYyis | 传统产品摄影仍定义了 AI 应模仿的东西：白底、光线、尺度、后期清理 |
| Product Card Design on Wildberries with AI | https://www.youtube.com/watch?v=AlnHcJvrWJg | 重点是复制竞品设计、套 Supa 模板、去背景、改文字和布局；非常支持 Ozon/WB 模板适配路线 |
| Ozon Product Card Through Neural Network: Full Guide | https://www.youtube.com/watch?v=67t9QlI8pkg | 需要后续完整观看，作为 Ozon 专项流程参考 |
| Product Card in 3 Minutes in ChatGPT | https://www.youtube.com/watch?v=19SQhBg9Xz4 | 说明卖家期待快速首版卡片，然后再修 |
| Nano Banana Pro for Ozon and Wildberries 2026 | https://www.youtube.com/watch?v=euQGgJyhGDk | 俄罗斯卖家也在采用 Nano Banana 类模型，模型可替换，流程更重要 |
| Infographic Styles for Wildberries and Ozon | https://www.youtube.com/watch?v=B6JH7250Uzc | 用于提取 Ozon/WB 模板家族和信息密度规则 |
| One Image - 6 Consistent Shots: Nano Banana + Gemini VLM in ComfyUI | https://www.youtube.com/watch?v=587IOqfqMMw | 直接支持“一张产品图 -> VLM 分析 -> 6 个 slot prompt -> 批量一致性生成”的 fanout 路线 |
| ComfyUI Product Photography V1 | https://www.youtube.com/watch?v=o3F3gCXIv4U | ComfyUI 产品摄影工作流参考 |
| ComfyUI Product Photography V2 | https://www.youtube.com/watch?v=rDGonsH1C8Q | 产品放置、重光、保真细节参考 |
| Relight and Preserve Any Detail with Stable Diffusion | https://www.youtube.com/watch?v=3N0vvmAoKJA | 保真和重光应独立于文字/模板渲染 |
| Easy Guide to Amazon Product Images - Pre-Built Templates | https://www.youtube.com/watch?v=Byp-3Yduc6I | 支持“预制模板包”而不是空白画布 |
| How to Design Amazon Listing Images with Canva | https://www.youtube.com/watch?v=K4CMdBiARfk | 精修体验更接近 Canva slot editing，而不是 Photoshop 级自由编辑 |
| Bulk Edit Product Photos With Canva | https://www.youtube.com/watch?v=PV49jL6rYHg | 后续 batch mode 应支持批量替换产品图、copy、徽章 |
| Amazon Listing Infographic Design + Canva Template | https://www.youtube.com/watch?v=zLYUWWdvmLo | 可拆 headline、product cutout、benefit callouts、icon rows、detail zoom、trust footer |

下一轮需要完整看的 YouTube 优先级：

1. https://www.youtube.com/watch?v=ioUgFhvgA_U
2. https://www.youtube.com/watch?v=AlnHcJvrWJg
3. https://www.youtube.com/watch?v=587IOqfqMMw
4. https://www.youtube.com/watch?v=KDI73nLbYk4
5. https://www.youtube.com/watch?v=Byp-3Yduc6I
6. https://www.youtube.com/watch?v=67t9QlI8pkg

## 5. 本地截图/案例资料

本地样本路径：

```text
references/user_cases/20260504_lark_examples/
```

这些不是干净模板图，不能直接喂给生图模型。它们适合反推版式逻辑、prompt 结构、平台规则、产品占比、文字层级、徽章/icon 使用、评分/迭代方式。

| 文件 | 有用信息 | 可沉淀模板 |
|---|---|---|
| `01.jpg` | 宠物/清洁动作场景，产品在真实问题里出现 | `image2_pet_cleaning_action_v1` |
| `02.jpg` | 可调支架对比/参数图，结构化卖点 | `adjustment_comparison_blueprint_v1` |
| `03.jpg` | GPT Image 2 prompt 指导：结构、可见描述 | prompt recipe |
| `04.jpg` | TLDR prompt 指导：具体、分清 keep/change、指定文字 | prompt recipe |
| `05.jpg` | Amazon/Walmart 紫色 PSD 模板，2x2 功能块 | `amazon_purple_feature_grid_v1` |
| `06.jpg` / `07.jpg` | 俄语 marketplace 图片规则 | Ozon/WB profile |
| `08.jpg` | 反推参考图逻辑、生活感、卖点可视化 | template reverse |
| `09.jpg` | Amazon 多场景布局分享 | `amazon_multi_scenario_board_v1` |
| `10.jpg` | 工业产品详情套图 | `industrial_dark_modular_detail_v1` |
| `11.jpg` / `12.jpg` / `13.jpg` | Ozon 主图案例和规则 | `ozon_high_conversion_main_v1` |

本地截图反推出的稳定视觉原则：

- 产品必须先被看见，marketplace 主图里产品视觉权重通常要很高。
- 数字和徽章优于长文案，例如功率、容量、数量、角度、时间。
- 信息要模块化：大产品、2-3 个卖点、1 个场景/细节 inset、底部参数/包装条。
- prompt 必须分清 `keep`、`change`、`layout`、`text policy`、`negative constraints`。
- 最终文字需要模板/PSD/Fabric/HTML 控制，不能依赖模型长期稳定写字。

## 6. Slot taxonomy：需要比“主图/副图/生活方式图”更细

当前应进入 `SlotPlan` 的 slot 类型：

- 白底主图 / search-stop hero
- 核心卖点信息图
- mobile-readable benefit card
- 尺寸/比例参考
- 包装展示 / show packaging
- 包含物展示 / show everything
- 细节放大 / detail zoom
- 使用步骤 / instructional / how-to-use
- 场景生活方式图
- 对比图 / us-vs-them
- 疑虑解决 / address sticking points
- before/after
- 多场景使用图 / multi-use grid
- 质量/材料/认证/来源图
- 适配性/兼容性图
- 评论/信任/保证图
- A+ 模块 / brand story / detail page modules

对应系统字段不能只写 `slot_type=infographic`，至少要有：

```json
{
  "slot_type": "size_reference",
  "buyer_question": "Will it fit my daily carry and laptop?",
  "image_job": "resolve size uncertainty on mobile",
  "template_card": "SizeReferenceCard",
  "copy_density": "short",
  "qa_focus": ["mobile_readability", "claim_safety", "product_fidelity"]
}
```

## 7. 四个核心问题的当前答案

### 7.1 产品一致性与品牌化

资料中重复出现的成熟做法：

- 用真实产品图或 cutout 作为锚点。
- 生图前先做 `ProductTruthPack` / preservation brief。
- 产品复杂时使用 mask、detail transfer、OCR text mask、latent injection、composite。
- 套图开始前确认 style anchor。
- 品牌规则写成 `DESIGN.md` / `BrandStylePack`，不依赖每张图自由发挥。
- 对全套图做 suite-level QA，而不是单张好看就过。

我们已有实验也支持这点：

- `flux_direct` 场景强，但产品容易漂移。
- `composite` 产品外形保留更稳。
- `composite x4` 比同 prompt 直接生成 4 张更能保持多场景一致性。
- 产品图里有接口、logo、文字、配件时，应优先 preserve-first 或 template/composite。

### 7.2 文字嵌入与处理

目前结论不是“永远不能让模型写字”，而是分阶段：

- 概念探索：可以让模型直接生成文字，用来发现好版式和视觉方向。
- 生产交付：最终标题、参数、徽章、表格、尺寸线、俄语/罗马尼亚语/多语种文案，应走确定性渲染。
- 不推荐路线：先生成英文图，再用白块盖住旧英文替换成其他语言，这种补丁感很强。
- 更稳路线：生成 clean/no-final-text base，保留干净文字区，再用 Fabric/HTML/PSD/Pillow/SVG 做完整 overlay/template。

需要注意：简单 PIL 叠字视觉上会很粗糙，它只能证明“文字可控”，不能证明“设计好”。真正要做的是字体层级、留白、安全区、文字自适应、图标/徽章/品牌框一体化。

### 7.3 构图与美观度

成熟方案都不靠泛 prompt：

- Amazon 适合先定义完整套图顺序。
- Ozon/WB 适合先拿优秀竞品/模板，反推 layout，再替换产品和文案。
- PSD/Fabric 模板适合强控制交付。
- Behance、Seller Studio、Sozdai、Bitypixel、本地 `05/10/11-13.jpg` 都适合作为 TemplateCard 来源。

结论：构图要靠 `TemplateCard` 和 `SuiteTemplate`，不是靠每张图临时写“make it beautiful”。

### 7.4 大模型审批与优化

QA 应该是 gate，而不是点评。

`QAReport` 至少包括：

- product_fidelity
- brand_consistency
- marketplace_compliance
- slot_fit / buyer_question_fit
- text_correctness
- mobile_readability
- composition_quality
- commercial_clarity
- claim_safety
- artifact_risk

修复动作要 typed：

- `regenerate_scene_keep_product`
- `replace_text_overlay`
- `adjust_crop_or_white_background`
- `switch_template_card`
- `rerender_brand_frame`
- `use_preserve_first_composite`
- `manual_review_required`

## 8. 三套 Scale 基线

### Scale A：Nexscope / Amazon 7 图策略

目标：验证一张产品图 + ProductTruthPack 能否进入 7/8/9 图 Amazon 套图。

核心 slot：

- 主图白底/点击图
- 核心卖点信息图
- 尺寸参考
- 包装/包含物
- 细节放大
- 生活方式
- 对比/疑虑解决
- A+ 延展

验收重点：套图顺序和买家问题是否成立，不是单图炫技。

### Scale B：Ozon/WB 模板适配路线

目标：验证 3:4 高转化卡片能否通过模板适配批量生产。

核心规则：

- 竞品分析优先。
- 产品要大。
- 短标题、短卖点、强徽章。
- 允许更高信息密度。
- 使用 PSD/Fabric/模板，不靠纯 AI 自由生成长文字。

验收重点：模板化批量是否比纯 prompt 生图稳定。

### Scale C：Brand Shoot Kit / QA-reroll 路线

目标：比较旧 keyword route、template reverse route、preserve-first/composite route 的可靠性。

核心规则：

- 先 scout/preserve。
- 再 shot plan。
- 生成后 QA。
- 失败后 typed reroll。
- 输出 review frontend / manifest / export。

验收重点：不合格图必须说明具体漂移点和修复动作。

## 9. 前端形态结论

更适合当前产品的不是 Lovart 式空白画布，而是“套图生产工作台”：

1. 产品输入：白底图、侧面图、细节图、标题、bullet、参数。
2. 产品真值确认：颜色、材质、尺寸、配件、不能改的 logo/接口/文字。
3. 品牌风格：logo、品牌色、字体、边框、徽章、风格 anchor。
4. 套图计划：Amazon 6/7/9 图或 Ozon/WB 3:4 卡片组。
5. 模板选择：每个 slot 选择 TemplateCard 或 PSD/Fabric template。
6. 生成：背景/场景/产品保真生成。
7. 确定性落版：文字、徽章、参数、品牌框。
8. QA 和 repair：每张图评分、失败原因、typed action。
9. 导出：PNG/JPG/PSD/manifest/QA report/contact sheet。

精修模式可以参考 Canva/Fabric/yft/gzm，但应作为 review/repair surface，而不是 V1 的主要入口。

## 10. 已有本地实验和需要保留的结论

| 文件/实验 | 价值 | 现在如何看 |
|---|---|---|
| `phase0_results/full_set_evaluation.md` | ST08 8 图实验，证明 direct generation 漂移、composite 保真 | 作为产品一致性反例和 composite 证据，不作为最终视觉标准 |
| `phase0_results/cross_category_evaluation.md` | ST08 vs 背包跨品类测试，证明 bbox 和 composite x4 有效 | 技术路径可参考，但视觉标准还不够 |
| `experiments/20260505_text_ab_test/review/ab_text_test_report.md` | direct text vs overlay A/B | 文字策略结论有效：概念可 direct，生产要确定性文本 |
| `experiments/20260505_text_ab_test/romanian/review/romanian_text_replacement_report.md` | 多语言替换测试 | 明确不要“盖旧英文替换”；要 clean base + full overlay |
| `experiments/20260504_img2img_validation/final_validation_report.md` | 12 张模板/PromptRecipe 验证 | 可作为 TemplateCard 探索记录，但评分不能代表最终生产质量 |
| `experiments/20260517_scale_template_validation/` | 三 Scale 结构原型 | 只证明 artifact chain，不证明视觉质量；不应作为视觉 demo |

## 11. 当前资料缺口

1. 小红书抓取不稳定，目前只确定关键词和截图归档方法，缺少系统化笔记样本。
2. YouTube 需要二轮完整观看，提取截图、具体步骤、工具名、模板分类。
3. Ozon/WB 完整开源生成项目很少，目前主要是商业产品和视频/案例线索。
4. 当前本地模板还缺真正高质量 PSD/Fabric 模板。
5. 需要用户提供品牌标准、品牌案例、模板图后，才能建立真正的 `BrandStylePack` 和第一批 production-grade TemplateCard。

## 12. 下一步资料整理任务

建议先不继续泛搜，做三件更有效的事：

1. **建立 12 个样本拆解记录。**  
   从本地 `05/10/11-13.jpg`、Seller Studio、Sozdai、Bitypixel、Behance Amazon/Ozon 中挑 12 个，按统一表拆成 TemplateCard draft。

2. **完整看 6 个 YouTube 优先视频。**  
   每个视频提取：流程步骤、使用工具、截图、slot 名称、模板样式、失败点、可借鉴 UI。

3. **把资料落成模板库结构。**  
   每个优秀案例输出：
   - `source`
   - `marketplace`
   - `category`
   - `slot_type`
   - `buyer_question`
   - `product_weight`
   - `layout_structure`
   - `copy_structure`
   - `text_overlay_method`
   - `brand_system`
   - `visual_generation_need`
   - `qa_risks`
   - `TemplateCard candidate`

## 13. 本轮最重要的纠偏

之前那个结构原型跑出来像“图片加文字”，这个批评是对的。它只能验证 JSON/artifact/QA 链路，不能代表你要的“套图生产系统”。

下一轮 demo 必须从真实优秀套图和真实生成/保真路线出发：

```text
好图/好套图拆解
  -> TemplateCard / SuiteTemplate
  -> 产品真值和品牌约束
  -> 真实生图或 preserve-first composite
  -> 专业字体/模板系统落版
  -> QA/reroll
  -> contact sheet + 单图 + manifest + 失败原因
```

验收也要按三个 Scale 对照：

- Amazon 套图逻辑是否完整。
- Ozon/WB 模板适配是否稳定。
- 保真/字体/QA/reroll 是否真正能闭环。

