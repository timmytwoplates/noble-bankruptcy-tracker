# AI-assisted update playbook

The free `refresh.yml` GitHub Action keeps `data/docket_entries.json` current
mechanically (new filings, dates, routine/substantive classification) but
can't write plain-English summaries or transcribe financial statements —
that needs an actual read of the PDF. This is the playbook for doing that
pass, meant to be followed by a Claude Code session (or any capable
human/AI) working in a local clone of this repo. It's written so the
session running it doesn't need any other context than this file.

## 1. Get current

```bash
git clone https://github.com/timmytwoplates/noble-bankruptcy-tracker
cd noble-bankruptcy-tracker
python scripts/refresh_docket.py   # catch up on anything the daily Action hasn't run for yet
```

## 2. Check what needs attention

Open `data/pending_review.json` — an array of `{docket_no, title, category, reason}`
for every substantive filing that only has a mechanical placeholder so far
(`"summary": null` in `data/docket_entries.json`). Work through it top to
bottom (oldest first, so cross-references make sense).

## 3. For each pending docket entry

Look up its `pdf_href` in `data/docket_entries.json`, download it, and extract text:

```bash
curl -sL "https://veritaglobal.net<pdf_href>" -A "Mozilla/5.0" -o /tmp/doc.pdf
pdftotext -layout /tmp/doc.pdf /tmp/doc.txt   # add -table instead of -layout for wide multi-column
                                                # tables (e.g. another creditor-style matrix) --
                                                # -layout badly interleaves those, -table doesn't.
```

If a table still looks garbled in the extracted text, or a schedule is an embedded image, read
that specific page as an image instead (any PDF viewer/tool that can rasterize a page range works;
in a Claude Code session, the Read tool's `pages` parameter on the PDF does this directly).

**Write a 2-4 sentence plain-English summary** — assume the reader knows nothing about bankruptcy
law — and set it as that entry's `summary` field in `data/docket_entries.json`. Refine `category`
if the mechanical guess was off (valid values: Sale Process, Financing / Cash Collateral, Financial
Reporting, Professional Retention, Committee, Claims / Bar Date, DLA Dispute, First Day / Case
Admin, Hearing / Court Admin, Employee / KERP, Other / General).

**If it's a Monthly Operating Report** (category "Financial Reporting"): transcribe every cash-flow
and balance-sheet line item into a new entry in `data/mor_financials.json`, matching the schema of
the existing entries there (`entity, docket_no, case_no, period_start, period_end, cash_flow[],
cash_summary{}, balance_sheet[], balance_sheet_totals{}, postpetition_taxes_current, notes,
discrepancy_flag, income_statement[], income_statement_note`). Write `notes` as multiple paragraphs
separated by blank lines (`\n\n`) — never one run-on paragraph. Add a new array entry per period
per entity; never overwrite a prior period.

**If it changes the sale process** (a stalking horse gets named, a deadline moves, an auction
happens, the sale closes): update `data/sale_milestones.json` — set the matching `sale_timeline` /
`cash_collateral_milestones` entry's `status`, and update `stalking_horse_status` the moment one is
named. This is the single most important fact in the case; call it out clearly in your summary to
the person you're doing this update for.

**If it changes the Committee, a professional retention, or the DLA dispute**: update the relevant
entry in `data/key_parties.json` or `data/dla_dispute.json`.

**If it reveals new vendor/creditor/systems intelligence** (an amended largest-creditors list, a
new critical-vendor disclosure, a newly identified software/utility vendor): update
`data/top_creditors.json`, `data/vendors_systems.json`, and/or the matching entry inside
`data/creditors_full.json`.

Once handled, remove that docket number's entry from `data/pending_review.json`.

## 4. Refresh the outlook

After processing everything pending, write ONE new object and append it to
`data/health_assessments.json` (never edit or remove prior entries — they're a history). Match the
shape of the existing entries: `as_of` (today), `indicator` (`"uncertain"` | `"positive"` |
`"negative"`), `indicator_label`, `summary`, `positive_signals[]`, `risk_signals[]`, `watch_next[]`
(array of `{date, event}`). Base it on what's actually true now — especially whether a stalking
horse has been named, how the sale timeline is tracking, and any MOR cash-trend signal — not a
restatement of the prior entry.

## 5. Rebuild and push

```bash
python scripts/build_standalone.py   # regenerates index.html from data/ + template/
git add -A
git commit -m "AI-assisted update: <one line on what changed>"
git push
```

GitHub Pages redeploys automatically on push to `main`; the live site updates within a minute or
two.

## Notes for whoever (or whatever) is running this

- The docket lives at `https://veritaglobal.net/noble/document/list/6618` — a plain
  server-rendered page, no login. `scripts/refresh_docket.py` shows the exact POST request that
  pages through it.
- `scripts/build_bundle.py` shows precisely what JSON shape `index.html`'s JavaScript expects from
  each `data/*.json` file — read it if a field name is unclear.
- Keep every dollar figure and quote sourced to a specific docket number; the page renders a
  "Source: Docket #N" link next to every claim it can, using `pdf_url` from
  `data/docket_entries.json` — don't state something as fact without a docket number behind it.
