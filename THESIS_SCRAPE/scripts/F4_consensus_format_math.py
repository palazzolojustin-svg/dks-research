"""F4 (wave 1): fresh calculations from Bloomberg consensus (CORE_NOTES/C05) and broker models (C06_R1).

Rerun:  python THESIS_SCRAPE\\scripts\\F4_consensus_format_math.py
Outputs: THESIS_SCRAPE\\raw\\F4_implied_underlying_comp.csv, F4_landlord_allowances.csv, F4_hos_count_estimates.csv

Inputs are typed in from CORE_NOTES\\C05 (Bloomberg FA quarterly setA/setB, printed 2026-10-04) and
C06_STREET_RESEARCH_R1 (JPM 2025-08-28 model, Barclays 2025-08-29 model). All values USD mn unless noted.

Calc 1: comp contribution from new formats implied by the CONSENSUS store path, and the 'underlying'
        (ex-format) comp left over inside consensus comp. Method: incremental HoS/FH store-quarters y/y
        (average of begin/end count per quarter) x relocation share x incremental annual sales per store
        x FY25 quarterly seasonality weight, divided by prior-year DKS segment revenue for that quarter.
        Relocated/converted stores sit in comp (management statement), so their uplift flows through comp.
Calc 2: landlord construction allowances (deferred construction allowances in CFO): actual run-rate vs consensus.
Calc 3: broker HoS/FH count estimates over time vs actuals.
"""
import csv, os, itertools

OUT = os.path.join(os.path.dirname(__file__), "..", "raw")
os.makedirs(OUT, exist_ok=True)

# ---------- Calc 1 ----------
q = ["1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26", "3Q26E", "4Q26E", "1Q27E", "2Q27E", "3Q27E", "4Q27E"]
hos = [21, 22, 35, 35, 36, 41, 47, 49, 53, 59, 66, 69]          # BBG setA/setB "Dick's House of Sport" EOP (actuals to 2Q26)
fh = [31, 35, 41, 42, 44, 52, 59, 63, 67, 72, 78, 81]           # BBG "Dick's Field House" EOP
hos_bop_1q25, fh_bop_1q25 = 19, 26                               # FYE24 counts (KNOWN_BRIEF)
dks_rev = {"1Q25": 3174.68, "2Q25": 3646.62, "3Q25": 3236.86, "4Q25": 4050.79,
           "1Q26": 3377.44, "2Q26": 3849.89}                     # DKS (core) segment revenue, actual
cons_comp = {"3Q26E": 1.69, "4Q26E": 1.59, "1Q27E": 2.41, "2Q27E": 2.24}  # BBG consensus DKS comp %
fy25 = sum(dks_rev[k] for k in ["1Q25", "2Q25", "3Q25", "4Q25"])
season = {i: dks_rev[k] / fy25 for i, k in enumerate(["1Q25", "2Q25", "3Q25", "4Q25"])}

def avg_counts(series, bop):
    out, prev = [], bop
    for v in series:
        out.append((prev + v) / 2)
        prev = v
    return out

hos_avg, fh_avg = avg_counts(hos, hos_bop_1q25), avg_counts(fh, fh_bop_1q25)

# scenarios: (label, HoS incremental $M/yr per relocated store, relocation share, FH uplift $M/yr, FH relo share)
scen = [("base: UBS $35M vs $15M replaced; 84% relo (F1 10-K calc); FH +$2M", 20.0, 0.84, 2.0, 0.90),
        ("low: HoS +$15M (ramp/smaller A-mall boxes); FH +$0", 15.0, 0.84, 0.0, 0.90),
        ("high: HoS +$20M; 100% relo; FH +$3M", 20.0, 1.00, 3.0, 1.00)]
rows = []
for label, hos_inc, hos_relo, fh_inc, fh_relo in scen:
    for i in range(6, 10):
        qq, ly = q[i], q[i - 4]
        w = season[i % 4]
        d_hos = hos_avg[i] - hos_avg[i - 4]
        d_fh = fh_avg[i] - fh_avg[i - 4]
        base = dks_rev[ly]
        hos_bps = d_hos * hos_relo * hos_inc * w / base * 100
        fh_bps = d_fh * fh_relo * fh_inc * w / base * 100
        fmt = hos_bps + fh_bps
        rows.append(dict(scenario=label, quarter=qq, d_hos_store_qtrs=round(d_hos, 1), d_fh_store_qtrs=round(d_fh, 1),
                         hos_comp_pts=round(hos_bps, 2), fh_comp_pts=round(fh_bps, 2), format_comp_pts=round(fmt, 2),
                         consensus_comp=cons_comp[qq], implied_underlying_comp=round(cons_comp[qq] - fmt, 2)))
with open(os.path.join(OUT, "F4_implied_underlying_comp.csv"), "w", newline="") as f:
    w_ = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w_.writeheader(); w_.writerows(rows)
print("Calc 1: implied underlying comp inside consensus")
for r in rows:
    print(r)

