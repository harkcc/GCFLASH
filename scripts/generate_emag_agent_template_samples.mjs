import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = '/Users/cc/Desktop/photo_show/output/emag_html_detail_agent_v1_2_test_runs';

const sharedCss = `
  <div style="font-family:Arial,Helvetica,sans-serif;color:#1f2937;line-height:1.55;">
`;

const closeCss = `
  </div>
`;

function esc(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}

function banner(src, alt) {
  return `<p style="text-align:center;margin:0 0 24px;"><img src="${src}" width="1140" alt="${esc(alt)}"></p>`;
}

function imageNeed(title, rows) {
  const body = rows
    .map((row) => `<li style="margin:6px 0;">${esc(row)}</li>`)
    .join('');
  return `
<div style="border:2px dashed #94a3b8;background:#f8fafc;padding:18px;margin:22px 0;">
  <h3 style="margin:0 0 10px;color:#0f172a;">PRODUCT IMAGE SLOT - ${esc(title)}</h3>
  <p style="margin:0 0 8px;"><strong>Next image-agent requirement:</strong></p>
  <ul style="margin:0;padding-left:20px;">${body}</ul>
</div>`;
}

function proofBand(items) {
  const cells = items
    .map(
      (item) =>
        `<td style="padding:16px;vertical-align:top;border:1px solid #dbe4de;"><strong>${esc(
          item.title,
        )}</strong><br>${esc(item.text)}</td>`,
    )
    .join('');
  return `<table style="width:100%;border-collapse:collapse;background:#eef7f0;margin:18px 0;"><tbody><tr>${cells}</tr></tbody></table>`;
}

function specsTable(rows) {
  return `<table style="width:100%;border-collapse:collapse;margin:18px 0;"><tbody>${rows
    .map(
      ([key, value]) =>
        `<tr><th style="text-align:left;padding:10px;background:#f3f4f6;border:1px solid #e5e7eb;">${esc(
          key,
        )}</th><td style="padding:10px;border:1px solid #e5e7eb;">${esc(value)}</td></tr>`,
    )
    .join('')}</tbody></table>`;
}

function faq(items) {
  return `<h2>FAQ</h2>${items
    .map(
      (item) =>
        `<p><strong>${esc(item.q)}</strong><br>${esc(item.a)}</p>`,
    )
    .join('')}`;
}

