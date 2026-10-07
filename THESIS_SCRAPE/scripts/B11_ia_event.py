"""B11: Iowa county x business group quarterly taxable sales (DOR Table 4), 2015Q4-2025Q4.
Event: Davenport HoS #1582 (NorthPark area, in-place remodel, reopened 2023-07-21), Scott County.
Control: state total for the same business group ex Scott; also median growth of the 10 largest counties.
Rerun: python scripts/B11_ia_event.py -> raw/B11_IA_county_group.csv, raw/B11_IA_event.csv"""
import pandas as pd, glob, re, warnings, numpy as np
warnings.filterwarnings('ignore')
MON = {'March': 1, 'June': 2, 'September': 3, 'December': 4}
rows = []
for f in glob.glob('raw/B11_cache/ia/*.xls*'):
    y, m = re.search(r'(\d{4})_(\w+)\.', f).groups(); q = MON[m]
    x = pd.ExcelFile(f)
    sh = [s for s in x.sheet_names if s.startswith('Table 4')]
    if not sh: print('no T4', f, x.sheet_names); continue
    d = pd.read_excel(x, sh[0], header=None)
    for _, r in d.iterrows():
        if isinstance(r[0], str) and isinstance(r[1], str) and len(r) > 3:
            try: amt = float(r[3])
            except: continue
            rows.append(dict(year=int(y), q=q, county=r[0].strip(), group=r[1].strip().title(), returns=r[2], taxable=amt))
p = pd.DataFrame(rows); p.to_csv('raw/B11_IA_county_group.csv', index=False)
print(p.groupby(['year', 'q']).size().tail(8))
out = []
for grp in ['Specialty Retail', 'Apparel', 'General Merchandise', 'County Totals']:
    t = p[p.group == grp].pivot_table(index=['year', 'q'], columns='county', values='taxable', aggfunc='sum') / 1e6
    big = t.loc[(2022, 1):].mean().sort_values(ascending=False).index[:12]
    peers = [c for c in big if c != 'Scott']
    ctl = t[[c for c in t.columns if c != 'Scott']].sum(axis=1)
    idx = list(t.index)
    def w(s, n): i = idx.index(s); return idx[i:i + n]
    for pre in [w((2022, 3), 4), w((2021, 3), 4)]:
        sh = t.loc[pre, 'Scott'].sum() / ctl.loc[pre].sum()
        for lab, ww in [('Y1 2023Q3-2024Q2', w((2023, 3), 4)), ('Y2 2024Q3-2025Q2', w((2024, 3), 4)), ('2025Q3-Q4', w((2025, 3), 2))]:
            act = t.loc[ww, 'Scott'].sum(); exp = sh * ctl.loc[ww].sum()
            med = 0
            for tt in ww:
                base = [b for b in pre if b[1] == tt[1]][0]
                med += t.loc[base, 'Scott'] * np.median(t.loc[tt, peers] / t.loc[base, peers])
            out.append(dict(group=grp, pre=f'{pre[0]}-{pre[-1]}', window=lab, actual=act, exp_share=exp, excess_share_ann=(act - exp) * 4 / len(ww), exp_median=med, excess_median_ann=(act - med) * 4 / len(ww), pre_level_ann=t.loc[pre, 'Scott'].sum()))
    if grp == 'Specialty Retail':
        print((t[['Scott', 'Linn', 'Polk', 'Johnson', 'Black Hawk']].loc[(2021, 1):]).round(1).to_string())
o = pd.DataFrame(out).round(2); o.to_csv('raw/B11_IA_event.csv', index=False)
pd.set_option('display.width', 250); print(o.to_string())
