# G1：参考图 → 生图 Workflow V1（P0）

日期：2026-07-30
状态：待实施
设计依据：`docs/REFERENCE_TO_IMAGE_GENERATION_V1_DESIGN.md`（同仓库；
附录 A 含 2026-07-11 成功案例的 9 步完整原始 Prompt，实施前必读）
上游合同：`/Users/cc/Desktop/photo_show_ozon_workflow_v1/docs/OZON_REFERENCE_WORKFLOW_V1.md`

本 SPEC 是自包含的：实施者只需要本文件 + 上面两份文档 + 本仓库代码，
不需要任何对话上下文。

---

## 1. 背景与证据（先读，不要跳过）

- 上游「Ozon 参考图 Workflow V1」已定型：从用户产品图+信息出发，最终
  `export_selected_reference.py` 导出一张 wc1000 高清参考图（~750×1000，3:4）
  和同名 metadata JSON（含 `claim_warnings`：参考图上的参数文案未经验证，
  生成层必须替换）。本任务建设的就是消费这个导出物的**生成层**。
- 唯一被用户验收过的高质量生成路径是 2026-07-11 的一次 Codex 交互任务
  （ID `019f5020-a106-7752-bb23-c4c7207711ca`）：暖色厨师版经 8 步收敛、
  紫灰信息图版在暖色收敛完成后**单步**生成。两张图是本任务的质量标杆，
  原图在 `~/.codex/generated_images/019f5020-a106-7752-bb23-c4c7207711ca/`
  （暖色终版 `exec-8ba8669f-…png`、紫灰终版 `exec-9bf2138e-…png`）。
- 历史上失败过三轮（合同 Prompt 倾倒、组件 JSON 注入、产品图裁剪预处理），
  共同根因：中间层在两张原图与生成器之间增删了视觉信息，或引入了多重
  视觉权威。这些做法已被冻结禁止（见 §2）。

## 2. 冻结决策（实施时的硬约束，任何一条都不许为了"跑通"而放宽）

- **R1 角色声明**：每张输入图必须在 Prompt 中声明权威角色
  （design master / product appearance anchor / accessories evidence /
  module inspiration）。图片顺序不是合同的一部分，禁止用顺序编码语义。
- **R2 禁增删视觉信息**：输入图与生成器之间不允许任何裁剪、抠图、拼接、
  组件化预处理。管线只做整图 decode → resample（记录前后尺寸）。
- **R3 锁定事实清单**：目标语言文案白名单一次编译（来自 truth_pack），
  之后**每一轮 Prompt 逐字完整重复**；参考图上的可见文案一律视为待替换。
- **R4 单变量迭代**：收敛循环每轮只修一个主要问题；上一轮输出是下一轮
  **唯一的画布输入**。修补轮 Prompt 永远以 "Edit this existing image"
  开头，禁止 "Create"。
- **R5 比例重排不裁剪**：目标画布是一等参数（与参考图比例无关）；比例
  修正必须是独立的 recompose 轮，Prompt 声明 re-layout、禁止 crop。
- **R6 负面约束逐轮重复**：no donor brand / no donor language script /
  no warranty / no price / no certifications / no testimonials /
  no fake logos / no unsupported claims / no watermark。
- **R7 原生文字豁免**：产品机身丝印（如 VACUUM SEALER / PULSE / SEAL）
  不因不在营销白名单而判失败；审核时与营销文案分开两个清单。
- **R8 判官受限**：判官只能从 repair menu（§7）选一项 + 写一段增量；
  不得改写锁定事实清单、不得引入新的视觉权威、不得输出完整 Prompt。
- **R9 轮次预算**：默认 8 轮（不含 round_00 首生成），耗尽转
  `needs_manual` 状态并停止，不放宽标准换产出。
- **R10 人工确认**：V1 每轮必须人工确认（approve / 换修补方向 / abort）；
  `review_mode=auto` 禁用。人工决定必须落盘（未来判官校准的标签）。
