"""H05: cohort + event-study on Google review velocity, normalising by legacy-DSG controls (same calendar months).
Rerun: python THESIS_SCRAPE/scripts/H05_event.py  (after H05_groups.py; reads raw/H05_reviews.csv, H05_hos_locations.csv, H05_controls.csv)
Cohort/opening months are INFERENCE from step-changes in each listing's monthly review series, cross-checked
with H07 TX permit first-sales dates (Dallas 2025-09-10, Live Oak 2025-10-15, Arlington 2026-06-17),
Jersey City 2025-09-18 (KNOWN_BRIEF) and Crabtree Sep-2026 (H04).
"""
import csv, collections, statistics as st
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
rev = list(csv.DictReader(open(R + r'\H05_reviews.csv', encoding='utf-8')))
JC = 'ChIJFwbfUHFXwokRhb583ME7-_0'
hos = {r['placeId']: r for r in csv.DictReader(open(R + r'\H05_hos_locations.csv', encoding='utf-8'))}
ctl = {r['placeId']: r for r in csv.DictReader(open(R + r'\H05_controls.csv', encoding='utf-8'))}
cnt = collections.defaultdict(collections.Counter)
for r in rev:
    cnt[r['placeId'] or JC][r['date'][:7]] += 1
M = ['%d-%02d' % (y, m) for y in (2025, 2026) for m in range(1, 13)][:21]
EXCL_LEG = {'ChIJoQK4GqTRNIgRT57dnDqpbt8', 'ChIJexFU3OuaQIYRZXB7k75C-ao',  # Greensburg Rr17 (dead listing), Webster TX (closed early 2026)
            'ChIJQzvbL0-wwogRhVjS1BOglsA', 'ChIJc4PDnFKv2YgRYvmmGYIPQfg'}  # Wesley Chapel, Pembroke Pines: scraper returned no data
LEG = [p for p, r in ctl.items() if r['group'] == 'LEG' and p not in EXCL_LEG]
legm = {m: st.mean([cnt[p].get(m, 0) for p in LEG]) for m in M}  # mean reviews per legacy store per month
print('legacy mean reviews/store/month:', ' '.join('%s:%.1f' % (m[2:], legm[m]) for m in M))

CONV = {  # placeId: inferred HoS opening month (in-place conversion / relocation keeping listing)
    'ChIJqURhEULOwogRv5F1-oQaUfE': '2025-11',  # Brandon FL
    'ChIJ879HjDDUw4kRmR7uQ_tjc00': '2025-11',  # Freehold NJ
    'ChIJEeSY-GP0OIgR2dKEYAFbBHw': '2025-08',  # Columbus Polaris (listing dark Feb-Jun 2025)
    'ChIJMTpivmly04kRnGspXOsyt14': '2026-03',  # Amherst NY
    'ChIJKytms9liToYRo9PbJlApoaI': '2026-06',  # Arlington TX (TX permit first sales 2026-06-17)
    'ChIJSywrOQnx5IcRZ7Kzz-vG-R0': '2026-06',  # Cedar Rapids IA
    'ChIJYWwijlEttokREeYp67_JnQE': '2026-06',  # Gaithersburg MD
    'ChIJgwk_u9fxt4kR1M95AqRoa0c': '2026-08',  # Annapolis MD
    'ChIJJ8LVYcnRNIgR1B2R9FI748E': '2026-08',  # Greensburg PA
}
NEW25 = {'ChIJv5rRsxyNXIYRBDsigiAX9t8': '2025-10', 'ChIJp_HEeQBBK4cR7vIHGFXd8bw': '2025-09', JC: '2025-09',
         'ChIJr5rqYF4hTIYRLtPtfqE2mGQ': '2025-09', 'ChIJRQfgFADprIkRkYSF-nFaFwE': '2025-10'}
SKIP = {'ChIJl8RHVFX2rIkRi0v2IkQYSC0',  # Raleigh Crabtree: opened Sep-2026
        'ChIJd5-zyMqr44kRDjTWo1yTJLQ', 'ChIJ6bu82KS9uokRs-RDna09owo', 'ChIJgRkgHpMVq4kRdnY7jbAH0ok', 'ChIJ3aEepYikJoYRYgdbVd3jr_c',  # DUP pairs
        'ChIJK7qWszx944kRQEY96A_6tTo', 'ChIJKTucqrcT44kRh5laGjSe52s'}  # placeholders
