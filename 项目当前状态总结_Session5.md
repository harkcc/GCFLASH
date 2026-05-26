# Excitat AI 电商套图系统 — 当前状态总结（Session 5）

> 生成时间：2026-04-18
> 涵盖 Session 3-5（调研 + 实测 + 架构定型）的全部成果

---

## 一、技术框架与逻辑

### 1.1 整体技术栈

```
┌─────────────────────────────────────────────────────────┐
│  规划与审核层  Gemini 3.1 Pro Preview                    │
│  （之前 Session 用的 2.5 Pro 已淘汰）                     │
├─────────────────────────────────────────────────────────┤
│  生成层（多模型混合）                                     │
│  ├── FLUX Kontext Multi  $0.04  产品保真主力              │
│  ├── Nano Banana 2       $0.08  生白底参考、风格融合       │
│  ├── FLUX Pro v1.1       $0.05  纯场景/氛围图             │
│  ├── BiRefNet            $0.005 抠图（备用回退）           │
│  └── Qwen-Image-2        $0.035 中文文字图层              │
├─────────────────────────────────────────────────────────┤
│  设计层  HTML Template + Playwright + Pillow             │
│  （+ 计划中的 sticker library + SVG）                     │
├─────────────────────────────────────────────────────────┤
│  数据/配置层  MongoDB（计划） + JSON 配置文件               │
│  ├── CategoryConfig      品类色彩/光线/字体/羽化参数        │
│  ├── ImageSpec / Plan    每张图的完整规格 JSON             │
│  ├── ToolRegistry        可调工具手册（让 Planner 选）      │
│  └── SKILL.md            每个设计 skill 的元数据           │
├─────────────────────────────────────────────────────────┤
│  执行环境  Node.js (.mjs) + Python 3.12 + Pillow         │
│  Playwright + Chromium 1208                              │
│  fal.ai SDK + @google/generative-ai                      │
└─────────────────────────────────────────────────────────┘
```

### 1.2 核心架构理念（Session 4-5 收敛）

| 决策 | 结论 | 理由 |
|------|------|------|
| Agent vs Workflow | **Workflow 外壳 + Agent 内核** | 顶层流程固定，工具选择交给 Gemini |
| 框架选型 | **裸 Python/Node + Pydantic schema** | LangGraph/PydanticAI 都过重，YAGNI |
| 一致性主力 | **FLUX Kontext Multi 多参考图** | 实测 ~85% 一致性，比 Nano Banana 60% 强且便宜一半 |
| 设计精度 | **HTML 模板 + Playwright** | 不靠 AI 写字，叠字走结构化模板 |
| 艺术字 | **预制贴纸库（PNG/SVG）** | CSS 做不到镀铬/3D 立体/玻璃质感 |
| 多品类 | **CategoryConfig 配置驱动** | 换品类只改 JSON，不改代码 |
| Skill 抽象 | **按"排版模式"而非"品类"切分** | 1 个 skill 覆盖一簇相邻品类 |
| 商用合规 | **fal.ai 已购 FLUX 商业授权** | 用户实测可用 |

### 1.3 Skill 系统结构（已实现首个）

```
design_skills/
├── gaming_hero_4k/                ← ✅ 已搭，覆盖 tech/auto/electronics 簇
│   ├── SKILL.md                    可读的"何时用"元数据，给 Gemini 选
│   ├── schema.json                 输入 JSON schema
│   ├── template.html               HTML + CSS（带变量占位）
│   ├── render.py                   Playwright 渲染器（base64 嵌图修复完成）
│   ├── assets/                     字体、图标
│   └── examples/                   范例输出
│
└── （未来）
    ├── lifestyle_hero_editorial/   服饰/美妆/家居/旅行
    ├── automotive_industrial_hero/ 汽车工具/重工
    ├── specs_callout_grid/         通用规格图
    ├── pain_point_cinematic/       通用痛点情绪图
    ├── cta_gift_warm/              通用促下单
    ├── before_after_split/         通用方案对比
    └── scene_multi_use_2x2/        通用四格场景
```