- **R11 锚图复用**：风格迁移（§5.5）必须以已收敛锚图为外观权威；禁止
  拿新参考图从头收敛（除非请求里显式 `force_full_convergence=true`）。
- **R12 产物不可变**：每轮一个目录，prompt、输入清单、候选图、判官输出、
  人工决定全部落盘；重跑换新目录，禁止原地覆盖。
- **R13 单一视觉权威原则**：Prompt 长度不是问题，多重权威才是问题。
  Prompt 中只允许出现 §5.2 定义的六个段；组件目录、评审合同、lineage、
  IntrinsicPlan 等任何其他结构化内容禁止进入 Prompt。

## 3. 目标形态：workflow 状态机 + 有界收敛循环（不是自由 Agent）

一个 Python runner（参照上游 `run_ozon_reference_selection.py` 的风格：
CLI 子命令、串行执行、产物即审计记录），状态机如下：

```
queued
  -> compiling          (编译锁定事实清单 / 设计简报 / 首轮 prompt)
  -> generating_initial (round_00, 必要时 round_01 recompose)
  -> awaiting_round_review  <--+
  -> repairing (judge + 生图)  |   每轮循环, 预算 8
  ------------------------------+
  -> converged   (人工 approve, 终图存为锚图)
  -> needs_manual(预算耗尽或人工 abort)

converged 之后可反复调用:
  style-transfer (单步) -> awaiting_transfer_review -> transfer_done
```

大模型只出现在**四个**固定节点，全部为单次调用、限定输出 schema：

| 节点 | 做什么 | 输入 | 输出 |
|---|---|---|---|
| 设计简报器 | 把参考图转成结构化设计描述 | 参考图 + 产品信息 | `reference_design_brief.json` |
| 产品外观描述器 | 从白底图提取不可变外观特征 | 产品图（1-3张） | `immutable_traits.json` |
| **文案编译器** | 把产品信息编译成目标语言的槽位文案 | **只有产品信息文本，不看任何图** | `locked_fact_list` 草稿 |
| 修补判官 | 看当前候选图选修补方向 | 候选图+参考图+事实清单+menu | `judge_decision.json` |

**修订说明（2026-07-30；本条冻结决策由「三个」改为「四个」）**

原文定为三个节点时，没有核对 2026-07-11 成功链里模型实际做了几件事。回查会话
记录（`~/.codex/sessions/2026/07/11/rollout-...019f5020....jsonl`）发现：操作者
当时只给了 Ozon 商品标题原文 +「不需要把所有信息都放上去，因为这是主图」+
「请用罗马尼亚语输出」，**那 9 条罗语槽位文案是模型自己编译的**。把这件事退回
人工手填，等于重做模型已经做好的工作。附录 A 只收录了 Prompt 文本、没记录文案
的出处，这是当初漏查的点。

文案编译器的两条硬约束：

1. **不看任何图**（连参考图都不给）——唯一信息源是操作者提供的产品信息，
   从物理上杜绝把 donor 的声明抄进我方文案；
2. 输出后由确定性代码 `verify_numbers_traceable()` 逐个数字回查产品信息，
   查不到就**拒绝冻结**（`UntraceableNumber`）。依据是 2026-07-11 的真实事故：
   操作者自己在追加指令里打成 "70 kPa"（实为 75 kPa），错误进了图，后来只能用
   一句事实防守去纠。**人工撰写本身并不保证正确，机械校验才保证。**

编译器还负责排版规范化（`75kpa` → `75 kPa`，只改字体排印不改数值）与
「headline 用品类名、不重复已有槽位的数字」——这两条都是 2026-07-30 实测
逐条补出来的。

其余全部是确定性代码：Prompt 模板编译、生图调用、落盘、状态迁移、预算。

## 4. 输入合同与产物目录

### 4.1 `generation_request.json`

