import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";

export function productIdFromUrl(url) {
  const match = String(url).match(/\/pd\/([^/?#]+)\/?/);
  return match ? match[1] : crypto.createHash("sha1").update(String(url)).digest("hex").slice(0, 10);
}

export function slugify(input, fallback = "product") {
  return (
    String(input || fallback)
      .normalize("NFKD")
      .replace(/[^\w\s.-]/g, "")
      .trim()
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-")
      .slice(0, 90) || fallback
  );
}

async function exists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function writeJson(filePath, data) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, JSON.stringify(data, null, 2));
}

async function writeText(filePath, data) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, data || "");
}

export function productDir(outDir, product, index) {
  const productId = product.productId || productIdFromUrl(product.url);
  return path.join(
    outDir,
    "products",
    `${String(index + 1).padStart(2, "0")}_${productId}_${slugify(product.title)}`,
  );
}

export async function collectProduct(tab, outDir, product, index) {
  const productId = product.productId || productIdFromUrl(product.url);
  const dir = productDir(outDir, product, index);
  if (await exists(path.join(dir, "description_meta.json"))) {
    return { productId, skipped: true, localDir: path.relative(outDir, dir) };
  }

  await fs.mkdir(dir, { recursive: true });
  await tab.goto(product.url);
  await tab.playwright.waitForLoadState({ state: "domcontentloaded", timeoutMs: 30_000 }).catch(() => {});
  await tab.playwright.waitForTimeout(1400);

  const descriptionTab = tab.playwright.locator("a[href='#description-section']").first();
  if (await descriptionTab.count().catch(() => 0)) {
    await descriptionTab.click({ force: true, timeoutMs: 2500 }).catch(() => {});
  }
  await tab.playwright.waitForTimeout(500);

  for (const selector of [".js-description-open", "button:has-text('Vezi mai mult')", "a:has-text('Vezi mai mult')"]) {
    const locator = tab.playwright.locator(selector).first();
    if (await locator.count().catch(() => 0)) {
      await locator.click({ force: true, timeoutMs: 1500 }).catch(() => {});
    }
  }
  await tab.playwright.waitForTimeout(400);

  const state = await tab.playwright.evaluate(() => {
    const selectors = [
      "#description-body",
      "#collapse-wrapper-description",
      ".product-page-description-text",
      ".product-page-description",
      "#description-section",
    ];
    const root = selectors
      .map((selector) => document.querySelector(selector))
      .find((node) => node && (((node.innerText || "").trim().length > 20) || node.querySelector("img")));

    const allProductImages = [...document.querySelectorAll("img")]
      .map((img, index) => {
        const rect = img.getBoundingClientRect();
        return {
          index,
          src: img.currentSrc || img.src || img.getAttribute("data-src") || "",
          alt: img.alt || "",
          naturalWidth: img.naturalWidth || 0,
          naturalHeight: img.naturalHeight || 0,
          renderedWidth: Math.round(rect.width || 0),
          renderedHeight: Math.round(rect.height || 0),
          top: Math.round(rect.top || 0),
          left: Math.round(rect.left || 0),
          inDescription: Boolean(
            img.closest(
              "#description-body,#collapse-wrapper-description,.product-page-description-text,.product-page-description,#description-section",
            ),
          ),
          style: img.getAttribute("style") || "",
        };
      })
      .filter((image) => image.src);

    if (!root) {
      return {
        found: false,
        url: location.href,
        title: document.title,
        h1: document.querySelector("h1")?.innerText?.trim() || "",
        allProductImages,
      };
    }

    const descriptionImages = allProductImages.filter((image) => image.inDescription);
    const tagFrequency = {};
    for (const node of root.querySelectorAll("*")) {
      const tag = node.tagName.toLowerCase();
      tagFrequency[tag] = (tagFrequency[tag] || 0) + 1;
    }

    const rowDistribution = [];
    for (const image of descriptionImages) {
      const row = rowDistribution.find((item) => Math.abs(item.top - image.top) <= 18);
      if (row) {
        row.count += 1;
        row.widths.push(image.renderedWidth);
        row.heights.push(image.renderedHeight);
      } else {
        rowDistribution.push({
          top: image.top,
          count: 1,
          widths: [image.renderedWidth],
          heights: [image.renderedHeight],
        });
      }
    }

    return {
      found: true,
      url: location.href,
      title: document.title,
      h1: document.querySelector("h1")?.innerText?.trim() || "",
      selector: selectors.find((selector) => document.querySelector(selector) === root) || "unknown",
      textLength: (root.innerText || "").trim().length,
      textSample: (root.innerText || "").trim().slice(0, 1800),
      headingCount: root.querySelectorAll("h1,h2,h3,h4,h5,h6").length,
      paragraphCount: root.querySelectorAll("p").length,
      tableCount: root.querySelectorAll("table").length,
      listCount: root.querySelectorAll("ul,ol").length,
      iframeCount: root.querySelectorAll("iframe").length,
      videoCount: root.querySelectorAll("video").length,
      imageCount: descriptionImages.length,
      gifCount: descriptionImages.filter((image) => /\.gif(\?|$)/i.test(image.src)).length,
      maxImagesPerRow: rowDistribution.reduce((max, row) => Math.max(max, row.count), 0),
      rowDistribution,
      tagFrequency,
      descriptionImages,
      allProductImages,
      outerHTML: root.outerHTML,
      innerHTML: root.innerHTML,
    };
  });

  const meta = {
    productId,
    listing: product,
    scrapedAt: new Date().toISOString(),
    ...state,
  };

  await writeJson(path.join(dir, "description_meta.json"), meta);
  if (state.found) {
    await writeText(path.join(dir, "description_outer.html"), state.outerHTML);
    await writeText(path.join(dir, "description_inner.html"), state.innerHTML);
  }

  return {
    productId,
    title: state.h1 || product.title,
    url: product.url,
    localDir: path.relative(outDir, dir),
    found: state.found,
    imageCount: state.imageCount || 0,
    gifCount: state.gifCount || 0,
    tableCount: state.tableCount || 0,
    textLength: state.textLength || 0,
    maxImagesPerRow: state.maxImagesPerRow || 0,
  };
}

export async function runChromeScrapeBatch(browser, outDir, batchSize = 8) {
  const productsData = JSON.parse(await fs.readFile(path.join(outDir, "vendor_products.json"), "utf8"));
  const products = productsData.products;
  const pending = [];
  for (let index = 0; index < products.length; index += 1) {
    const dir = productDir(outDir, products[index], index);
    if (!(await exists(path.join(dir, "description_meta.json")))) pending.push([index, products[index]]);
    if (pending.length >= batchSize) break;
  }

  const tab = await browser.tabs.new();
  const results = [];
  const failures = [];
  for (const [index, product] of pending) {
    try {
      const result = await collectProduct(tab, outDir, product, index);
      results.push(result);
      console.log(`[${index + 1}/${products.length}] ${result.productId} found=${result.found} imgs=${result.imageCount}`);
    } catch (error) {
      const productId = product.productId || productIdFromUrl(product.url);
      const failure = {
        index,
        productId,
        title: product.title,
        url: product.url,
        error: String(error?.message || error),
      };
      failures.push(failure);
      console.log(`[${index + 1}/${products.length}] FAIL ${productId} ${failure.error}`);
    }
  }
  await tab.close().catch(() => {});
  return { batchSize: pending.length, results, failures };
}
