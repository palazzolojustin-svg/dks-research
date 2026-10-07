"""R12: fetch the few Common Crawl captures of dicks.com listing pages archived with selectedSort=1 ("Top Sellers")
and compare owned share of the top-24 with the 2026-10-07 live census (X02, sort='top').
Rerun: python PB_SCRAPE\\scripts\\R12_cc_sorted.py
"""
import glob, os, re, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R9_cc_common import load_idx, fetch_warc
from R12_common import RAW, parse_plp

live = pd.read_csv(os.path.join(RAW, "X02_dsg_products_20261007.csv"))
live = live[live["sort"] == "top"]
for f in sorted(glob.glob(os.path.join(RAW, "X03_cc", "*_f.jsonl"))):
    for r in load_idx(f):
        if str(r.get("status")) == "200" and "selectedSort=1" in r["url"]:
            t = fetch_warc(r)
            p = parse_plp(t) if t else None
            if not p:
                print(r["url"], "no data"); continue
            slug = re.search(r"/f/([^?]+)", r["url"]).group(1)
            pr = p["products"][:24]
            print(f"{r['timestamp'][:8]} {r['url']}\n   sort={p['sort']} total={p['total']} owned in top-24: {sum(x[2] for x in pr)}/{len(pr)}"
                  f"  brands top-24: {[x[1] for x in pr]}")
            lv = live[(live.cat == slug) & (live["rank"] <= 24)]
            if len(lv):
                print(f"   live 2026-10-07 top-24 owned: {int(lv.vert.sum())}/{len(lv)}  brands: {lv.brand.tolist()}")
