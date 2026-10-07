"""B2: DICK'S-business traffic reconciliation (DSG banner + House of Sport; Foot Locker excluded).
Inputs (all hard-coded with sources):
  * PUBLIC Placer DICK'S-banner monthly y/y (visits, same-store visits) recovered from the Infogram data behind
    Placer Anchor charts (scripts/B2_infogram.py; raw/B2_infogram/*.json).
  * Bloomberg ALTD Placer DKS monthly y/y (CORE_NOTES/C01_SYNTHESIS_A.md sec 9d; Aug-26 disclosed, others digitized +-0.2pp)
    and weekly (sec 9e).
  * Placer per-location visits DSG vs HoS (Infogram _/ysbLGF3VT5cno7apHXf7) -> HoS/DSG per-location multiple and
    DSG monthly seasonality (used as weights).
  * Store counts: Bloomberg DKS segment store table (C01A line ~2604-2607 / C05 line 183): DSG, FH, HoS by quarter.
Outputs: raw/B2_traffic_recon_monthly.csv, raw/B2_traffic_recon_quarterly.csv; prints tables.
Rerun: python B2_traffic_recon.py
"""
import csv, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, 'raw')

# ---------- public Placer DICK'S banner (chain excludes HoS; includes Field House) ----------
# (visits y/y %, same-store visits y/y %), latest vintage preferred
pub = {
    '2025-01': (-3.1, -2.4), '2025-02': (-13.2, -12.5), '2025-03': (-1.9, -1.0), '2025-04': (-5.4, -4.8),
    '2025-05': (-1.2, -0.2), '2025-06': (-8.8, -7.9), '2025-07': (-2.7, -1.5),          # _/fDQhu6HQQ1Cy5AEyT17b (2025-08-20)
    '2025-08': (-1.0, None), '2025-09': (-6.7, None),                                   # _/fgLagdrwFEbQr7Hl4gJ8 (2025-11-25)
    '2025-10': (1.9, 2.7), '2025-11': (-0.1, 1.2), '2025-12': (-5.7, -4.6),             # _/W03pxhtveBba8vlclkzC (2026-02-27)
    '2026-01': (-0.5, 0.9), '2026-02': (1.6, 2.9), '2026-03': (-8.3, -7.5), '2026-04': (-1.2, -0.4),  # _/72A31xFGvsqPoRdDQY0U (2026-05-22)
}
# Bloomberg ALTD Placer DKS monthly y/y (C01A 9d)
bbg = {'2024-01': -8.7, '2024-02': 0.0, '2024-03': 1.9, '2024-04': -7.9, '2024-05': 1.3, '2024-06': 3.0, '2024-07': -6.0,
       '2024-08': 1.4, '2024-09': -8.6, '2024-10': -9.5, '2024-11': -4.2, '2024-12': -7.6,
       '2025-01': -3.6, '2025-02': -13.3, '2025-03': -2.4, '2025-04': -5.9, '2025-05': -1.7, '2025-06': -9.4,
       '2025-07': -1.5, '2025-08': -1.5, '2025-09': -1.1, '2025-10': 11.6, '2025-11': 7.8, '2025-12': 1.5,
       '2026-01': 8.4, '2026-02': 10.5, '2026-03': -1.0, '2026-04': 7.2, '2026-05': 6.9, '2026-06': 7.9,
       '2026-07': 4.8, '2026-08': 1.14}
# Placer per-location monthly visits (K) 2023: DSG nationwide / HoS nationwide (Infogram _/ysbLGF3VT5cno7apHXf7)
dsg_pl_2023 = [20.4, 19.9, 25.3, 22.44, 20.57, 24.81, 26.51, 30.83, 20.21, 17.91, 21.06, 36.37]
hos_pl_2023 = [55.91, 35.71, 44.6, 40.37, 39.56, 42.39, 86.13, 127.88, 77.12, 59.75, 70.64, 115.94]
season = {f'{m:02d}': v for m, v in zip(range(1, 13), dsg_pl_2023)}

# ---------- store counts (end of month, interpolated from fiscal-quarter ends; see notes) ----------
# HoS: FYE23 (3-Feb-24) 12; Q3FY24 (2-Nov-24) 19; FYE24 19; Q1FY25 21; Q2FY25 22; Q3FY25 35; Q4FY25 35; Q1FY26 36; Q2FY26 41;
# BBG cons Q3FY26E 47. Monthly path = assumption (Q3 openings weighted to Sep-Oct as in 2025, e.g. Jersey City 9/18/25).
hos = {'2024-01': 12, '2024-02': 12, '2024-03': 12, '2024-04': 13, '2024-05': 13, '2024-06': 14, '2024-07': 14, '2024-08': 14,
       '2024-09': 16, '2024-10': 19, '2024-11': 19, '2024-12': 19,
       '2025-01': 19, '2025-02': 19, '2025-03': 20, '2025-04': 21, '2025-05': 21, '2025-06': 22, '2025-07': 22,
       '2025-08': 23, '2025-09': 28, '2025-10': 35, '2025-11': 35, '2025-12': 35,
       '2026-01': 35, '2026-02': 35, '2026-03': 36, '2026-04': 36, '2026-05': 37, '2026-06': 39, '2026-07': 41,
       '2026-08': 41, '2026-09': 44, '2026-10': 47}
