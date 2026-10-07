"""R5: UPC 'clock' - how fast DKS consumes its own GS1 UPC numbers (each UPC = one sellable SKU, size x colour).
DKS-made goods (owned brands + DKS-sourced licensed brands such as Reebok, Prince, Slazenger, Umbro) carry UPCs from
DKS's GS1 company prefixes, used in sequence: 889751/889752 -> 194375 -> 196358 -> 198690 -> 199980.
Each style's lowest UPC ~ the moment its SKUs were set up. We date UPC ranges with the first-review date of styles
(a lagging proxy for launch) and compute per-block quarterly frontiers, then UPCs consumed per 12 months.
Input : raw/R5_catalog_brands_*.csv and raw/R5_catalog_cats_*.csv (latest)
Output: raw/R5_upc_clock_block_quarter.csv, printed table
Rerun : python R5_upc_clock.py
"""
import glob, os
import pandas as pd

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
BLK = ["889751", "889752", "194375", "196358", "198690", "199980"]
fs = [sorted(glob.glob(os.path.join(RAW, p)))[-1] for p in ("R5_catalog_brands_*.csv", "R5_catalog_cats_*.csv")]
d = pd.concat([pd.read_csv(f, dtype=str) for f in fs]).drop_duplicates("product_id")
d = d[d.upc_min.fillna("").str[:6].isin(BLK)].copy()
d["blk"] = d.upc_min.str[:6]
d["item"] = d.upc_min.str[6:11].astype(int)
d["fs"] = pd.to_datetime(d.first_sub, errors="coerce", utc=True).dt.tz_localize(None)
z = d.dropna(subset=["fs"])
z = z[(z.fs >= "2021-01-01")]
z["q"] = z.fs.dt.to_period("Q")
g = z.groupby(["blk", "q"]).item.agg(n="size", med="median", p75=lambda s: s.quantile(.75), p90=lambda s: s.quantile(.9)).reset_index()
g.to_csv(os.path.join(RAW, "R5_upc_clock_block_quarter.csv"), index=False)
pd.set_option("display.width", 200); pd.set_option("display.max_rows", 300)
print(g[g.n >= 15].to_string())

# block exhaustion dates: first quarter in which the next block's styles appear in volume (>=15 reviewed styles)
for b in BLK:
    t = g[(g.blk == b) & (g.n >= 15)]
    if len(t):
        print(b, "active quarters", t.q.min(), "->", t.q.max(), "max med item", int(t.med.max()))
