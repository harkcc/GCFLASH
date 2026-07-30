# 参考图 → 生图 Workflow V1 设计（衔接 Ozon 参考图 Workflow V1）

日期：2026-07-30
状态：设计稿，待评审
上游：`photo_show_ozon_workflow_v1` 的 `docs/OZON_REFERENCE_WORKFLOW_V1.md`（定型版）
实证依据：Codex 任务 `019f5020-a106-7752-bb23-c4c7207711ca`（2026-07-11）的完整
生图调用链，已从 61MB JSONL 中提取，全文见附录 A。

---

## 0. 结论先行

1. **不需要自由 Agent，做成「workflow 骨架 + 有界收敛循环」。**
   成功案例的全过程结构高度固定：首生成 → 比例重排 → N 轮单变量编辑 → 终审。
   每轮真正需要智能的只有两件事：看图选一种修补类型、把它措辞成一段短
   prompt 增量。这是 workflow 里嵌一个多模态判官节点就能覆盖的，不需要
   开放工具集的自主 Agent。当年失败的结构化实验，失败方向恰恰就是
   「给中间层过多自由度」。

2. **之前 PhotoRoom / Claude 拼接效果差，不是玄学，是七个可指认的差异。**
   见 §3。其中最重要的三个：缺少逐图角色声明、一次塞入所有规则而不是
   单变量迭代、上一轮输出没有作为下一轮的唯一画布输入。

3. **比例差异（参考图 3:4 vs 输出 1:1）当年就解决过**：专门一步
   「recompose 重排」，声明重排不裁剪不删模块。这要固化为硬规则 R5。

4. **紫灰图揭示了批量化杠杆**：暖色图收敛完成后，紫灰图是**单步**生成的
   （新参考 + 已收敛锚图 + 产品原图，三图三角色）。即：一个产品只需
   收敛一次得到「锚图」，之后每换一张参考风格都是单步操作。这是套图
   （5-8 张）成本模型的核心。

---

## 1. 衔接点：上游合同 → 生成层输入合同

上游 workflow 的终点（已定型，接口可依赖）：

```
export_selected_reference.py
  → 产品__候选.jpg          (wc1000 高清参考图, ~750×1000, 3:4)
  → 同名 metadata JSON      (含 claim_warnings: 参考图上的参数文案
                             未经 ProductTruth 验证，生成层必须替换)
```

生成层的输入合同（新增 `generation_request.json`）：

```json
{
  "product_id": "p-20260730-001",
  "selected_reference": {
    "image": "/path/to/exports/<job_id>/产品__候选.jpg",
    "metadata": "/path/to/exports/<job_id>/产品__候选.json"
  },
  "product_truth": "/path/to/runs/<job_id>/<product_id>/01_product_analysis/truth_pack.json",
  "product_images": [
    {"path": "/path/to/host_white_bg.png",        "role": "product_appearance_anchor"},
    {"path": "/path/to/accessories_white_bg.png", "role": "accessories_evidence"},
    {"path": "/path/to/original_poster.jpg",      "role": "native_text_evidence", "optional": true}
  ],
  "intent": {
    "canvas": "1:1",
    "output_px": 1600,
    "language": "ro",
    "marketplace_profile": "ozon_wb",
    "direction": "ozon_wb_main_card"
  },
  "round_budget": 8,
  "review_mode": "required"
}
```

要点：

- **三种权威分离**（这是对 2026-07-11 经验第 1 条的正式化）：
  - 事实权威 = `truth_pack.json` 编译出的锁定事实清单（不再依赖海报图上的文字）；
  - 外观权威 = 白底产品图（1-3 张，各带角色）；
  - 设计权威 = 上游选出的 Ozon 参考图。
- `claim_warnings` 是上游合同里明确要求生成层消费的字段——参考图上一切
  可见参数文案必须替换为锁定事实清单的内容。
- 输出画布 `canvas` 是一等参数，来自 marketplace profile，**永远不由参考图
  比例决定**。

## 2. 问题一：Agent 还是 Workflow？

### 判据：成功 trace 里，自由度到底用在了哪

附录 A 的 9 次生图调用显示，全过程只有两类步骤：

