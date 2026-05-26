import { chromium } from "playwright";
import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";

const VENDOR_URL =
  process.argv[2] ||
  "https://www.emag.ro/vendors/vendor/shanggvu?ref=seller-page-see-all-products";
const OUT_DIR =
  process.argv[3] ||
  path.resolve("references/user_cases/20260524_emag_shanggvu_detail_case");
const MAX_PAGES = Number(process.env.EMAG_VENDOR_MAX_PAGES || "20");
const MAX_PRODUCTS = Number(process.env.EMAG_VENDOR_MAX_PRODUCTS || "120");
const HEADED = process.env.EMAG_HEADED === "1";

const USER_AGENT =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36";

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function productIdFromUrl(url) {
  const match = String(url).match(/\/pd\/([^/?#]+)\/?/);
  return match ? match[1] : crypto.createHash("sha1").update(url).digest("hex").slice(0, 10);
}

function slugify(input, fallback = "product") {
  const value = String(input || "")
    .normalize("NFKD")
    .replace(/[^\w\s.-]/g, "")
    .trim()
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 90);
  return value || fallback;
}

function cleanUrl(rawUrl) {
  if (!rawUrl) return "";
  try {
    const url = new URL(rawUrl, "https://www.emag.ro");
    url.hash = "";
    url.search = "";
    return url.toString();
  } catch {
    return "";
  }
}

function cleanPageUrl(rawUrl) {
  try {
    const url = new URL(rawUrl, "https://www.emag.ro");
    url.hash = "";
    url.searchParams.delete("ref");
    return url.toString();
  } catch {
    return String(rawUrl || "");
  }
}

function extensionFromUrl(rawUrl, contentType = "") {
  try {
    const ext = path.extname(new URL(rawUrl).pathname).toLowerCase();
    if ([".jpg", ".jpeg", ".png", ".webp", ".gif"].includes(ext)) return ext;
  } catch {}
  if (contentType.includes("png")) return ".png";
  if (contentType.includes("webp")) return ".webp";
  if (contentType.includes("gif")) return ".gif";
  return ".jpg";
}

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function writeJson(filePath, value) {
  await ensureDir(path.dirname(filePath));
  await fs.writeFile(filePath, JSON.stringify(value, null, 2));
}

async function writeText(filePath, value) {
  await ensureDir(path.dirname(filePath));
  await fs.writeFile(filePath, value);
}

async function scrollPage(page) {
  await page.evaluate(async () => {
    const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    let previousHeight = 0;
    for (let index = 0; index < 12; index += 1) {
      window.scrollTo(0, document.body.scrollHeight);
      await wait(450);
      const height = document.body.scrollHeight;
      if (height === previousHeight) break;
      previousHeight = height;
    }
    window.scrollTo(0, 0);
  });
}

async function collectVendorPage(page, url, vendorPath) {
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60_000 });
  await page.waitForTimeout(1200);
  await scrollPage(page);

  return page.evaluate((currentVendorPath) => {
    const normalize = (href) => {
      try {
        const url = new URL(href, location.href);
        url.hash = "";
        url.searchParams.delete("ref");
        return url.toString();
      } catch {
        return "";
      }
    };

    const productMap = new Map();
    for (const card of document.querySelectorAll(".card-v2, [data-name='Product'], .card-item")) {
      const link = card.querySelector("a[href*='/pd/']");
      if (!link) continue;
      const url = normalize(link.href);
      if (!url) continue;
      const image = card.querySelector("img[src*='/products/'], img[data-src*='/products/']");
      productMap.set(url, {
        title:
          card.querySelector(".card-v2-title")?.textContent?.trim() ||
          link.getAttribute("title") ||
          link.textContent?.trim() ||
          "",
        url,
        listingImageUrl: image?.currentSrc || image?.src || image?.getAttribute("data-src") || "",
      });
    }

    for (const link of document.querySelectorAll("a[href*='/pd/']")) {
      const url = normalize(link.href);
      if (!url || productMap.has(url)) continue;
      productMap.set(url, {
        title: link.getAttribute("title") || link.textContent?.trim() || "",
        url,
        listingImageUrl: "",
      });
    }

    const pageLinks = [];
    for (const link of document.querySelectorAll("a[href]")) {
      const href = normalize(link.href);
      if (!href) continue;
      try {
        const parsed = new URL(href);
        if (parsed.pathname === currentVendorPath && /page=|\/p\d+/.test(link.href + parsed.search)) {
          pageLinks.push(href);
        }
      } catch {}
    }

    return {
      pageUrl: location.href,
      pageTitle: document.title,
      textSample: document.body.innerText.slice(0, 1800),
      products: [...productMap.values()],
      pageLinks: [...new Set(pageLinks)],
    };
  }, vendorPath);
}

