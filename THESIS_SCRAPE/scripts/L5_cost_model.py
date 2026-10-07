"""L5 (wave 2): thesis #2 cost model - (A) decomposition of the 1H FY26 DICK'S personnel deleverage into wage rate,
format mix, volume productivity and residual; (B) FY27 DSG margin bear/base/bull vs consensus; (C) Q3 FY26 test grid.
Rerun: python THESIS_SCRAPE\\scripts\\L5_cost_model.py  (from anywhere)
Writes: raw\\L5_1H26_decomp_grid.csv, raw\\L5_fy27_scenarios.csv, raw\\L5_q3_test_grid.csv; prints summary tables.
Inputs:
- DICK'S segment lines (10-Q/10-K CODM tables; D07/WA6 csv): 1H FY25 personnel 941.886, 1H FY26 1,029.869 ($M); sales 6,821.293 -> 7,227.327.
- Format incremental sales y/y from F2 schedule (raw\\F2_format_comp_schedule.csv): Q1FY26 63.3 + Q2FY26 78.1 = 141.4 base,
  low 103.6 / high 178.8 (F2 bps x PY base).
- Staffing: WF Exh 28 HoS 168 / FH 65 employees (KNOWN); legacy DSG box L heads (assumption 50-65; WA1 used ~62).
- Wage rate w: BLS CES AHE all employees, 1H FY26 (Feb-Jul 2026) y/y: sporting goods retailers (CEU4245911003) +3.50%,
  NAICS 459 +4.36%, retail +3.56% (scripts\\L5_bls_wages.py).
- Store share of personnel s (rest = CSC/field/GameChanger; WA6-5): 0.75-0.85.
All outputs INFERENCE unless stated.
"""
import csv, itertools, os, statistics
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'

# ---------------- (A) 1H FY26 decomposition ----------------
P0, P1 = 941.886, 1029.869
S0, S1 = 6821.293, 7227.327
g = S1 / S0 - 1
dP = P1 - P0
excess = dP - g * P0
r0 = P0 / S0
bp = lambda x: x / S1 * 1e4
# format staffing schedule: replicate F2 weights with staff $ instead of sales.
hos_open = [2, 0, 3, 2, 2, 1, 13, 0, 1, 5]          # Q1FY24..Q2FY26 (F2)
fh_open = [3, 4, 4, 4, 4, 4, 6, 1, 2, 8]
def reloc(i, fmt):
    if i < 4: return 6/7 if fmt == 'H' else 11/15
    if i < 8: return 13/16 if fmt == 'H' else 13/15
    return 0.75
def format_personnel_1h26(L, c):
    """y/y incremental personnel ($M) in Q1+Q2 FY26 from relocated/new HoS & FH opened in trailing year.
    relocations add (staff - L); new stores add full staff (their sales are non-comp new-store sales, handled separately).
    Labor assumed spread ~evenly (personnel seasonality ~24-25%/qtr in 1H); weights 0.5 opening qtr, 1.0 next 3, 0.5 anniversary."""
    tot_reloc, tot_new = 0.0, 0.0
    for i in (8, 9):
        for j in range(i - 4, i + 1):
            w = 0.5 if (i - j) in (0, 4) else 1.0
            for n, staff, f in ((hos_open[j], 168, 'H'), (fh_open[j], 65, 'F')):
                rs = reloc(j, f)
                tot_reloc += n * rs * (staff - L) * c / 1e6 * 0.245 * w
                tot_new += n * (1 - rs) * staff * c / 1e6 * 0.245 * w
    return tot_reloc, tot_new
def new_store_sales_1h26():
    # non-reloc new HoS ($35M) / FH ($14M) opened in trailing year, same weights, sales seasonality 1H 22.5%/25.8%
    tot = 0.0
    for i, sea in ((8, 0.225), (9, 0.258)):
        for j in range(i - 4, i + 1):
            w = 0.5 if (i - j) in (0, 4) else 1.0
            tot += (hos_open[j] * (1 - reloc(j, 'H')) * 35 + fh_open[j] * (1 - reloc(j, 'F')) * 14) * sea * w
    return tot