const cases = [
  {
    id: '01_technical_ev_charger',
    title: 'EV smart charger technical template',
    productType: 'technical_electronics',
    banner: '../../emag_banner_generation_tests/02_ev_charger_product_tech_rendered_1140x326.png',
    chain:
      'product_tech_hero -> result_summary -> compatibility_safety -> feature_proof_band -> specs_table -> usage_steps -> faq -> trust_closer',
    html: `${sharedCss}
${banner('../../emag_banner_generation_tests/02_ev_charger_product_tech_rendered_1140x326.png', 'EV charger technical hero banner')}
<h2>Charge at home with a setup that feels clear before you buy</h2>
<p>Use this layout when the buyer needs proof first: power, control method, protection rating, and fit with their parking or garage condition.</p>
${proofBand([
  { title: '11 kW power cue', text: 'Place this as the first rational anchor when power appears in product facts.' },
  { title: 'WiFi / RFID control', text: 'Translate control into everyday confidence for shared or private parking.' },
  { title: 'IP65 protection cue', text: 'Use as a fit signal, not as an installation promise.' },
])}
${imageNeed('EV charger product cutout + connector close-up', [
  'Transparent or clean-background product cutout, charger front visible, cable and connector visible.',
  'One close-up crop showing socket/connector pins and display/control area.',
  'No text rendered by image model; leave empty space for deterministic labels.',
  'Lighting: technical, clean, navy/gray background compatibility with the current banner.',
])}
<h2>Check technical fit before comparing price</h2>
${specsTable([
  ['Power', '11 kW'],
  ['Control', 'WiFi, RFID'],
  ['Protection', 'IP65'],
  ['Best use scene', 'Home garage or private parking after buyer verifies installation condition'],
])}
${faq([
  { q: 'What should the buyer confirm first?', a: 'Power, connector, installation environment, and control method should be confirmed before purchase.' },
  { q: 'Can this page mention seller promises?', a: 'Only if those promises are provided as evidence in the product input.' },
])}
${closeCss}`,
  },
  {
    id: '02_home_cleaning_vacuum',
    title: 'Home cleaning pain-scene template',
    productType: 'home_cleaning',
    banner: '../../emag_banner_generation_tests/03_official_people_category_style_rendered_1140x456.png',
    chain:
      'pain_scene_banner -> result_summary -> feature_benefit_stack -> visual_usage -> specs_table -> faq -> trust_closer',
    html: `${sharedCss}
${banner('../../emag_banner_generation_tests/03_official_people_category_style_rendered_1140x456.png', 'Home cleaning lifestyle banner')}
<h2>Clean the small mess before it becomes a full cleaning session</h2>
<p>This template starts from the buyer's tired scene: crumbs in the car, dust around the sofa, pet hair on fabric, and small corners that feel annoying to clean.</p>
${imageNeed('Handheld vacuum in real home and car scenes', [
  'Show product in hand, scale obvious, nozzle pointed at sofa seam or car seat corner.',
  'Create two scene crops: home sofa dust/pet hair and car interior crumbs.',
  'Product body must stay accurate enough for later SKU matching; no fake buttons or labels.',
  'Mood: practical, clean, daylight, not luxury beauty style.',
])}
${proofBand([
  { title: 'Small mess response', text: 'Position the product as quick access for local cleaning, not whole-house replacement.' },
  { title: 'Accessory logic', text: 'Show each nozzle solving a different surface or corner.' },
  { title: 'Maintenance cue', text: 'Use washable filter or dust-bin facts only if present in ProductTruthPack.' },
])}
${specsTable([
  ['Product type', 'Cordless handheld vacuum'],
  ['Core scenes', 'Car interior, sofa, desk, narrow corners'],
  ['Needed product facts', 'Suction, battery, dust-bin capacity, included nozzles'],
])}
${faq([
  { q: 'Is it for deep full-home cleaning?', a: 'Frame it as a convenient small-mess tool unless the specs prove whole-room performance.' },
  { q: 'What product photos are most important?', a: 'Hand scale, nozzle set, dust-bin/filter access, and one real-use scene.' },
])}
${closeCss}`,
  },
  {
    id: '03_beauty_personal_care',
    title: 'Beauty and personal care emotional-result template',
    productType: 'beauty_personal_care',
    banner: '../../emag_banner_generation_tests/03_official_people_category_style_rendered_1140x456.png',
    chain: 'people_category_banner -> emotional_result -> safety_comfort -> feature_proof -> faq -> trust_closer',
    html: `${sharedCss}
${banner('../../emag_banner_generation_tests/03_official_people_category_style_rendered_1140x456.png', 'Beauty personal care people banner')}
<h2>Make the routine feel calmer, cleaner, and easier to repeat</h2>
<p>Use this template when the purchase is driven by comfort and self-care feeling, then immediately support that emotion with safety, material, or skin-contact evidence.</p>
${imageNeed('Personal care device with model-use close-up', [
  'Show a calm model using the device naturally; face or hand visible depending on product.',
  'Include a clean product-only close-up showing texture, head/nozzle/surface, and scale.',
  'No medical-result visuals, no impossible before/after claims, no text in image.',
  'Color mood: soft white, light blue, or gentle rose with enough contrast for Romanian overlay text later.',
])}
${proofBand([
  { title: 'Comfort first', text: 'Open with how the routine feels, not with a dry spec list.' },
  { title: 'Safety evidence', text: 'Only mention skin-safe material, temperature, or certification when provided.' },
  { title: 'Repeatable routine', text: 'Explain cleaning, charging, or use steps so the product feels easy to keep using.' },
])}
${faq([
  { q: 'Can we use before/after skin claims?', a: 'Only with real evidence; otherwise keep the result emotional and routine-based.' },
  { q: 'What images should come after the banner?', a: 'Model use, product texture close-up, cleaning or storage detail.' },
])}
${closeCss}`,
  },
  {
    id: '04_baby_safety_soft',
    title: 'Baby safety-first template',
    productType: 'baby',
    banner: '../../emag_banner_generation_tests/03_official_people_category_style_rendered_1140x456.png',
    chain: 'soft_people_banner -> safety_first -> usage_scene -> feature_benefit -> specs -> faq -> trust_closer',
    html: `${sharedCss}
${banner('../../emag_banner_generation_tests/03_official_people_category_style_rendered_1140x456.png', 'Soft baby category banner')}
<h2>Start with reassurance before showing features</h2>
<p>For baby products, the page should first reduce parent worry: material, softness, size fit, cleaning, and daily-use safety cues must come before decorative selling points.</p>
${imageNeed('Baby product safety and softness scene', [
  'Show product near baby-care environment but avoid risky sleeping or unsafe-use staging.',
  'Include parent hand for scale and a material/edge close-up.',
  'Use soft daylight, clean nursery tones, no text, no official marketplace marks.',
  'Image must make softness and safe handling visible; avoid exaggerated toy-like colors unless product requires it.',
])}
${proofBand([
  { title: 'Material cue', text: 'Put material and surface facts first when available.' },
  { title: 'Daily-use scene', text: 'Show how the parent handles, cleans, stores, or carries the product.' },
  { title: 'Fit cue', text: 'Use size, age range, or capacity only when it exists in product facts.' },
])}
${specsTable([
  ['Product type', 'Baby care accessory'],
  ['Needed facts', 'Material, size, cleaning method, package contents'],
  ['Copy stance', 'Reassuring, specific, no unsupported safety certification'],
])}
${faq([
  { q: 'What should not be claimed?', a: 'Do not claim certification, age fit, or safety outcome unless provided as evidence.' },
  { q: 'What product image is most valuable?', a: 'A parent-hand scale photo plus a close-up of material and edges.' },
])}
${closeCss}`,
  },
  {
    id: '05_coffee_kitchen_lifestyle',
    title: 'Coffee kitchen lifestyle-result template',
    productType: 'coffee_kitchen',
    banner: '../../emag_banner_generation_tests/04_ai_brand_trust_background_overlay_rendered_1140x456.png',
    chain: 'lifestyle_result_banner -> taste_convenience_scene -> feature_proof -> usage_steps -> specs -> faq',
    html: `${sharedCss}
${banner('../../emag_banner_generation_tests/04_ai_brand_trust_background_overlay_rendered_1140x456.png', 'Kitchen lifestyle result banner')}
<h2>Turn the routine into a result the buyer can imagine using every morning</h2>
<p>Kitchen and coffee pages should sell the resulting moment first: speed, taste consistency, less mess, and a routine that feels easy to repeat.</p>
${imageNeed('Coffee/kitchen product use sequence', [
  'Show product on kitchen counter with ingredients or coffee cup nearby.',
  'Generate three product detail crops: control area, output/result, cleaning or detachable part.',
  'No fake steam overload, no unproven taste claim, no text in image.',
  'Warm but not beige-only palette; product must remain the visual center.',
])}
${proofBand([
  { title: 'Convenience cue', text: 'Show the step that saves time or reduces mess.' },
  { title: 'Result cue', text: 'Show the cup, foam, texture, or prepared food only if it matches product function.' },
  { title: 'Cleaning cue', text: 'A detachable or washable component image often reduces buyer friction.' },
])}
${specsTable([
  ['Product type', 'Kitchen or coffee appliance'],
  ['Needed facts', 'Capacity, power, modes, material, removable parts'],
  ['Best image module', 'Lifestyle result plus close-up proof details'],
])}
${faq([
  { q: 'Should copy focus on specs first?', a: 'No, lead with routine result, then use specs to make the result believable.' },
  { q: 'What image should follow the banner?', a: 'A use sequence showing input, product action, result, and cleaning detail.' },
])}
${closeCss}`,
  },
  {
    id: '06_store_brand_trust',
    title: 'Store and brand trust template',
    productType: 'store_brand_trust',
    banner: '../../emag_banner_generation_tests/01_brand_trust_dark_package_rendered_1140x456.png',
    chain: 'brand_trust_banner -> seller_service_band -> product_range_familiarity -> buyer_objection_faq -> closing_confidence',
    html: `${sharedCss}
${banner('../../emag_banner_generation_tests/01_brand_trust_dark_package_rendered_1140x456.png', 'Dark brand trust banner')}
<h2>Make an unfamiliar seller feel organized before the buyer judges one product</h2>
<p>This page type is not just a repeated logo. It builds familiarity through people, packaging, product range, and a calm explanation of how the buyer can verify service facts.</p>
${imageNeed('Brand product family and packaging proof images', [
  'Create a clean product family lineup: 4 to 6 representative SKUs, same lighting and perspective.',
  'Create one package/boxing scene with a real person holding or opening the box; no official marketplace logo unless owned/allowed.',
  'Create one support/process visual using neutral icons only; text will be overlaid later.',
  'Mood: premium dark or clean white depending on brand palette; avoid fake service promises inside the image.',
])}
${proofBand([
  { title: 'Product range familiarity', text: 'Show that the seller has a coherent range, not a random one-item page.' },
  { title: 'Packaging signal', text: 'Packaging and handling visuals make the purchase feel less anonymous.' },
  { title: 'Verification cue', text: 'Tell the buyer which live listing facts to check instead of inventing platform promises.' },
])}
${faq([
  { q: 'Can this module state seller service terms?', a: 'Only when those terms are supplied as verified listing facts.' },
  { q: 'What image should the next agent generate?', a: 'Product family, package moment, and neutral service-process icons that do not contain unsupported text.' },
])}
${closeCss}`,
  },
];

