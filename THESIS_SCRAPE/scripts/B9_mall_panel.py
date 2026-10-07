"""B9: for malls that host (or will host) a House of Sport / Field House, pull every DICK'S sales/rent window from the cached CMBS docs.

Rerun: python B9_mall_panel.py   -> raw/B9_mall_windows.txt (grouped by mall, deduped)
Caches scanned: raw/H04_edgar_cache, raw/B8_cache, raw/B9_edgar_cache (+ raw/B10_cache if present).
"""
import glob
import os
import re

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
files = []
for d in ("H04_edgar_cache", "B8_cache", "B9_edgar_cache", "B10_cache"):
    files += glob.glob(os.path.join(RAW, d, "*.txt"))
MALLS = ["Ridgedale", "Ross Park", "West Town", "Eastview", "Oakdale", "International Plaza", "Baybrook", "Katy Mills",
         "NorthPark Mall", "Greenbrier", "Market Place", "Colonie", "Latham", "Viewmont", "Prudential", "Brandywine",
         "Penn Square", "Woodland Hills", "Rockingham", "Dadeland", "Dayton Mall", "Mall of Louisiana", "Newport Centre",
         "Freehold", "SouthPark", "Annapolis", "Crabtree", "Parks Mall", "Brea", "Southdale", "Delray", "Gallery on the Parkway",
         "Empire Mall", "Washington Square", "Northshore", "Tysons", "Cerritos", "Gardens Mall", "Barton Creek", "Arden Fair",
         "Galleria", "King of Prussia", "Battlefield", "CoolSprings", "Westmoreland", "Southpoint", "Valley River", "Cherry Hill",
         "Springfield Town Center", "Mission Valley", "Mall of America", "Stonebriar", "Willowbrook", "Fashion Place", "Woodfield",
         "Twelve Oaks", "Polaris", "Easton", "Kenwood", "Lakeline", "Ingram Park", "La Cantera", "Alderwood", "Rivertown",
         "Mall at Rockingham", "Jordan Creek", "Haywood", "Cumberland", "Perimeter", "Town Center at Cobb", "Clackamas",
         "Pheasant Lane", "Natick", "Shops at Riverside", "Garden State", "Smith Haven", "Walt Whitman", "Roosevelt Field",
         "Destiny", "Galleria at Sunset", "St. Johns Town Center", "Mission Viejo", "Cape Cod", "Brandon", "Bel Air"]
import sys
if len(sys.argv) > 2:
    MALLS = sys.argv[2].split("|")
OUTN = sys.argv[1] if len(sys.argv) > 1 else "B9_mall_windows.txt"
MR = re.compile("|".join(re.escape(m) for m in MALLS))
DR = re.compile("Dick[\u2019']?s|DICK[\u2019']S|DHOS|House of Sport|Field House")
SALES = re.compile(r"(sales|Sales|PSF|psf|per square foot|Occupancy Cost|occupancy cost).{0,250}\$\s?[\d,]{3,}", re.S)
seen = set()
out = {}
for fp in sorted(files):
    txt = open(fp, encoding="utf-8", errors="ignore").read()
    malls = [(m.start(), m.group(0)) for m in MR.finditer(txt)]
    if not malls:
        continue
    for m in DR.finditer(txt):
        prev = [x for x in malls if x[0] <= m.start() and m.start() - x[0] < 15000]
        if not prev:
            continue
        mall = prev[-1][1]
        w = txt[max(0, m.start() - 350): m.end() + 450]
        if not SALES.search(w):
            continue
        k = re.sub(r"\W", "", txt[max(0, m.start() - 80): m.end() + 160])
        if k in seen:
            continue
        seen.add(k)
        out.setdefault(mall, []).append(f"[{os.path.basename(fp)}] ...{w}...")
with open(os.path.join(RAW, OUTN), "w", encoding="utf-8") as f:
    for mall in sorted(out):
        f.write(f"\n\n######## {mall} ({len(out[mall])})\n")
        f.write("\n\n".join(out[mall]))
for mall in sorted(out, key=lambda z: -len(out[z])):
    print(len(out[mall]), mall)

