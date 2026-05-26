from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "experiments" / "20260504_case_extraction"
VALIDATION_DIR = ROOT / "experiments" / "20260504_img2img_validation"
TEMPLATE_DIR = ROOT / "workflow" / "template_cards"
RECIPE_DIR = ROOT / "workflow" / "prompt_recipes"
REF_DIR = ROOT / "references" / "user_cases" / "20260504_lark_examples"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


CASES = [
    {
        "id": "01",
        "file": str(REF_DIR / "01.jpg"),
        "type": "产品图案例 / 案例",
        "summary": "吸尘器/宠物清洁场景案例，展示 3000x3000 主图和多张卖点附图的生成对照。",
        "visual_logic": [
            "产品在真实使用场景中解决具体痛点，宠物毛发、地面、家具形成问题语境。",
            "主图保持产品大面积可见，附图用局部细节和数据徽章证明性能。",
            "场景不只是装饰，要回答“这个产品解决什么问题”。",
        ],
        "prompt_structure": [
            "产品图作为身份源，场景作为转换目标。",
            "写清楚可见问题、产品动作、清洁结果、数据徽章和保留项。",
            "将长卖点改写为短数字和具体视觉动作。",
        ],
        "template_structure": "中心或三分位大产品 + 使用场景 + 2-4 个数字徽章 + 局部细节小图。",
        "scoring_rules": ["产品轮廓不漂移", "痛点是否一眼可懂", "数据徽章是否不抢主体"],
        "not_reusable": ["手机界面、点赞评论区、原帖作者信息", "具体品牌与原始产品外观"],
        "template_card": True,
        "prompt_recipe": True,
    },
    {
        "id": "02",
        "file": str(REF_DIR / "02.jpg"),
        "type": "产品图案例 / 模板展示",
        "summary": "可调支架的结构化卖点图，突出调节范围、角度和竞品对比。",
        "visual_logic": [
            "机械结构类产品适合蓝图式构图，箭头、编号、局部放大解释动作。",
            "竞品对比应压缩成右侧或底部模块，而不是长段文字。",
            "白/浅背景让黑色产品和蓝色 callout 更清晰。",
        ],
        "prompt_structure": [
            "明确产品姿态、中心主体、右侧对比对象、底部对比条。",
            "保留产品机械结构，变化的是 callout、场景和竞品图形。",
        ],
        "template_structure": "左中大主体 + 右侧竞品/限制对比 + 底部 VS 条 + 编号 callout。",
        "scoring_rules": ["结构是否真实可信", "对比关系是否清楚", "文字区是否可后期落版"],
        "not_reusable": ["原产品的具体支架形态", "截图中的社交平台外壳"],
        "template_card": True,
        "prompt_recipe": True,
    },
    {
        "id": "03",
        "file": str(REF_DIR / "03.jpg"),
        "type": "提示词教程 / 方法论",
        "summary": "GPT Image 2 提示词原则：结构化、具体、可见，适合照片级写实、编辑流、图中文字和品牌一致性。",
        "visual_logic": [
            "不是视觉模板，而是提示词质量规则。",
            "强调先写画面中看得见的东西，少堆抽象形容词。",
        ],
        "prompt_structure": ["场景", "主体", "重要细节", "用途", "限制条件"],
        "template_structure": "可转为所有 PromptRecipe 的基础段落结构。",
        "scoring_rules": ["prompt 是否具体可见", "是否分清用途与限制", "是否避免空泛形容词"],
        "not_reusable": ["把整张教程截图当参考图"],
        "template_card": False,
        "prompt_recipe": True,
    },
    {
        "id": "04",
        "file": str(REF_DIR / "04.jpg"),
        "type": "提示词教程 / 评分迭代规则",
        "summary": "TLDR：具体、结构化、编辑时分开变更和保留、文字必须明确、小步迭代且每轮重复不变量。",
        "visual_logic": [
            "编辑式生图需要明确 keep/change 边界。",
            "文字不应交给模型自由发挥，必须指定精确文案、位置和排版，或留空后期叠字。",
        ],
        "prompt_structure": ["Keep", "Change", "Layout", "Text policy", "Negative constraints", "Repair delta"],
        "template_structure": "可转成 repair.recipe.md 和 preserve_product.recipe.md 的规则。",
        "scoring_rules": ["是否复述不变量", "是否只修失败项", "是否避免每轮重写导致漂移"],
        "not_reusable": ["教程截图本身的排版风格"],
        "template_card": False,
        "prompt_recipe": True,
    },
    {
        "id": "05",
        "file": str(REF_DIR / "05.jpg"),
        "type": "模板展示 / PSD 模板",
        "summary": "Amazon/Walmart 紫色 PSD 主附图模板，展示功能格、数字徽章、before/after、人物/使用场景模块。",
        "visual_logic": [
            "紫色品牌底作为统一识别，白色卡片承载信息模块。",
            "2x2 功能格、圆形数字徽章、before/after 和底部小图组合成高密度附图。",
            "PSD 价值在于可编辑文字、图标和产品位，而不是让模型直接复制截图。",
        ],
        "prompt_structure": ["指定紫色/白色商业信息图", "产品主位", "功能格数量", "保留空文字区或精确短词"],
        "template_structure": "品牌色背景 + 2x2 模块 + 大数字徽章 + 对比条 + 人物/场景小图。",
        "scoring_rules": ["信息层级是否清楚", "PSD/叠字是否必要", "缩略图是否不显乱"],
        "not_reusable": ["原 PSD 图形细节和具体文案", "未授权模板素材"],
        "template_card": True,
        "prompt_recipe": True,
    },
    {
        "id": "06",
        "file": str(REF_DIR / "06.jpg"),
        "type": "平台规则 / 方法论",
        "summary": "俄区爆款图要点 1-3：先看产品，大数字短词，信息模块分层。",
        "visual_logic": [
            "主图产品占 60% 以上，中心或黄金三分位，背景低干扰。",
            "卖点用大数字 + 短词，圆/方徽章承载。",
            "层级为产品 -> 卖点徽章 -> 细节图/生活场景。",
        ],
        "prompt_structure": ["product_weight >= 60%", "2-3 badge zones", "1 scene/detail inset", "1-3 visual focus points"],
        "template_structure": "大主体 + 上角徽章 + 底/角场景小图。",
        "scoring_rules": ["0.5 秒识别产品", "数字是否醒目", "是否信息平铺"],
        "not_reusable": ["截图中的中文讲义版式"],
        "template_card": True,
        "prompt_recipe": True,
    },
    {
        "id": "07",
        "file": str(REF_DIR / "07.jpg"),
        "type": "平台规则 / 方法论",
        "summary": "俄区爆款图要点 4-6：本地化短词/图标、信任触点、色彩与品牌节奏一致。",
        "visual_logic": [
            "图标比长文案更快，文案控制在 3-4 字或一行。",
            "质保、配件、使用场景、数量包是转化触点。",
            "主色 + 强对比色，配色不超过 3 色系。",
        ],
        "prompt_structure": ["短词 + icon", "trust badge", "accessory/package strip", "limited palette"],
        "template_structure": "功能 icon 列 + 信任徽章 + 套装/配件底条。",
        "scoring_rules": ["本地化短词是否可读", "信任信息是否前置", "颜色是否抢产品"],
        "not_reusable": ["具体俄文词的误拼风险，生产应人工审核或后期叠字"],
        "template_card": True,
        "prompt_recipe": True,
    },
    {
        "id": "08",
        "file": str(REF_DIR / "08.jpg"),
        "type": "提示词教程 / 方法论",
        "summary": "从参考图反推视觉逻辑：主体形态、比例结构、材质质感、色彩系统、光影关系、空间层次、整体风格。",
        "visual_logic": [
            "参考图应被分析成规则，不应整图直接喂模型。",
            "生活感来自真实道具和使用痕迹，而不是摆拍式秀产品。",
            "技术参数要翻译为视觉卖点，例如耐磨、宠物抓不烂、通行无障碍。",
        ],
        "prompt_structure": ["Reverse visual logic", "Life props", "Visualized benefit", "Style constraints"],
        "template_structure": "可转成 reference_logic_reverse.recipe.md。",
        "scoring_rules": ["是否提取结构而非复制画面", "卖点是否被视觉化", "场景是否像真实生活"],
        "not_reusable": ["整张讲义图作为 style reference"],
        "template_card": False,
        "prompt_recipe": True,
    },
    {
        "id": "09",
        "file": str(REF_DIR / "09.jpg"),
        "type": "模板展示 / 平台案例",
        "summary": "Amazon 排版分享，多场景/多模块板式：户外、工具、功能格、人物使用图混排。",
        "visual_logic": [
            "附图可按任务拆为场景、功能、规格、对比、信任，而不是一张图塞完所有信息。",
            "多场景 grid 适合讲产品使用范围，卡片边界和标题层级必须清晰。",
        ],
        "prompt_structure": ["multi panel grid", "one scene per panel", "consistent lighting", "reserved text header"],
        "template_structure": "2x2 或 3x2 场景格 + 中央/边缘产品锚点 + 每格短标题。",
        "scoring_rules": ["每格是否回答不同问题", "整体是否像商品附图", "缩略图是否不糊成一团"],
        "not_reusable": ["具体 Amazon 贴图和原图素材"],
        "template_card": True,
        "prompt_recipe": True,
    },
    {
        "id": "10",
        "file": str(REF_DIR / "10.jpg"),
        "type": "产品图案例 / 详情图案例",
        "summary": "工业产品深色详情页案例，黑灰背景、橙色强调、横纵模块和局部特写。",
        "visual_logic": [
            "B2B/工具/工业类产品可用深色背景建立专业感。",
            "大产品主图搭配材质、便携、性能、接口等细节模块。",
            "图标规格与局部放大比生活场景更能建立信任。",
        ],
        "prompt_structure": ["dark modular detail", "macro detail panels", "orange/blue accent", "technical icon specs"],
        "template_structure": "深色背景 + 主产品 + 3-5 个横纵 detail panels + icon/spec 行。",
        "scoring_rules": ["是否专业可信", "细节是否真实", "深色背景是否吞掉产品轮廓"],
        "not_reusable": ["原工业产品和原文案"],
        "template_card": True,
        "prompt_recipe": True,
    },
    {
        "id": "11",
        "file": str(REF_DIR / "11.jpg"),
        "type": "产品图案例 / Ozon 案例",
        "summary": "Ozon 宠物产品图案例，展示俄区主图用大产品、强对比背景、卖点徽章和场景小图吸引点击。",
        "visual_logic": [
            "主图首先解决“这是什么、值不值得点、可信不可信”。",
            "宠物用品用真实宠物/使用状态场景提高理解速度。",
            "灰暗/虚化场景搭配明亮产品和徽章，增强缩略图跳出。",
        ],
        "prompt_structure": ["large product", "dark or low-tone background", "2-3 badges", "pet usage inset"],
        "template_structure": "Ozon 大主体 + 数字徽章 + 右侧 icon list + 场景小图 + 底部信任条。",
        "scoring_rules": ["产品是否最大", "点击理由是否 1 秒内明确", "背景是否支撑而不干扰"],
        "not_reusable": ["具体宠物图和俄文排版应重新生成/审核"],
        "template_card": True,
        "prompt_recipe": True,
    },
    {
        "id": "12",
        "file": str(REF_DIR / "12.jpg"),
        "type": "平台规则 / 方法论",
        "summary": "Ozon 用户浏览逻辑：0.5 秒知道是什么，1 秒判断是否值得点，3 秒建立信任。",
        "visual_logic": [
            "主图不是艺术品，是信息筛选和快速表达。",
            "产品 60%+，数字代替长文案，主体最大、2-3 个徽章、1 个场景或细节图。",
            "强对比背景组合按品类匹配：黑绿科技/户外，灰橙工具，白蓝家电。",
        ],
        "prompt_structure": ["0.5s recognition", "1s click reason", "3s trust", "large number badges"],
        "template_structure": "高转化主图标准结构。",
        "scoring_rules": ["0.5/1/3 秒测试", "数字是否替代长文", "是否禁止小字堆积"],
        "not_reusable": ["直接照搬俄文或社媒截图"],
        "template_card": True,
        "prompt_recipe": True,
    },
    {
        "id": "13",
        "file": str(REF_DIR / "13.jpg"),
        "type": "平台规则 / 模板结构",
        "summary": "Ozon 万能主图结构：渐变/虚化背景、产品主体最大、左上核心数字卖点、右侧 2-4 icon、底部配件/保修信息。",
        "visual_logic": [
            "信任必须可视化：保修、套装、电池、配件等做成标签/徽章。",
            "场景图是转化加速器，要回答买了能干什么。",
            "新手坑：字太多、颜色太杂、没重点、没数字。",
        ],
        "prompt_structure": ["background gradient", "largest product", "top-left numeric benefit", "right icon list", "bottom trust strip"],
        "template_structure": "OzonHighConversionMainCard 的直接来源。",
        "scoring_rules": ["点击率结构是否完整", "坑点是否规避", "场景是否回答用途"],
        "not_reusable": ["原帖 UI 和具体截断文本"],
        "template_card": True,
        "prompt_recipe": True,
    },
]