**关键洞察**：1 个 skill 不绑死单品类。`gaming_hero_4k` 已实测同时覆盖游戏机和 ST08 充气泵，只换 JSON 参数。

---

## 二、整体流程

### 2.1 端到端 Pipeline（最终定型版）

```
┌── Step 0: 用户输入 ──────────────────────────────────────┐
│  • 产品信息（标题/规格/卖点）                              │
│  • 产品图素材（固定槽位）                                 │
│    ├── 白底正面图           [必填]                       │
│    ├── 白底侧面/45° 图      [可选]                       │
│    ├── 细节/内部图          [可选]                       │
│    └── 其他素材 × 3         [可选]                       │
│  • 风格偏好（可覆盖 AI 判断）                             │
└────────────────────────────────────────────────────────┘
                         ↓
┌── Step 1: Gemini Planner ──────────────────────────────┐
│  ├── 读产品信息 → 判定品类簇                              │
│  ├── 读 CategoryConfig 拿色彩/光线/字体基础                │
│  ├── 读 ToolRegistry + SKILL.md 列表                     │
│  └── 对 8 种 image_type 各自决定:                        │
│       ├── 用哪个 skill                                   │
│       ├── 用哪些工具/模型                                  │
│       ├── 生成本图 prompt                                 │
│       └── 填充 skill_inputs.json                         │
│  输出: 8 份 image_spec.json                              │
└────────────────────────────────────────────────────────┘
                         ↓
┌── Step 2: 多模型生成（按保真等级路由） ─────────────────────┐
│                                                          │
│  高保真（hero/detail/specs/cta/solution/multi-use/trust）│
│  └── FLUX Kontext Multi（多参考图）                       │
│      $0.04/张, ~85-90% 产品一致性                        │
│                                                          │
│  无产品（pain_point）                                    │
│  └── FLUX Pro v1.1 直生  $0.05/张                       │
│                                                          │
│  中文文字层                                              │
│  └── Qwen-Image-2 透明底  $0.035/张                     │
│                                                          │
│  失败回退                                                │
│  └── Nano Banana 2 多参考  $0.08/张                     │
└────────────────────────────────────────────────────────┘
                         ↓
┌── Step 3: 设计 Skill 渲染 ────────────────────────────┐
│  ├── 读 image_spec → 选 skill                          │
│  ├── 把生成图作为底图 + 填变量                          │
│  ├── Playwright 加载 HTML → 截图                       │
│  └── 输出: 最终 PNG（1024 / 2048）                       │
└────────────────────────────────────────────────────────┘
                         ↓
┌── Step 4: 一致性检查（计划） ─────────────────────────────┐
│  ├── BiRefNet 抠产品 → SSIM vs 源参考                   │
│  └── 不达标 → 回退 Pillow composite 强制保真              │
└────────────────────────────────────────────────────────┘
                         ↓
┌── Step 5: Gemini 审核（计划） ──────────────────────────┐
│  ├── 5 维 rubric 打分                                  │
│  │   ├── 产品保真 0.30                                  │
│  │   ├── 文字可读 0.20                                  │
│  │   ├── 构图     0.15                                  │
│  │   ├── 光影     0.15                                  │
│  │   └── 品牌一致 0.20                                  │
│  ├── < 7 → 重生（最多 3 次）                            │
│  └── ≥ 7 → 交付                                        │
└────────────────────────────────────────────────────────┘
                         ↓
┌── Step 6: 交付 ─────────────────────────────────────────┐
│  ├── PNG（必出）                                       │
│  ├── 分层 PSD（计划，对接设计师）                         │
│  └── JSON 报告（耗时/成本/分数/版本）                     │
└────────────────────────────────────────────────────────┘
```

### 2.2 8 图任务分工（最终方案）

