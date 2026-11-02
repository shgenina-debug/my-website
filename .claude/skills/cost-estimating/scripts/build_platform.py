#!/usr/bin/env python3
"""Embed the item library and the examples into pricing-platform/index.html.

The platform is a single offline HTML file, so the library is copied into it
between the /*LIB*/ ... /*LIB-END*/ and /*EX*/ ... /*EX-END*/ markers.
Run after editing library/library.json or any example:

    python3 .claude/skills/cost-estimating/scripts/build_platform.py
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
HTML = os.path.join(ROOT, "pricing-platform", "index.html")
LIB = os.path.join(HERE, "..", "library", "library.json")
EXAMPLES = {
    "electromechanical": os.path.join(HERE, "..", "examples", "electromechanical_project.json"),
    "maintenance_services": os.path.join(HERE, "..", "examples", "maintenance_services_project.json"),
    "water_networks": os.path.join(ROOT, ".claude", "skills", "water-pricing", "examples", "water_network_project.json"),
}


def compact(obj):
    # "</" would end the inline <script>
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def inject(html, tag, payload):
    pattern = re.compile(r"/\*" + tag + r"\*/.*?/\*" + tag + r"-END\*/", re.S)
    if not pattern.search(html):
        raise SystemExit(f"marker /*{tag}*/ not found in {HTML}")
    return pattern.sub(lambda _: f"/*{tag}*/{payload}/*{tag}-END*/", html, count=1)


def main():
    with open(LIB, encoding="utf-8") as f:
        lib = json.load(f)
    examples = {}
    for key, path in EXAMPLES.items():
        with open(path, encoding="utf-8") as f:
            examples[key] = json.load(f)
    with open(HTML, encoding="utf-8") as f:
        html = f.read()
    html = inject(html, "LIB", compact(lib))
    html = inject(html, "EX", compact(examples))
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"embedded {len(lib['templates'])} templates, {len(lib['resources'])} resources, "
          f"{len(examples)} examples into {os.path.relpath(HTML, ROOT)} ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
