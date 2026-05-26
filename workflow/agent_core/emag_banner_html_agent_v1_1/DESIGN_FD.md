# eMAG Detail HTML / Front-End Delivery Contract v1.1

## Output Shape

Every run must export:

- `detail.html`
- `preview_mobile.html`
- `DESIGN_SPEC.json`
- `media_asset_index.json`
- `validation_report.json`
- `repair_log.md`

## HTML Policy

Allowed core tags:

- `p`, `h2`, `h3`, `strong`, `br`, `ul`, `li`, `img`

Gray-zone tags allowed when simple and validated:

- `div`, `span`, `table`, `tr`, `td`, `blockquote`

Forbidden:

- `script`, `iframe`, `form`, external CSS, external JS

Preferred image embed:

```html
<p style="text-align:center;margin:0 0 20px 0;">
  <img src="assets/module.png" width="1140" alt="..." style="max-width:100%;height:auto;">
</p>
```

## Mobile Policy

- Rendered image modules should be 1140 px wide.
- 390 px mobile preview must not clip, overlap or create unreadable small text.
- Text-heavy modules must stay as simple HTML or locally rendered boards.
- Complex visual boards become one image/GIF, not a fragile HTML layout.

## Review and QA Separation

- QA answers buyer doubts and must not use fake names, dates, ratings or stars.
- Review boards can use preview placeholders only when explicitly marked as preview.
- Real review boards require source, rating and date evidence.

## Route Policy

- `pure_composite`: specs, QA, review, manual, service cues.
- `ai_background_plus_composite`: premium hero, scene banner, product context.
- `pure_ai_generation`: exploration only; not production unless validated.

