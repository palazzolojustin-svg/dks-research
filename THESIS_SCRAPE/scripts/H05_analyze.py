"""H05: review-velocity analysis. Reads raw/H05_reviews.csv (+ raw/H05_hos_locations.csv, raw/H05_controls.csv if present)
and prints monthly review-count matrix per store and group summaries.
Rerun: python THESIS_SCRAPE/scripts/H05_analyze.py
"""
import csv, collections, os
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
rev = list(csv.DictReader(open(R + r'\H05_reviews.csv', encoding='utf-8')))
loc = {r['placeId']: r for r in csv.DictReader(open(R + r'\H05_hos_locations.csv', encoding='utf-8'))}
JC = 'ChIJFwbfUHFXwokRhb583ME7-_0'
grp = {pid: 'HoS' for pid in loc}
if os.path.exists(R + r'\H05_controls.csv'):
    for r in csv.DictReader(open(R + r'\H05_controls.csv', encoding='utf-8')):
        grp[r['placeId']] = r['group']; loc.setdefault(r['placeId'], r)
months = ['%d-%02d' % (y, m) for y in (2025, 2026) for m in range(1, 13)][:21]  # 2025-01 .. 2026-09
cnt = collections.defaultdict(collections.Counter)
for r in rev:
    pid = r['placeId'] or JC
    cnt[pid][r['date'][:7]] += 1
mode = os.environ.get('H05_MODE', 'matrix')
with open(R + r'\H05_monthly_matrix.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['placeId', 'group', 'address', 'lifetime_reviews'] + months)
    for pid, c in sorted(cnt.items(), key=lambda kv: -sum(kv[1].values())):
        L = loc.get(pid, {})
        w.writerow([pid, grp.get(pid, '?'), L.get('address', ''), L.get('reviewsCount', '')] + [c.get(m, 0) for m in months])
        if mode == 'matrix':
            print('%-4s %-45s %5s | ' % (grp.get(pid, '?'), (L.get('address', '') or '')[:45], L.get('reviewsCount', '')) + ' '.join('%3d' % c.get(m, 0) for m in months))