# DSG-banner locations (DICK'S + Field House) at quarter ends: FYE24 703 (677+26); Q1FY25 701; Q2FY25 700; Q3FY25 690; Q4FY25 686;
# Q1FY26 684; Q2FY26 682.  FY24 approximations ~712 (pre-HoS-relocation wave).
# Placer's own location counts differ from the 10-K table: Placer per-location prints imply DSG-banner venues -1.2% y/y in
# Jan-Apr 2025 (visits -5.9 vs per-location -4.8) and -1.5% in Q1-2026 (-3.1 vs -1.6). Counts below are scaled to match those ratios.
dsg = {'2024-01': 714, '2024-02': 714, '2024-03': 714, '2024-04': 713, '2024-05': 713, '2024-06': 712, '2024-07': 712, '2024-08': 712,
       '2024-09': 711, '2024-10': 709, '2024-11': 707, '2024-12': 706,
       '2025-01': 705, '2025-02': 705, '2025-03': 705, '2025-04': 705, '2025-05': 704, '2025-06': 704, '2025-07': 703,
       '2025-08': 703, '2025-09': 700, '2025-10': 696, '2025-11': 695, '2025-12': 695,
       '2026-01': 694, '2026-02': 694, '2026-03': 694, '2026-04': 693, '2026-05': 693, '2026-06': 692, '2026-07': 691,
       '2026-08': 691, '2026-09': 690, '2026-10': 689}


def prev(m):
    y, mo = int(m[:4]), int(m[5:])
    return f'{y-1}-{mo:02d}'


def combined(m, g_d, mult):
    """combined DSG+HoS visit y/y given DSG-banner y/y g_d (%). HoS per-location visits = mult x DSG per-location
    in the same month (so HoS same-store tracks DSG per-location trend)."""
    p = prev(m)
    nd0, nd1, nh0, nh1 = dsg[p], dsg[m], hos[p], hos[m]
    vpl = (1 + g_d / 100) / (nd1 / nd0)               # DSG per-location visit ratio t / t-1
    d0 = nd0 * 1.0; d1 = nd1 * vpl                     # in units of 'avg DSG store-month at t-1'
    h0 = nh0 * mult; h1 = nh1 * mult * vpl
    return ((d1 + h1) / (d0 + h0) - 1) * 100, (vpl - 1) * 100


rows = []
print('month   | pubDSG  SSDSG | BBG   gap  | DSG/loc | comb m2.0 m2.5 m3.3 | HoS share(m3.3)')
months = sorted(set(list(pub.keys()) + [k for k in bbg if k >= '2025-01']))
# calibration of the post-deal BBG step: k = gap/(1+g) on Oct-25..Apr-26
ks = []
for m in months:
    if '2025-10' <= m <= '2026-04' and m in pub:
        ks.append((bbg[m] - pub[m][0]) / (1 + pub[m][0] / 100))
k_mean = sum(ks) / len(ks)
k_lo, k_hi = min(ks), max(ks)
for m in months:
    src = 'public'
    if m in pub:
        g = pub[m][0]
        ss = pub[m][1]
    else:
        # estimate DSG banner from BBG minus calibrated step (pre-lap months only)
        g = ((1 + bbg[m] / 100) - k_mean / 100) * 100 - 100
        g = (bbg[m] - k_mean) / (1 + k_mean / 100)
        ss = None
        src = 'BBG-k'
    c2, vpl = combined(m, g, 2.0)
    c25, _ = combined(m, g, 2.5)
    c33, _ = combined(m, g, 3.3)
    share = hos[m] * 3.3 / (hos[m] * 3.3 + dsg[m])
    gap = bbg[m] - pub[m][0] if m in pub and m in bbg else None
    rows.append({'month': m, 'src_dsg': src, 'dsg_banner_yoy': round(g, 2), 'dsg_same_store_yoy': ss, 'bbg_placer_yoy': bbg.get(m),
                 'bbg_minus_public': None if gap is None else round(gap, 2), 'dsg_per_location_yoy': round(vpl, 2),
                 'hos_count': hos[m], 'hos_count_ly': hos[prev(m)], 'dsg_locations': dsg[m],
                 'combined_m2.0': round(c2, 2), 'combined_m2.5': round(c25, 2), 'combined_m3.3': round(c33, 2),
                 'hos_visit_share_m3.3': round(share * 100, 1)})
    print(f"{m} | {g:6.1f} {'' if ss is None else ss:>6} | {bbg.get(m, float('nan')):5.1f} {'' if gap is None else round(gap,1):>5} | {vpl:6.1f} | {c2:6.1f} {c25:6.1f} {c33:6.1f} | {share*100:4.1f}% [{src}]")
