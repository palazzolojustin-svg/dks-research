"""B2: what is the ~8.5pp post-deal step in the Bloomberg ALTD Placer DKS series? Two hypotheses:
  H-FL : Bloomberg added (part of) Foot Locker's chains point-in-time from ~w/e 21-Sep-25 -> step k = FL_t / DSG_(t-1).
         At the lap (from w/e 20-Sep-26) the step should vanish almost entirely (FL in both periods).
  H-HoS: Bloomberg added the separately-tracked 'DICK'S House of Sport' chain from ~w/e 21-Sep-25 without restating history
         -> step k = HoS_t / DSG_(t-1); at the lap the gap falls only to the HoS growth contribution.
Uses weekly BBG Placer y/y (C01A sec 9e) and the calibrated k (B2_traffic_recon.py, Oct-25..Apr-26).
Rerun: python B2_lap_test.py
"""
wk = {  # w/e (Sunday) : BBG Placer DKS y/y %, digitized +-0.5pp (27-Sep-26 disclosed)
    '2026-08-09': 0.8, '2026-08-16': 6.9, '2026-08-23': 0.4, '2026-08-30': 0.7, '2026-09-06': 3.8,
    '2026-09-13': -4.4, '2026-09-20': 4.8, '2026-09-27': -3.80}
k = 8.46          # mean post-deal step, pp (range 7.6-9.5)
pre = [wk[d] for d in ['2026-08-09', '2026-08-16', '2026-08-23', '2026-08-30', '2026-09-06']]
post = [wk[d] for d in ['2026-09-20', '2026-09-27']]
pre_m, post_m = sum(pre) / len(pre), sum(post) / len(post)
print(f'pre-lap BBG avg (5 wks Aug 9-Sep 6) {pre_m:+.2f}; post-lap BBG avg (w/e 20,27-Sep) {post_m:+.2f}; observed step-down {pre_m-post_m:.2f}pp')
# expected step-down if underlying DSG trend unchanged
# H-FL: step-down = k (FL fully in both periods after lap; assume FL and DSG y/y similar)
# H-HoS: after lap gap = share*(gH - gD); HoS count late Sep-25 ~28-30 vs late Sep-26 ~43-45; m implied by k:
nd, nh_now, nh_ly_sep = 680, 44, 29
m_impl = k / 100 * nd / 35          # k = m*N_H/N_D at Oct-25..Apr-26 (N_H=35, N_D~686)
gH_minus_gD = nh_now / nh_ly_sep - 1  # HoS chain growth from count only (per-location trend = DSG)
share_ly = m_impl * nh_ly_sep / (m_impl * nh_ly_sep + nd)
post_gap_hos = share_ly * gH_minus_gD * 100
print(f'H-HoS: implied HoS/DSG per-location multiple m = {m_impl:.2f}x; post-lap residual gap ~{post_gap_hos:.1f}pp -> expected step-down {k-post_gap_hos:.1f}pp')
print(f'H-FL : expected step-down ~{k:.1f}pp (less if FL visits fell faster than DSG; FL NA store count -6% y/y)')
# what change in the underlying DSG trend would reconcile each hypothesis with the observed step-down
obs = pre_m - post_m
print(f'Underlying DSG improvement needed (late Sep vs Aug): H-FL {k-obs:+.1f}pp ; H-HoS {(k-post_gap_hos)-obs:+.1f}pp')
# market control: Placer Mall Index open-air centers (most DSG boxes) Aug-26 vs Sep-26 (Sep incl. Labor Day shift)
print('Control: Placer mall index Sep-26 open-air +5.6%, indoor +5.5% (Labor-Day shift into Sep); Aug-26 values: see B2.md')
