"""B5: Field House (next-gen ~50K) county long-difference test with QCEW (no exact FH dates exist, so use store-number cohorts).
Treated = counties with a B4 FH-candidate store (tier 1 = store numbers 1560+, opened ~2024-26; tier 2 = 1500-1559, ~2021-24)
and NO House of Sport. Control = other DKS counties without HoS, fully disclosed. Outcome: sporting-goods (NAICS 451110/459110)
month-3 employment and quarterly wages, Q1-2024 -> Q1-2026 and Q4-2023 -> Q4-2025 (excess = treated change - control-implied change).
Rerun: python scripts/B5_fh_longdiff.py   (needs raw/H07_qcew_sporting_allcounties.csv, raw/D01_store_county.csv, raw/B4_fh_candidates.csv,
raw/B5_hos_events.csv) -> raw/B5_fh_longdiff.csv
"""
import pandas as pd, numpy as np
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
q = pd.read_csv(R + 'H07_qcew_sporting_allcounties.csv', dtype={'area_fips': str})
q['disc'] = q.disclosure_code.fillna('').eq('')
st = pd.read_csv(R + 'D01_store_county.csv', dtype={'fips': str})
fh = pd.read_csv(R + 'B4_fh_candidates.csv')
ev = pd.read_csv(R + 'B5_hos_events.csv', dtype={'fips': str})
hosf = set(st[st.hos == True].fips) | set(ev.fips)
fh = fh.merge(st[['storeno', 'fips']], on='storeno', how='left')
print('FH candidates', len(fh), 'mapped', fh.fips.notna().sum())
def val(f, y, qt, col):
    s = q[(q.area_fips == f) & (q.year == y) & (q.qtr == qt)]
    return s[col].sum() if len(s) and s.disc.all() else np.nan
rows = []
allf = set(st.fips.dropna()) - hosf
for f in allf:
    if f.startswith('09'):
        continue
    r = dict(fips=f)
    for (y, qt) in [(2023, 4), (2024, 1), (2025, 4), (2026, 1)]:
        r[f'e{y}q{qt}'] = val(f, y, qt, 'month3_emplvl'); r[f'w{y}q{qt}'] = val(f, y, qt, 'total_qtrly_wages')
    sub = fh[fh.fips == f]
    r['tier'] = sub.tier.min() if len(sub) else 0
    r['n_fh'] = len(sub); r['n_dks'] = (st.fips == f).sum()
    rows.append(r)
D = pd.DataFrame(rows).dropna(subset=['e2024q1', 'e2026q1', 'e2023q4', 'e2025q4'])
ctl = D[D.tier == 0]
for a, b in [('2024q1', '2026q1'), ('2023q4', '2025q4')]:
    g = ctl[f'e{b}'].sum() / ctl[f'e{a}'].sum(); gw = ctl[f'w{b}'].sum() / ctl[f'w{a}'].sum()
    D[f'exc_{a}_{b}'] = D[f'e{b}'] - D[f'e{a}'] * g
    D[f'excw_{a}_{b}'] = (D[f'w{b}'] - D[f'w{a}'] * gw) * 4
    print(f'\n{a}->{b}: control growth emp {g-1:+.2%}, wages {gw-1:+.2%}')
    print(D.groupby('tier').agg(n=('fips', 'size'), n_fh=('n_fh', 'sum'), exc_mean=(f'exc_{a}_{b}', 'mean'), exc_med=(f'exc_{a}_{b}', 'median'),
          excw_mean_M=(f'excw_{a}_{b}', lambda s: s.mean() / 1e6)).round(2).to_string())
    # per FH store (treated counties): sum of excess / number of FH stores
    for t in (1, 2):
        T = D[D.tier == t]
        print(f' tier {t}: excess jobs per FH store = {T[f"exc_{a}_{b}"].sum() / T.n_fh.sum():.1f}; '
              f't-stat vs control dispersion = {T[f"exc_{a}_{b}"].mean() / (D[D.tier == 0][f"exc_{a}_{b}"].std() / np.sqrt(len(T))):.2f}')
pd.set_option('display.width', 250)
print('\ntier-1 counties detail:')
print(D[D.tier == 1][['fips', 'n_fh', 'n_dks', 'e2024q1', 'e2026q1', 'exc_2024q1_2026q1', 'exc_2023q4_2025q4']].merge(
    fh[['fips', 'storeno', 'city', 'state']].groupby('fips').agg(lambda s: ','.join(map(str, s))), on='fips').round(0).to_string(index=False))
D.to_csv(R + 'B5_fh_longdiff.csv', index=False)
