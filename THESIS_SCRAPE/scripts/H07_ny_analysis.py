"""H07: event-study of NY county sporting-goods (NAICS 4511/4591) taxable sales around House of Sport openings.
Input raw/H07_NY_sporting_by_county.csv (from H07_ny_sporting.py). Control = sum of all 57 counties outside NYC
(excludes 'NY STATE', 'MCTD', 'NY CITY', and the treated county). Share-of-control method:
excess($/yr) = (post share - pre share) x control total (post window).
NY sales-tax quarter: Q1 Mar-May, Q2 Jun-Aug, Q3 Sep-Nov, Q4 Dec-Feb.
Rerun: python H07_ny_analysis.py
"""
import pandas as pd
df = pd.read_csv(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\H07_NY_sporting_by_county.csv')
p = df.pivot_table(index=['yr', 'q'], columns='jurisdiction', values='taxable_sales_and_purchases', aggfunc='sum') / 1e6
counties = [c for c in p.columns if c not in ('NY STATE', 'MCTD', 'NY CITY')]
# treated: county, first full post quarter (yr,q), pre window = 4 qtrs ending the quarter before opening quarter
events = {
    'ONTARIO (Victor HoS, opened Apr-2021, relocation from plaza across Rt 96)': ('ONTARIO', (2021, 1)),
    'BROOME (Johnson City HoS, opened Aug-2023)': ('BROOME', (2023, 2)),
    'ALBANY (Latham HoS, opened Jul-2023)': ('ALBANY', (2023, 2)),
}
idx = list(p.index)
pd.set_option('display.width', 250)
for name, (c, ev) in events.items():
    ctrl = p[[x for x in counties if x != c]].sum(axis=1)
    share = p[c] / ctrl
    i = idx.index(ev)
    pre = idx[max(0, i - 4):i]
    # skip covid-distorted 2020Q1 for Ontario pre window: use 2019Q1-2019Q4 and 2020Q2-Q4 as alt
    post1 = idx[i + 1:i + 5]
    post2 = idx[i + 5:i + 9]
    def tot(ix, s): return s.loc[ix].sum()
    print('\n==', name)
    for lab, w in [('pre4', pre), ('post q2-5', post1), ('post q6-9', post2)]:
        w = [x for x in w if not (c == 'ONTARIO' and x == (2025, 3))]  # drop Ontario 2025Q3 anomaly (240.9M)
        if not w: continue
        print(f"{lab:10s} {w[0]}..{w[-1]}  county ${tot(w, p[c]):7.1f}M  control ${tot(w, ctrl):8.1f}M  share {tot(w, p[c]) / tot(w, ctrl) * 100:5.2f}%")
    pre_sh = tot(pre, p[c]) / tot(pre, ctrl)
    for lab, w in [('post q2-5', post1), ('post q6-9', post2)]:
        if len(w) < 4: continue
        post_sh = tot(w, p[c]) / tot(w, ctrl)
        print(f"  excess {lab}: ${(post_sh - pre_sh) * tot(w, ctrl):.1f}M per 4 qtrs; county y/y vs pre {tot(w, p[c]) / tot(pre, p[c]) - 1:+.1%}, control {tot(w, ctrl) / tot(pre, ctrl) - 1:+.1%}")
print('\nAnnual share table (%), Mar-Feb sales-tax years:')
ann = p.groupby(level=0).sum()
ctrl_all = ann[counties].sum(axis=1)
print((ann[['ONTARIO', 'MONROE', 'BROOME', 'ALBANY', 'ERIE', 'SARATOGA']].div(ctrl_all, axis=0) * 100).round(2).to_string())
print((ann[['ONTARIO', 'MONROE', 'BROOME', 'ALBANY', 'ERIE', 'SARATOGA']]).round(1).assign(CTRL=ctrl_all.round(0)).to_string())
