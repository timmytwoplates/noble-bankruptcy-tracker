# HANDOFF: Noble Chapter 11 tracker

## 1. Purpose
A public, plain-English tracker for the Noble Supply & Logistics, LLC, et al. Chapter 11 case (Case No. 26-11369-CTG, D. Del., Judge Goldblatt). It is one self-contained HTML page (`index.html`) with the data embedded as JSON, published as a Claude Artifact and via GitHub Pages.

- Artifact: https://claude.ai/artifact/RaqHPDAYZi1WphWkDnFSge (private; updated in place)
- Repo: https://github.com/timmytwoplates/noble-bankruptcy-tracker
- Docket source: https://veritaglobal.net/noble/document/list/6618 (public, no login)

## 2. Current status (2026-11-11)
- Docket loaded through #453 (Nov 10).
- Nov 5 auction results (Docket #437) are in the Sale Process tab: the new "Auction results" section shows what sold, to whom, bid terms, a per-unit view of federal (GSA/IDIQ-type) contracts, and the still-unsold pieces (`data/sale_results.json`).
- Nothing is court-approved yet. Sale Hearing is Nov 16, 2026 at 1:00 PM ET.

## 3. Next steps
- When the asset purchase agreements, the designated-contract list and a proposed sale order are filed, update `data/sale_results.json` (deals, `gov_detail`, `remaining`, `open_items`).
- Nov 14: combined disclosure statement and plan of liquidation due. Nov 16: Sale Hearing and final cash collateral hearing. Dec 17: next omnibus hearing. Dec 18: sale-closing milestone.
- Re-check the cure schedule counts in `sale_results.json` against the filed designated-contract list.

## 4. Architecture and key files
- `data/*.json`: the source data. `scripts/build_bundle.py` (`FILES` dict) assembles them; `scripts/build_standalone.py` injects them into `template/dashboard_template.html` and writes `index.html`.
- Rebuild: `python scripts/build_standalone.py` (run without `-I`; it imports a sibling module).
- `scripts/refresh_docket.py`: mechanical docket refresh with no AI. Fails with a TLS error on the Windows dev machine, so use the GitHub Action instead: `gh workflow run refresh.yml`, then `git pull`.
- A daily cloud routine (`trig_012VfozJxhxg2iPhgGLDYyiJ`) writes AI summaries and republishes the artifact on its own. Before publishing from a local session: read the artifact, diff its bundle against `data/`, merge, then publish.
- `UPDATE_PLAYBOOK.md` has the routine's update steps.

## 5. Decisions and rationale
- Money is stored as whole USD in the JSON; the page formats it.
- Every claim links to a docket PDF via `citeHtml()`. PDF URLs come from `docket_entries.json`; never hand-type them.
- Bidder names are printed as in Docket #437. The backup bidder is "Forward Readiness, LLC" (the notice's table); some later filings write "IQ Forward Readiness, LLC".
- Government-contract flags are the tracker's own reading of the cure schedule (Docket #252-1), which labels 147 entries only "Government Contract". Counts by Debtor entity are approximate.

## 6. Data, integrations and environment
- No secrets or env vars are needed to build. GitHub Actions workflow: `refresh.yml` (docket refresh, no AI).
- Tools used locally: Python 3, `pdftotext`/`pdfdetach` (poppler/xpdf), `gh`.

## 7. Gotchas and open questions
- Verita lists a filing hours after it hits the court's docket.
- `pdftotext -layout` wraps table cells; read the page image when a name is ambiguous.
- The $266M versus $1B+ False Claims Act figure on the DOJ & FCA tab has not been reconciled.

## 8. Change log
- 2026-11-11: Added auction results and federal-contract section (`sale_results.json`, Sale Process tab). Merged the routine's Nov 11 update (docket through #453). Fixed the backup bidder name.
- 2026-11-06 to 11-10: Routine published the Notice of Auction Results update; added hearing and deadline calendar, 90-day vendor payments, breakeven and cause-of-filing analyses (earlier sessions).
