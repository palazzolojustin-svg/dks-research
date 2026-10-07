"""R8: quarterly owned / national / ambiguous / unknown split of DKS direct imports (calendar quarters, sea only), 2023-Q1 .. 2026-Q3.
Inputs: raw/R8_supplier_panel.csv (R8_panel.py), entity monthly totals (latest of raw/R8_iy_company_dick-s-merchandising-and-supply-cha_monthly.csv
or raw/X04_dmsc_monthly_2026-10-07.csv).
Outputs: raw/R8_quarterly_split.csv, raw/R8_quarterly_by_group.csv
'unknown' = entity total minus the classified union panel (suppliers outside the top-50 lists).
Owned share is shown three ways: owned/(owned+national) [classified], owned/entity [lower bound], and ex-consolidators.
Rerun: python R8_panel.py ; python R8_quarterly.py
"""
import os, glob
import pandas as pd

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
p = pd.read_csv(os.path.join(RAW, "R8_supplier_panel.csv"))
mfiles = sorted(glob.glob(os.path.join(RAW, "R8_dmsc_monthly_*.csv"))) or [os.path.join(RAW, "X04_dmsc_monthly_2026-10-07.csv")]
m = pd.read_csv(mfiles[-1])
m["q"] = m.month.str[:4] + "-" + ((m.month.str[5:7].astype(int) - 1) // 3 * 3 + 1).map("{:02d}".format)
ent = m.groupby("q")[["shipments", "teu", "weight_kg"]].sum().rename(columns={"shipments": "ent_ship", "teu": "ent_teu", "weight_kg": "ent_kg"})

p = p[(p.q >= "2023-01") & (p.q <= "2026-07")]
out = []
for q, g in p.groupby("q"):
    r = {"q": q}
    for cls in ["OWNED", "NATIONAL", "AMBIGUOUS"]:
        gg = g[g.cls == cls]
        r[f"{cls.lower()}_ship"] = gg.ship.sum(); r[f"{cls.lower()}_kg"] = gg.kg.sum(); r[f"{cls.lower()}_teu"] = gg.teu.sum()
    oc = g[(g.cls == "OWNED") & g.consolidator]
    r["owned_consol_ship"] = oc.ship.sum(); r["owned_consol_kg"] = oc.kg.sum(); r["owned_consol_teu"] = oc.teu.sum()
    cds = g[g.slug.str.startswith("century-distribution-systems")]
    r["cds_kg"] = cds.kg.sum(); r["cds_ship"] = cds.ship.sum()
    sl = g[(g.cls == "OWNED") & (g.segment == "Softline")]
    r["owned_softline_kg"] = sl.kg.sum(); r["owned_softline_ship"] = sl.ship.sum()
    out.append(r)
d = pd.DataFrame(out).set_index("q").join(ent, how="left").reset_index()
d["unknown_kg"] = d.ent_kg - d.owned_kg - d.national_kg - d.ambiguous_kg
d["unknown_ship"] = d.ent_ship - d.owned_ship - d.national_ship - d.ambiguous_ship
d["coverage_kg"] = 1 - d.unknown_kg / d.ent_kg
for basis in ["kg", "ship", "teu"]:
    d[f"own_share_classified_{basis}"] = d[f"owned_{basis}"] / (d[f"owned_{basis}"] + d[f"national_{basis}"])
    d[f"own_share_classified_exCDS_{basis}"] = (d[f"owned_{basis}"] - (d["cds_" + basis] if basis != "teu" else 0)) / (
        d[f"owned_{basis}"] - (d["cds_" + basis] if basis != "teu" else 0) + d[f"national_{basis}"])
d["own_share_of_entity_kg"] = d.owned_kg / d.ent_kg
d["own_share_of_entity_ship"] = d.owned_ship / d.ent_ship
d["own_share_of_entity_exCDS_kg"] = (d.owned_kg - d.cds_kg) / (d.ent_kg - d.cds_kg)
d["own_share_classified_exALLconsol_kg"] = (d.owned_kg - d.owned_consol_kg) / (d.owned_kg - d.owned_consol_kg + d.national_kg)
d.to_csv(os.path.join(RAW, "R8_quarterly_split.csv"), index=False, float_format="%.4f")

g2 = p[p.cls == "OWNED"].pivot_table(index="grp", columns="q", values="kg", aggfunc="sum").fillna(0)
g2s = p[p.cls == "OWNED"].pivot_table(index="grp", columns="q", values="ship", aggfunc="sum").fillna(0)
pd.concat({"kg": g2, "ship": g2s}).to_csv(os.path.join(RAW, "R8_quarterly_by_group.csv"))

if __name__ == "__main__":
    pd.set_option("display.width", 250, "display.max_columns", 50)
    cols = ["q", "ent_ship", "ent_kg", "owned_ship", "owned_kg", "national_ship", "national_kg", "ambiguous_kg", "unknown_kg", "cds_kg", "coverage_kg",
            "own_share_classified_kg", "own_share_classified_exCDS_kg", "own_share_classified_exALLconsol_kg", "own_share_classified_ship",
            "own_share_of_entity_kg", "own_share_of_entity_exCDS_kg", "own_share_of_entity_ship"]
    print(d[cols].round(3).to_string(index=False))
    print((g2 / 1000).round(0).to_string())
    print(g2s.to_string())
