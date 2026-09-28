# -*- coding: utf-8 -*-
import re, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
lines = open(f"{BASE}/noble_docs/text/0017_table.txt", encoding='utf-8').readlines()

US_STATES = set("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC PR VI GU AS MP AE AA AP".split())
CA_PROVINCES = set("ON QC BC AB MB SK NS NB NL PE NT YT NU".split())
STATE_LIKE = US_STATES | CA_PROVINCES

COUNTRIES = set("""Japan Germany Italy Canada France Spain Mexico Australia
Netherlands Belgium Switzerland Austria Poland Korea China Taiwan Singapore India Israel
UAE Qatar Kuwait Bahrain Ireland Sweden Norway Denmark Finland Portugal Greece Turkey
Brazil Argentina Chile Colombia Panama Philippines Thailand Vietnam Indonesia Malaysia
Romania Hungary Slovakia Bulgaria Croatia Slovenia Estonia Latvia Lithuania Ukraine
Egypt Jordan Lebanon Iraq Afghanistan Pakistan Bangladesh Kenya
Nigeria Morocco Tunisia Algeria Luxembourg Iceland Malta Cyprus Bahamas Jamaica""".split())
COUNTRIES_MULTIWORD = ["United Kingdom", "Puerto Rico", "South Korea", "South Africa", "New Zealand",
                        "Costa Rica", "Saudi Arabia", "Sri Lanka", "Czech Republic"]

def is_header_footer(raw):
    s = raw.strip()
    if not s:
        return True
    if s.startswith('Case 26-11369') or 'Filed 08/31/26' in s:
        return True
    if s == 'Creditor Matrix':
        return True
    if s.startswith('CreditorName'):
        return True
    if s.startswith('Noble Supply & Logistics') and 'Page' in s:
        return True
    return False

ZIP_RE = re.compile(r'^\d{5}(-\d{3,4})?$')
CA_POSTAL_RE = re.compile(r'^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$')

def classify_trailing(tokens):
    """tokens: list of (start,text), left to right, columns AFTER the name column.
    Peels country, then zip, then state/province (only if recognized), then city = whatever's left (last token)."""
    toks = tokens[:]
    country = None
    state = None
    zip_ = None
    city = None
    if toks and toks[-1][1] in COUNTRIES:
        country = toks[-1][1]; toks = toks[:-1]
    if toks and (ZIP_RE.match(toks[-1][1]) or CA_POSTAL_RE.match(toks[-1][1])):
        zip_ = toks[-1][1]; toks = toks[:-1]
    if toks and toks[-1][1] in STATE_LIKE:
        state = toks[-1][1]; toks = toks[:-1]
    if toks:
        city = toks[-1][1]; toks = toks[:-1]
    return toks, city, state, zip_, country

def last_token_is_anchor(text):
    if text in COUNTRIES or text in COUNTRIES_MULTIWORD:
        return True
    if ZIP_RE.match(text) or CA_POSTAL_RE.match(text):
        return True
    if text in STATE_LIKE:
        return True
    if 'Address on File' in text or text.strip() == 'Address on File':
        return True
    return False

NAME_COL_MAX = 8

entries = []
current_rows = []

def flush_group(rows):
    if not rows:
        return
    name_parts = []
    anchor_idx = len(rows) - 1
    for (start, text) in rows[anchor_idx]:
        pass
    other_rest = []
    for i, row in enumerate(rows):
        for (start, text) in row:
            if start <= NAME_COL_MAX:
                name_parts.append(text)
            elif i != anchor_idx:
                other_rest.append(text)
    anchor_rest = [(s, t) for (s, t) in rows[anchor_idx] if s > NAME_COL_MAX]
    redacted = any('Address on File' in t for (_, t) in anchor_rest)
    if redacted:
        anchor_rest = [(s, t) for (s, t) in anchor_rest if 'Address on File' not in t]
        remaining, city, state, zip_, country = anchor_rest, None, None, None, None
    else:
        remaining, city, state, zip_, country = classify_trailing(anchor_rest)
    address = ' '.join(other_rest + [t for (_, t) in remaining]).strip()
    name = ' '.join(name_parts).strip()
    if not name and not address and not city:
        return
    entries.append({
        "name": name,
        "address_raw": "Address on File" if redacted else address,
        "city": city,
        "state": state,
        "zip": zip_,
        "country": country,
        "redacted_address": redacted,
    })

for raw_line in lines:
    raw = raw_line.rstrip('\n')
    if is_header_footer(raw):
        continue
    if not raw.strip():
        continue
    tokens = []
    idx = 0
    for piece in re.split(r'( {2,})', raw):
        if piece.strip() == '':
            idx += len(piece)
            continue
        tokens.append((idx, piece.rstrip()))
        idx += len(piece)
    if not tokens:
        continue

    is_anchor_row = last_token_is_anchor(tokens[-1][1])
    # also treat 2-word trailing multi-word countries e.g. "Puerto Rico"
    if not is_anchor_row and len(tokens) >= 2:
        joined2 = tokens[-2][1] + ' ' + tokens[-1][1]
        if joined2 in COUNTRIES_MULTIWORD:
            is_anchor_row = True

    current_rows.append(tokens)
    if is_anchor_row:
        flush_group(current_rows)
        current_rows = []

flush_group(current_rows)

print(f"Parsed {len(entries)} entries")
json.dump(entries, open(f"{BASE}/noble_docs/data/creditor_matrix_raw.json", "w", encoding='utf-8'), indent=1, ensure_ascii=False)
