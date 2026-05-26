import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = '/Users/cc/Desktop/photo_show/output/emag_html_detail_agent_v1_2_rich_mobile';
const validatorNote =
  'The image-agent must generate this asset in the next step. Keep text out of the generated bitmap unless the overlay pipeline supplies it.';

function esc(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}

function page(content) {
  return `<div style="font-family:Arial,Helvetica,sans-serif;color:#24292f;line-height:1.6;max-width:1140px;margin:0 auto;padding:0 8px;font-size:16px;">${content}</div>`;
}

function h2(text) {
  return `<h2 style="color:#333;font-size:20px;line-height:1.25;margin:28px 0 14px 0;font-weight:500;letter-spacing:0;">${esc(
    text,
  )}</h2>`;
}

function img(src, alt, extra = '') {
  return `<p style="text-align:center;margin:0 0 20px 0;"><img src="${src}" width="1140" alt="${esc(
    alt,
  )}" style="max-width:100%;height:auto;${extra}"></p>`;
}

function anchorFlow(items) {
  return `<div style="margin:18px 0;background:#f8fafc;border:1px solid #e2e8f0;padding:12px;">${items
    .map(
      (item, index) =>
        `<div style="margin:8px 0;padding:10px 12px;border-left:4px solid ${item.color};background:#fff;"><span style="display:inline-block;width:34px;height:24px;line-height:24px;text-align:center;background:${item.color};color:#fff;font-weight:bold;margin-right:8px;">${String(
          index + 1,
        ).padStart(2, '0')}</span><strong>${esc(item.title)}</strong><br><span style="margin-left:46px;">${esc(
          item.text,
        )}</span></div>`,
    )
    .join('')}</div>`;
}

function slot(kind, title, requirements, why) {
  return `<div style="border:2px dashed #7aa2d6;background:#f8fbff;padding:16px;margin:22px 0;">
  <h3 style="margin:0 0 8px;color:#102033;font-size:17px;">${esc(kind)} - ${esc(title)}</h3>
  <p style="margin:0 0 8px;"><strong>Purpose:</strong> ${esc(why)}</p>
  <p style="margin:0 0 8px;"><strong>Next image-agent requirement:</strong> ${esc(validatorNote)}</p>
  <ul style="margin:0;padding-left:20px;">${requirements
    .map((item) => `<li style="margin:5px 0;">${esc(item)}</li>`)
    .join('')}</ul>
</div>`;
}

function band(title, rows, bg = '#e8f5e8') {
  return `<div style="background:${bg};padding:18px;margin:20px 0;">${title ? `<h3 style="margin:0 0 12px;font-size:17px;color:#1f2937;">${esc(title)}</h3>` : ''}${rows
    .map(
      (row) =>
        `<p style="margin:8px 0;"><strong>- ${esc(row.title)}</strong> - ${esc(row.text)}</p>`,
    )
    .join('')}</div>`;
}

function specTable(rows) {
  return `<table style="width:100%;border-collapse:collapse;margin:18px 0;font-size:15px;table-layout:fixed;"><tbody>${rows
    .map(
      ([key, value], index) =>
        `<tr style="background:${index % 2 === 0 ? '#f7f7f7' : '#fff'};"><td style="padding:10px;border:1px solid #ddd;font-weight:bold;width:38%;vertical-align:top;">${esc(
          key,
        )}</td><td style="padding:10px;border:1px solid #ddd;vertical-align:top;word-break:break-word;">${esc(
          value,
        )}</td></tr>`,
    )
    .join('')}</tbody></table>`;
}

function faq(items) {
  return `${h2('INTREBARI FRECVENTE')}${items
    .map(
      (item, index) =>
        `<p style="margin:12px 0;"><strong>${index + 1}. ${esc(item.q)}</strong><br>${esc(
          item.a,
        )}</p>`,
    )
    .join('')}`;
}

