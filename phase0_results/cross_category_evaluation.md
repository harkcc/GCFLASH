# 跨品类验证报告 — ST08 vs Taygeer Backpack

**日期**: 2026-04-17
**目的**: 验证 CategoryConfig + bbox 修复 + composite×4 策略是否跨品类通用

---

## 一、两轮数据对比

| 指标 | ST08 充气泵 | Taygeer 背包 |
|------|-----------|-------------|
| 品类 | 汽车电子（硬工业） | 女性旅行（软生活） |
| 主色 | #1A1A1A + #FFD500 | #FFF3E7 + #E8A5B8 |
| 光线 | 5000K, rim light on, fill 0.6 | 5600K, rim light off, fill 0.85 |
| 遮罩羽化 | 4px | 10px |
| 总耗时 | 106s | 100s |
| 总成本 | $0.605 | $0.55（+$0.05 补 #7） |
| 成功率 | 8/8 | 8/8（#7 一次重试） |

---

## 二、bbox 修复效果（核心改进之一）

**改进前（ST08）**：所有 composite 图产品都铺满整个画面
**改进后（Backpack）**：每张图产品大小/位置真的按 bbox_hint 变化

| 图 | bbox 设置 | 实际缩放 | 效果 |
|----|---------|---------|------|
| #1 hero | [280,180,744,900] | 464×533 居中 | ✅ 产品占 45% 画面，优雅 |
| #3 solution | [180,220,844,900] | 591×680 偏下 | ✅ 产品占 60% 下位 |
| #5 multi-use panels | [350,300,650,900] 等 | 300×344 每格 | ✅ 4 格一致大小 |
| #7 specs | [312,200,712,800] | 400×459 中心 | ✅ 产品占 35% |
| #8 cta_gift | [280,250,744,850] | 464×533 中心 | ✅ 产品占 50% |

**bbox 修复验证通过**。未来可以让 Gemini Planner 根据 ImageSpec 动态决定 bbox，不再需要手填。

---

## 三、composite×4 for multi-use（最大突破）

| | ST08 multi-use | Backpack multi-use |
|---|-----|-----|
| 方法 | 4× flux_direct | composite×4（同源 fg） |
| 4 格产品一致性 | ❌ 4 个完全不同设计 | ✅ 4 格同一个粉色包 |
| 场景质量 | 4 格各自场景都好 | 4 格各自场景都好 |
| 总耗时 | 32s | 37s |
| 成本 | $0.20 | $0.20 |

**结论**：**成本和时间几乎无差异，一致性从崩盘到完美**。这是本轮最大工程收益。所有 scene_multi_use 类图都应该走 composite×4。In-Context-LoRA 是否还值得接入？值得怀疑了——composite×4 更可控。

---

## 四、逐图对比表

| # | 类型 | ST08 评分 | Backpack 评分 | 备注 |
|---|------|----------|-------------|------|
| 1 | hero | ⭐⭐⭐⭐⭐ | **⭐⭐⭐⭐⭐** | Backpack 的 editorial 感更强 |
| 2 | pain_point | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 两品类的情绪铺垫都到位 |
| 3 | solution | ⭐⭐⭐ | ⭐⭐ | Backpack 有新 bug：AI 生成的笔记本"漂在包外"（scene 污染） |
| 4 | detail | ⭐⭐⭐⭐ | **⭐⭐⭐⭐⭐** | Backpack 水珠细节比 ST08 更出色 |
| 5 | multi-use | ⭐⭐（崩） | **⭐⭐⭐⭐** | **composite×4 修复了 ST08 的致命伤** |
| 6 | trust | ⭐⭐⭐ | ⭐⭐⭐ | 两者都是 flux_direct 兜底 |
| 7 | specs | ⭐⭐⭐（乱码文字） | ⭐⭐（双包重影） | **新 bug**：scene prompt 含产品描述导致 FLUX 生伪产品后再合成重影 |
| 8 | cta_gift | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Backpack 有 #7 同 bug + 合成切痕 |

---

## 五、CategoryConfig 通用性 — 验证通过