| 步骤类型 | 次数 | 决定者 | 自由度 |
|---|---|---|---|
| 结构固定步（首生成、比例重排） | 2 | 流程本身 | 零——prompt 由配方模板 + 锁定事实清单编译而成 |
| 单变量编辑步 | 6 | 人看图后指出「下一个要改的问题」 | 选修补类型 + 措辞一段增量 |
| 风格迁移步（紫灰） | 1 | 人 | 换设计权威图，其余照抄 |

也就是说：**需要智能的只有「看图 → 选修补类型 → 写增量」这一个节点**。
它可以是一次 Claude 多模态 API 调用（裁判层 Claude 所有，与 eval_gate
归属一致），输出限定为：

```json
{"repair": "<repair menu 中的一项>", "prompt_delta": "<一段话>", "stop": false}
```

其余全部是确定性代码：prompt 编译、生图后端调用、产物落盘、轮次控制、
预算与停止条件。这就是「workflow 骨架 + 有界收敛循环」。

### 为什么不做成自由 Agent

- 失败历史：过长合同 prompt、组件 JSON、多重视觉权威——都是「中间层
  自由发挥」的产物，冻结文档 §5 的常设规则就是为此立的；
- 可审计性：上游六阶段的产物即审计记录，生成层照搬这个模式（每轮落
  `round_NN/` 目录），自由 Agent 做不到产物可比对；
- 判官校准问题真实存在（锦标赛品味反转教训：终审偏好留白、惩罚信息
  密度，选中最弱参考图）。V1 每轮走人工确认，人工决定落盘成标签，
  攒够了再评估 `review_mode=auto`——与上游 finalize 的演进路径完全同构。

### 调用形态建议

- 骨架：Python runner（与 `run_ozon_reference_selection.py` 同构，
  串行 worker、异步任务、轮询状态）；
- 判官：Claude API（多模态，输入 = 当前候选图 + 参考图 + 锁定事实清单 +
  repair menu，输出 = 上述 JSON）。Claude CLI headless（`claude -p`）可作
  过渡实现，服务化后换 API；
- 生图后端：待 Phase 0 能力测试定（见 §4）。**不要**做成对话式 Agent 产品；
  网站侧只暴露「看图 → 点一个修补方向或通过」的确认界面。

## 3. 问题二：之前拼接链路效果差的七个原因

对照附录 A 与当时的失败批次，可指认的差异：

1. **缺少逐图角色声明。** 成功 prompt 每张输入图都有明确权威声明
   （"Use the FIRST reference as the authoritative source for the product…
   Do not redesign… do not use the Bellwell branding"）。拼接版只是把图
   按顺序丢进去。Batch 0.1 已证明顺序不是差异点，角色声明才是。
2. **一次塞入所有规则 vs 单变量迭代。** 成功链是 7 步，每步只改一个
   主要问题。一次性合同 prompt 造成多个视觉权威互相冲突。
3. **上一轮输出没有回灌。** 成功链每轮把上一步输出作为唯一画布输入
   （referenced_image），拼接版每次都从原图重新生成，前轮收敛全部丢失。
4. **锁定事实清单没有逐字重复。** 成功链 9 步 prompt 里罗马尼亚语文案
   白名单 + 负面约束（no Cyrillic / warranty / price / watermark /
   unsupported claims）每步完整重复，文字才不漂移。
5. **比例用裁剪而不是重排。** 成功链用专门一步 recompose（"Re-layout the
   elements so no important text or product is cropped"），拼接版让比例
   问题混在其他修改里或直接裁。
6. **后端能力未先验证。** 冻结文档 Step 1 明说：同输入同 prompt 下如果
   后端明显更差，那是模型能力问题，中间层工程救不了。PhotoRoom 是
   模板合成工具，本就不是多模态设计迁移模型。
7. **参考图分辨率。** 拼接实验期用的是缩略图级参考；上游现在导出的是
   wc1000 高清版，设计语法信息量完全不同。

## 4. 问题三：实施方案

### Phase 0 — 后端能力复刻测试（先决，未通过则停止）

用附录 A 的第 1 步 prompt + 相同两张输入图（产品海报 +
`r2-warm-chef.jpg`），在候选后端各跑一次：

- 候选：Codex CLI `image_gen`（原始成功环境）、GPT-image 直连 API、
  fal.ai 上的等价模型；