function modulePlan(item) {
  const modules = item.chain.split(' -> ').map((moduleId, index, arr) => ({
    module_id: moduleId,
    buyer_question:
      index === 0
        ? 'What result or trust signal do I see first?'
        : `What does ${moduleId} answer for the buyer?`,
    purpose: `Template sample module for ${item.productType}: ${moduleId}.`,
    comes_after: index === 0 ? 'start' : arr[index - 1],
    sets_up_next: index === arr.length - 1 ? 'end' : arr[index + 1],
    required_evidence: ['ProductTruthPack facts or explicitly inferred angle'],
    html_component: index === 0 ? 'component_centered_1140_image' : 'text_table_or_product_image_slot',
    asset_slots: index === 0 ? ['banner'] : ['product_image_if_needed'],
    failure_mode: 'Downgrade unsupported claims to neutral buyer guidance.',
  }));
  return {
    product_type: item.productType,
    template_chain: item.chain,
    modules,
  };
}

function mediaIndex(item) {
  return {
    assets: [
      {
        asset_id: `${item.id}_banner`,
        asset_type: 'generated_banner',
        local_path: item.banner,
        dimensions: item.banner.includes('326') ? '1140x326' : '1140x456',
        usage_rights: 'owned_or_generated',
        allowed_use: ['production-after-review'],
      },
    ],
  };
}

