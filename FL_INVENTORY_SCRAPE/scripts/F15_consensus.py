"""F15: build tidy FL-segment consensus table from Bloomberg FA (pulled 2026-10-04) + actuals.
Source: SOURCE/06_BLOOMBERG_FINANCIALS/DKS/DKS_Bloomberg-Financials_Quarterly_setA.md, _setB.md, _Annual_FY2022-FY2031E.md
Alignment verified by F15 (see wave0/F15.md data-quality notes)."""
import csv, os
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'F15_fl_consensus.csv')

# period, type, end, rev, gp, gm_row, oi, om_row, comp_row
Q = [
 # actuals (DKS reporting basis)
 ('3Q25A(stub 8wk)','A','2025-11-01', 930.91, 214.29, None, -46.33, None, -4.7),
 ('4Q25A','A','2026-01-31', 2175.27, 544.60, None, -5.89, None, -3.4),
 ('1Q26A','A','2026-05-02', 1787.06, 498.67, 27.90, 17.46, 0.98, 0.6),
 ('2Q26A','A','2026-08-01', 1736.93, 445.77, 25.66, -31.88, -1.83, -3.6),
 # consensus
 ('3Q26E','E','2026-10-31', 1738.14, 425.83, 24.37, -71.34, -4.11, 0.34),
 ('4Q26E','E','2027-01-30', 2139.45, 545.03, 25.63, 14.00, 0.37, 0.97),
 ('1Q27E','E','2027-05-01', 1749.00, 489.05, 27.87, 18.22, 1.01, 1.20),
 ('2Q27E','E','2027-07-31', 1725.35, 459.09, 26.46, -13.26, -0.76, 1.92),
 ('3Q27E','E','2027-10-30', 1733.89, 456.90, 26.01, -22.96, -1.19, 2.75),
 ('4Q27E','E','2028-01-29', 2174.61, 578.13, 26.73, 51.20, 2.01, 2.72),
 ('1Q28E','E','2028-04-29', 1773.19, 506.95, 28.29, 56.73, 3.18, 2.79),
 ('2Q28E','E','2028-07-29', 1749.74, 463.59, 26.13, 6.00, 0.31, 3.14),
 ('3Q28E','E','2028-10-28', 1722.47, 490.45, 27.01, 10.02, 0.59, 3.35),
 ('4Q28E','E','2029-02-03', 2214.16, 590.70, 27.24, 97.70, 4.22, 3.53),
]
# prior-year comparison bases (DKS basis; PF where FL not owned)
PY = {  # period: (rev, gm%, oi, comp) of the same quarter one year earlier
 '3Q26E': (1851.30, 23.02, 6.8, -4.7),   # PF full-qtr rev & NG OI; GM = 8-wk stub (full-qtr PF GM not disclosed)
 '4Q26E': (2175.27, 25.04, -5.89, -3.4),
 '1Q27E': (1787.06, 27.90, 17.46, 0.6),
 '2Q27E': (1736.93, 25.66, -31.88, -3.6),
}
rows = []
byp = {r[0]: r for r in Q}
for p, t, end, rev, gp, gm, oi, om, comp in Q:
    gm_calc = gp / rev * 100
    sga = gp - oi
    d = dict(period=p, type=t, period_end=end, fl_revenue=rev, fl_gross_profit=gp,
             fl_gm_pct_row=gm, fl_gm_pct_gp_over_rev=round(gm_calc, 2),
             fl_oi=oi, fl_om_pct_row=om, fl_om_pct_oi_over_rev=round(oi / rev * 100, 2),
             fl_sga_derived=round(sga, 2), fl_sga_pct_derived=round(sga / rev * 100, 2),
             fl_sga_pct_gm_minus_om=(round(gm - om, 2) if gm is not None and om is not None else None),
             fl_pf_comp_pct=comp)
    # y/y
    py = None
    if p in PY:
        py = PY[p]
    elif t == 'E':
        # same quarter prior year = 4 rows earlier in the E/A list
        idx = [r[0] for r in Q].index(p)
        prev = Q[idx - 4]
        py = (prev[3], prev[5] if prev[5] is not None else prev[4] / prev[3] * 100, prev[6], prev[8])
    if py:
        d['rev_yoy_pct'] = round((rev / py[0] - 1) * 100, 2)
        gmuse = gm if gm is not None else gm_calc
        d['gm_yoy_bps'] = round((gmuse - py[1]) * 100)
        d['oi_yoy_chg'] = round(oi - py[2], 2)
        d['two_yr_comp_stack'] = round(comp + py[3], 2)
        d['implied_noncomp_drag_pts'] = round(d['rev_yoy_pct'] - comp, 2)
    rows.append(d)

ANN = [  # FY, rev, gp, gm_row, oi, om_row, comp_row(unreliable)
 ('FY25A', 3106.18, 758.89, None, -52.22, None, -3.3),
 ('FY26E', 7401.59, 1911.26, 25.88, -72.61, -1.04, None),
 ('FY27E', 7366.80, 1987.47, 26.81, 19.71, 0.23, None),
 ('FY28E', 7585.72, 2084.64, 27.57, 108.64, 1.52, None),
 ('FY29E', 8329.76, 2191.08, 28.66, 212.18, None, None),
 ('FY30E', 8662.95, 2267.77, 29.18, 339.63, None, None),
]
for fy, rev, gp, gm, oi, om, comp in ANN:
    qs = {'FY26E': ['1Q26A', '2Q26A', '3Q26E', '4Q26E'], 'FY27E': ['1Q27E', '2Q27E', '3Q27E', '4Q27E'],
          'FY28E': ['1Q28E', '2Q28E', '3Q28E', '4Q28E']}.get(fy)
    d = dict(period=fy, type=('A' if fy.endswith('A') else 'E'), fl_revenue=rev, fl_gross_profit=gp,
             fl_gm_pct_row=gm, fl_gm_pct_gp_over_rev=round(gp / rev * 100, 2), fl_oi=oi, fl_om_pct_row=om,
             fl_om_pct_oi_over_rev=round(oi / rev * 100, 2), fl_sga_derived=round(gp - oi, 2),
             fl_sga_pct_derived=round((gp - oi) / rev * 100, 2), fl_pf_comp_pct=comp)
    if qs:
        R = sum(byp[q][3] for q in qs); G = sum(byp[q][4] for q in qs); O = sum(byp[q][6] for q in qs)
        C = sum(byp[q][3] * byp[q][8] for q in qs) / R
        d.update(qsum_rev=round(R, 2), qsum_gp=round(G, 2), qsum_gm_pct=round(G / R * 100, 2),
                 qsum_oi=round(O, 2), qsum_rev_wtd_comp=round(C, 2))
        d['fl_pf_comp_pct'] = round(C, 2)
    rows.append(d)

cols = []
for r in rows:
    for k in r:
        if k not in cols: cols.append(k)
with open(OUT, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
for r in rows:
    print({k: v for k, v in r.items() if v is not None})
