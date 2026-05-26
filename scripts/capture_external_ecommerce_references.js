const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const outDir = path.join(root, "references/external_ecommerce_frame_scan_20260522");

const references = [
  {
    id: "rendery3d",
    type: "ai_listing_tool",
    url: "https://rendery3d.com/",
    notes: ["3D-rendered listing aesthetic", "logo-safe details", "brand styles", "custom preset from competitor listings"],
  },
  {
    id: "picaz",
    type: "ai_marketplace_tool",
    url: "https://picazai.com/",
    notes: ["marketplace-ready listings", "brand colors and design guidelines", "template-based bulk production", "A/B test winners"],
  },
  {
    id: "marketplace_hero",
    type: "ai_marketplace_tool",
    url: "https://marketplacehero.ru/",
    notes: ["Wildberries/Ozon/Yandex card generator", "editable logo/text/blocks/icons", "upload photo then choose scene"],
  },
  {
    id: "kartochka_wb",
    type: "ai_marketplace_tool",
    url: "https://www.kartochka-wb.ru/",
    notes: ["WB/Ozon/Yandex templates", "background AI", "large design element library", "ready marketplace templates"],
  },
  {
    id: "orshot_ecommerce",
    type: "template_automation",
    url: "https://orshot.com/use-cases/t/auto-generate-e-commerce-images",
    notes: ["parameterized text/images/colors", "visual editor", "API/no-code/spreadsheet generation"],
  },
  {
    id: "bannerbear_template",
    type: "template_automation",
    url: "https://www.bannerbear.com/help/articles/15-what-is-a-template/",
    notes: ["reusable templates", "dynamic text/image placeholders", "custom SVGs with gradients and shadows"],
  },
  {
    id: "figma_buzz_assets",
    type: "template_automation",
    url: "https://help.figma.com/hc/en-us/articles/31271589645079-Create-marketing-assets-in-Figma-Buzz",
    notes: ["locked brand templates", "edit content without touching design", "bulk create from XLSX"],
  },
  {
    id: "behance_product_card_search",
    type: "design_community",
    url: "https://www.behance.net/search/projects/product%20card%20ecommerce",
    notes: ["product card concepts", "Ozon marketplace systems", "infographic product cards"],
  },
  {
    id: "behance_wb_amazon_vol3",
    type: "design_community",
    url: "https://www.behance.net/gallery/126158809/Wildberries-Amazon-product-cards-design-Vol3?locale=en_US",
    notes: ["Wildberries/Amazon/Ozon product-card portfolio", "high-density marketplace card examples"],
  },
  {
    id: "pinterest_wb_ozon_card",
    type: "moodboard",
    url: "https://www.pinterest.com/pin/wildberries-infographic-marketplace-card-wildberries-ozon-design-idea-logo-card-wildberries-product-card-design--282249101638978820/",
    notes: ["Pinterest WB/Ozon product-card pin", "thumbnail-first marketplace inspiration"],
  },
  {
    id: "freepik_3d_ecommerce_banner",
    type: "asset_marketplace",
    url: "https://www.freepik.com/psd/3d-e-commerce-banner",
    notes: ["3D ecommerce banner PSD patterns", "podiums", "badges", "promotion materials"],
  },
  {
    id: "envato_best_seller_badge",
    type: "asset_marketplace",
    url: "https://elements.envato.com/best-seller-badge-6WWFEPC",
    notes: ["3D ecommerce badge", "premium sticker/seal material language"],
  },
  {
    id: "graphicsfamily_3d_metallic_frame",
    type: "asset_marketplace",
    url: "https://graphicsfamily.com/downloads/3d-metallic-frame-modern-logo-mockup",
    notes: ["3D metallic frame/logo mockup", "layered PSD/smart object pattern"],
  },
  {
    id: "designries_listing_templates",
    type: "listing_template",
    url: "https://www.designries.com/product-page/designries-essential-oils-product-listing-templates-editable-canva-images",
    notes: ["square listing templates", "editable branding/colors/product photos", "Amazon/Etsy/eBay/Walmart/Shopify"],
  },
];

