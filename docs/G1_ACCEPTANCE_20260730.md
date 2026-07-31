# G1 在线验收报告（SPEC §10）

日期：2026-07-30
分支：`feature/g1-reference-generation-v1`
worktree：`/Users/cc/Desktop/photo_show_g1_reference_generation`
SPEC：`tasks/G1_reference_generation_workflow_v1.md`

| 验收项 | 状态 | 结论 |
|---|---|---|
| §10.1 P0 复刻冒烟（先决门槛） | ✅ 通过 | 与 2026-07-11 基线实质等价 |
| §10.2 端到端收敛 | ✅ 跑通，质量待产品负责人签字 | 1 个修补轮收敛（预算 8） |
| §10.3 风格迁移 | ✅ 跑通，质量待产品负责人签字 | 第 2 次（上限 3 次）通过 |
| §10.4 换参考图 + 文案全自动 | ✅ 跑通 | 编译期零人工，暴露并修掉判官画布缺陷 |
| §9 离线测试 | ✅ 183 passed | 编译器 115 + 状态机 68 |

> **签字边界**：§10.2/§10.3 的验收标准是「人工评分不低于当年终版」。
> 本次跑批里的 approve/accept 是为了驱动状态机走完 P3→P4，落盘时
> `decided_by` 一律记为 `agent_acceptance_run_20260730_pending_owner_review`，
> **不冒充产品负责人的口味判断**（R10 的人工决定是未来判官校准的标签，
> 混入代跑决定会污染标签集）。质量口径请以对比板为准自行裁定。

---

## §10.1 P0 复刻冒烟

### 方法

严格按 SPEC：设计文档附录 A.1 的**原始 Prompt 原文** + 原始两张输入图，
经 `scripts/imagegen_codex_adapter.py` 生成一张，与当年首生成并排比对。

Prompt 不是手抄的——由脚本从 `docs/REFERENCE_TO_IMAGE_GENERATION_V1_DESIGN.md`
的 A.1 代码块**程序化抽取**（2088 字符，35 行）存为
`artifacts/g1_p0_smoke/a1_original_prompt.txt`，杜绝转录漂移。

输入图（顺序即 prompt 里的 FIRST / SECOND 序数）：

| # | 角色 | 文件 | 尺寸 | sha256 前 12 |
|---|---|---|---|---|
| 1 | facts（产品外观权威） | `vacuum-sealer-product-source.jpg` | 720×720 | `2d16a1264202` |
| 2 | design master | `r2-warm-chef.jpg` | 736×982 | `bb6ba1f6cba1` |

后端：`codex-cli 0.144.4`，config 默认模型，耗时 **223.8 秒**，一次成功。

### 结果

| | 当年基线 exec-ef89d9cc | 本次复刻 |
|---|---|---|
| 分辨率 | 1086×1448 | 1122×1402 |
| 实测比例 | 0.750（3:4） | **0.800（正好 4:5）** |

对比板：`artifacts/g1_p0_smoke/board.png`。

### 人工三项评分

1. **产品外形保真 —— 持平（都优）**：黑银机身、圆角矩形、宽矮比例、
   顶部触控面板（PULSE/SEAL/VAC/MOIST/AUTO/STOP + `88` 数码管）、
   右侧黑色锁扣、机身丝印 `VACUUM SEALER` 全部保住，无重设计无形变。
2. **文字正确 —— 持平（都满分）**：9 项罗语白名单全中、变音符全对；
   无西里尔、无 `Bellwell`、无参考图上的 `12 месяцев гарантия`、
   无价格认证水印。R7 原生丝印豁免按预期生效。
3. **设计迁移完成度 —— 持平**：基线暖橙氛围更贴字面；复刻比例正好命中
   4:5（基线漂到 3:4），offer 块用袋子堆叠而非礼物盒图标。

**判定：通过。** 不构成 §11 停止条件 1 的「明显更差」，后端能力可用。

---

## §10.2 端到端收敛

Job：`artifacts/g1_e2e_20260730/generation_runs/e2e03/excitat_vacuum_sealer_ro`
对比板：`artifacts/g1_e2e_20260730/board_10_2_convergence.png`

请求按 §10.2 构造：复用同一套素材 + 附录 A 的罗语事实清单（即 §5.1 的
9 槽样例），画布 1:1 / 1600px / ro。

| 轮次 | 类型 | 判官选择 | 结果 |
|---|---|---|---|
| round_00_initial | INIT | — | 1600×1600，aspect 1.000 |
| — | 比例检查 | — | 命中目标，**未触发 recompose 轮** |
| round_01_reduce_clutter | REPAIR | `reduce_clutter` | 1600×1600，收敛 |

