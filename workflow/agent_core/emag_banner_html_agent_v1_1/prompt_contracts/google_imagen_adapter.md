# Google Imagen Adapter Contract

Do not hard-code Imagen 2. The agent must use a provider adapter selected by
current account/model availability.

## Capability Contract

- `background_generation`
- `reference_layout_exploration`
- `image_edit_or_inpaint` when available

## Output Boundary

Imagen outputs are treated as background or mood assets until local composition
adds exact EXCITAT branding and final text.

