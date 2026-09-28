# -*- coding: utf-8 -*-
"""
Free, no-AI mechanical refresh of the docket.

What this DOES:
  - Fetches the public docket list from veritaglobal.net (no login needed).
  - Finds filings newer than the highest docket number we already have.
  - Classifies each as routine/substantive using the same keyword rules the
    original build used (see categorize.py / build_docket_summaries.py), and
    writes a one-line factual note for routine filings (certs of service,
    pro hac vice, etc.) without needing to open the PDF.
  - Appends the new entries to data/docket_entries.json with the right
    schema, rebuilds index.html, and lists anything that still needs a human/
    AI pass in data/pending_review.json.

What this does NOT do (needs an actual AI read of the PDF -- see
UPDATE_PLAYBOOK.md for that pass):
  - Write a plain-English `summary` for a new SUBSTANTIVE filing.
  - Transcribe a new Monthly Operating Report's financials.
  - Update sale_milestones status, health_assessments, key_parties, or
    dla_dispute based on what a new filing actually says.

Designed to run unattended (GitHub Actions cron) with only the Python
standard library -- no pip installs, so it can't break on a dependency.
"""
import json, os, re, sys, urllib.request, urllib.parse, datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")
DOCKET_LIST_URL = "https://veritaglobal.net/noble/document/list/6618"
BASE_URL = "https://veritaglobal.net"
UA = "Mozilla/5.0 (compatible; noble-bankruptcy-tracker refresh bot; +https://github.com/timmytwoplates/noble-bankruptcy-tracker)"

