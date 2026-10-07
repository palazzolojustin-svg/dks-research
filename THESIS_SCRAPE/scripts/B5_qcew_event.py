"""B5: stacked event study of BLS QCEW county sporting-goods-store employment / wages / establishments
around DICK'S House of Sport openings.

Inputs : raw/H07_qcew_sporting_allcounties.csv (H07 pull: private NAICS 451110 2019-21, 459110 2022-26Q1, all US counties)
         raw/D01_store_county.csv (DKS locator stores -> county FIPS)
         raw/B5_hos_events.csv (hand-built opening dates, sources in file)
Method : season-matched share-of-control. Baseline year = quarters t0-5..t0-2 (t0-1 excluded: pre-opening hiring).
         For event quarter k, b(k) = t0-5 + ((k+1) mod 4).  excess_k = Y_c(t0+k) - Y_c(b) * C(t0+k)/C(b)
         where C = sum over control counties (DKS counties without any HoS, fully disclosed 2019Q1-2026Q1, CT dropped).
Outputs: raw/B5_event_panel.csv (event x k), prints stacked means.
Rerun  : python scripts/B5_qcew_event.py
"""
import pandas as pd, numpy as np
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
q = pd.read_csv(R + 'H07_qcew_sporting_allcounties.csv', dtype={'area_fips': str})
q['t'] = q.year * 4 + q.qtr - 1
q['disc'] = q.disclosure_code.fillna('').eq('')
emp = q.pivot_table(index='area_fips', columns='t', values='month3_emplvl', aggfunc='sum')
wag = q.pivot_table(index='area_fips', columns='t', values='total_qtrly_wages', aggfunc='sum')
est = q.pivot_table(index='area_fips', columns='t', values='qtrly_estabs', aggfunc='sum')
dis = q.pivot_table(index='area_fips', columns='t', values='disc', aggfunc='min')
T = sorted(emp.columns)
stores = pd.read_csv(R + 'D01_store_county.csv', dtype={'fips': str})
ev = pd.read_csv(R + 'B5_hos_events.csv', dtype={'fips': str})
hos_f = set(stores[stores.hos == True].fips) | set(ev.fips)
dks_f = set(stores.fips.dropna())
ctrl = [f for f in dks_f - hos_f if f in dis.index and not f.startswith('09') and dis.loc[f, T].fillna(False).all()]
print('control counties fully disclosed:', len(ctrl))
C = {'emp': emp.loc[ctrl, T].sum(), 'wag': wag.loc[ctrl, T].sum(), 'est': est.loc[ctrl, T].sum()}
Y = {'emp': emp, 'wag': wag, 'est': est}
rows = []
for _, e in ev.iterrows():
    f = e.fips
    if f not in emp.index:
        continue
    t0 = int(e.open_q[:4]) * 4 + int(e.open_q[-1]) - 1
    for k in range(-8, 21):
        t = t0 + k
        if t not in T:
            continue
        b = t0 - 5 + ((k + 1) % 4)
        if b not in T:
            continue
        r = dict(store=e.store, city=e.city, fips=f, open_q=e.open_q, type=e.type, k=k, t=f'{t // 4}Q{t % 4 + 1}',
                 disclosed=bool(dis.loc[f, t]) and bool(dis.loc[f, b]))
        for v in ('emp', 'wag', 'est'):
            yc, yb = Y[v].loc[f, t], Y[v].loc[f, b]
            r[v] = yc
            r[v + '_base'] = yb
            r[v + '_excess'] = yc - yb * C[v][t] / C[v][b]
        rows.append(r)
P = pd.DataFrame(rows)
P.to_csv(R + 'B5_event_panel.csv', index=False)
pd.set_option('display.width', 250)
D = P[P.disclosed]
print('\nStacked mean excess by event quarter k (disclosed obs only):')
g = D.groupby('k').agg(n=('emp_excess', 'size'), emp_x=('emp_excess', 'mean'), emp_x_med=('emp_excess', 'median'),
                       wag_x_mn=('wag_excess', lambda s: s.mean() / 1e6), est_x=('est_excess', 'mean'))
print(g.round(2).to_string())
print('\nPer-event excess jobs (k=-4..8):')
w = D.pivot_table(index=['open_q', 'city', 'fips'], columns='k', values='emp_excess').round(0)
print(w.to_string())
print('\nPer-event baseline emp (mean of base year):')
print(D[D.k.between(0, 3)].groupby(['open_q', 'city']).emp_base.mean().round(0).to_string())