- 与 `exec-ef89d9cc`（当时的首生成结果）并排比对；
- 判据：产品外形保真、文字正确率、设计迁移完成度三项人工评分；
- 明显更差 → 换后端或停止，**不进入中间层工程**。

### Phase 1 — 合同与编译器（纯确定性代码）

1. 定义 `generation_request.json`（§1）与产物目录：

   ```
   generation_runs/<job_id>/<product_id>/
     request/generation_request.json
     compiled/locked_fact_list.json     # truth_pack → 目标语言文案白名单
     compiled/negative_constraints.json
     round_00_initial/    {prompt.md, inputs.json, candidate.png}
     round_01_recompose/  {...}
     round_NN_<repair>/   {..., judge_decision.json, human_decision.json}
     anchor/anchor.png                  # 收敛完成的锚图
     style_transfers/<ref_id>/          # 紫灰模式产物
   ```

2. 锁定事实清单编译器：`truth_pack.json` + 用户标题 → 目标语言的
   短文案清单（品牌、大标题、徽章、参数、配件），一次编译、全程逐字复用；
   同时消费上游 `claim_warnings` 生成「必须替换」列表。
3. Prompt 编译器：配方模板（首生成 / recompose / 各修补类型）+ 角色声明 +
   锁定事实清单 + 负面约束 → 完整 prompt。模板直接从附录 A 的真实
   prompt 提炼，不新造。

### Phase 2 — 结构固定步 runner

- `round_00_initial`：三权威图 + 首生成模板（附录 A 步 1 的结构，
  画布声明直接写目标 canvas，减少一次重排的概率）；
- `round_01_recompose`：若首生成比例不对，跑专门重排步（附录 A 步 2）；
- 分辨率由管线 decode → resample 强制并记录两个尺寸，不靠 prompt
  （沿用冻结文档 §2 的规则）。

### Phase 3 — 判官 + 有界收敛循环（人工确认版）

- Repair menu（从真实 trace + Stage 6 typed repairs 合并，判官只能选一项）：

  ```
  recompose_aspect            比例/画布重排
  complete_accessories        补齐配件证据（可临时加挂 accessories_evidence 图）
  increase_product_dominance  产品视觉权重（居中、放大、去竞争元素）
  amplify_spec_impact         核心参数冲击力（大小/对比/位置）
  redesign_accessory_module   配件表现形式（错落/丝带/悬浮层次，可注入模块级参考图）
  redesign_spec_module        参数模块设计语言（可注入模块级参考图）
  add_breathing_room          留白/呼吸感/清透度
  fix_text_error              文字拼写/语言错误
  replace_claim_text          残留参考图文案替换（claim_warnings 驱动）
  reduce_clutter              信息过载消减
  ```

- 每轮流程：判官出 `{repair, prompt_delta}` → 编译器生成完整 prompt
  （上轮输出为唯一画布 + 锁定清单 + 负面约束逐字重复）→ 生图 →
  **人工确认**（通过 / 换一个修补方向 / 终止）→ 落盘决定；
- `round_budget` 默认 8，耗尽未通过 → 状态 `needs_manual`，整链产物
  留作分析；
- 人工每轮的选择就是未来判官校准标签（同上游 `human_decision.json`
  的地位），必须落盘。

### Phase 4 — 锚图与风格迁移（批量化杠杆）

- 人工通过的最终图存为 `anchor/anchor.png`；
- 换参考风格 = 单步调用（紫灰模式）：新参考图（设计权威）+ 锚图
  （外观权威）+ 白底产品图（事实旁证）+ 一次性 prompt；
- 套图（5-8 张）成本模型：收敛循环只为第一张主图付费，其余各张
  = 上游选一张参考 + 一次风格迁移 + 一次人工确认。

### Phase 5 — 网站接口

与上游 job 模型同构：

```
POST /api/generation-jobs                 -> 写 generation_request.json, 入队
  worker(串行): run_generation            -> queued -> generating -> awaiting_round_review
GET  /api/generation-jobs/:id             -> 轮询 round 状态与当前候选图
POST /api/generation-jobs/:id/approve     -> 收敛, 存 anchor
POST /api/generation-jobs/:id/repair      -> {repair_type?} 人工可覆盖判官选择
POST /api/generation-jobs/:id/abort       -> needs_manual
POST /api/generation-jobs/:id/style-transfer -> {reference_export_path} 锚图单步迁移
```

