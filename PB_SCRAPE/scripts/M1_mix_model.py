r"""M1_mix_model.py  (PB_SCRAPE wave 2, agent M1, 2026-10-07)

PURPOSE
  1) Reconciled history FY16-FY25 (+ quarterly FY24-1H FY26) of DKS owned/vertical-brand mix:
       owned-brand % of DICK'S sales | footwear % of DICK'S sales | owned-brand % of NON-FOOTWEAR MERCHANDISE
     (non-footwear merchandise = hardlines + apparel; the 10-K "Other" line is non-merchandise revenue
      -- services, shipping, GameChanger subscriptions, DMN, licensing -- and is EXCLUDED from the denominator).
     Each year carries a ROUNDING BAND: 10-Ks give vertical sales as "approximately X%" and/or "$X.X billion".
     Where both are given the band is the INTERSECTION of the two constraints.
  2) Scenario model FY26E-FY28E: penetration path (flat / +0.5pt/yr / +1pt/yr) x footwear share path
     (flat / -1pt/yr / +1pt/yr) -> owned $ , owned % of DICK'S sales, delta vs consensus-implied flat mix,
     DICK'S GM bps at 700/800/900bp premium, segment EBIT $ and EPS.

INPUTS (all hard-coded below, with sources)
  - Category net sales $M: DKS 10-K "Net sales by category" note, FY2016-FY2025 (EDGAR primary docs cached at
    PB_SCRAPE\raw\X13_edgar_cache\*1089063*; e.g. sec.gov/Archives/edgar/data/1089063/000108906326000007/dks-20260131.htm)
    and 10-Q revenue-disaggregation notes (WORKING_NOTES\W04 L516-526, L797-804, L1076-1083).
  - Vertical/private-brand sales: 10-K Item 1 sentences (same cached docs): FY16 ~10%; FY17 ">$1 billion", ~12%;
    FY18 ~14%; FY19 ~14%; FY20 ~15%; FY21 $1.7B ~14%; FY22 $1.7B ~14%; FY23 $1.6B ~13%; FY24 $1.7B ~13%;
    FY25 $1.8B ~13% "within the DICK'S Business". NB: the figure INCLUDES exclusively-licensed brands (adidas football,
    Cobra, Marucci, Lotto, Prince until FY24; Reebok/Slazenger/Umbro/adidas baseball in FY16-FY19).
  - Foot Locker category mix (to strip FL from FY25+ consolidated categories): FL 10-K footwear share of sales
    2020 84%, 2021 80%, 2022 80%, 2023 81%, 2024 84% (WORKING_NOTES\P_FL_10K_A L172, P_FL_10K_B L134/L453/L762).
    Base 84%, sensitivity 80% / 88%. FL assumed ~0 hardlines and ~0 "other"; FL apparel+accessories booked in DKS "Apparel".
  - FL segment sales: FY25 stub $3,106.2M (Q3 $930.9M, Q4 $2,175.3M derived), Q1 FY26 $1,787.1M, Q2 FY26 $1,736.9M.
  - Consensus (Bloomberg, CORE_NOTES\C05 L36 / 00_CORE_DIGEST L284-286, as of 2026-10-05): DICK'S segment revenue
    FY26E 14,753.08 / FY27E 15,202.95 / FY28E 15,741.60 $M; segment OI 1,554.67 / 1,647.17 / 1,737.84;
    diluted shares 89.95 / 89.09 / 89.67M; adj EPS 11.49 / 13.36 / 15.03; DSG GM ~36.2-36.3% flat.

RERUN
  python C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\scripts\M1_mix_model.py
  -> writes PB_SCRAPE\raw\M1_mix_model.csv (history + quarterly + scenarios) and prints the tables.
  To update: add the new 10-Q category row + FL segment sales to Q dict; after the FY26 10-K (~Mar 2027) add FY26 to H
  with the disclosed vertical $ / %.
All derived numbers are INFERENCE.
"""
import csv, itertools, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw", "M1_mix_model.csv")
FLFW = (0.80, 0.84, 0.88)  # FL footwear share sensitivity

