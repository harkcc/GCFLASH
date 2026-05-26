#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

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

async function readText(file) {
  return readFile(file, 'utf8');
}

function bullet(items, fallback = '- not specified') {
  if (!items || items.length === 0) return fallback;
  return items.map((item) => `- ${item}`).join('\n');
}

function zoneLines(template) {
  const lines = [];
  for (const zone of template.text_zones ?? []) {
    lines.push(`- Text zone ${zone.id}: ${zone.position}; ${zone.policy}`);
  }
  for (const zone of template.badge_zones ?? []) {
    lines.push(`- Badge zone ${zone.id}: ${zone.position}; ${zone.content}`);
  }
  for (const zone of template.scene_zones ?? []) {
    lines.push(`- Scene zone ${zone.id}: ${zone.position}; ${zone.role}`);
  }
  return lines.join('\n');
}

function normalizeTruth(raw, sku) {
  if (raw.immutable_traits && raw.selling_points) return raw;

  const immutable = [
    ...(raw.required_preservation_rules ?? []),
    ...(raw.visible_materials ?? []).map((v) => `visible material: ${v}`),
    ...(raw.visible_parts ?? []).map((v) => `visible part: ${v}`),
    ...(raw.visible_color ?? []).map((v) => `visible color: ${v}`),
  ];

  const sellingPoints = (raw.allowed_selling_points ?? raw.confirmed_features ?? []).map(
    (claim, index) => ({
      id: `sp_${index + 1}`,
      claim,
      visual_translation: claim,
      short_badge: claim.length <= 18 ? claim : claim.split(/\s+/).slice(0, 3).join(' '),
    }),
  );

  return {
    sku: sku ?? raw.product_name ?? 'unknown_sku',
    category: raw.visible_product_type ?? raw.category ?? 'unknown category',
    marketplace: raw.marketplace ?? 'Amazon',
    language: raw.language ?? 'English',
    source_images: raw.source_images ?? {},
    immutable_traits: immutable,
    allowed_changes: raw.allowed_changes ?? ['background', 'lighting', 'scene', 'composition', 'badge placement'],
    forbidden_changes: [...(raw.forbidden_claims ?? []), ...(raw.risky_details ?? [])],
    selling_points: sellingPoints,
    text_copy: raw.text_copy ?? {},
  };
}

function textPolicyInstruction(template, override) {
  const policy = override ?? template.text_policy ?? 'reserve_text_zone or overlay_later';
  if (/overlay/i.test(policy) || /reserve/i.test(policy)) {
    return `${policy}. Leave clean, high-contrast safe areas for deterministic PSD/HTML/Pillow text overlay. Do not render long final copy inside the image.`;
  }
  if (/no_text/i.test(policy)) return 'No final text. Use only visual evidence, icons, and empty safe areas.';
  return `${policy}. Render only exact short approved words or numbers. Do not invent copy.`;
}

function buildTextCopyPlan(truth, template, textPolicy) {
  const policy = textPolicy ?? template.text_policy ?? 'deterministic_overlay';
  const overlayRequired = /overlay|reserve|deterministic/i.test(policy);
  const sellingPoints = truth.selling_points ?? [];
  const slots = [];

  const headline =
    truth.text_copy?.headline ??
    `${truth.category}`;
  if (!/no_text/i.test(policy)) {
    slots.push({
      id: 'headline',
      role: 'headline',
      copy: headline,
      source: truth.text_copy?.headline ? 'user_approved' : 'generated_draft',
      placement: template.text_zones?.[0]?.position ?? 'primary safe area',
      priority: 'primary',
      max_lines: 2,
      max_chars: 32,
      style: {
        font_weight: '700-800',
        case: 'title_or_sentence',
        color_role: 'fg',
        background_role: 'none_or_surface',
      },
      translation_required: truth.language && truth.language !== 'English',
      overlay_required: overlayRequired,
      locked: Boolean(truth.text_copy?.headline),
    });
  }

  for (const [index, point] of sellingPoints.slice(0, 3).entries()) {
    slots.push({
      id: `badge_${index + 1}`,
      role: index === 0 ? 'badge' : 'callout',
      copy: point.short_badge ?? point.claim,
      source: point.proof ? 'listing' : 'generated_draft',
      placement: template.badge_zones?.[index]?.position ?? template.text_zones?.[1]?.position ?? 'secondary safe area',
      priority: index === 0 ? 'secondary' : 'tertiary',
      max_lines: 1,
      max_chars: 18,
      style: {
        font_weight: '700',
        case: 'short_label',
        color_role: index === 0 ? 'accent' : 'fg',
        background_role: 'surface_or_badge',
      },
      translation_required: truth.language && truth.language !== 'English',
      overlay_required: overlayRequired,
      locked: Boolean(point.proof),
    });
  }

  return {
    sku: truth.sku,
    marketplace: truth.marketplace,
    language: truth.language ?? 'English',
    text_policy: /no_text/i.test(policy) ? 'no_text' : overlayRequired ? 'deterministic_overlay' : 'model_exact_text',
    font_system: {
      primary_font: 'neutral geometric sans',
      display_font: 'bold geometric sans',
      number_font: 'tabular bold sans',
      fallback_font: 'system sans',
    },
    slots,
    forbidden_text: truth.forbidden_changes ?? [],
    notes:
      'Seed copy plan for overlay/PSD stage. Generated draft copy must be reviewed against product truth before production use.',
  };
}

