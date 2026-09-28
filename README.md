# Noble Supply & Logistics — Chapter 11 Tracker

A plain-English dashboard for the Noble Supply & Logistics, LLC, et al. Chapter 11 bankruptcy
(Case No. 26-11369, U.S. Bankruptcy Court, District of Delaware, Hon. Craig T. Goldblatt).

**Live site:** https://timmytwoplates.github.io/noble-bankruptcy-tracker/

## What's here

- **`index.html`** — the tracker itself. A single self-contained page (data is embedded inline
  as JSON, no backend) covering: case overview and capital structure, a plain-English breakdown
  of every docket filing, the asset-sale timeline, per-entity financials from the Monthly
  Operating Reports, the full creditor list (not just the court-disclosed top 30), known
  software/utility vendors and treasury/payment practices, and a running "likely outcome"
  assessment with its reasoning.
- **`data/`** — the structured JSON this page is built from: docket entries, MOR financials,
  sale milestones, the creditor list, key parties, and so on. Useful if you want to build your
  own view on top of the same data.
- **`scripts/`** — the Python used to turn the raw court filings into that structured data:
  parsing the docket list, categorizing filings, transcribing MOR financial statements,
  parsing the ~3,300-entry creditor mailing list (a multi-column PDF table that needed
  `pdftotext -table` rather than `-layout` to extract correctly), and classifying creditors by
  type. Included for transparency about the extraction method, not as a turnkey pipeline — the
  raw downloaded PDFs/HTML aren't included here (they're large and easy to re-fetch from the
  source below).

## Source

Everything on this page is built from the public docket maintained by Kurtzman Carson
Consultants dba Verita Global, the case's claims and noticing agent:
**https://veritaglobal.net/noble/document/list/6618**

Every claim on the page links back to the specific docket entry (and its source PDF) it came
from. Where something is our own inference rather than a fact the court filings state directly
(creditor type classifications, the health/outlook assessment, some vendor identifications),
the page says so.

## Staying current

This is a **snapshot**, not a live feed — it reflects the docket as of the date shown at the
bottom of the page. It is not automatically kept in sync with this GitHub repo.

## Not legal advice

This is a research aid for following the case in plain English, built with a mix of automated
extraction and manual review. Figures are transcribed from public court filings and may contain
errors, especially across the ~3,300-entry creditor list, which was extracted programmatically.
Verify anything decision-critical against the linked source PDF.
