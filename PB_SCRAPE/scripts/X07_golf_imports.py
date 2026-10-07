"""X07: golf owned-brand import read-through, built on X04's ImportYeti pull (no new scraping).

Input : PB_SCRAPE\\raw\\X04_dmsc_vendor_quarterly_2026-10-07.csv  (consignee DICK'S MERCHANDISING & SUPPLY CHAIN x supplier x quarter;
        sea BOLs via ImportYeti / CBP AMS). Rerun X04's scripts\\X04_dmsc_suppliers.py first to refresh, then:
Rerun : python X07_golf_imports.py [path_to_quarterly_csv]
Output: PB_SCRAPE\\raw\\X07_golf_imports_summary.csv  (supplier, window, year, shipments, teu, weight_kg)
Golf suppliers (identified from BOL product text in X04 data):
  foremost-golf-mfg  Taiwan  = Maxfli Tour-series ball OEM ("Maxflitour ... Tourxm ... Toursm")
  formosa-golf       China/TW = golf clubs ("Golf Club Includes ...")  -> Top Flite / Tommy Armour / Maxfli club sets (INFERENCE)
  cheung-shing-global-sky-hk-trade China = "Golf Sports Golf Etc" + mini basketball (mixed; golf accessories)
Caveats: quarterly granularity; Q3-2026 includes only to ~Oct-2; BOL data can miss shipments (air freight, transloads, confidential filers).
"""
import csv
import os
import sys
from collections import defaultdict

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAW, "X04_dmsc_vendor_quarterly_2026-10-07.csv")
GOLF = {"/supplier/foremost-golf-mfg": "Foremost (Maxfli balls)",
        "/supplier/formosa-golf": "Formosa Golf (clubs)",
        "/supplier/cheung-shing-global-sky-hk-trade": "Cheung Shing (golf misc + other)"}
WINDOWS = {"Jan-Sep": ("01", "04", "07"), "Apr-Sep": ("04", "07"), "Jul-Sep": ("07",), "FullYear": ("01", "04", "07", "10")}

agg = defaultdict(lambda: [0, 0, 0])
with open(src, encoding="utf8", errors="ignore") as f:
    for r in csv.DictReader(f):
        if r["url"] not in GOLF:
            continue
        y, q = r["quarter_start"][:4], r["quarter_start"][5:7]
        for w, qs in WINDOWS.items():
            if q in qs:
                a = agg[(GOLF[r["url"]], w, y)]
                a[0] += int(r["shipments"] or 0)
                a[1] += int(r["teu"] or 0)
                a[2] += int(float(r["weight_kg"] or 0))
out = os.path.join(RAW, "X07_golf_imports_summary.csv")
with open(out, "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["supplier", "window", "year", "shipments", "teu", "weight_kg"])
    for (s, w, y), v in sorted(agg.items()):
        if y >= "2022":
            wr.writerow([s, w, y, *v])
            print(f"{s:34s} {w:8s} {y} ship={v[0]:4d} teu={v[1]:4d} kg={v[2]:>9,d}")