## 5. 硬性规则（生成层冻结决策，改代码前必读）

- **R1 角色声明**：每张输入图必须在 prompt 中声明权威角色
  （facts source / design master / appearance anchor / module inspiration）。
  图片顺序不是合同的一部分。
- **R2 禁增删视觉信息**：输入图与生成器之间不允许任何裁剪、抠图、
  组件化预处理（冻结文档 §5 常设规则）。白底分离图是用户上传的原图，
  不是管线裁出来的——管线自己永远不做「什么是产品事实」的裁决。
- **R3 锁定事实清单**：目标语言文案白名单一次编译、每轮 prompt 逐字
  重复；参考图上的一切可见参数文案必须替换（`claim_warnings` 驱动）。
- **R4 单变量迭代**：每轮只修一个主要问题；上一轮输出是下一轮唯一的
  画布输入。
- **R5 比例重排不裁剪**：目标画布是一等参数，与参考图比例无关；
  比例修正必须是独立的 recompose 步，声明重排不删除模块；分辨率由
  管线 resample 强制，不靠 prompt。
- **R6 负面约束逐轮重复**：no donor brand / no Cyrillic(按目标市场) /
  no warranty / no price / no certifications / no watermark /
  no unsupported claims。
- **R7 原生文字与营销文案分开审核**：机身丝印（VACUUM SEALER / PULSE /
  SEAL / VAC 等）不因不在营销白名单而判失败。
- **R8 判官受限**：判官只能从 repair menu 选一项 + 写一段增量；
  不得改写锁定事实清单、不得引入新视觉权威。
- **R9 轮次预算**：默认 8 轮，耗尽转 `needs_manual`，不放宽标准换产出
  （与审美地板规则同源）。
- **R10 人工确认**：判官校准（用落盘的人工标签）之前，每轮必须人工
  确认；`auto` 模式禁用——与上游 `review_mode` 演进路径一致。
- **R11 锚图复用**：风格迁移必须以锚图为外观权威 + 白底图为事实旁证，
  禁止只拿新参考图从头收敛（除非用户明确要求）。
- **R12 产物不可变**：每轮一个目录，prompt、输入清单、候选图、判官
  决定、人工决定全部落盘；重跑换新目录。

## 6. 多图输入升级（白底 2-3 张）

用户后续原图形态：产品与背景分离的白底图，可能 2-3 张
（主机 / 配件 / 可选原海报）。设计已在 §1 合同中体现，要点：

1. `product_images[]` 每项带 `role`，prompt 编译器为每个角色生成对应
   声明段（外观锚 / 配件证据 / 原生文字证据）；
2. 白底图让「外观权威」更干净（没有海报设计语言干扰），但**参数事实
   不再出现在图上**——锁定事实清单成为唯一事实来源，这要求上游
   `truth_pack.json` 的字段完整性达标（缺参数时在 intake 阶段就报
   `incomplete_truth`，不进生成）；
3. 配件证据图缺失而 `expected_offer=host_with_accessories` 时，
   `complete_accessories` 修补步必须挂原海报或要求用户补图，禁止让
   模型脑补配件形态。

## 7. 验收标准

1. Phase 0：至少一个后端在复刻测试中达到「与 exec-ef89d9cc 可比」；
2. Phase 2：真空封口机案例，用新 runner 从 `generation_request.json`
   一键跑出 round_00 + recompose，产物目录齐全；
3. Phase 3：同案例走完收敛循环，轮数 ≤ 8，最终图人工评分不低于
   2026-07-11 的暖色终版；
4. Phase 4：用上游导出的一张新 Ozon 参考图对锚图做单步风格迁移，
   一次通过率 ≥ 1/2（紫灰当年是 1/1）；
5. 全程零次违反 R2（无任何中间层裁剪/抠图）。

---

## 附录 A：2026-07-11 成功案例完整 Prompt 链（实证配方）

任务：Codex `019f5020-a106-7752-bb23-c4c7207711ca`
原始记录：`~/.codex/sessions/2026/07/11/rollout-2026-07-11T00-42-23-019f5020-a106-7752-bb23-c4c7207711ca.jsonl`
产物目录：`~/.codex/generated_images/019f5020-a106-7752-bb23-c4c7207711ca/`