grid = []
for w, L, c, e, s, fmt in itertools.product([0.035, 0.039, 0.0436], [50, 58, 65], [28e3, 33e3], [0.0, 0.3, 0.5],
                                            [0.75, 0.80, 0.85], [103.6, 141.4, 178.8]):
    rate = w * P0                                   # wage rate on whole base (store + CSC)
    f_rel, f_new = format_personnel_1h26(L, c)
    new_sales = new_store_sales_1h26()
    fmt_sales = fmt + new_sales
    fmt_pers = f_rel + f_new
    nonfmt_sales = (S1 - S0) - fmt_sales
    vol = e * (nonfmt_sales / S0) * (P0 * s)         # store hours flexing with non-format sales (GameChanger/DMN have no store labor; e absorbs)
    resid = dP - rate - fmt_pers - vol
    b_rate = bp(rate)
    b_fmt = bp(fmt_pers - r0 * fmt_sales)
    b_vol = bp(vol - r0 * nonfmt_sales)
    b_res = bp(resid)
    grid.append(dict(w=w, L=L, c=c, e=e, s=s, fmt_sales=round(fmt_sales, 1), fmt_pers=round(fmt_pers, 1),
                     rate_bp=round(b_rate, 1), format_mix_bp=round(b_fmt, 1), volume_productivity_bp=round(b_vol, 1),
                     rate_net_of_productivity_bp=round(b_rate + b_vol, 1), residual_bp=round(b_res, 1),
                     total_bp=round(b_rate + b_fmt + b_vol + b_res, 1)))
with open(os.path.join(RAW, 'L5_1H26_decomp_grid.csv'), 'w', newline='') as f:
    wtr = csv.DictWriter(f, fieldnames=list(grid[0])); wtr.writeheader(); wtr.writerows(grid)
base = [r for r in grid if r['w'] == 0.035 and r['L'] == 58 and r['c'] == 30e3] or \
       [r for r in grid if r['w'] == 0.035 and r['L'] == 58 and r['c'] == 28e3 and r['e'] == 0.3 and r['s'] == 0.80 and r['fmt_sales'] > 141]
print(f"1H FY26: personnel +${dP:.1f}M (+{dP/P0*100:.2f}%), sales +{g*100:.2f}%, excess ${excess:.1f}M = {bp(excess):.1f}bp")
print('BASE (w 3.5%, L 58, c $28K, e 0.3, s 0.80, F2 base fmt):', base[0])
for k in ('format_mix_bp', 'rate_net_of_productivity_bp', 'residual_bp'):
    v = [r[k] for r in grid]
    print(f"  {k}: min {min(v)}  p25 {statistics.quantiles(v, n=4)[0]:.1f}  median {statistics.median(v)}  p75 {statistics.quantiles(v, n=4)[2]:.1f}  max {max(v)}")

# ---------------- (B) FY27 scenarios ----------------
REV27 = 15203.0; REV26 = 14753.0
P26_pct = 14.33   # FY26E personnel % (1H actual 14.25% + 2H 14.40% = 2H FY25 14.15% +25bp); INFERENCE
SH, TAX = 89.09, 0.2746
per_bp = REV27 / 1e4 * (1 - TAX) / SH          # $/sh per bp
g27 = REV27 / REV26 - 1
P26 = P26_pct / 100 * REV26
store_share = 0.80
cons_opex_hurdle = 22   # bp of SG&A/occupancy/pre-open leverage embedded (KNOWN: +29 total, GM +7)
def scen(name, w, fmt_bp, btw_gross, reinvest, hc_bp, bonus_bp, wc_m, preopen_bp, occ_bp, sga_other_bp):
    # personnel: rate vs productivity on base. Store hours on legacy flat (scheduling), sales growth ex format ~1.2%
    fmt_sales_share = 0.0183  # F2 FY27E format comp contribution ~1.83% avg (Q1-Q4 171/172/184/204bp)
    nonfmt = g27 - fmt_sales_share
    e = 0.3
    rate_gap = -(w - nonfmt * (1 - e * store_share)) * P26 / REV27 * 1e4   # bp (negative = deleverage)
    btw = btw_gross * (1 - reinvest) / REV27 * 1e4
    wc = wc_m / REV27 * 1e4
    pers = rate_gap + fmt_bp + btw + hc_bp + bonus_bp
    other = wc + preopen_bp + occ_bp + sga_other_bp
    tot = pers + other
    return dict(scenario=name, wage_rate=w, rate_vs_productivity_bp=round(rate_gap, 1), format_mix_bp=fmt_bp,
                btw_net_savings_bp=round(btw, 1), btw_gross_musd=btw_gross, reinvest=reinvest, healthcare_bp=hc_bp,
                bonus_rebuild_bp=bonus_bp, personnel_total_bp=round(pers, 1), wc_marketing_rolloff_bp=round(wc, 1),
                preopen_bp=preopen_bp, occupancy_bp=occ_bp, sga_other_tech_bp=sga_other_bp,
                opex_total_bp=round(tot, 1), vs_consensus_hurdle_bp=round(tot - cons_opex_hurdle, 1),
                eps_vs_cons=round((tot - cons_opex_hurdle) * per_bp, 2))
