# -*- coding: utf-8 -*-
import json, os

BASE = os.path.dirname(os.path.abspath(__file__)) + "/noble_docs/data"
m = json.load(open(f"{BASE}/mor_financials.json", encoding='utf-8'))
by_docket = {e['docket_no']: e for e in m}

SIGNED = "Signed by Robert Albergotti, Chief Transformation Officer, 09/22/2026."
Q7 = "Part 7 questionnaire: no prepetition-debt payments, no out-of-ordinary-course payments, no insider payments, current on postpetition tax filings and estimated payments, trust fund taxes current, no postpetition borrowing, no professional payments (N/A), has workers' comp/casualty/general liability insurance with current premiums, no plan of reorganization or disclosure statement filed yet, current on quarterly UST fees."
PARTS_ZERO = "Part 3 (assets sold/transferred): $0. Part 5 (professional fees & expenses): blank — no professionals paid yet this period. Part 6 (postpetition taxes): all $0."

# ---------- Noble Supply & Logistics, LLC (0156) ----------
e = by_docket['0156']
e['notes'] = (
    "Lead/reporting debtor. Reporting period is the 2-day stub period 08/30/2026 (petition date) through 08/31/2026 — Months Pending: 0, cash basis reporting.\n\n"
    "Part 1–4 figures are taken from a clean re-read of the native PDF (pdftotext badly interleaved the multi-line Part 2/4 cells for this filing). The detailed balance sheet and statement of operations come from the 5-page support-schedule attachment (Doc 156-1), a consolidated 2-column schedule covering only this entity and K.D. Analytical Consulting, LLC — the other 9 jointly-administered debtors filed blank/zero main forms with no attachments.\n\n"
    "Cash balance of $1,308,831 (beginning = ending, no activity in the stub period) is held across JPMorgan accounts x3671 ($20,856), x0745 ($102,058), x9326 ($1,163,196), x9876 ($22,721), x6129 ($0) and x6203 ($0), per the Cash Balances schedule.\n\n"
    f"{PARTS_ZERO}\n\n"
    f"{Q7}\n\n"
    f"{SIGNED}"
)
e['discrepancy_flag'] = (
    "The main MOR form's Part 2 liability classification (secured/priority/unsecured debt: total liabilities $546,983,813, ending equity $773,289,233) does NOT match the detailed support-schedule balance sheet's current/long-term classification (total liabilities $1,244,114,519, total equity $76,158,527). Both splits independently sum to the same Total Assets of $1,320,273,046, so this looks like two different liability-classification methodologies applied to the same asset base rather than a math error — flagged for legal/financial review rather than resolved here."
)
e['income_statement'] = [
    {"line_item": "Product Sales", "amount_usd": 4124287, "section": "revenue"},
    {"line_item": "Training Revenue", "amount_usd": 3250, "section": "revenue"},
    {"line_item": "Less Returns & Allowances", "amount_usd": -54646, "section": "revenue"},
    {"line_item": "Total Revenue", "amount_usd": 4072891, "section": "subtotal"},
    {"line_item": "Product COGS", "amount_usd": -4956160, "section": "cogs"},
    {"line_item": "Service COGS", "amount_usd": -308236, "section": "cogs"},
    {"line_item": "Total COGS", "amount_usd": -5264396, "section": "subtotal"},
    {"line_item": "Gross Profit", "amount_usd": 9337287, "section": "subtotal"},
    {"line_item": "Selling Expenses", "amount_usd": 12470, "section": "opex"},
    {"line_item": "Compensation & Payroll Taxes", "amount_usd": 1155058, "section": "opex"},
    {"line_item": "Employee Benefits", "amount_usd": 233859, "section": "opex"},
    {"line_item": "Occupancy & Facilities", "amount_usd": 155655, "section": "opex"},
    {"line_item": "IT & Technology", "amount_usd": 289701, "section": "opex"},
    {"line_item": "Professional & Consulting Fees", "amount_usd": 153526, "section": "opex"},
    {"line_item": "Insurance", "amount_usd": 137300, "section": "opex"},
    {"line_item": "Travel & Entertainment", "amount_usd": 528769, "section": "opex"},
    {"line_item": "Other G&A", "amount_usd": -396, "section": "opex"},
    {"line_item": "Total G&A Expenses", "amount_usd": 2653472, "section": "subtotal"},
    {"line_item": "Legal — Investigation Matters", "amount_usd": 58943, "section": "other"},
    {"line_item": "Financial Advisor & Restructuring-Related Fees", "amount_usd": 775085, "section": "other"},
    {"line_item": "Realized Gain/Loss", "amount_usd": -1063, "section": "other"},
    {"line_item": "Other/Rounding", "amount_usd": 12, "section": "other"},
    {"line_item": "Total Other Expense", "amount_usd": 832977, "section": "subtotal"},
    {"line_item": "Depreciation & Amortization", "amount_usd": 150390, "section": "other"},
    {"line_item": "Interest & Other Income, net", "amount_usd": -7630, "section": "other"},
    {"line_item": "Other Taxes (Non-Income)", "amount_usd": 6918, "section": "other"},
    {"line_item": "Net Income (Loss)", "amount_usd": 5688689, "section": "total"},
]
e['income_statement_note'] = "From the Doc 156-1 support schedule. Matches the main form's Part 4k profit/loss; current month = cumulative for this 2-day stub period."

