"""F6: DICK'S-segment cost ratios by quarter (10-Q / 10-K segment notes) + landlord construction allowances.

Rerun: python THESIS_SCRAPE\\scripts\\F6_segment_cost_ratios.py
Inputs are hard-coded from WORKING_NOTES\\W04_DKS_10Q_FY25Q1-FY26Q2.md (10-Q segment notes, latest comparatives)
and WORKING_NOTES\\W01_DKS_10K_FY2024-FY2025.md (10-K FY25 Note 17; cash-flow construction allowances),
WORKING_NOTES\\W05_DKS_8K_PRESSRELEASES_A/B/C.md (press-release cash flows). $000.
Writes THESIS_SCRAPE\\raw\\F6_dks_segment_cost_ratios.csv and F6_construction_allowances.csv
"""
import csv, os

OUT = os.path.join(os.path.dirname(__file__), '..', 'raw')
os.makedirs(OUT, exist_ok=True)

# sales, merch cost, occupancy, personnel, other (DICK'S segment)
q = {
 'Q1FY24': (3018383, 1501409, 273739, 442257, None),
 'Q2FY24': (3473635, 1755464, 283159, 456558, 508358),
 'Q3FY24': (3057181, 1525800, 289477, 456822, 495562),
 'Q1FY25': (3174677, 1567248, 289836, 455238, 501947),
 'Q2FY25': (3646616, 1836326, 294245, 486648, 554445),
 'Q3FY25': (3236860, 1613894, 303280, 485490, 545625),
 'Q1FY26': (3377440, 1677274, 307735, 499482, 531974),
 'Q2FY26': (3849887, 1885917, 318130, 530387, 630249),
}
FY = {'FY24': (13442849, 6813682, 1139387, 1869257, 2122954),
      'FY25': (14108943, 7100929, 1197019, 1972850, 2269702)}
n39 = {'FY24': (9549200, 4782672, 846375, 1355637, 1459954),
       'FY25': (10058153, 5017467, 887361, 1427377, 1602016)}
for y, nq in (('FY24', 'Q4FY24'), ('FY25', 'Q4FY25')):
    q[nq] = tuple(a - b for a, b in zip(FY[y], n39[y]))

order = ['Q1FY24','Q2FY24','Q3FY24','Q4FY24','Q1FY25','Q2FY25','Q3FY25','Q4FY25','Q1FY26','Q2FY26']
rows = []
for k in order:
    s, m, o, p, ot = q[k]
    rows.append({'qtr': k, 'sales': s, 'occ_pct': round(100*o/s, 2), 'pers_pct': round(100*p/s, 2),
                 'other_pct': round(100*ot/s, 2) if ot else '', 'merch_cost_pct': round(100*m/s, 2),
                 'occ_yoy_pct': '', 'pers_yoy_pct': '', 'sales_yoy_pct': ''})
idx = {r['qtr']: r for r in rows}
for k in order:
    prev = k[:2] + 'FY' + str(int(k[-2:]) - 1)
    if prev in q:
        s, m, o, p, ot = q[k]; s0, m0, o0, p0, ot0 = q[prev]
        idx[k]['sales_yoy_pct'] = round(100*(s/s0-1), 1)
        idx[k]['occ_yoy_pct'] = round(100*(o/o0-1), 1)
        idx[k]['pers_yoy_pct'] = round(100*(p/p0-1), 1)
        idx[k]['pers_bps_chg'] = round(10000*(p/s - p0/s0))
        idx[k]['occ_bps_chg'] = round(10000*(o/s - o0/s0))
with open(os.path.join(OUT, 'F6_dks_segment_cost_ratios.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) + ['pers_bps_chg', 'occ_bps_chg'])
    w.writeheader(); [w.writerow(r) for r in rows]
for r in rows: print(r)

# landlord construction allowances (CFO) and gross capex ($000)
allow = {'FY23': 67061, 'FY24': 76287, 'FY25': 161659,
         '1H FY24': 46556, '1H FY25': 70583, '1H FY26': 129263,
         'Q1FY25': 22776, 'Q2FY25': 70583-22776, 'Q3FY25': 119495-70583, 'Q4FY25': 161659-119495,
         'Q1FY26': 71723, 'Q2FY26': 129263-71723}
capex = {'FY24': 802565, 'FY25': 1137176, '1H FY24': 372105, '1H FY25': 526076, '1H FY26': 743470}
with open(os.path.join(OUT, 'F6_construction_allowances.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['period', 'allowances_000', 'gross_capex_000', 'allow_pct_gross_capex'])
    for k, v in allow.items():
        c = capex.get(k); w.writerow([k, v, c or '', round(100*v/c, 1) if c else ''])
        print(k, v, c, round(100*v/c, 1) if c else '')