| # | 类型 | 任务 | 优选模型 | 用 skill |
|---|------|------|---------|---------|
| 1 | hero | 抓眼球 | FLUX Kontext Multi（3 参考） | `gaming_hero_4k` 类 |
| 2 | pain_point | 戳痛点 | FLUX Pro 直生 / Pexels | `pain_point_cinematic`（待搭） |
| 3 | solution | 给方案 | FLUX Kontext Multi（2 参考） | `before_after_split`（待搭） |
| 4 | detail | 秀细节 | FLUX Kontext Multi（细节参考） | `specs_callout_grid`（待搭） |
| 5 | scene_multi_use | 看场景 | FLUX Kontext Multi（一次 num_images=4） | `scene_multi_use_2x2`（待搭） |
| 6 | trust | 建信任 | FLUX Kontext Multi（俯视参考） | `trust_inside_view`（待搭） |
| 7 | specs | 选规格 | FLUX Kontext Multi 底图 + HTML 叠真实参数 | `specs_callout_grid` |
| 8 | cta_gift | 促下单 | FLUX Kontext Multi（2 参考） | `cta_gift_warm`（待搭） |

---

## 三、具体成果

### 3.1 跑通的产品（Session 4-5）

| 产品 | 来源 | 8 图覆盖 | 总成本 | 总耗时 | 平均得分 |
|------|------|---------|-------|-------|---------|
| ST08 充气泵 | emag.ro | 8/8 ✅ | $0.605 | 106s | 4-6/10（FLUX 早期管道） |
| Taygeer 背包 | Amazon | 8/8 ✅ | $0.55 | 100s | 5-7/10（中期 Nano Banana） |
| EXCITAT Game Stick | hero 单图 | 1/8（hero） | $0.08 | 51s | 7.5/10（Nano + skill） |
| ST08（同 skill 测试） | 复用 | 1/1 | $0.08 | 43s | 7/10 |
| Game Stick FLUX Kontext | 3 参考实验 | 1/1 | $0.16 | 110s | **8.5/10（最高）** |

**累计实测产物：~30 张图，跨 3 品类**。

### 3.2 已构建文件清单（`phase0_results/`）

```
代码与配置
├── product_st08.json                 ST08 完整产品数据
├── product_backpack.json             Taygeer 背包数据
├── image_plan_st08.json              ST08 8 图规格 JSON
├── image_plan_backpack.json          Backpack 8 图规格 JSON
├── category_config_auto_accessory.json   ST08 类目配置
├── category_config_backpack_women.json   背包类目配置
├── tool_registry.json                工具手册
├── composite.py                      Pillow 合成 v2（支持 bbox）
├── grid_compose.py                   2x2 网格合成
└── design_skills/
    └── gaming_hero_4k/                   首个完整 skill
        ├── SKILL.md
        ├── schema.json
        ├── template.html
        ├── render.py                     Playwright + base64 修复完成
        └── assets/, examples/

测试脚本
├── test_st08_smoke.mjs               smoke test
├── test_st08_hero.mjs                hero composite 链路
├── test_st08_full_set.mjs            ST08 8 图批量
├── test_backpack_full_set.mjs        Backpack 8 图批量
├── test_nanobanana_person.mjs        Nano Banana 人+产品+场景
├── test_st08_same_skill.mjs          跨品类 skill 复用证明
├── test_gamestick_hero.mjs           Game Stick + skill 端到端
└── test_flux_kontext_multi.mjs       FLUX Kontext vs Nano Banana 对比

输出目录
├── output_st08_test/                 ST08 8 图 + 中间产物
├── output_backpack_test/             Backpack 8 图
├── output_gamestick_test/            Game Stick 实验
├── output_nanobanana_test/           人物场景测试
├── output_flux_kontext_test/         FLUX Kontext 对照实验
└── ...

报告与文档
├── README_ST08.md                    ST08 测试说明
├── full_set_evaluation.md            ST08 8 图详细评估
├── cross_category_evaluation.md      跨品类（ST08 vs Backpack）评估
└── 项目当前状态总结_Session5.md      （本文件）
```

### 3.3 验证通过的核心命题

