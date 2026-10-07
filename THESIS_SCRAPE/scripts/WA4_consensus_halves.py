"""WA4: half-year decomposition of Bloomberg DICK'S-segment consensus (thesis #2 timing test).
Rerun: python THESIS_SCRAPE\\scripts\\WA4_consensus_halves.py  -> prints table, writes raw\\WA4_consensus_halves.csv
Inputs (hard-coded, with sources):
  Actuals: 8-K Ex 99.1 segment tables (WORKING_NOTES\\W05_DKS_8K_PRESSRELEASES_C.md): Q3FY25 rev 3,236.860 / OI 288.571 / GP 1,166.573;
           Q4FY25 4,050.789 / 444.511 / 1,443.369; Q1FY26 3,377.440 / 360.975 / 1,227.321; Q2FY26 3,849.887 / 485.204 / 1,457.029.
  Consensus (BBG, CORE_NOTES\\C05 l.214-218; digest 7b): DSG rev Q3FY26E 3,436.61, Q4 4,144.38, Q1FY27E 3,478.03, Q2FY27E 4,102.66;
           OI 246.40 / 457.16 / 370.13 / 482.51; GP 1,170.21 / 1,464.47 / 1,261.52 / 1,487.45;
           separately-averaged margin rows: OM 7.17 / 10.58 / 10.07 / 11.69 %, GM 35.42 / 35.42 / 36.26 / 37.51 % (different contributor sets).
           FY27E DSG rev 15,202.95, OI 1,647.17 (digest 7a). FY25 actual DSG 14,108.943 / 1,568.443.
"""
import csv, os
A = {'Q3FY25': (3236.860, 288.571, 1166.573), 'Q4FY25': (4050.789, 444.511, 1443.369),
     'Q1FY26': (3377.440, 360.975, 1227.321), 'Q2FY26': (3849.887, 485.204, 1457.029),
     'Q1FY25': (3174.677, 360.408, 1165.086), 'Q2FY25': (3646.616, 474.952, 1351.272)}
C = {'Q3FY26E': (3436.61, 246.40, 1170.21, 7.17, 35.42), 'Q4FY26E': (4144.38, 457.16, 1464.47, 10.58, 35.42),
     'Q1FY27E': (3478.03, 370.13, 1261.52, 10.07, 36.26), 'Q2FY27E': (4102.66, 482.51, 1487.45, 11.69, 37.51)}
def half(keys, src):
    r = sum(src[k][0] for k in keys); o = sum(src[k][1] for k in keys); g = sum(src[k][2] for k in keys)
    return r, o, g
rows = []
def add(name, r, o, g, om_alt=None):
    rows.append(dict(period=name, rev=round(r, 1), oi=round(o, 1), om=round(o / r * 100, 2), gm=round(g / r * 100, 2),
                     opex_pct=round((g - o) / r * 100, 2), om_marginrow=om_alt))
r, o, g = half(['Q1FY25', 'Q2FY25'], A); add('1H FY25 A', r, o, g)
r, o, g = half(['Q3FY25', 'Q4FY25'], A); add('2H FY25 A', r, o, g)
r, o, g = half(['Q1FY26', 'Q2FY26'], A); add('1H FY26 A', r, o, g)
r, o, g = half(['Q3FY26E', 'Q4FY26E'], C)
omr = round((C['Q3FY26E'][3] * C['Q3FY26E'][0] + C['Q4FY26E'][3] * C['Q4FY26E'][0]) / r, 2); add('2H FY26 E', r, o, g, omr)
r1, o1, g1 = half(['Q1FY27E', 'Q2FY27E'], C)
omr = round((C['Q1FY27E'][3] * C['Q1FY27E'][0] + C['Q2FY27E'][3] * C['Q2FY27E'][0]) / r1, 2); add('1H FY27 E', r1, o1, g1, omr)
FYr, FYo = 15202.95, 1647.17
rows.append(dict(period='2H FY27 E (FY27E - 1H27E)', rev=round(FYr - r1, 1), oi=round(FYo - o1, 1), om=round((FYo - o1) / (FYr - r1) * 100, 2)))
rows.append(dict(period='FY27 E', rev=FYr, oi=FYo, om=round(FYo / FYr * 100, 2)))
rows.append(dict(period='FY25 A', rev=14108.9, oi=1568.4, om=round(1568.443 / 14108.943 * 100, 2)))
out = os.path.join(os.path.dirname(__file__), '..', 'raw', 'WA4_consensus_halves.csv')
with open(out, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['period', 'rev', 'oi', 'om', 'gm', 'opex_pct', 'om_marginrow']); w.writeheader(); w.writerows(rows)
for x in rows: print(x)
# variance: 1H FY27 at flat y/y margin
b = rows[2]['om']
for lab, om27 in [('OI/rev', rows[4]['om']), ('margin rows', rows[4]['om_marginrow'])]:
    d = (b - om27) / 100 * r1
    print(f'1H FY27E flat-margin variance using {lab}: {(b-om27)*100:.0f}bp ->> ${d:.1f}M pre-tax = ${d*0.00814:.2f}/sh')
