"""R8: MONTHLY series Jan-2023 .. Sep-2026 of DKS direct imports (entity Dick's Merchandising & Supply Chain, sea), split
owned / national / ambiguous / unknown.
Method: entity monthly shipments/TEU/kg are actual (ImportYeti company series). The split is ALLOCATED: each month gets its calendar
quarter's class shares from the supplier x quarter panel (R8_quarterly.py / R8_value_ieepa.py), because ImportYeti gives supplier volumes
only by quarter. Jul-Sep 2026 also carries a BOL-level check (R8_bol_monthly.py fixed panel). Value columns use R8_value_ieepa.py $/kg.
Output: raw/R8_monthly_split.csv   Rerun: python R8_panel.py; python R8_quarterly.py; python R8_value_ieepa.py; python R8_bol_monthly.py; python R8_monthly_split.py
"""
import os, glob
import pandas as pd
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
mfiles = sorted(glob.glob(os.path.join(RAW, "R8_dmsc_monthly_*.csv"))) or [os.path.join(RAW, "X04_dmsc_monthly_2026-10-07.csv")]
m = pd.read_csv(mfiles[-1])
m = m[(m.month >= "2023-01") & (m.month <= "2026-09")].copy()
m["q"] = m.month.str[:4] + "-" + ((m.month.str[5:7].astype(int) - 1) // 3 * 3 + 1).map("{:02d}".format)
qs = pd.read_csv(os.path.join(RAW, "R8_quarterly_split.csv")).set_index("q")
vv = pd.read_csv(os.path.join(RAW, "R8_value_weighted_quarterly.csv")).set_index("q")
rows = []
for _, r in m.iterrows():
    s = qs.loc[r.q]; v = vv.loc[r.q]
    sh = {k: s[f"{k}_kg"] / s.ent_kg for k in ["owned", "national", "ambiguous", "unknown"]}
    usd_per_kg = v.entity_usd_est / v.entity_kg
    rows.append(dict(month=r.month, cal_q=r.q, shipments=r.shipments, teu=r.teu, kg=r.weight_kg,
                     owned_kg_alloc=round(r.weight_kg * sh["owned"]), national_kg_alloc=round(r.weight_kg * sh["national"]),
                     ambiguous_kg_alloc=round(r.weight_kg * sh["ambiguous"]), unknown_kg_alloc=round(r.weight_kg * sh["unknown"]),
                     owned_apparel_kg_alloc=round(r.weight_kg * v.owned_apparel_kg / v.entity_kg),
                     est_value_usd=round(r.weight_kg * usd_per_kg), owned_value_usd_alloc=round(r.weight_kg * usd_per_kg * v.own_share_val_of_entity),
                     owned_share_kg_classified_q=round(s.own_share_classified_kg, 3), owned_share_value_classified_q=round(v.own_share_val_classified, 3),
                     owned_share_value_classified_exCDS_q=round(v.own_share_val_classified_exCDS, 3), method="quarter-share allocation"))
o = pd.DataFrame(rows)
b = pd.read_csv(os.path.join(RAW, "R8_bol_monthly_split.csv"))
fx = b[b.month.str.contains("fixed")].copy(); fx["month"] = fx.month.str[:7]
o = o.merge(fx[["month", "owned_bols", "national_bols", "owned_share_bols"]].rename(columns={"owned_bols": "bolcheck_owned_bols", "national_bols": "bolcheck_national_bols", "owned_share_bols": "bolcheck_owned_share"}), on="month", how="left")
o.to_csv(os.path.join(RAW, "R8_monthly_split.csv"), index=False)
if __name__ == "__main__":
    pd.set_option("display.width", 250)
    print(o.drop(columns=["method"]).to_string(index=False))
