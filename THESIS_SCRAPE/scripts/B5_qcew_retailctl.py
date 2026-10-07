"""B5: robustness - county-specific control. Pulls QCEW private all-retail (NAICS 44-45, slice '44_45') for the HoS event counties
(2019Q1-2026Q1) and recomputes excess sporting-goods jobs using the county's OWN retail-ex-sporting-goods growth as the control:
excess_k = SG_c(t) - SG_c(b) * RX_c(t)/RX_c(b), RX = retail 44-45 minus sporting goods. Same b(k) as B5_qcew_event.py.
Outputs raw/B5_qcew_retail_events.csv (county retail series) and raw/B5_event_panel_retailctl.csv; prints stacked means.
Rerun: python scripts/B5_qcew_retailctl.py
"""
import requests, io, os, pandas as pd, numpy as np
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
H = {'User-Agent': 'Mozilla/5.0 research palazzolojustin@gmail.com'}
ev = pd.read_csv(R + 'B5_hos_events.csv', dtype={'fips': str})
F = set(ev.fips)
cache = R + 'B5_qcew_retail_events.csv'
if os.path.exists(cache):
    ret = pd.read_csv(cache, dtype={'area_fips': str})
else:
    fr = []
    for yr in range(2019, 2027):
        for q in range(1, 5):
            r = requests.get(f'https://data.bls.gov/cew/data/api/{yr}/{q}/industry/44_45.csv', headers=H, timeout=180)
            if r.status_code != 200:
                continue
            d = pd.read_csv(io.StringIO(r.text), dtype={'area_fips': str})
            d = d[(d.own_code == 5) & d.area_fips.isin(F)][['area_fips', 'year', 'qtr', 'month3_emplvl', 'total_qtrly_wages', 'disclosure_code']]
            fr.append(d); print(yr, q, len(d), flush=True)
    ret = pd.concat(fr); ret.to_csv(cache, index=False)
ret['t'] = ret.year * 4 + ret.qtr - 1
RE = ret.pivot_table(index='area_fips', columns='t', values='month3_emplvl', aggfunc='sum')
P = pd.read_csv(R + 'B5_event_panel.csv', dtype={'fips': str})
out = []
for _, r in P.iterrows():
    k = r.k; t0 = int(r.open_q[:4]) * 4 + int(r.open_q[-1]) - 1; t = t0 + k; b = t0 - 5 + ((k + 1) % 4)
    try:
        rx_t = RE.loc[r.fips, t] - r.emp; rx_b = RE.loc[r.fips, b] - r.emp_base
        out.append(dict(r, retail_ex_t=rx_t, retail_ex_b=rx_b, emp_excess_rc=r.emp - r.emp_base * rx_t / rx_b))
    except KeyError:
        pass
O = pd.DataFrame(out)
O.to_csv(R + 'B5_event_panel_retailctl.csv', index=False)
D = O[O.disclosed & ~O.city.isin(['Tulsa', 'Harris(Baybrook+Katy)', 'Glendale', 'Dallas(Galleria)'])]
pd.set_option('display.width', 200)
print(D.groupby('k').agg(n=('emp_excess_rc', 'size'), own_retail_ctl_mean=('emp_excess_rc', 'mean'), own_retail_ctl_med=('emp_excess_rc', 'median'),
      dks_ctl_mean=('emp_excess', 'mean')).loc[-8:12].round(1).to_string())
D2 = D[D.k >= 0].copy(); D2['yr'] = D2.k // 4 + 1
print(D2.pivot_table(index='city', columns='yr', values='emp_excess_rc', aggfunc='mean').round(0).to_string())