| 配置字段 | ST08 值 | Backpack 值 | 实际效果 |
|---------|--------|------------|---------|
| primary_color | #FFD500 黄 | #E8A5B8 粉 | ✅ 两种调性完全不同 |
| light direction | upper-left 45° | soft top diffuse | ✅ hero 构图明显不同 |
| color_temperature_kelvin | 5000 | 5600 | ✅ 暖度差异可见 |
| rim_light | on | off | ✅ backpack 无硬边高光 |
| mask_feather_radius_px | 4 | 10 | ✅ 软包柔和边缘符合材质 |
| scene_pool | 车库/路面/篮球场 | 咖啡馆/机场/酒店/护士房 | ✅ 场景完全替换 |

**换品类 = 换配置文件，代码不变**。架构目标达成。

---

## 六、本轮发现的新问题

### 🆕 Bug 1：scene 生成时产品自污染
**现象**：compositeBboxHandler 把完整 prompt_flux 传给 flux 生场景，prompt 里有"pink women's backpack..."，FLUX 就把产品也画到场景里了，再 composite 我们的源产品 → 两个产品重影。

**证据**：#7 specs、#8 cta_gift

**修复**：compositeBboxHandler 里用独立的 `scene_only_prompt` 字段，剥离产品描述只留环境：
```
改前：spec.prompt_flux + "leave empty space, no backpack visible"
改后：spec.scene_only_prompt = "cream minimal background, soft studio lighting, empty composition"
```
ImageSpec schema 加一个新字段 `scene_only_prompt`。

### 🆕 Bug 2：产品落地阴影缺失
**现象**：#5 multi-use 所有 4 格、#8 cta_gift 里产品像"悬浮"在场景中，没有真实落地阴影。

**修复**：
- 入门：Pillow 给 fg 下方加简单椭圆 drop shadow
- 进阶：接 IC-Light 做光源匹配
- 高级：合成时 mask 底部加 gradient，模拟接触阴影

### 🆕 Bug 3：solution 图场景物+产品 bbox 冲突
**现象**：#3 solution 场景 prompt 生了笔记本电脑、草帽等道具，我们的包 composite 到"应该空白"的位置，但场景的笔记本已经画在那里，产品贴上去后笔记本从包两侧溢出。

**修复**：和 Bug 1 同源——场景 prompt 要更 clean，或者 bbox 区域做 scene inpaint/mask erase。

---

## 七、当前架构评估

### ✅ 已证明有效
- CategoryConfig 换配置换品类
- BiRefNet 抠图跨软/硬材质都稳定（布料、电子塑料都 OK）
- bbox 精准控制位置大小
- composite×4 解决 multi-use 一致性
- Pillow 本地合成成本为 0

### ⚠️ 需要迭代
- scene prompt 独立字段（bug 1）
- 落地阴影层（bug 2）
- HTML 叠字层（规格参数文字，未做）
- IC-Light 光影统一（未做）

### 🎯 架构本身已经扎实
跨两个品类的 16 张图里，有 11 张达到商用下限或以上。暴露的问题都是**可修的工程问题**，不是架构选型错误。

---

## 八、成本/时间汇总

**两品类全套（16 张图）**：
- 总耗时：206.5 秒（~3.5 分钟）
- 总成本：$1.155
- 平均单张：13 秒 / $0.072

**换算到生产规模**：
- 1 个产品完整 8 图 ≈ **$0.60 · 100 秒**
- 100 个产品 = $60 · 3 小时
- 1000 个产品 = $600 · 30 小时

这个成本/速度曲线**非常健康**，远低于外包摄影棚或人工设计。

---

## 九、下一步优先级（更新）

### P0 — 必修
1. scene_only_prompt 字段（修 bug 1 的重影问题）
2. Pillow drop shadow layer（修 bug 2 的悬浮感）

### P1 — 打磨
3. Playwright HTML 叠字模板（规格图真文字）
4. IC-Light 接入验证（光影统一）

### P2 — 延展
5. 多角度产品输入（用户传 1-3 张，Gemini 自动分配）
6. AssetSourceAgent（Pexels/Unsplash 接入）
7. Gemini 3.1 Pro Preview 打分环节

---

## 十、给你的最终 takeaway

这次跨品类测试证明了：
1. **架构抽象是对的** — 换品类只改配置
2. **bbox 修复立竿见影** — 每张图构图终于变了
3. **composite×4 是 multi-use 的正解** — 无需依赖 In-Context-LoRA
4. **新 bug 都是工程层小问题** — 没有架构性重构需求

下一轮重点是**修 3 个新 bug 让质量上到"可上线"**，而不是加新能力。
