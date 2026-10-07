"""WA6: split DICK'S-segment 'other segment expenses' (CODM table) into
   (a) COGS-side other  = (segment sales - segment GP) - cost of merch & services - occupancy
                          -> shipping, e-com fulfilment, freight/distribution/supply chain (incl. Fort Worth DC), i.e. GAAP COGS items
   (b) pre-opening      = DICK'S pre-opening (in other segment expenses per Q3 FY25 10-Q segment note)
   (c) SG&A-side other  = other - (a) - (b) -> advertising, bank card, tech, e-com platform, other store, CSC non-wage
   and compare with personnel (store + administrative + field + GameChanger wages/comp, per 10-K/10-Q definitions).
Also: personnel $ per DICK'S Business store and per sq ft (end-of-period store tables), quarterly y/y.

Inputs ($000) transcribed from WORKING_NOTES\\W04 (10-Q segment notes + segment MD&A GP), W01 (10-K FY25 segment table,
FY24/FY25 pre-opening), W03-derived FY24 quarters as used by D07 (scripts\\D07_dsg_cost_lines.py).
DICK'S pre-opening: FY24 quarters and Q1-Q2 FY25 = consolidated (single segment); Q3 FY25 = Q3 FY24 16,779 + 13.1M (10-Q:
"Pre-opening expenses increased $13.1 million"); Q4 FY25 = FY25 DSG (57,492 + 9.8M per 10-K) - 39w DSG (46,806 + 8.9M);
Q2 FY26 = 12,322 + 10.3M; Q1 FY26 = (25,763 + 10.9M) - Q2 FY26.  (DSG increments are management-rounded -> +/-0.05M.)
Caveat: Q1/Q2 FY24 'other' were reported before the FY25 recast that moved deferred-comp FV changes / M&I to Corporate & other
-> FY24 Q1-Q2 SG&A-side other is not exactly like-for-like (Q2 FY24 reconciles exactly to GAAP SG&A, so recast effect there ~0).
Rerun: python THESIS_SCRAPE\\scripts\\WA6_dsg_cost_split.py -> THESIS_SCRAPE\\raw\\WA6_dsg_cost_split.csv
"""
import csv

# qtr: sales, GP (DICK'S), merch&services, occupancy, personnel, other, pre-opening(DSG), stores_end, sqft_end(M)
R = {
 'Q1FY24': (3018383, 1095293, 1501409, 273739, 442257, 470179, 21095, None, None),
 'Q2FY24': (3473635, 1275700, 1755464, 283159, 456558, 508358, 8931, None, None),
 'Q3FY24': (3057181, 1093444, 1525800, 289477, 456822, 495562, 16779, None, None),
 'Q4FY24': (13442849-9549200, 4825696-3464438, 6813682-1501409-1755464-1525800, 1139387-273739-283159-289477,
            1869257-1355637, 2122954-1459954, 57492-46806, 885, 44.8),
 'Q1FY25': (3174677, 1165086, 1567248, 289836, 455238, 501947, 13442, 885, 45.0),
 'Q2FY25': (3646616, 1351272, 1836326, 294245, 486648, 554445, 12322, 889, 45.1),
 'Q3FY25': (3236860, 1166573, 1613894, 303280, 485490, 545625, 16779+13100, 891, 45.7),
 'Q4FY25': (14108943-10058153, 5126299-3682930, 7100929-5017467, 1197019-887361, 1972850-1427377, 2269702-1602016,
            (57492+9800)-(46806+8900), 888, 45.5),
 'Q1FY26': (3377440, 1227321, 1677274, 307735, 499482, 531974, (25763+10900)-(12322+10300), 888, 45.6),
 'Q2FY26': (3849887, 1457029, 1885917, 318130, 530387, 630249, 12322+10300, 892, 46.0),
}
order = list(R)
out = {}
for q in order:
    s, gp, m, o, p, x, pre, st, sf = R[q]
    cogs_other = (s - gp) - m - o
    sga_other = x - cogs_other - pre
    d = dict(qtr=q, sales=s, merch_pct=100*m/s, occ_pct=100*o/s, cogs_other=cogs_other, cogs_other_pct=100*cogs_other/s,
             preopen=pre, preopen_pct=100*pre/s, sga_other=sga_other, sga_other_pct=100*sga_other/s,
             personnel=p, pers_pct=100*p/s, seg_margin=100*(s-m-o-p-x)/s, stores=st, sqft=sf)
    out[q] = d

