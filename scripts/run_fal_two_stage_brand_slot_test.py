#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.request import urlretrieve

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/20260522_fal_two_stage_brand_slot"
SIZE = 1024


SOURCE = (
    ROOT
    / "references/user_cases/20260521_emag_cangswjp/products/31_DDD60W3BM_Kit-suport-perete-Excitat-pentru-PS5-Slim-Pro-cu-Incarcator-Dual-pentru-Controlere-si-In/main_gallery/01_6d9b90c4.jpg"
)


FRAME_PROMPT = (
    "Edit only the masked outer border and top-right brand shelf area. Preserve all unmasked product, product box, "
    "RGB badge, headline text, and layout exactly. Create a premium thin integrated gaming-tech marketplace border: "
    "black base, cyan and magenta hairline rails, subtle circuit accents only on the edge, not a thick poster frame. "
    "In the top-right, create a low-profile empty brand shelf integrated with the border, shaped like a slim angled tab. "
    "The shelf must be blank: no readable letters, no logo, no random text. Keep the design modern, sharp, and commercial."
)


LOGO_PROMPT = (
    "Inside the masked blank top-right brand shelf, add only the exact word EXCITED. Use sharp sporty italic art lettering, "
    "white letters with cyan highlights and a subtle dark shadow. Keep it low profile and integrated into the shelf. "
    "Do not add any other words, numbers, slogans, icons, or extra labels. Preserve everything outside the mask exactly."
)