# ---------------- annual history: consolidated category $M, FL segment $M, vertical disclosure ----------------
# pct = disclosed "approximately X%" (None if not given); usd = disclosed $M (None if not given); lo_usd = lower bound text (">$1 billion")
H = {
 "FY16": dict(hl=3573.6, ap=2756.1, fw=1529.4, ot=62.9,  tot=7922.0,  fl=0, pct=10, usd=None, lo_usd=None),
 "FY17": dict(hl=3887.0, ap=2920.3, fw=1694.6, ot=88.6,  tot=8590.5,  fl=0, pct=12, usd=None, lo_usd=1000),
 "FY18": dict(hl=3632.1, ap=2962.4, fw=1719.5, ot=122.6, tot=8436.6,  fl=0, pct=14, usd=None, lo_usd=None),
 "FY19": dict(hl=3695.2, ap=3109.0, fw=1811.4, ot=135.1, tot=8750.7,  fl=0, pct=14, usd=None, lo_usd=None),
 "FY20": dict(hl=4428.5, ap=3180.2, fw=1834.3, ot=141.0, tot=9584.0,  fl=0, pct=15, usd=None, lo_usd=None),
 "FY21": dict(hl=5407.9, ap=4131.2, fw=2562.8, ot=191.5, tot=12293.4, fl=0, pct=14, usd=1700, lo_usd=None),
 "FY22": dict(hl=4952.2, ap=4218.1, fw=2979.1, ot=218.8, tot=12368.2, fl=0, pct=14, usd=1700, lo_usd=None),
 "FY23": dict(hl=4915.5, ap=4329.8, fw=3388.7, ot=350.4, tot=12984.4, fl=0, pct=13, usd=1600, lo_usd=None),
 "FY24": dict(hl=4899.3, ap=4425.4, fw=3829.0, ot=289.1, tot=13442.8, fl=0, pct=13, usd=1700, lo_usd=None),
 "FY25": dict(hl=5048.3, ap=4895.4, fw=6888.0, ot=383.4, tot=17215.1, fl=3106.2, pct=13, usd=1800, lo_usd=None),
}
# ---------------- quarterly (no vertical disclosure; denominators + footwear share only) ----------------
Q = {
 "Q3FY24": dict(hl=1057.5, ap=966.1,  fw=950.9,  ot=82.7,  tot=3057.2, fl=0),
 "Q4FY24": dict(hl=4899.3-3744.8, ap=4425.4-2773.5, fw=3829.0-2805.4, ot=289.1-225.5, tot=13442.8-9549.2, fl=0),
 "Q1FY25": dict(hl=1192.9, ap=884.7,  fw=998.3,  ot=98.8,  tot=3174.7, fl=0),
 "Q2FY25": dict(hl=1471.5, ap=1008.5, fw=1087.7, ot=78.9,  tot=3646.6, fl=0),
 "Q3FY25": dict(hl=1104.4, ap=1111.0, fw=1851.4, ot=101.0, tot=4167.8, fl=930.9),
 "Q4FY25": dict(hl=5048.3-3768.9, ap=4895.4-3004.2, fw=6888.0-3937.4, ot=383.4-278.6, tot=17215.1-10989.1, fl=3106.2-930.9),
 "Q1FY26": dict(hl=1326.6, ap=1109.5, fw=2605.1, ot=123.3, tot=5164.5, fl=1787.1),
 "Q2FY26": dict(hl=1552.3, ap=1299.4, fw=2616.1, ot=119.0, tot=5586.8, fl=1736.9),
 "1HFY25": dict(hl=2664.4, ap=1893.2, fw=2086.0, ot=177.7, tot=6821.3, fl=0),
 "1HFY26": dict(hl=2878.9, ap=2408.9, fw=5221.2, ot=242.3, tot=10751.3, fl=3524.0),
}
YOY = {"Q3FY25": "Q3FY24", "Q4FY25": "Q4FY24", "Q1FY26": "Q1FY25", "Q2FY26": "Q2FY25", "1HFY26": "1HFY25"}


def strip(v, s):
    """DICK'S-segment categories: remove FL (footwear share s, rest apparel)."""
    flfw = v["fl"] * s
    d = dict(hl=v["hl"], ap=v["ap"] - (v["fl"] - flfw), fw=v["fw"] - flfw, ot=v["ot"], dk=v["tot"] - v["fl"])
    d["nonfw"] = d["hl"] + d["ap"]
    return d


def band(v, dk):
    """owned $ band from rounding: pct +/-0.5pt of DICK'S sales; usd +/-$50M; intersect when both exist."""
    lo, hi = -1e9, 1e9
    if v["pct"] is not None:
        lo, hi = max(lo, (v["pct"] - 0.5) / 100 * dk), min(hi, (v["pct"] + 0.5) / 100 * dk)
    if v["usd"] is not None:
        lo, hi = max(lo, v["usd"] - 50), min(hi, v["usd"] + 50)
    if v["lo_usd"] is not None:
        lo = max(lo, v["lo_usd"])
    return lo, hi


