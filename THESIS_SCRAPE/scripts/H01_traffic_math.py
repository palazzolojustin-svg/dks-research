"""H01: (1) compare PUBLIC Placer.ai 'DICK'S banner' visit prints (articles) with the Bloomberg ALTD Placer monthly
series (CORE_NOTES/C01_SYNTHESIS_A.md section 9d, estimated from chart); (2) re-weight the public DSG-banner series for
House of Sport boxes, which Placer tracks as a SEPARATE chain, under HoS visit multiples of 2x (DKS/Advan 2024),
3x (Placer 2022 Victor vs Rochester; DKS Corpus Christi 3.2x) and 4.3x (multiple implied by the BBG-public gap).
Writes raw/H01_placer_public_series.csv and prints the tables. Rerun: python H01_traffic_math.py
"""
import csv, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bbg = {  # Bloomberg ALTD Placer monthly y/y % (C01A 9d; Aug-26 disclosed, others chart-estimated +-0.2pp)
    '2025-01': -3.6, '2025-02': -13.3, '2025-03': -2.4, '2025-04': -5.9, '2025-05': -1.7, '2025-06': -9.4,
    '2025-07': -1.5, '2025-08': -1.5, '2025-09': -1.1, '2025-10': 11.6, '2025-11': 7.8, '2025-12': 1.5,
    '2026-01': 8.4, '2026-02': 10.5, '2026-03': -1.0, '2026-04': 7.2, '2026-05': 6.9, '2026-06': 7.9,
    '2026-07': 4.8, '2026-08': 1.14}
public = [  # (label, months, public Placer DICK'S-banner y/y %, source)
    ('Q1-25 (Jan-Mar)', ['2025-01', '2025-02', '2025-03'], -6.0, 'placer.ai 2025-11-25'),
    ('Feb-Jul-25 ("Q2 2025")', ['2025-02', '2025-03', '2025-04', '2025-05', '2025-06', '2025-07'], -5.3, 'placer.ai 2025-08-20'),
    ('Q3-25 (Jul-Sep)', ['2025-07', '2025-08', '2025-09'], -2.6, 'placer.ai 2025-11-25'),
    ('Oct-25', ['2025-10'], 2.2, 'placer.ai 2025-11-25'),
    ('Dec-25', ['2025-12'], -5.7, 'TheStreet/Yahoo 2026-03-10'),
    ('Feb-26 (assumed period of +0.2%)', ['2026-02'], 0.2, 'TheStreet/Yahoo 2026-03-10'),
    ('Q1-26 (Jan-Mar)', ['2026-01', '2026-02', '2026-03'], -3.1, 'placer.ai 2026-05-22'),
]
rows = []
print(f"{'period':34s} {'public':>7s} {'BBG':>7s} {'gap':>6s}")
for lab, ms, pub, src in public:
    b = sum(bbg[m] for m in ms) / len(ms)
    rows.append({'period': lab, 'public_placer_dsg_yoy': pub, 'bbg_placer_yoy_avg': round(b, 2), 'gap_pp': round(b - pub, 2), 'source': src})
    print(f"{lab:34s} {pub:7.1f} {b:7.1f} {b - pub:6.1f}")
with open(os.path.join(BASE, 'raw', 'H01_placer_public_series.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

# (2) HoS re-weighting for Q1-26 vs Q1-25. DSG-banner (incl. FH) store units: ~704 (677 DSG + 27 FH, FYE24)
# -> public per-location -1.6% vs visits -3.1% => ~1.5% fewer DSG-banner venues. HoS: 19 (FYE24) -> 35-36 (Q1-26).
P0 = 704.0
P1 = P0 * (1 - 0.031)
print('\nQ1-26 combined DSG-banner + HoS visit growth (avg DSG venue = 1 unit):')
for m in (2.0, 3.0, 4.3):
    H0, H1 = 19 * m, 35.5 * m
    g = (P1 + H1) / (P0 + H0) - 1
    print(f'  HoS multiple {m:.1f}x -> combined {g * 100:+.1f}% (public DSG-banner print -3.1%)')
# multiple implied if BBG (+6.0%) = DSG+HoS
m_impl = (1.06 * P0 - P1) / (35.5 - 1.06 * 19)
print(f'  multiple implied if BBG Q1-26 (+6.0%) = DSG+HoS only: {m_impl:.1f}x')
