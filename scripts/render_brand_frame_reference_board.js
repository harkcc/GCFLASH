const { chromium } = require("playwright");
const path = require("path");

const html = path.resolve(__dirname, "../references/external_ecommerce_frame_scan_20260522/brand_frame_reference_board.html");
const out = path.resolve(__dirname, "../references/external_ecommerce_frame_scan_20260522/brand_frame_reference_board.png");

async function render() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 2200, height: 2600 }, deviceScaleFactor: 1 });
  await page.goto(`file://${html}`);
  await page.waitForLoadState("load");
  await page.screenshot({ path: out, fullPage: true });
  await browser.close();
}

render().catch((error) => {
  console.error(error);
  process.exit(1);
});