TEMPLATES = [
    ("HeroCleanCenterCard", "hero", "search stop main image", "这是什么？我能一眼认出产品吗？", "centered large product on clean studio or soft gradient background", "65-80%", "minimal white/gray, accurate shadow"),
    ("HeroLifestyleSceneCard", "lifestyle", "show ownership and usage desire", "买了之后会在哪用、看起来靠谱吗？", "large product in a believable scene with one usage cue and light props", "45-60%", "natural lifestyle palette with product-matching accents"),
    ("FeatureRightTextCard", "infographic", "explain 2-3 key benefits quickly", "它比普通产品强在哪里？", "product left/center, right text/icon stack, bottom proof strip", "45-60%", "clean light background, one accent color"),
    ("CalloutAroundProductCard", "infographic", "turn physical details into proof", "这些结构/按钮/接口有什么用？", "product centered with radial callout lines, numbered micro labels", "55-70%", "technical white/blue or gray/orange"),
    ("MultiSceneGridCard", "detail_page", "show multiple usage contexts", "这个产品适合哪些场景？", "2x2 or 3x2 grid, one scene per panel, consistent product anchor", "25-40%", "consistent panels, restrained header bars"),
    ("BeforeAfterSplitCard", "comparison", "prove outcome difference", "用它前后有什么变化？", "left/right split or top/bottom comparison with product bridge", "35-55%", "high contrast before/after palette"),
    ("DetailMacroCard", "proof_detail", "prove material, texture, interface, or craftsmanship", "细节可靠吗？会不会廉价？", "macro detail close-up plus small full-product locator", "35-50%", "high clarity macro lighting"),
    ("PackageTrustCard", "proof_detail", "reduce purchase anxiety", "套装、配件、保修、规格是否清楚？", "package/accessory flat-lay with trust badges and short labels", "35-55%", "clean catalog palette with trust color"),
    ("OzonHighConversionMainCard", "hero", "maximize marketplace thumbnail click", "0.5 秒知道是什么，1 秒知道为什么点，3 秒建立信任吗？", "large product, low-tone/gradient background, numeric badge top-left, icon list right, scene/detail inset, bottom trust strip", "60-75%", "strong contrast, dark/low-tone background with bright badges"),
    ("IndustrialDarkDetailCard", "detail_page", "make tools and B2B products look professional", "这个工具/设备是否专业耐用？", "dark modular board, main product plus detail panels and spec icons", "35-55%", "black/charcoal with orange/blue accent"),
    ("JapaneseRakutenTrustBannerCard", "detail_page", "mobile vertical trust and proof", "品牌可信、功效明确、证据够吗？", "vertical dense banner, soft trust background, ribbons/badges, icons, small proof cards", "30-45%", "soft white/pastel with red/gold/blue trust accents"),
    ("AmazonPurpleFeatureGridCard", "infographic", "PSD-friendly Amazon feature attachment image", "卖点是否被模块化且易后期改字？", "purple brand background, 2x2 feature cards, big number badge, before/after or people-use module", "30-50%", "purple/white system with controlled accent colors"),
]


