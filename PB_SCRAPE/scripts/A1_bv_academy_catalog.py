"""A1 step 1: Academy (academy.com) Bazaarvoice catalog for the apparel peer control.

(a) categories: pages categories.json (27k rows) -> raw/A1_academy_categories.csv (Id, Name, ParentId, URL).
(b) products:  for every category whose academy.com URL sits under men's/women's/boys'/girls' apparel (+ kids clothing),
    pages products.json (CategoryAncestorId filter, TotalReviewCount>=1, Stats=Reviews) and writes the UNION of products
    (deduplicated by product Id) -> raw/A1_academy_products_apparel.csv with brand, leaf category, basket, review stats.
Basket = from the leaf CategoryId's URL (womens / mens / boys / girls / kids); falls back to the ancestor category that
found the product.
RERUN: python A1_bv_academy_catalog.py cats ; python A1_bv_academy_catalog.py products
"""
import csv, os, re, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from A1_bv_academy_common import session, get, RAW

CATS = os.path.join(RAW, "A1_academy_categories.csv")
PRODS = os.path.join(RAW, "A1_academy_products_apparel.csv")
APPAREL_RE = re.compile(r"/c/(mens/mens-apparel|womens/womens-apparel|kids/boys-apparel|kids/girls-apparel|kids/kids-apparel|kids/toddler|kids/baby)", re.I)


def basket_of(url):
    u = (url or "").lower()
    if "/c/womens/womens-apparel" in u: return "womens"
    if "/c/mens/mens-apparel" in u: return "mens"
    if "/c/kids/boys-apparel" in u: return "boys"
    if "/c/kids/girls-apparel" in u: return "girls"
    if "/c/kids/" in u and ("apparel" in u or "clothing" in u or "toddler" in u or "baby" in u): return "kids_other"
    return ""


def cats():
    s = session()
    n = get(s, "categories", [("Limit", "1")]).get("TotalResults") or 0
    rows = []
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(lambda o: get(s, "categories", [("Limit", "100"), ("Offset", str(o))]), range(0, n, 100)):
            for x in r.get("Results", []):
                rows.append([x.get("Id"), x.get("Name"), x.get("ParentId"), x.get("CategoryPageUrl"), x.get("Active")])
    with open(CATS, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["id", "name", "parent_id", "url", "active"]); w.writerows(rows)
    print("categories", len(rows), "of", n)


def products():
    s = session()
    with open(CATS, encoding="utf-8") as f:
        cs = [r for r in csv.DictReader(f) if basket_of(r["url"])]
    print("apparel categories", len(cs), flush=True)
    url_of = {}
    with open(CATS, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            url_of[r["id"]] = r["url"]
    seen = {}
    flt0 = [("Filter", "TotalReviewCount:gte:1")]

    def pull(c):
        out = []
        flt = flt0 + [("Filter", f"CategoryAncestorId:eq:{c['id']}")]
        n = get(s, "products", flt + [("Limit", "1")]).get("TotalResults") or 0
        for o in range(0, n, 100):
            for x in get(s, "products", flt + [("Stats", "Reviews"), ("Limit", "100"), ("Offset", str(o))]).get("Results", []):
                out.append((c, x))
        return out
    with ThreadPoolExecutor(6) as ex:
        for i, res in enumerate(ex.map(pull, cs)):
            for c, x in res:
                if x["Id"] in seen:
                    continue
                st = x.get("ReviewStatistics") or {}
                leaf = x.get("CategoryId")
                b = basket_of(url_of.get(leaf, "")) or basket_of(c["url"])
                seen[x["Id"]] = [x["Id"], (x.get("Brand") or {}).get("Id"), (x.get("Brand") or {}).get("Name"), x.get("Name"),
                                 leaf, "|".join(x.get("CategoryAncestryIds") or []), b, c["id"], x.get("Active"),
                                 st.get("TotalReviewCount"), st.get("AverageOverallRating"), st.get("FirstSubmissionTime"),
                                 st.get("LastSubmissionTime")]
            if i % 50 == 0:
                print(i, len(seen), flush=True)
    with open(PRODS, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["product_id", "brand_id", "brand_name", "name", "category_id", "ancestry", "basket", "found_via",
                    "active", "total_reviews", "avg_rating", "first_sub", "last_sub"])
        w.writerows(seen.values())
    print("products", len(seen))


if __name__ == "__main__":
    {"cats": cats, "products": products}[sys.argv[1]]()
