"""H05: group-level review-velocity analysis (HoS vs legacy DSG controls), 2025 vs 2026.
Inputs: raw/H05_reviews.csv, raw/H05_hos_locations.csv, raw/H05_controls.csv
Outputs: raw/H05_store_velocity.csv (per store), printed summary.
Rerun: python THESIS_SCRAPE/scripts/H05_groups.py
Definitions:
  W25 = Apr-Sep 2025 (6 months), W26 = Apr-Sep 2026 (6 months); JS25/JS26 = Jan-Sep.
  HoS cohorts (from review time series + known dates):
    MATURE  = HoS listing operating as HoS before 2025 (stable listing, no step-change in 2025-26)
    NEW25   = new Google listing created at a Q3-FY25 opening (first review Aug-Oct 2025)
    CONV    = existing listing converted in place / relocated during 2025-26 (step-change visible); opening month given
    DUP     = HoS store whose old DSG listing still exists at the same address (both listings summed)
"""
import csv, collections, statistics as st
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
rev = list(csv.DictReader(open(R + r'\H05_reviews.csv', encoding='utf-8')))
JC = 'ChIJFwbfUHFXwokRhb583ME7-_0'
hos = {r['placeId']: r for r in csv.DictReader(open(R + r'\H05_hos_locations.csv', encoding='utf-8'))}
ctl = {r['placeId']: r for r in csv.DictReader(open(R + r'\H05_controls.csv', encoding='utf-8'))}
cnt = collections.defaultdict(collections.Counter)
stars = collections.defaultdict(list)
for r in rev:
    pid = r['placeId'] or JC
    cnt[pid][r['date'][:7]] += 1
    if r['stars']:
        stars[(pid, r['date'][:4])].append(float(r['stars']))

def win(c, y, m0, m1):
    return sum(c.get('%d-%02d' % (y, m), 0) for m in range(m0, m1 + 1))

# cohort tags for HoS listings (judgement from monthly matrix + H07/H04 dates; see H05.md)
NEW25 = {'ChIJv5rRsxyNXIYRBDsigiAX9t8', 'ChIJp_HEeQBBK4cR7vIHGFXd8bw', JC, 'ChIJr5rqYF4hTIYRLtPtfqE2mGQ', 'ChIJRQfgFADprIkRkYSF-nFaFwE'}
DUPPAIR = {  # HoS listing -> old DSG listing at same site
    'ChIJd5-zyMqr44kRDjTWo1yTJLQ': 'ChIJtxD09jGq44kRqWnSTGhKC8g',  # Salem NH
    'ChIJ6bu82KS9uokRs-RDna09owo': 'ChIJj_buu8a8uokRORzYruZeIzc',  # Chesapeake
    'ChIJgRkgHpMVq4kRdnY7jbAH0ok': 'ChIJlQTLKNIUq4kRDqKy8uWF_cw',  # Fayetteville NC
    'ChIJ3aEepYikJoYRYgdbVd3jr_c': 'ChIJo3Tuu5GlJoYRgvMrcfyc9zA',  # Baton Rouge
}
rows = []
for pid, L in list(hos.items()) + list(ctl.items()):
    if pid in DUPPAIR.values():
        continue
    c = collections.Counter(cnt.get(pid, {}))
    if pid in DUPPAIR:
        c.update(cnt.get(DUPPAIR[pid], {}))
    g = ctl[pid]['group'] if pid in ctl else ('HoS-NEW25' if pid in NEW25 else ('HoS-DUP' if pid in DUPPAIR else 'HoS'))
    if not L.get('reviewsCount') or (L.get('reviewsCount') and int(L['reviewsCount'] or 0) < 5 and pid not in ctl):
        continue
    w25, w26 = win(c, 2025, 4, 9), win(c, 2026, 4, 9)
    js25, js26 = win(c, 2025, 1, 9), win(c, 2026, 1, 9)
    q325, q326 = win(c, 2025, 8, 9), win(c, 2026, 8, 9)
    s25 = stars.get((pid, '2025'), []); s26 = stars.get((pid, '2026'), [])
    rows.append(dict(placeId=pid, group=g, address=L['address'], lifetime=L.get('reviewsCount'), W25=w25, W26=w26, JS25=js25, JS26=js26,
                     AugSep25=q325, AugSep26=q326, mo_W26=round(w26 / 6, 2), stars25=round(st.mean(s25), 2) if s25 else '', stars26=round(st.mean(s26), 2) if s26 else ''))
with open(R + r'\H05_store_velocity.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, list(rows[0].keys())); w.writeheader(); w.writerows(rows)

def summ(name, rs):
    if not rs:
        return
    W25 = sum(r['W25'] for r in rs); W26 = sum(r['W26'] for r in rs)
    per = [r['W26'] / 6 for r in rs]
    yoy = [r['W26'] / r['W25'] - 1 for r in rs if r['W25'] >= 10]
    print('%-28s n=%2d  W25=%5d W26=%5d  agg y/y=%+6.1f%%  median store y/y=%+6.1f%%  mean rev/mo W26=%5.1f  median=%5.1f  JS25=%d JS26=%d AugSep25=%d AugSep26=%d' % (
        name, len(rs), W25, W26, (W26 / W25 - 1) * 100 if W25 else float('nan'), st.median(yoy) * 100 if yoy else float('nan'),
        st.mean(per), st.median(per), sum(r['JS25'] for r in rs), sum(r['JS26'] for r in rs), sum(r['AugSep25'] for r in rs), sum(r['AugSep26'] for r in rs)))

G = collections.defaultdict(list)
for r in rows:
    G[r['group']].append(r)
for g in sorted(G):
    summ(g, G[g])
summ('ALL HoS (excl NEW25)', [r for r in rows if r['group'] in ('HoS', 'HoS-DUP')])
summ('ALL HoS incl NEW25', [r for r in rows if r['group'].startswith('HoS')])
