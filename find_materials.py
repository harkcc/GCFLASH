"""
找素材脚本 — 通过产品图片在全球电商平台找同类产品套图

流程:
1. 上传产品图到 imgur (临时公开URL) 供 Google Lens 使用
2. SerpApi Google Lens 搜索 → 拿到匹配产品链接
3. 访问产品页 → 抓取套图 (所有产品图片)
4. Gemini Vision 判断 → 是否同类产品、设计质量
5. 下载符合条件的套图到本地
"""

import os
import re
import json
import time
import hashlib
import base64
import requests
from pathlib import Path
from urllib.parse import urlparse, urljoin
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GEMINI_KEY = os.getenv("GEMINI_KEY")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# =============================================================================
# Step 1: 上传图片获取公开 URL
# =============================================================================

def upload_image(image_path):
    """上传图片获取公开 URL, 尝试多个免费图床"""

    # 方法1: litterbox.catbox.moe (临时文件, 1小时过期)
    try:
        with open(image_path, "rb") as f:
            resp = requests.post(
                "https://litterbox.catbox.moe/resources/internals/api.php",
                data={"reqtype": "fileupload", "time": "1h"},
                files={"fileToUpload": f},
                timeout=30,
            )
        if resp.status_code == 200 and resp.text.startswith("http"):
            url = resp.text.strip()
            print(f"  ✓ 图片已上传: {url}")
            return url
    except Exception as e:
        print(f"  ⚠ catbox 失败: {e}")

    # 方法2: freeimage.host
    try:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        resp = requests.post(
            "https://freeimage.host/api/1/upload",
            data={"key": "6d207e02198a847aa98d0a2a901485a5", "source": b64, "format": "json"},
            timeout=30,
        )
        if resp.status_code == 200:
            url = resp.json()["image"]["url"]
            print(f"  ✓ 图片已上传: {url}")
            return url
    except Exception as e:
        print(f"  ⚠ freeimage 失败: {e}")

    print("  ✗ 所有图床均失败")
    return None


def get_image_url(image_input):
    """支持本地路径或 URL"""
    if image_input.startswith("http"):
        return image_input
    path = Path(image_input)
    if path.exists():
        return upload_image(str(path))
    print(f"  ✗ 文件不存在: {image_input}")
    return None


# =============================================================================
# Step 2: Google Lens 搜索
# =============================================================================

def google_lens_search(image_url):
    """通过 SerpApi Google Lens 搜索相似产品"""
    print(f"\n🔍 Google Lens 搜索中...")

    params = {
        "engine": "google_lens",
        "url": image_url,
        "api_key": SERPAPI_KEY,
    }

    resp = requests.get("https://serpapi.com/search", params=params)
    data = resp.json()

    if "error" in data:
        print(f"  ✗ 搜索失败: {data['error']}")
        return []

    matches = data.get("visual_matches", [])
    print(f"  ✓ 找到 {len(matches)} 个匹配结果")

    # 打印前 10 个结果概览
    for i, m in enumerate(matches[:10]):
        price_info = ""
        if m.get("price"):
            price_info = f" | {m['price'].get('value', '')}"
        rating_info = ""
        if m.get("rating"):
            rating_info = f" | ★{m['rating']}"
        reviews_info = ""
        if m.get("reviews"):
            reviews_info = f" ({m['reviews']}条评论)"

        print(f"  [{i+1}] {m.get('source', '?'):15s} | {m.get('title', '?')[:50]}{price_info}{rating_info}{reviews_info}")

    return matches


# =============================================================================
# Step 3: 抓取产品页套图
# =============================================================================

def extract_asin_from_url(url):
    """从 Amazon URL 中提取 ASIN"""
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'asin=([A-Z0-9]{10})',
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return None