def template_card(template_id, image_role, business_goal, viewer_question, layout_pattern, product_weight, color_style):
    return {
        "template_id": template_id,
        "image_role": image_role,
        "business_goal": business_goal,
        "viewer_question": viewer_question,
        "layout_pattern": layout_pattern,
        "product_weight": product_weight,
        "text_zones": [
            {"id": "headline_zone", "position": "top or primary safe area", "policy": "short phrase or reserve for overlay"},
            {"id": "support_zone", "position": "side or bottom", "policy": "2-4 short labels only"},
        ],
        "badge_zones": [
            {"id": "numeric_badge", "position": "top-left/top-right", "content": "one large number or proof point"},
            {"id": "trust_badge", "position": "bottom/side", "content": "warranty, package quantity, certification, accessory"},
        ],
        "scene_zones": [
            {"id": "main_scene", "position": "background or panel", "role": "usage context or mood"},
            {"id": "inset_scene", "position": "corner/grid cell", "role": "detail, result, before/after, or usage state"},
        ],
        "color_style": color_style,
        "prompt_keep_rules": [
            "Keep exact product shape, color, material, visible labels/logos, ports, buttons, seams, proportions, and package/accessory structure.",
            "Keep commercial hierarchy: product first, then 1-3 proof points, then scene/detail support.",
        ],
        "prompt_change_rules": [
            "Change background, usage scene, props, lighting, badge copy, and panel layout to fit the selected product and marketplace.",
            "Translate technical parameters into visible proof instead of long copy.",
        ],
        "negative_constraints": [
            "No product deformation, no changed color, no extra parts, no fake accessories, no unreadable fake text, no busy background, no tiny text blocks.",
            "Do not copy the phone screenshot UI or original post layout.",
        ],
        "text_policy": "Prefer reserve_text_zone or overlay_later for final marketplace copy; model may render only short exact numbers/words in drafts.",
        "best_for_categories": ["small appliance", "tools", "pet products", "digital accessories", "backpack/storage", "home goods"],
        "best_for_marketplaces": ["Amazon", "Ozon", "Rakuten", "Walmart", "eMAG"],
        "scoring_focus": [
            "product_fidelity",
            "product_scale",
            "template_compliance",
            "selling_point_clarity",
            "commercial_quality",
            "text_safety",
            "marketplace_fit",
            "repairability",
        ],
    }


