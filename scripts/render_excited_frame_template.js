const { chromium } = require("playwright");
const path = require("path");

const root = path.resolve(__dirname, "..");
const outDir = path.join(root, "experiments/20260522_single_frame_template");

async function render() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1500, height: 1500 }, deviceScaleFactor: 1 });

  await page.goto(`file://${path.join(outDir, "excited_frame_v1_preview.html")}`);
  await page.waitForSelector("#ready");
  await page.screenshot({ path: path.join(outDir, "excited_frame_v1_preview.png") });

  await page.setContent(`
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <style>
          html, body { margin: 0; width: 1500px; height: 1500px; background: transparent; overflow: hidden; }
          img { position: absolute; inset: 0; width: 1500px; height: 1500px; display: block; }
        </style>
      </head>
      <body><img src="file://${path.join(outDir, "excited_frame_v1.svg")}"></body>
    </html>
  `);
  await page.screenshot({
    path: path.join(outDir, "excited_frame_v1_overlay_transparent.png"),
    omitBackground: true,
  });

  await browser.close();
}

render().catch((error) => {
  console.error(error);
  process.exit(1);
});
