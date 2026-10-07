"""R5: dicks.com product-catalog census via the Bazaarvoice front-door products API (no login, no key).

WHY: every dicks.com style is registered in Bazaarvoice (client "dsg"), active AND discontinued, with its
DKS item id. DKS item ids start with a 2-digit season-year code (e.g. 26JLOW... = 2026 season), followed by a
3-letter vendor code (JLO = CALIA vendor, DSG/QYF = DSG, KRM = VRST ...). The record also carries brand, current
category ancestry, active flag, the list of UPCs (= size x colour SKUs), and review stats (first/last review date).
So the catalog gives a census of styles by brand x season x category, with SKU depth and a launch proxy.

ENDPOINT: https://apps.bazaarvoice.com/bfd/v1/clients/dsg/api-products/cv2/resources/data/products.json
          header bv-bfd-token: 13107,main_site,en_US   (see X01_bv_reviews.py)
Limits: max Offset < ~500k; Id range filters not allowed -> partition by BrandId or CategoryAncestorId.

USAGE (weekly/monthly rerun; output is overwritten per run-date):
  python R5_bv_catalog.py brands            # all owned/exclusive brands -> raw/R5_catalog_brands_<date>.csv
  python R5_bv_catalog.py cats              # all-brand category census   -> raw/R5_catalog_cats_<date>.csv
  python R5_bv_catalog.py brands Nike adidas  # any extra brand ids
Then: python R5_analyze.py
Runtime: brands ~3 min; cats ~2,500 requests ~15 min with 6 threads.
"""
import csv, os, sys, datetime as dt
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from X01_bv_reviews import session_for, get, RAW

OWNED_CORE = ["Calia", "CALIA_by_Carrie_Underwood", "VRST", "DSG", "Maxfli", "Walter_Hagen", "Lady_Hagen",
              "Alpine_Design", "ETHOS", "Fitness_Gear", "Top_Flite", "Tommy_Armour_Golf", "Nishiki", "Quest",
              "PRIMED", "Field___Stream", "DICK_S_Sporting_Goods", "Tour_Trek", "Monarch"]
OWNED_EXT = ["Slazenger", "P-TEX", "Jawbone", "DBX"]   # on /c/dicks-exclusive-brands hub (X02-9); flagged separately
CATS = ["WomensApparel-129841", "MensApparel-129824", "BoysApparel-129859", "girls-apparel-footwear",
        "Golf-129239", "ExerciseFitness-128988", "CampingHiking-128904", "BikesCycling-128852", "Outdoor-236211",
        "ShopBySport-128771", "MensFootwear-129886", "WomensFootwear-129911", "YouthFootwear-129933",
        "Slides-Flip-Flops", "Footwear-129885", "WomensSwimsuits-129848"]
TODAY = dt.date.today().strftime("%Y%m%d")
COLS = ["query", "product_id", "pre", "vendor", "brand_id", "brand_name", "name", "category_id", "ancestry",
        "active", "n_upc", "upc_min", "upc_max", "upc_prefixes", "total_reviews", "avg_rating", "first_sub",
        "last_sub", "url"]


def slim(q, x):
    st = x.get("ReviewStatistics") or {}
    upcs = sorted(set((x.get("UPCs") or [])))
    pid = x.get("Id") or ""
    return [q, pid, pid[:2], pid[2:5].upper(), (x.get("Brand") or {}).get("Id"), (x.get("Brand") or {}).get("Name"),
            x.get("Name"), x.get("CategoryId"), "|".join(x.get("CategoryAncestryIds") or []), x.get("Active"),
            len(upcs), upcs[0] if upcs else "", upcs[-1] if upcs else "",
            "|".join(sorted({u[:6] for u in upcs})), st.get("TotalReviewCount"), st.get("AverageOverallRating"),
            st.get("FirstSubmissionTime"), st.get("LastSubmissionTime"), x.get("ProductPageUrl")]


def pull(filters, out_name):
    s = session_for("dsg")
    path = os.path.join(RAW, out_name)
    done = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            done = {r["query"] for r in csv.DictReader(f)}
    new = not os.path.exists(path)
    f = open(path, "a", newline="", encoding="utf-8")
    w = csv.writer(f)
    if new:
        w.writerow(COLS)
    for flt in filters:
        if flt in done:
            print("skip", flt); continue
        n = get(s, "dsg", "products", [("Filter", flt), ("Limit", "1")]).get("TotalResults") or 0
        print(flt, n, flush=True)

        def page(o):
            return get(s, "dsg", "products", [("Filter", flt), ("Stats", "Reviews"), ("Limit", "100"), ("Offset", str(o))])
        rows = 0
        with ThreadPoolExecutor(6) as ex:
            for r in ex.map(page, range(0, n, 100)):
                for x in r.get("Results", []):
                    w.writerow(slim(flt, x)); rows += 1
        f.flush()
        print("  rows", rows, flush=True)
    f.close()


if __name__ == "__main__":
    mode = sys.argv[1]
    extra = sys.argv[2:]
    if mode == "brands":
        pull([f"BrandId:eq:{b}" for b in (extra or OWNED_CORE + OWNED_EXT)], f"R5_catalog_brands_{TODAY}.csv")
    elif mode == "cats":
        pull([f"CategoryAncestorId:eq:{c}" for c in (extra or CATS)], f"R5_catalog_cats_{TODAY}.csv")