1. ✅ **多品类配置抽象有效**——CategoryConfig 换 JSON 即可换品类，跨硬黑黄工业（ST08）和软粉奶生活（背包）
2. ✅ **bbox 控制构图**——产品大小位置按 image_plan 真的变化（非全屏铺满）
3. ✅ **composite×4 解决多场景一致性**——比 flux_direct×4（4 个不同产品）质量飞跃
4. ✅ **Skill 1 vs N 品类**——同一 skill 文件跑游戏机+ST08，仅换输入 JSON
5. ✅ **HTML+Playwright 叠字可行**——结构化文字（标题/徽章/品牌/规格）渲染完美
6. ✅ **FLUX Kontext Multi > Nano Banana 在产品保真上**——~85% vs ~60%，且半价
7. ✅ **Skill 化是对的方向**——SKILL.md 让 Gemini Planner 自动选 skill

### 3.4 关键 API & 模型 fal.ai endpoint 清单

| Endpoint | 用途 | 单价 | 实测耗时 |
|----------|------|------|---------|
| `fal-ai/flux-pro/kontext/multi` | **产品置入场景** | $0.04 | 10s |
| `fal-ai/nano-banana-2` | 白底产品/风格融合/Edit | $0.08 | 20-30s |
| `fal-ai/flux-pro/v1.1` | 文生图（场景/氛围） | $0.05 | 7-9s |
| `fal-ai/birefnet` | 抠图（前景+遮罩） | $0.005 | 5s |
| `fal-ai/qwen-image-2` | 中文文字层 | $0.035 | 待测 |
| `fal-ai/iclight-v2` | 重打光（备选） | $0.015 | 待测 |
| `fal-ai/clarity-upscaler` | 4K 增强（备选） | 按 MP | 待测 |

---

## 四、遇到的难题 vs 解决进度

### 4.1 已彻底解决

| 难题 | 表现 | 解决方案 |
|------|------|---------|
| **产品一致性差** | 早期 Nano Banana 单参考 60-70% | FLUX Kontext Multi + 3 参考图 → 85%+ |
| **跨格风格漂移** | ST08 multi-use 4 个不同产品 | composite×4：同一 fg 合到 4 个场景 |
| **bbox 控制无效** | 产品永远铺满全屏 | composite.py 支持等比缩放+定位 |
| **跨品类硬编码** | 露营专用代码不通用 | CategoryConfig + skill 双层抽象 |
| **场景污染** | scene prompt 含产品描述导致 FLUX 自生重影 | scene_only_prompt 字段独立 |
| **HTML 背景加载失败** | Playwright 阻断 file:// | base64 data URI 内联 |
| **品牌商业授权** | Finegrain non-commercial | fal 已购 FLUX 商用许可 |
| **Gemini 模型版本** | 2.5-pro-preview 过期 | 升级到 3.1-pro-preview |

### 4.2 已部分解决

| 难题 | 进度 | 后续做法 |
|------|------|---------|
| **AI 写字乱码** | HTML 叠字解决了 70% | 艺术字（4K/PRO 这种）走 sticker 库 |
| **合成边缘硬切痕** | bbox + 羽化 10px 改善 | 接 IC-Light 做光源匹配（待验证） |
| **场景 AI-slop 痕迹** | Nano Banana/FLUX Kontext 缓解 | Pexels 拉真实场景图（未接） |
| **多次生成不稳定** | 串行 + seed 锁可缓解 | 真正的 LoRA 训练才彻底解决 |

### 4.3 未解决

| 难题 | 阻塞原因 | 待做 |
|------|---------|------|
| **真实产品图缺失** | 用户侧未提供 | 用户提供 3-5 张/SKU 多视角白底图 |
| **审核闭环未接** | 优先级 P1 | 接 Gemini 3.1 rubric 打分 + 重试 |
| **PSD 分层导出** | 优先级 P2 | psd-tools 或 ImageMagick 分层 |
| **LoRA 训练流程** | 工程量大 | 头部爆款 SKU 才值得做 |
| **Sticker library** | 需设计师参与 | 首批 20 个艺术字 + 20 个徽章 |
| **AssetSourceAgent** | 未实现 | Pexels/Unsplash API + Gemini 决策 |
| **Skill 数量不足** | 只有 1 个 | 还需 7 个覆盖 80% 场景 |

---