```json
{
  "product_id": "p-20260730-001",
  "selected_reference": {
    "image": "/abs/path/exports/<job_id>/产品__候选.jpg",
    "metadata": "/abs/path/exports/<job_id>/产品__候选.json"
  },
  "product_truth": "/abs/path/runs/<job_id>/<product_id>/01_product_analysis/truth_pack.json",
  "product_images": [
    {"path": "/abs/host_white_bg.png",        "role": "product_appearance_anchor"},
    {"path": "/abs/accessories_white_bg.png", "role": "accessories_evidence"},
    {"path": "/abs/original_poster.jpg",      "role": "native_text_evidence", "optional": true}
  ],
  "intent": {
    "canvas": "1:1",
    "output_px": 1600,
    "language": "ro",
    "marketplace_profile": "ozon_wb"
  },
  "round_budget": 8,
  "review_mode": "required"
}
```

约束：

- `product_images` 1-3 张，`product_appearance_anchor` 必须恰好 1 张；
- `expected_offer=host_with_accessories`（读 truth_pack）而无
  `accessories_evidence` 图时：允许进入，但 `complete_accessories` 修补轮
  必须挂 `native_text_evidence` 图或报 `needs_user_input`，**禁止让模型
  脑补配件形态**；
- truth_pack 缺核心参数（品牌/品名/主参数任一为空）→ 直接终态
  `incomplete_truth`，不进生成。

### 4.2 产物目录（每轮不可变）

```
generation_runs/<job_id>/<product_id>/
  request/generation_request.json          # 原样快照
  compiled/
    locked_fact_list.json                  # §5.1
    immutable_traits.json                  # §5.1
    reference_design_brief.json            # §5.1
    negative_constraints.json              # R6 固定内容 + donor 特化
  round_00_initial/
    prompt.md  inputs.json  candidate.png  candidate_meta.json
  round_01_recompose/                      # 仅当首轮比例不达标
    ...
  round_NN_<repair_type>/
    prompt.md  inputs.json  candidate.png
    judge_decision.json  human_decision.json
  anchor/anchor.png  anchor/anchor_meta.json
  style_transfers/<ref_id>/
    prompt.md  inputs.json  candidate.png  human_decision.json
  state.json                               # 状态机当前态 + 轮次账本
```

`candidate_meta.json` 记录：后端返回原始尺寸、resample 后尺寸、耗时、
后端标识。

## 5. Prompt 编译器（本任务的核心）

### 5.1 三个编译产物

**`locked_fact_list.json`** —— 从 truth_pack + 请求标题编译，目标语言：

```json
{
  "language": "ro",
  "copy_slots": [
    {"slot": "brand",           "text": "EXCITAT"},
    {"slot": "headline",        "text": "APARAT DE VIDAT"},
    {"slot": "badge",           "text": "6 ÎN 1"},
    {"slot": "supporting_line", "text": "PENTRU PRODUSE USCATE ȘI UMEDE"},
    {"slot": "spec_primary",    "text": "75 kPa"},
    {"slot": "spec_secondary",  "text": "120 W"},
    {"slot": "offer",           "text": "100 DE PUNGI INCLUSE"},
    {"slot": "feature",         "text": "BARĂ DE SIGILARE DE 30 cm"},
    {"slot": "feature_optional","text": "CUTTER ÎNCORPORAT • STERILIZARE UV"}
  ],
  "native_product_text": ["VACUUM SEALER", "PULSE", "SEAL", "VAC"],
  "must_replace_from_reference": ["…从上游 metadata 的 claim_warnings 逐条搬入…"]
}
```

编译规则：一次编译、人工可改（编译后允许用户在开始前修订一次）、开始后
冻结；`native_product_text` 单列（R7）。

**`immutable_traits.json`** —— 产品外观描述器对
`product_appearance_anchor`（+可选 accessories 图）做一次多模态调用：

