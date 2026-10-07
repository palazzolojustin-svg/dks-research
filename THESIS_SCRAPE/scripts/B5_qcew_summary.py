"""B5: per-event and grouped summary of the QCEW HoS event study (reads raw/B5_event_panel.csv).
Groups: net-new (no in-county DSG closed), relocation/conversion, unknown; small county (base < 300 jobs) where HoS dominates.
Outputs raw/B5_event_summary.csv. Rerun: python scripts/B5_qcew_summary.py
"""
import pandas as pd, numpy as np
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
P = pd.read_csv(R + 'B5_event_panel.csv', dtype={'fips': str})
D = P[P.disclosed].copy()
D['yr'] = np.where(D.k < 0, 0, D.k // 4 + 1)
D.loc[D.k == -1, 'yr'] = -1
S = D.groupby(['open_q', 'city', 'type']).apply(lambda g: pd.Series({
    'base_emp': g[g.k.between(0, 3)].emp_base.mean(),
    'pre_trend_k-8..-6': g[g.k.between(-8, -6)].emp_excess.mean(),
    'k-1': g[g.k == -1].emp_excess.mean(),
    'y1_jobs': g[g.yr == 1].emp_excess.mean(), 'y2_jobs': g[g.yr == 2].emp_excess.mean(), 'y3_jobs': g[g.yr == 3].emp_excess.mean(),
    'y1_wages_$M_ann': g[g.yr == 1].wag_excess.mean() * 4 / 1e6, 'y2_wages_$M_ann': g[g.yr == 2].wag_excess.mean() * 4 / 1e6,
    'y1_estabs': g[g.yr == 1].est_excess.mean(), 'n_post_q': (g.k >= 0).sum()}), include_groups=False).reset_index()
def grp(t):
    t = str(t)
    if 'net-new' in t: return 'net-new'
    if any(w in t for w in ('relocation', 'conversion', 'remodel', 'in-place', 'consolidation', 'reopened')): return 'relocation/conversion'
    return 'unknown'
S['group'] = S.type.map(grp)
S.loc[S.city.isin(['Tulsa', 'Harris(Baybrook+Katy)', 'Glendale', 'Dallas(Galleria)']), 'group'] += ' [contaminated/large]'
S.to_csv(R + 'B5_event_summary.csv', index=False)
pd.set_option('display.width', 260)
print(S.drop(columns='type').round(1).to_string(index=False))
print('\nGroup means / medians (y1 jobs, y2 jobs):')
print(S.groupby('group').agg(n=('city', 'size'), y1_mean=('y1_jobs', 'mean'), y1_med=('y1_jobs', 'median'), y2_mean=('y2_jobs', 'mean'),
      y2_med=('y2_jobs', 'median'), y1_wage_med=('y1_wages_$M_ann', 'median'), km1=('k-1', 'mean')).round(1).to_string())
sm = S[(S.base_emp < 300)]
print('\nSmall-county (base<300) events:', len(sm))
print(sm[['city', 'open_q', 'base_emp', 'k-1', 'y1_jobs', 'y2_jobs', 'y3_jobs', 'y1_wages_$M_ann', 'y2_wages_$M_ann']].round(1).to_string(index=False))
b = sm.dropna(subset=['y2_jobs'])
print('small-county balanced y1->y2: n=%d y1 %.1f y2 %.1f (%.0f%%); wages y1 %.2f y2 %.2f $M' % (len(b), b.y1_jobs.mean(), b.y2_jobs.mean(),
      (b.y2_jobs.mean() / b.y1_jobs.mean() - 1) * 100, b['y1_wages_$M_ann'].mean(), b['y2_wages_$M_ann'].mean()))
b3 = sm.dropna(subset=['y3_jobs'])
print('small-county y3 available: n=%d y1 %.1f y3 %.1f' % (len(b3), b3.y1_jobs.mean(), b3.y3_jobs.mean()))
clean = S[~S.group.str.contains('contaminated')]
print('\nAll clean events: n=%d  y1 jobs mean %.1f median %.1f ; y1 wages median $%.2fM/yr ; k-1 mean %.1f' % (
    clean.y1_jobs.notna().sum(), clean.y1_jobs.mean(), clean.y1_jobs.median(), clean['y1_wages_$M_ann'].median(), clean['k-1'].mean()))
