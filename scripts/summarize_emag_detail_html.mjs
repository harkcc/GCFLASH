import fs from "node:fs/promises";
import path from "node:path";

const SAMPLE_ROOT =
  process.argv[2] ||
  path.resolve("references/user_cases/20260521_emag_cangswjp");

async function readJson(filePath) {
  return JSON.parse(await fs.readFile(filePath, "utf8"));
}

function median(values) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];
}

function topEntries(map, limit = 12) {
  return [...map.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([key, count]) => ({ key, count }));
}

function classify(meta) {
  if (meta.imageCount >= 8 && meta.maxImagesPerRow <= 1) return "single_column_long_strip";
  if (meta.maxImagesPerRow >= 3) return "multi_image_row_layout";
  if (meta.tableCount > 0) return "table_heavy";
  if (meta.headingCount >= 3 && meta.paragraphCount >= 3) return "mixed_text_and_visual";
  return "image_led_basic";
}

async function main() {
  const productsRoot = path.join(SAMPLE_ROOT, "products");
  const productDirs = await fs.readdir(productsRoot);
  const metas = [];

  for (const dirName of productDirs) {
    const metaPath = path.join(productsRoot, dirName, "description_meta.json");
    try {
      metas.push(await readJson(metaPath));
    } catch {}
  }

  const ok = metas.filter((meta) => meta.found);
  const families = new Map();
  const maxRow = new Map();
  const blockTags = new Map();
  const imgHosts = new Map();

  for (const meta of ok) {
    const family = classify(meta);
    families.set(family, (families.get(family) || 0) + 1);
    maxRow.set(String(meta.maxImagesPerRow), (maxRow.get(String(meta.maxImagesPerRow)) || 0) + 1);

    for (const block of meta.blocks || []) {
      blockTags.set(block.tag, (blockTags.get(block.tag) || 0) + 1);
    }

    for (const image of meta.images || []) {
      try {
        const host = new URL(image.src).hostname;
        imgHosts.set(host, (imgHosts.get(host) || 0) + 1);
      } catch {}
    }
  }

  const summary = {
    sampleRoot: SAMPLE_ROOT,
    generatedAt: new Date().toISOString(),
    totalProducts: metas.length,
    foundDescriptions: ok.length,
    missingDescriptions: metas.length - ok.length,
    metrics: {
      avgImageCount: Number((ok.reduce((sum, meta) => sum + meta.imageCount, 0) / Math.max(ok.length, 1)).toFixed(2)),
      medianImageCount: median(ok.map((meta) => meta.imageCount)),
      avgTextLength: Number((ok.reduce((sum, meta) => sum + meta.textLength, 0) / Math.max(ok.length, 1)).toFixed(2)),
      medianTextLength: median(ok.map((meta) => meta.textLength)),
      avgMaxImagesPerRow: Number((ok.reduce((sum, meta) => sum + meta.maxImagesPerRow, 0) / Math.max(ok.length, 1)).toFixed(2)),
      productsWithThreePlusImagesPerRow: ok.filter((meta) => meta.maxImagesPerRow >= 3).length,
      productsWithTables: ok.filter((meta) => meta.tableCount > 0).length,
      productsWithIframes: ok.filter((meta) => meta.iframeCount > 0).length,
      productsWithVideos: ok.filter((meta) => meta.videoCount > 0).length,
    },
    familyDistribution: topEntries(families),
    maxImagesPerRowDistribution: topEntries(maxRow),
    commonBlockTags: topEntries(blockTags),
    commonImageHosts: topEntries(imgHosts),
    examples: ok.slice(0, 12).map((meta) => ({
      productId: meta.productId,
      selector: meta.selector,
      imageCount: meta.imageCount,
      maxImagesPerRow: meta.maxImagesPerRow,
      textLength: meta.textLength,
      family: classify(meta),
    })),
  };

  await fs.writeFile(
    path.join(SAMPLE_ROOT, "description_analysis_summary.json"),
    JSON.stringify(summary, null, 2),
  );

  const lines = [
    "# eMAG detail HTML structure summary",
    "",
    `- Sample root: ${SAMPLE_ROOT}`,
    `- Products with captured descriptions: ${summary.foundDescriptions}/${summary.totalProducts}`,
    `- Avg image count: ${summary.metrics.avgImageCount}`,
    `- Median image count: ${summary.metrics.medianImageCount}`,
    `- Avg text length: ${summary.metrics.avgTextLength}`,
    `- Median text length: ${summary.metrics.medianTextLength}`,
    `- Products with 3+ images in same mobile row: ${summary.metrics.productsWithThreePlusImagesPerRow}`,
    `- Products with tables: ${summary.metrics.productsWithTables}`,
    "",
    "## Family distribution",
    ...summary.familyDistribution.map((item) => `- ${item.key}: ${item.count}`),
    "",
    "## Max images per row",
    ...summary.maxImagesPerRowDistribution.map((item) => `- ${item.key}: ${item.count}`),
    "",
    "## Common image hosts",
    ...summary.commonImageHosts.map((item) => `- ${item.key}: ${item.count}`),
  ];

  await fs.writeFile(
    path.join(SAMPLE_ROOT, "description_analysis_summary.md"),
    `${lines.join("\n")}\n`,
  );
}

await main();
