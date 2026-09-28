# -*- coding: utf-8 -*-
import json, re, os

BASE = os.path.dirname(os.path.abspath(__file__)) + "/noble_docs"
d = json.load(open(f"{BASE}/data/docket_categorized.json", encoding='utf-8'))
by_num = {e['docket_no']: e for e in d}

# ---- Topic groups for First Day / Case Admin relief (consolidated narrative) ----
TOPICS = {
    "cash_management": {
        "nums": ["0012", "0056", "0078", "0180", "0212"],
        "label": "Cash Management System",
        "summary": "The court let Noble keep using its existing bank accounts, cash-management system, and intercompany-transaction practices during the case, instead of forcing it onto a new all-bankruptcy set of accounts — standard relief that avoids disrupting day-to-day operations. Approved on an interim basis 9/1/26 and made final 9/26/26."
    },
    "taxes": {
        "nums": ["0008", "0047", "0076", "0176", "0208"],
        "label": "Taxes & Fees",
        "summary": "Noble was authorized to keep paying routine taxes and government fees that came due, so the business doesn't fall into tax default while in Chapter 11. Approved on an interim basis 9/1/26 and made final 9/26/26."
    },
    "wages": {
        "nums": ["0010", "0053", "0077", "0178", "0210"],
        "label": "Employee Wages & Benefits",
        "summary": "Noble was authorized (but not required) to keep paying employee wages, benefits, and related obligations that came due before the filing, and to continue its benefit programs — protecting the workforce from disruption during the case. Approved on an interim basis 8/30-9/1/26 and made final 9/26/26."
    },
    "insurance": {
        "nums": ["0009", "0050", "0071", "0177", "0209"],
        "label": "Insurance Coverage",
        "summary": "Noble was authorized to keep its existing insurance policies in force, pay related premiums, and renew or purchase new coverage as needed — avoiding a lapse in coverage that could expose the estate to uninsured losses. Approved on an interim basis 8/30-9/1/26 and made final 9/26/26."
    },
    "verita_claims_agent": {
        "nums": ["0004", "0042", "0043", "0044", "0074"],
        "label": "Claims & Noticing Agent Retention",
        "summary": "The court approved hiring Kurtzman Carson Consultants LLC (dba Verita Global) as the claims and noticing agent — the company that runs this document website, mails court notices, and will process proofs of claim, taking that administrative burden off the court's own clerk. Approved 9/1/26."
    },
    "joint_admin": {
        "nums": ["0003", "0068"],
        "label": "Joint Administration",
        "summary": "The 11 Noble entities' cases are administered together under one case number (26-11369) for efficiency, even though each remains a legally separate debtor. Approved 9/1/26."
    },
    "redaction_service": {
        "nums": ["0007", "0058", "0070", "0175", "0207"],
        "label": "PII Redaction & Email Service",
        "summary": "Noble was authorized to redact employees' and individuals' personal identifying information (like home addresses) from public filings, and to serve case notices by email rather than paper mail where possible, cutting cost and protecting privacy. Approved on an interim basis 8/30-9/1/26 and made final 9/26/26."
    },
    "critical_vendors": {
        "nums": ["0011", "0057", "0072", "0179", "0211"],
        "label": "Critical Vendors & Lien Claimants",
        "summary": "Noble was authorized to pay certain pre-filing debts owed to vendors and lien claimants considered critical to keeping the supply chain running — vendors who might otherwise stop shipping and disrupt Noble's ability to serve its military/government customers. Approved on an interim basis 8/30-9/1/26 and made final 9/26/26."
    },
    "utilities": {
        "nums": ["0006", "0046", "0075", "0174", "0206"],
        "label": "Utilities",
        "summary": "Standard protections ensuring utility companies (power, water, telecom, etc.) can't cut off service over unpaid pre-filing bills, in exchange for Noble providing them 'adequate assurance' of future payment. Approved on an interim basis 8/30-9/1/26 and made final 9/26/26."
    },
    "worldwide_stay": {
        "nums": ["0005", "0045", "0069"],
        "label": "Worldwide Automatic Stay",
        "summary": "The court restated that the bankruptcy 'automatic stay' (which halts lawsuits, collection efforts, and contract terminations against Noble) applies worldwide, including at Noble's overseas operations in Germany and Japan, and reinforced anti-discrimination and 'ipso facto' contract protections. Approved 9/1/26."
    },
    "customer_deposits": {
        "nums": ["0112", "0184", "0216"],
        "label": "Customer Deposits",
        "summary": "Noble was authorized to honor certain pre-filing customer deposit obligations, preserving relationships with customers who had prepaid for goods/services. Order entered 9/26/26."
    },
    "ordinary_course_professionals": {
        "nums": ["0115", "0185", "0217"],
        "label": "Ordinary Course Professionals",
        "summary": "Noble was authorized to keep paying its regular outside professionals (accountants, routine outside counsel, etc. that pre-date the bankruptcy) through a streamlined process, without each one having to file a separate, costly retention application with the court. Order entered 9/26/26."
    },
    "interim_comp_procedures": {
        "nums": ["0111", "0183", "0215"],
        "label": "Professional Fee Payment Procedures",
        "summary": "Sets up a streamlined monthly process for the case's own retained professionals (law firms, financial advisors) to get paid on an interim basis during the case, subject to final court review at the end — standard case-administration housekeeping. Order entered 9/26/26."
    },
    "misc_asset_sales": {
        "nums": ["0110", "0182", "0214"],
        "label": "Miscellaneous Asset Sale Procedures",
        "summary": "Sets up a simplified, pre-approved process for Noble to sell smaller, non-material assets outside the main sale process without needing a separate court hearing for each one, speeding up monetization of odds-and-ends assets. Order entered 9/26/26."
    },
    "seal_confidential_parties": {
        "nums": ["0088", "0181", "0213"],
        "label": "Sealing Confidential Party Names",
        "summary": "Allows Noble and any official committee to file certain sensitive names (e.g., individuals in professional-retention disclosures) under seal rather than in the public record, balancing transparency with legitimate privacy/business-sensitivity concerns. Order entered 9/26/26."
    },
}

