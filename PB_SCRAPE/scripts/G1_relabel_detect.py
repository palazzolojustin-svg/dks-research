"""G1: definitive relabel detection among DKS owned/exclusive brands.
Edges between product ids of DIFFERENT brands when they share (a) a UPC, (b) a BV FamilyId, or (c) a review id
(raw/R1_reviews_owned.csv). Plus (d) "inherited" review history: a product whose first review predates its season
prefix by >=2 years (reviews moved onto a new id) - origin brand found via name match.
Outputs raw/G1_relabel_edges.csv and raw/G1_relabel_products.csv (product -> origin brand, method).
RERUN: python G1_bv_upc_pull.py dsg ; python G1_relabel_detect.py
"""
import os, json, re, itertools
import pandas as pd
from collections import defaultdict

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500); pd.set_option("display.max_colwidth", 60)

P = [json.loads(l) for l in open(os.path.join(RAW, "G1_products_upc_dsg.jsonl"), encoding="utf-8")]
p = pd.DataFrame(P)
p["season"] = p.id.str[:2].where(p.id.str[:2].str.isdigit())
brand_of = dict(zip(p.id, p.brand))

edges = []
# (a) UPC
upc = defaultdict(set)
for x in P:
    for u in x["upcs"]:
        upc[u].add(x["id"])
for u, ids in upc.items():
    bs = {brand_of[i] for i in ids}
    if len(bs) > 1:
        for a, b in itertools.combinations(sorted(ids), 2):
            if brand_of[a] != brand_of[b]:
                edges.append((a, b, "upc", u))
# (b) family
fam = defaultdict(set)
for x in P:
    for fm in x["families"]:
        fam[fm].add(x["id"])
for fm, ids in fam.items():
    bs = {brand_of[i] for i in ids}
    if len(bs) > 1:
        for a, b in itertools.combinations(sorted(ids), 2):
            if brand_of[a] != brand_of[b]:
                edges.append((a, b, "family", fm))
# (c) shared review ids
r = pd.read_csv(os.path.join(RAW, "R1_reviews_owned.csv"), usecols=["review_id", "product_id", "brand_id"], low_memory=False)
g = r.groupby("review_id").product_id.apply(lambda s: tuple(sorted(set(s))))
seen = set()
for ids in g[g.map(len) > 1]:
    for a, b in itertools.combinations(ids, 2):
        if a in brand_of and b in brand_of and brand_of[a] != brand_of[b] and (a, b) not in seen:
            seen.add((a, b)); edges.append((a, b, "review", ""))

e = pd.DataFrame(edges, columns=["a", "b", "method", "key"]).drop_duplicates(["a", "b", "method"])
e["brand_a"] = e.a.map(brand_of); e["brand_b"] = e.b.map(brand_of)
e["pair"] = [ "|".join(sorted([x, y])) for x, y in zip(e.brand_a, e.brand_b)]
e.to_csv(os.path.join(RAW, "G1_relabel_edges.csv"), index=False)
print("== cross-brand edges by method x brand pair (distinct product pairs)")
print(pd.crosstab(e.pair, e.method).sort_values("upc", ascending=False).to_string())

# direction: older season -> newer season
def seas(i):
    s = i[:2]
    return int(s) if s.isdigit() else 0
rows = []
for _, x in e.iterrows():
    a, b = x.a, x.b
    if seas(a) > seas(b):
        a, b = b, a
    rows.append((a, brand_of[a], seas(a), b, brand_of[b], seas(b), x.method))
d = pd.DataFrame(rows, columns=["old_id", "old_brand", "old_season", "new_id", "new_brand", "new_season", "method"])
d = d[d.old_brand != d.new_brand]
flow = d.drop_duplicates(["old_id", "new_id"]).groupby(["old_brand", "new_brand"]).agg(
    pairs=("new_id", "size"), new_ids=("new_id", "nunique"), first_new_season=("new_season", "min"),
    last_new_season=("new_season", "max")).sort_values("new_ids", ascending=False)
print("\n== directional flows (old style season -> new style season)")
print(flow.to_string())
d.to_csv(os.path.join(RAW, "G1_relabel_directional.csv"), index=False)
# examples
for (ob, nb), _ in flow.head(14).iterrows():
    ex = d[(d.old_brand == ob) & (d.new_brand == nb)].drop_duplicates("new_id").head(6)
    print(f"\n-- {ob} -> {nb}")
    for _, y in ex.iterrows():
        print("  ", y.old_id, P[[q['id'] for q in P].index(y.old_id)]['name'][:45], "=>", y.new_id,
              P[[q['id'] for q in P].index(y.new_id)]['name'][:45], y.method)
