# eMAG 详情页生成工作流草案

日期：2026-05-23  
工作目录：`/Users/cc/Desktop/photo_show`

## 1. 目标

把 eMAG 详情 HTML 的生成拆成一条稳定、可审计、可 Scale 化的链路，而不是让模型直接自由输出整页 HTML。

## 2. 借鉴来源

### 2.1 来自 Open Design / PPT Agent 的方法

- 先读规则和上下文，不先动手写最终产物
- 先锁 brief，再做 planning
- 用模块库 / 模板库组织输出，而不是每次从零写
- 在生成后做 checklist / validator

### 2.2 来自当前 eMAG 样本的现实约束

- 手机端单列优先
- 图文节奏比复杂布局更重要
- 详情区可渲染的标签范围大于官方示例，但不能无限放开
- GIF / 表格 / 外链图源都属于灰区能力，不能默认依赖

## 3. 建议的整体链路

```text
User/Product Input
-> Rule Bundle Read
-> Design Context Read
-> DetailSectionPlan
-> Template Family Binding
-> Controlled HTML Render
-> eMAG Detail Validator
-> Human Annotation / Approval
-> Final HTML Artifact
```

## 4. 输入层

### 4.1 必填输入

- `product_title`
- `brand`
- `product_type`
- `language`
- `core_features[]`
- `specs[]`
- `compatibility[]`
- `package_contents[]`

### 4.2 强烈建议输入

- `usage_scenarios[]`
- `target_users[]`
- `risk_notes[]`
- `image_assets[]`
- `forbidden_claims[]`
- `allowed_claims[]`
- `brand_style_notes`

### 4.3 可选参考输入

- `competitor_urls[]`
- `category_reference_urls[]`
- `brand_reference_urls[]`

## 5. 预读上下文

后续 Agent 在开始规划前，应先读三类内容。

### 5.1 Rule Bundle

- eMAG 官方合规限制
- 当前允许 / 灰区标签子集
- 图片 / GIF / 视频规则
- 移动端单列优先约束

### 5.2 Design Context Bundle

- `DESIGN.md`
- 品牌案例
- 类目审美参考
- Amazon / Ozon / WB 的更优表达方式

### 5.3 Product Truth Bundle

- 产品事实
- 参数
- 材质 / 尺寸 / 功率 / 兼容性
- 包装内容
- 安全提示

## 6. 规划层：先产出 `DetailSectionPlan`

不要先写 HTML。先生成一份中间规划对象。

### 6.1 推荐字段

```json
{
  "section_id": "hero-01",
  "section_type": "hero",
  "buyer_question": "这是什么，它能解决什么问题？",
  "title": "Fast Type-2 EV Charging at Home and Outdoors",
  "body_points": [
    "22kW three-phase charging",
    "IP65 protection",
    "5m cable for flexible parking setups"
  ],
  "proof_mode": "hero_image_plus_short_copy",
  "image_slot": "hero_usage",
  "compliance_notes": [
    "Do not mention price",
    "Do not mention shipping"
  ]
}
```

### 6.2 section_type 建议

- `hero`
- `benefit`
- `feature_proof`
- `scenario`
- `specs`
- `compatibility`
- `package_contents`
- `safety_or_usage`
- `closing`

### 6.3 规划原则

- 每个 section 只回答一个 buyer question
- 每页只承载一个主要视觉动作
- 规格类 section 不强行做大图
- 不把同一信息重复写三遍

## 7. 模板绑定层

建议先做 3 套 template family，而不是一开始做很多花样。

### 7.1 `minimal_clean`

- 适合工具类、参数明确类产品
- 图少一点，结构清楚
- 强调标题、短段落、清单、参数块

### 7.2 `dense_feature`

- 适合卖点较多、需要逐条证明的产品
- 图文交替更密
- 每一段强调一个 feature + proof

### 7.3 `spec_first`

- 适合强参数、兼容性、尺寸敏感类产品
- 更重 specs / compatibility / package 内容
- 视觉上克制，但阅读效率高

## 8. 渲染层

HTML renderer 默认只允许受控子集：

- `p`
- `h1`
- `h2`
- `h3`
- `strong`
- `br`
- `img`
- `ul`
- `li`
- 必要时 `table`
- 必要时 `tr`
- 必要时 `td`

默认策略：

- 单列
- 窄屏优先
- 图片块全宽或近全宽
- 不默认输出复杂 inline style

## 9. 校验层

建议单独做一个 `validate-emag-detail-html`，负责脚本化约束。

### 9.1 可脚本化的检查

- 是否出现价格 / 运费 / 保修 / 联系方式 / 促销词
- 是否超出允许标签集
- 是否存在失效图片链接
- 是否存在明显过密结构
- 是否出现过多并列图片
- 是否把大段文字烤进图片区块说明中

### 9.2 需要标灰而不是直接拦截的能力

- GIF
- 外链图床
- 表格
- inline style

这些能力不是绝对不行，但需要额外风险提示。

## 10. 人工审核层

最后一轮不应只有文本审阅，还要支持 HTML 批注与修改。

人工审核重点：

- 信息是否准确
- 是否有违规承诺
- 手机端是否顺
- 节奏是否太像“长图堆叠”
- 是否可以删掉冗余模块

## 11. 最小可做版本

第一版建议不要上太多自动化，先做：

1. 固定输入表
2. 固定 3 套 template family
3. 先产 `DetailSectionPlan`
4. 再渲染 HTML
5. 跑 validator
6. 人工审批

这已经足够把链路跑通。

## 12. 一句总结

这条链路的关键不是“让模型更会写 HTML”，而是：

- 先把规则、事实、设计上下文读对
- 再把详情拆成可规划的 section
- 最后才把它渲染成受控 HTML

这样它才适合被做成 Skill / Scale / Agent Platform 里的稳定能力。
