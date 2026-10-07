"""G1: detect brand migrations (relabelling) among DKS owned brands in the dicks.com Bazaarvoice catalog.

Two detectors, both from existing raw files (no web calls):
 1. Review-family sharing: the same BV review_id attached to products of two different brands
    (BV product families keep reviews when a style is re-IDed / re-branded).
 2. Name matching: product names with the brand word stripped that exist under two different owned brands.
Outputs raw/G1_migration_pairs.csv (product pairs) and prints a summary.
Then quantifies how much of each brand's review growth (Apr-Aug 2024/25/26, PIE+ORG and ALL) is on migrated
(inherited) products.

RERUN: python G1_brand_migration.py   (after refreshing raw/X01_products_dsg.csv and raw/R1_reviews_owned.csv)
"""
import re, os
import pandas as pd

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70); pd.set_option("display.max_rows", 500)

p = pd.read_csv(os.path.join(RAW, "X01_products_dsg.csv"), low_memory=False)
r = pd.read_csv(os.path.join(RAW, "R1_reviews_owned.csv"), low_memory=False,
                usecols=["review_id", "product_id", "brand_id", "submission_time", "campaign_id", "is_syndicated"])

BRANDWORDS = ["fitness gear", "ethos", "dsg", "quest", "alpine design", "top flite", "top-flite", "maxfli",
              "tommy armour", "walter hagen", "lady hagen", "calia by carrie underwood", "calia", "vrst", "nishiki",
              "primed", "field & stream", "dick's sporting goods", "monarch", "prince"]


def norm(s):
    s = str(s).lower()
    for w in BRANDWORDS:
        s = s.replace(w, " ")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


print("== products by brand")
print(p.groupby("brand_id").agg(n=("product_id", "count"), rev=("total_reviews", "sum")).to_string())

# --- detector 1: shared review ids
g = r.groupby("review_id").brand_id.nunique()
multi = g[g > 1].index
m = r[r.review_id.isin(multi)]
pairs1 = m.groupby("review_id").brand_id.apply(lambda s: "|".join(sorted(set(s))))
print("\n== detector 1: review ids shared across brands")
print(pairs1.value_counts().to_string())

# --- detector 2: name match
p["key"] = p.name.map(norm)
k = p.groupby("key").brand_id.nunique()
keys = k[(k > 1)].index
mm = p[p.key.isin(keys) & (p.key.str.len() > 6)]
pairs2 = mm.groupby("key").brand_id.apply(lambda s: "|".join(sorted(set(s))))
print("\n== detector 2: normalized-name matches across brands (count of names)")
print(pairs2.value_counts().to_string())
out = mm.sort_values(["key", "brand_id"])[["key", "brand_id", "product_id", "name", "category_id", "active",
                                           "total_reviews", "first_sub", "last_sub"]]
out.to_csv(os.path.join(RAW, "G1_migration_name_pairs.csv"), index=False)
for pr in pairs2.value_counts().index:
    ks = pairs2[pairs2 == pr].index[:12]
    print("\n--", pr)
    print(mm[mm.key.isin(ks)].sort_values(["key", "brand_id"])[["brand_id", "product_id", "name", "active",
                                                                  "total_reviews", "first_sub"]].to_string())