S = [scen('bear', 0.0375, -10, 10, 0.5, -10, -23, 0, -8, -10, -12),
     scen('base', 0.0325, -7, 30, 0.25, -7, -12, 15, -3, -5, -5),
     scen('bull', 0.0275, -5, 50, 0.10, -4, -5, 23, 0, 0, 0)]
with open(os.path.join(RAW, 'L5_fy27_scenarios.csv'), 'w', newline='') as f:
    wtr = csv.DictWriter(f, fieldnames=list(S[0])); wtr.writeheader(); wtr.writerows(S)
print(f"\nFY27 (rev growth {g27*100:.2f}%, $/sh per bp {per_bp:.4f}); consensus opex hurdle +{cons_opex_hurdle}bp")
for r in S: print(r)
# BtW gross savings needed just to meet consensus hurdle in base (other items as base):
b = S[1]; need = cons_opex_hurdle - (b['opex_total_bp'] - b['btw_net_savings_bp'])
print(f"Base: net BtW savings needed to hit consensus = {need:.1f}bp = ${need*REV27/1e4:.0f}M net (${need*REV27/1e4/(1-0.25):.0f}M gross at 25% reinvest)")

# ---------------- (B2) backtest of the 'natural personnel growth' model on FY24, FY25, 1H FY26 ----------------
# natural growth = wage rate w + format staffing (17.5% of format incremental sales, = 1H26 base-case fmt_pers/fmt_sales)
#                  + store-hours volume e*s*(non-format sales growth); residual = actual - natural (savings < 0 < investment)
print('\nBacktest: natural personnel growth vs actual (format sales from F2 schedule base case)')
bt = [  # period, P0, S0, P1, S1, fmt_sales, w_sporting_goods_BLS, w_retail_BLS, incentive note
    ('FY24 (52wk basis)', 1838.554*52/53, 12984.399-170.2, 1869.257, 13442.849, 69.6, 0.0281, 0.0270, 'STIP 100%->163.8% (higher bonus)'),
    ('FY25', 1869.257, 13442.849, 1972.850, 14108.943, 220.7, 0.0174, 0.0395, 'STIP 163.8%->100% (lower bonus)'),
    ('1H FY26', 941.886, 6821.293, 1029.869, 7227.327, 141.4, 0.0350, 0.0356, 'no bonus mention; healthcare up')]
btrows = []
for name, p0, s0, p1, s1, fs, wsg, wrt, note in bt:
    gS = s1/s0-1; nonf = gS - fs/s0
    for wl, w in (('sporting-goods AHE', wsg), ('retail AHE', wrt)):
        nat = w + 0.175*fs/p0 + 0.3*0.8*nonf
        res = (p1/p0-1) - nat
        btrows.append(dict(period=name, wage_source=wl, w=w, sales_g=round(gS*100, 2), actual_pers_g=round((p1/p0-1)*100, 2),
                           natural_g=round(nat*100, 2), residual_pct=round(res*100, 2), residual_musd=round(res*p0, 1),
                           residual_bp_sales=round(res*p0/s1*1e4, 1), note=note))
for r in btrows: print(r)
with open(os.path.join(RAW, 'L5_backtest.csv'), 'w', newline='') as f:
    wtr = csv.DictWriter(f, fieldnames=list(btrows[0])); wtr.writeheader(); wtr.writerows(btrows)