**轮数 1 / 预算 8**，远低于 §10.2 的 ≤8 要求，也低于当年的 8 步。

三个大模型节点全部实测可用：

- 外观描述器产出 9 条具体特征（`black-and-silver rectangular body`、
  `seven icon control buttons`、`right-side black ridged knob` …）——
  §5.6 机制 1 要的就是这种具体短语；
- 设计简报器正确识别 donor `BELLWELL` / `Russian/Cyrillic`，并把 6 条
  donor 声明（含 `12 месяцев гарантия`、`Пакеты в подарок`）全部转录进
  `visible_claims_on_reference`，供 R6 剥离；
- 判官独立发现了 round_00 的重复副标题，选 `reduce_clutter`，
  `prompt_delta` 单变量、不复述白名单、不引入新参考图，
  `fact_violations` 为空、`product_integrity_ok=true` —— 完全符合 §7 合同。

修补轮验证了画布链（R4）：round_01 以 round_00 输出为唯一输入，
Prompt 以 `Edit this existing 1:1 image.` 开头，只改了重复副标题，
产品、模块、其余文案逐项未动。

**质量**：产品保真、9 项白名单全中、无越界文案、1:1 精确。与当年暖色终版
`exec-8ba8669f` 相比，本次在产品占比与字体层级上更强，暖色氛围不同（本次
偏暗调 + 亮绿点缀）。**是否「不低于」请以对比板自行裁定。**

---

## §10.3 风格迁移

对比板：`artifacts/g1_e2e_20260730/board_10_3_style_transfer.png`

以收敛锚图为外观权威（R11，未重新收敛），紫色参考图
`r1-purple-info.jpg` 作 design master，单步生成。

| 尝试 | 结果 |
|---|---|
| attempt_00 | ❌ 顶部生成了白名单外的模式条 `1 PULSE / 2 SIGILARE / 3 VAC / 4 UMED / 5 AUTOMAT / 6 STOP` |
| attempt_01 | ✅ 越界文案消失，该区域改由白名单声明填充 |

**第 2 次通过，上限 3 次（§5.5：首次 + 最多 2 次重掷）**，达标。

产品与锚图逐像素级一致（R11 生效），紫色信息图美学完成迁移，
9 项白名单全中，无西里尔、无 donor 品牌、无保修。
残留小瑕疵：`BARĂ DE SIGILARE DE 30 cm` 出现两次（风格迁移按 §5.5 是单步，
不进收敛循环，故未修）。

---

## §10.4 第二个案例：换参考图 + 文案全自动（2026-07-30 追加）

Job：`artifacts/g1_e2e_v2_20260730/generation_runs/v2run/excitat_vacuum_sealer_ro_v2`
对比板：`artifacts/g1_e2e_v2_20260730/board_v2.png`

目的：验证「换一张没用过的参考图 + 请求里不给 `copy_slots`」能否全自动跑通。
参考图换成 `r3-blue-hero.jpg`（深蓝硬朗风，与暖色厨师版设计语言完全不同）。

### 结果：编译期零人工介入

| 环节 | 结果 |
|---|---|
| 文案编译器 | 9 个罗语槽位，**一次通过**，数字零重试 |
| 比例实测 | `3:4`（修复前简报器报 `32:41`） |
| 比例适配指令 | 已进 Prompt，显式禁止裁剪／黑边／压扁 |
| round_00 | 1600×1600，aspect 1.000，133 秒 |

**信息出处核对**（这是本管线最核心的合同）：

| | 参考图上写的 | 我们图上 |
|---|---|---|
| 赠品 | `20 пакетов в подарок`（送 20 个袋子） | `100 PUNGI INCLUSE`（我方真实数字） |
| 保修 | `1 год гарантии`（1 年保修） | **整块不存在** |
| 语言 | 俄文 + 俄国旗 + 「инструкция на русском языке」 | 全部罗语，无西里尔 |
| 水印 | 小红书号 9486914676 | 无 |

借的只有：深蓝质感、紫色封口光、三文鱼演示、构图角度。

### 本轮暴露并修复的缺陷：判官不知道目标画布

首次 review 时判官选了 `recompose_aspect`，要把**正确的 1:1 图改成竖版**，
理由是「贴合参考图的纵向流」。

根因：判官 Prompt 里从来没有目标画布这个信息，它唯一能比对的形状就是参考图。
而 R5 明写「目标画布是一等参数，与参考图比例无关」。若人工照此预填执行，
会把一张本来正确的图改到违反合同，并白烧一轮预算。

