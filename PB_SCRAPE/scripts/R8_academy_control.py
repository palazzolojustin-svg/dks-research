"""R8: Academy Sports (ImportYeti company/academy) control: private-label vs national split of Academy's direct imports by quarter,
tagged from vendor BOL text. NOTE: the Academy page carries CBP manifest confidentiality 2020-07 .. 2025-01, so supplier-level data is only
usable from 2025-Q3; compare 2025-Q3/Q4 with 2026. Input raw/X04_iy_company_academy.txt (or raw/R8_iy_company_academy.txt if newer).
Output raw/R8_academy_control.csv. Rerun: python R8_iy_fetch.py company academy ; python R8_academy_control.py
"""
import os, re, json
import pandas as pd
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
src = os.path.join(RAW, "R8_iy_company_academy.txt")
if not os.path.exists(src):
    src = os.path.join(RAW, "X04_iy_company_academy.txt")
big = open(src, encoding="utf-8").read()
OWN = re.compile(r"mosaic|magellan|\bmag\b|\bbcg\b|academy sports outdoors|\baso\b|brazos|freely|game winner|tellico|laguna madre|ozone|agame|r\.?o\.?w|outdoor gourmet", re.I)
NAT = re.compile(r"stiga|nordictrack|schwinn|\bsch\b|nexgrill|cartridge|shotgun|rifle|freestyle rocker|comfort pro|kickback|triumph", re.I)
rows = []
for v in re.finditer(r'\{"shipments_12m":(\d+),"vendor_name":"([^"]*)".*?"country":"([^"]*)".*?"url":"/supplier/([^"]*)".*?"product_descriptions":"([^"]*)","vendor_time_series":(\{.*?\}\}),', big):
    desc = v.group(5)
    cls = "PRIVATE" if OWN.search(desc) else ("NATIONAL" if NAT.search(desc) else "UNTAGGED")
    for k, x in json.loads(v.group(6)).items():
        rows.append(dict(vendor=v.group(2), cls=cls, q=f"{k[6:]}-{k[3:5]}", ship=x["shipments"], kg=x["weight"]))
d = pd.DataFrame(rows)
d = d[d.q >= "2025-07"]
t = d.pivot_table(index="cls", columns="q", values="kg", aggfunc="sum").fillna(0)
t.loc["private_share_of_tagged"] = t.loc["PRIVATE"] / (t.loc["PRIVATE"] + t.loc["NATIONAL"])
t.to_csv(os.path.join(RAW, "R8_academy_control.csv"))
if __name__ == "__main__":
    print(t.round(3).to_string())
    print(d.groupby(["cls", "vendor"]).kg.sum().sort_values(ascending=False).head(40).to_string())
