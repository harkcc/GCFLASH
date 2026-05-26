# Listing 层级与视觉引导参考笔记

日期：2026-05-23  
工作目录：`/Users/cc/Desktop/photo_show`

## 1. 这次修正的问题

上一版 eMAG 优化样例更像“合规 HTML snippet 清理”，不够像一个有完整视觉层级的 listing。缺的问题主要是：

- 缺少整块背景板。
- 参数区还是偏文字清单，没有形成视觉分区。
- 每段之间的阅读顺序不够强。
- 还没有充分吸收 Amazon / A+ / 社区里关于信息层级的做法。

## 2. 外部参考提炼

### 2.1 Amazon / A+ / infographic 的共同做法

参考来源：

- [Amazon A+ Content Design Guide](https://sell.amazon.com/blog/a-plus-content-design-guide?mons_sel_locale=en_US)
- [Amazon Product Infographics Guide 2026](https://salesduo.com/blog/guide-to-amazon-product-infographics/)
- [Amazon Infographic Images Guide 2026](https://evolveamz.com/amazon-infographic-images-guide/)
- [GreenOnion A+ module tutorial](https://greenonion.ai/blog/amazon-aplus-content-tutorial-step-by-step)
- [Parials listing image tips](https://www.parials.com/insights/10-tips-better-amazon-listing-images)
- [Reddit: A+ content importance](https://www.reddit.com/r/AmazonFBA/comments/1qj0rhr/how_important_is_a_content_actually/)
- [Reddit: Blurry A+ content](https://www.reddit.com/r/AmazonFBA/comments/1shagzj/blurry_a_content_premium/)

可用结论：

- 主图偏白底，但详情/A+ 可以使用背景板、图文模块和色块。
- 每个模块只讲一个主要信息，不要一屏塞多个卖点。
- 视觉层级必须明确：主标题先抓住用户，副文案解释，图片或参数提供证明。
- 移动端优先，文字要大、短、对比强，不能用太小的字和太密的图标。
- A+ 更像一组连续模块，不是单张图片的重复堆叠。
- 背景图/背景板可以用，但不能抢走产品和核心卖点。
- 图片尺寸和模块比例要匹配，否则会模糊、拉伸或在手机端难读。

## 3. 转成 eMAG 详情 HTML 的原则

### 3.1 模块顺序

建议基础顺序：

1. `Hero Board`: 产品是什么 + 购买场景
2. `Motion Proof`: GIF 或动作用图，解释它证明什么
3. `Benefit Board`: 用户得到什么
4. `Feature Board`: 产品独特结构或核心机制
5. `Spec Board`: 参数和兼容性
6. `Package Board`: 包装内容
7. `Care / Safety Board`: 使用提醒

### 3.2 背景板用法

eMAG 详情 HTML 可以先按这组方式尝试：

- `table` 或 `div` 作为 800px 宽背景板
- inline `background-color`
- inline `color`
- inline `padding`
- inline `border`
- inline `text-align`
- 图片仍然单列、居中、`width=800`

更稳的做法是 `table width="800"` 或 `style="max-width:800px;width:100%;"`，因为很多电商详情系统对 table 的兼容比复杂 CSS 更稳定。

### 3.3 参数表现

参数区不要只是连续居中段落。更好的做法：

- 分成 2-3 个小组：尺寸/玩法/材质/适用年龄。
- 每个参数用粗体 label + 短 value。
- 背景用浅灰或浅色板。
- 如果用 table，要控制列数，手机端不做复杂多列。

### 3.4 可变量

后续每个产品要先判断表达变量：

- `product_archetype`: 教育玩具、技术配件、工具耗材、礼品、母婴小家电等
- `visual_intensity`: 白底极简、轻量色块、技术深色、生活方式
- `background_strategy`: 全板背景、分段背景、只用标题条
- `proof_mode`: 静态图、GIF、参数、步骤图、场景图
- `copy_density`: 极短、标准、参数密集
- `spec_strategy`: 列表、表格、图文对照

这一步决定模板，不应直接套固定样式。
