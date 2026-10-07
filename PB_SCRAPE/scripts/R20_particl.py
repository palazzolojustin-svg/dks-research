"""R20_particl.py - Particl (particl.com) PUBLIC company pages: e-commerce product-level sales estimates.
For each retailer slug, extract: monitored products/SKUs, data-since date, 6-month revenue estimate, last-month revenue,
top-10 products (name, first seen, price, revenue, units) and flag DKS-owned brands; plus product-type counts.
Also pulls Wayback captures of the same page (history of the public top-10).
Usage: python R20_particl.py [slug ...]   default: dicks-sporting-goods golf-galaxy public-lands academy-sports-outdoors
Output: PB_SCRAPE/raw/R20_particl_top10.csv (append-only, with capture date) ; prints summary.
Rerun weekly/monthly: the public top-10 refreshes monthly; owned-brand entries in the top-10 are the signal.
"""
import sys, re, csv, os, time, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R20_fetch import fetch, text_of
OWNED = re.compile(r"\b(DSG|CALIA|VRST|Maxfli|Walter Hagen|Top Flite|Top-Flite|Tommy Armour|Alpine Design|ETHOS|Fitness Gear|"
                   r"Nishiki|Quest|FOXBURG|Monarch|Field & Stream|Prince)\b", re.I)
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")


def parse(t):
    out = {}
    m = re.search(r"Monitoring ([0-9.,]+K?) Products · ([0-9.,]+K?) SKUs/Variants Data since ([A-Za-z]+ \d+, \d{4})", t)
    if m: out.update(products=m.group(1), skus=m.group(2), since=m.group(3))
    m = re.search(r"most recent 6 months, .*? estimated \$?([0-9.]+[BMK]) in sales", t)
    if m: out["rev6m"] = m.group(1)
    m = re.search(r"last full month's sales during ([A-Za-z]+ \d{4}) were \$([0-9.]+[BMK])", t)
    if m: out.update(month=m.group(1), rev_month=m.group(2))
    seg = t[t.find("Image Rank Name Price Sales"):]
    seg = seg[:seg.find("Similar Competitors")] if "Similar Competitors" in seg else seg[:3000]
    items = re.findall(r"(\d{1,2}) (.+?) First seen ([A-Za-z]+ \d+, \d{4}) · \$([0-9.,]+) \$([0-9.,]+[KMB]?) ([0-9.,]+[KMB]?) sold", seg)
    out["top"] = items
    return out


if __name__ == "__main__":
    slugs = sys.argv[1:] or ["dicks-sporting-goods", "golf-galaxy", "public-lands", "academy-sports-outdoors"]
    rows = []
    for s in slugs:
        u = f"https://www.particl.com/company/{s}"
        caps = [("live", u)]
        try:  # Wayback history of the public page
            cdx = requests.get("http://web.archive.org/cdx/search/cdx", params={"url": u.replace("https://", ""), "output": "json",
                               "filter": "statuscode:200", "collapse": "timestamp:6"}, timeout=60).json()
            caps += [(c[1], f"http://web.archive.org/web/{c[1]}/{c[2]}") for c in cdx[1:]]
        except Exception as e:
            print("cdx err", s, e)
        for when, url in caps:
            try:
                t = text_of(fetch(url).text)
            except Exception as e:
                print("ERR", url, e); continue
            d = parse(t)
            owned = [x for x in d.get("top", []) if OWNED.search(x[1])]
            print(f"{s:25s} {when:15s} prod={d.get('products')} since={d.get('since')} rev6m={d.get('rev6m')} "
                  f"month={d.get('month')} {d.get('rev_month')} top={len(d.get('top', []))} owned_in_top={len(owned)} {[o[1] for o in owned]}")
            for x in d.get("top", []):
                rows.append([time.strftime("%Y-%m-%d"), s, when, x[0], x[1], x[2], x[3], x[4], x[5], bool(OWNED.search(x[1]))])
            time.sleep(1.5)
    out = os.path.join(RAW, "R20_particl_top10.csv")
    new = not os.path.exists(out)
    with open(out, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new: w.writerow(["run_date", "slug", "capture", "rank", "product", "first_seen", "price", "revenue", "units", "owned"])
        w.writerows(rows)
    print(len(rows), "rows ->", out)