def fetch_amazon_images_via_serpapi(product_url):
    """通过 SerpApi Amazon Product API 获取套图 (绕过反爬)"""
    asin = extract_asin_from_url(product_url)
    if not asin:
        print(f"  ⚠ 无法从 URL 提取 ASIN")
        return []

    # 判断 Amazon 域名
    parsed = urlparse(product_url)
    host = parsed.netloc.lower()
    # 提取实际域名: amazon.com, amazon.co.uk, amazon.ca 等
    import re as _re
    domain_match = _re.search(r'(amazon\.[a-z.]+)', host)
    domain = domain_match.group(1) if domain_match else "amazon.com"

    print(f"  → ASIN: {asin} ({domain})")

    params = {
        "engine": "amazon_product",
        "asin": asin,
        "amazon_domain": domain,
        "api_key": SERPAPI_KEY,
    }

    try:
        resp = requests.get("https://serpapi.com/search", params=params, timeout=30)
        data = resp.json()
    except Exception as e:
        print(f"  ✗ SerpApi 请求失败: {e}")
        return []

    if "error" in data:
        print(f"  ✗ SerpApi 错误: {data['error']}")
        return []

    images = []
    pr = data.get("product_results", {})

    # 1. thumbnails — 套图核心 (高清大图列表)
    for img_url in pr.get("thumbnails", []):
        if isinstance(img_url, str):
            images.append(img_url)

    # 2. 主缩略图 (如果 thumbnails 没有的话)
    thumb = pr.get("thumbnail", "")
    if thumb and thumb not in images:
        # 转高清
        thumb = re.sub(r'\._[A-Z0-9_,]+_\.', '._AC_SL1500_.', thumb)
        images.append(thumb)

    # 3. 变体图片
    for variant in pr.get("variants", []):
        for item in variant.get("items", []):
            if item.get("image") and item["image"] not in images:
                images.append(item["image"])

    # 去重
    seen = set()
    unique = []
    for img in images:
        if img and img not in seen:
            seen.add(img)
            unique.append(img)

    return unique


def extract_images_generic(html, url):
    """通用产品页图片提取 (非 Amazon)"""
    images = []
    soup = BeautifulSoup(html, "html.parser")

    for img in soup.find_all("img"):
        src = img.get("data-src") or img.get("data-large") or img.get("data-zoom-image") or img.get("src") or ""
        if not src:
            continue
        try:
            width = int(img.get("width", "0"))
            height = int(img.get("height", "0"))
            if width and width < 100:
                continue
            if height and height < 100:
                continue
        except (ValueError, TypeError):
            pass

        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = urljoin(url, src)

        if src.startswith("http") and not any(x in src.lower() for x in ["logo", "icon", "sprite", "pixel", "tracking", "badge"]):
            images.append(src)

    # JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            ld = json.loads(script.string)
            if isinstance(ld, dict):
                img = ld.get("image")
                if isinstance(img, str):
                    images.append(img)
                elif isinstance(img, list):
                    images.extend([i for i in img if isinstance(i, str)])
        except (json.JSONDecodeError, TypeError):
            pass

    seen = set()
    return [x for x in images if x not in seen and not seen.add(x)]


def fetch_product_images(product_url):
    """获取产品套图 — Amazon 走 SerpApi, 其他走直接抓取"""
    print(f"  📸 抓取套图: {product_url[:80]}...")

    domain = urlparse(product_url).netloc.lower()

    if "amazon" in domain:
        images = fetch_amazon_images_via_serpapi(product_url)
    else:
        try:
            resp = requests.get(product_url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            images = extract_images_generic(resp.text, product_url)
        except Exception as e:
            print(f"  ✗ 访问失败: {e}")
            images = []

    print(f"  ✓ 找到 {len(images)} 张套图")
    return images


# =============================================================================
# Step 4: Gemini 判断
# =============================================================================

def gemini_judge(image_urls, product_description=""):
    """用 Gemini 判断图片是否为同类高质量产品图"""

    # 下载前几张图作为判断依据
    image_parts = []
    for url in image_urls[:4]:  # 最多看4张
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                content_type = resp.headers.get("content-type", "image/jpeg")
                if "image" in content_type:
                    b64 = base64.b64encode(resp.content).decode()
                    image_parts.append({
                        "inline_data": {
                            "mime_type": content_type.split(";")[0],
                            "data": b64
                        }
                    })
        except Exception:
            continue

    if not image_parts:
        return {"suitable": False, "reason": "无法下载图片"}

    prompt = f"""你是一个电商产品图片评估专家。请判断这组产品图片:

1. 这是什么产品？属于什么品类？
2. 图片设计质量如何？(专业产品摄影/一般/低质量)
3. 图片是否适合作为电商产品设计参考素材？(主要看构图、场景、细节展示)
4. 简要描述图片中产品的形态特征

请用JSON格式回答:
{{
  "product_name": "产品名称",
  "category": "品类",
  "design_quality": "high/medium/low",
  "suitable_as_reference": true/false,
  "features": "产品形态特征描述",
  "reason": "判断理由"
}}

只返回JSON，不要其他内容。"""

    parts = image_parts + [{"text": prompt}]

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"

    payload = {
        "contents": [{"parts": parts}]
    }

    try:
        resp = requests.post(api_url, json=payload, timeout=30)
        data = resp.json()

        text = data["candidates"][0]["content"]["parts"][0]["text"]
        # 提取 JSON
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r'^```\w*\n?', '', text)
            text = re.sub(r'\n?```$', '', text)

        result = json.loads(text)
        return result
    except Exception as e:
        print(f"  ⚠ Gemini 判断出错: {e}")
        return {"suitable_as_reference": False, "reason": str(e)}