const cards = [];
for (const item of cases) {
  const dir = join(root, item.id);
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, 'detail.html'), item.html, 'utf8');
  writeFileSync(join(dir, 'module_plan.json'), `${JSON.stringify(modulePlan(item), null, 2)}\n`, 'utf8');
  writeFileSync(join(dir, 'media_asset_index.json'), `${JSON.stringify(mediaIndex(item), null, 2)}\n`, 'utf8');
  writeFileSync(
    join(dir, 'product_image_requirements.md'),
    `# ${item.title}\n\nProduct type: ${item.productType}\n\nBanner is already inserted in detail.html.\n\nProduct image slots are written inside the HTML as next-step image-agent requirements.\n`,
    'utf8',
  );
  cards.push(`<li><a href="./${item.id}/detail.html">${esc(item.id)} - ${esc(item.title)}</a></li>`);
}

writeFileSync(
  join(root, 'index.html'),
  `<div style="font-family:Arial,Helvetica,sans-serif;padding:24px;"><h1>eMAG HTML Detail Agent v1.2 Template Samples</h1><p>Banner images are inserted. Product images are intentionally represented as requirement slots for the next image-generation agent.</p><ul>${cards.join('')}</ul></div>`,
  'utf8',
);

console.log(`Generated ${cases.length} eMAG template samples in ${root}`);
