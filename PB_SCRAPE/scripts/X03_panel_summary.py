"""X03: summarise the matched-page y/y panel (raw/X03_cc_panel_<tag>.csv).
Owned-brand pages: total product count y/y, sale-flag count y/y.
Category pages with brand facet in both periods: owned facet count and share y/y (sum and median).
Usage: python X03_panel_summary.py AugOct
"""
import sys, os, csv, re, statistics
RAW = os.path.join(os.path.dirname(__file__), "..", "raw")
tag = sys.argv[1] if len(sys.argv) > 1 else "AugOct"
rows = list(csv.DictReader(open(os.path.join(RAW, f"X03_cc_panel_{tag}.csv"), encoding="utf-8")))
OWNED = re.compile(r"^f/(calia|vrst|dsg|maxfli|walter-hagen|alpine-design|ethos|fitness-gear|nishiki|quest|top-flite|tommy-armour)")
num = lambda x: int(x) if x not in (None, "", "None") else None

print("== OWNED-BRAND PAGES: product count base -> cmp")
tb = tc = 0
for r in rows:
    if OWNED.search(r["slug"]):
        b, c = num(r["total_base"]), num(r["total_cmp"])
        sb, sc = num(r["sale_base"]), num(r["sale_cmp"])
        print(f"  {r['slug']:<60} {r['ts_base'][:8]} {b} -> {r['ts_cmp'][:8]} {c}  sale {sb}->{sc}")
        if b and c:
            tb += b; tc += c
print(f"  SUM owned-page products {tb} -> {tc} ({(tc / tb - 1) * 100:.1f}%)" if tb else "")

for label, keep in (("REGULAR", lambda s: not re.search(r"sale|clearance", s)), ("SALE/CLEARANCE", lambda s: bool(re.search(r"sale|clearance", s)))):
  print(f"== {label} CATEGORY PAGES with brand facet both periods")
  fb = fc = ob = oc = n = 0
  shares = []
  for r in rows:
    if OWNED.search(r["slug"]) or not keep(r["slug"]):
        continue
    a, b2 = num(r["facet_sum_base"]), num(r["facet_sum_cmp"])
    t1, t2 = num(r["total_base"]), num(r["total_cmp"])
    o1, o2 = num(r["facet_owned_base"]), num(r["facet_owned_cmp"])
    full = a and b2 and t1 and t2 and a >= 0.95 * t1 and b2 >= 0.95 * t2
    if full and o1 is not None and o2 is not None and (o1 + o2) > 0:
        n += 1
        fb += a; fc += b2; ob += o1; oc += o2
        shares.append((o2 / b2) - (o1 / a))
        print(f"  {r['slug']:<50} {r['ts_base'][:8]} owned {o1}/{a} ({o1 / a:.1%}) -> {r['ts_cmp'][:8]} {o2}/{b2} ({o2 / b2:.1%})  {r['owned_detail_cmp'][:80]}")
  if n:
    print(f"  N={n} pages: owned facet {ob} -> {oc} ({(oc / ob - 1) * 100:+.1f}%), all-brand facet {fb} -> {fc} ({(fc / fb - 1) * 100:+.1f}%)")
    print(f"  pooled owned share {ob / fb:.2%} -> {oc / fc:.2%}; median page share change {statistics.median(shares) * 100:+.2f}pp; pages up {sum(1 for s in shares if s > 0)}/{n}")
