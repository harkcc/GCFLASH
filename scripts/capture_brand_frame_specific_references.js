const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const outDir = path.join(root, "references/external_ecommerce_frame_scan_20260522/brand_frame_specific");

const refs = [
  {
    id: "mday_frame_overlay",
    url: "https://www.noreason.io/scripts/mday-frame-overlay",
    note: "non-destructive decorative frames, corner flourishes, and branded accents over product imagery",
  },
  {
    id: "logobean_frame_logo",
    url: "https://www.logobean.com/frame-logo-maker.html",
    note: "logo text/icon enclosed by a frame to create structure, emphasis, and constrained brand focus",
  },
  {
    id: "shutterstock_brand_logo_frame",
    url: "https://www.shutterstock.com/search/brand-logo-frame",
    note: "stock library taxonomy for logo frames, decorative labels, badge shapes, and packaging-style brand frames",
  },
  {
    id: "graphicsfamily_3d_metallic_frame",
    url: "https://graphicsfamily.com/downloads/3d-metallic-frame-modern-logo-mockup",
    note: "3D metallic logo frame and layered PSD/smart-object material reference",
  },
  {
    id: "envato_3d_badge",
    url: "https://elements.envato.com/best-seller-badge-6WWFEPC",
    note: "3D ecommerce badge/sticker material for premium product highlights",
  },
  {
    id: "freepik_brand_frame_search",
    url: "https://www.freepik.com/search?format=search&query=brand%20logo%20frame%20badge&type=psd",
    note: "PSD search board for brand logo frame and badge templates",
  },
];

async function dismiss(page) {
  for (const label of ["Accept", "Accept all", "I agree", "Got it", "OK"]) {
    try {
      const button = page.getByRole("button", { name: new RegExp(label, "i") }).first();
      if (await button.isVisible({ timeout: 700 })) {
        await button.click({ timeout: 1000 });
        await page.waitForTimeout(300);
      }
    } catch {
      // Ignore.
    }
  }
}

async function run() {
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
  for (const ref of refs) {
    const page = await context.newPage();
    const output = path.join(outDir, `${ref.id}.png`);
    const entry = { ...ref, output, ok: false };
    try {
      await page.goto(ref.url, { waitUntil: "domcontentloaded", timeout: 45000 });
      await page.waitForTimeout(3000);
      await dismiss(page);
      await page.screenshot({ path: output, fullPage: false });
      entry.title = await page.title();
      entry.ok = true;
    } catch (error) {
      entry.error = String(error && error.message ? error.message : error);
      try {
        await page.screenshot({ path: output, fullPage: false });
      } catch {
        // Ignore.
      }
    } finally {
      manifest.push(entry);
      await page.close();
    }
  }
  await browser.close();
  fs.writeFileSync(path.join(outDir, "brand_frame_specific_manifest.json"), JSON.stringify(manifest, null, 2));
  fs.writeFileSync(
    path.join(outDir, "brand_frame_specific_manifest.md"),
    [
      "# Brand-frame-specific external references",
      "",
      ...manifest.map((entry) => [
        `## ${entry.id}`,
        "",
        `- url: ${entry.url}`,
        `- status: ${entry.ok ? "ok" : `failed: ${entry.error || "unknown"}`}`,
        `- screenshot: ${path.basename(entry.output)}`,
        `- note: ${entry.note}`,
        "",
      ].join("\n")),
    ].join("\n"),
  );
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