function cta(title, text) {
  return `<div style="background:#000;padding:18px;margin:24px 0;text-align:center;border:5px solid #f4c300;">
  <p style="font-size:17px;font-weight:bold;color:#fff;margin:8px 0;">${esc(title)}</p>
  <p style="font-size:16px;color:#fff;margin:8px 0;">${esc(text)}</p>
</div>`;
}

const cases = [
  {
    id: '01_technical_ev_charger_rich',
    title: 'Technical EV charger rich mobile template',
    product_type: 'technical_electronics',
    chain:
      'product_tech_hero -> buyer_anchor_flow -> product_proof_slots -> feature_band -> specs_table -> setup_steps -> faq -> motion_trust -> closing_confidence',
    html: page(`
${img('../../emag_banner_generation_tests/02_ev_charger_product_tech_rendered_1140x326.png', 'EV charger technical hero')}
${anchorFlow([
  { color: '#0ea5e9', title: 'Mai intai: potrivire tehnica', text: 'Putere, control si protectie trebuie intelese in primele secunde.' },
  { color: '#14b8a6', title: 'Apoi: dovezi vizuale', text: 'Produsul, conectorul si mediul de utilizare trebuie vazute, nu doar descrise.' },
  { color: '#6366f1', title: 'La final: verificare rationala', text: 'Tabelul de specificatii confirma daca produsul se potriveste situatiei cumparatorului.' },
])}
${h2('REZULTATUL PE CARE IL CUMPERI')}
<p>Un incarcator EV tehnic nu trebuie vandut ca un simplu accesoriu. Pagina trebuie sa arate ca produsul transforma parcarea sau garajul intr-un punct de incarcare mai usor de controlat.</p>
${slot('PRODUCT IMAGE SLOT', 'Product cutout + connector proof board', [
  'Canvas 1140x705. Center: charger front cutout, display and cable visible.',
  'Right detail crop: connector pins and plug head, sharp commercial lighting.',
  'Left bottom: small non-text icon areas for power, control, protection; no generated words.',
  'Background must match navy/purple technical banner, but keep product brighter than background.',
], 'This board turns abstract specs into visible product proof.')}
${band('PRINCIPALELE BENEFICII SI CARACTERISTICI', [
  { title: 'Control clar al sesiunii', text: 'WiFi si RFID trebuie explicate ca elemente de control, nu ca decor tehnic.' },
  { title: 'Protectie pentru mediu de utilizare', text: 'IP65 poate sustine ideea de utilizare in garaj sau zona protejata, fara promisiuni de instalare.' },
  { title: 'Verificare inainte de cumparare', text: 'Puterea, conectorul si mediul electric trebuie confirmate inainte de decizie.' },
  { title: 'Mai putine intrebari dupa banner', text: 'Primele module raspund la ce este, unde se foloseste si ce trebuie verificat.' },
])}
${slot('DETAIL IMAGE SLOT', 'Installation-condition checklist image', [
  'Canvas 1140x684. Show clean garage wall, EV parked, cable route, power box area as visual placeholders.',
  'Do not show unsafe DIY wiring. Avoid certification badges unless provided.',
  'Add empty small callout zones for deterministic overlay: power source, cable path, vehicle position.',
], 'This gives the buyer a concrete mental model for fit and setup.')}
${h2('SPECIFICATII TEHNICE COMPLETE')}
${specTable([
  ['Putere', '11 kW'],
  ['Control', 'WiFi, RFID'],
  ['Protectie', 'IP65'],
  ['Scenariu potrivit', 'Garaj, parcare privata, spatiu unde instalarea poate fi verificata'],
  ['De verificat', 'Compatibilitate conector, alimentare electrica, montaj si conditii locale'],
])}
${band('UTILIZARE POSIBILA', [
  { title: 'Garaj acasa', text: 'Pagina trebuie sa arate clar unde sta produsul si cum ajunge cablul la vehicul.' },
  { title: 'Parcare privata', text: 'Controlul RFID poate fi prezentat ca filtru de acces doar daca produsul il include.' },
  { title: 'Flota mica sau spatiu comun', text: 'Se poate folosi ca scenariu de control, dar fara promisiuni operationale nefondate.' },
], '#f8f9fa')}
${faq([
  { q: 'Ce trebuie confirmat inainte de achizitie?', a: 'Puterea, conectorul, mediul de montaj si modul de control trebuie verificate in faptele produsului.' },
  { q: 'De ce nu punem tabelul primul?', a: 'Cumparatorul are nevoie intai sa inteleaga rezultatul si contextul, apoi sa confirme specificatiile.' },
])}
${img('./assets/brand_trust_motion_demo.gif', 'Brand motion trust GIF')}
${cta('Incarcare EV cu o prezentare tehnica usor de verificat', 'Pagina combina impactul vizual, dovezile de produs si confirmarile rationale intr-un flux mobil coerent.')}`),
  },
  {
    id: '02_home_cleaning_vacuum_rich',
    title: 'Home cleaning handheld vacuum rich mobile template',
    product_type: 'home_cleaning',
    chain:
      'pain_scene_banner -> result_summary -> detail_proof_images -> color_band_feature_stack -> specs_table -> usage_scenes -> package_content -> faq -> question_board -> closing_confidence',
    html: page(`
${img('./assets/brand_trust_motion_demo.gif', 'Animated dark brand banner for cleaning product')}
${h2('CURATA MIZERIA MICA FARA SA PORNESTI O SESIUNE MARE DE CURATENIE')}
<p>Acest tip de pagina trebuie sa inceapa cu situatia pe care cumparatorul o recunoaste imediat: firimituri in masina, praf langa canapea, par pe material textil si spatii unde un aspirator mare este prea incomod.</p>
${anchorFlow([
  { color: '#16a34a', title: 'Scena dureroasa', text: 'Masina, canapea, birou, colturi inguste.' },
  { color: '#2563eb', title: 'Dovada produsului', text: 'Aspirator in mana, duze, filtru, recipient.' },
  { color: '#f59e0b', title: 'Confirmare finala', text: 'Putere, baterie, greutate, accesorii, intretinere.' },
])}
${slot('PRODUCT IMAGE SLOT', 'Hand scale + car/sofa cleaning scene board', [
  'Canvas 1140x705. Left: hand holding vacuum near car seat crumbs. Right: sofa seam dust/pet hair scene.',
  'Center: product cutout, nozzle connected, scale obvious.',
  'Add small empty icon areas for suction, cordless, LED, washable filter.',
  'Mood practical and clean; no luxury background, no generated text.',
], 'This module replaces abstract feature copy with visible usage proof.')}
${band('PRINCIPALELE BENEFICII SI CARACTERISTICI', [
  { title: 'Putere de aspirare pentru murdarie locala', text: 'Mentioneaza valoarea exacta doar daca exista in ProductTruthPack.' },
  { title: 'Fara fir pentru masina si casa', text: 'Arata libertatea miscarii in spatii unde cablul ar incurca.' },
  { title: 'LED pentru zone intunecate', text: 'Conecteaza lumina cu zona de sub scaun sau coltul canapelei.' },
  { title: 'Filtru reutilizabil', text: 'Explica intretinerea numai daca filtrul lavabil este fapt confirmat.' },
  { title: 'Duze pentru suprafete diferite', text: 'Fiecare accesoriu trebuie legat de o scena, nu listat singur.' },
  { title: 'Greutate redusa', text: 'Greutatea conteaza pentru utilizarea cu o singura mana si curatarea rapida.' },
])}
${slot('DETAIL IMAGE SLOT', 'Accessory and nozzle purpose board', [
  'Canvas 1140x684. Show vacuum plus 4 accessory slots: brush nozzle, flat nozzle, hose, charging cable.',
  'Each accessory needs an empty label zone; final text overlay will map accessory -> surface.',
  'Use white or pale blue background so small accessories stay readable on mobile.',
], 'Accessory boards prevent the package section from becoming plain text.')}
${h2('SPECIFICATII TEHNICE COMPLETE')}
${specTable([
  ['Putere aspirare', '9500 Pa if confirmed by product facts'],
  ['Baterie', '2200 mAh if confirmed'],
  ['Autonomie', 'Pana la 30 min if confirmed'],
  ['Greutate', '545 g if confirmed'],
  ['Recipient praf', '0.4 L if confirmed'],
  ['Nivel zgomot', '50 dB if confirmed'],
])}
${band('UTILIZARE POSIBILA', [
  { title: 'Masina', text: 'Scaune, covorase, spatiu dintre consola si scaun.' },
  { title: 'Casa', text: 'Canapea, birou, sertar, colturi greu accesibile.' },
  { title: 'Animale de companie', text: 'Doar daca materialele si puterea sustin scenariul.' },
], '#f8f9fa')}
${band('PACHET COMPLET CONTINUT', [
  { title: 'Aspirator portabil', text: 'Produsul principal, fotografiat separat si in mana.' },
  { title: 'Duze de curatare', text: 'Fiecare duza trebuie aratata cu scena potrivita.' },
  { title: 'Cablu de incarcare', text: 'Arata portul si cablul doar daca sunt confirmate.' },
], '#eef6ff')}
${faq([
  { q: 'Este potrivit pentru curatare rapida in masina?', a: 'Da, daca imaginea si specificatiile confirma portabilitatea, duzele si autonomia.' },
  { q: 'Cum evitam textul generic?', a: 'Fiecare beneficiu trebuie legat de o scena concreta si de un detaliu vizual.' },
  { q: 'Ce imagine lipseste cel mai mult?', a: 'O placa de accesorii care arata clar ce face fiecare duza.' },
])}
${img('../../emag_detail_visual_boards/bestplaza_faq_question_board_v1_800.png', 'Buyer question flow board')}
${cta('Aspirator portabil pentru masina, casa si spatii inguste', 'Fluxul mobil raspunde intai la scena, apoi arata dovada, apoi confirma specificatiile.')}`),
  },
  {
    id: '03_beauty_personal_care_rich',
    title: 'Beauty personal care rich mobile template',
    product_type: 'beauty_personal_care',
    chain:
      'people_category_banner -> emotional_result -> safety_comfort -> routine_steps -> proof_images -> specs_table -> faq -> motion_trust -> closing_confidence',
    html: page(`
${img('../../emag_banner_generation_tests/03_official_people_category_style_rendered_1140x456.png', 'People category beauty banner')}
${h2('TRANSFORMA RUTINA INTR-UN MOMENT USOR DE REPETAT')}
<p>Pentru frumusete si ingrijire personala, prima promisiune trebuie sa fie senzatia si rutina: confort, control, curatare usoara, depozitare si folosire fara stres. Rezultatele medicale sau estetice puternice trebuie evitate daca nu exista dovada.</p>
${anchorFlow([
  { color: '#db2777', title: 'Emotie', text: 'Rutina mai calma si mai usoara.' },
  { color: '#7c3aed', title: 'Confort', text: 'Material, forma, contact cu pielea, curatare.' },
  { color: '#0891b2', title: 'Dovada', text: 'Moduri, baterie, accesorii, utilizare.' },
])}
${slot('PRODUCT IMAGE SLOT', 'Model-use + texture close-up board', [
  'Canvas 1140x705. Use a calm model using the device naturally; show only safe contact position.',
  'Add close-up crop of material/head/nozzle/LED surface depending on product.',
  'No before-after skin transformation. No medical claim. No generated text.',
  'Palette: soft white, light blue, gentle rose; product remains central.',
], 'Beauty products need emotional context, but the detail image must still prove comfort and structure.')}
${band('BENEFICII SI CARACTERISTICI', [
  { title: 'Confort in utilizare', text: 'Leaga forma produsului de modul in care se tine sau se aplica.' },
  { title: 'Material si contact', text: 'Materialul trebuie aratat in close-up, nu doar mentionat.' },
  { title: 'Moduri de functionare', text: 'Prezinta modurile ca optiuni de rutina, nu ca promisiuni exagerate.' },
  { title: 'Curatare si depozitare', text: 'Un modul vizual separat reduce teama de intretinere complicata.' },
])}
${slot('DETAIL IMAGE SLOT', 'Routine sequence board', [
  'Canvas 1140x684. Four panels: prepare, use, clean, store.',
  'Show hands and product scale; avoid excessive face retouching or impossible effects.',
  'Leave clean label zones for deterministic overlay: Step 1, Step 2, Step 3, Step 4.',
], 'A routine board makes the buyer feel the product is easy to keep using.')}
${h2('SPECIFICATII SI DETALII DE CONFIRMAT')}
${specTable([
  ['Tip produs', 'Personal care device'],
  ['Moduri', 'Use only confirmed modes'],
  ['Material', 'Use exact material if provided'],
  ['Alimentare', 'USB / baterie only if confirmed'],
  ['Curatare', 'Mention only confirmed washable/removable parts'],
])}
${faq([
  { q: 'Putem promite rezultate vizibile?', a: 'Nu fara dovada. Scriem despre rutina, confort si utilizare verificabila.' },
  { q: 'Ce imagini sunt obligatorii?', a: 'Model-use, close-up material, detaliu de curatare si depozitare.' },
])}
${img('./assets/brand_trust_motion_demo.gif', 'Brand motion trust GIF')}
${cta('Rutina personala prezentata prin emotie, confort si dovada', 'Pagina ramane premium, dar nu inventeaza rezultate pe care produsul nu le poate proba.')}`),
  },
  {
    id: '04_baby_safety_soft_rich',
    title: 'Baby safety rich mobile template',
    product_type: 'baby',
    chain:
      'soft_people_banner -> safety_first -> parent_hand_scale -> usage_scene -> feature_benefit -> specs -> package_content -> faq -> closing_confidence',
    html: page(`
${img('../../emag_banner_generation_tests/03_official_people_category_style_rendered_1140x456.png', 'Soft baby care category banner')}
${h2('INCEPE CU LINISTEA PARINTELUI, NU CU DECORUL PRODUSULUI')}
<p>La produsele pentru bebelusi, pagina trebuie sa reduca anxietatea: material, margini, dimensiune, curatare, utilizare zilnica. Designul trebuie sa fie bland, dar informatia trebuie sa ramana precisa.</p>
${anchorFlow([
  { color: '#38bdf8', title: 'Siguranta perceputa', text: 'Material, margini, forma, contact.' },
  { color: '#22c55e', title: 'Scena reala', text: 'Mana parintelui, produsul, locul de folosire.' },
  { color: '#f59e0b', title: 'Confirmare', text: 'Dimensiuni, continut, curatare, restrictii.' },
])}
${slot('PRODUCT IMAGE SLOT', 'Parent-hand scale + soft material board', [
  'Canvas 1140x705. Show parent hand holding product for scale; soft nursery background.',
  'Add close-up crop of edge/material/texture. Avoid unsafe sleep staging or risky use pose.',
  'No text in image; leave top-left label space for deterministic overlay.',
  'Colors: soft blue, white, light green; keep product high contrast.',
], 'This board makes the safety/softness claim visible without using unsupported claims.')}
${band('SIGURANTA SI CONFORT', [
  { title: 'Material vizibil', text: 'Materialul trebuie aratat prin close-up si confirmat prin ProductTruthPack.' },
  { title: 'Margini si contact', text: 'Arata zonele pe care parintele le-ar inspecta cu privirea.' },
  { title: 'Curatare usoara', text: 'Daca piesele sunt detasabile sau lavabile, imaginea trebuie sa arate asta.' },
  { title: 'Dimensiune clara', text: 'Foloseste mana parintelui sau obiect neutru pentru scara.' },
])}
${slot('DETAIL IMAGE SLOT', 'Daily-care usage board', [
  'Canvas 1140x684. Three panels: prepare, use with parent hand, clean/store.',
  'No unsafe baby positioning. No medical or safety certification badge unless provided.',
  'Leave label zones for overlay; use calm daylight and low clutter.',
], 'This replaces generic baby copy with a controlled, parent-readable workflow.')}
${h2('SPECIFICATII DE CONFIRMAT')}
${specTable([
  ['Material', 'Exact material from product facts'],
  ['Dimensiune', 'Length x width x height if provided'],
  ['Curatare', 'Wipe / washable / detachable only if confirmed'],
  ['Continut pachet', 'Main product and included accessories'],
])}
${band('PACHET COMPLET CONTINUT', [
  { title: 'Produs principal', text: 'Fotografiat singur si langa mana pentru scara.' },
  { title: 'Accesorii incluse', text: 'Arata fiecare piesa separat, cu spatiu pentru eticheta.' },
  { title: 'Depozitare', text: 'Daca exista husa/cutie, devine modul de incredere.' },
], '#eef6ff')}
${faq([
  { q: 'Ce trebuie dovedit vizual?', a: 'Materialul, marginile, dimensiunea si modul de curatare.' },
  { q: 'Ce evitam?', a: 'Evitam certificari, varste potrivite sau promisiuni de siguranta fara sursa.' },
])}
${cta('Pagina baby trebuie sa arate bland, dar sa verifice concret', 'Mai putina decoratie, mai multa liniste vizuala pentru parinte.')}`),
  },
  {
    id: '05_coffee_kitchen_lifestyle_rich',
    title: 'Coffee kitchen lifestyle rich mobile template',
    product_type: 'coffee_kitchen',
    chain:
      'lifestyle_result_banner -> taste_convenience_scene -> routine_sequence -> feature_proof -> usage_steps -> specs -> package_content -> faq -> closing_confidence',
    html: page(`
${img('../../emag_banner_generation_tests/04_ai_brand_trust_background_overlay_rendered_1140x456.png', 'Kitchen lifestyle result banner')}
${h2('VINDE MOMENTUL DE DIMINEATA, APOI DOVEDESTE-L CU DETALII')}
<p>La cafea si bucatarie, cumparatorul nu cumpara doar motor, capacitate sau moduri. Cumpara o rutina mai placuta: mai putina mizerie, rezultat mai constant, folosire usoara si curatare rapida.</p>
${anchorFlow([
  { color: '#a16207', title: 'Rezultat', text: 'Cafea, spuma, gust, rutina.' },
  { color: '#0f766e', title: 'Convenienta', text: 'Pasii trebuie sa para simpli.' },
  { color: '#2563eb', title: 'Dovada', text: 'Capacitate, parti detasabile, moduri.' },
])}
${slot('PRODUCT IMAGE SLOT', 'Kitchen counter result scene', [
  'Canvas 1140x705. Product on kitchen counter, cup/result visible, hands optional.',
  'Create three close-up crops: control panel/button, output/result, detachable cleaning part.',
  'No exaggerated steam. No unproven taste statement inside image. No generated text.',
  'Palette: warm kitchen light, but avoid beige-only flat look; product stays central.',
], 'This scene sells the morning result while leaving proof areas for detail modules.')}
${band('BENEFICII SI CARACTERISTICI', [
  { title: 'Rutina mai simpla', text: 'Arata pasul care economiseste timp sau reduce mizeria.' },
  { title: 'Rezultat vizibil', text: 'Cana, spuma sau textura trebuie sa fie compatibile cu functia produsului.' },
  { title: 'Control usor', text: 'Butoanele si modurile trebuie fotografiate separat.' },
  { title: 'Curatare dupa folosire', text: 'Piesa detasabila sau spalabila este un modul de conversie, nu o nota mica.' },
])}
${slot('DETAIL IMAGE SLOT', '4-step routine image board', [
  'Canvas 1140x684. Four panels: add ingredient, start product, show result, clean/remove part.',
  'Use consistent angle and lighting. Keep hands realistic and product shape stable.',
  'Leave label space above each panel for deterministic overlay.',
], 'A routine sequence turns the kitchen appliance into an easy habit.')}
${h2('SPECIFICATII DE CONFIRMAT')}
${specTable([
  ['Capacitate', 'ml / g from product facts'],
  ['Putere', 'W if confirmed'],
  ['Moduri', 'Cold / warm / foam / grind settings only if confirmed'],
  ['Material', 'Steel, glass, ABS, silicone as provided'],
  ['Curatare', 'Detachable / washable facts only'],
])}
${band('PACHET COMPLET CONTINUT', [
  { title: 'Aparat principal', text: 'Imagine produs curat, frontal si in scena.' },
  { title: 'Accesorii', text: 'Lingura, cablu, capac, recipient sau perie daca exista.' },
  { title: 'Manual / ghid', text: 'Doar daca este inclus in pachet.' },
], '#eef6ff')}
${faq([
  { q: 'De ce nu incepem cu tabelul?', a: 'Pentru ca decizia este declansata de rutina dorita; tabelul confirma dupa aceea.' },
  { q: 'Ce trebuie generat ca imagine?', a: 'Scena rezultat, close-up control, piesa de curatare si secventa de folosire.' },
])}
${cta('Rutina de cafea prezentata prin rezultat, pasi si dovada', 'Template-ul combina lifestyle cu specificatii fara sa devina reclama generica.')}`),
  },
  {
    id: '06_store_brand_trust_rich',
    title: 'Store brand trust rich mobile template',
    product_type: 'store_brand_trust',
    chain:
      'brand_trust_gif -> store_positioning -> product_range -> service_evidence_slots -> buyer_question_board -> faq -> closing_confidence',
    html: page(`
${img('./assets/brand_trust_motion_demo.gif', 'Animated brand trust banner')}
${h2('BRANDUL NU SE REPETA, SE FACE FAMILIAR')}
<p>Un modul de incredere bun nu inseamna logo de zece ori. El arata ca vanzatorul are produse coerente, ambalare controlata, suport verificabil si raspunsuri la obiectiile care apar inainte de achizitie.</p>
${anchorFlow([
  { color: '#f59e0b', title: 'Familiaritate', text: 'Brand, ambalaj, oameni, categorie.' },
  { color: '#2563eb', title: 'Ordine', text: 'Gama de produse, proces, informatii clare.' },
  { color: '#16a34a', title: 'Incredere verificabila', text: 'Doar fapte pe care listingul sau sellerul le poate sustine.' },
])}
${slot('PRODUCT IMAGE SLOT', 'Product family lineup + package moment', [
  'Canvas 1140x705. Show 4-6 representative SKUs in one coherent product family lineup.',
  'Create one package/boxing scene with a person holding a plain box; no marketplace logo unless authorized.',
  'Create small neutral icon slots for process cues; text will be overlaid after evidence check.',
  'Use premium dark or clean white background depending on brand palette.',
], 'This module makes a small seller feel organized and less anonymous.')}
${band('MODULE DE INCREDERE', [
  { title: 'Gama coerenta', text: 'Arata mai multe produse din acelasi univers vizual.' },
  { title: 'Ambalare si manipulare', text: 'Un moment cu pachetul face experienta mai reala decat un logo repetat.' },
  { title: 'Proces verificabil', text: 'Foloseste doar termeni de serviciu confirmati in datele sellerului.' },
  { title: 'Intrebari inainte de cumparare', text: 'Raspunde la ce ar cauta cumparatorul in alta parte.' },
])}
${img('../../emag_detail_visual_boards/bestplaza_faq_question_board_v1_800.png', 'Buyer question flow board')}
${slot('DETAIL IMAGE SLOT', 'Store process visual without unsupported promises', [
  'Canvas 1140x456. Three process cards: packed, checked, support path.',
  'No exact delivery time, no refund phrase, no protected-term claim unless evidence is supplied.',
  'Use neutral icons and blank text areas for deterministic overlay.',
], 'This is the safer replacement for unsupported service badges.')}
${faq([
  { q: 'Cand folosim testimonial?', a: 'Numai cand exista review real. Altfel folosim Buyer Question Flow, nu clienti inventati.' },
  { q: 'Ce face pagina mai puternica decat modelul BestPlaza?', a: 'Pastreaza impactul vizual, dar separa clar faptele, imaginile necesare si riscurile de claim.' },
])}
${cta('Incredere construita prin gama, ambalaj si raspunsuri clare', 'Acest modul poate fi atasat la orice produs cand brandul este inca nefamiliar pentru cumparator.')}`),
  },
];

