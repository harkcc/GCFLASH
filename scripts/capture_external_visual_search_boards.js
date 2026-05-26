const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const outDir = path.join(root, "references/external_ecommerce_frame_scan_20260522");

const boards = [
  {
    id: "bing_wb_ozon_cards",
    url: "https://www.bing.com/images/search?q=Wildberries%20Ozon%20product%20card%20infographic%20design%20frame%20badge",
    notes: "visual search board for WB/Ozon marketplace cards, infographic density, labels, and badge placement",
  },
  {
    id: "bing_ecommerce_3d_badge_frame",
    url: "https://www.bing.com/images/search?q=ecommerce%20product%20poster%203D%20badge%20frame%20brand%20logo%20design",
    notes: "visual search board for 3D badges, brand frames, and product poster layouts",
  },
  {
    id: "bing_metallic_nameplate_badge",
    url: "https://www.bing.com/images/search?q=3D%20metallic%20nameplate%20badge%20logo%20frame%20ecommerce%20design",
    notes: "visual search board for metallic/glossy nameplate references",
  },
  {
    id: "pinterest_search_wb_ozon",
    url: "https://www.pinterest.com/search/pins/?q=wildberries%20ozon%20product%20card%20design%20infographic",
    notes: "Pinterest search board for WB/Ozon product-card visual language",
  },
  {
    id: "dribbble_product_banner",
    url: "https://dribbble.com/search/product%20banner",
    notes: "Dribbble product banner board: typography/background/product/brand compositions",
  },
  {
    id: "behance_wb_ozon_search",
    url: "https://www.behance.net/search/projects/wildberries%20ozon%20product%20card",
    notes: "Behance search board for marketplace product-card projects",
  },
  {
    id: "freepik_ecommerce_badge",
    url: "https://www.freepik.com/search?format=search&query=ecommerce%20product%20badge%20frame&type=psd",
    notes: "Freepik board for PSD badge/frame material directions",
  },
];

async function dismiss(page) {
  for (const label of ["Accept", "Accept all", "I agree", "Got it", "Allow all", "OK", "Принять"]) {
    try {
      const button = page.getByRole("button", { name: new RegExp(label, "i") }).first();
      if (await button.isVisible({ timeout: 800 })) {
        await button.click({ timeout: 1200 });
        await page.waitForTimeout(500);
      }
    } catch {
      // Ignore missing buttons.
    }
  }
}

async function capture() {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1600, height: 1600 },
    deviceScaleFactor: 1,
    locale: "en-US",
    userAgent:
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
  });
  const manifest = [];

  for (const board of boards) {
    const page = await context.newPage();
    const output = path.join(outDir, `${board.id}.png`);
    const entry = { ...board, output, ok: false };
    try {
      await page.goto(board.url, { waitUntil: "domcontentloaded", timeout: 45000 });
      await page.waitForTimeout(3500);
      await dismiss(page);
      await page.evaluate(() => window.scrollTo(0, 260));
      await page.waitForTimeout(1200);
      await page.screenshot({ path: output });
      entry.title = await page.title();
      entry.ok = true;
    } catch (error) {
      entry.error = String(error && error.message ? error.message : error);
      try {
        await page.screenshot({ path: output });
      } catch {
        // Ignore.
      }
    } finally {
      manifest.push(entry);
      await page.close();
    }
  }

  await browser.close();
  fs.writeFileSync(path.join(outDir, "visual_search_boards_manifest.json"), JSON.stringify(manifest, null, 2));
  fs.writeFileSync(
    path.join(outDir, "visual_search_boards_manifest.md"),
    [
      "# External visual search boards",
      "",
      ...manifest.map((entry) => [
        `## ${entry.id}`,
        "",
        `- url: ${entry.url}`,
        `- status: ${entry.ok ? "ok" : `failed: ${entry.error || "unknown"}`}`,
        `- screenshot: ${path.basename(entry.output)}`,
        `- notes: ${entry.notes}`,
        "",
      ].join("\n")),
    ].join("\n"),
  );
}

capture().catch((error) => {
  console.error(error);
  process.exit(1);
});
