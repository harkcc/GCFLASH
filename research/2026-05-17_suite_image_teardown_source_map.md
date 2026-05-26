# 套图优秀案例拆解源地图 V1

日期：2026-05-17

目标：为“预制图生产系统”建立可复用的样本池。重点不是复制图片，而是从成熟案例里抽取稳定的 `Slot -> Layout -> Copy -> Overlay -> QA` 结构，最后沉淀成我们的 `TemplateCard`。

## 1. 先采用的样本源分层

### A. 本地已有截图样本，优先拆

路径：`references/user_cases/20260504_lark_examples/`

这些是最适合马上开始拆的素材，因为它们已经接近用户看到的小红书/实战教程语境，包含 Amazon、Ozon、俄语平台、PSD 模板、提示词方法和套图结构。

| 样本 | 主要价值 | 可沉淀 TemplateCard |
|---|---|---|
| `05.jpg` Amazon/Walmart 紫色 PSD 模板 | 固定品牌色、功能分区、卖点块、适合批量替换产品 | `amazon_purple_feature_grid_v1` |
| `11.jpg`、`12.jpg`、`13.jpg` Ozon 主图规则/案例 | 俄语平台高转化主图逻辑：大产品、强利益点、少文字、移动端优先 | `ozon_high_conversion_main_v1` |
| `02.jpg` 可调支架对比图 | 对比图/参数图：前后状态、角度、功能差异 | `adjustment_comparison_blueprint_v1` |
| `10.jpg` 工业产品详情套图 | 深色科技/工业类详情：局部放大、结构说明、模块化参数 | `industrial_dark_modular_detail_v1` |
| `09.jpg` Amazon 多场景布局分享 | 多 slot 套图顺序：主图、功能图、场景图、细节图 | `amazon_multi_scenario_board_v1` |
| `01.jpg` 宠物/清洁场景图 | 场景图和产品保持一致的提示词思路 | `image2_pet_cleaning_action_v1` |

结论：本地样本已经足够做第一批 6 个 TemplateCard 草稿。

### B. Amazon 成熟套图/作品集源

| 来源 | 链接 | 适合拆什么 |
|---|---|---|
| Seller Studio examples | https://sellerstudio.us/examples.html | “一张产品图 -> 8 张图”的最直接产品化参考。其公开示例包含 Main Image、Lifestyle、Dimension Callout、Three-Strip Infographic、Callout Diagram。 |
| Jungle Scout Amazon infographic guide | https://www.junglescout.com/resources/articles/amazon-product-infographic/ | Amazon 信息图的商业逻辑：副图承担卖点解释、使用场景、品牌一致性、字体一致性、目标人群匹配。 |
| Behance Amazon A+ / Listing portfolio | https://www.behance.net/gallery/153196069/Amazon-A-Content-Listing-Lifestyle-Infographics | 设计师作品集，适合拆完整套图顺序：Main、Dimensional、Infographics、Features、Lifestyle、A+。 |
| Behance Amazon infographic search | https://www.behance.net/search/projects/amazon%20infographics?locale=en_US | 用于持续扩充跨品类案例：美妆、宠物、补剂、工具、健身、水杯、家居。 |
| Parials Amazon listing image design | https://www.parials.com/amazon-listing-image-design/ | 候选拆解源，适合看服务商如何组织 Amazon 9 图/信息图/对比表/利益图。 |
| Delightful Design Studio listing images | https://www.delightfuldesignstudio.com/listing-images | 候选拆解源，适合找偏品牌化和高审美的 Amazon 副图。 |

Amazon 源的主要价值：它更适合建立“标准 slot taxonomy”和套图顺序。典型顺序可以先按：

1. 白底主图优化
2. 核心卖点信息图
3. 尺寸/比例参考
4. 包装/包含物展示
5. 细节放大
6. 使用步骤/安装步骤
7. 场景生活方式图
8. 对比图/竞品替代图
9. A+ 模块延展

### C. Ozon / Wildberries 模板化源

