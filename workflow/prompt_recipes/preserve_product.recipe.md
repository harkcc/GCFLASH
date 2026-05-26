# 保产品一致性编辑

## 使用场景

保产品一致性编辑。用于把“案例方法论 -> TemplateCard -> 结构化 prompt -> 图生图/生成 -> 评分 -> 修复”连成可重复流程。

## 输入图角色

- Product source: 真实产品图或干净白底产品图，是产品身份唯一真值。
- Optional clean reference: 只提供构图、色彩、光影、信息层级或场景逻辑。
- Phone screenshot: 只能用于分析方法论，不能整张当 reference image。

## reference role

Product image is the source of truth. Reference images can only provide layout/style logic.

## keep

- Keep exact product identity: shape, color, material, size ratio, labels, logos, seams, ports, buttons, zipper/hardware/accessory structure.
- Keep marketplace visual hierarchy from the selected TemplateCard: product first, proof second, scene/detail third.
- Keep 1-3 visual focus points; do not spread attention across many small elements.

## change

- Change background, usage context, lighting mood, props, badge wording, panel arrangement, and marketplace style.
- Replace long selling copy with visible proof: numbers, icons, result scenes, detail close-ups, or trust badges.

## visible scene

Describe concrete visible objects only: product placement, surface, background depth, usage state, hand/pet/environment if relevant, badge/icon areas, empty text zones, and shadows.

## layout

- Product weight: follow TemplateCard, usually 60%+ for main images and 35-55% for secondary images.
- Text zones: name exact safe areas; reserve clean areas when text accuracy matters.
- Badge zones: 1 large numeric proof, 1-2 short trust/function badges.
- Scene zones: one primary scene or one detail inset unless using MultiSceneGrid.

## text policy

- Production default: reserve clean text zones and overlay later.
- Model text allowed only for short exact numbers/words such as “2000W”, “3 YEARS”, “5 PCS”.
- Never ask the model to invent marketplace copy.

## negative constraints

No product deformation, no changed color/material, no added fake parts, no duplicate product, no unreadable fake text, no copied screenshot UI, no cluttered tiny labels, no watermark, no brand hallucination.

## GPT Image 2 写法

```text
Create a marketplace-ready ecommerce image.
Reference roles:
- Product image: source of truth; preserve exact product identity.
- Reference logic: use only the commercial layout logic from {template_id}.
Keep: {immutable_product_traits}.
Change: {scene_or_layout_changes}.
Visible scene: {concrete_visible_scene}.
Layout: {product_weight}, {text_zones}, {badge_zones}, {scene_zones}.
Text policy: {reserve_or_exact_text}.
Negative constraints: no product drift, no extra parts, no unreadable text.
```

## Flux / img2img 写法

```text
Use the product image as the strongest identity reference. Preserve exact silhouette, color, materials, ports, labels and proportions. Apply the {template_id} layout: {layout_pattern}. Generate a commercial ecommerce scene with {visible_scene}. Leave {text_zones} clean for overlay. Avoid changing the product or adding accessories.
```

## Nano Banana 写法

```text
Use the uploaded product as the exact product. Make a {image_role} ecommerce image using this simple layout: {layout_pattern}. Product must stay unchanged and large. Add only {scene_or_badges}. Keep text minimal or leave clean empty text areas.
```

## repair 写法

```text
Keep the product unchanged. Only fix these failed dimensions: {failed_scores}.
Make the product {scale_fix}, improve {selling_point_fix}, adjust {layout_fix}, and keep {text_policy}.
Do not alter product geometry, color, logo, material, ports, seams, or accessories.
```
