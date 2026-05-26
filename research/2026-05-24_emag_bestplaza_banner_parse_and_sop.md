# eMAG BestPlaza / Qoltec Banner 拆解、HTML 详情与 SOP

日期：2026-05-24  
工作目录：`/Users/cc/Desktop/photo_show`

## 1. 当天采集结果

### shanggvu / Besplaz 店铺

数据目录：

- [Chrome 采集目录](/Users/cc/Desktop/photo_show/references/user_cases/20260524_emag_shanggvu_detail_case_chrome)
- [scrape_summary.json](/Users/cc/Desktop/photo_show/references/user_cases/20260524_emag_shanggvu_detail_case_chrome/scrape_summary.json)
- [scrape_summary.md](/Users/cc/Desktop/photo_show/references/user_cases/20260524_emag_shanggvu_detail_case_chrome/scrape_summary.md)

结果：

- 店铺主商品区：`46` 个商品卡片。
- 已生成 `46` 个 `description_meta.json`。
- 成功采集到详情 HTML：`45 / 46`。
- 未采集到详情 HTML：`1 / 46`，商品 `D617222BM`，页面未命中可用 description 容器。
- 详情图片总数：`347`。
- 有详情图的产品：`44 / 45`。
- 有 GIF 的产品：`42 / 45`。
- GIF 总数：`42`。
- 含 table 的产品：`40 / 45`。
- 详情图最大每行：`44` 个产品都是 `1`，符合单列长流。

### 图片尺寸确认

BestPlaza / shanggvu 详情图片尺寸规律：

- 品牌动图常见原始尺寸：`1200 x 480`
- 前台常见渲染尺寸：`1140 x 456`
- 大量详情静态图原始尺寸：`4000 x 2400`、`4000 x 1600`、`3880 x 2400`
- 前台高频渲染尺寸：`1140 x 456`、`1140 x 705`、`1140 x 684`

结论：

- 现有卖家默认生产的是 `1140px` 宽详情图。
- 我们后续生产可以保留 `1140px` 作为 eMAG 实战兼容尺寸。
- 如果要做更通用和更轻量的模板，也可以导出 `800px` 版本，但 BestPlaza 这套实战样本主要是 `1200/1140` 系。

## 2. Banner 类型拆解

### 类型 A：品牌信任动图 Banner

样本：

- `https://emag.v9kj.com/Brand-Intro-BestPlaza-RO-General.gif`
- `https://emag.v9kj.com/Brand-Intro-BestPlaza-RO-Headphone.gif`

尺寸：

- 原图：`1200 x 480`
- 前台渲染：约 `1140 x 456`

结构：

- 黑色高级背景。
- 左侧大品牌名 / slogan / 服务图标。
- 右侧真人 + 包裹 / 产品使用场景。
- 侧边或主体可以做轻微动效，用 GIF 承载。
- 服务点通常是 3 个，不做太多。

Prompt 模板：

```text
Create a premium dark ecommerce brand-introduction banner for an eMAG product detail page.
Canvas: 1200x480, single wide horizontal banner.
Background: matte black / deep charcoal, subtle dotted halftone or light streak texture, premium marketplace style.
Left side: large brand name area, short slogan area, 3 service cue icon slots near the bottom.
Right side: friendly realistic European model or couple, holding a plain shipping box or interacting naturally with the product category.
Composition: strong left-to-right reading order, left 55% reserved for deterministic text overlay, right 45% human/product scene.
Mood: trustworthy, familiar, official-store feeling, warm but not luxury fashion.
Avoid: fake eMAG logo, unsupported service claims, discount badges unless sourced, unreadable generated text, clutter, distorted hands.
Output: no final text baked in if we plan deterministic overlay; use placeholder-free image background.
```

适配变量：

- `brand_name`
- `slogan`
- `service_cues`
- `category_scene`
- `model_type`
- `accent_color`
- `motion_elements`

可变体：

- 黑金高级感
- 蓝白平台熟悉感
- 产品类目色调，比如美妆紫、工具黄、车品蓝黑
- 真人换成产品 + 包装
- 静态图 / GIF 两版

### 类型 B：产品技术横幅 Banner

样本：

- [D978TDYBM 目标页](/Users/cc/Desktop/photo_show/references/user_cases/20260524_emag_qoltec_d978tdybm/target_summary.json)
- 首图：`https://i.postimg.cc/RVpB0cjt/1400x400-baner-EV.jpg`

尺寸：

- 原图：`1280 x 366`
- 前台渲染：约 `1140 x 326`

结构：

- 左侧品牌 logo。
- 中间放产品主体。
- 右侧放使用场景，比如汽车 / 城市 / 家庭。
- 背景用科技纹理、光效、深色渐变。
- 不靠很多文字，先建立技术可信度。

Prompt 模板：

```text
Create a product-tech hero banner for an eMAG product detail page.
Canvas: 1280x366 or 1400x400 wide banner.
Background: deep navy / purple technology gradient with subtle hexagon network or electric energy texture.
Left side: brand logo safe area and empty copy area.
Center: large clean product cutout, front-facing, sharp commercial lighting.
Right side: realistic usage context related to the product, such as electric vehicle, kitchen, bathroom, workshop, garden, or travel.
Composition: product is the main authority signal; context explains where it is used.
Text rule: minimal headline only, or leave text area empty for deterministic overlay.
Avoid: excessive claims, unreadable generated text, fake certification marks, fake platform logos.
```