function modulePlan(item) {
  const modules = item.chain.split(' -> ').map((module_id, index, arr) => ({
    module_id,
    buyer_question:
      index === 0
        ? 'What must the buyer understand in the first mobile screen?'
        : `Which objection does ${module_id} remove?`,
    purpose: `Rich mobile module for ${item.product_type}: ${module_id}.`,
    comes_after: index === 0 ? 'start' : arr[index - 1],
    sets_up_next: index === arr.length - 1 ? 'end' : arr[index + 1],
    required_evidence: ['ProductTruthPack facts', 'asset requirements', 'claim constraints'],
    html_component: module_id.includes('gif') || module_id.includes('hero') ? 'component_centered_1140_gif_or_image' : 'mobile_safe_block',
    asset_slots: module_id.includes('image') || module_id.includes('proof') || module_id.includes('range') ? ['product_image_requirement'] : [],
    failure_mode: 'Use neutral question/capability copy when evidence is missing.',
  }));
  return { product_type: item.product_type, template_chain: item.chain, modules };
}

function imageRequirements(item) {
  const slots = [];
  const slotPattern = /<h3[^>]*>([^<]+)<\/h3>[\s\S]*?<ul[^>]*>([\s\S]*?)<\/ul>/g;
  let match;
  while ((match = slotPattern.exec(item.html)) !== null) {
    const requirements = [...match[2].matchAll(/<li[^>]*>(.*?)<\/li>/g)].map((m) =>
      m[1].replace(/<[^>]+>/g, '').trim(),
    );
    slots.push({ title: match[1].replace(/PRODUCT IMAGE SLOT|DETAIL IMAGE SLOT| - /g, '').trim(), requirements });
  }
  return { product_type: item.product_type, image_slots: slots };
}

