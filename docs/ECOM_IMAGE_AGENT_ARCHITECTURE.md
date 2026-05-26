# Ecommerce Image Generation Agent Architecture

Date: 2026-05-04

## Position

This project should not start from a heavy multi-agent platform. The core loop should be a small, file-based visual production system:

```text
ProductTruthPack
  -> TemplateCard
  -> SellingPointPlan
  -> ModelPrompt
  -> image-to-image generation
  -> visual scoring
  -> repair prompt
  -> optional PSD/text-layer assembly
```

PSD is useful, but it is not the center of the system. It is a delivery and control layer used when text accuracy, editable handoff, or deterministic placement matter.

## Why this shape

The examples collected from Xiaohongshu, Amazon/Ozon layout posts, GPT Image 2 prompt tips, and PSD template posts are phone screenshots and learning references, not clean image templates. They should be used to extract visual logic, prompt structure, and marketplace rules. They should not be fed directly into image generation as reference images unless a clean crop/template is first prepared.

These references all point to the same operational rule:

- The image must answer a commercial question in 0.5-3 seconds.
- The product must be large and recognizable.
- The visual should contain 1-3 focus points, not a pile of tiny text.
- Numbers and badges beat long copy in marketplace thumbnails.
- A successful image is a structured layout, not a random beautiful scene.
- Prompt quality improves when the instruction separates what to keep, what to change, and where elements should appear.

## Components

### 1. ProductTruthPack

Stores product identity and non-negotiable traits.

Responsibilities:

- Product category and target marketplace.
- Immutable traits: color, shape, labels, ports, material, parts.
- Allowed changes: background, lighting, crop, scene, props.
- Forbidden changes: changed product, wrong text, extra parts.
- Selling points and proof points.

### 2. TemplateCard

A reusable visual logic card derived from successful examples.

Responsibilities:

- Layout type: hero, pain-solution, proof, lifestyle, comparison, grid, detail page.
- Product placement and approximate product weight.
- Text/badge zones.
- Style language: color palette, lighting, background, mood.
- Model instructions: what to preserve from reference, what to replace.
- Whether final text should be rendered by model or overlaid later.

### 3. SellingPointPlan

Converts raw product features into visual claims.

Example:

```text
"350W suction" -> large number badge + dust/debris visual path + clean floor result
"360 degree rotation" -> arrow ring + numbered hinge callouts + comparison with limited stand
"waterproof" -> product in splash/rain scene + IP rating badge
```

### 4. ModelPrompt

Compiled from truth pack, template card, and selling point plan.

Prompt must be:

- Concrete and visible.
- Structured by scene, subject, details, usage, constraints.
- Explicit about keep/change boundaries.
- Explicit about text behavior.
- Model-specific where needed.

### 5. Visual Scoring

Scores both image quality and commercial usefulness.

Minimum score dimensions:

- Product fidelity.
- Product size/recognition.
- Template compliance.
- Selling point clarity.
- Thumbnail readability.
- Text accuracy or text-zone safety.
- Market style fit.

### 6. Repair Loop

Every repair prompt should repeat invariant product constraints and only change failed dimensions.

Good repair style:

```text
Keep product unchanged. Only adjust: enlarge product to 65% of canvas, reduce background clutter, make the number badge more readable. Do not alter product geometry, logo, color, or parts.
```

## PSD Boundary

Use PSD when:

- The output contains important English/Russian/Japanese text.
- The user needs Photoshop/Photopea editability.
- Product placement or text layout must be deterministic.
- The generation model produces good visuals but weak text.
- We need to assemble a repeatable image set from product cutout + generated background + text layers.

Do not force PSD when:

- The goal is fast visual direction exploration.
- The image has no final text.
- A single img2img result is already commercially usable.
- The model successfully follows composition and product fidelity.

## Execution Modes

### Mode A: Reference Img2Img

Fastest validation path.

```text
product image + visual template image + compiled prompt -> model output
```

Use for hero images, concept posters, lifestyle scenes, and style exploration.

### Mode B: Img2Img + deterministic text

Best default for marketplace selling-point images.

```text
product image + visual template image + prompt with empty text zones -> model background/composition
then overlay approved copy with script/PSD
```

### Mode C: PSD assembly

Best for final deliverables.

```text
generated background + real product cutout + text layers + badges + frame -> PSD + preview
```

## Initial Template Families

1. Search-stop hero: large product, simple background, one visual hook.
2. Pain-solution: scenario problem plus product solving it.
3. Proof/detail: material, certification, parameter, or close-up evidence.
4. Lifestyle/dream: target user scene and emotional ownership.
5. White-background ticket: clean product image for algorithmic recognition.
6. Amazon/Ozon high-conversion grid: product large, numeric badges, 2-4 function icons, scene/detail inset.
7. Industrial dark detail page: black/gray background, modular panels, gold/orange or blue accents.
8. Japanese/Rakuten vertical landing banner: high information density, badges, soft trust palette.

## Next Build Target

The next concrete task should be a one-SKU reference-img2img experiment:

1. Select one product from existing local samples.
2. Select one TemplateCard from `workflow/template_cards`.
3. Compile prompt with `workflow/prompt_recipes/reference_img2img_base.md`.
4. Generate 2-3 candidates.
5. Score with `workflow/scorecards/ecommerce_image_scorecard.json`.
6. If text fails, move to Mode B or Mode C.
