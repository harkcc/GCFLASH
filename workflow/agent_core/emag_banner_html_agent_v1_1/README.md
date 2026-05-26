# eMAG Banner + HTML Agent v1.1

This is the stable EXCITAT route for eMAG detail-page banners and HTML modules.
It turns the current research into a repeatable agent package:

```text
Plan / DesignSpec -> Generate or Composite -> Validate -> Repair -> Final Export
```

The visual brand is always `EXCITAT`. Internal slugs may use `excitat`.

## Package Contents

- `DESIGN.md`: visual system, rhythm, typography, color and motion rules.
- `DESIGN_FD.md`: HTML/front-end delivery contract for eMAG detail modules.
- `data/banner_patterns.jsonl`: stable banner families and route rules.
- `data/tag_library.jsonl`: reusable EXCITAT tags and placement policy.
- `data/validation_cases.jsonl`: blocker and expected-pass cases.
- `prompt_contracts/`: provider-neutral prompt contracts.
- `validators/VALIDATION_RULES.md`: BDD-like gate and repair map.

## Conversation Trace

Current phase notes are captured in
`/Users/cc/Desktop/photo_show/research/2026-05-24_excitat_banner_stable_route_conversation_trace.md`.
That note is not a final design spec. It records the stable route, component
boundaries, generation templates, validation gates, and open work from the
current EXCITAT eMAG detail-page discussion.

## Production Rule

Use AI for scene, mood and background. Use deterministic local composition for
final text, brand tags, parameters, QA, review cards, service cues and GIF
effects.