# back-test on ACTUAL quarters (base scenario) using FY24 counts from JPM 2025-08-28 model
q_bt = ["1Q24", "2Q24", "3Q24", "4Q24"] + q[:6]
hos_bt = [14, 14, 17, 19] + hos[:6]
fh_bt = [13, 17, 22, 26] + fh[:6]
rev_bt = {"1Q24": 3018.4, "2Q24": 3473.6, "3Q24": 3057.2, "4Q24": 3893.6, **dks_rev}
act_comp = {"1Q25": 4.5, "2Q25": 5.0, "3Q25": 5.7, "4Q25": 3.1, "1Q26": 6.0, "2Q26": 4.9}
ha, fa = avg_counts(hos_bt, 12), avg_counts(fh_bt, 11)   # FYE23: HoS 12, next-gen 50K 11
print("Back-test (base scenario) on actual comps:")
for i in range(4, 10):
    qq, ly = q_bt[i], q_bt[i - 4]
    w = rev_bt[ly] / sum(rev_bt[k] for k in q_bt[:4])
    hb = (ha[i] - ha[i - 4]) * 0.84 * 20 * w / rev_bt[ly] * 100
    fb = (fa[i] - fa[i - 4]) * 0.90 * 2 * w / rev_bt[ly] * 100
    print(f"  {qq}: actual comp {act_comp[qq]:.1f} | format {hb+fb:.2f} (HoS {hb:.2f}, FH {fb:.2f}) | underlying {act_comp[qq]-hb-fb:.2f}")

# variance $/share if underlying comp = WF bear 1.2% instead of consensus-implied (base scenario, FY27 = 1Q27E..4Q27E proxy)
base_rows = [r for r in rows if r["scenario"].startswith("base")]
avg_under = sum(r["implied_underlying_comp"] for r in base_rows) / len(base_rows)
gap = 1.2 - avg_under
rev27, shares, tax = 15203.0, 89.09, 0.2746
for flow in (0.20, 0.25, 0.30):
    d_rev = rev27 * gap / 100
    d_oi = d_rev * flow
    eps = d_oi * (1 - tax) / shares
    print(f"gap {gap:.2f}pts -> +${d_rev:.0f}M rev, flow {flow:.0%} -> +${d_oi:.0f}M OI (+{d_oi/1647*100:.1f}% vs cons seg OI), +${eps:.2f}/sh")

# ---------- Calc 2 ----------
tia = {"1Q25": 22.78, "2Q25": 47.81, "3Q25": 48.91, "4Q25": 42.16, "1Q26": 71.72, "2Q26": 57.54,
       "3Q26E": 35.14, "4Q26E": 12.18, "1Q27E": 45.31, "2Q27E": 46.73, "3Q27E": 41.46, "4Q27E": 8.60}
ann = {"FY23": 67.06, "FY24": 76.29, "FY25": 161.66, "FY26E": 171.81, "FY27E": 158.64, "FY28E": 188.47}
h1_25, h1_26 = tia["1Q25"] + tia["2Q25"], tia["1Q26"] + tia["2Q26"]
h2_25 = tia["3Q25"] + tia["4Q25"]
cons_2h26 = tia["3Q26E"] + tia["4Q26E"]
fy26_if_2h_flat = h1_26 + h2_25
print("\nCalc 2: landlord construction allowances")
print(f"H1 FY25 {h1_25:.1f} -> H1 FY26 {h1_26:.1f} ({h1_26/h1_25-1:+.0%}); cons 2H26E {cons_2h26:.1f} vs 2H25A {h2_25:.1f};"
      f" FY26E cons annual {ann['FY26E']} / qtr-sum {h1_26+cons_2h26:.1f}; FY26 if 2H flat y/y {fy26_if_2h_flat:.1f}"
      f" (+{fy26_if_2h_flat-ann['FY26E']:.1f} vs cons = ${(fy26_if_2h_flat-ann['FY26E'])/shares:.2f}/sh FCF)")
with open(os.path.join(OUT, "F4_landlord_allowances.csv"), "w", newline="") as f:
    w_ = csv.writer(f); w_.writerow(["period", "deferred_construction_allowances_usd_mn", "type"])
    for k, v in tia.items(): w_.writerow([k, v, "estimate" if k.endswith("E") else "actual"])
    for k, v in ann.items(): w_.writerow([k, v, "estimate" if k.endswith("E") else "actual"])

# ---------- Calc 3 ----------
est = [  # source, date, period, HoS, FH
    ("JPM model", "2025-08-28", "1Q26E", 39, 47), ("JPM model", "2025-08-28", "2Q26E", 47, 50),
    ("JPM model", "2025-08-28", "3Q26E", 55, 56), ("JPM model", "2025-08-28", "FY26E", 60, 62),
    ("JPM model", "2025-08-28", "FY27E", 85, 82),
    ("Barclays model", "2025-08-29", "1Q26E", 40, None), ("Barclays model", "2025-08-29", "2Q26E", 46, None),
    ("Barclays model", "2025-08-29", "3Q26E", 52, None), ("Barclays model", "2025-08-29", "FY26E", 53, None),
    ("Barclays model", "2025-08-29", "FY27E", 66, None),
    ("BBG consensus", "2026-10-04", "3Q26E", 47, 59), ("BBG consensus", "2026-10-04", "FY26E", 49, 63),
    ("BBG consensus", "2026-10-04", "FY27E", 69, 81), ("BBG consensus", "2026-10-04", "FY28E", 88, 88),
    ("Actual", "2026-05-02", "1Q26", 36, 44), ("Actual", "2026-08-01", "2Q26", 41, 52),
]
with open(os.path.join(OUT, "F4_hos_count_estimates.csv"), "w", newline="") as f:
    w_ = csv.writer(f); w_.writerow(["source", "as_of", "period", "HoS", "FH"]); w_.writerows(est)
print("\nCalc 3 written.")