topic_num_to_key = {}
for key, t in TOPICS.items():
    for n in t["nums"]:
        topic_num_to_key[n] = key

# ---- Individually-authored summaries for key substantive filings actually reviewed ----
SUMMARIES = {
    "0001": "Noble Supply & Logistics, LLC's voluntary Chapter 11 petition — the filing that started the case, filed alongside 10 affiliated entities.",
    "0015": "The 'First Day Declaration' — the single most important narrative document in the case. Filed by CTO Robert Albergotti, it lays out Noble's business (a ~$1B/year defense logistics supplier, 5th-largest DLA prime vendor), its ~$292M in funded debt, and the chain of events — a terminated $1.2B DLA contract, a 7-week government shutdown, lender defaults, and DLA's Aug 27, 2026 termination of ~$400M of orders — that forced the bankruptcy filing. States the strategy: a parallel going-concern sale process and orderly liquidation, plus pursuit of an ~$86M claim against DLA.",
    "0018": "Filed Exhibit A to the First Day Declaration — Noble's corporate organizational chart, showing how the 11 debtor entities and their non-debtor parent (Noble Holdco, Inc., owned by founder Tom Noble) relate to each other.",
    "0017": "The redacted Creditor Matrix — the full mailing list of parties entitled to notice in the case (not a ranked list of largest creditors).",
    "0013": "Debtors' motion asking for court permission to use their secured lenders' cash collateral (essentially, permission to keep spending money that's collateral for the ABL, Term Loan, and Subordinated Note) to fund operations during the case, in exchange for giving those lenders 'adequate protection.'",
    "0014": "Declaration by CTO Robert Albergotti supporting the cash collateral motion, explaining why Noble needs court permission to keep using its lenders' collateral to fund operations.",
    "0073": "Interim order (first of several) giving Noble permission to use cash collateral, entered at the first-day hearing on 9/1/26, subject to a court-approved weekly budget and case milestones.",
    "0218": "Second Interim Cash Collateral Order, entered 9/26/26. Extends Noble's permission to spend secured lenders' cash collateral, attaches an updated 13-week cash flow budget, and locks in the case's key deadlines (Exhibit 2, 'Milestones') — including a sale-consummation deadline of ~Nov 28, 2026 and a plan-confirmation deadline of ~Dec 18, 2026. Final hearing on cash collateral set for Oct 16, 2026.",
    "0091": "Debtors' motion asking the court to approve the rules ('Bidding Procedures') for running an auction-style sale process for some or all of Noble's assets, including the ability to designate a stalking-horse bidder later if one emerges.",
    "0092": "Declaration of Lisa K. Lansio (Portage Point Partners, Noble's investment bank) describing the sale process: Noble entered Chapter 11 with NO stalking-horse bidder lined up; Portage Point has since contacted ~105 prospective buyers, ~25 of whom signed NDAs to review diligence materials, as part of a broad post-filing marketing effort.",
    "0219": "Order approving the Bidding Procedures for a sale of substantially all of Noble's assets — the court-approved rulebook for the auction. Sets the full sale timeline: bid deadline Oct 30, 2026; auction (if needed) Nov 4, 2026; sale hearing Nov 16, 2026; deadline to close Nov 20, 2026. Preserves Noble's ability to later designate a stalking-horse bidder (deadline ~Oct 21-23, 2026) but none has been named yet.",
    "0186": "Notice filing a revised, negotiated version of the proposed Bidding Procedures Order ahead of court approval — reflects last-minute changes made after discussions with the Term Loan Agent, ABL Agent, and other parties.",
    "0193": "Certification of Counsel presenting the final, court-ready version of the Bidding Procedures Order for the judge to sign, confirming no unresolved objections remained.",
    "0128": "U.S. Trustee's notice appointing the Official Committee of Unsecured Creditors — the formal body representing ordinary unsecured creditors' interests in the case (superseded by the amended notice at Docket #171).",
    "0171": "Amended notice of the Official Committee of Unsecured Creditors' membership — the current, authoritative list of which companies sit on the Committee representing unsecured creditors.",
    "0124": "The United States (on behalf of the Defense Logistics Agency) formally objected to Noble's emergency motion seeking to compel DLA performance and enforce the automatic stay — the government's side of the FSG-53 contract dispute.",
    "0142": "Certification of Counsel (filed by the United States) presenting a proposed order resolving the DLA/automatic-stay dispute for the court's signature.",
    "0151": "The court's ruling on Noble's emergency motion against DLA: Judge Goldblatt found that DLA's freeze of roughly $6.97M in invoice payments (to preserve a setoff against a ~$7.9M disincentive claim and an FCA settlement debt) went further than legally permitted, and ordered DLA to immediately pay Noble $6,434,434.37 (net of a ~$538K settlement offset). DLA remains free to separately seek stay relief later to pursue its larger disputed claims. A win for Noble on this specific cash-flow dispute, though distinct from — and smaller than — the ~$400M SOE contract termination and ~$86M FSG-53 claim described in the First Day Declaration, which remain unresolved.",
    "0219_note": "placeholder",
    "0204": "Redacted retention application for Kurtzman Carson Consultants dba Verita Global to serve in a second, broader role as Administrative Advisor to the Debtors (beyond just claims/noticing agent).",
    "0198": "Redacted application to retain Kirkland & Ellis LLP as the Debtors' lead bankruptcy counsel.",
    "0200": "Redacted application to retain Cole Schotz P.C. as Delaware co-counsel to the Debtors.",
    "0202": "Redacted application to retain Triple P TRS, LLC (a Portage Point Partners company) to continue providing Robert Albergotti as Chief Transformation Officer plus additional restructuring personnel.",
    "0004": "Original application to retain Verita Global as claims and noticing agent (see consolidated summary; approved 9/1/26 at Docket #74).",
    "0074": "Order approving Verita Global's retention as claims and noticing agent.",
    "0217": "Order approving streamlined procedures for paying Noble's ordinary-course (non-bankruptcy) professionals without individual retention applications.",
    "0115": "Motion seeking streamlined procedures for paying Noble's ordinary-course professionals.",
    "0016": "The unredacted List of Creditors, filed under seal (contains information Noble asked the court to keep confidential).",
    "0019": "Administrative case-management entry: the case was reassigned to Judge Craig T. Goldblatt (ending Judge Brendan Linehan Shannon's involvement).",
    "0021": "The formal Notice of Bankruptcy Filing bundling together the petitions and all first-day motions for service on creditors and other parties.",
    "0079": "Omnibus notice confirming the court's entry of the interim first-day orders and scheduling the final hearing on those matters for 9/28/26 (later cancelled/rescheduled — see Docket #220).",
    "0080": "The U.S. Trustee's routine request to the court clerk to schedule the mandatory Section 341 creditors' meeting.",
    "0081": "Notice of the Zoom-based Section 341 meeting of creditors, held 9/28/26 at 2:00pm ET — the meeting where a Debtor representative answers creditor questions under oath.",
    "0083": "The formal Notice of Chapter 11 Bankruptcy Case sent to all creditors, explaining the filing, the automatic stay, and the 341 meeting details.",
    "0084": "Certification of Counsel presenting a proposed order to the court scheduling the recurring omnibus hearing dates for the case.",
    "0085": "Order formally scheduling the case's omnibus hearing calendar, including the Oct 16, 2026 hearing date.",
    "0102": "Debtors' Emergency Motion asking the court to compel the Defense Logistics Agency (DLA) to perform under its contracts and to enforce the automatic stay against DLA — the opening filing in the DLA payment-freeze dispute (DLA had frozen roughly $6.97M of invoice payments owed to Noble). Resolved at Docket #151.",
    "0103": "CTO Robert Albergotti's declaration supporting the emergency motion against DLA, explaining the operational/financial harm from DLA freezing Noble's invoice payments.",
    "0104": "Declaration of Noble's counsel Seth Van Aalten supporting the emergency motion against DLA.",
    "0105": "Motion asking the court to shorten the normal notice period so the DLA dispute could be heard on an emergency basis.",
    "0106": "Order granting the request for expedited (shortened-notice) consideration of the DLA dispute.",
    "0107": "Notice of the hearing date for the DLA emergency motion.",
    "0108": "List of witnesses and exhibits Noble intended to present at the September 16, 2026 hearing (which covered the DLA dispute, among other matters).",
    "0125": "Declaration of Sean Cunniff supporting the United States' objection to Noble's emergency motion against DLA.",
    "0127": "Declaration of Ruth A. Sawdey supporting the United States' objection to Noble's emergency motion against DLA.",
    "0129": "Declaration of Amanda Parker supporting the United States' objection to Noble's emergency motion against DLA.",
    "0141": "Certification of Counsel (Noble) presenting the proposed order resolving the DLA dispute for the court's signature.",
    "0147": "Certification of Counsel regarding a court-approved stipulation resolving an automatic-stay issue tied to a pending state-court lawsuit against Noble.",
    "0170": "The Official Committee of Unsecured Creditors formally reserved its rights regarding the cash collateral and bid-procedures motions — signaling the Committee isn't objecting outright but wants to preserve its ability to raise issues later (e.g., on lender releases or sale terms).",
    "0187": "List of witnesses and exhibits Noble intended to present at the September 28, 2026 hearing.",
    "0188": "Notice filing the proposed Second Interim Cash Collateral Order ahead of the hearing where it was entered (see Docket #218).",
    "0191": "Certification of Counsel presenting the final, negotiated version of the Second Interim Cash Collateral Order for the court's signature.",
    "0195": "A sealed motion for approval — based on the related declaration at Docket #196, this is the Debtors' motion to approve a Key Employee Retention Plan (KERP) and Key Executive Incentive Plan (KEIP), with compensation details filed under seal.",
    "0196": "CTO Robert Albergotti's declaration supporting Noble's motion to approve a Key Employee Retention Plan (KERP) and Key Executive Incentive Plan (KEIP) — programs designed to keep essential employees and executives from leaving during the bankruptcy, with dollar amounts filed under seal.",
    "0197": "Sealed version of the Kirkland & Ellis retention application (see redacted public version at Docket #198).",
    "0199": "Sealed version of the Cole Schotz retention application (see redacted public version at Docket #200).",
    "0201": "Sealed version of the Triple P TRS / CTO retention application (see redacted public version at Docket #202).",
    "0203": "Sealed version of the Verita Global administrative-advisor retention application (see redacted public version at Docket #204).",
}

