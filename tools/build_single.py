"""Bundle the site into one self-contained HTML file.

Inlines the stylesheet, the script and every local image (as data URIs), so the
page can be opened directly on a phone or tablet, emailed, or shared as a
single file. Fonts still load from Google Fonts when online, with system
fallbacks offline.

Usage: python3 tools/build_single.py [output.html]
"""
import base64
import mimetypes
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / "oritec.html"

html = (ROOT / "index.html").read_text(encoding="utf-8")
css = (ROOT / "assets/css/style.css").read_text(encoding="utf-8")
js = (ROOT / "assets/js/main.js").read_text(encoding="utf-8")


def data_uri(rel):
    path = ROOT / rel
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


html = html.replace('<link rel="stylesheet" href="assets/css/style.css">', f"<style>\n{css}\n</style>")
html = html.replace('<script src="assets/js/main.js" defer></script>', f"<script>\n{js}\n</script>")
html = re.sub(r'(src|href)="(assets/img/[^"]+)"', lambda m: f'{m.group(1)}="{data_uri(m.group(2))}"', html)

missing = re.findall(r'(?:src|href)="assets/[^"]+"', html)
if missing:
    sys.exit(f"Unresolved local assets: {missing}")

out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print(f"Wrote {out} ({out.stat().st_size / 1024:.0f} KB)")
