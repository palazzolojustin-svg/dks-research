"""B11: robust VA event tests. Two controls:
 (a) regional sum control (Chesapeake vs Hampton Roads ex-Chesapeake: VB, Norfolk, Portsmouth, Suffolk, Hampton, Newport News)
 (b) median y/y of the 20+ large localities (>$5M/qtr), excluding Rockbridge (anomalous) and the event locality.
Annual windows aligned to the opening quarter. Rerun: python scripts/B11_va_event2.py -> raw/B11_VA_event2.csv"""
import pandas as pd, numpy as np
p = pd.read_csv('raw/B11_VA_panel.csv', dtype={'naics': str}); p = p[(p.naics == '451') & (p.sheet != 'State')]
loc = p.pivot_table(index=['year', 'q'], columns='locality', values='amount', aggfunc='sum') / 1e6
big = [c for c in loc.columns[loc.loc[(2024, 1):].mean() > 5] if c != 'Rockbridge']
idx = list(loc.index)
HR = ['Virginia Beach', 'Norfolk', 'Portsmouth', 'Suffolk', 'Hampton', 'Newport News']
loc['HR'] = loc[HR].sum(axis=1)
loc['CV'] = loc[['Albemarle', 'Charlottesville']].sum(axis=1)
def w(start, n): i = idx.index(start); return idx[i:i + n]
rows = []
def ratio_test(name, col, ctl, pre, posts):
    r0 = loc.loc[pre, col].sum() / loc.loc[pre, ctl].sum()
    for lab, ww in posts:
        ww = [x for x in ww if x in idx]
        act = loc.loc[ww, col].sum(); exp = r0 * loc.loc[ww, ctl].sum()
        rows.append(dict(event=name, method=f'ratio to {ctl}', pre=f'{pre[0]}-{pre[-1]}', window=lab, nq=len(ww), actual=act, expected=exp, excess=act - exp, excess_ann=(act - exp) * 4 / len(ww)))
def median_chain(name, col, pre, posts):
    peers = [c for c in big if c not in (col, 'Albemarle', 'Charlottesville', 'Chesapeake')]
    for lab, ww in posts:
        ww = [x for x in ww if x in idx]
        act = 0; exp = 0
        for t in ww:
            # same quarter in pre window (matching season)
            base = [b for b in pre if b[1] == t[1]][0]
            g = np.median(loc.loc[t, peers] / loc.loc[base, peers])
            act += loc.loc[t, col]; exp += loc.loc[base, col] * g
        rows.append(dict(event=name, method='median peer growth vs same-season pre quarter', pre=f'{pre[0]}-{pre[-1]}', window=lab, nq=len(ww), actual=act, expected=exp, excess=act - exp, excess_ann=(act - exp) * 4 / len(ww)))
ch = 'Chesapeake HoS (late-Jul 2023; DSG + 2016 Field & Stream combined in place, ~90K sf)'
for pre in [w((2022, 2), 4), w((2021, 3), 4)]:
    posts = [('Y1 2023Q3-2024Q2 ex 2024Q2*', w((2023, 3), 3)), ('Y2 2024Q3-2025Q2', w((2024, 3), 4)), ('Y3 2025Q3-2026Q2', w((2025, 3), 4))]
    ratio_test(ch, 'Chesapeake', 'HR', pre, posts); median_chain(ch, 'Chesapeake', pre, posts)
cv = 'Charlottesville HoS (2025-10-31, Fashion Square, Albemarle)'
for col in ['Albemarle', 'CV']:
    for pre in [w((2024, 4), 4), w((2023, 4), 4)]:
        posts = [('3q post 2025Q4-2026Q2', w((2025, 4), 3)), ('2026Q1-Q2 (full quarters)', w((2026, 1), 2))]
        median_chain(cv + ' [' + col + ']', col, pre, posts)
o = pd.DataFrame(rows).round(2); o.to_csv('raw/B11_VA_event2.csv', index=False)
pd.set_option('display.width', 260); pd.set_option('display.max_colwidth', 70); print(o.to_string())