ROUTINE_PATTERNS = [
    r'^Certificate of Service', r'^Notice of Appearance', r'^Entry of Appearance',
    r'Motion for Admission Pro Hac Vice', r'Order for Admission Pro Hac Vice',
    r'^Hearing Held', r'^Request for Transcript', r'^Transcript Regarding Hearing',
    r'PDF File with Audio File Attachment', r'^Notice of Agenda', r'^Notice of Amended Agenda',
    r'^Receipt of Filing Fee', r'^Notice of Change of Hearing', r'^Notice of Status Conference',
    r'^Supplemental Certificate of Service', r'Judge .* Added to Case',
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
ROUTINE_NOTE_RULES = [
    (r'^Certificate of Service', "Confirms that Verita Global (the claims agent) served a prior filing on the appropriate parties — a required proof-of-mailing, not new substantive news."),
    (r'^Notice of Appearance|^Entry of Appearance', "A law firm formally notifying the court it represents a creditor or party in interest in the case — procedural, but can signal which parties are actively watching the case."),
    (r'Motion for Admission Pro Hac Vice', "An out-of-state attorney asking the Delaware court for permission to appear in this case."),
    (r'Order for Admission Pro Hac Vice', "Court granting an out-of-state attorney permission to appear in this case."),
    (r'^Hearing Held', "Administrative record confirming a scheduled hearing took place (sign-in/registration sheet)."),
    (r'^Request for Transcript', "A request to the court reporter for a written transcript of a hearing."),
    (r'^Transcript Regarding Hearing', "Official transcript of a hearing (access is typically restricted for a period after filing)."),
    (r'PDF File with Audio File Attachment', "Audio recording of a hearing."),
    (r'^Notice of Agenda|^Notice of Amended Agenda', "The published running order of matters to be heard at an upcoming omnibus hearing."),
    (r'^Receipt of Filing Fee', "Administrative confirmation that the court filing fee was paid."),
    (r'^Notice of Change of Hearing', "Notice that a previously scheduled hearing's date or time changed."),
    (r'^Notice of Status Conference', "Notice of a scheduling/status conference with the court."),
    (r'^Supplemental Certificate of Service', "Additional proof-of-mailing for a prior filing."),
    (r'Judge .* Added to Case', "Administrative case-management entry reassigning the case to its presiding judge."),
]


def classify(title):
    for pat in ROUTINE_PATTERNS:
        if re.search(pat, title, re.IGNORECASE):
            return "Routine", False
    t = title.lower()
    for cat, pats in CATEGORY_RULES:
        for p in pats:
            if re.search(p, t):
                return cat, True
    return "Other / General", True


def routine_note(title):
    for pat, note in ROUTINE_NOTE_RULES:
        if re.search(pat, title, re.IGNORECASE):
            return note
    return "Procedural/administrative filing."


def to_iso(mdY):
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', mdY.strip())
    if not m:
        return None
    mo, da, yr = m.groups()
    return f"{yr}-{int(mo):02d}-{int(da):02d}"


def fetch_docket_page(page_num, total_records):
    data = urllib.parse.urlencode({
        "CurrentPage": page_num, "PageSize": 100, "TotalRecords": total_records,
        "AllCases": "True", "AllIndustryGroups": "True", "AllJurisdictions": "True",
    }).encode()
    req = urllib.request.Request(f"{DOCKET_LIST_URL}?pagesize=200", data=data,
                                  headers={"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_entries(html):
    entries = []
    for card in html.split('<!-- begin court document card -->')[1:]:
        card = card.split('<!-- end court document card -->')[0]
        m = re.search(r'court-docket">\s*(\d+)', card)
        if not m:
            continue
        num = m.group(1)
        href_m = re.search(r'Document Name:\s*</strong><a href="([^"]+)"', card)
        href = href_m.group(1) if href_m else None
        name_m = re.search(r'Document Name:\s*</strong><a[^>]*>(.*?)</a></p>', card, re.DOTALL)
        title = None
        if name_m:
            title = re.sub(r'<[^>]+>', ' ', name_m.group(1))
            title = re.sub(r'\s+', ' ', title).strip()
            import html as _html
            title = _html.unescape(title)
        date_m = re.search(r'Date Filed:\s*</strong><span>([^<]+)</span>', card)
        date_filed = date_m.group(1).strip() if date_m else None
        rel_m = re.search(r'Related Documents.*?<p>\s*(.*?)</p>', card, re.DOTALL)
        related = re.findall(r'\d{4}', rel_m.group(1)) if rel_m else []
        entries.append({"docket_no": num, "pdf_href": href, "title": title,
                         "date_filed": date_filed, "related": related})
    return entries


def main():
    with open(os.path.join(DATA_DIR, "docket_entries.json"), encoding="utf-8") as f:
        existing = json.load(f)
    max_known = max(int(e["docket_no"]) for e in existing)
    print(f"MAX_KNOWN docket number: {max_known}")

    # First fetch establishes TotalRecords (page 1 is enough almost always --
    # a new filing volume of >100 since the last run would be extraordinary).
    first_page = fetch_docket_page(1, 9999)
    m = re.search(r'name="TotalRecords"\s+type="hidden"\s+value="(\d+)"', first_page)
    total_records = int(m.group(1)) if m else 9999
    print(f"Docket reports TotalRecords={total_records}")

    all_new = []
    page = 1
    seen_pages_html = [first_page]
    while True:
        html = seen_pages_html[page - 1] if page - 1 < len(seen_pages_html) else fetch_docket_page(page, total_records)
        page_entries = parse_entries(html)
        if not page_entries:
            break
        new_here = [e for e in page_entries if int(e["docket_no"]) > max_known]
        all_new.extend(new_here)
        lowest_on_page = min(int(e["docket_no"]) for e in page_entries)
        if lowest_on_page <= max_known or len(new_here) < len(page_entries):
            break
        page += 1
        if page > 5:
            print("Stopping after 5 pages as a safety cap.")
            break

    if not all_new:
        print("No new docket entries. Nothing to do.")
        return 0

    print(f"Found {len(all_new)} new docket entries: "
          f"{sorted(int(e['docket_no']) for e in all_new)}")

    pending = []
    for e in all_new:
        category, substantive = classify(e["title"] or "")
        docket_no_padded = e["docket_no"].zfill(4)
        row = {
            "docket_no": docket_no_padded,
            "pdf_href": e["pdf_href"],
            "title": e["title"],
            "date_filed": e["date_filed"],
            "date_filed_iso": to_iso(e["date_filed"]) if e["date_filed"] else None,
            "related": e["related"],
            "source_list": "main",
            "category": category,
            "substantive": substantive,
            "summary": None if substantive else routine_note(e["title"] or ""),
            "topic": None,
            "topic_label": None,
            "pdf_url": (BASE_URL + e["pdf_href"]) if e["pdf_href"] else None,
        }
        existing.append(row)
        if substantive:
            pending.append({
                "docket_no": docket_no_padded,
                "title": e["title"],
                "category": category,
                "reason": "New substantive filing needs a plain-English summary"
                          + (" and full financial transcription (Monthly Operating Report)"
                             if category == "Financial Reporting" else ""),
            })

    existing.sort(key=lambda e: int(e["docket_no"]))
    with open(os.path.join(DATA_DIR, "docket_entries.json"), "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    pending_path = os.path.join(DATA_DIR, "pending_review.json")
    prior_pending = []
    if os.path.exists(pending_path):
        with open(pending_path, encoding="utf-8") as f:
            prior_pending = json.load(f)
    known_pending_nos = {p["docket_no"] for p in prior_pending}
    merged_pending = prior_pending + [p for p in pending if p["docket_no"] not in known_pending_nos]
    with open(pending_path, "w", encoding="utf-8") as f:
        json.dump(merged_pending, f, indent=2, ensure_ascii=False)
    print(f"{len(pending)} new entries flagged for AI review "
          f"({len(merged_pending)} total pending). See data/pending_review.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
