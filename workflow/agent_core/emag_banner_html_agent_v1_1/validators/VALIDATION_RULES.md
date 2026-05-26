# EXCITAT Banner + HTML Validation Rules

## Gate Sequence

```text
Plan -> Generate/Composite -> Validate -> Repair -> Final
```

The validator runs after every candidate. A final export is not accepted until
blockers are gone.

## Blockers

- Brand display is not exactly `EXCITAT`.
- `script`, `iframe`, `form`, external CSS or JS appear in `detail.html`.
- Product is visibly deformed or duplicated by AI generation.
- Final text is unreadable on 390 px mobile preview.
- QA contains fake review signals: names, dates, stars or ratings.
- Review preview is not labeled as preview.
- Delivery, return, warranty, rating, platform or certification claims lack evidence.
- Official marketplace assets are used commercially without rights.

## Repair Map

- Product drift: switch to real product image composite.
- Text error: disable model text and rerender local overlay.
- Too cluttered: remove chips/cards and insert a white text rest module.
- Mobile unreadable: increase type, reduce text, or split module.
- Motion risky: downgrade to static or keep only `shine_sweep`.
- Repeated image logic: crop proof detail or replace with text/spec board.