适配变量：

- `product_cutout`
- `use_context`
- `technical_texture`
- `brand_logo_area`
- `headline`
- `primary_claim`

适合产品：

- 车品 / 电器 / 工具 / 智能设备 / 安防 / 医疗小设备。

### 类型 C：官方 eMAG 促销视觉参考

已抓取官方来源：

- [official_asset_manifest.json](/Users/cc/Desktop/photo_show/references/emag_official_assets/20260524_homepage_banners/official_asset_manifest.json)
- [homepage_all_media_urls.json](/Users/cc/Desktop/photo_show/references/emag_official_assets/20260524_homepage_banners/homepage_all_media_urls.json)
- [homepage_screenshot.png](/Users/cc/Desktop/photo_show/references/emag_official_assets/20260524_homepage_banners/homepage_screenshot.png)

当前抓到的官方素材类型：

- 多张官方 eMAG 首页模块图：`420 x 480`
- 一张官方横幅图：`1200 x 225`

注意：

- 这些可以作为风格、构图和 prompt 参考。
- 不建议直接拿官方图片做我们自己的商业详情图，除非明确有复用授权。
- 更稳的做法是：提取它的构图、色彩、人物姿态、产品悬浮方式，再生成自己的品牌资产。

## 3. 详情文案怎么写

核心原则：

- 不要先讲参数，先讲购买结果。
- 不要简单陈述功能，要说明“这笔钱解决什么问题”。
- 不要把用户留在脑内自己提问，要替他把问题写出来。
- 一屏只解决一个疑虑。

推荐顺序：

1. 结果型开头  
   告诉用户获得什么状态，比如更方便、更安心、更省时间、更好清洁、更容易携带。

2. 痛点场景  
   写用户受够了什么，而不是产品有什么。

3. 功能转好处  
   每条用 `功能 -> 结果`，不要只有参数。

4. 证据模块  
   用图片、GIF、场景图、参数表证明，不只用形容词。

5. FAQ / objection closer  
   把用户会回头找的答案提前写出来。

示例公式：

```text
当你在 [具体场景] 里遇到 [具体麻烦]，这个产品通过 [核心功能] 帮你得到 [明确结果]。
```

## 4. HTML 格式设计

最稳结构：

```html
<p style="text-align:center;">
  <img src="BANNER_URL" width="1140" alt="Brand/product banner">
</p>

<h2>Result-oriented headline</h2>
<p><strong>Buyer question:</strong> Short answer focused on outcome.</p>

<p style="text-align:center;">
  <img src="FEATURE_BOARD_URL" width="1140" alt="Feature explanation">
</p>

<table width="100%" cellpadding="8" cellspacing="0">
  <tr>
    <td><strong>Spec</strong></td>
    <td>Value</td>
  </tr>
</table>

<h2>Intrebari frecvente</h2>
<p><strong>Question?</strong><br>Answer from source facts or reviews.</p>
```

实现规则：

- 复杂视觉尽量用图片板，不依赖复杂 CSS。
- 详情页默认单列。
- 主 banner 推荐 `1200 x 480` 或 `1280 x 366`，前台会收敛到约 `1140px` 宽。
- `table` 可用，但作为 gray zone，需要保留无 table 降级版本。
- GIF 可用，适合品牌动效、使用步骤、安装/前后对比。
- 图片必须有可追踪来源和尺寸记录。

## 5. SOP 总结

### 输入

- 产品事实：标题、规格、包装、适用场景、禁忌/注意事项。
- 图片资产：主图、细节图、场景图、品牌图、是否有产品 cutout。
- 证据资产：评论、Q&A、类目常见问题、官方参数。
- 品牌变量：品牌名、色调、服务承诺是否有来源。

### 规划

1. 选择 banner 类型：品牌信任 / 产品技术 / 官方促销参考 / FAQ 证据。
2. 写出 5-7 个 buyer questions。
3. 每个模块绑定一个问题，不混多个目标。
4. 判断哪些模块用 HTML，哪些模块用图片板。
5. 判断 testimonial 是否有真实证据；没有就改成 FAQ。

### 生成

1. 先生成无文字或少文字背景图。
2. 再用确定性工具叠加品牌名、标题、服务 cue。
3. 导出 `1200x480`、`1140px` 兼容版、必要时导出 `800px` 轻量版。
4. 生成 HTML snippet。
5. 记录所有图片 URL、自然尺寸、渲染尺寸。

### 校验

- 是否出现价格、站外链接、联系方式、虚假服务承诺。
- 是否伪造评价 / 星级 / 客户名。
- 是否每个模块只回答一个问题。
- 是否单列可读。
- 是否存在图片尺寸过大或字体过小。
- GIF 是否有明确用途。

## 6. 当前还要继续做的事

1. 对 45 个成功详情 HTML 做模块分类：品牌动图、功能图、参数表、FAQ、场景图。
2. 对 `D617222BM` 单独复查，看是否本身无详情，还是需要另一种 selector。
3. 从 BestPlaza GIF 中拆出更多 banner 类型，不只保留 General / Headphone。
4. 将这些 banner 类型写入模块库和模板选择器。
5. 后续你发新的 banner 后，按同一格式继续追加。
