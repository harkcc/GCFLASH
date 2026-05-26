# eMAG Detail Generation Scale Contract

日期：2026-05-23  
工作目录：`/Users/cc/Desktop/photo_show`

## 1. 目标

把 eMAG 详情页生成拆成：

- **机器可检查** 的结构契约
- **Skill/SOP** 负责的高判断任务

避免所有规则都堆在 prompt 里。

## 2. 机器契约文件

### 输入 schema

- [emag_detail_product_input.schema.json](/Users/cc/Desktop/photo_show/workflow/schemas/emag_detail_product_input.schema.json)

### 中间规划 schema

- [emag_detail_section_plan.schema.json](/Users/cc/Desktop/photo_show/workflow/schemas/emag_detail_section_plan.schema.json)

### 当前最小 renderer

- [render_emag_detail_from_plan.py](/Users/cc/Desktop/photo_show/scripts/render_emag_detail_from_plan.py)

### 当前最小 validator

- [validate_emag_detail_html.py](/Users/cc/Desktop/photo_show/scripts/validate_emag_detail_html.py)

## 3. 适合进入 validator / Scale 的规则

这些规则属于“脚本可判断”，应尽量离开纯 prompt：

### 3.1 输入结构

- 必填字段是否齐全
- specs 是否至少有基础键值对
- package contents 是否为空
- section plan 是否达到最小 section 数

### 3.2 合规规则

- 是否出现价格、运费、保修、联系方式、促销语
- 是否出现不在允许集内的标签
- 是否出现 GIF，以及是否有明确的动作证明/使用过程价值
- 是否出现外链图片 host
- 是否出现 table
- 是否出现桌面宽图偏置

### 3.3 输出结构

- section 是否存在
- 每段是否有标题
- 是否存在图片但没有 alt
- 是否存在超出约束的标签或媒体

## 4. 适合保留在 Skill / SOP 的规则

这些规则判断更依赖语境，不应硬塞进 validator：

- 应先回答哪些 buyer questions
- 哪个 template family 更适合当前产品
- 图文节奏怎么分配
- 哪些卖点需要更靠前
- 哪些 Amazon / Ozon / WB 模式适合借鉴
- 是否需要场景图、参数图、包装图、兼容性图

## 5. 推荐执行链

```text
Input schema check
-> Product Truth normalization
-> DetailSectionPlan generation
-> Section plan schema check
-> Template family selection
-> HTML render
-> Detail HTML validator
-> Human review / annotation
```

## 6. 第一版 Scale 建议

如果现在就要开始做 Scale，不建议做“大而全”的版本。建议先做：

### Scale A: Input Integrity

- 检查输入字段是否足够
- 检查 claims 是否越界
- 检查素材是否有最基本映射

### Scale B: Structure & Mobile Safety

- 检查 section plan 是否符合单列移动端逻辑
- 检查最终 HTML 是否只用了允许标签
- 检查是否出现桌面宽图偏置

### Scale C: Media And Layout Review

- 表格
- 外链图源
- YouTube embed

GIF 在详情 HTML 中可以接受，不作为默认风险；只有无意义、过多、或影响手机端阅读时才提示。其他项不是直接 fail，而是输出风险说明。

## 7. 当前 mock 已经覆盖的部分

当前 mock 目录：

- [README.md](/Users/cc/Desktop/photo_show/experiments/20260523_emag_detail_mock/README.md)

已经证明：

- `product input -> DetailSectionPlan -> renderer -> HTML snippet -> validator`

这条链可跑通。

## 8. 当前还没做满的部分

- 还没有正式的 Skill body / Agent profile
- 还没有标准化 eval cases
- 还没有真实浏览器预览自动截图证据
- 还没有把 renderer 收敛成真正面向 eMAG 最终贴入的版本

## 9. 一句结论

对这个方向来说，最重要的不是“写一个更聪明的 prompt”，而是：

- 把输入和 section plan 结构固定下来
- 把合规和灰区检查从 prompt 挪到 validator / Scale
- 把剩下需要审美和策略判断的部分留给 Skill / SOP

## 10. 2026-05-24 V2：从“可显示”升级到“可转化”

本轮基于 BestPlaza / shanggvu 风格截图和旧 live HTML 样本，Scale 需要新增一层：不只判断 HTML 能否渲染，还要判断每个模块是否回答了一个明确购买疑虑。

新增机器可读模块目录：

- [emag_detail_module_catalog.v2.json](/Users/cc/Desktop/photo_show/workflow/emag_detail_module_catalog.v2.json)

### 10.1 新增 Scale D: Conversion Module Fit

检查对象：`DetailSectionPlan`、模块目录、最终 HTML / 图片板。

建议检查项：

