#!/usr/bin/env python3
"""gaming_hero_4k skill renderer — HTML template + Playwright → PNG

Usage:
  python3 render.py <inputs.json> <output.png>

inputs.json schema: see schema.json
"""
import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright

SKILL_DIR = Path(__file__).parent

DEFAULTS = {
    "brand_color": "#EE1111",
    "badge_color": "#1E90FF",
    "canvas_size": 1024,
    "badge_text": "",
    "spec_line_1": "",
    "spec_line_2": "",
}

def build_html(inputs: dict) -> str:
    # Merge defaults
    ctx = {**DEFAULTS, **inputs}
    canvas = int(ctx["canvas_size"])
    ctx["canvas_px"] = canvas

    # Dynamic sizing based on canvas
    scale = canvas / 1024
    ctx["hero_number_font_size"] = int(220 * scale)
    ctx["brand_font_size"] = int(64 * scale)
    ctx["badge_font_size"] = int(52 * scale)
    ctx["spec_font_size"] = int(44 * scale)
    ctx["badge_top"] = 26
    ctx["spec_top"] = 22

    # Conditional HTML fragments
    if ctx.get("badge_text"):
        ctx["badge_html"] = f'<div class="badge">{ctx["badge_text"]}</div>'
    else:
        ctx["badge_html"] = ""

    spec_lines = []
    if ctx.get("spec_line_1"):
        spec_lines.append(f'<div class="line">{ctx["spec_line_1"]}</div>')
    if ctx.get("spec_line_2"):
        spec_lines.append(f'<div class="line">{ctx["spec_line_2"]}</div>')
    if spec_lines:
        ctx["spec_right_html"] = '<div class="spec-right">' + "".join(spec_lines) + '</div>'
    else:
        ctx["spec_right_html"] = ""

    template = (SKILL_DIR / "template.html").read_text()

    # Resolve background: inline local files as base64 data URI (Playwright blocks file://)
    import base64, mimetypes
    bg = ctx["background_image_url"]
    if bg.startswith(("http://", "https://", "data:")):
        pass  # keep as-is
    else:
        # Local path → read into data URI
        p = Path(bg.replace("file://", "", 1)).resolve()
        mime, _ = mimetypes.guess_type(str(p))
        mime = mime or "image/jpeg"
        b64 = base64.b64encode(p.read_bytes()).decode("ascii")
        bg = f"data:{mime};base64,{b64}"
    ctx["background_image_url"] = bg

    # Simple {{var}} substitution
    out = template
    for k, v in ctx.items():
        out = out.replace("{{" + k + "}}", str(v))
    return out


async def render(inputs_path: str, output_path: str):
    inputs = json.loads(Path(inputs_path).read_text())
    html = build_html(inputs)
    canvas = int(inputs.get("canvas_size", 1024))

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": canvas, "height": canvas}, device_scale_factor=1)
        page = await ctx.new_page()
        await page.set_content(html, wait_until="networkidle")
        # Make sure fonts loaded
        await page.evaluate("document.fonts.ready")
        await page.screenshot(path=output_path, full_page=False, omit_background=False)
        await browser.close()

    print(f"✅ Rendered → {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    asyncio.run(render(sys.argv[1], sys.argv[2]))
