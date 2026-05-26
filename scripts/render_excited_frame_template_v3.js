const { chromium } = require("playwright");
const path = require("path");

const root = path.resolve(__dirname, "..");
const outDir = path.join(root, "experiments/20260522_single_frame_template_v3");

async function renderPage(page, url, output, options = {}) {
  await page.goto(url);
  await page.waitForSelector("#ready");
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: output, ...options });
}

async function render() {
  const browser = await chromium.launch();

  const page = await browser.newPage({ viewport: { width: 1500, height: 1500 }, deviceScaleFactor: 1 });
  const template = `file://${path.join(outDir, "excited_frame_v3_template.html")}`;
  await renderPage(page, template, path.join(outDir, "excited_frame_v3_preview.png"));
  await renderPage(
    page,
    `${template}?mode=overlay`,
    path.join(outDir, "excited_frame_v3_overlay_transparent.png"),
    { omitBackground: true },
  );
  await page.close();

  const fontPage = await browser.newPage({ viewport: { width: 1500, height: 620 }, deviceScaleFactor: 1 });
  await renderPage(
    fontPage,
    `file://${path.join(outDir, "font_candidate_preview.html")}`,
    path.join(outDir, "font_candidate_preview.png"),
  );
  await fontPage.close();

  await browser.close();
}

render().catch((error) => {
  console.error(error);
  process.exit(1);
});
