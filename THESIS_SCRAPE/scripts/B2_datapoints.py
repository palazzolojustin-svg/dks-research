"""B2: write every dated foot-traffic datapoint used in B2 to raw/B2_traffic_datapoints.csv
(chain, period, metric, value, series_scope, source, published). Rerun: python B2_datapoints.py
"""
import csv, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IG = 'https://e.infogram.com/'
A = 'https://www.placer.ai/anchor/articles/'
rows = []


def add(chain, period, metric, value, scope, source, pub):
    rows.append(dict(chain=chain, period=period, metric=metric, value=value, series_scope=scope, source=source, published=pub))


# Placer public DICK'S banner (excludes HoS; includes Field House; excludes Foot Locker)
S1 = 'Placer DICK\'S banner: excl HoS, incl FH, excl FL'
for m, v, ss in [('2025-01', -3.1, -2.4), ('2025-02', -13.2, -12.5), ('2025-03', -1.9, -1.0), ('2025-04', -5.4, -4.8), ('2025-05', -1.2, -0.2),
                 ('2025-06', -8.8, -7.9), ('2025-07', -2.7, -1.5)]:
    add("DICK'S Sporting Goods", m, 'visits y/y %', v, S1, IG + '_/fDQhu6HQQ1Cy5AEyT17b ; ' + A + 'how-athletic-retailers-are-weathering-the-storm-in-q2-2025', '2025-08-20')
    add("DICK'S Sporting Goods", m, 'same-store visits y/y %', ss, S1, IG + '_/fDQhu6HQQ1Cy5AEyT17b', '2025-08-20')
for m, v in [('2025-01', -3.5), ('2025-02', -13.2), ('2025-03', -2.0), ('2025-04', -5.5), ('2025-05', -1.1), ('2025-06', -8.8), ('2025-07', -1.1),
             ('2025-08', -1.0), ('2025-09', -6.7), ('2025-10', 2.2), ('Q1 2025', -6.0), ('Q2 2025', -5.3), ('Q3 2025', -2.6)]:
    add("DICK'S Sporting Goods", m, 'visits y/y %', v, S1, IG + '_/fgLagdrwFEbQr7Hl4gJ8 ; ' + A + 'dicks-sporting-good-riding-positive-visit-trend-into-the-holidays', '2025-11-25')
for m, v in [('2025-01', -3.4), ('2025-02', -13.3), ('2025-03', -2.0), ('2025-04', -5.4)]:
    add("DICK'S Sporting Goods", m, 'visits y/y %', v, S1, IG + '_/CA2CvBRpLVaGxLt0qRbP ; ' + A + 'lululemon-and-dicks-scoring-big-with-celebs-and-events', '2025-05-27')
add("DICK'S Sporting Goods", 'Jan-Apr 2025', 'visits y/y % / visits per location y/y %', '-5.9 / -4.8', S1, IG + '_/CA2CvBRpLVaGxLt0qRbP', '2025-05-27')
for m, v, ss in [('2025-10', 1.9, 2.7), ('2025-11', -0.1, 1.2), ('2025-12', -5.7, -4.6), ('2026-01', 0.2, 1.2)]:
    add("DICK'S Sporting Goods", m, 'visits y/y % | same-store y/y %', f'{v} | {ss}', S1, IG + '_/W03pxhtveBba8vlclkzC ; ' + A + 'momentum-builds-in-athletic-apparel-sporting-goods-dicks-academy-sports-outdoors-and-lululemon', '2026-02-27')
for m, v, ss in [('2026-01', -0.5, 0.9), ('2026-02', 1.6, 2.9), ('2026-03', -8.3, -7.5), ('2026-04', -1.2, -0.4)]:
    add("DICK'S Sporting Goods", m, 'visits y/y % | same-store y/y %', f'{v} | {ss}', S1, IG + '_/72A31xFGvsqPoRdDQY0U ; ' + A + 'traffic-softens-but-growth-levers-remain-for-dicks-gap-and-lululemon', '2026-05-22')
add("DICK'S Sporting Goods", 'Q1 2026', 'visits y/y % / per location y/y %', '-3.1 / -1.6', S1, A + 'traffic-softens-but-growth-levers-remain-for-dicks-gap-and-lululemon', '2026-05-22')
# Saturdays Q1 2025
for d, v in [('2025-01-04', -6.0), ('2025-01-11', -18.6), ('2025-01-18', -12.1), ('2025-01-25', -14.9), ('2025-02-01', -9.6), ('2025-02-08', -9.7),
             ('2025-02-15', -12.4), ('2025-02-22', 0.6), ('2025-03-01', 21.4), ('2025-03-08', 22.6), ('2025-03-15', 16.6), ('2025-03-22', 14.0), ('2025-03-29', 8.0)]:
    add("DICK'S Sporting Goods", d, 'Saturday visits y/y %', v, S1, IG + '_/K966RcNrNlq0G1kW7Dzf', '2025-05-27')