function mediaIndex(item) {
  return {
    assets: [
      {
        asset_id: `${item.id}_motion_or_banner`,
        asset_type: item.html.includes('brand_trust_motion_demo.gif') ? 'generated_gif' : 'generated_banner',
        local_path: item.html.includes('brand_trust_motion_demo.gif')
          ? './assets/brand_trust_motion_demo.gif'
          : 'see detail.html banner src',
        usage_rights: 'owned_or_generated',
        allowed_use: ['production-after-review'],
      },
      {
        asset_id: `${item.id}_question_board`,
        asset_type: 'generated_banner',
        local_path: '../../emag_detail_visual_boards/bestplaza_faq_question_board_v1_800.png',
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
  writeFileSync(
    join(dir, 'image_requirements.json'),
    `${JSON.stringify(imageRequirements(item), null, 2)}\n`,
    'utf8',
  );
  writeFileSync(join(dir, 'media_asset_index.json'), `${JSON.stringify(mediaIndex(item), null, 2)}\n`, 'utf8');
  cards.push(`<li style="margin:8px 0;"><a href="./${item.id}/detail.html">${esc(item.id)} - ${esc(item.title)}</a></li>`);
}

writeFileSync(
  join(root, 'index.html'),
  page(`<h1 style="font-size:24px;">eMAG HTML Detail Agent v1.2 - Rich Mobile Templates</h1><p>These are richer mobile-first HTML detail samples. Banner/GIF modules are inserted. Product images remain as structured next-step image-agent requirements.</p><ul>${cards.join('')}</ul>`),
  'utf8',
);

console.log(`Generated ${cases.length} rich mobile templates in ${root}`);