MOR_SUMMARY = "Monthly Operating Report for {entity}, period ending August 31, 2026 — the court-required financial snapshot (cash flow and balance sheet) for this entity. See the Financials view for the transcribed figures."
MOR_ENTITIES = {
    "0156": "Noble Supply & Logistics, LLC", "0157": "COTS Solutions, LLC",
    "0158": "Federal Resources Supply Company, LLC", "0159": "FRS Holdings, LLC",
    "0160": "K.D. Analytical Consulting, LLC", "0161": "KDA Acquisition, LLC",
    "0162": "Noble Defense Corporation", "0163": "Noble Equity Holdings, LLC",
    "0164": "Noble.com, LLC", "0165": "Noble Mission Support, LLC",
    "0166": "Tactical & Survival Specialties, LLC",
}
for num, ent in MOR_ENTITIES.items():
    SUMMARIES[num] = MOR_SUMMARY.format(entity=ent)

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

def routine_note(title):
    for pat, note in ROUTINE_NOTE_RULES:
        if re.search(pat, title, re.IGNORECASE):
            return note
    return "Procedural/administrative filing."

count_topic = 0
count_individual = 0
count_routine = 0
count_none = 0

for e in d:
    n = e['docket_no']
    if n in topic_num_to_key:
        key = topic_num_to_key[n]
        e['topic'] = key
        e['topic_label'] = TOPICS[key]['label']
        e['summary'] = TOPICS[key]['summary']
        count_topic += 1
    elif n in SUMMARIES:
        e['summary'] = SUMMARIES[n]
        count_individual += 1
    elif not e['substantive']:
        e['summary'] = routine_note(e['title'])
        count_routine += 1
    else:
        e['summary'] = None
        count_none += 1

with open(f"{BASE}/data/docket_final.json", "w", encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f"topic={count_topic} individual={count_individual} routine={count_routine} NO_SUMMARY_YET={count_none}")
missing = [e for e in d if e['summary'] is None]
for e in missing:
    print(e['docket_no'], '|', e['category'], '|', e['title'][:90])
