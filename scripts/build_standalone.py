# -*- coding: utf-8 -*-
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
tpl = open(f"{BASE}/dashboard_template.html", encoding='utf-8').read()
bundle = open(f"{BASE}/noble_docs/data/bundle.json", encoding='utf-8').read()
tpl = tpl.replace('__DATA_JSON__', bundle)

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

out_path = f"{BASE}/gh_pages_build/index.html"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
open(out_path, "w", encoding='utf-8').write(standalone)
print("wrote", out_path, len(standalone.encode('utf-8')), "bytes")
