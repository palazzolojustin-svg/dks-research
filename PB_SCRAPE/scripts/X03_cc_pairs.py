"""X03: find dicks.com /f/ slugs captured (HTTP 200) by Common Crawl in BOTH a base window and a compare window
(e.g. Aug-Sep 2025 vs Aug-Sep 2026), write them to a slug file for X03_cc_plp.py (matched-page y/y panel).
Usage: python X03_cc_pairs.py <base colls comma> <cmp colls comma> <out slugfile>
  python X03_cc_pairs.py CC-MAIN-2025-33,CC-MAIN-2025-38 CC-MAIN-2026-34,CC-MAIN-2026-39 ..\raw\X03_pairs_AugSep.txt
"""
import os, sys, re, json

RAW = os.path.join(os.path.dirname(__file__), "..", "raw", "X03_cc")


def slugs(colls):
    s = set()
    for c in colls:
        fn = os.path.join(RAW, f"{c}_f.jsonl")
        if not os.path.exists(fn):
            continue
        for l in open(fn, encoding="utf-8"):
            try:
                r = json.loads(l)
            except Exception:
                continue
            if r.get("status") == "200" and "?" not in r["url"]:
                s.add(re.sub(r"^https?://[^/]+/", "", r["url"]).rstrip("/").lower())
    return s


a, b = slugs(sys.argv[1].split(",")), slugs(sys.argv[2].split(","))
both = sorted(a & b)
print(len(a), len(b), "both", len(both))
open(sys.argv[3], "w").write("\n".join(both) + "\n")