RECIPE_NAMES = [
    ("preserve_product.recipe.md", "保产品一致性编辑", "Product image is the source of truth. Reference images can only provide layout/style logic."),
    ("reference_logic_reverse.recipe.md", "从截图或参考图反推视觉逻辑", "Reference image is analysis input, not a direct generation reference unless cleaned."),
    ("scene_only_background.recipe.md", "只生成背景，后期合成真实产品", "Product image defines reserved slot; output must not include product-like objects."),
    ("feature_callout.recipe.md", "卖点 callout / 结构解释图", "Product image is source of truth; callouts explain visible structures."),
    ("multi_scene_grid.recipe.md", "多场景 grid 附图", "Product image anchors identity; each panel has one distinct usage scenario."),
    ("comparison_vs.recipe.md", "Before/After 或 VS 对比图", "Product image is hero; comparison side can be symbolic and must not fake competitor brands."),
    ("text_overlay.recipe.md", "文字区/后期叠字", "Model should reserve clean text zones unless exact short text is low risk."),
    ("repair.recipe.md", "评分后修复提示词", "Only repair failed dimensions while repeating product invariants."),
]


def recipe_text(filename: str, title: str, reference_role: str) -> str:
    return f"""# {title}

## 使用场景

{title}。用于把“案例方法论 -> TemplateCard -> 结构化 prompt -> 图生图/生成 -> 评分 -> 修复”连成可重复流程。

## 输入图角色

- Product source: 真实产品图或干净白底产品图，是产品身份唯一真值。
- Optional clean reference: 只提供构图、色彩、光影、信息层级或场景逻辑。
- Phone screenshot: 只能用于分析方法论，不能整张当 reference image。

## reference role

{reference_role}

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
- Reference logic: use only the commercial layout logic from {{template_id}}.
Keep: {{immutable_product_traits}}.
Change: {{scene_or_layout_changes}}.
Visible scene: {{concrete_visible_scene}}.
Layout: {{product_weight}}, {{text_zones}}, {{badge_zones}}, {{scene_zones}}.
Text policy: {{reserve_or_exact_text}}.
Negative constraints: no product drift, no extra parts, no unreadable text.
```

## Flux / img2img 写法

```text
Use the product image as the strongest identity reference. Preserve exact silhouette, color, materials, ports, labels and proportions. Apply the {{template_id}} layout: {{layout_pattern}}. Generate a commercial ecommerce scene with {{visible_scene}}. Leave {{text_zones}} clean for overlay. Avoid changing the product or adding accessories.
```

## Nano Banana 写法

```text
Use the uploaded product as the exact product. Make a {{image_role}} ecommerce image using this simple layout: {{layout_pattern}}. Product must stay unchanged and large. Add only {{scene_or_badges}}. Keep text minimal or leave clean empty text areas.
```

## repair 写法

```text
Keep the product unchanged. Only fix these failed dimensions: {{failed_scores}}.
Make the product {{scale_fix}}, improve {{selling_point_fix}}, adjust {{layout_fix}}, and keep {{text_policy}}.
Do not alter product geometry, color, logo, material, ports, seams, or accessories.
```
"""


