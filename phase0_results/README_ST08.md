# ST08 车载充气泵 — Phase 1 实跑文档

> 本文档记录 2026-04-17 这次用真实产品（Excitat ST08 Tire Inflator）实跑 Phase 0 管道的成果、已验证的部分、未验证的部分，以及下一步如何接着跑。

## 一、本次产出清单

| 文件 | 作用 | 状态 |
|------|------|------|
| `product_st08.json` | ST08 产品卖点分析（Gemini Step 0 输出的等价物，手工整理） | ✅ 已写 |
| `image_plan_st08.json` | 8 图完整规格（含三套 prompt + bbox + tool_chain） | ✅ 已写 |
| `category_config_auto_accessory.json` | "汽车电子/充气泵"品类配置（颜色/光源/字体/打分权重） | ✅ 已写 |
| `tool_registry.json` | 工具手册 v0.1（11 个工具，含 fal endpoint / cost） | ✅ 已写 |
| `test_st08_smoke.mjs` | 冒烟测试脚本（不需要产品输入图） | ✅ 已跑通 |
| `output_st08_test/` | 冒烟测试输出图 + report JSON | ✅ 已生成 |

## 二、已验证的事实（2026-04-17 实测）

✅ **fal.ai 真调用通过**
- Endpoint: `fal-ai/flux-pro/v1.1`
- Prompt: ST08 pain_point 的 prompt_flux（雨夜瘪胎场景）
- 耗时 **8.7 秒**，成本 **~$0.05**，输出 138 KB JPEG
- 图见 `output_st08_test/st08_pain_point_*.jpg`

✅ **情绪类纯场景图（无产品输入）质量可用**
- 构图、光影、氛围都达到商用下限
- 细节瑕疵（车顶多出警示灯条）是 FLUX 常见噪音，可通过加 negative_prompt 或 ControlNet 修

✅ **现有 .mjs 代码 + @fal-ai/client 1.9.5 能直接用**
- 没必要立刻切 Python。保留 Node 栈做 Phase 1-2。

## 三、**已验证**（2026-04-17 下午 T2 补测）

✅ **Hero 完整合成链路跑通**（`test_st08_hero.mjs`）
- 生成白底产品图（synthetic） → BiRefNet 抠图 → FLUX 场景底图 → Pillow 合成
- 总耗时 **19.4s**，总成本 **$0.105**
- 输出见 `output_st08_test/hero_04_final_*.jpg`
- 质量评估：构图、配色、LED 可读性、抠图边缘 — 均达商用主图下限
- 已知瑕疵：产品未投影到地面；产品源光和场景光方向不一致（IC-Light 可修）

✅ **BiRefNet 返回结构已确认**
- 字段：`image`（带 alpha 的 PNG）和 `mask_image`
- 兼容逻辑：若无显式 mask URL，从 PNG alpha 通道提取即可

## 四、**未验证**（下一步要干）

❌ **IC-Light 重打光在产品上的效果**（T4 solution 图需要）
❌ **ControlNet Canny 形状保真**（T3 detail 图需要）
❌ **In-Context-LoRA 做 scene_multi_use 四格一致性**（T5）
❌ **Gemini 3.1 Pro Preview 质量审核链路**（T6）
  - `@google/generative-ai` 0.24.1 可能不支持 `gemini-3.1-pro-preview`，需测或升 SDK

## 四、下一步行动（推荐顺序）

### 最小阻塞：拿到 ST08 白底产品图

有三种路径，选一条：

1. **从卖家处要原图**（最真）
   - 联系 emag 卖家 / Excitat 品牌方，要一张 1024×1024 白底产品图
   - 也可以用类似 ST08 的其他品牌充气泵产品图做替代测试（VIAIR 85P、AstroAI、EPAuto 都是业内标准参照物）

2. **从 Amazon / 其他平台抓**
   - 搜 "portable tire inflator 150 PSI" 找白底主图
   - 需要注意版权——测试阶段可用，上线要换自家图