```json
{
  "product_visual_traits": [
    "black-and-silver body", "rounded rectangular shape",
    "top control panel with touch buttons", "black locking bar",
    "realistic proportions"
  ],
  "accessories": [
    "stack of clear vacuum sealer bags",
    "external vacuum hose with connector"
  ]
}
```

这是「产品稳定性」的第一道机制：这些短语会逐字进入每一轮 Prompt 的
角色声明段（成功案例证明枚举具体特征比笼统说 keep the product 有效）。

**`reference_design_brief.json`** —— 设计简报器对参考图做一次多模态调用：

```json
{
  "aspect_ratio": "3:4",
  "layout_skeleton": "vertical hero: headline top-left, product lower half on wooden counter, person upper-right",
  "modules": [
    {"module": "headline_block", "position": "upper-left", "keep": true},
    {"module": "spec_badges",    "position": "mid-left",   "keep": true},
    {"module": "person",         "position": "upper-right","keep": true},
    {"module": "product_stage",  "position": "lower half", "keep": true, "replace_content": true}
  ],
  "color_mood": "warm premium kitchen, brown/orange, soft blur",
  "composition_notes": "product angled in perspective; sealed bag emerging from machine",
  "donor_brand": "Bellwell",
  "donor_language": "Russian/Cyrillic",
  "visible_claims_on_reference": ["…", "…"]
}
```

**「怎么借鉴参考图」的答案就在这里**：参考图以两种形态同时进入生成——
① 作为图片输入（design master 角色声明）；② 其设计语法被简报器重述成
文字进入 Prompt 的场景段，并声明哪些模块保留骨架、哪些替换内容。
只丢图不重述，模型对"模仿什么"没有约束；只重述不丢图，设计细节丢失。
两者都要。

### 5.2 INIT 模板（round_00，六段式）

模板变量用 `{{...}}` 表示；六段顺序固定；除这六段外禁止任何内容（R13）。
Prompt 用英语（成功链全部为英语，文案白名单保持目标语言原文）。

```text
[1 任务与画布]
Create a polished e-commerce main product image in {{canvas}} format for the
{{brand}} {{product_short_name}}.

[2 角色声明——每张输入图一段]
Use the {{ref_ordinal}} reference image as the design master: follow its
{{layout_skeleton}}, visual hierarchy, and commercial advertising style.
Do not use its product, its "{{donor_brand}}" branding, or any
{{donor_language}} text.
Use the {{anchor_ordinal}} reference image as the authoritative source for
the product appearance: keep the exact {{product_visual_traits, 逗号连接}}.
Do not redesign the product.
{{#accessories_evidence}}Use the {{acc_ordinal}} reference image as evidence
for the included accessories: {{accessories, 逗号连接}}. The accessories must
look like included items, not random props.{{/accessories_evidence}}

[3 场景与构图——由 design brief 编译]
Scene and composition: {{color_mood}}. {{composition_notes}}.
{{#modules}}{{module}} at {{position}}{{#replace_content}} (replace its
content with our product){{/replace_content}}. {{/modules}}
Keep the product itself as the largest sharp foreground object, with enough
negative space for readable copy.

[4 锁定事实清单——逐字，全部轮次相同]
Use {{language_name}} text only, correctly spelled with correct diacritics,
no {{donor_language}}. Use exactly these concise product claims:
{{#copy_slots}}- {{slot}}: {{text}}
{{/copy_slots}}

[5 负面约束——逐字，全部轮次相同]
Do not add warranty, certifications, testimonials, prices, fake logos, or
unsupported claims. Do not add any text not listed above, except text that is
natively printed on the product body itself. No watermark.

[6 质量收尾]
Final output: a single finished {{canvas}} e-commerce advertising image, high
resolution, realistic product photography, premium lighting, crisp legible
typography, clean high-conversion marketplace hero layout.
```

### 5.3 RECOMPOSE 模板（round_01，仅当首轮比例/画布不达标）

输入图只有上一轮输出。结构：