PRODUCTS = [
    {
        "id": "pink_backpack",
        "category": "backpack/storage",
        "source": ROOT / "experiments" / "20260504_backpack_mvp" / "inputs" / "product_source.jpg",
        "traits": "pink backpack, front pocket, gold zippers, side pockets, top handle, shoulder straps, soft nylon texture",
        "selling_points": ["large capacity", "organized pockets", "giftable clean look", "daily commute and travel"],
    },
    {
        "id": "portable_tire_inflator",
        "category": "tool/auto accessory",
        "source": ROOT / "phase0_results" / "output_st08_test" / "hero_00_product_1776389318071.jpg",
        "traits": "black and yellow portable tire inflator, handle, coiled hose, digital 150 PSI display, nozzle accessories",
        "selling_points": ["150 PSI", "portable emergency inflation", "car/bike/ball adapters", "digital pressure readout"],
    },
    {
        "id": "usb_cable_accessory_set",
        "category": "digital accessories",
        "source": ROOT / "phase0_results" / "output_flux_kontext_test" / "ref3_accessories_1776441204792.jpg",
        "traits": "black braided HDMI cable, black braided USB-C cable, small black USB receiver, flat lay on white background",
        "selling_points": ["braided durability", "multi-device connectivity", "organized cable ties", "plug-and-play accessory set"],
    },
]


