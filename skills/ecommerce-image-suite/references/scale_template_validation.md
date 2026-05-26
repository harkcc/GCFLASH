# Scale Template Validation Reference

Use this when the user asks to validate the newer marketplace-template approach
instead of the older Image2-keyword/PIL-overlay route.

## Command

```bash
python3 scripts/run_scale_template_validation.py
```

## Core Rule

Do not treat a generated image as the system. The system is the artifact chain:

```text
ProductTruthPack
  -> ScaleBaseline
  -> SuiteTemplate
  -> TemplateCard
  -> BrandStylePack
  -> ShotPlan + TemplateParams + CopyPlan
  -> candidate generator
  -> QAReport
  -> typed RepairPlan
```

## Scale Baselines

- `scale_a_nexscope_amazon_7`: Amazon 7-image suite strategy.
- `scale_b_ozon_wb_template_adaptation`: Ozon/WB 3:4 template adaptation.
- `scale_c_brandshootkit_qa_reroll`: preserve/QA/reroll route comparison.

## Template Products

- `single_image_template`: reverse-engineered one-image layout.
- `suite_template`: full gallery slot sequence.
- `psd_template`: layered control/delivery template.

## Important Boundary

`template_render_mvp` is a structural renderer for validation. It is not the
final visual renderer. After the artifact chain passes, route selected slots to:

- GPT Image 2 / Image2 reference edit for scene/background exploration.
- ComfyUI-productfix style preservation for product/logo/detail fidelity.
- Fabric/PSD/HTML renderer for final text, badges, font, icon, and brand frame.

