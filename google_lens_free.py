"""
免费版 Google Lens 搜图 — 浏览器可见模式, 手动过验证码

用法:
  python3 google_lens_free.py ./photo/product.jpg

流程:
1. 打开浏览器 → Google Images
2. 上传你的产品图
3. 如果弹验证码 → 你手动点一下
4. 自动解析搜索结果
"""

import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright


def google_lens_search_free(image_path, timeout=60000):
    image_path = str(Path(image_path).resolve())
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="chromium",
            timeout=30000,
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="en-US",
        )
        page = context.new_page()

        try:
            # Step 1: 打开 Google Images
            print("  → 打开 Google Images...")
            page.goto("https://images.google.com/", wait_until="networkidle", timeout=timeout)
            time.sleep(2)

            # Step 2: 点击相机图标
            print("  → 点击搜图按钮...")
            camera_btn = page.query_selector('[aria-label="Search by image"]')
            if camera_btn:
                camera_btn.click()
                time.sleep(2)

            # Step 3: 上传图片
            print(f"  → 上传图片: {Path(image_path).name}")
            file_input = page.query_selector('input[type="file"]')
            if file_input:
                file_input.set_input_files(image_path)
            else:
                print("  ✗ 找不到上传入口")
                browser.close()
                return []

            # Step 4: 等待 — 如果有验证码, 用户手动点
            print("")
            print("  ⏳ 等待搜索结果...")
            print("  💡 如果浏览器弹出验证码, 请手动点击完成")
            print("  💡 结果加载后脚本会自动继续")
            print("")

            # 轮询等待结果页出现 (最多等 120 秒, 给用户时间点验证码)
            for i in range(60):
                current_url = page.url
                if "/search" in current_url and "lens" in current_url.lower() or "tbm=isch" in current_url:
                    print("  ✓ 搜索结果已加载!")
                    break
                # 检查是否已经有外部链接 (说明结果已出)
                ext_links = page.evaluate("""
                    () => document.querySelectorAll('a[href*="amazon"], a[href*="ebay"], a[href*="walmart"]').length
                """)
                if ext_links > 0:
                    print("  ✓ 搜索结果已加载!")
                    break
                time.sleep(2)
            else:
                print("  ⚠ 等待超时, 尝试解析当前页面...")

            time.sleep(3)  # 额外等待渲染

            # Step 5: 解析结果
            print("  → 解析搜索结果...")

            all_links = page.evaluate("""
                () => {
                    const results = [];
                    const seen = new Set();

                    document.querySelectorAll('a[href]').forEach(a => {
                        const href = a.href;
                        if (!href || seen.has(href)) return;
                        if (href.includes('google.com') || href.includes('gstatic.com') ||
                            href.includes('googleapis.com') || href.includes('youtube.com') ||
                            href.includes('javascript:') || href.startsWith('#')) return;
                        if (!href.startsWith('http')) return;

                        seen.add(href);

                        let title = a.getAttribute('aria-label') || '';
                        if (!title) {
                            const h3 = a.querySelector('h3');
                            title = h3 ? h3.textContent : (a.textContent || '').trim().slice(0, 150);
                        }

                        const img = a.querySelector('img');
                        const thumbnail = img ? (img.src || '') : '';

                        // 价格
                        let price = '';
                        const text = a.closest('div')?.textContent || '';
                        const m = text.match(/[\$€£¥][\d,.]+/);
                        if (m) price = m[0];

                        results.push({ title: title.trim(), link: href, thumbnail, price });
                    });
                    return results;
                }
            """)

            for item in all_links:
                item["source"] = urlparse(item["link"]).netloc.replace("www.", "")
                results.append(item)

            # 截图保存
            page.screenshot(path="/tmp/lens_result.png")
            print(f"  ✓ 找到 {len(results)} 个结果")

        except Exception as e:
            print(f"  ✗ 出错: {e}")
            try:
                page.screenshot(path="/tmp/lens_error.png")
            except Exception:
                pass
        finally:
            browser.close()

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 google_lens_free.py <图片路径>")
        sys.exit(1)

    image_path = sys.argv[1]
    print("=" * 50)
    print("🔍 Google Lens 免费搜图 (手动过验证码)")
    print("=" * 50)

    results = google_lens_search_free(image_path)

    if results:
        print(f"\n📋 结果 ({len(results)} 个):")
        for i, r in enumerate(results[:20]):
            price = f" | {r['price']}" if r.get('price') else ""
            print(f"  [{i+1}] {r['source']:25s} | {r['title'][:50]}{price}")

        out = Path(image_path).stem + "_lens_results.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 已保存: {out}")