| # | 时间 | 类型 | 输入图（角色） | 输出 |
|---|---|---|---|---|
| 1 | 00:43 | 首生成 (4:5) | 产品海报(facts)、暖色参考(design) | exec-ef89d9cc |
| 2 | 00:45 | recompose 1:1 | 上轮输出 | exec-54b5471d |
| 3 | 00:47 | complete_accessories | 上轮输出、产品海报(facts) | exec-1191a50d |
| 4 | 01:07 | increase_product_dominance | 上轮输出 | exec-3f58f186 |
| 5 | 02:44 | amplify_spec_impact | 上轮输出 | exec-753137e4 |
| 6 | 02:47 | redesign_accessory_module | 上轮输出、模块级参考图 | exec-b1bca7c9 |
| 7 | 02:48 | redesign_spec_module | 上轮输出、模块级参考图 | exec-daa54c61 |
| 8 | 02:50 | add_breathing_room | 上轮输出 | **exec-8ba8669f（暖色终版）** |
| 9 | 02:52 | 风格迁移（单步） | 紫色参考(design)、暖色终版(appearance anchor)、产品海报(facts) | **exec-9bf2138e（紫灰终版）** |

结构注记：

- 步 6、7 各注入了一张**模块级参考图**（只声明用于该模块的灵感，
  "using the SECOND reference image as inspiration for the accessory
  treatment only"）——repair menu 里 `redesign_*_module` 类修补保留
  这个能力；
- 罗马尼亚语文案白名单（EXCITAT / APARAT DE VIDAT / 6 ÎN 1 / 75 kPa /
  120 W / 100 DE PUNGI INCLUSE / TUB PENTRU VIDARE EXTERNĂ / BARĂ DE
  SIGILARE DE 30 cm / CUTTER ÎNCORPORAT • STERILIZARE UV）与负面约束
  （no Cyrillic / warranty / price / unsupported claims / watermark）
  在 9 步中逐字重复；
- 步 5 有一处事实防守值得注意："Do not use 70 kPa: the authoritative
  source image says 75 kPa"——判官/人工发现模型改数字后用 prompt 显式
  钉死，这正是锁定事实清单要自动化的事。

### A.1 步 1 — 首生成（暖色，4:5）

输入：`codex-clipboard-ed7fd5d6…png`（产品海报）、`codex-clipboard-71072790…png`（暖色参考）

```text
Create a polished e-commerce main product image in the same vertical
composition, visual hierarchy, and commercial advertising style as the SECOND
reference image. Use the FIRST reference image as the authoritative source for
the product: keep the exact Excitat vacuum sealer machine design,
black-and-silver body, rounded rectangular shape, top control panel, black
locking bar, and realistic proportions. Do not redesign the appliance and do
not use the Bellwell branding or Russian text from the second image.

Scene and composition: warm premium home kitchen with a wooden countertop,
softly blurred brown/orange background, a smiling male chef in a white chef
jacket on the upper right holding a transparent vacuum bag filled with
colorful vegetables. Place the Excitat vacuum sealer prominently across the
lower half on the wooden counter, angled slightly in perspective like the
second image. Show a transparent sealed bag of vegetables emerging from the
machine, with a subtle purple sealing glow only if it looks natural. Preserve
a clean high-conversion marketplace hero-image layout with strong typography
blocks on the upper left and enough negative space for readable copy.

Use Romanian text only, with correct diacritics and no Cyrillic. Use concise,
accurate product claims from the first image, arranged similarly to the second
reference:
- brand: EXCITAT
- large headline: APARAT DE VIDAT
- badge: 6 ÎN 1
- supporting line: PENTRU PRODUSE USCATE ȘI UMEDE
- secondary benefits: 75 kPa • 120 W
- offer block: 100 DE PUNGI INCLUSE
- small feature line: BARĂ DE SIGILARE DE 30 cm
- optional small feature line: CUTTER ÎNCORPORAT • STERILIZARE UV
Do not add warranty, certifications, testimonials, prices, fake logos, or
unsupported claims. Make all Romanian copy legible, correctly spelled, and
visually integrated. Keep the product itself as the largest sharp foreground
object. Final output should be a single finished 4:5 e-commerce advertising
image, high resolution, realistic product photography, premium lighting,
strong contrast, no watermark, no Russian characters.
```

### A.2 步 2 — recompose 1:1