rows = []
print("=== RECONCILED ANNUAL HISTORY (FL footwear share 84% for FY25) ===")
print("FY   | DICK'S $M | fw% DK | other% | nonfw $M | owned $ band (mid)      | owned% DK band     | penetration nonfw band (mid) | F6-style pct/(1-fw%)")
for k, v in H.items():
    for s in FLFW:
        if v["fl"] == 0 and s != 0.84:
            continue
        d = strip(v, s)
        lo, hi = band(v, d["dk"])
        mid = (lo + hi) / 2
        r = dict(section="history", period=k, fl_fw_share=s, dk_sales=round(d["dk"], 1), dk_fw=round(d["fw"], 1),
                 dk_hl=round(d["hl"], 1), dk_ap=round(d["ap"], 1), dk_other=round(d["ot"], 1), dk_nonfw=round(d["nonfw"], 1),
                 fw_pct_dk=round(100 * d["fw"] / d["dk"], 2), other_pct_dk=round(100 * d["ot"] / d["dk"], 2),
                 owned_usd_lo=round(lo), owned_usd_hi=round(hi), owned_usd_mid=round(mid),
                 owned_pct_dk_lo=round(100 * lo / d["dk"], 2), owned_pct_dk_hi=round(100 * hi / d["dk"], 2),
                 pen_nonfw_lo=round(100 * lo / d["nonfw"], 2), pen_nonfw_hi=round(100 * hi / d["nonfw"], 2),
                 pen_nonfw_mid=round(100 * mid / d["nonfw"], 2),
                 f6_style=round(100 * v["pct"] / (100 - round(100 * d["fw"] / d["dk"])), 1))
        rows.append(r)
        if s == 0.84:
            print(f"{k} | {d['dk']:9.1f} | {r['fw_pct_dk']:5.1f}% | {r['other_pct_dk']:4.1f}% | {d['nonfw']:8.1f} | "
                  f"{lo:6.0f}-{hi:6.0f} ({mid:6.0f}) | {r['owned_pct_dk_lo']:5.2f}-{r['owned_pct_dk_hi']:5.2f}% | "
                  f"{r['pen_nonfw_lo']:5.2f}-{r['pen_nonfw_hi']:5.2f}% ({r['pen_nonfw_mid']:5.2f}%) | {r['f6_style']}%")

print("\n=== QUARTERLY DICK'S-SEGMENT DENOMINATORS (derived; no vertical $ disclosed) ===")
for k, v in Q.items():
    for s in FLFW:
        if v["fl"] == 0 and s != 0.84:
            continue
        d = strip(v, s)
        r = dict(section="quarterly", period=k, fl_fw_share=s, dk_sales=round(d["dk"], 1), dk_fw=round(d["fw"], 1),
                 dk_hl=round(d["hl"], 1), dk_ap=round(d["ap"], 1), dk_other=round(d["ot"], 1), dk_nonfw=round(d["nonfw"], 1),
                 fw_pct_dk=round(100 * d["fw"] / d["dk"], 2), other_pct_dk=round(100 * d["ot"] / d["dk"], 2))
        if k in YOY:
            p = strip(Q[YOY[k]], 0.84)
            r["fw_pct_dk_yoy_pt"] = round(r["fw_pct_dk"] - 100 * p["fw"] / p["dk"], 2)
            r["other_pct_dk_yoy_pt"] = round(r["other_pct_dk"] - 100 * p["ot"] / p["dk"], 2)
            r["dk_fw_yoy_pct"] = round(100 * (d["fw"] / p["fw"] - 1), 1)
            r["dk_nonfw_yoy_pct"] = round(100 * (d["nonfw"] / p["nonfw"] - 1), 1)
            r["dk_hl_yoy_pct"] = round(100 * (d["hl"] / p["hl"] - 1), 1)
            r["dk_ap_yoy_pct"] = round(100 * (d["ap"] / p["ap"] - 1), 1)
            r["dk_sales_yoy_pct"] = round(100 * (d["dk"] / p["dk"] - 1), 1)
        rows.append(r)
        if k in YOY:
            print(f"{k} FLfw={s:.0%}: DK sales {d['dk']:7.1f} ({r['dk_sales_yoy_pct']:+.1f}%) | fw% {r['fw_pct_dk']:5.2f} ({r['fw_pct_dk_yoy_pt']:+.2f}pt) | "
                  f"other% {r['other_pct_dk']:4.2f} ({r['other_pct_dk_yoy_pt']:+.2f}pt) | fw {r['dk_fw_yoy_pct']:+.1f}% | nonfw {r['dk_nonfw_yoy_pct']:+.1f}% "
                  f"(HL {r['dk_hl_yoy_pct']:+.1f}%, AP {r['dk_ap_yoy_pct']:+.1f}%)")

