# eMAG 详情 HTML 限制、样本规律与后续生成工作流

日期：2026-05-23  
工作目录：`/Users/cc/Desktop/photo_show`

## 1. 研究目标

本轮关注的是 eMAG 商品详情里的 **HTML 描述区**，不是主图设计本身。目标是：

- 读懂 eMAG 官方对详情描述、图片、HTML 的限制。
- 基于真实商品样本，确认前台实际会渲染什么、手机端为什么会呈现成现在这样。
- 把这些结论转成后续模板、SOP、Agent 工作流可直接复用的输入。

## 2. 当前证据面

### 2.1 官方来源

- eMAG 手动上新说明（中文）  
  [https://marketplace.emag.ro/infocenter/emag-academy/如何手动添加产品/?lang=zh-hans](https://marketplace.emag.ro/infocenter/emag-academy/%E5%A6%82%E4%BD%95%E6%89%8B%E5%8A%A8%E6%B7%BB%E5%8A%A0%E4%BA%A7%E5%93%81/?lang=zh-hans)
- eMAG 主图标准  
  [https://marketplace.emag.ro/infocenter/emag-academy/how-to-add-a-product/the-main-product-image-standard/?lang=en](https://marketplace.emag.ro/infocenter/emag-academy/how-to-add-a-product/the-main-product-image-standard/?lang=en)
- eMAG 无效图片错误页  
  [https://marketplace.emag.ro/infocenter/emag-academy/how-to-add-a-product/errors-when-adding-products-manually/errors-invalid-images/?lang=en](https://marketplace.emag.ro/infocenter/emag-academy/how-to-add-a-product/errors-when-adding-products-manually/errors-invalid-images/?lang=en)
- eMAG 图片文档标准  
  [https://marketplace.emag.ro/infocenter/documentation-standards-product-images/?lang=en](https://marketplace.emag.ro/infocenter/documentation-standards-product-images/?lang=en)

### 2.2 已抓取的真实前台样本

- 批量详情 HTML：`/Users/cc/Desktop/photo_show/output/emag_detail_html_live_batch/`
- 统计摘要：`/Users/cc/Desktop/photo_show/output/emag_detail_html_live_batch/summary.md`
- 约束信号摘要：`/Users/cc/Desktop/photo_show/output/emag_detail_html_live_batch/constraints_summary.md`
- 约束分析脚本：`/Users/cc/Desktop/photo_show/scripts/analyze_emag_detail_html_constraints.py`

当前已保存 **30 个真实产品** 的详情 HTML，超过最初的 20 个目标。

### 2.3 外部社区与补充官方信号

除了主文档外，这一轮又补了两类信号：

- eMAG FAQ 明确写到：产品描述中可以通过 HTML tag 添加图片和演示视频。
- eMAG 单独还有一篇 “Using HTML elements in product description” 说明页，明确讲了描述区支持图片、视频、段落、标题、加粗、居中、左右对齐等简单 HTML。
- 社区讨论里不断出现一个现实：同一个产品页会聚合多个 seller，描述、图片、标题和 seller 责任之间并不总是清晰分离；而且用户对“描述不准确、图片/描述不一致、审核不严”的抱怨不少。

这几条对我们后续生成非常重要，因为它们说明：

1. **官方示例很保守，但前台真实活着的 HTML 能力更大。**
2. **前台真实存活样本本身就是一类强证据。**
3. **社区反复提到描述/图片不准确，说明我们更应该做“受控生成 + validator”，而不是只模仿现有卖家页面。**

补充来源台账已单独落盘：

- [2026-05-23_emag_detail_external_source_ledger.md](/Users/cc/Desktop/photo_show/research/2026-05-23_emag_detail_external_source_ledger.md)

## 3. 官方明确给出的限制

### 3.1 描述内容限制

eMAG 官方手动上新文档对描述内容写得比较明确：

- 不要写价格、保修、配送费、库存、联系方式、网站、邮箱。
- 不要写“极好、卓越、超棒”等夸张形容词。
- 不要写促销口号或催单话术。
- 不要插入隐藏超链接。
- 不要链接到其他产品或外部销售网站的图片/视频。
- 不要使用编辑粗糙、低清晰度、低分辨率图片。

这部分属于 **硬合规边界**，后续生成器应直接内置为禁止项。

### 3.2 官方明确允许的描述能力

官方同页明确说描述区可以插入：

- 文本
- 图片
- 视频
- HTML 格式文本

并给了简单 HTML 示例：

- `<p>`
- `<h1>` 到 `<h6>`
- `<em>`
- `<b>`
- `<center>`
- `<u>`
- `<p style="text-align:right;">`
- `<p style="text-align:left;">`

同时官方还明确写到：

- 描述中图片标准宽度建议是 `800px`
- 图片链接应以 `.jpg` 或 `.png` 结尾
- 可以设置边框、`HSpace`、`VSpace`
- 视频建议用 YouTube embed

这里要注意：**这是示例，不是完整白名单**。它告诉我们“简单 HTML 肯定可以”，但没承诺“只有这些标签能用”。

另外，eMAG FAQ 和 “Using HTML elements in product description” 说明页进一步强化了这点：

- FAQ 直接回答：可以在产品描述里加入展示视频或图片，而且是通过 HTML tag 完成。
- HTML 元素说明页还明确说：可以从其他网页复制 HTML 代码放进描述里，只要内容符合 eMAG 标准，并且不能带 logo、水印、推广链接。

这条非常关键，因为它意味着平台思路本来就不是“只允许极少数硬编码标签”，而是：

- **允许使用 HTML 增强描述**
- **但是否通过，取决于内容是否符合平台标准**

### 3.3 图片上传规则与详情媒体规则不是一回事

官方图片上传规则包括：

- 主图应完整展示产品。
- 主图应清晰，产品尽量居中，占画面约 `85%`。
- 主图建议白底或灰底；某些类目允许专业环境背景。
- 图片格式可为 `jpg/png/jpeg/gif`，但 **不接受动态 GIF**。
- 最大文件大小 `8 MB`。
- 辅图建议至少 `3-5` 张。

关键点：

- 这部分说的是 **主图 / 辅图上传**。
- 不应直接把它等同于 **详情 HTML 内嵌媒体** 的规则。

## 4. 30 个真实详情 HTML 实际证明了什么

### 4.1 手机端承载方式

移动端详情不是直接裸露在商品正文流里，而是包在一个详情弹层中：

- 稳定容器选择器：`.in-modal-description-section`

这意味着后续模板设计必须默认：

- 按窄屏阅读设计
- 按“单列长流”设计
- 不按传统桌面详情页的双列心智设计

### 4.2 基础结构统计

样本汇总结果：

- 样本数：`30`
- 平均图片数：`10.67`
- 中位图片数：`10.5`
- 图片范围：`5 - 16`
- 平均文本长度：`3326.1`
- 中位文本长度：`2905.5`
- 平均标题数：`7.6`
- 平均段落数：`31.03`
- `maxImagesPerRow = 1`：`30 / 30`

直接结论：

- 前台真实呈现几乎都是 **单列图片流**。
- 没有任何样本在手机端形成“稳态双列图墙”。

### 4.3 实际标签使用范围

30 个样本高频标签远超官方示例。前 12 个高频标签是：

- `p`
- `strong`
- `img`
- `br`
- `td`
- `li`
- `div`
- `tr`
- `blockquote`
- `h2`
- `ul`
- `h1`

说明：

1. 前台渲染支持范围明显大于官方“简单 HTML 示例”。
2. 至少在真实存活样本里，`table / tr / td / ul / li / blockquote / strong / img / h1-h3` 都能显示。
3. 但这仍然不等于官方对这些标签做了正式承诺。

因此后续应分层：

- `Safe core`：`p / h1-h3 / strong / br / img / ul / li`
- `Gray zone but proven in live samples`：`table / tr / td / div / blockquote / inline style`

### 4.4 图片与 GIF 的真实使用情况

约束分析脚本输出显示：

- `30 / 30` 个样本都出现了 GIF
- 总 GIF 数：`44`
- 总图片数：`320`
- `30 / 30` 产品都至少有 1 张 GIF

这说明一个非常重要的现实：

- **动态 GIF 在详情 HTML 里至少“前台可见且被真实卖家使用”**
- 但官方上传规则同时写明 **主图/辅图上传不接受动态 GIF**

合理解释是：

1. 主图 / 辅图上传规则与详情 HTML 媒体规则分离；
2. 或者详情区对外链 GIF 的审核比主图上传更松；
3. 也可能只是“当前能活着”，不代表官方长期稳定支持。

所以后续系统里对 GIF 的处理应调整为：

- 详情 HTML 可以接受动态 GIF
- 主图/辅图上传规则仍单独校验
- 默认只在“动作证明、安装过程、前后对比、效果演示”这些有明确解释价值的模块里使用
- 在 validator 里标记为 info，而不是风险 warning

### 4.5 宽度、居中、以及“为什么手机端最后都变成这样”

约束信号摘要显示：

- `83.44%` 的图片以 `1140` / `1140px` 宽度渲染
- `text-align:center;` 是最高频 inline style，共 `645` 次
- 平均每个产品有 `21.53` 个居中节点
- 平均每个产品有 `4.87` 个包含 `1140px` 的节点

这说明大量详情 HTML 的作者其实是在写：

- 桌面宽图
- 固定宽度内容块
- 居中对齐的长图流

然后前台手机端再把这些内容 **整体缩进窄屏容器** 里显示。

所以手机端之所以几乎都看成：

- 一张一张全宽图
- 中间插少量说明文字
- 几乎没有真正多列

不是因为平台完全禁止复杂布局，而更可能是这几层因素共同作用：

1. 详情放在窄屏弹层里。
2. 大量卖家用固定宽度 `1140px` 的居中图片。
3. 浏览器在窄容器内自动缩放这些宽图。
4. 卖家自己也为了兼容手机，倾向于回避复杂并列布局。

### 4.6 表格不是禁用，但不是主流骨架

- `11 / 30` 样本含 `table`
- 但手机端最终仍然没有形成稳定双列阅读体验

这说明：

- `table` 可以作为“参数/对照/包装内容”的补充能力
- 但不应成为主模板骨架

## 5. 硬限制、卖家习惯写法、优化空间

### 5.1 可以视为硬限制的部分

- 不写价格、物流、保修、库存、联系信息、外链导购信息
- 不写促销话术和夸张广告词
- 不写竞争对手导向内容
- 不使用低清晰度图片
- 详情设计必须按手机端窄屏阅读优先
- 主图规则与详情 HTML 规则必须拆开处理

### 5.2 更像“当前卖家习惯”的部分

- 大量使用 `1140px` 固定宽图
- 全文高度依赖 `text-align:center`
- 一屏一张图，极少做并列
- 很多详情直接堆长图，而不是做清晰的模块层次
- 大量引用外部图床

这些不是必须照抄的标准。

同时，社区信号也支持这一点：

- 用户和卖家讨论里反复提到，eMAG 的商品页会聚合多个 seller，很多时候“产品描述”不是 seller 级精细隔离的。
- 也有人直接抱怨描述、图片、实际收到商品不一致，或者平台对 Marketplace 描述审核并不严格。

这说明：

- 现有前台案例里能活着的内容，不等于它们就是最佳实践。
- 但只要这些 HTML 在前台真实可见并稳定工作，它们就仍然是 **可用实现证据**。
- 我们后续要做的不是“否定这些活样本”，而是 **把它们里真正有效的能力抽出来，再用更干净的结构重写。**

这里再把证据优先级说死一点，避免后续跑偏：

1. 官方明确禁止：直接当硬限制
2. 官方明确允许：默认 safe
3. 前台 live HTML 稳定存活：默认当作可用能力证据
4. 社区/第三方讨论：只作为风险提示和优化启发，不单独升级成规则

### 5.3 明确存在的优化空间

用户前面提醒得对，**这些样本不能被当成唯一标准**。基于当前证据，可以明确看出还有空间：

- 可以比现有样本更讲究模块节奏，不必只是“长图堆叠”。
- 可以减少无意义的重复大图，提升每一屏的信息密度。
- 可以让文字层次更清楚，不必每段都只有居中大图 + 零散句子。
- 可以对参数、兼容性、包装内容做更克制的结构化表达。
- 可以把“图 + 文 + 规格 + 使用场景”的顺序设计得更像转化路径，而不是素材堆放路径。

## 6. 对后续模板最稳的结论

### 6.1 模板默认骨架

最稳妥的详情骨架建议仍然是单列、问题驱动：

1. 顶部主视觉 / 使用结果图
2. 产品是什么，解决什么问题
3. 3-5 个核心卖点模块
4. 尺寸 / 参数 / 兼容性
5. 包装内容 / 使用说明 / 注意事项
6. 场景收尾或补充证明

### 6.2 每个模块只回答一个 buyer question

建议把详情页理解为“连续回答用户问题”，而不是“连续贴图”：

- 这是什么？
- 为什么比普通方案更好？
- 适合谁 / 不适合谁？
- 怎么用？
- 尺寸和参数是否匹配？
- 包装里有什么？

### 6.3 建议默认启用的 HTML 子集

建议 renderer 默认只用：

- `section` 级结构在内部抽象，不直接依赖复杂 HTML
- 输出层只落：
  - `p`
  - `h1-h3`
  - `strong`
  - `br`
  - `img`
  - `ul`
  - `li`
  - 必要时 `table / tr / td`

并尽量避免：

- 复杂嵌套 `div`
- 深层表格套表格
- 大量自由 inline style

## 7. 更好的电商详情页 HTML SOP

当前很多样本的问题不是“不能看”，而是 **SOP 太弱**，更像素材堆放，没有明确的转化顺序。更好的 SOP 可以定义为：

### 7.0 外部成熟做法带来的启发

除了 eMAG 样本本身，还可以借几条更成熟的详情页逻辑：

- Amazon 官方 A+ 指南强调：
  - 文本和图片要平衡，不要只堆图。
  - 要明确补充技术规格。
  - 可以用 comparison chart 帮用户快速判断。
  - 不要把大量文字烤进图片里，否则手机端会难读。  
  来源：  
  [Amazon A+ Content Design Guide](https://sell.amazon.com/blog/a-plus-content-design-guide?mons_sel_locale=en_US)

- SupplyKick 对 A+ 的结构建议更接近可执行 SOP：
  - 先讲 benefit，不先讲 feature
  - 尽早回答最大的购买疑问
  - 多场景产品按“一张图对应一个场景”组织
  - 最后再落到 specs 和 what’s in the box  
  来源：  
  [Amazon A+ Content Guide: Best Practices That Convert](https://www.supplykick.com/blog/a-content-guide)

- Shopify 对产品页的通用经验说明：
  - 好页面不是只讲参数，而是更会讲 benefit
  - 更深层信息放在后面逐层展开，而不是首屏全塞满
  - 视频、3D、场景化内容的意义是帮助用户理解产品，不是纯装饰  
  来源：  
  [Shopify Product Page Design Examples](https://www.shopify.com/blog/product-page)

- 社区经验和官方结论是一致的：
  - 如果把太多文字做进图里，手机端缩放后会难读
  - 用真正的文本模块比“图片里嵌字”更稳，也更利于搜索理解  
  来源：  
  [Reddit: Advice for Images vs A+ Content](https://www.reddit.com/r/AmazonSeller/comments/1fqrdt0/advice_for_images_vs_a_content/)

### Step 1. 锁定事实层

先收集：

- 标题
- 品牌
- 产品类型
- 核心参数
- 兼容性 / 适用人群
- 包装内容
- 风险提示 / 安全提示
- 不允许写的内容

### Step 2. 锁定 buyer questions

把产品信息翻译成用户真实问题，通常先做 `5-8` 个：

- 为什么要买它？
- 和普通版差别是什么？
- 我的场景能不能用？
- 尺寸 / 功率 / 材质够不够？
- 安装 / 使用难不难？
- 包装里到底有什么？

### Step 3. 先规划 section，不先写 HTML

先产出 `DetailSectionPlan`：

- `section_type`
- `buyer_question`
- `title`
- `proof_type`
- `image_slot`
- `body_points`
- `compliance_notes`

### Step 4. 再决定图片与文案配比

不是每段都要“大图 + 少字”。应按问题类型分：

- 情绪和场景：图重一点
- 参数和兼容性：文字/结构重一点
- 复杂功能：图 + 简短解释并重
- 包装内容：清单化表达

### Step 5. 最后才渲染 HTML

把 plan 渲染为受控 HTML，而不是直接让模型自由写整个详情页。

### Step 6. 用 validator 做最后一轮审核

至少检查：

- 禁用词 / 禁用声明
- 标签子集是否越界
- 图片链接是否有效
- 是否出现过多并排 / 过密结构
- 是否有明显桌面优先而非手机优先的块

## 8. 后续 Agent 工作流应该怎么借 PPT Agent / Open Design

### 8.1 可以直接借的核心方法

从 Open Design 和 PPT Agent 这条线里，最值得借的不是“PPT 长什么样”，而是这套顺序：

1. 先读设计系统 / 规则 / 参考案例
2. 先锁 brief，再做计划
3. 用模块库组织输出
4. 生成前后都有 QA / validator

Open Design 里已经明确有这些模式：

- `DESIGN.md` 作为设计系统注入
- `question-form` 先锁 brief
- 先读 `template / references / checklist`
- 生成后做 checklist 和 critique

PPT Agent 那边更适合借的是：

- `source docs/data -> template library -> DESIGN.md -> asset system -> validator`

### 8.2 转成 eMAG 详情页后的建议链路

建议后续不是“用户一句话 -> 直接吐 HTML”，而是：

1. `Product Input`
   - 标题、品牌、参数、兼容性、包装内容、目标语言、素材
2. `Platform Rule Read`
   - eMAG 官方限制
   - 当前 renderer tag 子集
   - 当前 validator 规则
3. `Design Context Read`
   - `DESIGN.md`
   - 品牌案例
   - 类目参考页
   - Amazon / Ozon / WB 的更优设计模式
4. `Section Planning`
   - 生成 `DetailSectionPlan`
   - 明确每段 buyer question、图文比例、证明方式
5. `Template Binding`
   - 将 section plan 绑定到 2-3 套 detail template family
6. `HTML Render`
   - 输出受控 HTML
   - 默认单列、移动端优先
7. `Compliance / Mobile QA`
   - 禁用词
   - 标签越界
   - 图片/GIF/宽度风险
   - 是否出现难读小字 / 过密结构
8. `Human Review / Annotation`
   - 利用现有 HTML 批注与修改能力做最后修正

### 8.3 可以直接抽象出的中间产物

建议后续把详情页生成拆成几个稳定对象：

#### `DetailEvidencePack`

- 产品事实
- 合规规则
- 禁止声明
- 类目参考
- 品牌参考

#### `DetailSectionPlan`

- `section_id`
- `section_type`
- `buyer_question`
- `title`
- `body`
- `proof_mode`
- `image_slot`
- `compliance_notes`

#### `DetailTemplateFamily`

- `minimal_clean`
- `dense_feature`
- `spec_first`

#### `DetailHtmlArtifact`

- `html`
- `asset_refs`
- `validator_report`

## 9. 最值得固化进 Scale / Skill 的内容

适合固化进脚本 / validator / schema 的：

- 禁止声明
- 标签白名单 / 灰名单
- 图片链接与格式检查
- 单列优先规则
- 模块数量上限
- 参数 / 包装内容 / 兼容性的结构化输出要求

适合保留在 Skill / SOP 里的：

- 每种类目应该先回答哪些 buyer questions
- 图文节奏如何安排
- 何时该用更强视觉，何时该收敛
- 哪些 Amazon/Ozon/WB 模式适合作为设计参考，但不直接照搬

## 10. 当前结论

这批样本足以支持一个明确判断：

- eMAG 详情 HTML 并不是只能做得很土，它只是被手机端承载方式、卖家旧习惯、和合规边界共同压成了“单列长图流”。
- 真正应该尊重的是 **手机端单列阅读 + 内容合规 + 结构清晰**。
- 真正不该照抄的是 **1140px 长图堆叠、过度居中、无节奏素材堆放**。

所以后续方向应是：

- 把 eMAG 当作 **合规目的地**
- 把 Amazon / Ozon / WB 当作 **设计参考库**
- 把 Open Design / PPT Agent 当作 **生成流程与 QA 方法来源**

而不是把这 30 个卖家样本当作唯一审美标准。
