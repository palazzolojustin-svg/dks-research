"""G1: pull the full Bazaarvoice product records (UPC list, FamilyIds, review stats) for every DKS owned/exclusive
brand, for brand-migration (relabelling) detection. Same physical item (UPC) or same BV family under two brands
= relabel.

ENDPOINT: BV front door (see X01_bv_reviews.py), products.json Filter=BrandId:eq:<id>.
USAGE:  python G1_bv_upc_pull.py [dsg|golfgalaxy] [extra BrandIds...]
OUT:    raw/G1_products_upc_<client>.jsonl  (one product per line: id, brand, name, cat, active, upcs, families,
        total_reviews, first_sub, last_sub)
Runtime ~2-4 min (≈170 requests).
"""
import os, sys, json
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from X01_bv_reviews import session_for, get, RAW

BRANDS = ["Calia", "CALIA_by_Carrie_Underwood", "VRST", "DSG", "Maxfli", "Walter_Hagen", "Lady_Hagen",
          "Alpine_Design", "ETHOS", "Fitness_Gear", "Top_Flite", "Tommy_Armour_Golf", "Nishiki", "Quest",
          "PRIMED", "Field___Stream", "DICK_S_Sporting_Goods", "Tour_Trek", "Monarch", "Slazenger", "P-TEX",
          "Jawbone", "DBX", "Prince", "Foxburg", "FOXBURG", "Foxburg_Golf_Co_", "CALIA_Club", "Startline", "STARTLINE"]


def slim(x):
    st = x.get("ReviewStatistics") or {}
    return {"id": x["Id"], "brand": (x.get("Brand") or {}).get("Id"), "brand_name": (x.get("Brand") or {}).get("Name"),
            "name": x.get("Name"), "cat": x.get("CategoryId"), "anc": x.get("CategoryAncestryIds"),
            "active": x.get("Active"), "upcs": x.get("UPCs") or [], "families": x.get("FamilyIds") or [],
            "total_reviews": st.get("TotalReviewCount"), "first_sub": st.get("FirstSubmissionTime"),
            "last_sub": st.get("LastSubmissionTime"), "url": x.get("ProductPageUrl")}


def main(client, brands):
    s = session_for(client)
    out = os.path.join(RAW, f"G1_products_upc_{client}.jsonl")
    seen = set()
    with open(out, "w", encoding="utf-8") as f:
        for b in brands:
            first = get(s, client, "products", [("Filter", f"BrandId:eq:{b}"), ("Limit", "1")])
            n = first.get("TotalResults") or 0
            print(client, b, n, flush=True)
            if not n:
                continue

            def page(o):
                return get(s, client, "products", [("Filter", f"BrandId:eq:{b}"), ("Stats", "Reviews"),
                                                   ("Limit", "100"), ("Offset", str(o))])
            with ThreadPoolExecutor(6) as ex:
                for r in ex.map(page, range(0, n, 100)):
                    for x in r.get("Results", []):
                        if x["Id"] in seen:
                            continue
                        seen.add(x["Id"])
                        f.write(json.dumps(slim(x)) + "\n")
    print("wrote", len(seen), out)


if __name__ == "__main__":
    client = sys.argv[1] if len(sys.argv) > 1 else "dsg"
    main(client, BRANDS + sys.argv[2:])