# =============================================================================
# Step 5: 下载套图
# =============================================================================

def download_images(image_urls, save_dir, prefix=""):
    """批量下载图片到本地"""
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    downloaded = []
    for i, url in enumerate(image_urls):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                continue

            # 确定扩展名
            content_type = resp.headers.get("content-type", "")
            if "png" in content_type:
                ext = ".png"
            elif "webp" in content_type:
                ext = ".webp"
            else:
                ext = ".jpg"

            filename = f"{prefix}_{i+1:02d}{ext}" if prefix else f"img_{i+1:02d}{ext}"
            filepath = save_dir / filename

            with open(filepath, "wb") as f:
                f.write(resp.content)
            downloaded.append(str(filepath))

        except Exception as e:
            print(f"  ⚠ 下载失败 [{i+1}]: {e}")

    print(f"  ✓ 已下载 {len(downloaded)} 张图片到 {save_dir}")
    return downloaded


# =============================================================================
# 主流程
# =============================================================================

def filter_matches(matches, min_reviews=0, min_rating=0, platforms=None):
    """
    筛选 Google Lens 结果

    Args:
        min_reviews: 最低评论数 (如 100 = 只要评论 ≥100 的产品)
        min_rating: 最低评分 (如 4.0)
        platforms: 平台白名单 (如 ["amazon", "ebay", "walmart"])
    """
    filtered = []
    for m in matches:
        # 平台筛选
        if platforms:
            source = (m.get("source") or "").lower()
            link = (m.get("link") or "").lower()
            if not any(p in source or p in link for p in platforms):
                continue

        # 评论数筛选
        reviews = m.get("reviews", 0) or 0
        if reviews < min_reviews:
            continue

        # 评分筛选
        rating = m.get("rating", 0) or 0
        if rating < min_rating:
            continue

        filtered.append(m)

    return filtered


