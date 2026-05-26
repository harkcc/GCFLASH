# eMAG Banner Agent Validation Report

日期：2026-05-24  
工作目录：`/Users/cc/Desktop/photo_show`

## 1. 采集状态

### shanggvu / BestPlaza 店铺

来源：

- `https://www.emag.ro/vendors/vendor/shanggvu?ref=seller-page-see-all-products`
- 本地证据：`references/user_cases/20260524_emag_shanggvu_detail_case_chrome/scrape_summary.json`

结果：

- 商品卡：46 个
- meta 文件：46 个
- 详情 HTML：45 个
- 缺失详情：1 个，`D617222BM`，页面未拿到可用 description container
- 详情图片：347 张
- 含 GIF 的产品：42 个
- GIF 总数：42
- 最常见源尺寸：`1200x480`，出现 42 次
- 最常见渲染尺寸：`1140x456`，出现 75 次
- 页面结构：单列为主，`maxImagesPerRow=1`

结论：这个店铺的详情页不是“复杂前端页面”，而是单列图片板 + 少量 table/inline style。核心可复用资产是 `1200x480` 的品牌 GIF/banner 和一套 1140 宽详情图节奏。

### Qoltec 目标页

来源：

- `https://www.emag.ro/statie-de-incarcare-rapida-smart-11kw-pentru-vehicule-electrice-compatibilitate-universala-eficienta-maxima-si-siguranta-avansata-cu-control-wifi-rfid-si-protectie-ip65-52470/pd/D978TDYBM/`
- 本地证据：`references/user_cases/20260524_emag_qoltec_d978tdybm/target_summary.json`

结果：

- 详情图：5 张
- GIF：0
- table：5
- 首图源尺寸：`1280x366`
- 首图渲染尺寸：约 `1140x326`

结论：这是第二类 Banner：产品技术 Hero。它不是品牌信任型，而是把产品、技术背景、使用场景放到第一屏。

### eMAG 官方首页素材

本地证据：

- `references/emag_official_assets/20260524_homepage_banners/official_asset_manifest.json`
- `references/emag_official_assets/20260524_homepage_banners/official_asset_contact_sheet.png`

结果：

- 420x480 人物/类目卡：9 张
- 1200x225 促销条：1 张

使用边界：这些图片可作为风格和构图参考。未确认授权前，不应直接作为生产详情页商用素材。

## 2. 行为模式总结

1. 顶部先处理情绪和信任，不先堆参数。
2. 品牌信任 Banner 使用黑底、大品牌字、真人/包裹、服务锚点。
3. 产品技术 Banner 使用产品切图、技术背景、使用场景、2-3 个强卖点。
4. 详情正文每屏只解决一个问题：结果、痛点、证据、参数、使用、FAQ。
5. FAQ 的价值不是“补字数”，而是替用户完成脑中的疑问路径，减少返回前文找答案。
6. 色块、符号、表格是视觉顺序锚点，不是装饰。
7. 复杂视觉用图片解决；HTML 保持简单，避免依赖复杂 CSS。

## 3. Banner Prompt 拆解

### A. BestPlaza 黑底信任 Banner

用户截图中的结构可拆成：

- 背景：黑色/深紫，高级感，带点阵或光效。
- 左侧：品牌名 + slogan + 3 个服务锚点。
- 右侧：真人拿包裹/平台包裹/产品场景。
- 情绪：熟悉、可靠、有人味，不是冷冰冰的品牌 logo 重复。
- 心理机制：把品牌和平台购物体验绑定，降低陌生品牌的不确定感。

可复用 Prompt：

```text
Use case: ads-marketing
Asset type: eMAG detail-page brand trust banner, 1200x480.
Scene: premium black/deep purple ecommerce background, subtle dotted or light trail texture.
Subject: friendly European adults with a plain unbranded parcel, or a clean marketplace package scene.
Composition: left 45-55% reserved for deterministic text overlay; right side has people/package/product context.
Mood: warm, premium, reliable, not luxury fashion.
Text policy: no readable text, no logo, no discount badge, no trademarked marketplace mark in the generated background.
Post-process: add brand, slogan, and up to three service cues with deterministic overlay.
Avoid: fake eMAG logo, unsupported platform guarantees, model-written small text, clutter.
```

### B. Qoltec 产品技术 Banner

结构：

