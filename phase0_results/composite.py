#!/usr/bin/env python3
"""Pillow 合成 v2 — 支持 bbox 精准 resize + reposition

Usage:
  python3 composite.py <scene> <fg> <mask> <out> [feather_px] [bbox_x1,y1,x2,y2]

bbox 可选。传了 bbox 时，把产品 resize 到 bbox 尺寸并粘贴到 bbox 位置；
不传则保持 scene 尺寸整张覆盖（旧行为）。
"""
import sys
from PIL import Image, ImageFilter

def composite(scene_path, fg_path, mask_path, out_path, feather_px=4, bbox=None):
    scene = Image.open(scene_path).convert("RGBA")
    fg = Image.open(fg_path).convert("RGBA")
    mask = Image.open(mask_path).convert("L")

    sw, sh = scene.size

    if bbox is not None:
        # bbox 模式: 把 fg 等比缩放到 bbox 内
        x1, y1, x2, y2 = bbox
        bbox_w, bbox_h = x2 - x1, y2 - y1

        # 裁掉 fg 的透明外边（基于 mask 的紧致 bbox），避免留白
        fg_bbox = mask.getbbox() or (0, 0, *fg.size)
        fg_cropped = fg.crop(fg_bbox)
        mask_cropped = mask.crop(fg_bbox)

        # 等比缩放到 bbox 内（保持 aspect ratio）
        src_w, src_h = fg_cropped.size
        scale = min(bbox_w / src_w, bbox_h / src_h)
        new_w, new_h = int(src_w * scale), int(src_h * scale)

        fg_resized = fg_cropped.resize((new_w, new_h), Image.LANCZOS)
        mask_resized = mask_cropped.resize((new_w, new_h), Image.LANCZOS)

        # 居中在 bbox 里
        paste_x = x1 + (bbox_w - new_w) // 2
        paste_y = y1 + (bbox_h - new_h) // 2

        # 羽化 mask
        if feather_px > 0:
            mask_resized = mask_resized.filter(ImageFilter.GaussianBlur(radius=feather_px))

        # 构造全尺寸 fg 和 mask（周围透明）
        full_fg = Image.new("RGBA", scene.size, (0, 0, 0, 0))
        full_mask = Image.new("L", scene.size, 0)
        full_fg.paste(fg_resized, (paste_x, paste_y))
        full_mask.paste(mask_resized, (paste_x, paste_y))

        result = Image.composite(full_fg, scene, full_mask)
        print(f"✅ Composited (bbox {bbox} → paste ({paste_x},{paste_y}) size {new_w}x{new_h}) → {out_path}")
    else:
        # 旧行为
        if fg.size != (sw, sh):
            fg = fg.resize((sw, sh), Image.LANCZOS)
        if mask.size != (sw, sh):
            mask = mask.resize((sw, sh), Image.LANCZOS)
        if feather_px > 0:
            mask = mask.filter(ImageFilter.GaussianBlur(radius=feather_px))
        result = Image.composite(fg, scene, mask)
        print(f"✅ Composited (full-size) → {out_path}")

    result.convert("RGB").save(out_path, "JPEG", quality=92)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(1)
    feather = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    bbox = None
    if len(sys.argv) > 6:
        bbox = tuple(int(x) for x in sys.argv[6].split(","))
        assert len(bbox) == 4
    composite(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], feather, bbox)