# ---------- K.D. Analytical Consulting, LLC (0160) ----------
e = by_docket['0160']
e['notes'] = (
    "Second of the two debtors with populated financials this period. Reporting period is the 2-day stub period 08/30/2026–08/31/2026 — Months Pending: 0, cash basis.\n\n"
    "Main-form Part 1–4 figures are re-read from the clean native PDF (pdftotext jumbled the multi-line cells). The detailed balance sheet and statement of operations come from the identical 5-page support-schedule attachment filed at both Doc 156-1 and Doc 160-1 — a single consolidated 2-column schedule covering this entity together with Noble Supply & Logistics, LLC, duplicated as an exhibit to both dockets.\n\n"
    "Cash balance $3,669 is held in JPMorgan account x7189 (beginning = ending, no activity); a second account, x7854, in this entity's name shows a $0 balance per the Cash Balances schedule.\n\n"
    f"{PARTS_ZERO}\n\n"
    "Part 7 questionnaire answers are identical to the lead entity (see Noble Supply & Logistics notes).\n\n"
    f"{SIGNED}"
)
e['discrepancy_flag'] = (
    "Same balance-sheet-classification discrepancy as the lead entity: the main form's Part 2 secured/priority/unsecured classification (total liabilities $1,762,664, ending equity $47,910,540) does not match the support-schedule's current/long-term classification (total liabilities $25,837,532, total equity $23,835,672). Both splits independently sum to Total Assets of $49,673,204."
)
e['income_statement'] = [
    {"line_item": "Product Sales", "amount_usd": -584557, "section": "revenue"},
    {"line_item": "Service Revenue", "amount_usd": 1081241, "section": "revenue"},
    {"line_item": "Training Revenue", "amount_usd": 164535, "section": "revenue"},
    {"line_item": "Total Revenue", "amount_usd": 661219, "section": "subtotal"},
    {"line_item": "Product COGS", "amount_usd": -1010669, "section": "cogs"},
    {"line_item": "Service COGS", "amount_usd": 1307537, "section": "cogs"},
    {"line_item": "Total COGS", "amount_usd": 296868, "section": "subtotal"},
    {"line_item": "Gross Profit", "amount_usd": 364351, "section": "subtotal"},
    {"line_item": "Selling Expenses", "amount_usd": 0, "section": "opex"},
    {"line_item": "Compensation & Payroll Taxes", "amount_usd": 199664, "section": "opex"},
    {"line_item": "Employee Benefits", "amount_usd": 34936, "section": "opex"},
    {"line_item": "Occupancy & Facilities", "amount_usd": 579, "section": "opex"},
    {"line_item": "Other G&A", "amount_usd": 699, "section": "opex"},
    {"line_item": "Total G&A Expenses", "amount_usd": 235879, "section": "subtotal"},
    {"line_item": "Total Other Expense", "amount_usd": 0, "section": "subtotal"},
    {"line_item": "Depreciation & Amortization", "amount_usd": 6069, "section": "other"},
    {"line_item": "Net Income (Loss)", "amount_usd": 122402, "section": "total"},
]
e['income_statement_note'] = "From the Doc 160-1 support schedule (same source document as Doc 156-1). Matches the main form's Part 4k; current month = cumulative for this 2-day stub period."

