"""A1: coverage check of the URL-based apparel basket. For selected brand IDs, page ALL products with reviews via
BrandId filter, keep those with a review since 2024-01-01, and report what share (by products and by reviews) is in
raw/A1_academy_products_apparel.csv, plus names of apparel-looking products that were missed.
RERUN: python A1_coverage_check.py
"""
import csv, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from A1_bv_academy_common import session, get, RAW

BRANDS = ["Freely", "cy0hxx5ojl7a6vcmd2qbe8cml", "BCG", "367nzqysswbp68uijkt2mjlkv", "Magellan_Outdoors",
          "8hhr39fb4hz6720zcn8bedkh7", "R.O.W.", "cp8wk7hv3esimbows4vawxl9y", "Nike", "Under_Armour"]
APP = re.compile(r"(shirt|tee|t-shirt|top|tank|hoodie|sweatshirt|pullover|jacket|pant|short|legging|jogger|bra|polo|vest|dress|skirt|capri|tight|pullover|fleece|crew|1/4|quarter|set)", re.I)
NOT = re.compile(r"(shoe|cleat|slide|sandal|boot|sock|hat|cap|glove|bag|backpack|chair|cooler|mat|ball|tent|rod|reel)", re.I)


def main():
    s = session()
    have = {r["product_id"] for r in csv.DictReader(open(os.path.join(RAW, "A1_academy_products_apparel.csv"), encoding="utf-8"))}
    for b in BRANDS:
        flt = [("Filter", f"BrandId:eq:{b}"), ("Filter", "TotalReviewCount:gte:1")]
        n = get(s, "products", flt + [("Limit", "1")]).get("TotalResults") or 0
        tot = inn = app = app_in = 0; missed = []
        for o in range(0, n, 100):
            for x in get(s, "products", flt + [("Stats", "Reviews"), ("Limit", "100"), ("Offset", str(o))]).get("Results", []):
                st = x.get("ReviewStatistics") or {}
                if (st.get("LastSubmissionTime") or "")[:10] < "2024-01-01":
                    continue
                tot += 1; ok = x["Id"] in have; inn += ok
                nm = x.get("Name") or ""
                if APP.search(nm) and not NOT.search(nm):
                    app += 1; app_in += ok
                    if not ok and len(missed) < 6:
                        missed.append((nm[:60], x.get("CategoryId")))
        print(f"{b}: recent products {tot}, in basket {inn}; apparel-named {app}, in basket {app_in} "
              f"({(app_in / app * 100 if app else 0):.0f}%) missed e.g. {missed}", flush=True)


if __name__ == "__main__":
    main()