输入：exec-ef89d9cc

```text
Recompose this exact finished e-commerce hero image into a true 1:1 square
format. Preserve the same Excitat vacuum sealer product design, warm premium
kitchen, smiling male chef in white jacket, wooden countertop, transparent
vegetable vacuum bags, brand styling, and Romanian text. Do not change the
product or invent new claims. Re-layout the elements so no important text or
product is cropped: keep EXCITAT, APARAT DE VIDAT, 6 ÎN 1, PENTRU PRODUSE
USCATE ȘI UMEDE, 75 kPa, 120 W, 100 DE PUNGI INCLUSE, BARĂ DE SIGILARE DE
30 cm, CUTTER ÎNCORPORAT • STERILIZARE UV. Keep all text in Romanian with
correct diacritics and no Cyrillic. Make the square composition balanced for a
marketplace main image, with the appliance large in the lower half and the
chef visible in the upper right. High-resolution realistic commercial product
photography, clean sharp typography, no watermark.
```

### A.3 步 3 — complete_accessories

输入：exec-54b5471d、产品海报

```text
Edit the current square 1:1 image to visibly include the product accessories
shown in the FIRST reference image, while keeping the same overall design and
all existing Romanian text. Add a tasteful accessory callout area in the
upper-left or mid-left without covering the headline: show a neat stack/fan of
clear vacuum sealer bags and one realistic external vacuum hose with its
connector, matching the actual accessories from the first reference. The
accessories should look like included items, not random kitchen props. Keep
the Excitat machine as the dominant foreground object and keep the chef and
vegetable bag. Retain accurate Romanian text only, with these concise labels
if needed: "100 DE PUNGI INCLUSE" and "TUB PENTRU VIDARE EXTERNĂ". Do not add
warranty, prices, certifications, or unsupported accessories. Preserve square
1:1 marketplace composition, realistic commercial photography, crisp
typography, correct diacritics, no Cyrillic, no watermark.
```

### A.4 步 4 — increase_product_dominance

输入：exec-1191a50d

```text
Recompose this existing square 1:1 e-commerce image while preserving the same
Excitat vacuum sealer, accessories, Romanian copy, and realistic kitchen
style. Make the vacuum sealer the clear visual center and enlarge it
substantially: it should occupy roughly the central/lower 55–60% of the square
canvas, spanning most of the width, with its full body visible and crisp.
Place it centered horizontally and slightly above the bottom edge, angled
naturally on the wooden counter. Keep the chef smaller and secondary in the
upper-right background, and reduce/reposition the text blocks so they do not
compete with or overlap the appliance. Keep the accessory panels (stack of
vacuum bags and external vacuum hose) visible but compact on the upper-left
side. Preserve these accurate Romanian labels: EXCITAT, APARAT DE VIDAT,
6 ÎN 1, PENTRU PRODUSE USCATE ȘI UMEDE, 75 kPa, 120 W, 100 DE PUNGI INCLUSE,
TUB PENTRU VIDARE EXTERNĂ, BARĂ DE SIGILARE DE 30 cm, CUTTER ÎNCORPORAT •
STERILIZARE UV. Do not change the appliance design, do not crop its ends, do
not add unsupported claims, no Cyrillic, no watermark. Premium marketplace
hero image, balanced square composition, product-first visual hierarchy.
```

### A.5 步 5 — amplify_spec_impact

输入：exec-3f58f186

```text
Edit this existing square 1:1 marketplace hero image, preserving the exact
Excitat vacuum sealer, accessories, product-first layout, chef, kitchen, and
Romanian language. Make the core specifications much more visually impactful
without changing their values: prominently feature "75 kPa" and "120 W" as
large bold high-contrast hero badges, roughly 1.5–2x larger than currently,
with strong dark green/cream or white styling and clear separation. Place them
in a powerful compact spec block near the upper-middle/left area, visible at
thumbnail size, while keeping the appliance as the largest central visual
object. Keep accessories visible but secondary. Do not use 70 kPa: the
authoritative source image says 75 kPa. Keep all other accurate Romanian copy:
EXCITAT, APARAT DE VIDAT, 6 ÎN 1, PENTRU PRODUSE USCATE ȘI UMEDE, 100 DE
PUNGI INCLUSE, TUB PENTRU VIDARE EXTERNĂ, BARĂ DE SIGILARE DE 30 cm, CUTTER
ÎNCORPORAT • STERILIZARE UV. Do not add unsupported claims, prices, warranty,
Cyrillic, or watermark. Ensure typography is crisp, correctly spelled, and not
overlapping the product.
```

