#!/usr/bin/env node
import { copyFile, mkdir, readFile, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';

const execFileAsync = promisify(execFile);

function arg(name, fallback = undefined) {
  const i = process.argv.indexOf(`--${name}`);
  if (i === -1) return fallback;
  return process.argv[i + 1] ?? fallback;
}

function requireArg(name) {
  const value = arg(name);
  if (!value) {
    console.error(`Missing --${name}`);
    process.exit(2);
  }
  return value;
}

async function readJson(file) {
  return JSON.parse(await readFile(file, 'utf8'));
}

function pad2(value) {
  return String(value).padStart(2, '0');
}

function slug(value) {
  return String(value)
    .replace(/[^a-zA-Z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .slice(0, 96);
}

function defaultTextPolicy(slot) {
  if (/no text/i.test(slot.copy_policy ?? '')) return 'no_text';
  return 'deterministic_overlay';
}

function pickTemplate(slot, templateDir) {
  for (const templateId of slot.default_template_cards ?? []) {
    const templateFile = path.join(templateDir, `${templateId}.json`);
    if (existsSync(templateFile)) return { templateId, templateFile };
  }
  throw new Error(`No available template for slot ${slot.slot}: ${slot.role}`);
}

function scorePlaceholder(slot, templateId) {
  return {
    slot: slot.slot,
    role: slot.role,
    template_id: templateId,
    status: 'pending_visual_review',
    total: null,
    dimension_scores: {
      product_fidelity: null,
      commercial_appeal: null,
      selling_point_accuracy: null,
      layout_readability: null,
      text_quality: null,
      style_consistency: null,
      technical_quality: null,
    },
    reviewer_votes: [],
    keep: [],
    fix: [],
    quick_wins: [],
    repair_prompt: '',
    psd_or_overlay_needed: defaultTextPolicy(slot) === 'deterministic_overlay',
  };
}

async function main() {
  const root = process.cwd();
  const truthFile = requireArg('truth');
  const outDir = requireArg('out');
  const suitePlanFile = arg('suite-plan', path.join(root, 'workflow/suite_plans/ecommerce_5_to_8_suite_plan.json'));
  const templateDir = arg('template-dir', path.join(root, 'workflow/template_cards'));
  const compilerFile = arg('compiler', path.join(root, 'scripts/compile_ecommerce_prompt.mjs'));
  const marketplace = arg('marketplace', 'Amazon');
  const sku = arg('sku');
  const truthKey = arg('truth-key');
  const slotsRequested = Number.parseInt(arg('slots', '5'), 10);
  const productImage = arg('product-image');

  if (!Number.isInteger(slotsRequested) || slotsRequested < 1 || slotsRequested > 8) {
    throw new Error('--slots must be an integer from 1 to 8');
  }

  const truthSource = await readJson(truthFile);
  const truth = truthKey ? truthSource[truthKey] : truthSource;
  if (!truth) throw new Error(`Could not find truth key: ${truthKey}`);

  const suitePlan = await readJson(suitePlanFile);
  const selectedSlots = suitePlan.slots.slice(0, slotsRequested);

  await mkdir(outDir, { recursive: true });
  const inputsDir = path.join(outDir, 'inputs');
  const scoreDir = path.join(outDir, 'scorecards');
  const repairDir = path.join(outDir, 'repair_prompts');
  await mkdir(inputsDir, { recursive: true });
  await mkdir(scoreDir, { recursive: true });
  await mkdir(repairDir, { recursive: true });

  const singleTruthFile = path.join(inputsDir, `${slug(sku ?? truthKey ?? truth.sku ?? truth.product_name ?? 'product')}.truth.json`);
  await writeFile(singleTruthFile, `${JSON.stringify(truth, null, 2)}\n`);
  if (productImage) {
    await copyFile(productImage, path.join(inputsDir, path.basename(productImage)));
  }

  const selectedSuite = {
    id: `${suitePlan.id}_selected`,
    source_suite_plan: suitePlan.id,
    sku: sku ?? truthKey ?? truth.sku ?? truth.product_name ?? 'unknown_sku',
    marketplace,
    slots: [],
    suite_consistency_rules: suitePlan.suite_consistency_rules,
  };

  const templateSelection = [];

  for (const slot of selectedSlots) {
    const { templateId, templateFile } = pickTemplate(slot, templateDir);
    const slotDirName = `slot_${pad2(slot.slot)}_${slug(slot.role)}_${templateId}`;
    const slotOutDir = path.join(outDir, slotDirName);
    const textPolicy = defaultTextPolicy(slot);

    await execFileAsync('node', [
      compilerFile,
      '--truth',
      singleTruthFile,
      '--template',
      templateFile,
      '--out',
      slotOutDir,
      '--sku',
      selectedSuite.sku,
      '--marketplace',
      marketplace,
      '--text-policy',
      textPolicy,
    ]);

    const slotMetadata = {
      slot: slot.slot,
      role: slot.role,
      buyer_question: slot.buyer_question,
      product_weight: slot.product_weight,
      copy_policy: slot.copy_policy,
      risk: slot.risk,
      template_id: templateId,
      text_policy: textPolicy,
      output_dir: slotDirName,
    };
    await writeFile(path.join(slotOutDir, 'slot_metadata.json'), `${JSON.stringify(slotMetadata, null, 2)}\n`);
    await writeFile(
      path.join(scoreDir, `slot_${pad2(slot.slot)}_${templateId}.score.json`),
      `${JSON.stringify(scorePlaceholder(slot, templateId), null, 2)}\n`,
    );
    await writeFile(
      path.join(repairDir, `slot_${pad2(slot.slot)}_${templateId}.repair_prompt.md`),
      `# Repair Prompt Placeholder\n\nStatus: pending visual review for slot ${slot.slot} (${slot.role}).\n`,
    );

    selectedSuite.slots.push(slotMetadata);
    templateSelection.push({
      slot: slot.slot,
      role: slot.role,
      selected_template: templateId,
      reason: `Default template for ${slot.role}; buyer question: ${slot.buyer_question}`,
      alternatives: (slot.default_template_cards ?? []).filter((id) => id !== templateId),
    });
  }

  await writeFile(path.join(outDir, 'suite_plan.selected.json'), `${JSON.stringify(selectedSuite, null, 2)}\n`);
  await writeFile(path.join(outDir, 'template_selection.json'), `${JSON.stringify(templateSelection, null, 2)}\n`);

  const reviewLog = `# Human Review Log

SKU: ${selectedSuite.sku}
Marketplace: ${marketplace}
Status: generation requests prepared

## Review Instructions

For each generated image, review:

- product fidelity
- selling point accuracy
- marketplace fit
- thumbnail readability
- text safety
- PSD/overlay need

Write accepted changes back as next-run constraints. Do not rely on memory-only feedback.
`;

  await writeFile(path.join(outDir, 'review_log.md'), reviewLog);

  const report = `# Ecommerce Suite Run

SKU: ${selectedSuite.sku}
Marketplace: ${marketplace}
Slots prepared: ${selectedSlots.length}

## Outputs

${selectedSuite.slots
  .map(
    (slot) =>
      `- Slot ${slot.slot} ${slot.role}: \`${slot.output_dir}/compiled_prompt.md\` using \`${slot.template_id}\``,
  )
  .join('\n')}

## Status

This run prepared prompts and generation request JSON files. It did not call an
image model.

Next step: feed each \`generation_request.json\` plus product/reference images
into the selected image model, then fill \`scorecards/*.score.json\`.
`;

  await writeFile(path.join(outDir, 'run_report.md'), report);
  console.log(`Prepared ${selectedSlots.length} ecommerce image slots in ${outDir}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
