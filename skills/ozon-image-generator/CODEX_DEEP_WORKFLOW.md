# Codex Deep Generation Workflow

This workflow adapts the Ozon main-image agent for Codex/OpenAI-style image
models and future FAL.ai routes that can call those models.

## Goal

Use the existing product planner for product truth, buyer salience, brand
placement, and layout reasoning, then compile a higher-impact image prompt for a
stronger image model.

This route is for outputs that need:

- stronger information hierarchy
- sharper typography and panel design
- higher local contrast and perceived clarity
- richer product/background separation
- fewer, more important labels

## Entry Point

Run the existing agent with:

```bash
python3 scripts/ozon_main_image_agent.py \
  --product-name "<product name>" \
  --product-specs "<facts file or facts text>" \
  --product-image "<source image>" \
  --out-dir "<output dir>" \
  --prompt-compiler codex_deep \
  --prompt-only
```

The important output is:

- `agent_plan.json`: planner result and product reasoning
- `image_model_prompt.txt`: Codex/OpenAI/FAL-ready prompt
- `run_report.md`: route summary

## Routing Rules

The planner still decides product truth and buyer salience. The `codex_deep`
compiler changes only the final prompt profile:

- Use a premium commercial poster-card composition.
- Use heroic product scale and crisp silhouette separation.
- Keep the product body as the protected zone.
- Put readable information in outside information zones.
- Use a strong first-read value block when the value is commercially important.
- Use secondary slabs for important mode/function/value facts.
- Use small side callouts only for non-obvious buyer proof.
- Do not migrate weak details into labels.
- Render each claim once.

## Contrast And Clarity

The prompt asks the image model for high perceived clarity without changing the
product identity:

- deep low-noise background
- high local contrast
- crisp edges
- defined shadows
- rich blacks and clean whites
- saturated category accents
- no grey haze
- no muddy fog
- no flat low-contrast wash
- no over-soft bloom

Lighting can increase depth and separation, but must preserve the product color
atmosphere.

## Information Layout

Use the solar-system preview pattern as the target structure:

- top-right brand shard
- top-left title
- one dominant value block
- two compact secondary slabs when useful
- optional small side callout only when it adds real buyer proof
- bottom/corner category or trust badge

The model should not add labels just because a part is visible. If the fact is
not a first-second buying reason, leave it for a detail image.

## Future FAL.ai Adapter

When the FAL.ai key/API route is available, keep this split:

1. This script produces `image_model_prompt.txt`.
2. The FAL/OpenAI adapter sends that prompt plus the source image to the image
   model.
3. The adapter writes the final image next to `agent_plan.json` and
   `run_report.md`.

Do not merge Codex/OpenAI prompt shaping back into the Gemini `fusion_v1` image
route until side-by-side tests prove that the same wording improves Gemini.
