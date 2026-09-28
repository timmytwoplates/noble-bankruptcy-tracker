import json, re, os

BASE = os.path.dirname(os.path.abspath(__file__)) + "/noble_docs"
d = json.load(open(f"{BASE}/data/docket_all.json", encoding='utf-8'))

ROUTINE_PATTERNS = [
    r'^Certificate of Service',
    r'^Notice of Appearance',
    r'^Entry of Appearance',
    r'Motion for Admission Pro Hac Vice',
    r'Order for Admission Pro Hac Vice',
    r'^Hearing Held',
    r'^Request for Transcript',
    r'^Transcript Regarding Hearing',
    r'PDF File with Audio File Attachment',
    r'^Notice of Agenda',
    r'^Notice of Amended Agenda',
    r'^Receipt of Filing Fee',
    r'^Notice of Change of Hearing',
    r'^Notice of Status Conference',
    r'^Supplemental Certificate of Service',
]

CATEGORY_RULES = [
    ("Sale Process", [r'bidding procedures', r'stalking horse', r'\bsale\b', r'auction', r'assumption and assignment']),
    ("Financing / Cash Collateral", [r'cash collateral', r'cash management', r'dip ', r'adequate protection']),
    ("Financial Reporting", [r'monthly operating report']),
    ("Professional Retention", [r'employ and retain', r'retention', r'employ/retain', r'compensation and reimbursement', r'ordinary course.*professionals']),
    ("Committee", [r'committee of unsecured creditors']),
    ("Claims / Bar Date", [r'proof of claim', r'bar date', r'claims register', r'schedules and statements']),
    ("DLA Dispute", [r'defense logistics agency']),
    ("First Day / Case Admin", [r'first day', r'joint administration', r'automatic stay', r'critical vendor', r'prepetition wages', r'utility', r'taxes and fees', r'insurance', r'redact.*personally identifiable']),
    ("Hearing / Court Admin", [r'agenda of matters', r'omnibus hearing', r'status conference']),
    ("Employee / KERP", [r'key employee retention', r'key executive incentive', r'kerp', r'keip']),
]

def categorize(title):
    t = title.lower()
    for pat in ROUTINE_PATTERNS:
        if re.search(pat, title, re.IGNORECASE):
            return "Routine", False
    for cat, pats in CATEGORY_RULES:
        for p in pats:
            if re.search(p, t):
                return cat, True
    return "Other / General", True

for e in d:
    cat, substantive = categorize(e['title'])
    e['category'] = cat
    e['substantive'] = substantive

with open(f"{BASE}/data/docket_categorized.json", "w", encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

from collections import Counter
c = Counter(e['category'] for e in d)
for k, v in sorted(c.items(), key=lambda x: -x[1]):
    print(f"{k}: {v}")
print("TOTAL:", len(d))
print("Substantive:", sum(1 for e in d if e['substantive']))
print("Routine:", sum(1 for e in d if not e['substantive']))
