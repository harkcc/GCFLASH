# ST08 完整 8 图套评估（2026-04-17）

## 全部输出（`output_st08_test/`）

| # | 类型 | 生成方法 | 评分 | 产品一致 | 核心优点 | 核心问题 |
|---|------|---------|------|---------|---------|---------|
| 1 | hero | composite | ⭐⭐⭐⭐⭐ | ✅ | 黑金聚光灯商用级 | 产品未投地面阴影 |
| 2 | pain_point | flux_direct | ⭐⭐⭐⭐ | n/a (无产品) | 氛围电影感 | 车顶伪 LED 灯 |
| 3 | solution | composite | ⭐⭐⭐ | ✅ | 冷/暖 split 配色到位 | 场景里出现伪造小充气泵 |
| 4 | detail | flux_direct | ⭐⭐⭐⭐ | ❌ | 微距水珠 LED 质感好 | 不是我们的产品形态 |
| 5 | multi_use | 4x flux_direct + grid | ⭐⭐ | ❌❌ | 四个场景各自到位 | **四格是四个完全不同的产品** |
| 6 | trust | flux_direct | ⭐⭐⭐ | ❌ | 平铺构图专业 | 产品完全不同，连型号 ST08 字样都变了 |
| 7 | specs | composite | ⭐⭐⭐ | ✅ | 产品保留 | FLUX 生成了乱码参数标注 |
| 8 | cta_gift | composite | ⭐⭐⭐⭐⭐ | ✅ | 礼盒氛围极佳 | 小字标题"150 PSI"上方有抖动 |

## 成本与耗时

| 阶段 | 图数 | 耗时 | 成本 |
|------|------|------|------|
| T1 (pain_point) | 1 | 8.7s | $0.05 |
| T2 (hero) | 1 | 19.4s | $0.105 |
| Full set #3-8 | 6 | 78.2s | $0.45 |
| **总计** | **8** | **106.3s (1min 46s)** | **$0.605** |

## 核心发现

### 1. 产品一致性规律已验证
- **走 composite 链路（#1/#3/#7/#8）**：产品外形 100% 保留
- **走 flux_direct（#4/#5/#6）**：场景质量高但产品变了

**结论**：8 图里**至少 6 图必须走 composite**（#1/#3/#4/#5/#6/#7/#8），只有 #2 pain_point 可以 flux_direct 因为不含产品

### 2. In-Context-LoRA 的必要性被 #5 证明
- 4x flux_direct 在同一 prompt 下生成的 4 张图里，产品设计完全不同
- 这正是 In-Context-LoRA 或"同一产品合成到 4 场景"要解决的
- 下轮必须测 In-Context-LoRA，或改用 composite 做 4 次（耗时多但可控）

### 3. FLUX 写字不可用
- #7 specs 里 FLUX 生成的参数标注是完全乱码（"DIGIAL display"、"LED butter maker"、"Air output caliies"）
- 规格图、文字 overlay、参数表**必须**走 Playwright HTML 或 Qwen-Image

### 4. "场景为产品留空"策略有效但不完美
- 场景 prompt 加了 "leave space for product" 和 "no product visible in scene"
- 大部分图（#1/#7/#8）干净留空
- 但 #3 依然在背景里生成了一个伪充气泵（小尺寸，藏在右侧）
- 可用 ControlNet Inpaint 或 mask-based outpaint 根治

### 5. 场景氛围和情绪刻画 FLUX Pro 很强
- #2 雨夜瘪胎、#3 冷暖 split、#8 礼盒暖光——情绪都到位
- 这块不需要更贵的模型

## 修复清单（按优先级）

**P0 — 必修（影响 listing 可用）**
- [ ] #5 multi_use 改走 "composite × 4" 或 In-Context-LoRA（当前质量不可用）
- [ ] #6 trust 改走 composite（需要一张 top-down 的产品图做 fg）
- [ ] #4 detail 改走 composite + ControlNet Canny 保细节（或让用户提供一张产品面板特写图）
- [ ] #7 specs 的参数标注改走 Playwright HTML 叠字

**P1 — 可优化**
- [ ] 接 IC-Light 给 #1/#8 加真实地面阴影和光源匹配
- [ ] 场景"产品留空"改走 outpaint（scene 先生 mask，再 outpaint 外围）避免 #3 的伪造产品

**P2 — 锦上添花**
- [ ] Gemini 3.1 Pro Preview 打分验证每张图
- [ ] 色调统一：hero 色调提取 → 其他图 histogram matching

## 下一轮建议

**最小修复方案（再跑一次成本 ≈ $0.5-1）**：
1. 用一张 top-down 产品图（再生成或手动 crop）解决 #6
2. #5 用 composite × 4 代替 flux_direct × 4（同一 fg 合成到 4 个背景）
3. #7 加 Playwright HTML 叠真实参数标注
4. #3 的伪造产品用重跑或手动 inpaint 清掉

完成后 8 图套应达到"可上线 listing"级别。