# ---------------- scenarios ----------------
base = strip(H["FY25"], 0.84)
F0 = base["fw"] / base["dk"]                    # 30.33%
P0 = H["FY25"]["usd"] / base["nonfw"]           # 19.05%
CONS_MIX = H["FY25"]["usd"] / base["dk"]        # 12.76% = consensus-implied flat mix (INFERENCE)
OTHER = {"FY26E": 0.034, "FY27E": 0.034, "FY28E": 0.034}  # 1H FY26 run-rate 3.35% (vs FY25 2.72%); held flat (INFERENCE)
REV = {"FY26E": 14753.08, "FY27E": 15202.95, "FY28E": 15741.60}
OI = {"FY26E": 1554.67, "FY27E": 1647.17, "FY28E": 1737.84}
SH = {"FY26E": 89.95, "FY27E": 89.09, "FY28E": 89.67}
EPS = {"FY26E": 11.49, "FY27E": 13.36, "FY28E": 15.03}
TAX = 0.275
PEN = {"flat": 0.0, "+0.5pt/yr": 0.005, "+1pt/yr": 0.01}
FW = {"fw flat": 0.0, "fw -1pt/yr": -0.01, "fw +1pt/yr": 0.01}
PREM = (0.07, 0.08, 0.09)

print(f"\n=== SCENARIOS (base FY25: fw {F0:.2%}, penetration {P0:.2%}, owned/DK {CONS_MIX:.2%} = consensus-implied flat mix) ===")
for (pn, pa), (fn, fa) in itertools.product(PEN.items(), FW.items()):
    for n, yr in enumerate(("FY26E", "FY27E", "FY28E"), start=1):
        R = REV[yr]; f = F0 + fa * n; o = OTHER[yr]; p = P0 + pa * n
        nonfw = R * (1 - f - o)
        owned = p * nonfw
        mix = owned / R
        d_mix = mix - CONS_MIX
        # decomposition of delta mix (vs FY25 mix): penetration effect vs denominator (footwear+other) effect
        pen_eff = (p - P0) * (1 - f - o)
        den_eff = P0 * ((1 - f - o) - (1 - F0 - base["ot"] / base["dk"]))
        r = dict(section="scenario", period=yr, pen_path=pn, fw_path=fn, dk_sales=R, fw_pct_dk=round(100 * f, 2),
                 other_pct_dk=round(100 * o, 2), dk_nonfw=round(nonfw, 1), pen_nonfw=round(100 * p, 2),
                 owned_usd=round(owned, 1), owned_usd_cons=round(CONS_MIX * R, 1), owned_usd_vs_cons=round(owned - CONS_MIX * R, 1),
                 owned_pct_dk=round(100 * mix, 2), d_mix_pt_vs_cons=round(100 * d_mix, 2),
                 d_mix_from_pen_pt=round(100 * pen_eff, 2), d_mix_from_denominator_pt=round(100 * den_eff, 2))
        for pr in PREM:
            gp = d_mix * pr * R
            r[f"gm_bps_{int(pr*1e4)}"] = round(1e4 * d_mix * pr, 1)
            r[f"ebit_usd_{int(pr*1e4)}"] = round(gp, 1)
            r[f"ebit_pct_of_cons_OI_{int(pr*1e4)}"] = round(100 * gp / OI[yr], 2)
            r[f"eps_{int(pr*1e4)}"] = round(gp * (1 - TAX) / SH[yr], 3)
            r[f"eps_pct_of_cons_{int(pr*1e4)}"] = round(100 * gp * (1 - TAX) / SH[yr] / EPS[yr], 2)
        rows.append(r)

# breakeven: penetration needed each year to hold consensus-implied mix, by footwear path
print("\nBreak-even non-footwear penetration to hold owned mix at the consensus-implied 12.76% (other share 3.4%):")
for fn, fa in FW.items():
    s = []
    for n, yr in enumerate(("FY26E", "FY27E", "FY28E"), start=1):
        f = F0 + fa * n
        be = CONS_MIX / (1 - f - OTHER[yr])
        s.append(f"{yr} {100*be:.2f}%")
        rows.append(dict(section="breakeven", period=yr, fw_path=fn, fw_pct_dk=round(100 * f, 2), other_pct_dk=round(100 * OTHER[yr], 2),
                         pen_nonfw=round(100 * be, 2)))
    print(f"  {fn}: " + " | ".join(s))

print("\nScenario summary (800bp premium):  path | FY26E / FY27E / FY28E : owned $M ; owned % ; d-mix pt ; GM bps ; EBIT $M ; EPS $")
for r in rows:
    if r["section"] == "scenario":
        print(f"  {r['pen_path']:>10} x {r['fw_path']:<11} {r['period']}: ${r['owned_usd']:7.0f}M  {r['owned_pct_dk']:5.2f}%  {r['d_mix_pt_vs_cons']:+5.2f}pt  "
              f"{r['gm_bps_800']:+5.1f}bps  ${r['ebit_usd_800']:+6.1f}M  {r['eps_800']:+.3f}  ({r['eps_pct_of_cons_800']:+.2f}% of cons EPS)")

keys = []
for r in rows:
    for k in r:
        if k not in keys:
            keys.append(k)
with open(OUT, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=keys)
    w.writeheader(); w.writerows(rows)
print("\nwrote", os.path.abspath(OUT))
