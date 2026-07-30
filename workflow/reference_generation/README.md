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

## 四个大模型节点

| 节点 | 何时跑 | 看图吗 | 产出 |
|---|---|---|---|
| 文案编译器 | 编译期一次 | **不看任何图** | `locked_fact_list` 草稿 |
| 产品外观描述器 | 编译期一次 | 产品图 | `immutable_traits.json` |
| 设计简报器 | 编译期一次 | 参考图 | `reference_design_brief.json` |
| 修补判官 | 每轮一次 | 候选图 | `judge_decision.json` |

每个都是单次调用、JSON Schema 钉死输出、不循环、不调工具。判官**只做预填**,
人不确认不执行。

**文案编译器不看任何图是刻意的**——它唯一的信息源是操作者给的产品信息,
从物理上杜绝把参考图上 donor 的声明抄进我方文案。

它写出来的每个数字都会被确定性代码 `verify_numbers_traceable()` 回查产品信息,
查不到就**拒绝冻结**。依据是 2026-07-11 的真实事故:操作者自己打错成 "70 kPa"
(产品实为 75 kPa),错误进了图。文案一旦冻结每轮照发,错一个数字毁的是整批图,
所以这道闸是机械的,不靠人细心。

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

## 文案怎么来

不给 `copy_slots` 时,文案编译器自动起草并继续跑。请求里给了 `copy_slots`
就用你给的,跳过这个节点。

停下来只有两种情况:

- 某个数字在产品信息里查不到(见上);
- 你自己加了 `--confirm-copy`,想先过目再生图。

## 已知缺口

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
