"""L3: fetch Wayback-archived Workday CXS job-detail JSON (pre-Built-to-Win postings, mostly 2025) and extract
title, location, req id, posting date, time type and posted pay range.
Input: raw/L3_cdx_jobs*.csv (from L3_cdx_jobs.py). Uses one snapshot per distinct job URL (statuscode 200, json).
Rerun: python L3_fetch_archived_cxs.py  -> raw/L3_archived_cxs.jsonl (resumable; skips urls already fetched)
"""
import requests, json, time, os, re, html, glob
import pandas as pd
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
H = {'User-Agent': 'Mozilla/5.0 research (DKS thesis L3)'}
frames = [pd.read_csv(f, dtype=str) for f in glob.glob(os.path.join(RAW, 'L3_cdx_jobs*.csv'))]
d = pd.concat(frames).drop_duplicates(['timestamp', 'original'])
d = d[d.original.str.contains('/wday/cxs/', na=False) & (d.statuscode == '200')]
d['key'] = d.original.str.replace(r'\?.*$', '', regex=True).str.replace(r'-\d$', '', regex=True)
d = d.sort_values('timestamp').drop_duplicates('key', keep='first')
out = os.path.join(RAW, 'L3_archived_cxs.jsonl')
done = set()
if os.path.exists(out):
    for l in open(out, encoding='utf-8'):
        try:
            done.add(json.loads(l)['original'])
        except Exception:
            pass
print('to fetch', len(d), 'done', len(done), flush=True)
s = requests.Session()
with open(out, 'a', encoding='utf-8') as fh:
    for i, r in enumerate(d.itertuples()):
        if r.original in done:
            continue
        rec = {'timestamp': r.timestamp, 'original': r.original}
        for a in range(6):
            try:
                x = s.get(f'https://web.archive.org/web/{r.timestamp}id_/{r.original}', headers=H, timeout=90)
                if x.status_code == 200:
                    j = x.json().get('jobPostingInfo', {})
                    desc = html.unescape(re.sub(r'<[^>]+>', ' ', j.get('jobDescription', '') or ''))
                    desc = re.sub(r'\s+', ' ', desc)
                    m = re.search(r'Targeted Pay Range:\s*\$([\d,.]+)\s*-\s*\$([\d,.]+)([^.]{0,60})', desc)
                    rec.update({'title': j.get('title'), 'location': j.get('location'), 'req': j.get('jobReqId'),
                                'startDate': j.get('startDate'), 'timeType': j.get('timeType'),
                                'pay_lo': m.group(1) if m else None, 'pay_hi': m.group(2) if m else None,
                                'pay_tail': m.group(3) if m else None, 'desc': desc})
                    break
                rec['status'] = x.status_code
                if x.status_code in (404, 403):
                    break
            except Exception as e:
                rec['err'] = str(e)[:100]
            time.sleep(min(60, 5 * (a + 1)))
        fh.write(json.dumps(rec) + '\n'); fh.flush()
        if i % 25 == 0:
            print(i, rec.get('title'), rec.get('pay_lo'), flush=True)
        time.sleep(1.2)
print('done')
