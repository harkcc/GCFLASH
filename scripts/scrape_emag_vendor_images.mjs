import { chromium } from "playwright";
import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";

const VENDOR_URL =
  "https://www.emag.ro/vendors/vendor/cangswjp?ref=seller-page-see-all-products";

const OUT_DIR =
  process.argv[2] ||
  path.resolve("references/user_cases/20260521_emag_cangswjp");

const USER_AGENT =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36";

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function slugify(input, fallback = "item") {
  const value = String(input || "")
    .normalize("NFKD")
    .replace(/[^\w\s.-]/g, "")
    .trim()
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 88);
  return value || fallback;
}

function getProductId(url) {
  const match = String(url).match(/\/pd\/([^/?#]+)\/?/);
  return match ? match[1] : crypto.createHash("sha1").update(url).digest("hex").slice(0, 10);
}

function cleanImageUrl(url) {
  if (!url) return "";
  try {
    const parsed = new URL(url);
    if (parsed.hostname.includes("s13emagst") && parsed.pathname.includes("/products/")) {
      parsed.search = "";
    }
    return parsed.toString();
  } catch {
    return url;
  }
}

function extensionFromUrl(url, contentType = "") {
  const parsed = new URL(url);
  const ext = path.extname(parsed.pathname).toLowerCase();
  if ([".jpg", ".jpeg", ".png", ".webp", ".gif"].includes(ext)) return ext;
  if (contentType.includes("png")) return ".png";
  if (contentType.includes("webp")) return ".webp";
  if (contentType.includes("gif")) return ".gif";
  return ".jpg";
}

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function writeJson(filePath, data) {
  await ensureDir(path.dirname(filePath));
  await fs.writeFile(filePath, JSON.stringify(data, null, 2));
}

async function downloadImage(page, url, targetPath) {
  const response = await page.request.get(url, {
    headers: {
      referer: "https://www.emag.ro/",
      "user-agent": USER_AGENT,
    },
    timeout: 45_000,
  });
  if (!response.ok()) {
    throw new Error(`HTTP ${response.status()} ${url}`);
  }
  const body = await response.body();
  await ensureDir(path.dirname(targetPath));
  await fs.writeFile(targetPath, body);
  return {
    bytes: body.length,
    contentType: response.headers()["content-type"] || "",
  };
}

async function scrollPage(page) {
  await page.evaluate(async () => {
    const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    let lastHeight = 0;
    for (let i = 0; i < 14; i += 1) {
      window.scrollTo(0, document.body.scrollHeight);
      await wait(450);
      const currentHeight = document.body.scrollHeight;
      if (currentHeight === lastHeight) break;
      lastHeight = currentHeight;
    }
    window.scrollTo(0, 0);
  });
}

async function collectVendorProducts(page) {
  await page.goto(VENDOR_URL, { waitUntil: "networkidle", timeout: 60_000 });
  await scrollPage(page);

  return page.evaluate(() => {
    const cards = [...document.querySelectorAll(".card-v2, [data-name='Product']")];
    const productMap = new Map();

    for (const card of cards) {
      const link = card.querySelector("a[href*='/pd/']");
      if (!link) continue;
      const url = new URL(link.href);
      url.search = "";
      url.hash = "";
      const title =
        card.querySelector(".card-v2-title")?.textContent?.trim() ||
        link.getAttribute("title") ||
        link.textContent?.trim() ||
        "";
      const img = card.querySelector("img[src*='/products/'], img[data-src*='/products/']");
      const imgUrl = img?.currentSrc || img?.src || img?.getAttribute("data-src") || "";
      productMap.set(url.toString(), {
        title,
        url: url.toString(),
        listingImageUrl: imgUrl,
      });
    }

    if (productMap.size === 0) {
      for (const link of document.querySelectorAll("a[href*='/pd/']")) {
        const url = new URL(link.href);
        url.search = "";
        url.hash = "";
        productMap.set(url.toString(), {
          title: link.textContent?.trim() || "",
          url: url.toString(),
          listingImageUrl: "",
        });
      }
    }

    return {
      pageTitle: document.title,
      visibleText: document.body.innerText.slice(0, 2000),
      products: [...productMap.values()],
    };
  });
}

async function collectProductImages(page, product) {
  await page.goto(product.url, { waitUntil: "domcontentloaded", timeout: 60_000 });
  await page.waitForTimeout(1500);
  await scrollPage(page);
  await page.waitForTimeout(500);

  const productId = getProductId(product.url);
  const data = await page.evaluate((expectedUrl) => {
    const canonical = document.querySelector("link[rel='canonical']")?.href || location.href;
    const h1 = document.querySelector("h1")?.innerText?.trim() || "";
    const title = document.title;
    const allImages = [...document.querySelectorAll("img")].map((img, index) => {
      const closestLink = img.closest("a[href]");
      const parentHref = closestLink?.href || "";
      const currentSrc = img.currentSrc || img.src || img.getAttribute("data-src") || "";
      const src = currentSrc || img.getAttribute("data-src") || "";
      const dataSrc = img.getAttribute("data-src") || "";
      return {
        index,
        alt: img.alt || "",
        src,
        dataSrc,
        parentHref,
        naturalWidth: img.naturalWidth,
        naturalHeight: img.naturalHeight,
        className: String(img.className || ""),
        inDescription: Boolean(
          img.closest(
            "#description-section, .product-page-description, .product-description, .description-wrapper, .js-description-content, [itemprop='description']",
          ),
        ),
      };
    });

    const currentPageUrl = new URL(expectedUrl);
    currentPageUrl.search = "";
    currentPageUrl.hash = "";

    const isCurrentProductImage = (image) => {
      const src = image.src || image.dataSrc || "";
      const parentHref = image.parentHref || "";
      if (!src.includes("/products/") || !src.includes("/images/")) return false;
      if (parentHref.includes("/pd/") && !parentHref.startsWith(currentPageUrl.toString())) {
        return false;
      }
      if (parentHref.includes("/products/") && parentHref.includes("/images/")) return true;
      if (image.alt && h1 && image.alt.trim() === h1) return true;
      return false;
    };

    const isDetailImage = (image) => {
      const src = image.src || image.dataSrc || "";
      if (!src) return false;
      if (src.includes("postimg.cc") || src.includes("i.postimg.cc")) return true;
      if (image.inDescription && image.naturalWidth >= 500 && image.naturalHeight >= 350) {
        return true;
      }
      return false;
    };

    return {
      url: location.href,
      canonical,
      title,
      h1,
      bodyTextSample: document.body.innerText.slice(0, 2500),
      galleryCandidates: allImages.filter(isCurrentProductImage),
      detailCandidates: allImages.filter(isDetailImage),
      allImageCount: allImages.length,
    };
  }, product.url);

  const galleryByUrl = new Map();
  for (const image of data.galleryCandidates) {
    const parentOriginal =
      image.parentHref && image.parentHref.includes("/products/") ? image.parentHref : "";
    const url = cleanImageUrl(parentOriginal || image.src || image.dataSrc);
    if (!url) continue;
    galleryByUrl.set(url, {
      role: "main_gallery",
      sourceUrl: url,
      alt: image.alt,
      naturalWidth: image.naturalWidth,
      naturalHeight: image.naturalHeight,
      domIndex: image.index,
    });
  }

  const detailByUrl = new Map();
  for (const image of data.detailCandidates) {
    const url = cleanImageUrl(image.src || image.dataSrc);
    if (!url) continue;
    detailByUrl.set(url, {
      role: "detail_image",
      sourceUrl: url,
      alt: image.alt,
      naturalWidth: image.naturalWidth,
      naturalHeight: image.naturalHeight,
      domIndex: image.index,
    });
  }

  return {
    productId,
    productUrl: product.url,
    listingTitle: product.title,
    listingImageUrl: cleanImageUrl(product.listingImageUrl || ""),
    ...data,
    galleryImages: [...galleryByUrl.values()],
    detailImages: [...detailByUrl.values()],
  };
}

async function main() {
  await ensureDir(OUT_DIR);
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1800 },
    userAgent: USER_AGENT,
    locale: "ro-RO",
  });
  const page = await context.newPage();

  const vendor = await collectVendorProducts(page);
  await writeJson(path.join(OUT_DIR, "vendor_products.json"), vendor);
  await page.screenshot({
    path: path.join(OUT_DIR, "vendor_page_screenshot.png"),
    fullPage: true,
  });

  const summary = {
    sourceVendorUrl: VENDOR_URL,
    outputDir: OUT_DIR,
    scrapedAt: new Date().toISOString(),
    vendorPageTitle: vendor.pageTitle,
    productCount: vendor.products.length,
    products: [],
    failures: [],
  };

  console.log(`Found ${vendor.products.length} product URLs`);

  for (const [index, product] of vendor.products.entries()) {
    const productId = getProductId(product.url);
    const slug = `${String(index + 1).padStart(2, "0")}_${productId}_${slugify(product.title, "product")}`;
    const productDir = path.join(OUT_DIR, "products", slug);
    const galleryDir = path.join(productDir, "main_gallery");
    const detailDir = path.join(productDir, "detail_images");
    await ensureDir(galleryDir);
    await ensureDir(detailDir);

    console.log(`[${index + 1}/${vendor.products.length}] ${productId} ${product.title}`);
    try {
      const meta = await collectProductImages(page, product);
      await page.screenshot({
        path: path.join(productDir, "page_screenshot.png"),
        fullPage: false,
      });

      for (const [imageIndex, image] of meta.galleryImages.entries()) {
        const targetBase = `${String(imageIndex + 1).padStart(2, "0")}_${crypto
          .createHash("sha1")
          .update(image.sourceUrl)
          .digest("hex")
          .slice(0, 8)}`;
        try {
          const probe = await page.request.get(image.sourceUrl, {
            headers: { referer: product.url, "user-agent": USER_AGENT },
            timeout: 45_000,
          });
          if (!probe.ok()) throw new Error(`HTTP ${probe.status()}`);
          const body = await probe.body();
          const contentType = probe.headers()["content-type"] || "";
          const ext = extensionFromUrl(image.sourceUrl, contentType);
          const filePath = path.join(galleryDir, `${targetBase}${ext}`);
          await fs.writeFile(filePath, body);
          image.localPath = path.relative(OUT_DIR, filePath);
          image.bytes = body.length;
          image.contentType = contentType;
        } catch (error) {
          image.downloadError = String(error.message || error);
        }
      }

      for (const [imageIndex, image] of meta.detailImages.entries()) {
        const targetBase = `${String(imageIndex + 1).padStart(2, "0")}_${crypto
          .createHash("sha1")
          .update(image.sourceUrl)
          .digest("hex")
          .slice(0, 8)}`;
        try {
          const info = await downloadImage(page, image.sourceUrl, path.join(detailDir, `${targetBase}${extensionFromUrl(image.sourceUrl)}`));
          const ext = extensionFromUrl(image.sourceUrl, info.contentType);
          const initialPath = path.join(detailDir, `${targetBase}${extensionFromUrl(image.sourceUrl)}`);
          const finalPath = path.join(detailDir, `${targetBase}${ext}`);
          if (initialPath !== finalPath) {
            await fs.rename(initialPath, finalPath).catch(() => {});
          }
          image.localPath = path.relative(OUT_DIR, finalPath);
          image.bytes = info.bytes;
          image.contentType = info.contentType;
        } catch (error) {
          image.downloadError = String(error.message || error);
        }
      }

      await writeJson(path.join(productDir, "product_meta.json"), meta);
      summary.products.push({
        productId,
        title: meta.h1 || product.title,
        url: product.url,
        localDir: path.relative(OUT_DIR, productDir),
        galleryCount: meta.galleryImages.length,
        downloadedGalleryCount: meta.galleryImages.filter((image) => image.localPath).length,
        detailCount: meta.detailImages.length,
        downloadedDetailCount: meta.detailImages.filter((image) => image.localPath).length,
      });
    } catch (error) {
      summary.failures.push({
        productId,
        title: product.title,
        url: product.url,
        error: String(error.message || error),
      });
    }

    await sleep(900);
  }

  await writeJson(path.join(OUT_DIR, "scrape_summary.json"), summary);
  await browser.close();

  console.log(`Done. Summary: ${path.join(OUT_DIR, "scrape_summary.json")}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