NEGATIVE = (
    "No thick frame. No large logo block. No extra sentence. No random text. No second logo. No product redraw. "
    "No covering the RGB badge or product. No old-fashioned clipart."
)


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def fit_square(path: Path) -> Image.Image:
    src = Image.open(path).convert("RGB")
    ratio = SIZE / max(src.width, src.height)
    resized = src.resize((round(src.width * ratio), round(src.height * ratio)), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (SIZE, SIZE), "white")
    canvas.paste(resized, ((SIZE - resized.width) // 2, (SIZE - resized.height) // 2))
    return canvas


def make_frame_mask() -> Image.Image:
    mask = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(mask)
    edge = 24
    d.rectangle((0, 0, SIZE, edge), fill=255)
    d.rectangle((0, SIZE - edge, SIZE, SIZE), fill=255)
    d.rectangle((0, 0, edge, SIZE), fill=255)
    d.rectangle((SIZE - edge, 0, SIZE, SIZE), fill=255)
    # Broad enough to remove the original/AI logo, but shallow enough not to
    # become a banner. The left headline block remains unmasked.
    d.polygon([(680, 0), (SIZE, 0), (SIZE, 96), (722, 92), (666, 48)], fill=255)
    return mask


def make_logo_mask() -> Image.Image:
    mask = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(mask)
    # 1024 target: height 52 px, width 214 px. This follows the reference as a
    # thin top-right wordmark zone, not an oversized sticker.
    d.polygon([(776, 14), (1006, 14), (1006, 66), (804, 66), (768, 42)], fill=255)
    return mask


def preview(base: Image.Image, mask: Image.Image) -> Image.Image:
    out = base.convert("RGBA")
    red = Image.new("RGBA", base.size, (255, 0, 0, 0))
    red.putalpha(mask.point(lambda v: 105 if v else 0))
    out.alpha_composite(red)
    return out.convert("RGB")


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def call_fal(model: str, image_path: Path, mask_path: Path, prompt: str, extra: dict[str, object]) -> dict[str, object]:
    import fal_client

    image_url = fal_client.upload_file(str(image_path))
    mask_url = fal_client.upload_file(str(mask_path))
    args: dict[str, object] = {
        "prompt": f"{prompt} Negative constraints: {NEGATIVE}",
        "image_url": image_url,
        "mask_url": mask_url,
        "num_images": 1,
        **extra,
    }
    result = fal_client.subscribe(model, arguments=args, with_logs=False, client_timeout=180)
    images = result.get("images") or []
    if not images and result.get("image"):
        images = [result["image"]]
    if not images:
        raise RuntimeError(f"No image in fal result for {model}: {result}")
    return {"result": result, "url": images[0]["url"]}


def make_sheet(paths: dict[str, Path], out: Path) -> None:
    order = ["input", "frame_mask", "stage1", "logo_mask", "stage2"]
    labels = {
        "input": "input",
        "frame_mask": "stage 1 mask",
        "stage1": "stage 1 frame slot",
        "logo_mask": "stage 2 mask",
        "stage2": "stage 2 logo",
    }
    tile = 260
    label_h = 42
    sheet = Image.new("RGB", (tile * len(order), tile + label_h), "white")
    d = ImageDraw.Draw(sheet)
    f = font(16, True)
    for i, key in enumerate(order):
        img = Image.open(paths[key]).convert("RGB")
        img.thumbnail((tile - 14, tile - 14), Image.Resampling.LANCZOS)
        x = i * tile + (tile - img.width) // 2
        y = 8 + (tile - img.height) // 2
        sheet.paste(img, (x, y))
        d.text((i * tile + 10, tile + 8), labels[key], font=f, fill=(22, 26, 32))
    sheet.save(out, quality=94)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--frame-model", default="fal-ai/flux-pro/v1/fill")
    parser.add_argument("--logo-model", default="fal-ai/ideogram/v3/edit")
    args = parser.parse_args()

    load_env(ROOT / ".env")
    ensure(OUT)
    ensure(OUT / "inputs")
    ensure(OUT / "masks")
    ensure(OUT / "outputs")

    base = fit_square(SOURCE)
    input_path = OUT / "inputs/tech_input.png"
    frame_mask = make_frame_mask()
    logo_mask = make_logo_mask()
    frame_mask_path = OUT / "masks/tech_frame_mask.png"
    logo_mask_path = OUT / "masks/tech_logo_mask.png"
    input_path.parent.mkdir(parents=True, exist_ok=True)
    base.save(input_path)
    frame_mask.save(frame_mask_path)
    logo_mask.save(logo_mask_path)
    frame_preview = OUT / "masks/tech_frame_mask_preview.jpg"
    logo_preview = OUT / "masks/tech_logo_mask_preview.jpg"
    preview(base, frame_mask).save(frame_preview, quality=94)
    preview(base, logo_mask).save(logo_preview, quality=94)

    prompts = {
        "source": str(SOURCE),
        "input": str(input_path),
        "frame_mask": str(frame_mask_path),
        "logo_mask": str(logo_mask_path),
        "frame_prompt": FRAME_PROMPT,
        "logo_prompt": LOGO_PROMPT,
    }
    (OUT / "two_stage_prompts.json").write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")

    if not args.run:
        print(OUT / "two_stage_prompts.json")
        return

    if not os.environ.get("FAL_KEY"):
        raise SystemExit("FAL_KEY is not set")

    stage1_info = call_fal(
        args.frame_model,
        input_path,
        frame_mask_path,
        FRAME_PROMPT,
        {"output_format": "png", "safety_tolerance": "2", "enhance_prompt": False, "seed": 220527},
    )
    stage1_path = OUT / "outputs/tech_stage1_frame_slot.png"
    urlretrieve(str(stage1_info["url"]), stage1_path)

    # Re-preview the logo mask on the stage1 image, because this is the actual
    # second-stage edit target.
    stage1_img = Image.open(stage1_path).convert("RGB")
    logo_stage1_preview = OUT / "masks/tech_logo_mask_on_stage1_preview.jpg"
    preview(stage1_img, logo_mask).save(logo_stage1_preview, quality=94)

    stage2_info = call_fal(
        args.logo_model,
        stage1_path,
        logo_mask_path,
        LOGO_PROMPT,
        {"rendering_speed": "QUALITY", "expand_prompt": False, "style": "DESIGN", "seed": 220528},
    )
    stage2_path = OUT / "outputs/tech_stage2_logo_ideogram.png"
    urlretrieve(str(stage2_info["url"]), stage2_path)

    results = {
        "stage1": stage1_info,
        "stage2": stage2_info,
        "stage1_path": str(stage1_path),
        "stage2_path": str(stage2_path),
    }
    (OUT / "two_stage_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    make_sheet(
        {
            "input": input_path,
            "frame_mask": frame_preview,
            "stage1": stage1_path,
            "logo_mask": logo_stage1_preview,
            "stage2": stage2_path,
        },
        OUT / "two_stage_result_sheet.jpg",
    )
    print(OUT / "two_stage_result_sheet.jpg")


if __name__ == "__main__":
    main()
