"""X08 Parse the automated Reddit clearance bots r/dickssportingdeals and r/golfgalaxydeals
("Clearance - Today's Top Finds", daily since ~Jun-2026; items caught by automated daily price scans of
dickssportinggoods.com / golfgalaxy.com with sale price, was-price and % off).

Classifies each listed item as DKS owned brand vs national brand and reports, by month: items, owned-brand
share of items, median % off owned vs national. Data come from X08_arctic_sub_dump.py dumps.
Rerun: python X08_arctic_sub_dump.py dickssportingdeals 2026-05-01 <today>; same for golfgalaxydeals;
       python X08_deals_bot_parse.py
Output: PB_SCRAPE/raw/X08_deals_bot_items.csv
"""
import json, re, os, csv, collections, statistics as st, datetime as dt

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
OWNED = r"^(CALIA|VRST|DSG|Maxfli|Walter Hagen|Top Flite|Top-Flite|Tommy Armour|Alpine Design|ETHOS|Fitness Gear|Nishiki|Quest)\b"
ITEM = re.compile(r"\d+\. \[(?P<name>[^\]]+)\]\((?P<url>[^)]+)\) — \*\*\$(?P<price>[\d,.]+)\*\* \(was \$(?P<was>[\d,.]+), (?P<off>[\d.]+)% off\)")
rows = []
for sub in ["dickssportingdeals", "golfgalaxydeals"]:
    fn = os.path.join(RAW, f"X08_arctic_{sub}.jsonl")
    if not os.path.exists(fn):
        continue
    seen = set()
    for line in open(fn, encoding="utf-8"):
        x = json.loads(line)
        if x["k"] != "posts" or x["id"] in seen:
            continue
        seen.add(x["id"])
        d = dt.datetime.fromtimestamp(x["t"], dt.timezone.utc)
        for m in ITEM.finditer(x["text"]):
            name = m.group("name")
            ob = re.match(OWNED, name, re.I)
            rows.append({"sub": sub, "date": d.date().isoformat(), "month": d.strftime("%Y-%m"), "name": name,
                         "owned": 1 if ob else 0, "brand": ob.group(1).upper() if ob else name.split(" ")[0],
                         "price": float(m.group("price").replace(",", "")), "was": float(m.group("was").replace(",", "")),
                         "off": float(m.group("off"))})
with open(os.path.join(RAW, "X08_deals_bot_items.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for sub in ["dickssportingdeals", "golfgalaxydeals"]:
    rs = [r for r in rows if r["sub"] == sub]
    if not rs:
        continue
    print("==", sub, len(rs), "items; dates", min(r["date"] for r in rs), "->", max(r["date"] for r in rs))
    for mth in sorted(set(r["month"] for r in rs)):
        mm = [r for r in rs if r["month"] == mth]
        o = [r["off"] for r in mm if r["owned"]]; n = [r["off"] for r in mm if not r["owned"]]
        print(mth, "items", len(mm), "owned share", round(len(o) / len(mm), 3),
              "med%off owned", st.median(o) if o else None, "national", st.median(n) if n else None)
    print("owned brands:", collections.Counter(r["brand"] for r in rs if r["owned"]).most_common())
    print("top national:", collections.Counter(r["brand"] for r in rs if not r["owned"]).most_common(12))
