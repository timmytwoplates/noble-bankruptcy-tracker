# -*- coding: utf-8 -*-
"""
Rebuilds index.html from template/dashboard_template.html + the current
contents of data/*.json (via build_bundle.py). Run this after ANY change to a
file in data/ -- index.html is a static snapshot with the data baked in, it
does not read data/*.json at page-load time.

Usage: python scripts/build_standalone.py
"""
import json, os
from build_bundle import build_bundle

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(REPO_ROOT, "template", "dashboard_template.html")
OUT_PATH = os.path.join(REPO_ROOT, "index.html")


def main():
    tpl = open(TEMPLATE_PATH, encoding="utf-8").read()
    bundle = build_bundle()
    bundle_json = json.dumps(bundle, ensure_ascii=False, separators=(",", ":"))
    tpl = tpl.replace("__DATA_JSON__", bundle_json)

    marker = "</style>"
    idx = tpl.index(marker) + len(marker)
    head_bits = tpl[:idx]
    body_bits = tpl[idx:]

    standalone = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head_bits}
</head>
<body>
{body_bits}
</body>
</html>
"""
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(standalone)
    print(f"wrote {OUT_PATH} ({len(standalone.encode('utf-8'))} bytes)")


if __name__ == "__main__":
    main()
