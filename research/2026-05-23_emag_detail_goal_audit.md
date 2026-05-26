# eMAG Detail Goal Audit

日期：2026-05-23  
工作目录：`/Users/cc/Desktop/photo_show`

## 1. 目标拆解

### Requirement A

查清 eMAG 官方对产品详情 HTML 和图片/描述的限制。

### Requirement B

抓取并保存至少 20 个 eMAG 样本产品的详情 HTML。

### Requirement C

基于样本总结可执行的结构限制与模板规律，为后续详情页模板生成和 Skill/Scale 化提供输入。

### Requirement D

不要把当前样本当唯一标准，要明确：

- 哪些是平台硬限制
- 哪些是卖家常见写法
- 哪些地方还有优化空间

### Requirement E

设计出几套模板框架，并用 mock 产品信息填进去看效果。

### Requirement F

总结更好的详情页 HTML SOP，并规划后续 Agent 工作流。

## 2. 当前证据

### A. 官方限制

证据文件：

- [2026-05-23_emag_detail_html_constraints_and_template_inputs.md](/Users/cc/Desktop/photo_show/research/2026-05-23_emag_detail_html_constraints_and_template_inputs.md)
- [2026-05-23_emag_detail_capability_matrix.md](/Users/cc/Desktop/photo_show/research/2026-05-23_emag_detail_capability_matrix.md)

结论：

- 已覆盖描述禁区、图片规则、HTML 示例、视频规则、主图/辅图规则与详情媒体规则的分离。

判定：

- `completed`

### B. 样本 HTML 抓取数量

证据目录：

- [/Users/cc/Desktop/photo_show/output/emag_detail_html_live_batch](/Users/cc/Desktop/photo_show/output/emag_detail_html_live_batch)
- [summary.md](/Users/cc/Desktop/photo_show/output/emag_detail_html_live_batch/summary.md)

当前样本量：

- `30` 个产品详情 HTML

判定：

- `completed`

### C. 结构限制与模板规律

证据文件：

- [summary.md](/Users/cc/Desktop/photo_show/output/emag_detail_html_live_batch/summary.md)
- [constraints_summary.md](/Users/cc/Desktop/photo_show/output/emag_detail_html_live_batch/constraints_summary.md)
- [analyze_emag_detail_html_constraints.py](/Users/cc/Desktop/photo_show/scripts/analyze_emag_detail_html_constraints.py)
- [2026-05-23_emag_detail_html_constraints_and_template_inputs.md](/Users/cc/Desktop/photo_show/research/2026-05-23_emag_detail_html_constraints_and_template_inputs.md)

结论：

- 已总结标签使用、GIF、桌面宽图偏置、单列流、表格灰区、移动端弹层承载方式。

判定：

- `completed`

### D. 样本不是唯一标准

证据文件：

- [2026-05-23_emag_detail_html_constraints_and_template_inputs.md](/Users/cc/Desktop/photo_show/research/2026-05-23_emag_detail_html_constraints_and_template_inputs.md)
- [2026-05-23_emag_detail_capability_matrix.md](/Users/cc/Desktop/photo_show/research/2026-05-23_emag_detail_capability_matrix.md)
- [sample_vs_mock_validator_comparison.md](/Users/cc/Desktop/photo_show/experiments/20260523_emag_detail_mock/sample_vs_mock_validator_comparison.md)

结论：

- 已显式拆出“硬限制 / 卖家习惯 / 优化空间”
- 已用 mock 证明可以比真实样本更受控、更少灰区依赖

判定：

- `completed`

### E. 模板框架 + mock 产品

证据文件：

- [mock_ev_cable_detail_gallery.html](/Users/cc/Desktop/photo_show/experiments/20260523_emag_detail_mock/mock_ev_cable_detail_gallery.html)
- [mock_product_ev_cable.json](/Users/cc/Desktop/photo_show/experiments/20260523_emag_detail_mock/mock_product_ev_cable.json)
- [detail_section_plan_ev_cable.json](/Users/cc/Desktop/photo_show/experiments/20260523_emag_detail_mock/detail_section_plan_ev_cable.json)
- [rendered_minimal_clean.html](/Users/cc/Desktop/photo_show/experiments/20260523_emag_detail_mock/rendered_minimal_clean.html)
- [rendered_dense_feature.html](/Users/cc/Desktop/photo_show/experiments/20260523_emag_detail_mock/rendered_dense_feature.html)
- [rendered_spec_first.html](/Users/cc/Desktop/photo_show/experiments/20260523_emag_detail_mock/rendered_spec_first.html)

结论：

- 已形成 3 套 detail template family
- 已用真实类目 mock 产品跑出可读 HTML

判定：

- `completed`

### F. SOP + Agent workflow

证据文件：

- [2026-05-23_emag_detail_generation_workflow_draft.md](/Users/cc/Desktop/photo_show/research/2026-05-23_emag_detail_generation_workflow_draft.md)
- [EMAG_DETAIL_SCALE_CONTRACT.md](/Users/cc/Desktop/photo_show/workflow/EMAG_DETAIL_SCALE_CONTRACT.md)
- [emag_detail_product_input.schema.json](/Users/cc/Desktop/photo_show/workflow/schemas/emag_detail_product_input.schema.json)
- [emag_detail_section_plan.schema.json](/Users/cc/Desktop/photo_show/workflow/schemas/emag_detail_section_plan.schema.json)

结论：

- 已给出更清晰的 SOP
- 已给出 Agent/Scale 化工作流
- 已拆出输入 schema、section-plan schema、renderer、validator 边界

判定：

- `completed`

## 3. 额外验证

### 生成链路

证据文件：

- [render_emag_detail_from_plan.py](/Users/cc/Desktop/photo_show/scripts/render_emag_detail_from_plan.py)
- [validate_emag_detail_artifacts.py](/Users/cc/Desktop/photo_show/scripts/validate_emag_detail_artifacts.py)
- [validate_emag_detail_html.py](/Users/cc/Desktop/photo_show/scripts/validate_emag_detail_html.py)
- [artifact_validation_report.json](/Users/cc/Desktop/photo_show/experiments/20260523_emag_detail_mock/artifact_validation_report.json)
- [validator_report_rendered_dense_feature_v2.json](/Users/cc/Desktop/photo_show/experiments/20260523_emag_detail_mock/validator_report_rendered_dense_feature_v2.json)

结论：

- `product input -> section plan -> rendered html -> validator`
  已跑通。

## 4. 总判定

以“前置研究 + 模板输入 + mock 验证 + Skill/Scale 输入”这个目标范围来看，当前证据已经覆盖原始要求。

当前没有完成的事情主要是：

- 把它正式接入 Agent Platform
- 把 renderer/validator 做到生产级
- 做真实浏览器自动预览截图

这些属于下一阶段实现工作，不属于本轮“前置研究”目标的必需条件。

最终判定：

- `goal complete`