print(f'\nBBG post-deal step k (Oct-25..Apr-26) mean {k_mean:.2f}pp, range {k_lo:.2f}-{k_hi:.2f}')

with open(os.path.join(RAW, 'B2_traffic_recon_monthly.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

# ---------- fiscal quarters (DKS FY: Q1 Feb-Apr, Q2 May-Jul, Q3 Aug-Oct, Q4 Nov-Jan), visit-weighted by DSG seasonality ----------
fq = {'Q1FY25': ['2025-02', '2025-03', '2025-04'], 'Q2FY25': ['2025-05', '2025-06', '2025-07'], 'Q3FY25': ['2025-08', '2025-09', '2025-10'],
      'Q4FY25': ['2025-11', '2025-12', '2026-01'], 'Q1FY26': ['2026-02', '2026-03', '2026-04'], 'Q2FY26': ['2026-05', '2026-06', '2026-07'],
      'Q3FY26 QTD(Aug)': ['2026-08']}
comp = {'Q1FY25': 4.5, 'Q2FY25': 5.0, 'Q3FY25': 5.7, 'Q4FY25': 3.1, 'Q1FY26': 6.0, 'Q2FY26': 4.9, 'Q3FY26 QTD(Aug)': None}
R = {r['month']: r for r in rows}
qrows = []
print('\nquarter | comp | DSG banner | DSG SS | comb m2.0 | m3.3 | comp-gap vs DSG banner | vs comb m2.0 | vs comb m3.3')
for q, ms in fq.items():
    wts = [season[m[5:]] for m in ms]
    def wavg(key):
        vals = [R[m][key] for m in ms]
        if any(v is None for v in vals):
            return None
        return sum(v * w for v, w in zip(vals, wts)) / sum(wts)
    d, s, c2, c3 = wavg('dsg_banner_yoy'), wavg('dsg_same_store_yoy'), wavg('combined_m2.0'), wavg('combined_m3.3')
    cp = comp[q]
    qrows.append({'quarter': q, 'core_comp': cp, 'dsg_banner_visits': round(d, 2), 'dsg_same_store_visits': None if s is None else round(s, 2),
                  'combined_m2.0': round(c2, 2), 'combined_m3.3': round(c3, 2),
                  'comp_minus_dsg': None if cp is None else round(cp - d, 2),
                  'comp_minus_comb2': None if cp is None else round(cp - c2, 2), 'comp_minus_comb33': None if cp is None else round(cp - c3, 2),
                  'dsg_source': ','.join(sorted(set(R[m]['src_dsg'] for m in ms)))})
    print(f"{q:16s} | {cp} | {d:6.1f} | {'' if s is None else round(s,1):>5} | {c2:6.1f} | {c3:6.1f} | "
          f"{'' if cp is None else round(cp-d,1)} | {'' if cp is None else round(cp-c2,1)} | {'' if cp is None else round(cp-c3,1)}  [{qrows[-1]['dsg_source']}]")
with open(os.path.join(RAW, 'B2_traffic_recon_quarterly.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(qrows[0].keys())); w.writeheader(); w.writerows(qrows)

# ---------- extra: HoS program net traffic effect, comp minus legacy same-store visits, k sensitivity ----------
print('\nquarter | DSG per-loc | HoS net traffic effect m2.0 / m3.3 (combined minus DSG per-location) | comp - DSG same-store visits')
for q, ms in fq.items():
    wts = [season[m[5:]] for m in ms]
    wa = lambda f_: sum(f_(R[m]) * w for m, w in zip(ms, wts)) / sum(wts)
    vpl = wa(lambda r: r['dsg_per_location_yoy'])
    e2 = wa(lambda r: r['combined_m2.0'] - r['dsg_per_location_yoy'])
    e3 = wa(lambda r: r['combined_m3.3'] - r['dsg_per_location_yoy'])
    ss = [R[m]['dsg_same_store_yoy'] for m in ms]
    ssq = None if any(s is None for s in ss) else sum(s * w for s, w in zip(ss, wts)) / sum(wts)
    cp = comp[q]
    print(f"{q:16s} | {vpl:5.1f} | {e2:4.1f} / {e3:4.1f} | {'' if (ssq is None or cp is None) else round(cp - ssq, 1)}")
print('\nAug-26 DSG banner estimate sensitivity to step k (pp): ', {kk: round((bbg['2026-08'] - kk) / (1 + kk / 100), 1) for kk in (7.6, 8.46, 9.5, 9.9)})

