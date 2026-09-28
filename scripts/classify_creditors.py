# -*- coding: utf-8 -*-
import json, re, os, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
mat = json.load(open(f"{BASE}/noble_docs/data/creditor_matrix_raw.json", encoding='utf-8'))
top = json.load(open(f"{BASE}/noble_docs/data/top_creditors.json", encoding='utf-8'))
vs = json.load(open(f"{BASE}/noble_docs/data/vendors_systems.json", encoding='utf-8'))
util_names = {p['provider'].lower() for p in vs['telecom_utility_vendors']['providers']}
sw_names = {v['name'].lower() for v in vs['software_vendors']['vendors']}

def norm(s):
    s = s.lower()
    s = re.sub(r'[.,()]', '', s)
    s = re.sub(r'\b(llc|inc|corp|corporation|co|company|ltd|dba|gmbh|lp|llp|pllc|usa)\b', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

top_by_norm = {norm(c['name']): c for c in top['creditors']}

# One-off aliases for the 2 top-30 names whose punctuation/spacing differs enough
# from the matrix listing that normalized exact-match fails (verified by hand,
# not a general fuzzy fallback -- a substring fallback wrongly merged unrelated
# "Mountain Horse Solutions" into "Mountain Horse, LLC"'s $15.5M claim, so we
# don't do that anymore).
MATRIX_TO_TOP30_ALIAS = {
    "ryo enterprisecoltd": "ryo enterprise",
    "s&b wg henschen": "s&b wg henschen abound",
}

def find_top_hit(entry_name):
    n = norm(entry_name)
    hit = top_by_norm.get(n)
    if hit:
        return hit
    alias = MATRIX_TO_TOP30_ALIAS.get(n)
    if alias:
        return top_by_norm.get(alias)
    return None

BUSINESS_SUFFIX_RE = re.compile(
    r'\b(LLC|Inc|Corp|Corporation|Co|Company|Ltd|Limited|GmbH|LP|LLP|PLLC|PC|Group|Solutions|Systems|'
    r'Technologies|Enterprises|Industries|Holdings|Partners|Associates|International|Services|Supply|'
    r'Products|Manufacturing|Consulting|Labs|Laboratories|Institute|Foundation|Agency|Squadron|Center|'
    r'Corporation|SA|SRL|BV|Pty|AG|KG|SPA)\b', re.IGNORECASE)

GOV_PATTERNS = [
    r'\bUnited States\b', r'\bU\.?S\.?\b.*\b(Dept|Department|Government|Treasury)\b', r'\bDept\.? of\b',
    r'\bDepartment of\b', r'\bCity of\b', r'\bCounty of\b', r'\bState of\b', r'\bTownship\b',
    r'\bIRS\b', r'\bInternal Revenue\b', r'\bContracting Squadron\b', r'\bAir Force\b', r'\bArmy\b',
    r'\bNavy\b', r'\bMarine Corps\b', r'\bComptroller\b', r'\bMunicipal', r'\bCommonwealth of\b',
    r'\bBureau of\b', r'\bClerk of\b', r'\bDefense Logistics Agency\b', r'\bGeneral Services Admin',
    r'\bCourt\b', r'\bU\.S\. Trustee\b', r'\bSecretary of\b', r'\bFederal \b', r'\bPublic Works\b',
    r'\bSocial Security\b', r'\bDMV\b', r'\bRevenue Service\b', r'\bTax Commission\b', r'\bTax Collector\b',
]
UTILITY_PATTERNS = [r'\bElectric\b', r'\bPower (Co|Company|Corp)\b', r'\bEnergy\b', r'\bGas (Co|Company|Utility)\b',
                     r'\bWater (Co|Company|Works|District|Authority)\b', r'\bUtilit(y|ies)\b', r'\bCooperative\b.*Electric']
INSURANCE_PATTERNS = [r'\bInsurance\b', r'\bAssurance\b', r'\bUnderwriters\b']
FINANCIAL_PATTERNS = [r'\bBank\b', r'\bCapital LLC\b', r'\bFinancial\b', r'\bCredit Union\b', r'\bLeasing\b']
LEGAL_PATTERNS = [r'\bLLP\b', r'\bLaw (Firm|Group|Office)\b', r'\bAttorneys\b', r'\b(P\.?C\.?)$']
STAFFING_PATTERNS = [r'\bStaffing\b', r'\bRecruiting\b', r'\bPersonnel\b', r'\bWorkforce\b']
FREIGHT_PATTERNS = [r'\bFreight\b', r'\bLogistics\b', r'\bTrucking\b', r'\bCargo\b', r'\bForwarding\b',
                     r'\bCourier\b', r'\bShipping\b', r'\bExpress (Inc|LLC|Freight)\b']
CONSTRUCTION_PATTERNS = [r'\bConstruction\b', r'\bContracting\b', r'\bBuilders\b', r'\bRoofing\b',
                          r'\bPlumbing\b', r'\bHVAC\b', r'\bKensetsu\b', r'\bCivil Corp\b', r'\bElectrical (Co|Contractors)\b',
                          r'\bWeatherproofing\b', r'\bBuilding Solutions\b']
TELECOM_PATTERNS = [r'\bTelecom\b', r'\bCommunications\b', r'\bWireless\b', r'\bBroadband\b']

def any_match(patterns, text):
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)

PERSON_RE = re.compile(r"^[A-Z][a-zA-Z'-]+(?:\s[A-Z]\.?)?(?:\s[A-Z][a-zA-Z'-]+){1,2}$")

