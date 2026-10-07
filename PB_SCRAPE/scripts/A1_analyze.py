"""A1 step 3: Academy (ASO) owned-brand share of apparel reviews, the peer control for R1's DKS series.

Inputs : raw/A1_academy_products_apparel.csv, raw/A1_academy_reviews_apparel.csv
Outputs: raw/A1_aso_windows.csv   (basket x window x year x variant: owned n, total, share, eq-weight-month share)
         raw/A1_aso_brand_windows.csv (brand shares, Apr-Aug and Feb-Jul, ALLX variant)
         raw/A1_aso_monthly.csv   (basket x month x variant: owned, total, share; plus campaign volumes)
Variants: ALLX = all native reviews excluding bvsampling_* campaigns; EMAIL = BV_PIE_MPR + BV_PIE_FOLLOWUP_MPR;
          TEXT = BV_PI_TEXT (post-purchase SMS, launched 2025); PURCH = EMAIL + TEXT; ORG = null/BV_REVIEW_DISPLAY/
          BV_MOBILE_REVIEW_DISPLAY; SAMPLING = bvsampling_*.
Owned = Academy, Ltd. private brands by brand NAME (USPTO list; see OWNED_RE).
RERUN: python A1_analyze.py
"""
import csv, os, re, sys, math, collections
sys.path.insert(0, os.path.dirname(__file__))
from A1_bv_academy_common import RAW

OWNED_RE = re.compile(r"^(magellan|bcg|freely|r\.?o\.?w\.?$|row$|o'rageous|academy|brazos|game winner|h2ox|h2o xpress|"
                      r"austin (trading|clothing)|brava|mosaic|outdoor gourmet|redfield)", re.I)
BRAND_GROUPS = {"Magellan": re.compile(r"^magellan", re.I), "BCG": re.compile(r"^bcg", re.I), "Freely": re.compile(r"^freely", re.I),
                "R.O.W.": re.compile(r"^(r\.?o\.?w|row$)", re.I), "O'Rageous": re.compile(r"^o'rageous", re.I),
                "Nike": re.compile(r"^nike$", re.I), "Jordan": re.compile(r"^jordan$", re.I), "Under Armour": re.compile(r"^under armour", re.I),
                "adidas": re.compile(r"^adidas", re.I), "Columbia": re.compile(r"^columbia", re.I),
                "Carhartt": re.compile(r"^carhartt", re.I), "Chubbies": re.compile(r"^chubbies", re.I),
                "Levi's": re.compile(r"^levi", re.I), "The North Face": re.compile(r"^the north face", re.I),
                "Wrangler": re.compile(r"^wrangler", re.I), "Champion": re.compile(r"^champion", re.I)}
BASKETS = {"APPAREL": {"mens", "womens", "boys", "girls", "kids_other"}, "MENS": {"mens"}, "WOMENS": {"womens"},
           "KIDS": {"boys", "girls", "kids_other"}}
EMAIL = {"BV_PIE_MPR", "BV_PIE_FOLLOWUP_MPR"}; TEXT = {"BV_PI_TEXT"}; ORG = {"", "BV_REVIEW_DISPLAY", "BV_MOBILE_REVIEW_DISPLAY"}


def variant_of(c):
    if c.startswith("bvsampling"): return {"SAMPLING"}
    v = {"ALLX"}
    if c in EMAIL: v |= {"EMAIL", "PURCH"}
    elif c in TEXT: v |= {"TEXT", "PURCH"}
    elif c in ORG: v |= {"ORG"}
    else: v |= {"OTHER"}
    return v


WINDOWS = {"Apr-Aug": [4, 5, 6, 7, 8], "Feb-Jul": [2, 3, 4, 5, 6, 7], "Q1(Feb-Apr)": [2, 3, 4], "Q2(May-Jul)": [5, 6, 7],
           "Aug": [8], "Aug1-17": [8], "Sep": [9]}