## 五、关键决策记录（按 Session 顺序）

| Session | 关键决策 | 理由 |
|---------|---------|------|
| 2 | Workflow 不用 Agent 框架 | 流程固定，调试可复现 |
| 3 | 调研定 Top 资源（Finegrain/IC-Light/In-Context-LoRA） | 业内成熟方案 |
| 4 | 多品类系统而非单品（Backpack 验证） | 用户原始定位 |
| 5 早期 | bbox 修复 + composite×4 | 实测发现的工程缺口 |
| 5 中期 | 切到 Nano Banana 2 主力 | 产品摄影专用 + 多参考 |
| 5 后期 | **再切到 FLUX Kontext Multi** | 实测产品保真更强且半价 |
| 5 后期 | Skill 化设计层 + HTML 叠字 | 解决 AI 写字乱码 |
| 5 后期 | "贴纸库 + SVG" 方案治艺术字 | CSS 做不到镀铬/玻璃质感 |

---

## 六、单张图最终成本/质量基准

```
8 图套（FLUX Kontext Multi 主力）
├── 7 × FLUX Kontext Multi × $0.04 = $0.28
├── 1 × FLUX Pro pain_point  × $0.05 = $0.05
├── 8 × Skill HTML 渲染            = $0.00
├── 8 × Gemini 审核 × $0.01        = $0.08（计划）
└── 总计: ~$0.41/8 图套
```

| 规模 | 成本 | 时长 |
|------|------|------|
| 单 SKU（8 图）| ≈ $0.41 | ≈ 100-150s |
| 100 SKU | ≈ $41 | ≈ 3-4 小时 |
| 1000 SKU | ≈ $410 | ≈ 30-40 小时 |

**对比传统人工**：1 个 SKU 8 图请设计师 ≈ ¥3000-8000、3-5 工作日。**降本 >100 倍，提速 >100 倍**。

---

## 七、下一步路线图

### Week 1（本周必做）
- [ ] 用户提供 3-5 张真实产品白底图（Game Stick / ST08 / Backpack 任选）
- [ ] 用 FLUX Kontext Multi 重跑全部品类的 8 图，确认稳定性
- [ ] 接 Gemini 3.1 审核 rubric，建立基线分数

### Week 2-3
- [ ] 搭 4-5 个新 skill（lifestyle / pain_point / specs / cta / multi_use）
- [ ] Sticker library v1（20 张艺术字 + 20 张徽章）
- [ ] PSD 分层导出（差异化交付）

### Week 4+
- [ ] AssetSourceAgent（Pexels/Unsplash 接入）
- [ ] 首个产品 LoRA 训练实验（爆款 SKU）
- [ ] 批量队列（Prefect / Temporal）
- [ ] 客户上线试点

---

## 八、当前**待你决策**事项（按重要度）

1. **真实产品白底图**——能否本周拿到？没有则上限锁在合成参考的 ~85%
2. **首批 skill 优先级**——先搭哪 4-5 个？
3. **审核接入时机**——Week 1 还是 Week 2？
4. **客户/业务方**——这套系统目标是 Excitat 自家 SKU 还是对外服务？
5. **设计师资源**——sticker library 谁画？设计师投入多少？
6. **PSD 分层是否必要**——决定是否花工程量

---

## 九、文件位置参考

- 全部代码与产物：`/Users/cc/Desktop/photo_show/phase0_results/`
- 先前 Session 文档：`/Users/cc/Desktop/photo_show/项目背景与关键决策_Session2.md`
- 调研报告（5 篇）：`/Users/cc/Desktop/photo_show/调研_*.md`
- 凭证：`/Users/cc/Desktop/photo_show/.env`（GEMINI_KEY / FAL_KEY / GEMINI_MODEL=gemini-3.1-pro-preview）

---

> **总结一句话**：架构从 Session 2 的"合成 pipeline"演进到 Session 5 的"FLUX Kontext Multi + Skill 化设计层 + 多模型分工"。质量从早期 4-5 分跃升到当前最佳 8.5 分。剩余的工程问题都明确、可解，不再是架构性挑战。