RUNS = [
    ("pink_backpack", "main", "HeroCleanCenterCard", "Amazon", "clean marketplace hero with the backpack centered large, soft white studio background, one subtle capacity badge area"),
    ("pink_backpack", "selling_point", "FeatureRightTextCard", "Amazon", "backpack large left, right reserved text/icon stack for pockets and capacity, bottom small organizer proof strip"),
    ("pink_backpack", "scene", "HeroLifestyleSceneCard", "Rakuten", "backpack in a bright commuter cafe or travel entryway, warm lifestyle props, no text"),
    ("pink_backpack", "detail_comparison", "MultiSceneGridCard", "Amazon", "four panels showing commute, travel, school, gift use, with backpack identity consistent in each panel"),
    ("portable_tire_inflator", "main", "OzonHighConversionMainCard", "Ozon", "large tire inflator on dark gray/orange background, 150 PSI numeric badge, right icon list zones, bottom accessory trust strip"),
    ("portable_tire_inflator", "selling_point", "CalloutAroundProductCard", "Ozon", "centered inflator with callout arrows to hose, digital display, adapters, handle, short labels reserved"),
    ("portable_tire_inflator", "scene", "HeroLifestyleSceneCard", "Ozon", "roadside car trunk emergency inflation scene, product foreground large, no brand hallucination"),
    ("portable_tire_inflator", "detail_comparison", "IndustrialDarkDetailCard", "Amazon", "dark modular detail board with macro panels for display, hose, adapters, rugged casing"),
    ("usb_cable_accessory_set", "main", "PackageTrustCard", "Amazon", "clean flat-lay package trust image, cable set large, compatibility and included-items badge zones"),
    ("usb_cable_accessory_set", "selling_point", "AmazonPurpleFeatureGridCard", "Amazon", "purple/white 2x2 feature grid, cable set anchor, braided durability and plug-and-play zones"),
    ("usb_cable_accessory_set", "scene", "JapaneseRakutenTrustBannerCard", "Rakuten", "vertical trust banner style with clean desk setup scene, cable use case, soft trust badges"),
    ("usb_cable_accessory_set", "detail_comparison", "BeforeAfterSplitCard", "eMAG", "before/after split showing messy weak cables versus organized braided cables, product set unchanged on clean side"),
]