| 来源 | 链接 | 适合拆什么 |
|---|---|---|
| Sozdai examples | https://sozdai.app/blog/infografika-primery | 非常适合我们的方法论：一个 slide 一个卖点；完整卡片通常 4-6 张；按服装、化妆品、电子、家居、食品、儿童品类分 slot。 |
| Bitypixel | https://bitiypixel.ru/ | 模板化产品参考：上传普通产品图、去背景、套 12 个 3:4 模板、文字/图标/徽章自动排版；重点是“模板适配”不是纯生图。 |
| Ischenko Design | https://ischenkodesign.ru/ | 俄语服务商作品集，强调买家浏览行为、平台要求、竞品分析、CTR 因素，适合拆 Ozon/WB 首图和电子/家居/美妆品类。 |
| Behance Ozon/WB card project | https://www.behance.net/gallery/229053767/kartochki-tovarov-s-infografikoj-Ozon-i-Wildberries | 单个作品集内有服装、玩具、睫毛膏、运动用品，适合看同一市场下的品牌一致性和图标/色块系统。 |
| Behance Ozon/WB search | https://www.behance.net/search/projects/ozon%20wildberries%20product%20card | 用于继续扩充俄语平台视觉案例。 |

Ozon/WB 源的主要价值：更贴近“批量生产”。常见工作流不是自由生成，而是：

`竞品分析 -> 选择模板 -> 抠图/去背景 -> 改标题和短卖点 -> 套品牌色/徽章 -> 导出 3:4 卡片`

这条路线比纯 AI 生图更稳定，尤其适合我们做预制系统。

### D. 小红书/中文社区源

网页搜索对小红书内容抓取不稳定，直接网页检索很难系统拿到完整笔记。但小红书仍然值得作为“中文实战拆解语言”和“卖家审美样本”的来源。

建议在小红书里手动搜这些词，然后把截图放进 `references/user_cases/`：

| 搜索词 | 预期找什么 |
|---|---|
| `亚马逊 主图 拆解` | 主图构图、白底合规、主图点击率思路 |
| `亚马逊 副图 模板` | 信息图、尺寸图、卖点图模板 |
| `Amazon listing 图片拆解` | 完整 listing 套图顺序 |
| `跨境电商 主图 副图` | 中文卖家实操案例 |
| `商品图 信息图 模板` | 通用信息图布局 |
| `亚马逊 A+ 页面设计` | A+ 模块和副图的衔接 |
| `Ozon 商品卡片` | Ozon 首图/副图设计 |
| `WB Ozon 信息图` | 俄语平台模板和高密度卡片 |
| `电商套图 拆解` | 完整套图案例拆解 |
| `详情页 套图 设计拆解` | 非平台化但可转成 A+ / 副图的长图模块 |

小红书拆解时不要重点学“具体视觉风格”，重点学这些：

- 标题如何压缩成 3-7 个字的可扫读短句
- 一个图只解决一个买家问题，还是堆多个卖点
- 主视觉占比、徽章数量、局部放大数量
- 图文关系：文字是设计的一部分，还是后期硬贴
- 是否适合移动端首屏读完
- 评论区/博主说明里提到的转化理由

## 2. 拆解统一表

后续每张优秀图都按这张表拆，不直接讨论“好不好看”。

| 字段 | 记录内容 |
|---|---|
| `source` | 来源链接或本地图片路径 |
| `marketplace` | Amazon / Ozon / WB / Xiaohongshu / other |
| `category` | 品类，例如家居、电子、美妆、宠物、服装、工业件 |
| `slot_type` | 主图、卖点图、疑虑解决、尺寸参考、包装展示、对比图、步骤图、细节放大、生活方式、移动端信息图、A+ 模块 |
| `buyer_question` | 这张图回答买家的什么问题 |
| `product_weight` | 产品在画面中的占比和位置 |
| `layout_structure` | 版式骨架：左右分栏、上下三段、中心大产品、角落徽章、三条带、局部放大等 |
| `copy_structure` | 标题、短卖点、数字、参数、注释的层级 |
| `text_overlay_method` | 文字是模板叠加、AI 生成进图、还是后期排版 |
| `brand_system` | 色彩、字体、边框、icon、徽章是否统一 |
| `visual_generation_need` | 需要 AI 生图、产品抠图、场景图、还是只需要模板排版 |
| `qa_risks` | 产品变形、文字错误、移动端不可读、违规、过度承诺、构图拥挤 |
| `template_card_candidate` | 可沉淀的 TemplateCard 名称 |