修复两处：① 判官现在收到目标画布 + 候选图实测比例，并被明确告知
「参考图形状不同不是缺陷」；② runner 增加确定性兜底——候选图已在画布上却提
`recompose_aspect` 时直接标警告，不依赖 Prompt 措辞。修复后重跑同一张图，
判官改选 `reduce_clutter`（右侧食材道具确实过密），判断合理。

**这个缺陷单元测试抓不到，只有真跑才会暴露**，已补回归测试。

### 比例总核对

管线产出的 7 张图（含锚图与风格迁移）**全部 1600×1600 精确 1:1**。
唯一非 1:1 的是 §10.1 复刻冒烟的 1122×1402，那是刻意复现当年要求 4:5 的
原始 Prompt，属后端能力测试，不是本管线目标。

---

## 实施期发现并修掉的缺陷（都由「真跑一遍」暴露）

1. **三个 schema 全被 API 拒绝**。严格结构化输出要求**每一层 `properties`
   的每个 key 都出现在同层 `required`**，`immutable_traits` 漏了
   `native_product_text`、brief 的 `modules[]` 漏了 `replace_content`。
   更糟的是 schema 被拒时 `codex exec` 不写 `-o` 文件，报错只在 stderr，
   于是 §11 停止条件 3 拿到三个空样本、完全无法诊断——已让 describers 在
   空响应时把 rc/stderr/stdout 一起记进样本。已回写 SPEC §6。

2. **段 3 变成了第二个文案权威（最严重的一个）**。设计简报的模块清单被逐条
   渲染成 `<文字模块>（replace its content with our product）`，等于主动邀请
   模型自己写词，与段 4 的锁定白名单打架。2026-07-30 的 round_00 果然长出了
   白名单里没有的罗语 tagline `PĂSTREAZĂ PROSPEȚIMEA, SAVUREAZĂ CALITATEA`。
   这正是 R13「多重权威才是问题」的一个隐蔽实例。三道修补：
   - 文字模块保留结构位，但改成「只能用下面列出的已批准声明」；
   - R6 明令禁止的 donor 促销位（warranty/certification/testimonial/
     price/gift/discount/promo）**直接从版面里删掉并显式声明拒绝**，
     不再「留着位子指望负面约束压住」；
   - 文字模块无对应文案时给出合法出路：「留白，不要编造步骤条/模式名/
     编号序列」——这条是 §10.3 attempt_00 暴露的：只禁不给出路，模型仍会
     按结构指令硬填（`process_strip` 就是这么长出模式条的）。

3. **`replace_content` 被简报器打在全部 10 个模块上**，产出
   `person（replace its content with our product）` 这种荒谬指令。
   已在 schema 描述里钉死「只有承载 donor 自身产品的那个模块才为 true」，
   重跑后只剩 `product_stage` 一个。

4. **round_00 静默丢弃 `native_text_evidence` 图**：请求里给了也不会被挂载。

5. **人工决定没进账本**：`human_decision.json` 落了盘，但 `state.json` 的
   轮次记录没更新，`status` 一直显示 `human=-`。

另有三项由测试作者发现并修复：INIT 未声明 `native_text_evidence`（R1）、
重复 role 会让第二张图静默无声明（R1）、适配器每轮每图泄漏一个文件描述符。

---

## 顺带钉死的接线事实（已回写 SPEC §6）

1. `[features] image_generation = true` 是前置条件，缺则无生图工具。
2. `thread.started` 事件的 `thread_id` 是定位产物的唯一可靠钩子。
3. 产物文件名**不稳定**：同日实测既有 `exec-<uuid>.png` 也有
   `call_<call_id>.png`。**禁止按文件名匹配**，只能扫 thread 目录。
4. 生图工具调用**不产生 `item.*` 事件**，无法从事件流拿路径。
5. macOS 无 `timeout`/`gtimeout`，超时只能用 Python `subprocess` 的
   `timeout=` 参数。
6. 单次生成实测 176–407 秒，`timeout_s` 默认应 ≥600。适配器的 2 次重试
   在 §10.3 真实触发过一次（首次无产物，第 2 次成功）。
7. `--output-schema` 的 required 全覆盖约束（见上）。

---

## 未做 / 明确留给下一步

- §10.2/§10.3 的**质量签字**（产品负责人口径）；
- `approved_modules` 保留清单在本次只跑了 1 个修补轮，未产生累积样本
  （机制与测试都在，真实多轮累积待下一个案例）；
- `provider="claude"` 是 §6 声明的接缝，目前显式 `NotImplementedError`，
  没有静默回退；
- SPEC §13 列的不在范围项全部未做。