```text
Recompose this exact finished e-commerce image into a true {{canvas}} format.
Preserve the same product ({{product_visual_traits}}), scene, style, and all
existing {{language_name}} text. Do not change the product or invent new
claims. Re-layout the elements so no important text or product is cropped.
[段4 锁定事实清单逐字] [段5 负面约束逐字]
Balanced {{canvas}} composition for a marketplace main image, high-resolution
realistic commercial photography, no watermark.
```

### 5.4 REPAIR 模板（round_02..N）

输入图 = 上一轮输出（唯一画布）+ 修补类型允许的附加图（见 §7 表）。

```text
[1 编辑声明 + 保留清单]
Edit this existing {{canvas}} image. {{#approved_modules}}The
{{module_name}} is already approved and must remain essentially
unchanged.{{/approved_modules}} Preserve the exact product
({{product_visual_traits}}), the overall layout, and all existing
{{language_name}} text except as instructed below.

[2 修补指令——判官的 prompt_delta 原文放入, 仅此一处是每轮可变的]
{{prompt_delta}}

[3 事实防守——仅当判官报 fact_violations 时插入]
{{#fact_violations}}Do not use {{wrong_value}}: the authoritative source
says {{correct_value}}.{{/fact_violations}}

[段4 锁定事实清单逐字] [段5 负面约束逐字]
[6] Keep {{canvas}} format, crisp typography, no watermark, no element cropped.
```

保留清单规则（产品稳定性第二道机制）：人工在轮评审里 approve 过的模块
（如"配件组合已通过"）写入 `state.json.approved_modules`，此后每轮
自动进入段 1（成功案例第 7 步的 "already approved and must remain
essentially unchanged" 就是这个机制的手工版）。

### 5.5 STYLE_TRANSFER 模板（锚图单步风格迁移）

输入图固定三张：新参考图（design master）、锚图（appearance anchor）、
白底产品图（facts 旁证）。结构 = INIT 六段式，但段 2 的外观权威声明
指向锚图 + 白底图，段 3 用**新参考图**的 design brief 编译。
不进入收敛循环：生成一次 → 人工确认（approve / 重掷一次 / abort），
最多重掷 2 次。

### 5.6 产品稳定性机制汇总（回答"怎么保证产品和小细节"）

| # | 机制 | 落点 |
|---|---|---|
| 1 | 不可变特征枚举：具体外观短语逐轮进 Prompt | `immutable_traits.json` → 段2/段1 |
| 2 | 固定禁令句："Do not redesign the product / do not crop its ends" | 模板固定文本 |
| 3 | 画布链：上一轮输出是唯一画布，修补轮禁止 Create | R4 + REPAIR 模板 |
| 4 | 保留清单累积：已通过模块显式声明不动 | `approved_modules` |
| 5 | 事实防守：判官发现数值漂移，下一轮 Prompt 显式钉死 | `fact_violations` |
| 6 | 文案白名单逐字重复，杜绝文字漂移 | R3 |
| 7 | 原生丝印豁免清单，避免误杀 | R7 + `native_product_text` |
| 8 | 锚图：收敛成果固化为外观权威，迁移不重新收敛 | R11 |
| 9 | 整图输入，禁止任何裁剪/抠图预处理 | R2 |

## 6. 生图后端适配器（Codex）

实现 `scripts/imagegen_codex_adapter.py`，接口：

```python
def generate(prompt: str, image_paths: list[str], out_png: str,
             timeout_s: int = 300) -> dict:  # 返回 candidate_meta
```

