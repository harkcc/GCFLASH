# eMAG Detail HTML Capability Matrix

日期：2026-05-23  
工作目录：`/Users/cc/Desktop/photo_show`

## 1. 目的

把目前对 eMAG 详情 HTML 的理解压成一个可以直接用于生成和校验的能力矩阵：

- `Safe`
- `Accepted detail capability`
- `Gray zone`
- `Avoid / not recommended`

这里的判断来自两类证据：

- eMAG 官方文档
- 30 个真实前台样本的 live HTML

补充判定原则：

- 只要前台真实可见并稳定渲染，就视为“可用能力证据”。
- 但默认模板仍优先选手机端更稳、更简单的做法，而不是照抄现有卖家写法。

## 2. 标签能力

| 能力 | 结论 | 说明 |
|---|---|---|
| `p` | Safe | 官方示例明确给出，真实样本大量使用 |
| `h1-h3` | Safe | 官方给到 `h1-h6`，真实样本大量使用 |
| `strong` / `b` | Safe | 官方给了 `b`，真实样本高频使用 `strong` |
| `br` | Safe | 真实样本高频使用 |
| `ul` / `li` | Safe | 真实样本稳定存在，适合参数和清单 |
| `img` | Safe | 官方明确允许图片 |
| `table` / `tr` / `td` | Gray zone | 样本能显示，但不建议做主骨架 |
| `div` | Gray zone | 样本存在，但生成时不建议依赖复杂层级 |
| `blockquote` | Gray zone | 样本存在，但没有必要作为默认模块 |
| `em` / `u` / `center` | Gray zone | 官方示例有，但不是核心模板必需 |
| `iframe` | Avoid | 真实样本偶见，但只适合官方建议的 YouTube embed 路径 |
| `button` / `span` / 编辑器杂项 | Avoid | 更像现有样本残留，不适合作为生成输出 |

## 3. 图片与媒体能力

| 能力 | 结论 | 说明 |
|---|---|---|
| 普通图片 | Safe | 详情描述允许图片 |
| `width=\"800\"` 级别图片 | Safe | 官方明确给了 800px 建议 |
| 外链 `.jpg` / `.png` | Gray zone | 官方允许通过 URL 插图，但长期稳定性与版权仍需注意 |
| eMAG 自己域名图片 | Safer | 更接近平台内部图源 |
| GIF | Accepted for detail HTML | 样本 30/30 都有；按当前判断，详情 HTML 可以接受动态 GIF，但仍要和主图/辅图上传规则分开 |
| YouTube embed | Gray zone but official-path | 官方推荐视频只走 YouTube embed |
| 其他视频 / 任意 iframe | Avoid | 审核与兼容风险高 |

## 4. 布局与 CSS 能力

| 能力 | 结论 | 说明 |
|---|---|---|
| 单列长流 | Safe | 当前最稳，也最符合手机端弹层 |
| 居中单图 + 标题 + 短文 | Safe | 与真实样本和移动端阅读一致 |
| 简单 `text-align:center` | Safe | 样本高频使用 |
| `width:1140px` 固定宽图 | Gray zone | 样本高频使用，但明显是桌面偏置写法 |
| 多图并排 | Avoid by default | 样本在手机端基本没有稳态并排成功案例 |
| 大量 inline style | Gray zone | 能活，但生成上不应依赖太多自由样式 |
| 复杂多列表格 | Avoid by default | 样本能显示，但移动端体验不稳 |
| 完整自定义 CSS 体系 | Avoid | 当前证据不足，不适合假设可控 |

## 5. 内容能力

| 能力 | 结论 | 说明 |
|---|---|---|
| 客观卖点描述 | Safe | 官方鼓励 |
| 参数、兼容性、包装内容 | Safe | 应成为核心模块 |
| 使用方式 / 安全提示 | Safe | 与官方安全信息要求一致 |
| 价格、运费、库存、联系方式 | Avoid | 官方明确禁止 |
| 促销口号 / 夸张广告词 | Avoid | 官方明确禁止 |
| 竞争对手对比 | Avoid | 官方不鼓励，外部平台也常是风险点 |
| 图片里塞大量小字 | Avoid | Amazon/社区经验与移动端体验都反对 |

## 6. 生成默认策略

如果要为 eMAG 详情页做第一版稳定生成，默认策略应是：

- 只用安全标签子集
- 默认输出单列长流
- 默认图片宽度 `800`
- 默认用 `buyer question -> proof section` 节奏组织内容
- GIF 可用，但默认只在“动作证明/前后对比/使用过程”这类模块里使用
- 默认不用多表格和复杂布局

## 7. 灰区策略

以下能力可以保留，但必须做成“显式选择 + validator 提示”，不能静默默认：

- GIF
- 外链图床
- 表格
- `div` / `blockquote`
- 桌面宽图

## 8. 当前最稳的落地判断

对于后续 Skill / Scale / Agent Platform 集成，最稳的组合是：

- `Safe core HTML`
- `800px` 图片
- `single-column mobile-first`
- `benefit / proof / specs / package / safety` 五段式结构

而不是继续沿用当前卖家样本里的：

- `1140px` 固定长图
- 过度居中
- 大量灰区标签
- 无意义 GIF 依赖