# ---------- The 9 all-zero entities: paragraph-break + trim ----------
ZERO_NOTES = {
    '0157': ("COTS Solutions, LLC", "26-11370",
        "Every dollar figure on Parts 1–4 of the main form is printed as $0 — no separate bank accounts or standalone activity attributed to this entity during the stub period. The enterprise's actual cash, receivables, inventory and liabilities for the period are reported at the two entities that filed populated schedules: Noble Supply & Logistics, LLC (Doc 156) and K.D. Analytical Consulting, LLC (Doc 160). No support-schedule attachment was filed for this entity."),
    '0158': ("Federal Resources Supply Company, LLC", "26-11371",
        "Despite the entity name suggesting an operating supply business, every dollar figure on Parts 1–4 is printed as $0 for this reporting period — no separate bank accounts or activity attributed to this entity. The Cash Balances schedule (Doc 156-1/160-1) does list a “Federal Resources Supply Company, LLC” JPMorgan account, x7847, with a $0 balance, consistent with this filing. No support-schedule attachment was filed for this docket."),
    '0159': ("FRS Holdings, LLC", "26-11372",
        "The entity name (“Holdings”) and all-zero form are consistent with this being a non-operating holding company with no separate bank accounts or activity during the stub period. No support-schedule attachment was filed."),
    '0161': ("KDA Acquisition, LLC", "26-11374",
        "All-zero main form; an “Acquisition” shell entity with no separate bank activity this period. The Cash Balances schedule (Doc 156-1/160-1) lists a JPMorgan account, x7056, in this entity's name with a $0 balance, consistent with this filing. No support-schedule attachment was filed."),
    '0162': ("Noble Defense Corporation", "26-11375",
        "All-zero main form; not among the entities listed on the Cash Balances schedule, consistent with no bank accounts and no activity this period. No support-schedule attachment was filed."),
    '0163': ("Noble Equity Holdings, LLC", "26-11376",
        "All-zero main form; the entity name (“Equity Holdings”) and the lack of any listed bank account are consistent with a pure holding-company shell with no operations this period. No support-schedule attachment was filed."),
    '0164': ("Noble.com, LLC", "26-11377",
        "All-zero main form; likely a dormant IP/domain-holding entity with no separate bank accounts or activity this period. No support-schedule attachment was filed."),
    '0165': ("Noble Mission Support, LLC", "26-11378",
        "All-zero main form; consistent with a services/payroll-support entity whose costs and cash flow through the two reporting entities (Noble Supply & Logistics and K.D. Analytical Consulting) rather than its own accounts this stub period. No support-schedule attachment was filed."),
    '0166': ("Tactical & Survival Specialties, LLC", "26-11379",
        "All-zero main form despite this entity having its own JPMorgan account (x3770, $0 balance per the Cash Balances schedule in Doc 156-1/160-1) — no activity through that account this stub period. No support-schedule attachment was filed for this docket."),
}

for docket_no, (name, case_no, specific) in ZERO_NOTES.items():
    e = by_docket[docket_no]
    e['notes'] = (
        f"Stub-period MOR (08/30/2026–08/31/2026, Months Pending: 0), Case No. {case_no}, jointly administered under lead Case No. 26-11369.\n\n"
        f"{specific}\n\n"
        f"{PARTS_ZERO}\n\n"
        "Part 7 questionnaire answers are identical to the lead entity's: current on tax filings and estimated payments, trust fund taxes current, no postpetition borrowing, no insider or out-of-ordinary-course payments, insurance in place, no plan or disclosure statement filed yet, current on quarterly UST fees.\n\n"
        f"{SIGNED}"
    )

json.dump(m, open(f"{BASE}/mor_financials.json", "w", encoding='utf-8'), indent=2, ensure_ascii=False)
print("done, entities:", len(m))