- 背景：深蓝/紫科技感。
- 主体：产品切图居中或偏左。
- 右侧：使用场景，例如车辆、办公室、户外环境。
- 文案：先讲安全、速度、兼容性，再补参数。

可复用 Prompt：

```text
Use case: ads-marketing
Asset type: eMAG detail-page product technical hero, 1280x366.
Scene: deep navy or purple technical background, light grid, subtle energy lines.
Subject: product cutout or realistic product render centered; usage context on the right.
Composition: left has 2-3 deterministic feature chips; center product; right buyer-result phrase.
Mood: precise, safe, high-confidence.
Text policy: no generated text except large abstract UI shapes; overlay exact copy later.
Avoid: fake certifications, dense spec tables, unsupported compatibility claims.
```

### C. 官方蓝底人物/类目 Banner

结构：

- 背景：eMAG 官方促销页常见亮蓝色。
- 主体：人物 + 类目物品 + 圆角商品卡。
- 画面逻辑：人带情绪，商品带品类，蓝底带平台熟悉感。

可复用 Prompt：

```text
Use case: ads-marketing
Asset type: eMAG promo-inspired detail banner, 1200x480.
Scene: bright marketplace blue background, circular motion lines, floating rounded category tiles.
Subject: one smiling person plus product/category objects.
Composition: left has hook area; right has person and 2-3 product tiles.
Mood: energetic, friendly, app-first, mainstream retail.
Text policy: no official eMAG logo or discount text unless rights and campaign facts are confirmed.
Avoid: overcrowded floating products, unreadable text, direct copying of official assets for commercial deployment.
```

## 4. HTML / CSS 验证

验证文件：

- `experiments/20260524_emag_banner_css_validation/emag_banner_css_validation_snippet.html`
- `experiments/20260524_emag_banner_css_validation/validation_report.json`

结果：

- status: `pass`
- 图片：2
- GIF：1
- table：2
- inline style：10
- center style：2
- 1140 桌面宽图：2

已验证可用形式：

- `<p style="text-align:center;"><img width="1140" ... /></p>`
- GIF 作为详情页图片嵌入
- `table/tr/td` 做色块和规格表
- inline `padding/background-color/text-align`
- FAQ 使用普通 `p/strong/br`

风险提示：

- 外链图片 host 会 warning。
- table 会 warning，但 live page 已证明可用。
- 1140 宽图会 warning，因为它是桌面偏置；本项目现在把它作为 eMAG live desktop 标准，同时保留 800 fallback。

## 5. Agent / Scale 修改

已修改：

- `workflow/agent_flow/ecommerce_image_agent_v0.md`
- `workflow/agent_flows/emag_detail_banner_agent_v1.md`
- `workflow/emag_detail_module_catalog.v2.json`
- `workflow/EMAG_DETAIL_SCALE_CONTRACT.md`

新增规则：

- eMAG 详情页默认走 `1140px` 渲染宽度。
- Banner 先选 family，再写文案，再生成图。
- 复杂视觉生成图片；准确文字用 HTML/Pillow 叠加。
- 官方素材只作为风格参考，未确认授权前不直接生产复用。
- 服务、配送、退货、保修等 claim 必须有证据。

## 6. 测试生成结果

生成脚本：

- `scripts/build_emag_banner_test_assets.py`

输出目录：

- `output/emag_banner_generation_tests/`

当前 4 套：

1. `01_brand_trust_dark_package_1200x480.png`
   - 黑底品牌信任 Banner
   - 适合品牌实力、平台熟悉感、服务锚点
2. `02_ev_charger_product_tech_1280x366.png`
   - 产品技术 Hero
   - 适合 EV / 工具 / 电子类
3. `03_official_people_category_style_1200x480.png`
   - 官方蓝底人物/类目风格
   - 适合 app 感、类目感、生活方式商品
4. `04_ai_brand_trust_background_overlay_1200x480.png`
   - Image Tool 生成真人包裹背景，本地确定性文字叠加
   - 适合后续作为黑底信任 Banner 的模板图

## 7. 下一步建议

下一轮接入更多 Banner 类型时，按这个顺序扩展：

1. 每新增一种 Banner，先记录来源图、尺寸、场景、心理作用。
2. 拆出 Prompt 框架，不直接复制图。
3. 生成 1 张无文字背景 + 1 张确定性叠字成品。
4. 放进 `banner_style_selector`。
5. 用 HTML snippet 验证实际可嵌入形式。