# per-location DSG vs HoS
dsg = [20.4, 19.9, 25.3, 22.44, 20.57, 24.81, 26.51, 30.83, 20.21, 17.91, 21.06, 36.37, 17.61, 18.7]
hos = [55.91, 35.71, 44.6, 40.37, 39.56, 42.39, 86.13, 127.88, 77.12, 59.75, 70.64, 115.94, 55.62, 64.6]
ms = [f'2023-{i:02d}' for i in range(1, 13)] + ['2024-01', '2024-02']
for m, a, b in zip(ms, dsg, hos):
    add("DICK'S Sporting Goods Nationwide", m, 'visits per location (K/month)', a, 'Placer chain avg per venue', IG + '_/ysbLGF3VT5cno7apHXf7 ; ' + A + 'dicks-sporting-goods-new-store-formats-driving-visit-outperformance', '2024-03-15')
    add("DICK'S House of Sport Nationwide", m, 'visits per location (K/month)', b, 'Placer HoS chain avg per venue', IG + '_/ysbLGF3VT5cno7apHXf7', '2024-03-15')
    add('HoS / DSG', m, 'per-location visit multiple (x)', round(b / a, 2), 'derived', IG + '_/ysbLGF3VT5cno7apHXf7', '2024-03-15')
for q, v in [('Q1 2024', -2.5), ('Q2 2024', -1.7), ('Q3 2024', -4.4), ('Q4 2024', -6.6)]:
    add("DICK'S Sporting Goods", q, 'visits y/y %', v, S1, IG + '_/CAHrHQCUwxBwRH5xcAq3', '2025-01')
# Academy
for m, v, ss in [('2025-01', -2.1, -5.3), ('2025-02', -8.5, -11.5), ('2025-03', -2.4, -6.7), ('2025-04', 0.0, -4.0), ('2025-05', 1.8, -2.6), ('2025-06', -3.9, -8.0), ('2025-07', 0.9, -3.4)]:
    add('Academy Sports + Outdoors', m, 'visits y/y % | same-store y/y %', f'{v} | {ss}', 'Placer ASO chain', IG + '_/c8Bk97xBAY2JKxHgDYhH', '2025-08-20')
for m, v, ss in [('2025-10', 5.9, 0.5), ('2025-11', 1.6, -3.7), ('2025-12', -1.9, -6.6), ('2026-01', -0.4, -5.2)]:
    add('Academy Sports + Outdoors', m, 'visits y/y % | same-store y/y %', f'{v} | {ss}', 'Placer ASO chain', IG + '_/UDqeDsHTu3DGvTtYfgPr', '2026-02-27')
# Mall index open-air / indoor
oa = {'2025-01': 2.0, '2025-02': -4.5, '2025-03': -2.5, '2025-04': 2.1, '2025-05': 4.4, '2025-06': -1.9, '2025-07': 0.4, '2025-08': 0.4, '2025-09': -0.4,
      '2025-10': 2.6, '2025-11': 1.7, '2025-12': 0.8, '2026-01': 5.3, '2026-02': 6.8, '2026-03': 2.9, '2026-04': 3.3, '2026-05': 5.5, '2026-08': 6.6, '2026-09': 5.6}
for m, v in oa.items():
    add('Placer Mall Index: open-air centers', m, 'visits y/y %', v, '100 top-tier open-air centers',
        'Infogram _/XWgH1iXqcJJ9SZfQKCAk, _/io74KSlJLP77BzZPFJWy, _/aV8Vud5xymH3yb1tQ3Dx, _/Rh3AFf3vN4hGYNqWcjok; Aug/Sep-26 article text', '2026')
# FL vs DKS demographics
add('Foot Locker (All Banners) vs DICK\'S (All Banners)', '2025 (pre-deal)', 'trade-area median HHI', '$62.3K vs $87.4K', 'Placer', IG + '_/7HdtWsq1QDuGEx5Zi62D', '2025-06-04')
# Bloomberg ALTD Placer (folder) for completeness
bbg = {'2025-01': -3.6, '2025-02': -13.3, '2025-03': -2.4, '2025-04': -5.9, '2025-05': -1.7, '2025-06': -9.4, '2025-07': -1.5, '2025-08': -1.5, '2025-09': -1.1,
       '2025-10': 11.6, '2025-11': 7.8, '2025-12': 1.5, '2026-01': 8.4, '2026-02': 10.5, '2026-03': -1.0, '2026-04': 7.2, '2026-05': 6.9, '2026-06': 7.9,
       '2026-07': 4.8, '2026-08': 1.14}
for m, v in bbg.items():
    add('Bloomberg ALTD Placer DKS ticker', m, 'visits y/y %', v, 'BBG ticker: = DSG banner pre-deal; +7-10pp add-on (partial FL or HoS) from w/e 21-Sep-25 to lap',
        'CORE_NOTES/C01_SYNTHESIS_A.md sec 9d (digitized except Aug-26)', '2026-10-04')
with open(os.path.join(BASE, 'raw', 'B2_traffic_datapoints.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows), 'rows')
