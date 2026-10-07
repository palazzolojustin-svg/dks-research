"""D07: DICK'S-segment cost-line decomposition by quarter (Q1 FY24 - Q2 FY26) from 10-K/10-Q segment notes
(CODM expense categories, ASU 2023-07). Values $000 transcribed from WORKING_NOTES W04 (10-Q notes) and W01 (10-K Note 16/17),
verified against SOURCE\\01_DKS_SEC_FILINGS\\10-Q\\DKS_10-Q_FY2026-Q2_filed-2026-09-03.md.
Note: 'other' in FY24/1H FY25 single-segment tables included corporate items (M&I, deferred comp) -> other % is not like-for-like before Q3 FY25.
Rerun: python THESIS_SCRAPE\\scripts\\D07_dsg_cost_lines.py  -> writes THESIS_SCRAPE\\raw\\D07_dsg_cost_lines.csv
"""
import csv
rows = {  # qtr: (sales, cogs, occupancy, personnel, other, segment_profit_or_None)
 'Q1FY24': (3018383, 1501409, 273739, 442257, 470179, None),
 'Q2FY24': (3473635, 1755464, 283159, 456558, 508358, None),
 'Q3FY24': (3057181, 1525800, 289477, 456822, 495562, 289520),
 'Q4FY24': (13442849-3018383-3473635-3057181, 6813682-1501409-1755464-1525800, 1139387-273739-283159-289477,
            1869257-1355637, 2122954-(1459954), None),
 'Q1FY25': (3174677, 1567248, 289836, 455238, 501947, 360408),
 'Q2FY25': (3646616, 1836326, 294245, 486648, 554445, 474952),
 'Q3FY25': (3236860, 1613894, 303280, 485490, 545625, 288571),
 'Q4FY25': (14108943-10058153, 7100929-5017467, 1197019-887361, 1972850-1427377, 2269702-1602016, 444511),
 'Q1FY26': (3377440, 1677274, 307735, 499482, 531974, 360975),
 'Q2FY26': (3849887, 1885917, 318130, 530387, 630249, 485204),
}
out = []
for q, (s, c, o, p, x, sp) in rows.items():
    out.append(dict(qtr=q, sales=s, cogs_pct=round(100*c/s, 2), occ_pct=round(100*o/s, 2), pers_pct=round(100*p/s, 2),
                    other_pct=round(100*x/s, 2), personnel=p))
idx = {r['qtr']: r for r in out}
for r in out:
    q = r['qtr']; py = q[:2] + 'FY' + str(int(q[4:]) - 1)
    if py in idx:
        b = idx[py]
        r['sales_yoy'] = round(100*(r['sales']/b['sales']-1), 1)
        r['pers_yoy'] = round(100*(r['personnel']/b['personnel']-1), 1)
        for k in ('cogs_pct', 'occ_pct', 'pers_pct', 'other_pct'):
            r[k+'_chg_bps'] = round(100*(r[k]-b[k]))
with open(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\D07_dsg_cost_lines.csv', 'w', newline='') as f:
    keys = sorted({k for r in out for k in r}, key=lambda k: list(out[-1].keys()).index(k) if k in out[-1] else 99)
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(out)
for r in out: print(r)