def load():
    prods = {r["product_id"]: r for r in csv.DictReader(open(os.path.join(RAW, "A1_academy_products_apparel.csv"), encoding="utf-8"))}
    seen, out = set(), []
    for r in csv.DictReader(open(os.path.join(RAW, "A1_academy_reviews_apparel.csv"), encoding="utf-8")):
        if r["review_id"] in seen:
            continue
        seen.add(r["review_id"])
        p = prods.get(r["product_id"])
        if not p:
            continue
        bn = (p["brand_name"] or "").replace("\x99", "").replace("™", "").replace("®", "").strip()
        out.append({"y": int(r["submission_time"][:4]), "m": int(r["submission_time"][5:7]), "d": int(r["submission_time"][8:10]),
                    "basket": p["basket"], "brand": bn, "owned": bool(OWNED_RE.match(bn)), "vars": variant_of(r["campaign_id"] or ""),
                    "camp": r["campaign_id"] or ""})
    return out


def main():
    rows = load()
    print("unique reviews", len(rows))
    # windows
    agg = collections.defaultdict(lambda: [0, 0]); mon = collections.defaultdict(lambda: [0, 0])
    bagg = collections.defaultdict(int); btot = collections.defaultdict(int)
    for r in rows:
        for b, s in BASKETS.items():
            if r["basket"] not in s:
                continue
            for v in r["vars"]:
                mon[(b, f"{r['y']}-{r['m']:02d}", v)][0] += r["owned"]; mon[(b, f"{r['y']}-{r['m']:02d}", v)][1] += 1
                for w, ms in WINDOWS.items():
                    if r["m"] in ms and not (w == "Aug1-17" and r["d"] > 17):
                        agg[(b, w, r["y"], v)][0] += r["owned"]; agg[(b, w, r["y"], v)][1] += 1
                        if v == "ALLX":
                            btot[(b, w, r["y"])] += 1
                            for g, rx in BRAND_GROUPS.items():
                                if rx.match(r["brand"]):
                                    bagg[(b, w, r["y"], g)] += 1
                            if r["owned"]:
                                bagg[(b, w, r["y"], "ALL OWNED")] += 1
    with open(os.path.join(RAW, "A1_aso_windows.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["basket", "window", "year", "variant", "owned", "total", "share", "se", "eqw_month"])
        for (b, win, y, v), (o, t) in sorted(agg.items()):
            ms = [m for m in WINDOWS[win]]
            sh = [mon[(b, f"{y}-{m:02d}", v)] for m in ms]
            eq = [x[0] / x[1] for x in sh if x[1] >= 20]
            p = o / t if t else float("nan")
            w.writerow([b, win, y, v, o, t, round(p, 4), round(math.sqrt(p * (1 - p) / t), 4) if t else "",
                        round(sum(eq) / len(eq), 4) if eq and win != "Aug1-17" else ""])
    with open(os.path.join(RAW, "A1_aso_brand_windows.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["basket", "window", "year", "brand", "n", "total", "share"])
        for (b, win, y, g), n in sorted(bagg.items()):
            w.writerow([b, win, y, g, n, btot[(b, win, y)], round(n / btot[(b, win, y)], 4)])
    with open(os.path.join(RAW, "A1_aso_monthly.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["basket", "month", "variant", "owned", "total", "share"])
        for (b, m, v), (o, t) in sorted(mon.items()):
            w.writerow([b, m, v, o, t, round(o / t, 4) if t else ""])
    # campaign volumes by month (apparel)
    cv = collections.Counter((f"{r['y']}-{r['m']:02d}", sorted(r["vars"] - {"ALLX", "PURCH"})[0] if r["vars"] - {"ALLX", "PURCH"} else "ALLX") for r in rows)
    with open(os.path.join(RAW, "A1_aso_campaign_monthly.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["month", "variant", "reviews"])
        for (m, v), n in sorted(cv.items()):
            w.writerow([m, v, n])
    # sampling campaigns detail
    sc = collections.Counter((r["camp"], r["owned"]) for r in rows if "SAMPLING" in r["vars"])
    for (c, o), n in sorted(sc.items()):
        print("SAMPLING", c, "owned" if o else "national", n)


if __name__ == "__main__":
    main()