def build_case_outputs() -> None:
    lines = ["# 20260504 Lark Examples Case Extraction", "", "说明：这些都是手机截图，只提取方法论、构图逻辑和 prompt 结构，不把整张截图当 reference image。", ""]
    for c in CASES:
        lines.extend([
            f"## {c['id']}. {Path(c['file']).name}",
            "",
            f"- 类型：{c['type']}",
            f"- 摘要：{c['summary']}",
            "- 可复用的视觉逻辑：",
        ])
        lines.extend([f"  - {x}" for x in c["visual_logic"]])
        lines.append("- 可复用的提示词结构：")
        lines.extend([f"  - {x}" for x in c["prompt_structure"]])
        lines.extend([
            f"- 可复用的模板结构：{c['template_structure']}",
            "- 可复用的评分规则：",
        ])
        lines.extend([f"  - {x}" for x in c["scoring_rules"]])
        lines.extend([
            "- 不适合复用的部分：",
        ])
        lines.extend([f"  - {x}" for x in c["not_reusable"]])
        lines.extend([
            f"- 是否能转成 TemplateCard：{'是' if c['template_card'] else '否'}",
            f"- 是否能转成 PromptRecipe：{'是' if c['prompt_recipe'] else '否'}",
            "",
        ])
    write_text(CASE_DIR / "case_extraction.md", "\n".join(lines))
    write_json(CASE_DIR / "case_index.json", CASES)


def build_templates() -> None:
    for args in TEMPLATES:
        card = template_card(*args)
        write_json(TEMPLATE_DIR / f"{card['template_id']}.json", card)


def build_recipes() -> None:
    for filename, title, role in RECIPE_NAMES:
        write_text(RECIPE_DIR / filename, recipe_text(filename, title, role))


def compile_prompt(product, run, template):
    return f"""Use case: ads-marketing
Asset type: marketplace ecommerce image, {run[1]}
Primary request: Create a {run[1]} image for {run[3]} using TemplateCard {run[2]}.

Input images:
- Product image: source of truth. Preserve exact product identity.
- Screenshot-derived reference logic: extracted from 20260504 Lark examples only as methodology, not as a direct visual reference.

Product truth:
{product['traits']}

Selling points:
{'; '.join(product['selling_points'])}

Reference logic:
{template['layout_pattern']}
Viewer question: {template['viewer_question']}

Keep:
- Exact product shape, color, material, proportions, labels/logos if any, ports, zippers, seams, buttons, accessories and visible details.
- Product should stay commercially recognizable in thumbnail.

Change:
- Build this visual concept: {run[4]}.
- Adapt background, lighting, props, badge zones, and scene details to the product and marketplace.

Layout:
- Product visual weight: {template['product_weight']}.
- Text zones: reserve clean areas for later overlay unless a short number such as 150 PSI is explicitly present on the real product.
- Badge zones: use no more than 2-3 short proof badges.
- Scene zones: one clear scene/detail support area unless this is a grid template.

Text policy:
Reserve clean text zones for final copy. Avoid long generated text. If rendering text, use only short exact terms from the source product or selling points.

Negative constraints:
No product deformation. No changed product color. No extra ports, fake accessories, duplicated product, unreadable fake text, watermark, copied screenshot UI, or cluttered tiny labels.

Output:
Square or vertical marketplace-ready commercial image, sharp product focus, clear hierarchy, realistic lighting, ecommerce quality."""


def initial_score_for(run_role: str):
    # Initial score is a pre-output risk estimate. It will be replaced or confirmed
    # after generated output inspection.
    base = {
        "product_fidelity": 6.5,
        "product_scale": 7.0,
        "template_compliance": 7.0,
        "selling_point_clarity": 6.5,
        "commercial_quality": 7.0,
        "text_safety": 7.5,
        "marketplace_fit": 7.0,
        "repairability": 8.0,
    }
    if run_role in {"scene", "detail_comparison"}:
        base["product_fidelity"] = 6.0
        base["repairability"] = 7.5
    return base


def repair_prompt(product, run, score):
    failed = [k for k, v in score.items() if isinstance(v, (int, float)) and v < 7]
    if not failed:
        failed = ["none yet; inspect generated output before next iteration"]
    return f"""# Repair Prompt

Product: {product['id']}
Image role: {run[1]}
TemplateCard: {run[2]}

Failed or weak dimensions:
{', '.join(failed)}

Repair instruction:
Keep the product unchanged. Preserve exact product shape, color, material, proportions, labels/logos if any, ports, zippers, seams, buttons, accessories and all visible details.

Only fix the weak dimensions:
- Make the product larger and clearer if product_scale or product_fidelity is weak.
- Reduce background clutter and keep only one clear selling point if selling_point_clarity is weak.
- Re-align the composition to {run[2]} if template_compliance is weak.
- Reserve clean empty text zones if text_safety is weak.

Do not alter product geometry, product color, logo/label, material, ports, seams, zippers, cable ends, hose, display, adapters, or accessories. No fake text, no new product parts, no duplicate product.
"""


