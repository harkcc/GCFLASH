import { chromium } from "playwright";
import fs from "node:fs/promises";
import path from "node:path";

const SAMPLE_ROOT =
  process.argv[2] ||
  path.resolve("references/user_cases/20260521_emag_cangswjp");

const FORCE = process.argv.includes("--force");

const USER_AGENT =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36";

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function readJson(filePath) {
  return JSON.parse(await fs.readFile(filePath, "utf8"));
}

async function writeJson(filePath, data) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, JSON.stringify(data, null, 2));
}

async function writeText(filePath, value) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, value);
}

async function loadProducts(sampleRoot) {
  const summary = await readJson(path.join(sampleRoot, "scrape_summary.json"));
  return summary.products.map((product) => ({
    ...product,
    productDir: path.join(sampleRoot, product.localDir),
  }));
}

async function preparePage(page) {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.setExtraHTTPHeaders({
    "accept-language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
  });
}

async function expandDescription(page) {
  const tab = page.locator("a[href='#description-section']").first();
  if (await tab.count()) {
    await tab.click({ force: true }).catch(() => {});
    await sleep(500);
  }

  const root = page.locator("#collapse-wrapper-description, .product-page-description").first();
  if (await root.count()) {
    await root.scrollIntoViewIfNeeded().catch(() => {});
    await sleep(250);
  }

  const openButtons = page.locator(
    "#collapse-wrapper-description .js-description-open, .product-page-description .js-description-open",
  );
  const buttonCount = await openButtons.count();
  for (let index = 0; index < Math.min(buttonCount, 3); index += 1) {
    const button = openButtons.nth(index);
    if (await button.isVisible().catch(() => false)) {
      await button.click({ force: true }).catch(() => {});
      await sleep(350);
    }
  }
}

function collectDescriptionState() {
  const rootCandidates = [
    "#description-body",
    "#collapse-wrapper-description",
    ".product-page-description-text",
    ".product-page-description",
  ];

  const root =
    rootCandidates
      .map((selector) => document.querySelector(selector))
      .find((node) => node && node.innerText && node.innerText.trim().length > 40) || null;

  if (!root) {
    return {
      found: false,
      title: document.title,
      url: location.href,
    };
  }

  const blocks = [...root.children].map((node, index) => {
    const rect = node.getBoundingClientRect();
    return {
      index,
      tag: node.tagName,
      className: String(node.className || ""),
      childCount: node.children.length,
      textLength: (node.innerText || "").trim().length,
      imageCount: node.querySelectorAll("img").length,
      width: Math.round(rect.width),
      height: Math.round(rect.height),
      style: node.getAttribute("style") || "",
    };
  });

  const images = [...root.querySelectorAll("img")].map((img, index) => {
    const rect = img.getBoundingClientRect();
    return {
      index,
      src: img.currentSrc || img.src || img.getAttribute("data-src") || "",
      alt: img.alt || "",
      width: Math.round(rect.width),
      height: Math.round(rect.height),
      naturalWidth: img.naturalWidth || 0,
      naturalHeight: img.naturalHeight || 0,
      top: Math.round(rect.top),
      left: Math.round(rect.left),
      className: String(img.className || ""),
      style: img.getAttribute("style") || "",
    };
  });

  const rowGroups = [];
  for (const image of images) {
    const row = rowGroups.find((item) => Math.abs(item.top - image.top) <= 18);
    if (row) {
      row.count += 1;
      row.widths.push(image.width);
      row.heights.push(image.height);
    } else {
      rowGroups.push({
        top: image.top,
        count: 1,
        widths: [image.width],
        heights: [image.height],
      });
    }
  }

  const tagFrequency = {};
  for (const node of root.querySelectorAll("*")) {
    const tag = node.tagName.toLowerCase();
    tagFrequency[tag] = (tagFrequency[tag] || 0) + 1;
  }

  return {
    found: true,
    url: location.href,
    title: document.title,
    selector:
      rootCandidates.find((selector) => document.querySelector(selector) === root) || "unknown",
    rootTag: root.tagName,
    rootClassName: String(root.className || ""),
    rootChildCount: root.children.length,
    textLength: (root.innerText || "").trim().length,
    headingCount: root.querySelectorAll("h1, h2, h3, h4, h5, h6").length,
    paragraphCount: root.querySelectorAll("p").length,
    tableCount: root.querySelectorAll("table").length,
    listCount: root.querySelectorAll("ul, ol").length,
    iframeCount: root.querySelectorAll("iframe").length,
    videoCount: root.querySelectorAll("video").length,
    imageCount: images.length,
    maxImagesPerRow: rowGroups.reduce((max, row) => Math.max(max, row.count), 0),
    rowDistribution: rowGroups.map((row) => ({
      top: row.top,
      count: row.count,
      widths: row.widths,
      heights: row.heights,
    })),
    blocks,
    images,
    tagFrequency,
    textSample: (root.innerText || "").trim().slice(0, 1200),
    outerHTML: root.outerHTML,
    innerHTML: root.innerHTML,
  };
}

async function scrapeOne(page, product) {
  const metaPath = path.join(product.productDir, "description_meta.json");
  const htmlPath = path.join(product.productDir, "description.html");

  if (!FORCE) {
    try {
      await fs.access(metaPath);
      await fs.access(htmlPath);
      return {
        productId: product.productId,
        status: "skipped",
      };
    } catch {}
  }

  await page.goto(product.url, {
    waitUntil: "domcontentloaded",
    timeout: 60_000,
  });
  await sleep(2_500);
  await expandDescription(page);
  await sleep(500);

  const state = await page.evaluate(collectDescriptionState);
  const screenshotPath = path.join(product.productDir, "description_mobile.png");
  const rootLocator = page.locator("#collapse-wrapper-description, .product-page-description").first();
  if (await rootLocator.count()) {
    await rootLocator.screenshot({ path: screenshotPath }).catch(() => {});
  }

  const meta = {
    productId: product.productId,
    productUrl: product.url,
    localDir: product.localDir,
    scrapedAt: new Date().toISOString(),
    ...state,
  };

  if (!state.found) {
    await writeJson(metaPath, meta);
    return {
      productId: product.productId,
      status: "missing",
    };
  }

  await writeJson(metaPath, meta);
  await writeText(htmlPath, state.outerHTML);
  await writeText(path.join(product.productDir, "description_inner.html"), state.innerHTML);

  return {
    productId: product.productId,
    status: "ok",
    imageCount: state.imageCount,
    maxImagesPerRow: state.maxImagesPerRow,
  };
}

async function main() {
  const products = await loadProducts(SAMPLE_ROOT);
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    userAgent: USER_AGENT,
  });
  await preparePage(page);

  const results = [];
  for (const product of products) {
    try {
      const result = await scrapeOne(page, product);
      results.push(result);
      console.log(
        `${product.productId} ${result.status}${result.imageCount ? ` imgs=${result.imageCount}` : ""}${result.maxImagesPerRow ? ` rowMax=${result.maxImagesPerRow}` : ""}`,
      );
    } catch (error) {
      results.push({
        productId: product.productId,
        status: "error",
        error: error instanceof Error ? error.message : String(error),
      });
      console.error(`${product.productId} error`, error);
    }
  }

  await browser.close();

  await writeJson(path.join(SAMPLE_ROOT, "description_scrape_summary.json"), {
    sampleRoot: SAMPLE_ROOT,
    scrapedAt: new Date().toISOString(),
    productCount: products.length,
    results,
  });
}

await main();