def find_materials(image_input, output_dir="./materials", top_n=5,
                   auto_judge=True, min_reviews=0, min_rating=0,
                   platforms=None):
    """
    主入口: 输入产品图, 找素材套图

    Args:
        image_input: 本地图片路径 或 图片URL
        output_dir: 输出目录
        top_n: 取前N个结果抓取套图
        auto_judge: 是否用 Gemini 自动判断
        min_reviews: 最低评论数筛选 (如 50)
        min_rating: 最低评分筛选 (如 4.0)
        platforms: 平台筛选 (如 ["amazon", "ebay"])
    """
    print("=" * 60)
    print("🎯 找素材流程启动")
    print("=" * 60)

    # 打印筛选条件
    filters = []
    if min_reviews > 0:
        filters.append(f"评论≥{min_reviews}")
    if min_rating > 0:
        filters.append(f"评分≥{min_rating}")
    if platforms:
        filters.append(f"平台: {', '.join(platforms)}")
    if filters:
        print(f"  筛选条件: {' | '.join(filters)}")

    # Step 1: 获取图片 URL
    print("\n📤 Step 1: 准备图片...")
    image_url = get_image_url(image_input)
    if not image_url:
        return

    # Step 2: Google Lens 搜索
    print("\n🔍 Step 2: Google Lens 搜索...")
    matches = google_lens_search(image_url)
    if not matches:
        print("  ✗ 未找到匹配结果")
        return

    # Step 2.5: 筛选
    if min_reviews or min_rating or platforms:
        before = len(matches)
        matches = filter_matches(matches, min_reviews, min_rating, platforms)
        print(f"  📊 筛选: {before} → {len(matches)} 个结果")
        if not matches:
            print("  ✗ 筛选后无结果, 尝试降低条件")
            return

    # Step 3 & 4: 逐个抓取套图 + Gemini 判断
    actual_n = min(top_n, len(matches))
    print(f"\n📸 Step 3: 抓取前 {actual_n} 个结果的套图...")

    results = []
    for i, match in enumerate(matches[:actual_n]):
        product_url = match.get("link", "")
        source = match.get("source", "unknown")
        title = match.get("title", "unknown")
        reviews = match.get("reviews", 0) or 0
        rating = match.get("rating", 0) or 0

        if not product_url:
            continue

        review_info = f" | ★{rating}" if rating else ""
        review_info += f" ({reviews}条评论)" if reviews else ""
        print(f"\n--- [{i+1}/{actual_n}] {source}: {title[:45]}{review_info} ---")

        # 先用 Google Lens 返回的图片
        lens_images = []
        if match.get("image"):
            lens_images.append(match["image"])
        if match.get("thumbnail"):
            lens_images.append(match["thumbnail"])

        # 再去产品页抓更多图
        page_images = fetch_product_images(product_url)

        all_images = lens_images + [img for img in page_images if img not in lens_images]

        if not all_images:
            print("  ⚠ 未找到图片, 跳过")
            continue

        # Gemini 判断 (可选, 失败不影响流程)
        judgment = {}
        if auto_judge and all_images:
            print("  🤖 Gemini 判断中...")
            judgment = gemini_judge(all_images)
            if judgment.get("category"):
                quality = judgment.get("design_quality", "?")
                suitable = judgment.get("suitable_as_reference", False)
                category = judgment.get("category", "?")
                print(f"  → 品类: {category} | 质量: {quality} | 适合参考: {'✓' if suitable else '✗'}")
                print(f"  → 理由: {judgment.get('reason', '')[:80]}")
            else:
                print(f"  ⚠ Gemini 跳过 (可能额度不足): {judgment.get('reason', '')[:60]}")
                auto_judge = False  # 后续不再尝试

        result = {
            "source": source,
            "title": title,
            "url": product_url,
            "price": match.get("price", {}),
            "rating": rating,
            "reviews": reviews,
            "image_count": len(all_images),
            "images": all_images,
            "judgment": judgment,
        }
        results.append(result)

        # 下载套图 (Gemini 判断不可用时全部下载, 用户手动筛选)
        should_download = (not auto_judge) or judgment.get("suitable_as_reference", True)
        if should_download and all_images:
            safe_source = re.sub(r'[^\w]', '_', source)[:20]
            folder_name = f"{i+1:02d}_{safe_source}"
            download_images(all_images, Path(output_dir) / folder_name, prefix=safe_source)

        time.sleep(1)  # 礼貌延迟

    # 保存汇总报告
    report_path = Path(output_dir) / "report.json"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"✅ 完成! 共处理 {len(results)} 个产品")
    print(f"📁 素材保存在: {output_dir}")
    print(f"📊 报告保存在: {report_path}")
    print(f"{'=' * 60}")

    return results


# =============================================================================
# CLI 入口
# =============================================================================

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="找素材 — 通过产品图在全球电商平台找同类产品套图")
    parser.add_argument("image", help="产品图片路径或URL")
    parser.add_argument("-o", "--output", default="./materials", help="输出目录 (默认: ./materials)")
    parser.add_argument("-n", "--top", type=int, default=5, help="取前N个结果 (默认: 5)")
    parser.add_argument("--min-reviews", type=int, default=0, help="最低评论数筛选 (如: 50)")
    parser.add_argument("--min-rating", type=float, default=0, help="最低评分筛选 (如: 4.0)")
    parser.add_argument("--platforms", nargs="*", help="平台筛选 (如: amazon ebay walmart)")
    parser.add_argument("--no-judge", action="store_true", help="跳过 Gemini AI 判断")

    args = parser.parse_args()

    find_materials(
        image_input=args.image,
        output_dir=args.output,
        top_n=args.top,
        auto_judge=not args.no_judge,
        min_reviews=args.min_reviews,
        min_rating=args.min_rating,
        platforms=args.platforms,
    )
