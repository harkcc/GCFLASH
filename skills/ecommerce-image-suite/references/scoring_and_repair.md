# Scoring And Repair

Use scoring to decide repair, not to produce a decorative report.

## Reviewer Roles

Use three reviewer perspectives:

1. Commercial creative reviewer
   - thumbnail stopping power
   - marketplace fit
   - visual hierarchy
   - style consistency

2. Product truth reviewer
   - product fidelity
   - parts count
   - material and color preservation
   - fake details
   - claim accuracy

3. Layout and text reviewer
   - text readability
   - typo risk
   - text-zone safety
   - PSD/overlay need
   - module balance

## Dimension Scores

Use `workflow/scorecards/ecommerce_multimodel_scorecard.json`.

Default pass threshold: 82.

Manual review required if:

- product_fidelity is below threshold
- selling_point_accuracy is below threshold
- text_quality is unsafe for final use

## Fail Conditions

Reject or repair if:

- product is not the first recognizable thing
- product shape, color, parts, or included accessories changed
- unsupported numbers/certifications/warranty claims appear
- text is intended as final but unreadable or misspelled
- template role and buyer question do not match
- image is generic AI art rather than a marketplace commercial image
- suite images repeat the same selling point instead of progressing

## Repair Prompt Pattern

Use this structure:

```text
Keep product unchanged:
- <immutable trait 1>
- <immutable trait 2>
- <immutable trait 3>

Only repair these failed dimensions:
- <failed dimension>
- <specific visual fix>

Do not change:
- product geometry
- product colors/materials
- ports/buttons/parts/accessories
- logo/labels
- approved facts

Target outcome:
- <template role>
- <buyer question>
- <thumbnail/readability goal>
```

## PSD Or Overlay Decision

Set `psd_or_overlay_needed = true` if:

- final copy is important
- output has English/Russian/Japanese text
- marketplace compliance depends on exact words
- badges need reusable localization
- brand frame must be editable

Do not waste repair iterations trying to make the model spell final text if a
deterministic overlay would solve it.
