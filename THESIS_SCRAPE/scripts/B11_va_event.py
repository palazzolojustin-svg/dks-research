"""B11: Virginia HoS event tests on NAICS 451 taxable sales (locality x quarter).
Control = Virginia state total 451 ex the event localities and ex Rockbridge (anomalous ~$100M/yr dealer).
Method: share-of-control. Excess($) in a post window = actual - (pre-window share x control in post window).
Rerun: python scripts/B11_va_event.py  -> raw/B11_VA_event.csv"""
import pandas as pd
p = pd.read_csv('raw/B11_VA_panel.csv', dtype={'naics': str})
p = p[p.naics == '451']
loc = p[p.sheet != 'State'].pivot_table(index=['year', 'q'], columns='locality', values='amount', aggfunc='sum') / 1e6
state = p[p.sheet == 'State'].groupby(['year', 'q']).amount.sum() / 1e6
ctrl = state - loc[['Rockbridge', 'Albemarle', 'Charlottesville', 'Chesapeake']].sum(axis=1)
loc['CTRL'] = ctrl
loc['CVILLE_MSA'] = loc[['Albemarle', 'Charlottesville']].sum(axis=1)
loc['HAMPTON_RDS_EX_CHES'] = loc[['Virginia Beach', 'Norfolk', 'Portsmouth', 'Suffolk', 'Hampton', 'Newport News']].sum(axis=1)
idx = list(loc.index)
def win(start, n):
    i = idx.index(start); return idx[i:i + n]
out = []
def event(name, col, pre, posts):
    sh = loc.loc[pre, col].sum() / loc.loc[pre, 'CTRL'].sum()
    for lab, w in posts:
        w = [x for x in w if x in idx]
        if not w: continue
        act = loc.loc[w, col].sum(); exp = sh * loc.loc[w, 'CTRL'].sum()
        ann = (act - exp) * 4 / len(w)
        out.append(dict(event=name, series=col, pre=f'{pre[0]}..{pre[-1]}', window=lab, nq=len(w), actual=round(act, 2), expected=round(exp, 2), excess=round(act - exp, 2), excess_annualised=round(ann, 2), pre_share=round(sh * 100, 3)))
# Chesapeake HoS: in-place DSG+F&S (2016) -> ~90K sf HoS; closed for conversion ~2023Q2; opened late Jul 2023.
pre = win((2022, 2), 4)  # 2022Q2-2023Q1
event('Chesapeake HoS (Jul-2023, DSG+F&S combined in place)', 'Chesapeake', pre, [('Y1 2023Q3-2024Q2', win((2023, 3), 4)), ('Y2 2024Q3-2025Q2', win((2024, 3), 4)), ('Y3 2025Q3-2026Q2', win((2025, 3), 4))])
pre = win((2021, 2), 8)
event('Chesapeake HoS (alt pre: 2021Q2-2023Q1, 8q)', 'Chesapeake', pre, [('Y1', win((2023, 3), 4)), ('Y2', win((2024, 3), 4)), ('Y3', win((2025, 3), 4))])
# Charlottesville HoS (Fashion Square, Albemarle), opened 2025-10-31
pre = win((2024, 4), 4)  # 2024Q4-2025Q3
for col in ['Albemarle', 'CVILLE_MSA']:
    event('Charlottesville HoS (Oct-31-2025)', col, pre, [('2025Q4', [(2025, 4)]), ('2026Q1', [(2026, 1)]), ('2026Q2', [(2026, 2)]), ('3q post 2025Q4-2026Q2', win((2025, 4), 3))])
    pre8 = win((2023, 4), 8)
    event('Charlottesville HoS (alt pre 8q 2023Q4-2025Q3)', col, pre8, [('3q post', win((2025, 4), 3))])
o = pd.DataFrame(out); o.to_csv('raw/B11_VA_event.csv', index=False)
pd.set_option('display.width', 250); print(o.to_string())
s = loc[['Albemarle', 'Charlottesville', 'CVILLE_MSA', 'Chesapeake', 'HAMPTON_RDS_EX_CHES', 'CTRL']].round(2)
s.to_csv('raw/B11_VA_451_series.csv'); print(s.to_string())