async function expandDescription(page) {
  const tab = page.locator("a[href='#description-section'], a[href='#specification-section']").first();
  if (await tab.count()) {
    await tab.click({ force: true }).catch(() => {});
    await sleep(500);
  }

  const root = page.locator("#collapse-wrapper-description, .product-page-description, #description-section").first();
  if (await root.count()) {
    await root.scrollIntoViewIfNeeded().catch(() => {});
    await sleep(400);
  }

  const openButtons = page.locator(
    "#collapse-wrapper-description .js-description-open, .product-page-description .js-description-open, .show-more, button:has-text('Vezi mai mult')",
  );
  const count = await openButtons.count();
  for (let index = 0; index < Math.min(count, 4); index += 1) {
    const button = openButtons.nth(index);
    if (await button.isVisible().catch(() => false)) {
      await button.click({ force: true }).catch(() => {});
      await sleep(400);
    }
  }
}

function collectDescriptionState() {
  const rootSelectors = [
    "#description-body",
    "#collapse-wrapper-description",
    ".product-page-description-text",
    ".product-page-description",
    "#description-section",
  ];
  const root =
    rootSelectors
      .map((selector) => document.querySelector(selector))
      .find((node) => node && (node.innerText || "").trim().length > 30) || null;

  const imageData = (node) =>
    [...node.querySelectorAll("img")].map((img, index) => {
      const rect = img.getBoundingClientRect();
      return {
        index,
        src: img.currentSrc || img.src || img.getAttribute("data-src") || "",
        alt: img.alt || "",
        width: Math.round(rect.width),
        height: Math.round(rect.height),
        naturalWidth: img.naturalWidth || 0,
        naturalHeight: img.naturalHeight || 0,
        style: img.getAttribute("style") || "",
      };
    });

  const productImages = [...document.querySelectorAll("img")]
    .map((img, index) => ({
      index,
      src: img.currentSrc || img.src || img.getAttribute("data-src") || "",
      alt: img.alt || "",
      naturalWidth: img.naturalWidth || 0,
      naturalHeight: img.naturalHeight || 0,
      inGallery: Boolean(img.closest(".product-gallery, .gallery, .thumbnail-wrapper")),
    }))
    .filter((img) => img.src.includes("/products/"));

  if (!root) {
    return {
      found: false,
      url: location.href,
      title: document.title,
      h1: document.querySelector("h1")?.innerText?.trim() || "",
      productImages,
    };
  }

  const tagFrequency = {};
  for (const node of root.querySelectorAll("*")) {
    const tag = node.tagName.toLowerCase();
    tagFrequency[tag] = (tagFrequency[tag] || 0) + 1;
  }

  const images = imageData(root);
  const rowGroups = [];
  for (const image of images) {
    const row = rowGroups.find((item) => Math.abs(item.top - image.top) <= 18);
    if (row) {
      row.count += 1;
    } else {
      rowGroups.push({ top: image.top, count: 1 });
    }
  }

  return {
    found: true,
    url: location.href,
    title: document.title,
    h1: document.querySelector("h1")?.innerText?.trim() || "",
    selector: rootSelectors.find((selector) => document.querySelector(selector) === root) || "unknown",
    textLength: (root.innerText || "").trim().length,
    textSample: (root.innerText || "").trim().slice(0, 1600),
    headingCount: root.querySelectorAll("h1, h2, h3, h4, h5, h6").length,
    paragraphCount: root.querySelectorAll("p").length,
    tableCount: root.querySelectorAll("table").length,
    listCount: root.querySelectorAll("ul, ol").length,
    iframeCount: root.querySelectorAll("iframe").length,
    imageCount: images.length,
    gifCount: images.filter((image) => /\.gif(\?|$)/i.test(image.src)).length,
    maxImagesPerRow: rowGroups.reduce((max, row) => Math.max(max, row.count), 0),
    tagFrequency,
    images,
    productImages,
    outerHTML: root.outerHTML,
    innerHTML: root.innerHTML,
  };
}

async function downloadImages(page, productDir, productUrl, images) {
  const seen = new Set();
  const downloaded = [];
  for (const [index, image] of images.entries()) {
    if (!image.src || seen.has(image.src)) continue;
    seen.add(image.src);
    try {
      const response = await page.request.get(image.src, {
        headers: { referer: productUrl, "user-agent": USER_AGENT },
        timeout: 45_000,
      });
      if (!response.ok()) throw new Error(`HTTP ${response.status()}`);
      const body = await response.body();
      const contentType = response.headers()["content-type"] || "";
      const name = `${String(index + 1).padStart(2, "0")}_${crypto
        .createHash("sha1")
        .update(image.src)
        .digest("hex")
        .slice(0, 8)}${extensionFromUrl(image.src, contentType)}`;
      const filePath = path.join(productDir, "description_images", name);
      await ensureDir(path.dirname(filePath));
      await fs.writeFile(filePath, body);
      downloaded.push({ ...image, localPath: path.relative(OUT_DIR, filePath), bytes: body.length, contentType });
    } catch (error) {
      downloaded.push({ ...image, downloadError: String(error.message || error) });
    }
  }
  return downloaded;
}

