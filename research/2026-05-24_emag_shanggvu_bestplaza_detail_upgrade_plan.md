# shanggvu / BestPlaza eMAG 详情页升级研究

日期：2026-05-24  
工作目录：`/Users/cc/Desktop/photo_show`

## 1. 当前采集状态

目标店铺：

- `https://www.emag.ro/vendors/vendor/shanggvu?ref=seller-page-see-all-products`

实际访问结果：

- headless Playwright：进入 `eMAG Captcha`
- headed Chrome channel Playwright：仍进入 `eMAG Captcha`
- curl / direct HTTP：CloudFront 返回 `HTTP 511`，要求 AWS WAF token
- Codex web fetch：同样不可稳定读取页面

已保留阻断证据：

- [scrape_summary.json](/Users/cc/Desktop/photo_show/references/user_cases/20260524_emag_shanggvu_detail_case/scrape_summary.json)
- [vendor_pages.json](/Users/cc/Desktop/photo_show/references/user_cases/20260524_emag_shanggvu_detail_case/vendor_pages.json)
- [scrape_emag_vendor_detail_case.mjs](/Users/cc/Desktop/photo_show/scripts/scrape_emag_vendor_detail_case.mjs)

结论：这次没有把 shanggvu 店铺下所有商品链接抓下来。原因不是选择器为空，而是当前网络被 eMAG WAF 拦截。后续需要在已通过验证的真实 Chrome session 或可用 WAF token 下重跑新脚本。

## 2. 可以继续复用的旧研究结论

旧研究已经证明：

- 详情 HTML 要作为一等 artifact 保存，不应只保存图片。
- 真实 eMAG PDP 在手机端趋向单列长流，`maxImagesPerRow = 1`。
- 30 个 live HTML 样本平均图片数约 `10.67`，中位数 `10.5`。
- 高频标签包括 `p / strong / img / br / td / li / div / tr / blockquote / h2 / ul / h1`。
- `table / div / inline style / GIF` 在 live 样本里能活着显示，但仍应标记为 gray zone。
- 图片常见宽度是 `1140px`，但后续生产不应盲目照抄，应默认 `800px` 宽图板，便于 eMAG 描述区和移动端阅读。

## 3. 从 BestPlaza 截图提炼出的新模式

用户给的截图里，不只是“更好看”，而是出现了新的转化结构：

1. 顶部品牌信任 banner  
   黑底、真人、包裹、服务符号，让买家把品牌和 eMAG 熟悉感挂钩。它不是重复 logo，而是在建立“这家店像正规店”的心理位置。

2. 用户问题前置  
   FAQ 不是页面末尾的补丁，而是替用户把犹豫写出来。它减少买家回头翻详情、重新找答案的成本。

3. 色块分组  
   浅绿色色块让优势列表从普通段落变成“可扫读模块”。它的价值是阅读顺序，不是装饰。

4. 标志符号作为视觉锚点  
   每个重点前用统一符号，使移动端长文不至于散。

5. 规格表保持克制  
   参数区仍然需要，但是不应放在开头。它解决理性确认，而不是负责第一秒的购买动机。

6. Testimonial 图板可生成，但内容不能乱编  
   可以用 Image Tool 生成评价风格图板；但客户姓名、评分、日期、具体评价必须来自真实 review 或明确改成“常见问题/用户关注点”。否则会变成伪造社会证明。

## 4. 新详情页推荐模块顺序

建议把 eMAG 详情页从“信息堆叠”改成“购买疑虑清除”：

1. `emotional_result_hero`  
   三秒内告诉用户买到的结果，不先讲参数。

2. `pain_scene_solution`  
   说清楚用户受够了什么场景，这个产品具体替他省掉什么麻烦。

3. `color_band_feature_stack`  
   用色块列出 5-8 个核心优势，每条是“功能 -> 好处”。

4. `buyer_question_answer_block`  
   每个模块只回答一个买家问题。

5. `spec_table_clean`  
   规格、尺寸、兼容性、包装内容在中后段做确认。

6. `brand_platform_trust_banner`  
   深色品牌/服务 banner 作为信任增强，但服务 claim 必须有来源。

7. `faq_objection_closer`  
   收尾回答最可能让买家犹豫的问题。

## 5. HTML 可做的优化形式

在 eMAG 描述区里，最稳的是：

- 单列图片板：用 `<img>` 承载复杂视觉和真人 banner。
- 简单 HTML 文本：用 `<h2>`、`<p>`、`<strong>`、`<ul><li>` 做可复制描述。
- 参数表：可以用 `<table>`，但要标记 gray zone，并准备无表格降级版本。
- 色块：优先做成图片板；如果用 HTML，则用 table 背景色或内联 style，必须过真实前台验证。
- GIF：只用于动作证明、安装步骤、效果前后对比。

不建议默认做：

- 桌面双列布局。
- 复杂 CSS class 依赖。
- 全页黑底。
- 伪造评价、伪造评分、伪造配送/退货/保修承诺。

## 6. 对 Scale / SOP 的修改

已新增：

- [emag_detail_module_catalog.v2.json](/Users/cc/Desktop/photo_show/workflow/emag_detail_module_catalog.v2.json)
- [EMAG_DETAIL_SCALE_CONTRACT.md](/Users/cc/Desktop/photo_show/workflow/EMAG_DETAIL_SCALE_CONTRACT.md)

新增 Scale 重点：

- `Scale D: Conversion Module Fit`
- `Scale E: Visual Board Feasibility`

核心变化：

- section plan 必须绑定 `module_id`。
- 每个模块必须回答一个 buyer question。
- 顶部模块必须先回答结果/痛点，再进入规格。
- testimonial 必须有真实 review 数据，否则改成 FAQ。
- brand/platform trust banner 的配送、退货、保修等 claim 必须有来源。

## 7. 新采集脚本重跑方式

当 eMAG WAF 已通过或本机 Chrome 有可用 session 时运行：

```bash
EMAG_HEADED=1 node /Users/cc/Desktop/photo_show/scripts/scrape_emag_vendor_detail_case.mjs \
  'https://www.emag.ro/vendors/vendor/shanggvu?ref=seller-page-see-all-products' \
  /Users/cc/Desktop/photo_show/references/user_cases/20260524_emag_shanggvu_detail_case
```

预期输出：

- `vendor_products.json`
- `vendor_pages.json`
- `scrape_summary.json`
- `products/*/description_outer.html`
- `products/*/description_inner.html`
- `products/*/description_meta.json`
- `products/*/description_mobile.png`
- `products/*/description_images/*`

## 8. 下一步

下一轮最值得做的是：

1. 先解决 WAF，通过真实 Chrome session 把 shanggvu 全店链接和 HTML 抓下来。
2. 在抓到的 HTML 上跑模块归类：哪些产品用了 hero / FAQ / brand banner / color band / specs。
3. 选 2 个产品做 before/after 对比页，直接验证新 Scale 是否比旧模板更像 BestPlaza 模式。
4. 把 Image Tool 生成图板接进 `image_board` 输出模式，而不是只作为单独图片实验。