- 每个 section 必须绑定一个 `module_id` 或明确标记为 legacy/simple。
- 每个模块必须有 `buyer_question`，且一个模块只回答一个问题。
- 顶部 1-2 个模块必须优先回答“买了以后得到什么结果”和“解决什么痛点”，不能先堆规格。
- FAQ 模块必须来自真实评论、真实问答、类目问题库，或明确标记为“待采集问题”；不能生成虚构实名评论。
- testimonial / star rating 模块只能使用真实 review 数据或汇总，不允许伪造客户、日期和评分。
- brand / platform trust banner 只能使用有来源的 seller/platform 服务事实；配送、退货、保修这类 claim 默认需要证据，否则只能做品牌好感和服务流程表达。

### 10.2 新增 Scale E: Visual Board Feasibility

检查对象：生成图片板、GIF、banner、HTML 嵌入方式。

建议检查项：

- eMAG 详情页生产优先生成 `1140px` 渲染宽度；`800px` 只作为移动端/旧模板 fallback。当前 shanggvu 样本中最常见渲染宽度是 `1140`。
- 品牌信任 GIF/banner 的常见源尺寸是 `1200x480`，渲染约 `1140x456`。
- 产品技术 Hero 可使用 `1280x366` 或 `1400x400` 源图，渲染约 `1140x326`。
- 每张图板只承载一个主信息层级：主标题、产品/场景、2-4 个证明点。
- 深色品牌 banner 可以使用，但正文模块不能整页都走黑底，否则移动端阅读负担会变重。
- 色块只能用于阅读顺序、分组和情绪锚点，不作为纯装饰。
- GIF 只用于动作证明、安装过程、前后对比、使用效果；无证明价值的动图应提示降级为静态图。

### 10.3 Skill / SOP 新增判断

这些仍不适合硬塞进 validator：

- 当前产品适合“情绪驱动 hero”还是“技术可信 hero”。
- 哪些痛点应该放进顶部三秒区，哪些应该放到 FAQ。
- 品牌实力是否需要真人 / 包裹 / 平台熟悉感，还是只需要轻量服务说明。
- 是否把用户评价图做成 testimonial，或因证据不足改成 FAQ / common objections。

### 10.4 App 版工具建议

模块选择工具应给操作员三个显式开关：

- `evidence_mode`: `strict_source_only` / `source_plus_category_qa` / `concept_preview`
- `output_mode`: `html_only` / `image_board` / `html_plus_image_boards`
- `review_usage`: `actual_only` / `summary_only` / `faq_instead`

这三个开关能避免一个核心风险：把“可以生成得像评价”的图片误用成“真实评价证据”。

## 11. 2026-05-24 V3：eMAG Banner / HTML 实证回写

本轮补充了真实抓取和 HTML 校验证据：

- 店铺采集：`references/user_cases/20260524_emag_shanggvu_detail_case_chrome/scrape_summary.json`
- Qoltec 技术 Hero：`references/user_cases/20260524_emag_qoltec_d978tdybm/target_summary.json`
- 官方首页素材：`references/emag_official_assets/20260524_homepage_banners/official_asset_manifest.json`
- CSS/HTML 校验：`experiments/20260524_emag_banner_css_validation/validation_report.json`
- eMAG 详情专用 Agent：`workflow/agent_flows/emag_detail_banner_agent_v1.md`

### 11.1 已验证 HTML 形式

`validate_emag_detail_html.py` 已验证以下片段 `status=pass`：

- `p style="text-align:center"` 包裹 `img width="1140"`
- GIF 作为详情页普通图片嵌入
- `table/tr/td` 做浅色块和规格表
- 内联 `padding/background-color/text-align`
- 纯文本 FAQ / buyer-question 模块

validator 对 GIF、table、外链 host、1140 桌面宽图给 warning，不直接 fail。生产时这些 warning 必须进入 ReviewLog，并说明使用理由。

### 11.2 Banner 类型 Scale

新增三类 banner family：

- `premium_dark_brand_trust`：黑底、真人/包裹、3 个服务锚点。适合品牌熟悉感和卖家信任。
- `product_tech_context`：产品切图、技术背景、使用场景。适合 EV、工具、电子、检测类。
- `official_blue_people_category`：参考 eMAG 官方首页的蓝底、人物、类目卡片。只能作为风格参考，未确认授权前不能直接商用官方素材。

### 11.3 文案 Scale

新增文案判断：

- 顶部三秒区必须先讲“买了得到什么结果”，不能先讲参数。
- 问题型模块要替用户完成思考路径：疑问 -> 答案 -> 证据/场景。
- FAQ 可以从评论、问答、竞品差评、类目共性问题生成；但不得伪造实名评价、评分、日期。
- 服务类 claim 默认需要证据；没有证据时只能写品牌服务态度或流程，不写平台承诺。
