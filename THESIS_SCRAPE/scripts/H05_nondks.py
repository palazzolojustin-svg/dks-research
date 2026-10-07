"""H05: non-DKS retail control (Target / Old Navy listings in HoS metros): Google review velocity and content, Apr-Sep 2025 vs Apr-Sep 2026.
Usage: python H05_nondks.py <apify dump .txt>   -> writes raw/H05_nondks_reviews.csv and prints comparison.
"""
import json, sys, csv, statistics as st, collections
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
d = json.load(open(sys.argv[1], encoding='utf-8'))
rows = []
for it in d['items']:
    for rv in it.get('reviews') or []:
        t = rv.get('text') or ''
        rows.append(dict(placeId=it['placeId'], title=it['title'], address=it['address'], date=(rv.get('publishedAtDate') or '')[:10], stars=rv.get('stars'), textlen=len(t)))
with open(R + r'\H05_nondks_reviews.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, list(rows[0].keys())); w.writeheader(); w.writerows(rows)
c = collections.defaultdict(lambda: [0, 0])
for r in rows:
    if '2025-04' <= r['date'][:7] <= '2025-09': c[(r['title'], r['address'][:30])][0] += 1
    if '2026-04' <= r['date'][:7] <= '2026-09': c[(r['title'], r['address'][:30])][1] += 1
for k, v in c.items():
    print('%-12s %-30s AprSep25=%4d AprSep26=%4d y/y=%+.0f%%' % (k[0][:12], k[1], v[0], v[1], (v[1] / v[0] - 1) * 100 if v[0] else float('nan')))
a = sum(v[0] for v in c.values()); b = sum(v[1] for v in c.values())
print('TOTAL %d -> %d  y/y %+.0f%%  (note: capped at 500 newest per place; check caps below)' % (a, b, (b / a - 1) * 100))
for it in d['items']:
    rv = it.get('reviews') or []
    print(it['title'], len(rv), min((x.get('publishedAtDate') or '')[:10] for x in rv) if rv else '')
for per, lo, hi in (('AprSep25', '2025-04', '2025-09'), ('AprSep26', '2026-04', '2026-09')):
    rs = [r for r in rows if lo <= r['date'][:7] <= hi]
    s = [r['stars'] for r in rs if r['stars']]
    print(per, 'n=%d avg*=%.2f no-text=%.0f%% medlen=%d' % (len(rs), st.mean(s), 100 * sum(1 for r in rs if r['textlen'] == 0) / len(rs), st.median(r['textlen'] for r in rs)))