MATURE = [p for p in hos if p not in CONV and p not in NEW25 and p not in SKIP and hos[p]['reviewsCount']]

def ratio_series(p):
    return {m: cnt[p].get(m, 0) / legm[m] for m in M if legm[m] > 0}

def win(p, months):
    return sum(cnt[p].get(m, 0) for m in months)

W25 = M[3:9]; W26 = M[15:21]
legW25 = sum(legm[m] for m in W25); legW26 = sum(legm[m] for m in W26)
mat25 = st.mean([win(p, W25) for p in MATURE]); mat26 = st.mean([win(p, W26) for p in MATURE])
print('\nMATURE HoS n=%d: mean reviews/store Apr-Sep25 %.1f, Apr-Sep26 %.1f (y/y %+.0f%%); LEGACY n=%d: %.1f -> %.1f (y/y %+.0f%%)' % (
    len(MATURE), mat25, mat26, (mat26 / mat25 - 1) * 100, len(LEG), legW25, legW26, (legW26 / legW25 - 1) * 100))
print('  MATURE/LEG velocity ratio: Apr-Sep25 %.2fx, Apr-Sep26 %.2fx; relative y/y (HoS vs legacy) %+.1f%%' % (
    mat25 / legW25, mat26 / legW26, ((mat26 / mat25) / (legW26 / legW25) - 1) * 100))
med = lambda xs: st.median(xs)
print('  median store ratio to legacy-mean, Apr-Sep26: MATURE %.2fx' % med([win(p, W26) / legW26 for p in MATURE]))
print('\nEvent study (CONV): listing velocity relative to legacy mean, 6m pre vs months after opening')
out = []
for p, m0 in CONV.items():
    i0 = M.index(m0)
    pre = M[max(0, i0 - 6):i0]; post = M[i0 + 1:]  # exclude opening month
    if not post:
        post = M[i0:]
    pre_r = win(p, pre) / sum(legm[m] for m in pre); post_r = win(p, post) / sum(legm[m] for m in post)
    out.append((hos[p]['address'][:40], m0, len(pre), len(post), pre_r, post_r, post_r / pre_r if pre_r else float('nan')))
    print('  %-40s open %s  pre(%dm) %.2fx  post(%dm) %.2fx  uplift %.2fx' % (hos[p]['address'][:40], m0, len(pre), pre_r, len(post), post_r, post_r / pre_r if pre_r else float('nan')))
ups = [o[6] for o in out if o[6] == o[6]]
print('  CONV uplift: median %.2fx, mean %.2fx (n=%d)' % (med(ups), st.mean(ups), len(ups)))
print('\nNEW25 listings (new sites): velocity relative to legacy mean, months after opening month')
nr = []
for p, m0 in NEW25.items():
    i0 = M.index(m0); post = M[i0 + 1:]
    r_ = win(p, post) / sum(legm[m] for m in post); nr.append(r_)
    r26 = win(p, W26) / legW26
    print('  %-40s open %s  post(%dm) %.2fx   Apr-Sep26 %.2fx' % (hos[p]['address'][:40], m0, len(post), r_, r26))
print('  NEW25 median %.2fx mean %.2fx' % (med(nr), st.mean(nr)))
with open(R + r'\H05_event_study.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['store', 'open_month', 'pre_months', 'post_months', 'pre_ratio_vs_leg', 'post_ratio_vs_leg', 'uplift'])
    w.writerows(out)
with open(R + r'\H05_legacy_monthly_mean.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['month', 'legacy_mean_reviews_per_store', 'mature_hos_mean', 'n_leg', 'n_mature'])
    for m in M:
        w.writerow([m, round(legm[m], 2), round(st.mean([cnt[p].get(m, 0) for p in MATURE]), 2), len(LEG), len(MATURE)])
# mature HoS monthly vs legacy
print('\nmature HoS mean/store by month:', ' '.join('%s:%.1f' % (m[2:], st.mean([cnt[p].get(m, 0) for p in MATURE])) for m in M))
