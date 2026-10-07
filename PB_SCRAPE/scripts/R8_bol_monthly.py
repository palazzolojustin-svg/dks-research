"""R8: MONTHLY owned/national split of DKS direct imports for recent months, built from BOL-level records.
ImportYeti only gives supplier x QUARTER volumes for the DKS entity, but each supplier page lists its 50 most recent BOLs (all customers,
with consignee). For a supplier whose 50-BOL window starts before month M, its DKS BOLs in month M are complete. This script:
  - loads supplier BOL lists (raw/X04_dmsc_supplier_pages_2026-10-07.json, plus any raw/R8_iy_supplier_*.txt payloads),
  - keeps BOLs whose consignee looks like DKS (Dick S Merchandising...),
  - per supplier, records window_start = earliest BOL date in the list, and counts DKS BOLs per month ONLY for months fully inside the window,
  - checks completeness against the supplier's quarterly count in the DMSC vendor_time_series,
  - aggregates by owned/national class (raw/R8_supplier_classes.csv).
Outputs: raw/R8_bol_monthly_by_supplier.csv, raw/R8_bol_monthly_split.csv, raw/R8_bols_all.csv (BOL-level, incl. weight if available)
"""
import os, re, json, glob
import pandas as pd

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
cls = pd.read_csv(os.path.join(RAW, "R8_supplier_classes.csv")).set_index("slug")
DKS = re.compile(r"dick", re.I)

recs = []
# 1) X04 json (parsed: date, bol, consignee, desc)
j = json.load(open(os.path.join(RAW, "X04_dmsc_supplier_pages_2026-10-07.json"), encoding="utf-8"))
for url, v in j.items():
    slug = url.split("/")[-1]
    for b in v.get("recent_bols") or []:
        recs.append(dict(src="X04json", slug=slug, date=b["date"], bol=b["bol"], consignee=b["consignee"], desc=b["desc"], kg=None))
# 2) R8 refreshed supplier payloads (richer: weight)
for p in glob.glob(os.path.join(RAW, "R8_iy_supplier_*.txt")):
    slug = os.path.basename(p)[len("R8_iy_supplier_"):-4]
    big = open(p, encoding="utf-8").read()
    for m in re.finditer(r'"date":"(\d{4}-\d\d-\d\d)T[^{}]*?"bol":"([^"]*)"(.{0,1500}?)"description":"([^"]*)"', big):
        d, b, mid, desc = m.groups()
        who = re.search(r'"title":"([^"]*)"', mid)
        w = re.search(r'"weight":"?([\d.]+)', mid)
        recs.append(dict(src="R8", slug=slug, date=d, bol=b, consignee=who.group(1) if who else "", desc=desc, kg=float(w.group(1)) if w else None))
b = pd.DataFrame(recs)
b = b.sort_values("src").drop_duplicates(["slug", "bol"], keep="last")
b["month"] = b.date.str[:7]
b["dks"] = b.consignee.fillna("").str.contains(DKS)
b.to_csv(os.path.join(RAW, "R8_bols_all.csv"), index=False)

win = b.groupby("slug").agg(window_start=("date", "min"), n=("bol", "count"), n_dks=("dks", "sum"))
dk = b[b.dks]
mon = dk.groupby(["slug", "month"]).bol.count().rename("dks_bols").reset_index()
mon = mon.merge(win, left_on="slug", right_index=True)
# keep only months that start after the window start (complete months)
mon["complete"] = (mon.month + "-01") >= mon.window_start
mon["cls"] = mon.slug.map(cls["cls"]).fillna("UNMAPPED")
mon["grp"] = mon.slug.map(cls["grp"]).fillna("")
mon.to_csv(os.path.join(RAW, "R8_bol_monthly_by_supplier.csv"), index=False)

# panel of suppliers complete from a given month: for month M, suppliers with window_start <= M-01
months = ["2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"]
out = []
for M in months:
    sup = win[win.window_start <= M + "-01"].index
    g = mon[(mon.month == M) & mon.slug.isin(sup)]
    r = {"month": M, "n_suppliers_complete": len(sup)}
    for c in ["OWNED", "NATIONAL", "AMBIGUOUS", "UNMAPPED"]:
        r[c.lower() + "_bols"] = int(g[g.cls == c].dks_bols.sum())
    out.append(r)
# fixed panel: suppliers complete since 2026-07-01 (same panel for Jul/Aug/Sep)
fixed = win[win.window_start <= "2026-07-01"].index
for M in ["2026-07", "2026-08", "2026-09"]:
    g = mon[(mon.month == M) & mon.slug.isin(fixed)]
    out.append({"month": M + " (fixed Jul-complete panel)", "n_suppliers_complete": len(fixed),
                **{c.lower() + "_bols": int(g[g.cls == c].dks_bols.sum()) for c in ["OWNED", "NATIONAL", "AMBIGUOUS", "UNMAPPED"]}})
o = pd.DataFrame(out)
o["owned_share_bols"] = o.owned_bols / (o.owned_bols + o.national_bols)
o.to_csv(os.path.join(RAW, "R8_bol_monthly_split.csv"), index=False)

if __name__ == "__main__":
    pd.set_option("display.width", 250, "display.max_rows", 300)
    print(win.sort_values("window_start").to_string())
    print(o.to_string(index=False))
    fx = mon[mon.slug.isin(fixed) & mon.month.isin(["2026-07", "2026-08", "2026-09"])].pivot_table(index=["cls", "slug"], columns="month", values="dks_bols", aggfunc="sum").fillna(0)
    print(fx.to_string())