def prev(q):
    return q[:2] + 'FY' + str(int(q[4:]) - 1)

def prevq(q):
    i = order.index(q)
    return order[i-1] if i > 0 else None

rows = []
for q in order:
    d = out[q]; py = prev(q)
    if py in out:
        b = out[py]
        for k in ('merch_pct', 'occ_pct', 'cogs_other_pct', 'preopen_pct', 'sga_other_pct', 'pers_pct', 'seg_margin'):
            d[k.replace('_pct', '') + '_bps_yoy'] = round(100*(d[k]-b[k]))
        d['sales_yoy'] = round(100*(d['sales']/b['sales']-1), 2)
        d['cogs_other_yoy'] = round(100*(d['cogs_other']/b['cogs_other']-1), 1)
        d['sga_other_yoy'] = round(100*(d['sga_other']/b['sga_other']-1), 1)
        d['pers_yoy'] = round(100*(d['personnel']/b['personnel']-1), 1)
        # $ excess vs growing at sales growth
        g = d['sales']/b['sales']
        d['cogs_other_excess_$k'] = round(d['cogs_other'] - b['cogs_other']*g)
        d['sga_other_excess_$k'] = round(d['sga_other'] - b['sga_other']*g)
        d['pers_excess_$k'] = round(d['personnel'] - b['personnel']*g)
        if d['stores'] and b['stores']:
            pq = prevq(q); ppq = prevq(py)
            # average of begin/end of quarter where available
            def avg(qq, pqq, key):
                a = out[qq][key]; c = out[pqq][key] if pqq and out[pqq][key] else a
                return (a + c) / 2
            if pq and out[pq]['stores'] and ppq and out[ppq]['stores']:
                d['pers_per_store_yoy'] = round(100*((d['personnel']/avg(q, pq, 'stores'))/(b['personnel']/avg(py, ppq, 'stores'))-1), 1)
                d['pers_per_sqft_yoy'] = round(100*((d['personnel']/avg(q, pq, 'sqft'))/(b['personnel']/avg(py, ppq, 'sqft'))-1), 1)
                d['sales_per_sqft_yoy'] = round(100*((d['sales']/avg(q, pq, 'sqft'))/(b['sales']/avg(py, ppq, 'sqft'))-1), 1)
    rows.append(d)

# half-year 1H FY26 vs 1H FY25
def half(qs):
    tot = {k: sum(out[q][k] for q in qs) for k in ('sales', 'cogs_other', 'preopen', 'sga_other', 'personnel')}
    m = sum(R[q][2] for q in qs); o = sum(R[q][3] for q in qs); x = sum(R[q][5] for q in qs)
    tot['merch'] = m; tot['occ'] = o
    tot['margin'] = 100*(tot['sales']-m-o-tot['personnel']-x)/tot['sales']
    return tot
h26, h25 = half(['Q1FY26', 'Q2FY26']), half(['Q1FY25', 'Q2FY25'])
print('1H FY26 vs 1H FY25 (bps of DICK\'S sales):')
for k in ('merch', 'occ', 'cogs_other', 'preopen', 'sga_other', 'personnel'):
    print(f"  {k:11s} {100*h26[k]/h26['sales']:6.2f}% vs {100*h25[k]/h25['sales']:6.2f}%  {round(10000*(h26[k]/h26['sales']-h25[k]/h25['sales'])):+d}bp")
print(f"  seg margin {h26['margin']:.2f}% vs {h25['margin']:.2f}%  {round(100*(h26['margin']-h25['margin'])):+d}bp")

keys = []
for r in rows:
    for k in r:
        if k not in keys:
            keys.append(k)
with open(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\WA6_dsg_cost_split.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader()
    for r in rows:
        w.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
for r in rows:
    print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()
           if k in ('qtr', 'sales_yoy', 'cogs_other_pct', 'cogs_other_bps_yoy', 'preopen_bps_yoy', 'sga_other_pct',
                    'sga_other_bps_yoy', 'pers_bps_yoy', 'seg_margin', 'seg_margin_bps_yoy', 'cogs_other_excess_$k',
                    'sga_other_excess_$k', 'pers_excess_$k', 'pers_yoy', 'sga_other_yoy', 'cogs_other_yoy',
                    'pers_per_store_yoy', 'pers_per_sqft_yoy', 'sales_per_sqft_yoy')})
