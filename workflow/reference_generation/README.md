# G1 参考图 → 生图 Workflow V1

消费上游「找图模块」导出的参考图,产出电商主图。**是 workflow 状态机,不是自由
Agent**——大模型只出现在三个固定节点,其余全是确定性代码。

- 规格:`tasks/G1_reference_generation_workflow_v1.md`(冻结决策 R1–R13 在 §2)
- 设计依据:`docs/REFERENCE_TO_IMAGE_GENERATION_V1_DESIGN.md`(附录 A 是 2026-07-11
  已验收成功链的 9 步原始 Prompt)
- 验收报告:`docs/G1_ACCEPTANCE_20260730.md`

## 在整条链路里的位置

```
【找图模块】
  run_product_truth_intake.py           → truth_pack.json
  run_ozon_reference_selection.py run   → 候选池 + 评审板
  ──── 人工闸 ① 筛参考图 ────
  run_ozon_reference_selection.py finalize
  export_selected_reference.py          → 参考图 + metadata
                                              ↓
【本模块 · 生图】
  run_reference_generation.py run       → 编译 + round_00
  ──── 人工闸 ② 逐轮确认 ────
  review → repair(循环)→ approve       → 锚图
  style-transfer                        → 风格变体
```

两道人工闸都是强制的。`review_mode=auto` 会被代码直接拒绝(R10)。

## 三个大模型节点

| 节点 | 何时跑 | 产出 | schema |
|---|---|---|---|
| 产品外观描述器 | 编译期一次 | `immutable_traits.json` | `schemas/immutable_traits.schema.json` |
| 设计简报器 | 编译期一次 | `reference_design_brief.json` | `schemas/reference_design_brief.schema.json` |
| 修补判官 | 每轮一次 | `judge_decision.json` | `schemas/judge_decision.schema.json` |

每个都是单次调用、JSON Schema 钉死输出、不循环、不调工具。判官**只做预填**,
人不确认不执行。

## 四个 Prompt 模板

`templates.py` 里的 `compile_init` / `compile_recompose` / `compile_repair` /
`compile_style_transfer`,全部确定性拼装。

锁定文案段和负面约束段**整个 job 只渲染一次**,然后原样塞进每一轮——所以
「逐轮逐字重复」(R3/R6)是代码属性而非自觉。`audit_prompt()` 在每次调后端前
再验一遍,模板回归会当场炸而不是悄悄降质。

## 怎么跑

```bash
python scripts/run_reference_generation.py run --request req.json
python scripts/run_reference_generation.py review --job <job_dir>
python scripts/run_reference_generation.py repair --job <job_dir> --from-judge
python scripts/run_reference_generation.py approve --job <job_dir>
python scripts/run_reference_generation.py style-transfer --job <job_dir> \
    --reference <new_ref.jpg> --ref-id purple
```

请求样例见 `examples/g1_vacuum_sealer/generation_request.json`。

### 前置条件

1. `codex` CLI 可用,且 `$CODEX_HOME/config.toml` 里
   `[features] image_generation = true`——**缺这条模型就没有生图工具**。
2. Python 3.12 + Pillow。
3. 单次生成实测 176–407 秒,`--timeout` 默认 900。

## 已知缺口

- **目标语言文案要手填**。`truth_pack` 存的是自由文本产品信息(`75 kPa`、
  `100 bags included`…),信息是全的,但转成目标语言成品槽位
  (`100 DE PUNGI INCLUSE`)这一步没自动化——SPEC §3 只允许三个大模型节点,
  里面没有文案撰写器。不给 `copy_slots` 时 runner 会起草一版然后停在
  `needs_user_input` 等你改(§5.1 的「人工改一次再冻结」)。
- **以下代码路径只有单元测试覆盖,没真跑过**:RECOMPOSE 轮(首轮比例正好命中
  就不会触发)、产品完整性强制修复轮、预算耗尽、配件证据缺失门禁、
  模块级灵感图挂载、`backend_error` 终态、`incomplete_truth` 终态、
  `approved_modules` 多轮累积。
- `provider="claude"` 是 SPEC §6 声明的接缝,目前显式 `NotImplementedError`,
  没有静默回退。

## 测试

```bash
python -m pytest tests/test_reference_generation_compiler.py \
                 tests/test_reference_generation_state.py -q
```

145 个,全离线,不调真实后端(一次生成约 220 秒的付费推理)。
