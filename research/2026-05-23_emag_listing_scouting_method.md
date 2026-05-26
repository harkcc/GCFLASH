# eMAG 好看详情 Listing 寻找方法

日期：2026-05-23  
工作目录：`/Users/cc/Desktop/photo_show`

## 1. 当前判断

eMAG 详情 HTML 里可以接受 GIF 动态图。后续规则应拆开：

- 主图/辅图上传规则：仍按官方图片规则校验。
- 详情 HTML 媒体规则：GIF 可用，尤其适合动作证明、安装过程、使用效果、前后对比。

## 2. 找好看 listing 的方法

### 2.1 先从已抓 live HTML 里筛

本地脚本：

- [find_emag_good_listing_candidates.py](/Users/cc/Desktop/photo_show/scripts/find_emag_good_listing_candidates.py)

输出：

- [2026-05-23_emag_good_listing_candidates.md](/Users/cc/Desktop/photo_show/research/2026-05-23_emag_good_listing_candidates.md)
- [2026-05-23_emag_good_listing_candidates.json](/Users/cc/Desktop/photo_show/research/2026-05-23_emag_good_listing_candidates.json)

评分依据：

- 手机端是否保持单列
- 图片数量是否足够但不过量
- 是否有清晰标题分段
- 是否有列表/参数/包装内容结构
- 图文长度是否适中
- GIF 是否承担动作证明价值
- 是否存在过多表格、残留标签、过长描述等风险

当前 30 个样本里，最值得先人工打开看的候选：

| 排名 | 产品 ID | 类型 | 为什么值得看 |
|---|---|---|---|
| 1 | `D3JCBV3BM` | 儿童教育棋类 | 10 图、2 GIF、5 个标题、5 个列表，结构节奏比较完整 |
| 2 | `DDQ5ZS3BM` | A3/A4 laminator | 9 图、1 GIF、文字长度适中，适合办公工具类模板 |
| 3 | `DR990W3BM` | WiFi 天线 | 参数解释较多，含 3 GIF，适合技术/兼容性类模板 |
| 4 | `D5YN6S3BM` | 婴儿辅食机 | 图片形态包含 square/tall/wide，适合母婴小家电模板 |
| 5 | `DZ9JSS3BM` | 排风扇 | 工具类信息密度高，适合功能证明和规格模板 |

### 2.2 再用搜索引擎找大牌详情

可用搜索式：

```text
site:emag.ro/pd/ "## Descriere" "Samsung" "Image"
site:emag.ro/pd/ "## Descriere" "Philips" "Image"
site:emag.ro/pd/ "## Descriere" "Anker" "Image"
site:emag.ro/pd/ "## Descriere" "TP-Link" "Image"
```

这类结果通常更容易出现官方品牌素材、模块化卖点、较好的图文节奏。

已经找到的外部候选：

| 候选 | URL | 值得看的点 |
|---|---|---|
| Samsung Galaxy S23 | [eMAG](https://www.emag.ro/telefon-mobil-samsung-galaxy-s23-dual-sim-8gb-ram-256gb-5g-phantom-black-sm-s911bzkgeue/pd/DW2R8RMBM/) | 模块很多，图片和短文案交替，适合学习手机端长详情节奏 |
| Samsung Galaxy Tab A9+ | [eMAG](https://www.emag.ro/tableta-samsung-galaxy-tab-a9-octa-core-11-8gb-ram-256gb-wi-fi-graphite-sm-x210rzapeue/pd/DNDPCJ3BM/) | 大牌平板详情，适合学习场景图 + 功能解释 |
| Philips Series 5000 Shaver | [eMAG](https://www.emag.ro/aparat-de-ras-electric-philips-series-5000-s5887-30/pd/D9MF88MBM/) | 功能点拆得细，适合个人护理类模板 |
| Anker 736 100W | [eMAG](https://www.emag.ro/incarcator-retea-anker-736-100w-qc-3-0-2-x-usb-type-c-1-x-usb-negru-a2145g11/pd/D4Z8R8MBM/) | 小电子产品的 benefit/spec 节奏参考 |
| Anker 737 GaNPrime 120W | [eMAG](https://www.emag.ro/incarcator-retea-anker-737-ganprime-120w-pps-3-2x-usb-c-1x-usb-a-poweriq-4-0-negru-a2148311/pd/DCZ8R8MBM/) | 充电器类官方卖点表达，可参考参数和安全模块 |
| TP-Link Archer AX53 | [eMAG](https://www.emag.ro/router-wireless-tp-link-archer-ax53-ax3000-2-benzi-18573/pd/DN37VZMBM/) | 路由器/技术参数类详情参考 |
| TP-Link Archer BE230 | [eMAG](https://www.emag.ro/router-wireless-tp-link-be3600-dual-band-wi-fi-7-mlo-homeshield-easymesh-archer-be230/pd/DPBTY4YBM/) | 新 Wi-Fi 7 产品，适合学习技术卖点排序 |

## 3. 后续可自动化

后续可以把流程做成：

1. 输入品牌或类目关键词。
2. 搜索 eMAG PDP URL。
3. 打开 PDP 并展开 description。
4. 抓取详情 HTML、移动端截图、图片尺寸和标签结构。
5. 用 `find_emag_good_listing_candidates.py` 排序。
6. 人工只看 Top 10-20 个。

如果 eMAG 再次出现验证码，就先暂停在第 3 步，等人工过验证后继续批量抓。