- **接线方式（2026-07-30 在本机实测钉死，codex-cli 0.144.4，勿再猜）**：

  ```
  codex exec --json --skip-git-repo-check -C <workdir> -i <img1> -i <img2> ...
  # prompt 走 stdin（-i 会吃掉位置参数，和 codex_match_judge.py 同构）
  ```

  1. 前置条件：`$CODEX_HOME/config.toml` 里 `[features] image_generation = true`
     （本机已开）。缺这一项则模型不会有生图工具。
  2. `--json` 输出 JSONL，**第一条**事件是
     `{"type":"thread.started","thread_id":"<uuid>"}`，这个 `thread_id`
     是定位产物的唯一可靠钩子。
  3. 产物落在 `$CODEX_HOME/generated_images/<thread_id>/<name>.png`。
     **文件名不稳定**：实测既出现过 `call_<call_id>.png` 也出现过
     `exec-<uuid>.png`。因此**禁止按文件名匹配**，只能扫 thread 目录取
     最新 PNG（适配器已按此实现，并保留「按 mtime 扫全目录」兜底）。
  4. **生图工具调用不产生 `item.*` 事件**——事件流里看不到它。不要试图
     解析工具调用事件来拿路径，只能落盘扫描。
  5. 需要一段**机械包装词**告诉 agent「调一次生图工具、把这几个路径当
     参考图、把下面这段 prompt 原文照传」。包装词是
     `imagegen_codex_adapter.WRAPPER_TEMPLATE`，**必须零视觉信息**
     （R13：视觉权威只能来自六段式 prompt），测试对此有断言。
     同时用 `-i` 附图（给视觉上下文）并在包装词里列出绝对路径（给工具
     的 `referenced_image_paths`），两者顺序必须一致（prompt 里的
     FIRST/SECOND 序数依赖它）。
  6. 实测耗时：单次首生成约 220 秒。`timeout_s` 默认给 600 以上。
  7. macOS 上**没有 `timeout` 命令**（也没有 `gtimeout`），超时必须用
     Python `subprocess` 的 `timeout=`，不要写 shell `timeout`。

  §10.1 复刻冒烟已于 2026-07-30 通过（见 `docs/G1_ACCEPTANCE_20260730.md`），
  适配器可以接入 runner。
- 适配器职责边界：调用、取回 PNG、整图 resample 到 `output_px`（记录
  前后尺寸）、写 `candidate_meta.json`。不做任何其他图像处理（R2）。
- **resample 语义澄清（实施期定，避免与 R2/R5 冲突）**：resample 是
  「长边缩放到 `output_px`，**等比**」。后端返回的比例与目标画布不一致时
  **不许拉伸、不许裁剪**去凑——比例不达标是 RECOMPOSE 轮（§5.3）的职责，
  由重新生成解决（R5）。适配器只在 meta 里记录实测 `aspect_ratio`，
  由 runner 判定是否需要 recompose 轮。`output_px=0` 表示保留后端原分辨率
  （复刻冒烟用，便于与当年产物同分辨率比对）。
- 失败重试：同参数最多重试 2 次，仍失败则该轮标 `backend_error`，
  状态回 `awaiting_round_review`，不消耗修补预算。

判官与两个描述器同样走 `codex exec` 多模态调用（或 Claude API，二选一，
实现处留 provider 参数），输出用 `--output-schema` 钉死 JSON。

**`--output-schema` 的硬约束（2026-07-30 实测踩坑，三个 schema 全被拒）**：

1. **每一层 `properties` 的每个 key 都必须出现在同层 `required` 里**，否则
   API 直接拒绝整个 schema：
   `'required' is required to be supplied and to be an array including every
   key in properties. Missing '<key>'`。
   「可选字段」只能表达成**必填但可为空**（返回 `[]` / `""`），不能省略。
   嵌套对象（如 brief 的 `modules[].*`）同样受约束，容易漏。
2. schema 被拒时 `codex exec` **不写 `-o` 的 last-message 文件**，报错只出现在
   stdout/stderr。所以 schema 失败时必须把 rc/stderr/stdout 一起记进样本，
   否则 §11 停止条件 3 的「连续 3 次 schema 失败」拿到的是三个空字符串，
   完全无法诊断（本次就先踩了这个坑）。
3. `minItems` / `minimum` / `maximum` 实测可用（沿用
   `references/.../eval/judge_schema.json` 的既有约定）。

