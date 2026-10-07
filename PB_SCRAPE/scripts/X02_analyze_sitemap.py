"""X02: analyze dicks.com sitemap product URLs by brand and item-id year prefix.

Rerun: python PB_SCRAPE\\scripts\\X02_analyze_sitemap.py PB_SCRAPE\\raw\\X02_dsg_sitemap_urls_<date>.csv
Brand is taken from the URL slug prefix (slugs start with the brand name, e.g. /p/calia-womens-...).
DKS item ids (last path segment) start with a 2-digit year code (e.g. 26nik... -> 26), which tracks the
season/year the item was set up. Live sitemap = currently listed products only (survivorship caveat).
Output: prints tables, writes PB_SCRAPE\\raw\\X02_sitemap_brand_by_prefix_<date>.csv
"""
import sys, csv, collections, os

OWNED = {
    "dsg": "DSG", "calia": "CALIA", "vrst": "VRST", "maxfli": "MAXFLI", "walter-hagen": "Walter Hagen",
    "top-flite": "Top-Flite", "tommy-armour": "Tommy Armour", "alpine-design": "Alpine Design",
    "ethos": "ETHOS", "fitness-gear": "Fitness Gear", "nishiki": "Nishiki", "quest": "Quest",
}


def owned_brand(slug):
    for k, v in OWNED.items():
        if slug == k or slug.startswith(k + "-"):
            return v
    return None


def main(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    tot = collections.Counter(); own = collections.Counter(); byb = collections.Counter()
    bybp = collections.Counter()
    seen = set()
    for r in rows:
        pid = r["pid"].lower()
        if pid in seen:
            continue
        seen.add(pid)
        p = r["year_prefix"] or "na"
        tot[p] += 1
        b = owned_brand(r["slug"].lower())
        if b:
            own[p] += 1; byb[b] += 1; bybp[(b, p)] += 1
    n = len(seen); no = sum(own.values())
    print(f"unique product ids {n}; owned {no} = {no/n:.2%}")
    print("prefix  total  owned  owned%")
    out = []
    for p in sorted(tot):
        if tot[p] >= 50:
            print(f"{p:>6} {tot[p]:>6} {own[p]:>6} {own[p]/tot[p]:7.2%}")
        out.append([p, tot[p], own[p]])
    print("by brand:", byb.most_common())
    prefixes = ["21", "22", "23", "24", "25", "26"]
    print("brand x prefix:")
    for b, _ in byb.most_common():
        print(b, [bybp[(b, p)] for p in prefixes])
    d = os.path.basename(path).split("_")[-1].replace(".csv", "")
    with open(os.path.join(os.path.dirname(path), f"X02_sitemap_brand_by_prefix_{d}.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["prefix", "total_ids", "owned_ids"] + [f"own_{b}" for b in OWNED.values()])
        for p in sorted(tot):
            w.writerow([p, tot[p], own[p]] + [bybp[(b, p)] for b in OWNED.values()])


if __name__ == "__main__":
    main(sys.argv[1])
