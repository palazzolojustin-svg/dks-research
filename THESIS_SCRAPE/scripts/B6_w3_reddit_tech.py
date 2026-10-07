"""B6 wave 3: grep L2's Reddit corpus (raw/L2_reddit_posts.jsonl + L2_reddit_threads.jsonl) for store-tech terms.
Rerun: python B6_w3_reddit_tech.py > raw/B6_w3_reddit_tech.txt
"""
import json, re, collections, datetime
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
PAT = re.compile(r'self[- ]?check|\bSCO\b|kiosk|zebra|handheld|\bTC5\d|\bscanner|\bRFID|legion|workload|labor model|payroll hours|hours budget|budgeted hours|cut hours|hours cut|labor budget|\bcoach\b.*app|ipad|mobile pos|line ?buster|tablet|robot|esl|electronic shelf|ship[- ]from[- ]store|\bSFS\b|BOPIS|pickup lockers?|locker', re.I)
seen = set(); hits = []
for fn in ['L2_reddit_posts.jsonl', 'L2_reddit_threads.jsonl']:
    try:
        f = open(RAW + '\\' + fn, encoding='utf-8')
    except Exception:
        continue
    for l in f:
        try: d = json.loads(l)
        except Exception: continue
        def walk(o):
            if isinstance(o, dict):
                txt = ' '.join(str(o.get(k) or '') for k in ('title', 'selftext', 'body', 'text'))
                if txt.strip():
                    ts = o.get('created_utc') or o.get('created') or o.get('date')
                    yield ts, o.get('subreddit'), o.get('id'), txt
                for v in o.values(): yield from walk(v)
            elif isinstance(o, list):
                for v in o: yield from walk(v)
        for ts, sub, pid, txt in walk(d):
            for m in PAT.finditer(txt):
                key = (pid, m.group(0).lower())
                if key in seen: continue
                seen.add(key)
                try: dt = datetime.datetime.utcfromtimestamp(float(ts)).strftime('%Y-%m-%d')
                except Exception: dt = str(ts)[:10]
                ctx = re.sub(r'\s+', ' ', txt[max(0, m.start()-220):m.end()+220])
                hits.append((dt, sub, pid, m.group(0).lower(), ctx))
hits.sort(key=lambda h: tuple(str(x) for x in h))
c = collections.Counter(re.sub(r'\W', '', h[3])[:10] for h in hits)
print('COUNTS', c.most_common())
for h in hits:
    print(' | '.join(str(x) for x in h))