## 7. 判官合同与 repair menu

判官输入：当前候选图、参考图、`locked_fact_list.json`、
`immutable_traits.json`、repair menu、已用轮次/预算。输出 schema：

```json
{
  "repair": "amplify_spec_impact",
  "prompt_delta": "一段 60-180 词的英文修补指令, 只描述这一个问题怎么改",
  "fact_violations": [{"wrong_value": "70 kPa", "correct_value": "75 kPa"}],
  "product_integrity_ok": true,
  "stop_recommended": false,
  "reason": "一句话"
}
```

Repair menu（判官只能选其一；「允许附加图」列之外禁止加图）：

| repair_type | 修什么 | 允许附加图 |
|---|---|---|
| recompose_aspect | 画布/比例重排（重排不裁剪） | 无 |
| complete_accessories | 补齐配件证据 | accessories_evidence 或 native_text_evidence |
| increase_product_dominance | 产品视觉权重（居中/放大/去竞争） | 无 |
| amplify_spec_impact | 核心参数冲击力（大小/对比/位置） | 无 |
| redesign_accessory_module | 配件模块设计语言 | 1 张模块级灵感图（人工提供） |
| redesign_spec_module | 参数模块设计语言 | 1 张模块级灵感图（人工提供） |
| add_breathing_room | 留白/呼吸感/清透度 | 无 |
| fix_text_error | 文字拼写/语言错误 | 无 |
| replace_claim_text | 残留参考图文案替换 | 无 |
| reduce_clutter | 信息过载消减 | 无 |

`product_integrity_ok=false`（产品外形被改）时：本轮不算修补，直接用
REPAIR 模板 + 固定 delta（restore the exact product appearance …
per traits）重生成，且此情形优先于判官所选 repair。

V1 判官只做**预填**：其输出展示给人工，人工可改选 repair 类型后才执行
（R10）。人工每次选择（含推翻判官）写入 `human_decision.json`。

## 8. 实施阶段与最小 diff

全部新增文件，不改上游任何管线代码：

| 阶段 | 交付 | 依赖 |
|---|---|---|
| P0 复刻冒烟 | 适配器 + §10.1 通过 | 无 |
| P1 编译器 | locked_fact_list / immutable_traits / design brief / 四个模板 | P0 |
| P2 runner 骨架 | `scripts/run_reference_generation.py`（子命令：run / review / approve / repair / abort / style-transfer / status）+ 状态机 + 产物目录 | P1 |
| P3 收敛循环 | 判官 + repair 轮 + 保留清单 + 预算 | P2 |
| P4 风格迁移 | anchor + style-transfer 子命令 | P3 |

建议落点：本仓库（`/Users/cc/Desktop/photo_show`）新建
`workflow/reference_generation/`（编译器、模板、状态机）+
`scripts/run_reference_generation.py`（CLI）+
`scripts/imagegen_codex_adapter.py`。

## 9. 测试要求（离线，pytest，不调真实后端）

`tests/test_reference_generation_compiler.py` 至少覆盖：

1. 任意轮编译出的 Prompt 中，锁定事实清单每个 `text` **逐字**出现，
   负面约束段逐字出现（R3/R6 的机械保证）；
2. 每张输入图都有对应角色声明段；`product_appearance_anchor` 缺失或
   多于 1 张时编译报错（R1）；
3. REPAIR 轮 Prompt 以 "Edit this existing" 开头且输入图含上一轮输出
   （R4）；INIT 之外任何轮不含 "Create"；
4. `approved_modules` 非空时保留清单段出现在 Prompt 中；
5. `fact_violations` 注入生成 "Do not use … says …" 句式；
6. repair menu 之外的 repair 值被拒绝；附加图超出 §7 允许列被拒绝（R8）;
7. truth_pack 缺核心参数 → `incomplete_truth` 终态（§4.1）；
8. 预算耗尽 → `needs_manual`，不再产生新轮目录（R9）；
9. 状态机非法迁移（如 converged 后再 repair）被拒绝；
10. 适配器 mock：输出尺寸 ≠ `output_px` 时 resample 且 meta 记录两个尺寸；
    除 resample 外对图片字节零改动（R2 抽查：输入图 hash 传递）。