def classify(name, redacted):
    nlow = name.lower()
    if nlow in util_names:
        return "Utility"
    if nlow in sw_names:
        return "Software / Technology"
    if any_match(GOV_PATTERNS, name):
        return "Government / Military"
    if any_match(UTILITY_PATTERNS, name):
        return "Utility"
    if any_match(TELECOM_PATTERNS, name):
        return "Telecom"
    if any_match(INSURANCE_PATTERNS, name):
        return "Insurance"
    if any_match(FINANCIAL_PATTERNS, name):
        return "Financial / Banking"
    if any_match(LEGAL_PATTERNS, name):
        return "Legal / Professional Services"
    if any_match(STAFFING_PATTERNS, name):
        return "Staffing / HR Services"
    if any_match(FREIGHT_PATTERNS, name):
        return "Freight / Logistics"
    if any_match(CONSTRUCTION_PATTERNS, name):
        return "Construction / Facilities"
    has_suffix = bool(BUSINESS_SUFFIX_RE.search(name))
    # "Address on File" is how Noble redacted PII for individuals under the PII-redaction
    # order (Docket #6/#175/#207) -- it's the strongest signal we have that a row is a person,
    # not a business. Bare name-pattern matching alone (e.g. "Ace Hardware", "Accuspec Packaging")
    # produces too many false positives on businesses that just lack an LLC/Inc suffix in the
    # matrix, so we don't classify as Individual from name shape alone anymore.
    if redacted and not has_suffix and len(name.split()) <= 4 and not re.search(r'\d', name):
        return "Individual"
    return "Trade Vendor / Supplier"

def maps_url(e):
    parts = [e['name']]
    if e.get('address_raw') and e['address_raw'] != 'Address on File':
        parts.append(e['address_raw'])
    if e.get('city'):
        parts.append(e['city'])
    if e.get('state'):
        parts.append(e['state'])
    if e.get('zip'):
        parts.append(e['zip'])
    if e.get('country'):
        parts.append(e['country'])
    q = ', '.join(parts)
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(q)

# Known official websites we're confident about (curated, not guessed per-entry)
KNOWN_SITES = {
    "raytheon company": "https://www.rtx.com",
    "northrop grumman systems corp": "https://www.northropgrumman.com",
    "northrop grumman systems corporation": "https://www.northropgrumman.com",
    "l3 harris global technologies": "https://www.l3harris.com",
    "persistent systems": "https://www.persistentsystems.com",
    "bluehalo": "https://www.bluehalo.com",
    "salesforcecom": "https://www.salesforce.com",
    "microsoft corporation": "https://www.microsoft.com",
    "docusign": "https://www.docusign.com",
    "zoom video communications": "https://www.zoom.us",
    "hubspot": "https://www.hubspot.com",
    "concur technologies": "https://www.concur.com",
    "celigo": "https://www.celigo.com",
    "oracle america": "https://www.oracle.com",
    "adp screening and selection": "https://www.adp.com",
}

out = []
matched_ranks = set()
for e in mat:
    top_hit = find_top_hit(e['name'])
    amount = top_hit['amount_usd'] if top_hit else 0
    rank = top_hit['rank'] if top_hit else None
    if top_hit:
        matched_ranks.add(top_hit['rank'])
    redacted = bool(e.get('redacted_address'))
    ctype = classify(e['name'], redacted)
    if top_hit and top_hit.get('likely_type'):
        # prefer our researched top-30 type label, mapped to closest bucket for consistency, but keep original detail in notes
        display_type = top_hit['likely_type']
    else:
        display_type = ctype
    site = KNOWN_SITES.get(norm(e['name']))
    out.append({
        "name": e['name'],
        "amount_usd": amount,
        "rank_in_top30": rank,
        "type": ctype,
        "type_detail": display_type,
        "city": e.get('city'),
        "state": e.get('state'),
        "zip": e.get('zip'),
        "country": e.get('country'),
        "address_raw": e.get('address_raw'),
        "redacted_address": redacted,
        "maps_search_url": maps_url(e),
        "official_website": site,
        "top30_notes": top_hit.get('notes') if top_hit else None,
    })

missing = [c for c in top['creditors'] if c['rank'] not in matched_ranks]
print("total merged entries:", len(out))
print("top30 matched:", len(matched_ranks), "of 30; missing:", [c['name'] for c in missing])

from collections import Counter
print(Counter(o['type'] for o in out).most_common(20))

json.dump({
    "source_note": "Full creditor mailing list from Docket #17 (Redacted Creditor Matrix, filed 09/25/26), merged with dollar amounts from the Top-30-Largest-Unsecured-Claims list (Docket #1). Everyone not on that Top-30 list holds an amount of $0 here — not because they're owed nothing, but because Noble was only required to disclose amounts for its 30 largest unsecured claims; the true amount for the rest isn't in any filing we've reviewed. 'Type' is an automated best-effort classification from the company/person name and known vendor lists, not a category the court filings themselves assign — expect some misclassifications, especially for generically-named companies. Addresses (and therefore map links) are the mailing/notice address on file with the court, which is sometimes a payment/AP address rather than a physical storefront.",
    "generated_note": "Map links point to a Google Maps search for the creditor's name and exact notice address — for a franchise or chain, this generally resolves to the specific location tied to that address rather than the brand's corporate site. 'Official website' is populated only for a small set of creditors we could confidently identify by name; we did not attempt to verify a website for every entry.",
    "creditors": out,
}, open(f"{BASE}/noble_docs/data/creditors_full.json", "w", encoding='utf-8'), indent=1, ensure_ascii=False)
