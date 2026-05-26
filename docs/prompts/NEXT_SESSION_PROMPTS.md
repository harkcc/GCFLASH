# Next Session Prompts

Use these prompts when opening a new Codex/Goal conversation.

## Prompt 1: Continue Framework Build

```text
你现在接手 /Users/cc/Desktop/photo_show 项目。请先读取：
- docs/ECOM_IMAGE_AGENT_ARCHITECTURE.md
- workflow/agent_flow/ecommerce_image_agent_v0.md
- skills/ecommerce-image-suite/SKILL.md
- skills/ecommerce-image-suite/references/*.md
- workflow/template_cards/*.json
- workflow/prompt_recipes/*.md
- workflow/scorecards/ecommerce_multimodel_scorecard.json
- workflow/suite_plans/ecommerce_5_to_8_suite_plan.json

目标：把 ecommerce-image-suite 从文档骨架推进成可执行的 v0 工作流。

请完成：
1. 检查现有 12 个 TemplateCard 是否字段完整，输出缺口清单。
2. 创建一个 run folder 规范和一个最小样例 ProductTruthPack。
3. 写一个 prompt compiler 设计方案：输入 ProductTruthPack + TemplateCard + PromptRecipe，输出 compiled_prompt.md。
4. 写一个 scoring/review 的 JSON 输出规范。
5. 不要重构整个项目，不要删除已有实验结果。

最后输出：已完成文件、还缺什么、下一步如何跑第一轮真实 SKU。
```

## Prompt 2: Run One SKU Validation

```text
你在 /Users/cc/Desktop/photo_show 中继续电商 AI 套图验证。请使用 skills/ecommerce-image-suite/SKILL.md 的流程。

目标：选择一个本地 product image，跑通单 SKU 的 5 张图方案，但如果无法直接调用生图工具，就先生成完整 generation_request 和 compiled prompts。

要求：
1. 从 photo/ 或 experiments/*/inputs 中选择一个清晰产品图。
2. 建 ProductTruthPack，必须列出 immutable_traits、allowed_changes、forbidden_changes。
3. 生成 SellingPointPlan，不能编造产品参数。
4. 根据 workflow/suite_plans/ecommerce_5_to_8_suite_plan.json 选择 5 个 slot。
5. 每个 slot 选择一个 TemplateCard。
6. 为每张图生成 compiled_prompt.md。
7. 如果可用，调用当前 Codex 生图能力生成候选图；如果不可用，保存 generation_request.json。
8. 按 ecommerce_multimodel_scorecard 输出 score.json 和 repair_prompt.md。

重点验证：产品比例、产品真实度、文字是否需要 PSD/overlay、套图风格一致性。
```

## Prompt 3: OpenDesign And OSS Deep Dive

```text
请在 /Users/cc/Desktop/photo_show 中继续研究 OpenDesign 与相关开源项目，目标不是泛泛介绍，而是提炼可迁移到电商生图系统的机制。

先读：
- tools/open-design/README.md
- tools/open-design/docs/skills-protocol.md
- tools/open-design/packages/contracts/src/prompts/system.ts
- tools/open-design/skills/critique/SKILL.md
- tools/open-design/skills/tweaks/SKILL.md
- tools/open-design/craft/*.md
- skills/ecommerce-image-suite/SKILL.md

然后调研这些 upstream/相邻项目：
- alchaincyf/huashu-design
- op7418/guizang-ppt-skill
- VoltAgent/awesome-design-md
- bergside/awesome-design-skills
- referodesign/refero_skill
- OpenCoworkAI/open-codesign
- multica-ai/multica

输出一份 docs/OPEN_DESIGN_OSS_TRANSFER_REPORT.md：
1. 每个项目能借什么。
2. 哪些不能直接用。
3. 如何映射到 ProductTruthPack、TemplateCard、PromptRecipe、Scorecard、PSDManifest。
4. 对我们当前项目的优先级排序。
5. 给出下一步最小实现任务。

要求带来源链接，不能把 OpenDesign 当成直接生图模型。
```

## Prompt 4: PSD Template Validation

```text
你在 /Users/cc/Desktop/photo_show 中继续 PSD 模板验证。

先读：
- workflow/psd_templates/psd_template_contract.md
- skills/ecommerce-image-suite/references/brand_frame.md
- experiments/20260504_img2img_validation/psd_validation/*
- tools/bggg-skills/bggg-creator-image2psd 相关文件

目标：验证 PSD 在什么情况下对电商生图有实际价值。

请完成：
1. 总结当前 PSD 验证结果的真实能力边界：哪些能用，哪些不能用。
2. 设计 PSDManifest v1，覆盖 background、product、brand_frame、text、badge、icon、inset。
3. 用一个简单产品图创建 1 个新的 PSD assembly 测试，要求至少分层：background、product、brand frame、headline、badge、footer。
4. 输出 preview PNG、PSD、manifest JSON。
5. 明确说明文字是不是原生可编辑文本；如果不是，如何用 manifest 补偿。

不要夸大 PSD 效果，重点看可控性和后续模板复用。
```

## Prompt 5: Brand Frame Extraction

```text
我会提供品牌图、门框风格图、PSD 或参考图。请在 /Users/cc/Desktop/photo_show 中用 ecommerce-image-suite 的方式处理。

目标：把品牌素材转成可复用 BrandFrameSpec，而不是简单贴图。

请完成：
1. 读取所有品牌参考图。
2. 提取 palette、frame geometry、logo slot、badge style、text safe area、do_not rules。
3. 写入 workflow/brand_frames/<brand_frame_id>.json。
4. 更新或创建一个 Ecommerce DESIGN.md。
5. 给出 3 个可用 TemplateCard 适配建议：主图、卖点图、详情图。
6. 判断哪些部分适合 prompt 控制，哪些必须用 PSD/HTML/Pillow overlay。
```