async function dismissCommonPopups(page) {
  const labels = [
    "Accept",
    "Accept all",
    "I agree",
    "Agree",
    "Got it",
    "Allow all",
    "Принять",
    "Согласен",
    "Согласиться",
    "ОК",
    "OK",
  ];
  for (const label of labels) {
    const button = page.getByRole("button", { name: new RegExp(label, "i") }).first();
    try {
      if (await button.isVisible({ timeout: 700 })) {
        await button.click({ timeout: 1200 });
        await page.waitForTimeout(300);
      }
    } catch {
      // Ignore sites without that popup.
    }
  }
}

async function collectVisibleImageSignals(page) {
  return page.evaluate(() => {
    const viewportW = window.innerWidth;
    const viewportH = window.innerHeight;
    const images = Array.from(document.images)
      .map((img) => {
        const rect = img.getBoundingClientRect();
        return {
          alt: img.alt || "",
          src: img.currentSrc || img.src || "",
          x: Math.round(rect.x),
          y: Math.round(rect.y),
          w: Math.round(rect.width),
          h: Math.round(rect.height),
          visible:
            rect.width >= 80 &&
            rect.height >= 80 &&
            rect.bottom >= 0 &&
            rect.right >= 0 &&
            rect.top <= viewportH * 3 &&
            rect.left <= viewportW,
        };
      })
      .filter((img) => img.visible)
      .slice(0, 30);
    const headings = Array.from(document.querySelectorAll("h1,h2,h3"))
      .map((el) => el.textContent.trim().replace(/\s+/g, " "))
      .filter(Boolean)
      .slice(0, 20);
    return { title: document.title, headings, images };
  });
}

async function capture() {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1300 },
    deviceScaleFactor: 1,
    locale: "en-US",
    userAgent:
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
  });
  const manifest = [];

  for (const ref of references) {
    const page = await context.newPage();
    const screenshot = path.join(outDir, `${ref.id}.png`);
    const clipped = path.join(outDir, `${ref.id}_top.png`);
    const entry = { ...ref, screenshot, top_screenshot: clipped, ok: false };
    try {
      await page.goto(ref.url, { waitUntil: "domcontentloaded", timeout: 45000 });
      await page.waitForTimeout(2500);
      await dismissCommonPopups(page);
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.waitForTimeout(500);
      entry.signals = await collectVisibleImageSignals(page);
      await page.screenshot({ path: clipped });
      await page.screenshot({ path: screenshot, fullPage: true });
      entry.ok = true;
    } catch (error) {
      entry.error = String(error && error.message ? error.message : error);
      try {
        await page.screenshot({ path: clipped });
      } catch {
        // Some pages fail before a screenshot can be captured.
      }
    } finally {
      manifest.push(entry);
      await page.close();
    }
  }

  await browser.close();
  fs.writeFileSync(path.join(outDir, "reference_capture_manifest.json"), JSON.stringify(manifest, null, 2));
  fs.writeFileSync(
    path.join(outDir, "reference_capture_manifest.md"),
    [
      "# External ecommerce reference capture manifest",
      "",
      ...manifest.map((entry) => {
        const status = entry.ok ? "ok" : `failed: ${entry.error || "unknown"}`;
        const headings = entry.signals?.headings?.slice(0, 5).join(" | ") || "";
        return [
          `## ${entry.id}`,
          "",
          `- url: ${entry.url}`,
          `- type: ${entry.type}`,
          `- status: ${status}`,
          `- screenshot: ${path.basename(entry.screenshot)}`,
          `- top screenshot: ${path.basename(entry.top_screenshot)}`,
          `- notes: ${entry.notes.join("; ")}`,
          headings ? `- visible headings: ${headings}` : "",
          "",
        ]
          .filter(Boolean)
          .join("\n");
      }),
    ].join("\n"),
  );
}

capture().catch((error) => {
  console.error(error);
  process.exit(1);
});
