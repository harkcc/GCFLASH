# Screenshot Method to TemplateCard

Date: 2026-05-05

This document turns the phone-screenshot research into reusable ecommerce image rules. The screenshots are not clean templates. They are evidence for visual logic, prompt structure, marketplace hierarchy, and scoring criteria.

## Extraction Boundary

Use screenshots for:

- layout archetype
- visual hierarchy
- product scale
- badge/icon density
- prompt-writing style
- platform-specific selling logic
- repair/scoring rules

Do not use screenshots for:

- direct image reference without a clean crop
- copying original author UI, social chrome, comments, watermark, or brand
- final marketplace text
- unsupported product claims

## Reusable Method

1. Identify the commercial question.
   - Main image: "what is this, why stop scrolling?"
   - Selling-point image: "what problem does it solve?"
   - Detail image: "is it real, durable, and trustworthy?"
   - Scene image: "where does the buyer imagine using it?"
   - Comparison image: "what changes before vs after?"

2. Extract the layout, not the picture.
   - product anchor
   - headline zone
   - badge zones
   - detail inset zones
   - proof/trust strip
   - empty text zones for later overlay

3. Convert the extracted layout into a TemplateCard.
   - `slot_role`
   - `product_weight`
   - `text_zone_policy`
   - `allowed_claim_types`
   - `style_tokens`
   - `psd_layer_plan`

4. Compile prompt from the card.
   - Reference role
   - Product truth
   - Keep
   - Change
   - Layout
   - Text policy
   - Negative constraints
   - Repair delta

5. Score against commercial usefulness, not beauty alone.

## Screenshot Families Mapped to TemplateCards

| Screenshot logic | TemplateCard | Main use |
| --- | --- | --- |
| Vacuum / pet cleaning action | `HeroLifestyleSceneCard`, future `PainSolutionActionCard` | pain-solution scene |
| Adjustable stand blueprint | `CalloutAroundProductCard`, future `ComparisonBlueprintCard` | mechanical structure explanation |
| Purple Amazon/Walmart PSD post | `AmazonPurpleFeatureGridCard` | dense Amazon attachment image |
| Russian/Ozon rules | `OzonHighConversionMainCard` | thumbnail-first marketplace main image |
| Industrial product detail page | `IndustrialDarkDetailCard` | tool/B2B trust detail |
| Ozon pet-product examples | `OzonHighConversionMainCard`, `MultiSceneGridCard` | fast product recognition + trust |
| Japanese/Rakuten prompt examples | `JapaneseRakutenTrustBannerCard` | soft trust / mobile landing banner |

## European / Marketplace Style Notes

The "European/Ozon/eMAG" direction the user likes should be treated as a style scale, not a single template:

- high product visibility
- cool white/gray base
- strong but limited blue/green/yellow accent
- short badges, large numbers, icon proof
- fewer decorative elements than Chinese social templates
- more trust/proof modules than pure white Amazon hero
- practical scenes: car, workshop, desk, home, outdoor use

This maps best to:

- `OzonHighConversionMainCard`
- `IndustrialDarkDetailCard`
- `PackageTrustCard`
- `BeforeAfterSplitCard`
- future `EuropeanCleanProofCard`

## OpenDesign Mapping

OpenDesign's useful pattern is composable file contracts:

- `DESIGN.md`: visual tokens and anti-patterns
- `SKILL.md`: workflow instructions
- `assets/template`: seed layout
- `references/checklist.md`: quality gates
- critique loop: evidence-backed scores and actionable fixes
- prompt stack: discovery + design system + skill + metadata

For this project, the equivalent is:

- `EcommerceDesignMD`: brand/marketplace visual rules
- `TemplateCard`: layout and slot rules
- `PromptRecipe`: prompt compiler body
- `SuitePlan`: 5-8 image story order
- `ProductTruthPack`: product facts and forbidden claims
- `Scorecard`: product/commercial/text/marketplace scoring
- `ReviewLog`: human and model review writeback