## 3. 第一批要拆的 12 个目标

| 优先级 | 目标 | 为什么先拆 |
|---|---|---|
| P0 | 本地 `05.jpg` Amazon/Walmart 紫色模板 | 已经是可复用 PSD/模板思路，适合直接变成 TemplateCard |
| P0 | 本地 `11-13.jpg` Ozon 主图逻辑 | 适合沉淀 Ozon/WB 高转化 3:4 首图 |
| P0 | Seller Studio tea kettle 8 图套装 | 最接近“一张产品图生成一套图”的产品化范式 |
| P0 | Sozdai 分类例子 | 可以快速建立品类 -> slot 的映射 |
| P1 | Bitypixel 12 个模板逻辑 | 用来确认模板适配、文本替换、去背景、徽章系统 |
| P1 | Jungle Scout 信息图指南 | 用来补 Amazon 副图为什么这样排 |
| P1 | Behance Amazon A+ / Listing portfolio | 用来拆高审美完整套图顺序 |
| P1 | Ischenko Design Ozon/WB 作品 | 用来拆俄语平台首图、竞品分析、CTR 视角 |
| P1 | Behance Ozon/WB card project | 用来拆同一平台不同品类的视觉一致性 |
| P2 | Parials / Delightful Design Studio | 用来补服务商交付包结构 |
| P2 | 小红书 `亚马逊 副图 模板` 搜索结果 | 用来提炼中文卖家的实操表达和拆解语言 |
| P2 | 小红书 `Ozon 商品卡片` 搜索结果 | 用来补 Ozon/WB 中文圈的模板改图经验 |

## 4. 目前看到的稳定规律

### Amazon：更适合沉淀“套图顺序”

Amazon 的成熟套图通常不是单张图取胜，而是整套图在解决一组买家问题：

- 主图：让买家在搜索页认出产品，避免复杂背景。
- 卖点图：把 bullet point 变成可扫读视觉。
- 尺寸图：解决“买回来合不合适”的疑虑。
- 包装/包含物：解决“到底收到什么”的疑虑。
- 细节放大：证明材料、结构、质感。
- 场景图：让买家想象使用状态。
- 对比图：解释为什么比旧方案/竞品好。
- A+：承接品牌故事、模块化参数、长解释。

### Ozon/WB：更适合沉淀“模板适配”

俄语平台的高频逻辑更像搜索卡片广告：

- 3:4 竖图优先，移动端可读。
- 产品很大，文字很短，利益点强。
- 模板里预留标题、2-4 个卖点、icon、徽章、底部参数条。
- 常见流程是去背景 + 套模板 + 改文字 + 调品牌色。
- 竞品分析比纯 prompt 更重要，因为首图要在搜索结果里赢点击。

### 小红书：更适合提炼“中文卖家拆解语言”

小红书不是最稳定的素材抓取源，但很适合补这些东西：

- 卖家如何解释“为什么这张图转化更高”。
- 他们如何命名 slot，例如主图、卖点图、参数图、疑虑图、氛围图。
- 哪些视觉元素在中文跨境卖家圈被反复使用，例如箭头、对比框、红色/黄色强提示、局部放大、参数贴片。

## 5. 下一步产物

下一步不继续泛搜，先做一个可落地样本库：

1. 从本地样本和上面的外部源里选 12 个优秀套图/单图。
2. 每个样本按统一拆解表填一条记录。
3. 每个样本输出一个 `TemplateCard draft`：
   - `slot_type`
   - `canvas_ratio`
   - `required_inputs`
   - `layout_zones`
   - `copy_rules`
   - `brand_tokens`
   - `generation_prompt_notes`
   - `overlay_rules`
   - `qa_checks`
4. 先不追求自动生成，先把模板和判断标准做扎实。

