"""B4: NY taxable-sales event table for DICK'S Field House / next-gen relocations (data.ny.gov ny73-2j3u, NAICS 4511/4591).
Uses raw/B4_ny_4511_all_counties.csv (made by B4_ny_fh_counties.py). NY quarter q1=Mar-May, q2=Jun-Aug, q3=Sep-Nov, q4=Dec-Feb; yr = year in which the sales-tax year starts.
Excess = county pre-period level x (county growth - NY State growth). Also a 'rest of upstate' control (all counties outside NYC/MCTD).
Rerun: python B4_ny_fh_event.py -> raw/B4_ny_fh_event.csv
"""
import pandas as pd
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
df = pd.read_csv(R + 'B4_ny_4511_all_counties.csv')
p = df.pivot_table(index=['yr', 'q'], columns='jurisdiction', values='v', aggfunc='sum').sort_index() / 1e6
idx = list(p.index)
mctd = ['NY STATE', 'MCTD', 'NEW YORK CITY', 'BRONX', 'KINGS', 'NEW YORK', 'QUEENS', 'RICHMOND', 'NASSAU', 'SUFFOLK', 'WESTCHESTER', 'ROCKLAND', 'PUTNAM', 'ORANGE', 'DUTCHESS']
ups = [c for c in p.columns if c not in mctd and c.isupper() and c not in ('ONTARIO',)]  # Ontario Sep-Nov 2025 = $240.9M anomaly (H07-7)
events = [  # county, label, first (partial) post quarter, store note
    ('TOMPKINS', 'Ithaca #156 -> #1535 South Meadow Sq (~Dec-2023)', (2023, 4)),
    ('JEFFERSON', 'Watertown #158 -> #1545 Towne Center (opened 2024-04-17)', (2024, 1)),
    ('MONROE', 'Rochester Marketplace Mall #427 -> Henrietta #1630 50K (opened 2025-05-08)', (2025, 1)),
    ('ULSTER', 'Kingston HV Mall #154 -> #1622 53K HV Plaza (moved 2026-03-11)', (2026, 1)),
    ('ONTARIO', 'Victor HoS #1500 (Apr-2021) [known; reference only]', (2021, 1)),
    ('CAYUGA', 'Auburn #705 closed (~Jan-2026, Syracuse.com 2026-01-06) [closure control]', (2025, 4)),
]
rows = []
for c, lab, e in events:
    i = idx.index(e)
    for k, nq in [('Y1', 4), ('Y2', 4)]:
        s = i + (0 if k == 'Y1' else 4)
        post = idx[s:s + nq]
        if len(post) < 1 or s >= len(idx):
            continue
        pre = [idx[idx.index(q) - 4] for q in post]  # same quarters one year earlier
        if k == 'Y2':
            pre = [idx[idx.index(q) - 8] for q in post]  # vs pre-event year
        pre0 = [idx[i - 4 + j] for j in range(len(post))] if k == 'Y1' else pre
        cp, cq = p.loc[pre, c].sum(), p.loc[post, c].sum()
        sp, sq = p.loc[pre, 'NY STATE'].sum(), p.loc[post, 'NY STATE'].sum()
        up, uq = p.loc[pre, ups].sum().sum() - p.loc[pre, c].sum(), p.loc[post, ups].sum().sum() - p.loc[post, c].sum()
        gc, gs, gu = cq / cp - 1, sq / sp - 1, uq / up - 1
        gmed = float((p.loc[post, [u for u in ups if u != c]].sum() / p.loc[pre, [u for u in ups if u != c]].sum() - 1).median())
        rows.append({'county': c, 'event': lab, 'window': k, 'quarters': f'{post[0]}..{post[-1]} ({len(post)}q)', 'pre_$M': round(cp, 2), 'post_$M': round(cq, 2),
                     'county_g%': round(gc * 100, 1), 'state_g%': round(gs * 100, 1), 'upstate_g%': round(gu * 100, 1), 'median_upstate_county_g%': round(gmed * 100, 1), 'excess_vs_median_': round(cp * (gc - gmed), 2),
                     'excess_vs_state_$M': round(cp * (gc - gs), 2), 'excess_vs_upstate_$M': round(cp * (gc - gu), 2),
                     'annualised_excess_vs_upstate_$M': round(cp * (gc - gu) * 4 / len(post), 2)})
out = pd.DataFrame(rows)
out.to_csv(R + 'B4_ny_fh_event.csv', index=False)
pd.set_option('display.width', 300); pd.set_option('display.max_colwidth', 60)
print(out.to_string(index=False))


