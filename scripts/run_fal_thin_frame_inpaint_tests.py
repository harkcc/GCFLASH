#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from urllib.request import urlretrieve

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/20260522_fal_thin_frame_inpaint"
SIZE = 1024


TESTS = [
    {
        "id": "01_teal_baby_thin",
        "source": ROOT
        / "references/user_cases/20260521_emag_cangswjp/products/02_D5YN6S3BM_Aparat-de-gatit-cu-aburi-si-blender-pentru-bebelusi-Excitat-multifunctional-Alarma-LED-a/main_gallery/01_890ab6b4.jpg",
        "prompt": (
            "Edit only the masked border and top-right brand tag. Preserve the unmasked baby steamer blender product, "
            "orange food, bottom title strip, left icon stack, and overall composition exactly. Create a very thin elegant "
            "teal marketplace border that blends into the white background. In the top-right corner create a compact, flat, "
            "slightly slanted brand tab with the word EXCITED, sporty italic art lettering, white/cyan letters, subtle black "
            "shadow, small and low profile, not covering the product. Premium eMAG/Ozon style product main image, clean, modern."
        ),
    },
    {
        "id": "02_neon_tech_thin",
        "source": ROOT
        / "references/user_cases/20260521_emag_cangswjp/products/31_DDD60W3BM_Kit-suport-perete-Excitat-pentru-PS5-Slim-Pro-cu-Incarcator-Dual-pentru-Controlere-si-In/main_gallery/01_6d9b90c4.jpg",
        "prompt": (
            "Edit only the masked outer frame and top-right brand tag. Preserve the unmasked PS5 wall mount product, box, "
            "RGB badge, text blocks, and layout exactly. Upgrade the border into a thin modern black-cyan-purple neon frame, "
            "rounded square marketplace main image style, with subtle circuit details only at the edges. Top-right brand tag "
            "must be compact and flat, naturally integrated with the frame, reading EXCITED in sharp futuristic italic art font. "
            "Do not make a thick poster frame, do not cover the product."
        ),
    },
    {
        "id": "03_ornamental_thin",
        "source": ROOT
        / "references/user_cases/20260521_emag_cangswjp/products/19_DYKFJW3BM_Puzzle-din-Lemn-244-Piese-Excitat-Model-Artistic-Cathedral-Cat-Castelul-Magic-Colorful-D/main_gallery/01_01756804.jpg",
        "prompt": (
            "Edit only the masked border and top-right brand tag. Preserve the unmasked puzzle product, cat artwork, wooden box, "
            "hand, and central image exactly. Create a thin premium ornamental black-pink border, elegant small floral/puzzle "
            "line details only around the edges, white inner product field. Add a compact top-right EXCITED brand tag with art "
            "lettering, small and tasteful, integrated into the ornamental border. Modern marketplace main image, refined and not crowded."
        ),
    },
]


NEGATIVE = (
    "Do not alter the unmasked product. Do not redraw product. Do not add a thick frame. Do not make a large logo block. "
    "Do not add random icons. Do not cover the product. No old-fashioned clipart. No messy text. No extra products."
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


def mask_for(test_id: str) -> Image.Image:
    mask = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(mask)

    edge = 28
    if "neon" in test_id:
        edge = 34
    d.rectangle((0, 0, SIZE, edge), fill=255)
    d.rectangle((0, SIZE - edge, SIZE, SIZE), fill=255)
    d.rectangle((0, 0, edge, SIZE), fill=255)
    d.rectangle((SIZE - edge, 0, SIZE, SIZE), fill=255)

    # A compact top-right brand shelf area. It is deliberately shallow because
    # the reference logo tab is a small eMAG-style corner mark, not a large hero
    # banner.
    if "teal" in test_id:
        pts = [(730, 0), (SIZE, 0), (SIZE, 106), (690, 104)]
    elif "neon" in test_id:
        pts = [(690, 0), (SIZE, 0), (SIZE, 128), (650, 122)]
    else:
        pts = [(700, 0), (SIZE, 0), (SIZE, 112), (660, 110)]
    d.polygon(pts, fill=255)
    return mask


def make_mask_preview(base: Image.Image, mask: Image.Image) -> Image.Image:
    preview = base.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (255, 0, 0, 0))
    red = Image.new("RGBA", base.size, (255, 0, 0, 115))
    red.putalpha(mask.point(lambda v: 115 if v else 0))
    overlay.alpha_composite(red)
    preview.alpha_composite(overlay)
    return preview.convert("RGB")


