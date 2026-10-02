# -*- coding: utf-8 -*-
"""
Assembles data/*.json into the single JSON object the tracker page embeds and
reads at load time. This is the canonical way to go from "the structured data
files" to "the blob the page's JavaScript expects" -- both refresh_docket.py
(the free/no-AI GitHub Action) and any AI-assisted local update should call
this after touching any file in data/, then feed the result to
build_standalone.py to regenerate index.html.

Usage: python scripts/build_bundle.py > /tmp/bundle.json
   or: from build_bundle import build_bundle
"""
import json, os, datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")

# Order matches what the page's JS destructures from DATA.*; see index.html /
# template/dashboard_template.html for the exact field names each section reads.
FILES = {
    "case_overview": "case_overview.json",
    "sale_milestones": "sale_milestones.json",
    "cash_budget": "cash_budget.json",
    "dla_dispute": "dla_dispute.json",
    "key_parties": "key_parties.json",
    "mor_financials": "mor_financials.json",
    "docket_entries": "docket_entries.json",
    "health_assessments": "health_assessments.json",
    "top_creditors": "top_creditors.json",
    "vendors_systems": "vendors_systems.json",
    "creditors_full": "creditors_full.json",
    "vendor_90day_payments": "vendor_90day_payments.json",
    "case_calendar": "case_calendar.json",
    "case_analysis": "case_analysis.json",
}


def build_bundle():
    bundle = {"generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    for key, filename in FILES.items():
        path = os.path.join(DATA_DIR, filename)
        with open(path, encoding="utf-8") as f:
            bundle[key] = json.load(f)
    return bundle


if __name__ == "__main__":
    import sys
    json.dump(build_bundle(), sys.stdout, ensure_ascii=False, separators=(",", ":"))
