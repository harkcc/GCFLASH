# Source Contract

The production agent intentionally does not replace the Gemini-created source
documents. It consumes them as the canonical contract:

- `../ozon-image-generator/README.md`
- `../ozon-image-generator/SKILL.md`
- `../ozon-image-generator/DESIGN.md`

Interpretation rules:

1. `README.md` defines the high-level order: analyze, prompt, check.
2. `SKILL.md` defines the product-analysis checklist, generation prompt rules,
   and product-fidelity/composite methodology.
3. `DESIGN.md` defines the visual system: palette, typography, components,
   icons, layout, safe margins, and mobile validation.
4. Product blueprints under `outputs/*_blueprint.md` are run-specific plans
   generated from those source rules. When available, they should drive the
   exact scene, copy hierarchy, feature badges, and brand shelf variant.
5. The model should generate only visual scene/product base imagery. Text and
   brand overlays are deterministic post-processing layers.