3. **用 Kontext Multi 从现有多张带装饰的产品图"还原"白底图**（不稳）
   - emag 页面的图都带黄色 banner + 文字，需要 inpaint 除掉

### 接下来的测试清单（建议按顺序跑）

| # | 测试 | 依赖 | 实测/预期耗时 | 实测/预期成本 |
|---|------|------|---------|--------|
| T1 | ✅ pain_point 纯场景图 | 无 | **8.7s 实测** | **$0.05 实测** |
| T2 | ✅ hero 图（走完整合成链路） | 白底产品图 | **19.4s 实测** | **$0.105 实测** |
| T3 | detail 图（加 ControlNet Canny） | 白底产品图 | ~45s 预期 | $0.20 预期 |
| T4 | solution 图（加 IC-Light） | 白底产品图 | ~50s 预期 | $0.25 预期 |
| T5 | scene_multi_use（In-Context-LoRA） | 白底产品图 | ~90s 预期 | $0.40 预期 |
| T6 | Gemini 3.1 Pro Preview 打分 | T1-T5 输出 | ~5s/张 预期 | $0.01/张 预期 |

全部跑完一套 8 图约 **$1.5 内**。

## 五、怎么跑

### 环境准备（已完成）
```bash
cd /Users/cc/Desktop/photo_show/phase0_results
npm install   # 已装了 @fal-ai/client @google/generative-ai
```

### 跑冒烟测试（已验证）
```bash
node test_st08_smoke.mjs
```

### 跑完整 8 图（需要自己先写 runner，下次我来）
```bash
# 预期接口
node run_st08_full.mjs --product-image ./st08_white_bg.png
```

## 六、已知债务与改动建议

### P0 — 安全
- [x] FAL_KEY 已进 `.env`（不在代码里）
- [ ] **`step1_gemini_plan.mjs` 第 7 行硬编码的 Gemini API Key 需要挪到 .env**（Session 1 P0 至今未修）
- [ ] 用户在聊天里明文发过的 FAL_KEY 建议**在 fal 后台轮换一次**以防泄漏

### P1 — 模型升级
- [ ] `@google/generative-ai` 升到最新版以支持 `gemini-3.1-pro-preview`
- [ ] 或改用 `@google-cloud/vertexai` SDK（Vertex 路径对 3.1 支持更完整）
- [ ] 现有 `step1_gemini_plan.mjs` / `step4_gemini_review.mjs` 里的模型 ID 要同步升

### P2 — 架构
- [ ] 把 Session 2/3/4 讨论的 Planner+Executor Agent 模式用**裸 Python + Pydantic** 重写（当前 Node 栈作为 Phase 1-2 临时通路，第 3 阶段迁移）
- [ ] 这个 ToolRegistry 先让 Gemini 3.1 在 prompt 里读着用，还不需要完整的 agent 框架

## 七、跨产品验证建议

用户提到"一个产品不够可以再找"。建议 Phase 2 验证时至少再加 1-2 个产品确保 CategoryConfig 不绑死 ST08：

- **同品类跨品牌**：VIAIR 85P、AstroAI 充气泵 —— 验证 `category_config_auto_accessory.json` 通用性
- **跨品类**：找一个美妆/厨房类产品 —— 验证是否需要新的 CategoryConfig，参数差距有多大

Amazon / Aliexpress 搜索 "tire inflator"、"digital pressure gauge" 可以快速拿到多款对照样本。

## 八、本次成就与下次开始点

✅ 真实产品（Excitat ST08）的完整 ImageSpec 已落地
✅ CategoryConfig 模板已定（有第二个产品时照样子加一份）
✅ ToolRegistry v0.1 已定
✅ 冒烟测试跑通 → **fal.ai + prompt → image 的主管道是通的**

**下次开始点**：拿到 ST08 白底产品图 → 跑 T2 hero 合成测试 → 如果通，一路跑 T3-T6，一天内能完成整套 8 图验证。
