"""Bundle the site into self-contained HTML files, one per language.

Inlines the stylesheet, the script and every local image (as data URIs), so
each page can be opened directly on a phone or tablet, emailed, or shared as
a single file. The language switch links the two files to each other when
they sit in the same folder. Fonts still load from Google Fonts when online,
with system fallbacks offline.

Usage: python3 tools/build_single.py [output-folder]
Writes almasia.html (English) and almasia-ar.html (Arabic).
"""
import base64
import mimetypes
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist"

css = (ROOT / "assets/css/style.css").read_text(encoding="utf-8")
js = (ROOT / "assets/js/main.js").read_text(encoding="utf-8")

PAGES = [
    # source page, asset prefix used in it, output name, language-switch target
    ("index.html", "", "almasia.html", ("ar/index.html", "almasia-ar.html")),
    ("ar/index.html", "../", "almasia-ar.html", ("../index.html", "almasia.html")),
]


def data_uri(rel):
    path = ROOT / rel
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


out_dir.mkdir(parents=True, exist_ok=True)
for src, prefix, name, (switch_from, switch_to) in PAGES:
    html = (ROOT / src).read_text(encoding="utf-8")
    html = html.replace(f'<link rel="stylesheet" href="{prefix}assets/css/style.css">', f"<style>\n{css}\n</style>")
    html = html.replace(f'<script src="{prefix}assets/js/main.js" defer></script>', f"<script>\n{js}\n</script>")
    html = re.sub(rf'(src|href)="{re.escape(prefix)}(assets/img/[^"]+)"',
                  lambda m: f'{m.group(1)}="{data_uri(m.group(2))}"', html)
    html = html.replace(f'class="lang-switch" href="{switch_from}"', f'class="lang-switch" href="{switch_to}"')

    missing = re.findall(r'(?:src|href)="(?:\.\./)?assets/[^"]+"', html)
    if missing:
        sys.exit(f"{src}: unresolved local assets: {missing}")

    out = out_dir / name
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size / 1024:.0f} KB)")