## 10. 在线验收（需要本机 Codex 生图可用；条件不满足则停下报告）

### 10.1 P0 复刻冒烟（先决门槛）—— ✅ 2026-07-30 已通过

结果：产品外形保真持平、9 项罗语文案全中且变音符正确、设计迁移持平；
复刻图比例 0.800（正好 4:5，即 prompt 要求值），当年基线漂到 0.75（3:4）。
判定「不明显更差」，停止条件 1 未触发。产物见
`artifacts/g1_p0_smoke/`（`candidate.png` / `board.png` / `candidate_meta.json`
/ `a1_original_prompt.txt`），报告见 `docs/G1_ACCEPTANCE_20260730.md`。


用设计文档附录 A.1 的**原始 Prompt 原文**和原始两张输入图：

- 产品海报：`/Users/cc/Desktop/photo_show_p0_0_contract_freeze/references/p0x_template_transfer/vacuum-sealer-product-source.jpg`
- 暖色参考：`/Users/cc/Desktop/photo_show_p0_0_contract_freeze/references/p0x_template_transfer/r2-warm-chef.jpg`

经适配器生成一张，与当年首生成
`~/.codex/generated_images/019f5020-a106-7752-bb23-c4c7207711ca/exec-ef89d9cc-cf1f-4e26-9d00-7436a2a0199d.png`
并排出对比板，人工三项评分（产品外形保真 / 文字正确 / 设计迁移完成度）。
**明显更差 → 停止并报告**（后端能力问题，中间层救不了，见停止条件）。

### 10.2 端到端收敛

真空封口机案例（复用上述素材 + 附录 A 的罗语事实清单构造
generation_request）：runner 从 request 跑到 `converged`，
轮数 ≤ 8，最终图人工评分不低于暖色终版 `exec-8ba8669f`。

### 10.3 风格迁移

用紫色参考图
`…/p0x_template_transfer/r1-purple-info.jpg`
对 10.2 的锚图执行 style-transfer，两次重掷内人工通过
（当年紫灰是一次通过，标杆 `exec-9bf2138e`）。

## 11. 停止条件（任一发生即停手报告，不许继续改）

1. §10.1 复刻冒烟明显差于 2026-07-11 原结果 → 报告"后端能力不足"，
   不得试图用更复杂 Prompt/中间层弥补；
2. 实现过程中发现需要对输入图做裁剪/抠图/拼接才能继续 → 停（违反 R2，
   方案本身要重议）；
3. 判官无法稳定输出合法 JSON（连续 3 次 schema 失败）→ 停，报告样本；
4. 任何一条冻结决策（§2）与实现细节冲突 → 停，报告冲突点，不自行放宽。

## 12. 交付物清单

- `workflow/reference_generation/`（编译器 + 模板 + 状态机 + schema）
- `scripts/run_reference_generation.py`
- `scripts/imagegen_codex_adapter.py`
- `tests/test_reference_generation_compiler.py`（§9 全绿）
- §10 三项在线验收的产物目录 + 对比板 + 一页验收报告
  （`docs/G1_ACCEPTANCE_<date>.md`，含每轮缩略图表格）

## 13. 明确不在范围（不要做）

- `review_mode=auto`（判官全自动收敛）——标签攒够前禁用；
- 套图（5-8 张 suite）规划与批量调度——G2；
- 确定性文字叠加 / PSD 分层导出；
- 网站 UI——本任务只交付 CLI 与 JSON 合同；
- 上游 Ozon 选图管线的任何改动；
- 新的图像预处理能力（哪怕"看起来无害"）。