def build_validation_plan() -> None:
    source_dir = VALIDATION_DIR / "source_products"
    source_dir.mkdir(parents=True, exist_ok=True)
    product_by_id = {}
    for p in PRODUCTS:
        out = source_dir / f"{p['id']}{p['source'].suffix.lower()}"
        shutil.copy2(p["source"], out)
        pp = dict(p)
        pp["source_saved"] = str(out)
        pp["source"] = str(p["source"])
        product_by_id[p["id"]] = pp

    cards = {Path(f).stem: json.loads(Path(f).read_text(encoding="utf-8")) for f in TEMPLATE_DIR.glob("*.json")}
    runs = []
    for i, run in enumerate(RUNS, start=1):
        product = product_by_id[run[0]]
        template = cards[run[2]]
        run_id = f"{i:02d}_{run[0]}_{run[1]}_{run[2]}"
        run_dir = VALIDATION_DIR / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        source_copy = run_dir / f"source_product{Path(product['source_saved']).suffix}"
        shutil.copy2(product["source_saved"], source_copy)
        write_json(run_dir / "template_card.json", template)
        prompt = compile_prompt(product, run, template)
        write_text(run_dir / "compiled_prompt.md", prompt)
        score = initial_score_for(run[1])
        write_json(run_dir / "score.json", {
            "status": "pending_output_inspection",
            "scoring_scale": "0-10",
            "scores": score,
            "needs_repair_prompt": any(v < 7 for v in score.values()),
            "notes": "Initial risk score before generation. Update after inspecting output image.",
        })
        write_text(run_dir / "repair_prompt.md", repair_prompt(product, run, score))
        write_json(run_dir / "generation_request.json", {
            "run_id": run_id,
            "product_id": run[0],
            "image_role": run[1],
            "template_id": run[2],
            "marketplace": run[3],
            "model_priority": ["codex_imagegen_builtin", "openai_gpt_image_2_api", "fal_gpt_image_2", "fal_nano_banana_2", "fal_flux_kontext"],
            "model_name": None,
            "model_parameters": {
                "aspect_ratio": "1:1",
                "output_format": "png_or_jpeg",
                "input_images": [str(source_copy)],
            },
            "output_image": None,
            "fallback_reason": None,
        })
        runs.append({
            "run_id": run_id,
            "run_dir": str(run_dir),
            "product_id": run[0],
            "source_product_image": str(source_copy),
            "template_id": run[2],
            "image_role": run[1],
            "marketplace": run[3],
            "compiled_prompt": str(run_dir / "compiled_prompt.md"),
            "score": str(run_dir / "score.json"),
            "repair_prompt": str(run_dir / "repair_prompt.md"),
            "output_image": None,
        })

    write_json(VALIDATION_DIR / "experiment_plan.json", {
        "date": "2026-05-04",
        "method": "screenshot methodology -> TemplateCard -> PromptRecipe -> image generation/editing -> scoring -> repair",
        "products": list(product_by_id.values()),
        "runs": runs,
    })

    readme = """# 20260504 Img2Img Validation

## 实验目标

验证“案例方法论 -> TemplateCard -> 结构化 prompt -> 图生图/生成 -> 评分 -> 修复”是否能产出实际可用的电商图。

## 当前策略

优先调用 Codex built-in imagegen。若 built-in imagegen 不能基于本地输入图编辑或不能把输出落盘到项目，则记录失败原因，并 fallback 到可落盘的 OpenAI GPT Image 2 API / fal.ai / Nano Banana / Flux。

## 产品图

- pink_backpack: 背包/收纳。
- portable_tire_inflator: 工具/车载配件。
- usb_cable_accessory_set: 数码配件。

## 模型/方案结果

待生成后更新。每个 run 目录包含 source_product、template_card、compiled_prompt、generation_request、output_image、score、repair_prompt。

## PSD 判断

PSD 只在文字准确、可编辑交付、固定落版或批量复用时值得使用。本实验先验证结构化 prompt 和生成链路，不为了 PSD 而 PSD。
"""
    write_text(VALIDATION_DIR / "README.md", readme)


def main():
    build_case_outputs()
    build_templates()
    build_recipes()
    build_validation_plan()


if __name__ == "__main__":
    main()