function styleFromDesign(designText) {
  const palette = [];
  const paletteRegex = /`--([^`]+)`: `([^`]+)`/g;
  let match;
  while ((match = paletteRegex.exec(designText)) && palette.length < 12) {
    palette.push(`${match[1]} ${match[2]}`);
  }
  return {
    palette: palette.join(', ') || 'use the active ecommerce design system palette',
    lighting: 'commercial product lighting, clear shadows, product-first readability',
    background: 'marketplace-ready clean background adapted to the selected template',
    typography: 'neutral geometric ecommerce typography; final copy should be overlaid when accuracy matters',
  };
}

async function main() {
  const root = process.cwd();
  const truthFile = requireArg('truth');
  const templateFile = requireArg('template');
  const outDir = requireArg('out');
  const recipeFile = arg('recipe', path.join(root, 'workflow/prompt_recipes/reference_img2img_base.md'));
  const designFile = arg('design', path.join(root, 'workflow/design_systems/ecommerce_european_premium.DESIGN.md'));
  const sku = arg('sku');
  const marketplace = arg('marketplace');
  const textPolicy = arg('text-policy');

  const truth = normalizeTruth(await readJson(truthFile), sku);
  if (marketplace) truth.marketplace = marketplace;
  const template = await readJson(templateFile);
  const recipe = await readText(recipeFile);
  const design = await readText(designFile);
  const style = styleFromDesign(design);
  const textCopyPlan = buildTextCopyPlan(truth, template, textPolicy);

  const sellingPointsVisualized = (truth.selling_points ?? [])
    .map((sp) => `- ${sp.claim}: ${sp.visual_translation}${sp.proof ? ` (proof: ${sp.proof})` : ''}`)
    .join('\n');

  const compiled = `# Compiled Ecommerce Image Prompt

## Inputs

- SKU: ${truth.sku}
- Category: ${truth.category}
- Marketplace: ${truth.marketplace}
- TemplateCard: ${template.template_id}
- Image role: ${template.image_role}

## Model Prompt

TASK
Create a marketplace-ready ecommerce image for ${truth.marketplace}. The image role is ${template.image_role}: ${template.business_goal}.

REFERENCE ROLES
- Product image: source of truth for the product.
- Visual template image: composition, visual hierarchy, color mood, lighting direction, and commercial layout reference only.
- Brand reference, if provided: extract palette, frame geometry, badge style, and safe areas only.

KEEP FROM PRODUCT IMAGE
Keep the exact product identity:
${bullet(truth.immutable_traits)}

KEEP FROM TEMPLATE
Keep this commercial logic:
- Buyer question: ${template.viewer_question}
- Layout pattern: ${template.layout_pattern}
- Product hierarchy: product first, then proof/badge, then scene/detail support.

CHANGE / ADAPT
Replace the template product with this product category: ${truth.category}.
Adapt all visual metaphors and scene details to these selling points:
${sellingPointsVisualized || '- no approved selling points supplied; use generic product clarity only'}

LAYOUT
${zoneLines(template)}
Product should be visually dominant: ${template.product_weight}.
Use 1-3 focus points only. Avoid visual clutter.

TEXT POLICY
${textPolicyInstruction(template, textPolicy)}

TEXT COPY PLAN
Use the generated text copy seed file for final overlay planning: text_copy_plan.seed.json.
Do not invent additional claims beyond the ProductTruthPack. If final typography matters, leave clean empty zones and apply text later with PSD/HTML/Pillow.

STYLE
- Template color style: ${template.color_style}
- Palette: ${style.palette}
- Lighting: ${style.lighting}
- Background: ${style.background}
- Typography mood: ${style.typography}

NEGATIVE CONSTRAINTS
${bullet([...(template.negative_constraints ?? []), ...(truth.forbidden_changes ?? [])])}

OUTPUT
Sharp, commercial, marketplace-ready image with clear product recognition and high conversion visual structure.

## Source Recipe Notes

${recipe}
`;

  const request = {
    sku: truth.sku,
    marketplace: truth.marketplace,
    template_id: template.template_id,
    image_role: template.image_role,
    product_truth_pack: truth,
    template_card: template,
    text_policy: textPolicy ?? template.text_policy,
    text_copy_plan_file: 'text_copy_plan.seed.json',
    prompt_file: 'compiled_prompt.md',
    references_expected: {
      product_image: 'required',
      visual_template_image: 'optional but recommended',
      brand_reference: 'optional',
    },
    generation_status: 'request_prepared',
  };

  await mkdir(outDir, { recursive: true });
  await writeFile(path.join(outDir, 'product_truth_pack.normalized.json'), `${JSON.stringify(truth, null, 2)}\n`);
  await writeFile(path.join(outDir, 'text_copy_plan.seed.json'), `${JSON.stringify(textCopyPlan, null, 2)}\n`);
  await writeFile(path.join(outDir, 'compiled_prompt.md'), compiled);
  await writeFile(path.join(outDir, 'generation_request.json'), `${JSON.stringify(request, null, 2)}\n`);
  console.log(`Wrote ${path.join(outDir, 'compiled_prompt.md')}`);
  console.log(`Wrote ${path.join(outDir, 'generation_request.json')}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
