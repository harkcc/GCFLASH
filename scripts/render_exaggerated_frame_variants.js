const { chromium } = require("playwright");
const path = require("path");

const root = path.resolve(__dirname, "..");
const outDir = path.join(root, "experiments/20260522_exaggerated_frame_variants");
const base = `file://${path.join(outDir, "exaggerated_frame_variants.html")}`;

async function renderPage(browser, viewport, url, output, options = {}) {
  const page = await browser.newPage({ viewport, deviceScaleFactor: 1 });
  await page.goto(url);
  await page.waitForSelector("#ready");
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: output, ...options });
  await page.close();
}

async function render() {
  const browser = await chromium.launch();

  await renderPage(
    browser,
    { width: 2200, height: 2320 },
    `${base}?mode=sheet`,
    path.join(outDir, "exaggerated_frame_variants_sheet.png"),
  );

  for (const id of ["tealClaw", "neonFang", "toolSlash", "magentaOrnament"]) {
    await renderPage(
      browser,
      { width: 1500, height: 1500 },
      `${base}?mode=single&id=${id}`,
      path.join(outDir, `${id}_preview.png`),
    );
    await renderPage(
      browser,
      { width: 1500, height: 1500 },
      `${base}?mode=overlay&id=${id}`,
      path.join(outDir, `${id}_overlay_transparent.png`),
      { omitBackground: true },
    );
  }

  await browser.close();
}

render().catch((error) => {
  console.error(error);
  process.exit(1);
});
