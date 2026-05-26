# 方向 2 调研：ComfyUI 社区产品图工作流

> 面向 Excitat AI 多品类电商套图框架（首个验证品类：Amazon 蓝牙营地灯音箱）
> 目标：挖掘 ComfyUI 社区中可迁移到 fal.ai Workflow 的技术、节点拓扑、以及「一个工作流跑多品类」的实现模式。
> 调研时间：2026-04-15

---

## 一、Top 10 工作流对照表

| # | 名称 | 作者 | 链接 | 品类覆盖 | 节点数（量级） | 关键技术栈 |
|---|---|---|---|---|---|---|
| 1 | Product Photography Relight v3/v4 (Frequency Separation) | risunobushi (Andrea Baioni) | [OpenArt v4](https://openart.ai/workflows/risunobushi/product-photo-relight-v4---from-photo-to-advertising-preserve-details-color-upscale-and-more/gCMFAhrxCMjqc3Xr3Zsj) · [Civitai](https://civitai.com/articles/5393) | 通用：任意硬质产品（瓶罐、电子、配件） | 80–120 | IC-Light + SAM + IPAdapter + Frequency Separation + Color Match + PAG + Upscale |
| 2 | Product Photography V2 – Relight, Customized Placement & Detail Retention | MyAIForce | [OpenArt](https://openart.ai/workflows/myaiforce/product-photography-v2-relight-customized-placement-detail-retention-v2/GL2vEhda2lKbX0snXCNG) · [教程](https://myaiforce.com/comfyui-product-photography/) | 通用+自定义构图位置 | 60–90 | ControlNet Depth/Canny + Inpaint + Relight + 用户可拖拽 mask 定位 |
| 3 | Background Replacer V4 for Products & Portraits (Flux Fill) | MyAIForce | [OpenArt](https://openart.ai/workflows/myaiforce/background-replacer-for-products-portraits-lighting-adjustment-detail-preservation/UdbHePrLFEP9WzdrmmFj) · [教程](https://myaiforce.com/flux-replace-background-v4/) | 产品+人物双模式 | 70–100 | Flux Fill + Redux + 双模式 Switch（产品/人像）+ 细节保留 |
| 4 | FLUX Kontext Preset Workflow (15+ 内置风格) | RunComfy / Black Forest Labs 生态 | [RunComfy](https://www.runcomfy.com/comfyui-workflows/flux-kontext-preset-comfyui-workflow-ai-scene-control) · [官方文档](https://docs.comfy.org/tutorials/flux/flux-1-kontext-dev) | 通用（Teleport/Relight/Product Photo/Interior 等 15 预设） | 40–60 | Flux Kontext Dev + 预设枚举 Switch + 自然语言编辑 |
| 5 | A Rui - Product Migration_Background Swap_Clothing Swap (Redux + ACE++) | Comflowy 生态 | [Comflowy E-commerce](https://www.comflowy.com/blog/E-commerce) | 产品+服装双通路 | 100+ | Redux 风格迁移 + ACE++ LoRA + 分支 Switch |
| 6 | Change Background of Product Photos | mixlab_shadow | [OpenArt](https://openart.ai/workflows/mixlab_shadow/change-background-of-product-photos/ltyLoGeX8Vut4NrqzH1o) | 白底产品→场景 | 30–50 | BiRefNet 抠图 + SDXL 场景生成 + 光影融合 |
| 7 | Product Composite Photography | mixlab_shadow | [OpenArt](https://openart.ai/workflows/mixlab_shadow/product-composite-photography-enhancing-online-presence-and-social-media-engagement/PtuUGs9n8aMpug3r7PBX) | 多产品合成（礼盒/套组） | 50–80 | 多图合成 + ControlNet 布局 + 颜色一致化 |
| 8 | Professional Product Photography Style | cgtips | [OpenArt](https://openart.ai/workflows/cgtips/comfyui---professional-product-photography-style/KCBAhLGX1fD3qECZ0RsP) · [品类示范](https://openart.ai/workflows/cgtips/comfyui---product-photography-techniques/RjMpsRCttOelyQo7nC6N) | 手表/耳机/香水/包/单反（5 子品类示例） | 40–60 | Segment Anything + ControlNet + IPAdapter + 品类化 prompt |
| 9 | Product Image to Hero Shot | nouvo_ai | [OpenArt](https://openart.ai/workflows/nouvo_ai/product-image-to-hero-shot/3JOVHeA2U4xW3UnoOsw9) | 通用（主图/英雄图） | 30–50 | 抠图 + 戏剧化光影 + 构图放大 |
| 10 | ModelSwap FashionStable (Ghost Mannequin 近似) | denrakeiw | [OpenArt](https://openart.ai/workflows/denrakeiw/modelswap-fashionstable/4MoLzlsVgpnsoy0KHH3k) · [DeepFashion 版](https://openart.ai/workflows/myaiforce/seamlessly-swap-clothing-ip-adapter-v2-facedetailer-deepfashion/Ei0r9zHeiJ6Rl8qkt4Gj) | 服装/鞋包 | 60–90 | DeepFashion2 分割 + IP-Adapter V2 + FaceDetailer |

辅助资源（基础设施级）：
- [kijai/ComfyUI-IC-Light](https://github.com/kijai/ComfyUI-IC-Light)（IC-Light 重光照核心节点）
- [1038lab/ComfyUI-RMBG](https://github.com/1038lab/ComfyUI-RMBG)（BiRefNet/SAM/SAM2/SAM3/GroundingDINO 一站式抠图）
- [risunobushi/comfyUI_FrequencySeparation_RGB-HSV](https://github.com/risunobushi/comfyUI_FrequencySeparation_RGB-HSV)（频率分离自定义节点）
- [ltdrdata/ComfyUI-Impact-Pack](https://github.com/ltdrdata/ComfyUI-extension-tutorials/blob/Main/ComfyUI-Impact-Pack/tutorial/switch.md)（Switch/Inversed Switch/ConditionalBranch，条件路由骨架）
- [asagi4/comfyui-prompt-control](https://github.com/asagi4/comfyui-prompt-control)（prompt 内嵌 LoRA 调度）
- [willmiao/ComfyUI-Lora-Manager](https://github.com/willmiao/ComfyUI-Lora-Manager)（LoRA Pool + Randomizer）
- [aifeifei798/ComfyUI-Style-Selector-Node](https://github.com/aifeifei798/ComfyUI-Style-Selector-Node) · [shin131002/ComfyUI-Prompt-Preset-Selector](https://github.com/shin131002/ComfyUI-Prompt-Preset-Selector)（YAML 预设下拉切换）
- [adieyal/comfyui-dynamicprompts](https://github.com/adieyal/comfyui-dynamicprompts)（通配符/变量模板）

---

## 二、节点图拆解要点（逐个工作流）

### 1. risunobushi Product Photography Relight v3/v4
**拓扑（典型五段式）**：
1. 输入分支：`Load Image` → 两条路 ——（a）SAM Group（GroundingDINO 文字 prompt → SAM2 mask）产出产品 mask；（b）原图保留作为「高频细节源」。
2. 背景生成：`Empty Latent` + `KSampler` + 场景 prompt → 新背景。
3. 合成：`Image Composite Masked` 把产品放到新背景上。
4. 重光照：`IC-LightApplyV2`（Kijai 节点）以 mask 或 background 作为光源。
5. **频率分离复原**：把原产品图 RGB 分解成 HF（高频细节，text/logo/划痕）+ LF（低频色块/光影）；只用新合成图的 LF，把原图的 HF 叠回去 → 保住文字不糊。
6. 收尾：Color Match（匹配参考色）→ PAG（Perturbed Attention）→ Ultimate SD Upscale。

**关键点**：频率分离是 Photoshop 产品精修的核心手法，ComfyUI 版用 Gaussian Blur + Subtract 或 HSV V 通道两种实现（见 risunobushi/comfyUI_FrequencySeparation_RGB-HSV）。这是「AI 生成不糊文字」的通用解。

### 2. MyAIForce Product Photography V2
**拓扑**：抠图→用户手绘 mask 定位产品在画布的位置→ControlNet Depth 保住形状→Inpaint 生成环境→Relight。亮点：**自定义放置**（不是简单居中），支持海报/场景式构图。

### 3. Background Replacer V4（Flux Fill + Redux）
**拓扑**：自动 BiRefNet 抠图 → Flux Fill 填充背景 → Flux Redux 注入参考场景风格 → **双模式 Switch**（产品 vs 人像走不同后处理）。展示了 Impact Switch 在产品/人像分流上的实战用法。

### 4. FLUX Kontext Preset（最接近「多品类切换」的模板）
**拓扑**：输入图 → **Preset Selector（枚举 15+ 场景/风格：Product Photo / Relight / Move Camera / Teleport / Interior ...）** → 每个预设对应一段固化的 Kontext 自然语言 prompt 模板 → Flux Kontext Dev 编辑 → 输出。这是**单工作流跑多意图**的教科书样板。

### 5. A Rui 产品迁移 / 换装
**拓扑**：两条独立 pipeline 用 Switch 合并——（a）白底产品→场景（Redux 注入场景风格 + ACE++ LoRA 保主体）；（b）服装换装（mask + Inpaint）。**ACE++ LoRA 的价值**：在 Redux 场景迁移时保住产品 geometry 不变形。

### 6–7. mixlab_shadow 系列
**拓扑**：BiRefNet 抠图（比 rembg 精度高，尤其发丝、透明玻璃）→ 生成背景 → `LayerStyle` 节点做 Photoshop 式图层合成（投影、色彩匹配、反射）。Composite 版本额外引入多产品布局（礼盒/套组），用 ControlNet 约束每件产品的位置。

### 8. cgtips 品类化示范
**拓扑本体简单**，价值在于**为 5 个子品类（手表/耳机/香水/包/单反）各配了一套 prompt + ControlNet 参考图**。这是"参数化 prompt"的朴素实现：换品类=换 prompt 包 + 换 IPAdapter 参考图。

### 9. nouvo_ai Hero Shot
**拓扑**：强调「戏剧化构图」——额外的 shadow/rim-light 生成、低角度视角 prompt 固化。单品类不强，但**作为"Amazon 主图"节点很贴合**。

### 10. ModelSwap / 服装类
**拓扑**：DeepFashion2 细粒度分割（分出上衣、下装、鞋、包） → IP-Adapter V2 注入参考服饰 → FaceDetailer 保脸 → 人/物重新合成。**对 Excitat 来说，这是"服装品类分支"的参考模板**。

---

## 三、可迁移到 fal.ai Workflow 的具体 trick

以下 trick 都是节点级思路，fal.ai Workflow 是 Python 编排，实现成本低。

| # | Trick | ComfyUI 出处 | 到 fal.ai 的落地 |
|---|---|---|---|
| 1 | **频率分离保细节** | risunobushi 频分节点 | 在 FLUX 2 Pro 生成完成后，用 PIL/OpenCV 做 Gaussian Blur 分 HF/LF；把原图 HF 叠回合成图 LF。可避免文字/logo/纹路糊掉，对音箱按键、食品包装字体尤其关键 |
| 2 | **BiRefNet 抠图优先于 rembg** | ComfyUI-RMBG 默认选型 | fal.ai 已提供 BiRefNet；透明塑料、金属高光、发丝场景都更干净 |
| 3 | **IC-Light 重光照作为独立阶段** | kijai/ComfyUI-IC-Light | fal.ai 上做法：FLUX 生成 + BiRefNet mask → 调 IC-Light endpoint 做"以新背景光线重打产品"。不重新生成产品，只改光 → 保 100% 一致性 |
| 4 | **Flux Kontext 做"编辑式"背景替换** | FLUX Kontext Preset | Kontext 的"100% subject consistency"特性适合替代"生成+抠+贴"三段式。一次调用：输入产品图 + 场景 prompt，直接产出 |
| 5 | **Redux 注入参考场景风格** | A Rui 工作流 | 用 Flux Redux 传入一张场景参考图（比如"露营夜景灯光"），比纯 text prompt 风格一致性高 |
| 6 | **Switch 条件分支 = Python if/elif** | Impact Pack Switch | ComfyUI 用 `ImpactSwitch` + `ImpactInversedSwitch` 做分支，fal.ai 直接用 Python，但**要抄它们的"分支颗粒度"**：产品 vs 人像 vs 服装 vs 食品 各走不同后处理链，不要一个 pipeline 包打 |
| 7 | **Preset Selector + YAML** | ComfyUI-Prompt-Preset-Selector | 把 Amazon 8 图公式的每一格（抓眼球/戳痛点/给方案/秀细节/看场景/建信任/选规格/促下单）做成 YAML 模板，每格有 prompt 骨架 + ControlNet/Redux 参考图路径。品类是另一维。笛卡尔积=模板库 |
| 8 | **Dynamic Prompts 通配符** | comfyui-dynamicprompts | `{camping\|beach\|backyard}` 这种通配符语法可直接搬进 fal.ai prompt 生成函数；搭配随机/穷举模式跑 A/B |
| 9 | **LoRA Stack + Prompt Control 调度** | asagi4 prompt-control + Lora Manager | fal.ai 调 FLUX 时每次传不同 LoRA 组合。把"品类 LoRA + 风格 LoRA + 构图 LoRA"做成三维独立轴，在 Python 里组合 |
| 10 | **SAM2 + GroundingDINO 文本驱动抠图** | ComfyUI-RMBG 集成 | fal.ai 有 GroundingDINO；用文本 prompt（"the speaker, not the tripod"）精确抠目标主体——多产品合成图的刚需 |
| 11 | **Color Match 节点对齐参考色** | risunobushi v4 | 直方图匹配（skimage.exposure.match_histograms）对齐到品牌色参考，保色彩一致性 |
| 12 | **PAG（Perturbed Attention Guidance）提高细节** | risunobushi v4 | FLUX 2 Pro 若支持 guidance scale 调整，对应做法是提高 guidance 到 3.5–5；或用 Kontext 二次精修 |
| 13 | **DeepFashion2 分割** | ModelSwap | 服装品类上线时直接用；fal.ai 若无原生，用 GroundingDINO + SAM2 文本驱动等价替代 |
| 14 | **ACE++ LoRA 保主体 geometry** | A Rui | 场景迁移时产品变形是大坑；保主体 LoRA（或换 Kontext）是解 |
| 15 | **分层合成（LayerStyle）** | mixlab_shadow | 产品+投影+反射+背景分层生成再合成，比单次生成可控。fal.ai 实现：多次调 FLUX 生成各图层，Python 用 Pillow 合成 |

---

## 四、多品类切换的实现模式总结

ComfyUI 社区摸索出的多品类模式可归纳为**四种**，从耦合度由低到高：

### 模式 A：Prompt 模板变量（最轻）
**代表**：cgtips 品类化示范、ComfyUI-Style-Selector-Node、Prompt-Preset-Selector。
**做法**：同一工作流，仅替换 prompt 文本模板。品类 = 一份 YAML：`{category: speaker, prompt: "..."}`。
**优点**：零改动，一次部署。**缺点**：不同品类的光影/构图差异无法只靠 prompt 解决（食品 vs 电子产品的打光风格差异大）。
**Excitat 建议**：作为 baseline，所有品类先上 A。

### 模式 B：Switch 条件分支（中）
**代表**：Background Replacer V4（产品 vs 人像分流）、A Rui（产品 vs 服装分流）。
**做法**：Impact Switch 节点根据 `category_type` 路由到不同子图。fal.ai 等价于 Python `if category in {"speaker", "electronics"}: pipeline_A(); elif ...`。
**颗粒度建议**：按「后处理差异」分，不按「品类名称」分。例如：
- **Branch 1 硬质工业品**（音箱、家电、3C、工具）→ 强反光抠图 + IC-Light 精确控光
- **Branch 2 软质/食品**（食品、纺织、宠物玩具）→ 柔光 + 暖色调 + 场景化 IPAdapter
- **Branch 3 服装/鞋包**（含佩戴）→ DeepFashion2 或 Grounding-SAM + 人模
- **Branch 4 母婴/家居大件**→ 场景 + 比例/环境 ControlNet Depth
**优点**：差异化充分；**缺点**：每加一支 branch 要测试。

### 模式 C：LoRA 路由（重）
**代表**：Lora Manager、Prompt Control。
**做法**：每个品类训练或选取专属 LoRA（产品外观 LoRA + 品类风格 LoRA），运行时动态加载。fal.ai 调 FLUX 时传 `loras=[...]` 参数。
**前提**：有足够素材微调 LoRA（每品类 20–100 张）。Excitat 初期不必上；验证后再做。

### 模式 D：Kontext 预设（最优雅）
**代表**：FLUX Kontext Preset Workflow（15+ 预设）。
**做法**：品类差异 + Amazon 8 图意图差异 → 组合成**（品类 × 镜位 × 场景）预设矩阵**，每格对应一段 Kontext 自然语言指令。Kontext 的 subject consistency 省去抠图+重合成。
**Excitat 建议**：**这是最贴合 Amazon 8 图公式的形态**。每一格（抓眼球/戳痛点/…）= 一个 preset，每个 preset 下按品类覆写场景描述。

### 推荐架构（给 Excitat）
把**模式 A+B+D 组合**：
1. **顶层**：Amazon 8 图意图路由器（D 预设思想）——8 个节点模板。
2. **中层**：品类分支 Switch（B）——4 条大 branch（硬质 / 软质 / 服装 / 家居）。
3. **底层**：Prompt YAML（A）——品类 + 意图 笛卡尔积模板。
4. **存储**：MongoDB 存 `{category, intent, prompt_template, reference_image_url, lora_stack, controlnet_config}` 文档，Python Workflow 按 `(category, intent)` 查询装配。
未来演进加 C（LoRA 路由）做差异化提升。

---

## 五、一手作者信息（便于后续深挖）

- **risunobushi / Andrea Baioni**：OpenArt + Civitai 双平台，频率分离节点开源在 GitHub（risunobushi/comfyUI_FrequencySeparation_RGB-HSV），v4 是目前社区最完整的产品重光照流水线
- **MyAIForce**：自营站 myaiforce.com，博客有 V2/V4 详细拆解文章
- **mixlab_shadow**：国内团队，LayerStyle 节点作者 chflame163 同圈
- **kijai**：ComfyUI 核心生态贡献者（IC-Light、SAM2、多个热门 Flux 节点）
- **ltdrdata**：Impact Pack 作者，条件分支/Switch 节点生态奠基人
- **Comflowy**：中文团队运营的工作流站，E-commerce 频道有 A Rui 等商业级工作流
- **RunComfy**：云端 ComfyUI 提供方，整理了 Kontext Preset 等精品模板

---