async function scrapeProduct(page, product, index, total) {
  const productId = productIdFromUrl(product.url);
  const productDir = path.join(
    OUT_DIR,
    "products",
    `${String(index + 1).padStart(2, "0")}_${productId}_${slugify(product.title)}`,
  );
  await ensureDir(productDir);
  console.log(`[${index + 1}/${total}] ${productId} ${product.title}`);

  await page.goto(product.url, { waitUntil: "domcontentloaded", timeout: 60_000 });
  await page.waitForTimeout(1800);
  await expandDescription(page);
  await page.waitForTimeout(600);

  const state = await page.evaluate(collectDescriptionState);
  const root = page.locator("#collapse-wrapper-description, .product-page-description, #description-section").first();
  if (await root.count()) {
    await root.screenshot({ path: path.join(productDir, "description_mobile.png") }).catch(() => {});
  }
  await page.screenshot({ path: path.join(productDir, "product_page_top.png"), fullPage: false }).catch(() => {});

  const downloadedDescriptionImages = state.found
    ? await downloadImages(page, productDir, product.url, state.images)
    : [];
  const meta = {
    productId,
    listingTitle: product.title,
    listingImageUrl: product.listingImageUrl,
    productUrl: product.url,
    scrapedAt: new Date().toISOString(),
    ...state,
    downloadedDescriptionImages,
  };

  await writeJson(path.join(productDir, "description_meta.json"), meta);
  if (state.found) {
    await writeText(path.join(productDir, "description_outer.html"), state.outerHTML);
    await writeText(path.join(productDir, "description_inner.html"), state.innerHTML);
  }

  return {
    productId,
    title: state.h1 || product.title,
    url: product.url,
    localDir: path.relative(OUT_DIR, productDir),
    found: state.found,
    textLength: state.textLength || 0,
    imageCount: state.imageCount || 0,
    gifCount: state.gifCount || 0,
    tableCount: state.tableCount || 0,
    maxImagesPerRow: state.maxImagesPerRow || 0,
  };
}

async function main() {
  await ensureDir(OUT_DIR);
  const browser = await chromium.launch({
    headless: !HEADED,
    channel: HEADED ? "chrome" : undefined,
  });
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    userAgent: USER_AGENT,
    locale: "ro-RO",
  });
  const page = await context.newPage();

  const vendorPath = new URL(VENDOR_URL).pathname;
  const visitedPages = new Set();
  const pageQueue = [VENDOR_URL];
  const productMap = new Map();
  const vendorPages = [];

  while (pageQueue.length && visitedPages.size < MAX_PAGES) {
    const pageUrl = pageQueue.shift();
    const normalizedPageUrl = cleanPageUrl(pageUrl) || pageUrl;
    if (visitedPages.has(normalizedPageUrl)) continue;
    visitedPages.add(normalizedPageUrl);
    const result = await collectVendorPage(page, pageUrl, vendorPath);
    vendorPages.push(result);
    for (const product of result.products) {
      if (productMap.size >= MAX_PRODUCTS) break;
      productMap.set(product.url, product);
    }
    for (const nextUrl of result.pageLinks) {
      if (!visitedPages.has(nextUrl) && !pageQueue.includes(nextUrl)) pageQueue.push(nextUrl);
    }
    console.log(`Vendor page ${visitedPages.size}: ${result.products.length} products, ${result.pageLinks.length} page links`);
  }

  const products = [...productMap.values()];
  await writeJson(path.join(OUT_DIR, "vendor_pages.json"), vendorPages);
  await writeJson(path.join(OUT_DIR, "vendor_products.json"), {
    sourceVendorUrl: VENDOR_URL,
    scrapedAt: new Date().toISOString(),
    pageCount: visitedPages.size,
    productCount: products.length,
    products,
  });

  const summary = {
    sourceVendorUrl: VENDOR_URL,
    outputDir: OUT_DIR,
    scrapedAt: new Date().toISOString(),
    pageCount: visitedPages.size,
    productCount: products.length,
    products: [],
    failures: [],
  };

  for (const [index, product] of products.entries()) {
    try {
      summary.products.push(await scrapeProduct(page, product, index, products.length));
    } catch (error) {
      summary.failures.push({
        productId: productIdFromUrl(product.url),
        title: product.title,
        url: product.url,
        error: String(error.message || error),
      });
    }
    await sleep(700);
  }

  await writeJson(path.join(OUT_DIR, "scrape_summary.json"), summary);
  await browser.close();
  console.log(`Done: ${path.join(OUT_DIR, "scrape_summary.json")}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
