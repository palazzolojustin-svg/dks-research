"""B5: robustness layer on B5_qcew_event.py output.
(1) placebo: for each HoS event, assign the same opening quarter to every size-matched control county
    (base-year emp within 0.5x-2x, fully disclosed, DKS county without HoS) and compute the same excess -> null distribution.
(2) clean subsample (base emp < 1,500; excludes Tulsa [Scheels Tulsa opened Nov-2024 same quarter], Harris, Maricopa, Dallas).
(3) balanced fade test: events with disclosed k=0..7 -> year-1 (k=0..3) vs year-2 (k=4..7) excess jobs and wages.
(4) excess wages per excess job (annualised) = implied pay per incremental HoS worker.
Rerun: python scripts/B5_qcew_event2.py   (needs raw/B5_event_panel.csv from B5_qcew_event.py)
"""
import pandas as pd, numpy as np
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
q = pd.read_csv(R + 'H07_qcew_sporting_allcounties.csv', dtype={'area_fips': str})
q['t'] = q.year * 4 + q.qtr - 1
q['disc'] = q.disclosure_code.fillna('').eq('')
emp = q.pivot_table(index='area_fips', columns='t', values='month3_emplvl', aggfunc='sum')
wag = q.pivot_table(index='area_fips', columns='t', values='total_qtrly_wages', aggfunc='sum')
dis = q.pivot_table(index='area_fips', columns='t', values='disc', aggfunc='min')
T = sorted(emp.columns)
stores = pd.read_csv(R + 'D01_store_county.csv', dtype={'fips': str})
ev = pd.read_csv(R + 'B5_hos_events.csv', dtype={'fips': str})
hos_f = set(stores[stores.hos == True].fips) | set(ev.fips)
ctrl = [f for f in set(stores.fips.dropna()) - hos_f if f in dis.index and not f.startswith('09') and dis.loc[f, T].fillna(False).all()]
Ce = emp.loc[ctrl, T].sum(); Cw = wag.loc[ctrl, T].sum()
P = pd.read_csv(R + 'B5_event_panel.csv', dtype={'fips': str})
D = P[P.disclosed].copy()
pd.set_option('display.width', 250)

def excess(Y, Ctot, f, t0, k):
    t = t0 + k; b = t0 - 5 + ((k + 1) % 4)
    return Y.loc[f, t] - Y.loc[f, b] * Ctot[t] / Ctot[b]

# (1) placebo
null = []
for _, e in ev.iterrows():
    t0 = int(e.open_q[:4]) * 4 + int(e.open_q[-1]) - 1
    if e.fips not in emp.index or t0 - 5 not in T:
        continue
    base = emp.loc[e.fips, t0 - 5:t0 - 2].mean()
    pool = [f for f in ctrl if 0.5 * base <= emp.loc[f, t0 - 5:t0 - 2].mean() <= 2 * base]
    for k in range(0, 9):
        if t0 + k not in T:
            continue
        vals = [excess(emp, Ce, f, t0, k) for f in pool]
        null.append(dict(city=e.city, k=k, n_pool=len(pool), null_mean=np.mean(vals), null_sd=np.std(vals),
                         null_p95=np.percentile(vals, 95)))
N = pd.DataFrame(null)
M = D.merge(N, on=['city', 'k'], how='left')
M['z'] = (M.emp_excess - M.null_mean) / M.null_sd.where(M.null_sd > 0)
M['pctile_rank_gt_p95'] = M.emp_excess > M.null_p95
print('(1) placebo: by k, mean HoS excess vs mean placebo excess and share of events above placebo 95th pct')
print(M[M.k >= 0].groupby('k').agg(n=('z', 'size'), hos=('emp_excess', 'mean'), placebo=('null_mean', 'mean'),
      placebo_sd=('null_sd', 'mean'), mean_z=('z', 'mean'), share_gt_p95=('pctile_rank_gt_p95', 'mean')).round(2).to_string())
# stacked t-stat at k=0..3 pooled
y1 = M[M.k.between(0, 3)]
print('pooled k=0..3: mean z', round(y1.z.mean(), 2), 'n', len(y1), '; share >p95', round(y1.pctile_rank_gt_p95.mean(), 2))

# (2) clean subsample
bad = {'Tulsa', 'Harris(Baybrook+Katy)', 'Glendale', 'Dallas(Galleria)'}
base = D[D.k.between(0, 3)].groupby('city').emp_base.mean()
clean = [c for c in base.index if base[c] < 1500 and c not in bad]
Dc = D[D.city.isin(clean)]
print('\n(2) clean subsample events:', len(clean))
print(Dc.groupby('k').agg(n=('emp_excess', 'size'), mean=('emp_excess', 'mean'), median=('emp_excess', 'median'),
      wag_mn=('wag_excess', lambda s: s.mean() / 1e6)).round(2).loc[-1:8].to_string())

# (3) balanced fade test
bal = [c for c, g in D.groupby('city') if set(range(0, 8)) <= set(g.k)]
print('\n(3) balanced k=0..7 events:', bal)
B = D[D.city.isin(bal)]
y1 = B[B.k.between(0, 3)].groupby('city')[['emp_excess', 'wag_excess', 'emp_base']].mean()
y2 = B[B.k.between(4, 7)].groupby('city')[['emp_excess', 'wag_excess']].mean()
F = y1.join(y2, lsuffix='_y1', rsuffix='_y2')
F['jobs_chg_%'] = (F.emp_excess_y2 / F.emp_excess_y1 - 1) * 100
F['wag_y1_ann_$M'] = F.wag_excess_y1 * 4 / 1e6
F['wag_y2_ann_$M'] = F.wag_excess_y2 * 4 / 1e6
F['pay_per_job_y1_$K'] = F.wag_excess_y1 * 4 / F.emp_excess_y1 / 1e3
F['pay_per_job_y2_$K'] = F.wag_excess_y2 * 4 / F.emp_excess_y2 / 1e3
print(F.round(1).to_string())
print('mean y1 jobs %.1f  y2 jobs %.1f ; median y1 %.1f y2 %.1f' % (F.emp_excess_y1.mean(), F.emp_excess_y2.mean(), F.emp_excess_y1.median(), F.emp_excess_y2.median()))
print('mean y1 wages $%.2fM/yr  y2 $%.2fM/yr' % (F['wag_y1_ann_$M'].mean(), F['wag_y2_ann_$M'].mean()))
F.to_csv(R + 'B5_fade_balanced.csv')
M.to_csv(R + 'B5_event_panel_placebo.csv', index=False)

# (4) county average weekly wage in sporting goods (baseline) for context
print('\n(4) pooled pay per excess job (all disclosed, k=0..8, excess>20):')
Z = D[(D.k >= 0) & (D.emp_excess > 20)]
print('median annualised $K', round((Z.wag_excess * 4 / Z.emp_excess).median() / 1e3, 1),
      '; county baseline pay per worker $K', round((Z.wag_base * 4 / Z.emp_base).median() / 1e3, 1))