### A.6 步 6 — redesign_accessory_module（含模块级参考注入）

输入：exec-753137e4、模块级参考图（clipboard-70786b28）

```text
Redesign the accessory presentation in this existing square 1:1 Excitat vacuum
sealer hero image to feel more premium, dynamic, and art-directed, using the
SECOND reference image as inspiration for the accessory treatment only. Keep
the main Excitat appliance large, centered, and dominant; keep the large
high-impact spec badges "75 kPa" and "120 W"; keep the smiling chef, warm
kitchen, Romanian copy, and all product facts.

Replace the current stiff, repetitive two green rectangular accessory boxes
with a more elegant layered composition inspired by the reference: show a
realistic fan of translucent vacuum sealer bags emerging from a soft black
rounded backdrop or floating product card, with natural overlapping layers and
subtle shadow; add a beautiful rounded green gradient ribbon/label across the
lower part of the bag stack with a refined gift icon and the Romanian text
"100 DE PUNGI INCLUSE". Integrate the external vacuum hose as a smaller
secondary accessory element, slightly angled and visually connected to the bag
bundle, with a compact tasteful label "TUB PENTRU VIDARE EXTERNĂ". Use
asymmetry, depth, soft highlights, rounded corners, and subtle green glow so
the accessory grouping feels designed rather than like two rigid catalog
tiles. Keep accessories on the upper-left/mid-left, compact enough not to
compete with the appliance or the large spec badges.

Maintain accurate Romanian text only: EXCITAT, APARAT DE VIDAT, 6 ÎN 1,
PENTRU PRODUSE USCATE ȘI UMEDE, 75 kPa, 120 W, 100 DE PUNGI INCLUSE, TUB
PENTRU VIDARE EXTERNĂ, BARĂ DE SIGILARE DE 30 cm, CUTTER ÎNCORPORAT •
STERILIZARE UV. Do not use Russian/Cyrillic, do not add warranty, prices,
certifications, or unsupported claims. Preserve the exact product design and
square marketplace format. High-end commercial product advertising, clean
hierarchy, realistic accessory photography, crisp legible typography, no
watermark.
```

### A.7 步 7 — redesign_spec_module（含模块级参考注入）

输入：exec-b1bca7c9、模块级参考图（clipboard-7beb3ca1）

```text
Edit only the specification presentation in this existing square 1:1 Excitat
marketplace hero image. The accessory composition on the left is already
approved and must remain essentially unchanged: preserve the elegant fan of
vacuum bags, green gift ribbon, external hose, product, chef, Romanian copy,
and overall layout.

Redesign the current "75 kPa" and "120 W" specification area so it feels more
distinctive, premium, and art-directed than two plain stacked rounded
rectangles. Keep the exact values and units: "75 kPa" and "120 W". Create a
more dynamic branded spec composition using a single cohesive dark-green
premium panel or asymmetrical layered badge: large dimensional numerals, cream
circular gauge/lightning icons, subtle metallic or neon-green accents,
diagonal cut lines or offset layers, a refined hierarchy where 75 and 120 are
the visual stars, and a small Romanian descriptor integrated elegantly if
useful (for example "PRESIUNE DE VID" and "PUTERE"). Avoid generic dashboard
cards, avoid excessive clutter, and keep the spec block readable at thumbnail
size. It should feel like a designed marketing badge that matches the green
accessory ribbon and the Excitat identity.

Do not change the product design or its size/position. Keep all accurate
Romanian text elsewhere: EXCITAT, APARAT DE VIDAT, 6 ÎN 1, PENTRU PRODUSE
USCATE ȘI UMEDE, 100 DE PUNGI INCLUSE, TUB PENTRU VIDARE EXTERNĂ, BARĂ DE
SIGILARE DE 30 cm, CUTTER ÎNCORPORAT • STERILIZARE UV. No Russian/Cyrillic,
no warranty, no price, no unsupported claims, no watermark. High-end realistic
e-commerce advertising, crisp typography, square 1:1.
```

### A.8 步 8 — add_breathing_room（暖色终版）