# FY27 'natural drift' under consensus sales (+3.05%), format ~1.83% of sales (F2 FY27E), underlying same-store
# non-format ~0.5-1.2% (residual of consensus growth):
print('\nFY27 natural personnel drift vs consensus sales path (no Built to Win savings):')
for w in (0.0275, 0.0325, 0.0375):
    for nonf in (0.005, 0.0122):
        nat = w + 0.175*0.0183*REV26/P26 + 0.3*0.8*nonf
        # new non-reloc stores ratio-neutral; excess vs sales path:
        exc = (nat - g27) * P26
        print(f"  w {w:.4f} non-format growth {nonf:.4f}: natural +{nat*100:.2f}% vs sales +{g27*100:.2f}% -> {-exc/REV27*1e4:+.1f}bp (${-exc:.0f}M)")
# consensus phasing (BBG quarterly OI; revenue rebuilt at ~3% growth because BBG quarterly revenue rows are inconsistent)
oi_1h26, oi_2h26e = 360.98+485.20, 1554.67-360.98-485.20
oi_1h27e = 370.13+482.51; oi_2h27e = 1647.17-oi_1h27e
rev_1h27 = 7227.327*1.03; rev_2h27 = REV27-rev_1h27; rev_2h26 = REV26-7227.327
print(f"Consensus phasing: 1H27E OI {oi_1h27e:.1f} vs {oi_1h26:.1f} ({(oi_1h27e/oi_1h26-1)*100:+.1f}%), margin {oi_1h27e/rev_1h27*100:.2f}% vs {oi_1h26/7227.327*100:.2f}%;"
      f" 2H27E OI {oi_2h27e:.1f} vs 2H26E {oi_2h26e:.1f} ({(oi_2h27e/oi_2h26e-1)*100:+.1f}%), margin {oi_2h27e/rev_2h27*100:.2f}% vs {oi_2h26e/rev_2h26*100:.2f}%")

# ---------------- (B3) joint grid: comp beat x Built to Win savings -> FY27 DSG OI vs consensus ----------------
# bottom-up margin = FY26E 10.54% + GM +7bp (consensus) + my opex total (base items, BtW varied);
# comp beat adds sales on FY26E base at a 29% incremental margin (GM ~36.3% less variable personnel e*s*r ~3.4% less
# variable card/shipping/other ~4%; INFERENCE).
print('\nJoint grid: FY27 DSG OI vs consensus $1,647M ($/sh at $0.00814 per $1M)')
jrows = []
for btw in (10, 30, 50, 80):
    o = scen('x', 0.0325, -7, btw, 0.25, -7, -12, 15, -3, -5, -5)['opex_total_bp']
    m0 = 10.54 + 0.07 + o/100
    for dcomp in (0.0, 0.01, 0.02):
        oi = m0/100*REV27 + 0.29*dcomp*REV26
        jrows.append(dict(btw_gross=btw, comp_beat_pts=dcomp*100, dsg_oi=round(oi), margin=round(oi/(REV27+dcomp*REV26)*100, 2),
                          oi_vs_cons=round(oi-1647.17), eps_vs_cons=round((oi-1647.17)*0.00814, 2)))
for r in jrows: print(r)
with open(os.path.join(RAW, 'L5_joint_grid.csv'), 'w', newline='') as f:
    wtr = csv.DictWriter(f, fieldnames=list(jrows[0])); wtr.writeheader(); wtr.writerows(jrows)
print(f"Personnel leverage per +100bp underlying comp with flexible labor (e=0.3, s=0.8): {P26_pct*(1-0.3*0.8):.1f}bp of sales growth -> ~{P26_pct*(1-0.24)/100*100:.1f}bp margin")

# ---------------- (C) Q3 FY26 test grid ----------------
q3p0, q3s0 = 485.490, 3236.860
rows = []
for sg in (0.035, 0.045, 0.055):        # Q3 FY26 DICK'S sales growth (cons comp 1.69% + ~2pt new/format sales)
    for pg in (0.04, 0.055, 0.07, 0.09):
        s1 = q3s0 * (1 + sg); p1 = q3p0 * (1 + pg)
        rows.append(dict(sales_g=sg, pers_g=pg, pers_pct=round(p1 / s1 * 100, 2), bp_yoy=round((p1 / s1 - q3p0 / q3s0) * 1e4)))
with open(os.path.join(RAW, 'L5_q3_test_grid.csv'), 'w', newline='') as f:
    wtr = csv.DictWriter(f, fieldnames=list(rows[0])); wtr.writeheader(); wtr.writerows(rows)
print('\nQ3 FY26 test grid (Q3 FY25 personnel 15.00%):')
for r in rows: print(r)
