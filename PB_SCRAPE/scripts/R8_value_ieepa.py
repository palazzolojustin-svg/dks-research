"""R8: (1) value-weighted owned share of DKS direct imports by calendar quarter; (2) reconciliation of the IEEPA refund with import value.

Value = ImportYeti gross kg x assumed customs $/kg (gross) by product group. $/kg anchors = UN Comtrade US-import unit values 2025
(raw/R8_us_import_unit_values*.csv; HS4 knit apparel 6103/6104/6110 ~$26-30/kg net from VN/KH/ID; 950691 fitness ~$7; 950632 golf balls ~$19.5;
940179 seats ~$5.9; 871680 wagons ~$6.2; 950699 ~$10.6), converted to gross weight with net/gross = 1/1.2 (ASSUMPTION).
IEEPA rates by origin and month are public tariff schedules (outside the folder; see R8.md). All outputs are INFERENCE.
Inputs: raw/R8_supplier_panel.csv, raw/R8_supplier_classes.csv, entity monthly CSV.
Outputs: raw/R8_value_weighted_quarterly.csv, raw/R8_ieepa_reconciliation.csv
Rerun: python R8_value_ieepa.py [apparel_usd_per_kg_net]   (default 28)
"""
import os, sys, glob
import pandas as pd

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
APP_NET = float(sys.argv[1]) if len(sys.argv) > 1 else 28.0
G2N = 1.2
NET = {  # $/kg NET by group
    "Athletic apparel direct (CALIA/DSG/VRST)": APP_NET, "Apparel via consolidator (CDS/APL/Phi)": APP_NET,
    "Golf apparel (MGA/WGH codes; INFERENCE Walter Hagen)": APP_NET, "Golf hardgoods (Maxfli/Top-Flite/WH/TA)": 25.0,
    "Fitness (ETHOS/DSG)": 7.0, "Outdoor/camp (Quest/Alpine Design/DSG)": 6.0, "Bikes (Nishiki)": 6.0,
    "Team sports/games (DSG)": 9.0, "Footwear (DSG boots)": 10.0, "Other owned": 9.0, "NATIONAL": 6.5, "AMBIGUOUS": 6.0}
import json
CH_NET = {"61": APP_NET, "62": APP_NET, "64": 15.0, "95": 9.0, "94": 6.0, "87": 6.0, "63": 5.0, "39": 5.0, "42": 12.0}
GOLF = {"foremost-golf-mfg", "formosa-golf", "apl-logistics-taiwan", "dongguan-dongcheng-shen-rui-hand", "dong-guan-her-cheng-sporting-goods",
        "xiamen-progoal-sport-goods", "ye-gin-enterprise"}
p = pd.read_csv(os.path.join(RAW, "R8_supplier_panel.csv"))
c = pd.read_csv(os.path.join(RAW, "R8_supplier_classes.csv")).set_index("slug")
p["country"] = p.slug.map(c["country"])


def per_kg(slug, grp):
    """returns ($/kg net, apparel share of kg) from the supplier's HS-chapter weight mix; group default if no chapters"""
    chs = json.loads(c.loc[slug, "chapters"]) if isinstance(c.loc[slug, "chapters"], str) else {}
    if not chs:
        app = 0.95 if "pparel" in str(grp) else 0.0
        return NET.get(grp, 9.0), app
    tot = sum(chs.values())
    val = sum(v * (25.0 if (slug in GOLF and k == "95") else CH_NET.get(k, 7.0)) for k, v in chs.items()) / tot
    app = (chs.get("61", 0) + chs.get("62", 0)) / tot
    return val, app


