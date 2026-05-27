#!/usr/bin/env python3
import shutil
from pathlib import Path

ROOT = Path("/Users/cc/Desktop/photo_show")
OUT = ROOT / "output/emag_banner_generation_tests"
BANNER_REF_DIR = Path("/Users/cc/Desktop/banner")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    
    # Define mappings of style -> reference filename -> local copied filename -> generated filename
    mappings = [
        {
            "style": "Glassmorphism",
            "ref_file": "img_v3_02120_86e9c5a3-a999-4fd0-ad22-bb34544737bg.jpg",
            "local_ref": "ref_template_glassmorphism.jpg",
            "gen_file": "ref_banner_glassmorphism_img2img_ai.jpg",
            "desc": "Frosted glass container floating on electric violet and deep navy gradients with cyan accents."
        },
        {
            "style": "Premium Dark",
            "ref_file": "img_v3_02120_8765ee8f-75a8-4e47-8e08-ca536a39719g.jpg",
            "local_ref": "ref_template_premium_dark.jpg",
            "gen_file": "ref_banner_premium_dark_img2img_ai.jpg",
            "desc": "Brushed dark tech metal with glowing gold and amber horizontal panel lines."
        },
        {
            "style": "Organic Wood & Stone",
            "ref_file": "img_v3_02120_5cac50f6-f295-40f4-98b6-5f2764bcbddg.jpg",
            "local_ref": "ref_template_organic_wood.jpg",
            "gen_file": "ref_banner_organic_wood_img2img_ai.jpg",
            "desc": "Waterworn beige travertine stone slab against clean teak wood, warm shadow overlays."
        }
    ]
    
    # Copy files
    for m in mappings:
        src = BANNER_REF_DIR / m["ref_file"]
        dst = OUT / m["local_ref"]
        if src.exists():
            shutil.copy2(src, dst)
            print(f"Copied template: {src.name} -> {dst.name}")
        else:
            print(f"Warning: template not found: {src}")
            
    # Generate HTML content
    html_lines = [
        "<!doctype html>",
        "<html>",
        "<head>",
        "  <meta charset='utf-8'>",
        "  <meta name='viewport' content='width=device-width, initial-scale=1'>",
        "  <title>eMAG Banners - Reference Template vs AI Generated</title>",
        "  <style>",
        "    body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #1e293b; padding: 40px 20px; }",
        "    main { max-width: 1200px; margin: 0 auto; }",
        "    header { text-align: center; margin-bottom: 50px; }",
        "    h1 { font-size: 32px; color: #0f172a; margin-bottom: 10px; font-weight: 800; letter-spacing: -0.5px; }",
        "    header p { color: #64748b; font-size: 18px; margin: 0; }",
        "    .section { background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); border: 1px solid #e2e8f0; padding: 32px; margin-bottom: 40px; }",
        "    h2 { font-size: 24px; color: #0f172a; margin-top: 0; margin-bottom: 8px; font-weight: 700; }",
        "    .desc { color: #64748b; font-size: 15px; margin-bottom: 24px; line-height: 1.5; }",
        "    .comparison-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }",
        "    @media (max-width: 900px) { .comparison-grid { grid-template-columns: 1fr; } }",
        "    .card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; }",
        "    .card-title { font-weight: 700; font-size: 14px; text-transform: uppercase; letter-spacing: 0.8px; color: #64748b; margin-bottom: 12px; }",
        "    img { width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); display: block; border: 1px solid #e2e8f0; }",
        "    .tag { display: inline-block; padding: 4px 10px; font-size: 12px; font-weight: 700; border-radius: 6px; text-transform: uppercase; margin-bottom: 12px; }",
        "    .tag-ref { background: #e0f2fe; color: #0369a1; }",
        "    .tag-gen { background: #dcfce7; color: #15803d; }",
        "  </style>",
        "</head>",
        "<body>",
        "  <main>",
        "    <header>",
        "      <h1>eMAG Banners: Stability Performance</h1>",
        "      <p>Comparison gallery showing reference design templates on the left and stable, text-injected final AI banners on the right.</p>",
        "    </header>"
    ]
    
    for m in mappings:
        html_lines.append(f"""
    <div class="section">
      <h2>Style: {m['style']}</h2>
      <div class="desc">{m['desc']}</div>
      <div class="comparison-grid">
        <div class="card">
          <div class="tag tag-ref">Original Desktop Reference Template</div>
          <img src="{m['local_ref']}" alt="{m['style']} Reference Template">
        </div>
        <div class="card">
          <div class="tag tag-gen">Generated Stabilized Banner (EXCITAT)</div>
          <img src="{m['gen_file']}" alt="{m['style']} AI Generated">
        </div>
      </div>
    </div>
        """)
        
    html_lines.append("""
  </main>
</body>
</html>
    """)
    
    (OUT / "banners_preview.html").write_text("\n".join(html_lines), encoding="utf-8")
    print(f"Generated banners preview HTML page: {OUT / 'banners_preview.html'}")

if __name__ == "__main__":
    main()
