"""H03: filter raw/H03_tabs_projects.csv to DKS major projects (>= $1M, completion >= 2023-06) -> raw/H03_tabs_dks_major.csv
Rerun: python H03_tabs_summary.py
"""
import pandas as pd, re, os
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
d = pd.read_csv(os.path.join(RAW, "H03_tabs_projects.csv"))
d["costn"] = pd.to_numeric(d["cost"].astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce")
d["sq"] = pd.to_numeric(d["sqft"].astype(str).str.replace(r"[^0-9]", "", regex=True), errors="coerce")
d["comp"] = pd.to_datetime(d["completion"], errors="coerce")
pat = r"dick'?s sport|house of sport|\bdsg\b|dicks sport|golf galaxy|public lands|dick's #|dick's - |^dick's$|dick's house"
m = d.apply(lambda r: bool(re.search(pat, (str(r["name"]) + " | " + str(r["facility"]) + " | " + str(r["owner"])).lower())), axis=1)
d = d[m & (d["comp"] >= "2023-06-01") & (d["costn"] >= 1e6)].sort_values("comp")
d["psf"] = d["costn"] / d["sq"]
d.to_csv(os.path.join(RAW, "H03_tabs_dks_major.csv"), index=False)
for _, r in d.iterrows():
    print(r["project"], "|", str(r["name"])[:45], "|", str(r["address"])[:55], "|", r["start"], "->", r["completion"],
          "| $%.1fM" % (r["costn"] / 1e6), "|", (int(r["sq"]) if r["sq"] == r["sq"] else ""), "| psf", (round(r["psf"]) if r["psf"] == r["psf"] else ""),
          "| tenantfunded", r["tenant_funded"], "|", str(r["owner"])[:35], "|", str(r["worktype"])[:12], "|", str(r["scope"])[:120])