输入：exec-daa54c61 → 输出 **exec-8ba8669f**

```text
Refine this existing square 1:1 Excitat e-commerce hero image into a cleaner,
airier, more premium art-directed composition. Keep the current approved
accessory treatment: the realistic fan of vacuum bags with the elegant green
ribbon and the external hose. Keep the exact vacuum sealer large and centered
in the lower half, keep the chef secondary in the upper-right, and keep the
Romanian product claims accurate.

Main design changes: create more breathing room and visual calm. Increase
spacing between the headline, accessory grouping, specification badges, chef,
and appliance. Reduce the feeling of stacked boxes and crowded information.
Let the accessory composition and spec block have clearer margins and a
lighter visual rhythm, with refined asymmetry and more negative space.
Simplify decorative edges and reduce the neon-green glow so it feels
sophisticated, not heavy. Keep 75 kPa and 120 W prominent, but make the two
spec badges slightly slimmer and more elegant, with more space around them.

Make the whole image more luminous, clear, and translucent: brighter soft
daylight-like exposure, lighter warm wood, cleaner whites, airy soft
beige/cream and muted green accents, gentle shadows, less muddy dark brown
background, subtle depth-of-field. Keep the appliance's silver metal crisp and
realistic, the transparent vacuum bags visibly clear, and the vegetables fresh
and colorful. Do not wash out the product or lose contrast. Maintain a premium
marketplace main-image look.

Preserve accurate Romanian text only: EXCITAT, APARAT DE VIDAT, 6 ÎN 1,
PENTRU PRODUSE USCATE ȘI UMEDE, 75 kPa, 120 W, 100 DE PUNGI INCLUSE, TUB
PENTRU VIDARE EXTERNĂ, BARĂ DE SIGILARE DE 30 cm, CUTTER ÎNCORPORAT •
STERILIZARE UV. No Cyrillic, no warranty, no price, no unsupported claims, no
watermark. Ensure all text is crisp and legible and no important element is
cropped.
```

### A.9 步 9 — 风格迁移（紫灰终版，单步）

输入：紫色参考（clipboard-1f83ef9e，design）、exec-8ba8669f（appearance
anchor）、产品海报（facts）→ 输出 **exec-9bf2138e**

```text
Create a new square 1:1 e-commerce product image for the Excitat vacuum
sealer. Use the FIRST reference as the main visual and layout inspiration:
clean light gray and soft lavender/purple background split into geometric
color areas, editorial infographic style, large central product, translucent
rounded callout labels, soft glow, clear visual hierarchy, and a vacuum-packed
food item emerging beneath the machine. Use the SECOND and THIRD references as
authoritative sources for the exact Excitat appliance appearance and
accessories.

Composition: place the exact Excitat black-and-silver vacuum sealer large and
centered across the middle of the square canvas, viewed from the front/top at
a slight natural angle. Show a transparent embossed vacuum bag with a vivid
salmon steak or fresh food directly under/coming out of the sealing strip,
with a subtle violet UV glow. Use clean white/light-gray space around the
product, with purple accent panels and elegant translucent rounded capsules.
Add small, tasteful callouts for the included accessories: a fan of
transparent vacuum bags and the external vacuum hose with connector, shown as
floating product cutouts or compact bubbles. Keep the product dominant and
uncluttered.

Use Romanian text only, accurately spelled with diacritics, no
Russian/Cyrillic. Suggested copy adapted to the reference layout:
- top headline: APARAT DE VIDAT PENTRU ALIMENTE
- feature callout: CUTTER ÎNCORPORAT
- large spec: 75 kPa
- secondary spec: 120 W
- feature callout: STERILIZARE UV
- supporting line: PROTEJEAZĂ ALIMENTELE
- badge: 6 ÎN 1
- included accessory badge: 100 DE PUNGI INCLUSE
- small accessory label: TUB PENTRU VIDARE EXTERNĂ
- small feature: BARĂ DE SIGILARE DE 30 cm
Do not add warranty, price, customer count, certifications, or any
unsupported claims. Do not use Bellwell branding. Keep EXCITAT brand visible
on the appliance or at the top. Preserve exact product proportions and control
panel details from the source. Make the result premium, airy, highly legible
at thumbnail size, realistic product photography blended with refined
infographic design, no watermark.
```