def system_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def make_sheet(rows: list[dict[str, str]], out: Path) -> None:
    tile = 330
    label_h = 52
    sheet = Image.new("RGB", (tile * 3, (tile + label_h) * len(rows)), "white")
    d = ImageDraw.Draw(sheet)
    title = system_font(18, True)
    headers = ["input", "mask", "fal output"]
    for col, header in enumerate(headers):
        d.text((col * tile + 10, 8), header, font=title, fill=(24, 28, 34))
    for r, row in enumerate(rows):
        y = r * (tile + label_h) + 30
        for col, key in enumerate(["input", "mask_preview", "output"]):
            img = Image.open(row[key]).convert("RGB")
            img.thumbnail((tile - 18, tile - 18), Image.Resampling.LANCZOS)
            x = col * tile + (tile - img.width) // 2
            sheet.paste(img, (x, y + (tile - img.height) // 2))
        d.text((10, y + tile + 8), row["id"], font=title, fill=(24, 28, 34))
    sheet.save(out, quality=94)


def prepare() -> list[dict[str, str]]:
    ensure(OUT / "inputs")
    ensure(OUT / "masks")
    ensure(OUT / "mask_previews")
    rows: list[dict[str, str]] = []
    for test in TESTS:
        base = fit_square(test["source"])
        mask = mask_for(test["id"])
        input_path = OUT / "inputs" / f"{test['id']}_input.png"
        mask_path = OUT / "masks" / f"{test['id']}_mask.png"
        preview_path = OUT / "mask_previews" / f"{test['id']}_mask_preview.jpg"
        base.save(input_path)
        mask.save(mask_path)
        make_mask_preview(base, mask).save(preview_path, quality=94)
        rows.append(
            {
                "id": test["id"],
                "source": str(test["source"]),
                "input": str(input_path),
                "mask": str(mask_path),
                "mask_preview": str(preview_path),
                "prompt": f"{test['prompt']} Negative constraints: {NEGATIVE}",
            }
        )
    (OUT / "fal_thin_frame_prompts.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return rows


def run_fal(rows: list[dict[str, str]], model: str, limit: int | None) -> list[dict[str, str]]:
    import fal_client

    ensure(OUT / "outputs")
    api_key = os.environ.get("FAL_KEY")
    if not api_key:
        raise SystemExit("FAL_KEY is not set")

    completed: list[dict[str, str]] = []
    for row in rows[: limit or len(rows)]:
        image_url = fal_client.upload_file(row["input"])
        mask_url = fal_client.upload_file(row["mask"])
        result = fal_client.subscribe(
            model,
            arguments={
                "prompt": row["prompt"],
                "image_url": image_url,
                "mask_url": mask_url,
                "num_images": 1,
                "output_format": "png",
                "safety_tolerance": "2",
                "enhance_prompt": False,
                "seed": 220526,
            },
            with_logs=False,
        )
        images = result.get("images") or []
        if not images and result.get("image"):
            images = [result["image"]]
        if not images:
            raise RuntimeError(f"No image in fal result for {row['id']}: {result}")
        url = images[0]["url"]
        output_path = OUT / "outputs" / f"{row['id']}_{model.replace('/', '_')}.png"
        urlretrieve(url, output_path)
        done = dict(row)
        done["output"] = str(output_path)
        done["fal_url"] = url
        done["model"] = model
        completed.append(done)
        time.sleep(0.5)

    (OUT / "fal_results.json").write_text(json.dumps(completed, ensure_ascii=False, indent=2), encoding="utf-8")
    return completed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--model", default="fal-ai/flux-pro/v1/fill")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--ids",
        nargs="*",
        default=None,
        help="Optional test ids to run, for quota-controlled retries.",
    )
    args = parser.parse_args()

    load_env(ROOT / ".env")
    rows = prepare()
    if args.ids:
        wanted = set(args.ids)
        rows = [row for row in rows if row["id"] in wanted]
    if args.run:
        rows = run_fal(rows, args.model, args.limit)
        make_sheet(rows, OUT / "fal_thin_frame_result_sheet.jpg")
        print(OUT / "fal_thin_frame_result_sheet.jpg")
    else:
        print(OUT / "fal_thin_frame_prompts.json")


if __name__ == "__main__":
    main()
