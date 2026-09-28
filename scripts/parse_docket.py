import re, json, html, os

BASE = os.path.dirname(os.path.abspath(__file__)) + "/noble_docs"

def strip_tags(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def parse_file(path, source_list):
    text = open(path, encoding='utf-8', errors='ignore').read()
    cards = text.split('<!-- begin court document card -->')
    out = []
    for card in cards[1:]:
        card = card.split('<!-- end court document card -->')[0]
        m = re.search(r'court-docket">\s*(\d+)', card)
        if not m:
            continue
        num = m.group(1)
        href_m = re.search(r'Document Name:\s*</strong><a href="([^"]+)"', card)
        href = href_m.group(1) if href_m else None
        name_m = re.search(r'Document Name:\s*</strong><a[^>]*>(.*?)</a></p>', card, re.DOTALL)
        name = strip_tags(name_m.group(1)) if name_m else None
        date_m = re.search(r'Date Filed:\s*</strong><span>([^<]+)</span>', card)
        date = date_m.group(1).strip() if date_m else None
        rel_m = re.search(r'Related Documents.*?<p>\s*(.*?)</p>', card, re.DOTALL)
        related = []
        if rel_m:
            related = re.findall(r'\d{4}', rel_m.group(1))
        out.append({
            "docket_no": num,
            "pdf_href": href,
            "title": name,
            "date_filed": date,
            "related": related,
            "source_list": source_list,
        })
    return out

all_entries = []
for p, src in [
    (f"{BASE}/html/docket_p1.html", "main"),
    (f"{BASE}/html/docket_p2.html", "main"),
    (f"{BASE}/html/docket_p3.html", "main"),
]:
    all_entries.extend(parse_file(p, src))

seen = set()
deduped = []
for e in all_entries:
    key = (e['docket_no'], e['pdf_href'])
    if key in seen:
        continue
    seen.add(key)
    deduped.append(e)

deduped.sort(key=lambda e: int(e['docket_no']))

os.makedirs(f"{BASE}/data", exist_ok=True)
with open(f"{BASE}/data/docket_all.json", "w", encoding='utf-8') as f:
    json.dump(deduped, f, indent=2)

print(f"Parsed {len(deduped)} unique entries (raw {len(all_entries)})")
print("First:", deduped[0])
print("Last:", deduped[-1])
