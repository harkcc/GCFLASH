# 请求样例:真空封口机(罗马尼亚语)

SPEC §10.2 端到端验收用的那一组输入。把 `/ABS/PATH/TO/...` 换成你的真实路径
即可作为模板。

- `generation_request.json` — 输入合同(SPEC §4.1)
- `truth_pack.json` — 上游 `run_product_truth_intake.py` 的产出形态
- `r2-warm-chef.metadata.json` — 上游 `export_selected_reference.py` 的产出形态,
  `claim_warnings` 是参考图上未经验证的声明,生成层必须替换

注意 `copy_slots`:目标语言的成品营销文案目前需要人工提供(见模块 README
的「已知缺口」)。这一组取自设计文档附录 A 的罗语事实清单。
