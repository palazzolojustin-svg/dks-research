"""R4: classify iSpot spots (raw\\R4_ispot_spots.csv) as owned-brand-led / owned-brand-mentioned / other,
by year of iSpot 'Published' date. Output raw\\R4_ispot_spots_classified.csv and prints a year x class table.
Run after R4_ispot_crawl.py:  python PB_SCRAPE\\scripts\\R4_ispot_analyze.py
NOTE: the crawl only reaches spots linked from brand pages / related lists / web-search seeds, so the
DICK'S master-brand set is a SAMPLE (iSpot lists 540 DKS creatives). Owned-brand pages (VRST, CALIA,
Maxfli) are complete per their 'Total Creatives' counts.
"""
import csv, re, pathlib, datetime as dt
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
rows = list(csv.DictReader(open(ROOT / "raw" / "R4_ispot_spots.csv", encoding="utf-8")))
air = {r["path"]: r["public_airings_count"] for r in csv.DictReader(open(ROOT / "raw" / "R4_ispot_linktitles.csv", encoding="utf-8"))}
OWN = r"\b(CALIA|VRST|DSG|Maxfli|Walter Hagen|Alpine Design|ETHOS|Fitness Gear|Nishiki|Quest|Top[- ]Flite|Tommy Armour)\b"
out = []
for r in rows:
    try:
        d = dt.datetime.strptime(r["published"], "%B %d, %Y").date()
    except ValueError:
        d = None
    title, desc = r["title"], r["description"]
    t_hits = sorted(set(m.group(1) for m in re.finditer(OWN, title, re.I)))
    d_hits = sorted(set(m.group(1) for m in re.finditer(OWN, desc, re.I)))
    if r["brand"] in ("VRST", "CALIA", "Maxfli") or t_hits:
        cls = "owned_led"
    elif d_hits:
        cls = "owned_mentioned"
    else:
        cls = "other"
    out.append({"published": d.isoformat() if d else "", "year": d.year if d else "", "brand": r["brand"], "class": cls,
                "owned_in_title": "|".join(t_hits), "owned_in_desc": "|".join(d_hits),
                "airings_30d_to_2026-10-07": air.get(r["path"], ""), "title": title, "path": r["path"]})
out.sort(key=lambda x: x["published"])
with open(ROOT / "raw" / "R4_ispot_spots_classified.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
tab = defaultdict(Counter)
for o in out:
    tab[o["year"]][o["class"]] += 1
    tab[o["year"]]["brand:" + o["brand"]] += 1
for y in sorted(tab, key=str):
    print(y, dict(tab[y]))
for o in out:
    if o["class"] != "other" and o["year"] and o["year"] >= 2023:
        print(o["published"], o["brand"], o["class"], o["owned_in_title"] or o["owned_in_desc"], "|", o["title"][:90], "| airings30d:", o["airings_30d_to_2026-10-07"])
