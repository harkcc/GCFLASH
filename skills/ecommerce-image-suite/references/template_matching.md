# Template Matching Rules

Templates are selected by commercial job, not by decoration.

## Slot Mapping

Use `workflow/suite_plans/ecommerce_5_to_8_suite_plan.json`.

| Slot | Job | Buyer Question | Common Templates |
| --- | --- | --- | --- |
| 1 | Search-stop hero | What is this and why stop scrolling? | HeroCleanCenterCard, OzonHighConversionMainCard |
| 2 | Pain-solution | What problem does it solve? | FeatureRightTextCard, CalloutAroundProductCard |
| 3 | Proof/detail | Can I trust it? | IndustrialDarkDetailCard, DetailMacroCard, PackageTrustCard |
| 4 | Lifestyle | Where will I use it? | HeroLifestyleSceneCard |
| 5 | Comparison | Why this one? | BeforeAfterSplitCard, MultiSceneGridCard |
| 6 | Package/trust | What is included? | PackageTrustCard |
| 7 | Dense platform attachment | Can I scan benefits fast? | AmazonPurpleFeatureGridCard, JapaneseRakutenTrustBannerCard |
| 8 | White ticket | Can platform identify the SKU? | HeroCleanCenterCard |

## Matching Criteria

Score candidate templates before picking:

- buyer question fit
- product category fit
- product aspect ratio fit
- text-policy fit
- marketplace fit
- risk of hallucinated details
- brand/design-system fit

## TemplateCard Requirements

Every TemplateCard must include:

- image role
- marketplaces
- viewer question
- core layout pattern
- product weight
- zones
- style language
- text policy
- keep/change rules
- model notes
- scoring focus

Use `workflow/schemas/template_card.schema.json`.

## Screenshot References

User-provided phone screenshots are methodology references only.

Allowed use:

- infer layout logic
- extract prompt-writing patterns
- extract marketplace scoring rules
- identify style preferences

Disallowed use:

- treating the screenshot as a clean template
- copying app UI overlays
- feeding the whole phone screenshot as the only reference image
- assuming text inside screenshot is final copy

## Brand Frame References

Brand frame references should produce rules, not random decorations:

- frame geometry
- corner treatment
- line weight
- color budget
- logo slot
- badge shapes
- safe areas
- where the frame must not cover product details