pk = {s: per_kg(s, c.loc[s, "grp"] if isinstance(c.loc[s, "grp"], str) else ("NATIONAL" if c.loc[s, "cls"] == "NATIONAL" else "AMBIGUOUS")) for s in c.index}
p["usd"] = [kg * pk[s][0] / G2N for kg, s in zip(p.kg, p.slug)]
p["apparel_kg"] = [kg * pk[s][1] for kg, s in zip(p.kg, p.slug)]
p["apparel_usd"] = p.apparel_kg * APP_NET / G2N
p = p[(p.q >= "2023-01") & (p.q <= "2026-07")]
mfiles = sorted(glob.glob(os.path.join(RAW, "R8_dmsc_monthly_*.csv"))) or [os.path.join(RAW, "X04_dmsc_monthly_2026-10-07.csv")]
m = pd.read_csv(mfiles[-1])
m["q"] = m.month.str[:4] + "-" + ((m.month.str[5:7].astype(int) - 1) // 3 * 3 + 1).map("{:02d}".format)
ent = m.groupby("q").weight_kg.sum()

rows = []
for q, g in p.groupby("q"):
    o, n, a = g[g.cls == "OWNED"], g[g.cls == "NATIONAL"], g[g.cls == "AMBIGUOUS"]
    cds = o[o.slug.str.startswith("century-distribution-systems")]
    pan_kg, pan_usd = g.kg.sum(), g.usd.sum()
    unk_kg = ent.get(q, 0) - pan_kg
    unk_usd = unk_kg * (pan_usd / pan_kg)  # residual valued at the panel's average $/kg
    rows.append(dict(q=q, owned_usd=o.usd.sum(), national_usd=n.usd.sum(), ambig_usd=a.usd.sum(), unknown_usd=unk_usd, cds_usd=cds.usd.sum(),
                     owned_apparel_usd=o.apparel_usd.sum(), owned_apparel_kg=o.apparel_kg.sum(), cds_apparel_kg=cds.apparel_kg.sum(),
                     owned_nonapparel_usd=o.usd.sum() - o.apparel_usd.sum(), national_apparel_kg=n.apparel_kg.sum(),
                     entity_usd_est=pan_usd + unk_usd, entity_kg=ent.get(q, 0),
                     own_share_val_classified=o.usd.sum() / (o.usd.sum() + n.usd.sum()),
                     own_share_val_classified_exCDS=(o.usd.sum() - cds.usd.sum()) / (o.usd.sum() - cds.usd.sum() + n.usd.sum()),
                     own_share_val_of_entity=o.usd.sum() / (pan_usd + unk_usd),
                     own_share_val_incl_ambig_as_nat=o.usd.sum() / (o.usd.sum() + n.usd.sum() + a.usd.sum())))
v = pd.DataFrame(rows)
v.to_csv(os.path.join(RAW, "R8_value_weighted_quarterly.csv"), index=False, float_format="%.4f")

# ---------------- IEEPA reconciliation ----------------
# average IEEPA ad-valorem rate by origin and CALENDAR quarter (arrival ~ entry), outside-folder public schedules:
# China: fentanyl 10% from 2025-02-04, 20% from 03-04, 10% from 11-10; reciprocal 10% from 04-05 (125% 04-10..05-13 with in-transit relief,
#   ignored in base case), 10% thereafter. Others: reciprocal 10% from 2025-04-05; country rates from 2025-08-07 (VN 20, KH 19, ID 19, TH 19,
#   TW 20, BD 20, MM 40, PK 19, IL 15, SG 10, DO/SV 10, IN 25 -> 50 from 08-27). All IEEPA duties ended 2026-02-20 (SCOTUS).
RATE = {
    "China": {"2025-01": 0.15, "2025-04": 0.30, "2025-07": 0.30, "2025-10": 0.233, "2026-01": 0.20},
    "default": {"2025-01": 0.0, "2025-04": 0.10, "2025-07": 0.165, "2025-10": 0.195, "2026-01": 0.195},
    "Myanmar": {"2025-01": 0.0, "2025-04": 0.10, "2025-07": 0.30, "2025-10": 0.40, "2026-01": 0.40},
    "Israel": {"2025-01": 0.0, "2025-04": 0.10, "2025-07": 0.13, "2025-10": 0.15, "2026-01": 0.15},
    "Singapore": {"2025-01": 0.0, "2025-04": 0.10, "2025-07": 0.10, "2025-10": 0.10, "2026-01": 0.10},
    "Dominican Republic": {"2025-01": 0.0, "2025-04": 0.10, "2025-07": 0.10, "2025-10": 0.10, "2026-01": 0.10},
    "Mexico": {"2025-01": 0.0, "2025-04": 0.0, "2025-07": 0.0, "2025-10": 0.0, "2026-01": 0.0},
}
# share of each calendar quarter's entity kg that falls inside the IEEPA-dutiable window Feb-2025 .. 2026-02-20 (from monthly entity kg)
mk = m.set_index("month").weight_kg
frac = {"2025-01": (mk["2025-02"] * (27 / 28) + mk["2025-03"]) / (mk["2025-01"] + mk["2025-02"] + mk["2025-03"]),
        "2025-04": 1.0, "2025-07": 1.0, "2025-10": 1.0,
        "2026-01": (mk["2026-01"] + mk["2026-02"] * 19 / 28) / (mk["2026-01"] + mk["2026-02"] + mk["2026-03"])}
rec = []
for q in RATE["China"]:
    g = p[p.q == q].copy()
    g["rate"] = [RATE.get(cn, RATE["default"])[q] for cn in g.country]
    pan_usd = g.usd.sum()
    duty_pan = (g.usd * g.rate).sum()
    vq = v.set_index("q").loc[q]
    scale = vq.entity_usd_est / pan_usd
    rec.append(dict(q=q, dutiable_frac=frac[q], entity_usd_est=vq.entity_usd_est * frac[q], avg_rate=duty_pan / pan_usd,
                    est_ieepa_duty=duty_pan * scale * frac[q], china_share_usd=g[g.country == "China"].usd.sum() / pan_usd))
r = pd.DataFrame(rec)
r.loc["total"] = r.sum(numeric_only=True)
r.loc["total", "avg_rate"] = r.loc["total", "est_ieepa_duty"] / r.loc["total", "entity_usd_est"]
r.to_csv(os.path.join(RAW, "R8_ieepa_reconciliation.csv"), float_format="%.4f")

if __name__ == "__main__":
    pd.set_option("display.width", 250)
    print("apparel $/kg net =", APP_NET)
    print((v.assign(**{k: v[k] / 1e6 for k in ["owned_usd", "national_usd", "ambig_usd", "unknown_usd", "cds_usd", "owned_apparel_usd", "entity_usd_est"]})).round(3).to_string(index=False))
    print(r.round(3).to_string())
    for yr in ["2023", "2024", "2025", "2026"]:
        s = v[v.q.str.startswith(yr)]
        print(yr, "entity $M est", round(s.entity_usd_est.sum() / 1e6, 1), "owned $M", round(s.owned_usd.sum() / 1e6, 1))
