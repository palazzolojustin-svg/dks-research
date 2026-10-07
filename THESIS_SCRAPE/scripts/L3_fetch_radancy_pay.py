"""L3: fetch Wayback copies of old careers-site job pages (www.dickssportinggoods.jobs/job/<title>/<city-ST>/<req>/)
in pay-transparency states and extract the posted "Targeted Pay Range". Builds a 2024 / 2025 / early-2026 pay sample.
Input: raw/L3_cdx_reqs.csv (L3_cdx_title_mix.py) + raw/L3_cdx_jobs*.csv for timestamps.
Rerun: python L3_fetch_radancy_pay.py [max_per_year]  -> raw/L3_radancy_pay.jsonl (resumable)
"""
import requests, json, time, os, re, sys, glob
import pandas as pd
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
H = {'User-Agent': 'Mozilla/5.0 research (DKS thesis L3)'}
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 300
PAYST = {'CA', 'CO', 'NY', 'WA', 'IL', 'MD', 'NJ', 'MN', 'MA', 'CT', 'VT', 'DC', 'HI', 'NV', 'OH', 'RI'}
v = pd.concat([pd.read_csv(f, dtype=str) for f in glob.glob(os.path.join(RAW, 'L3_cdx_jobs*.csv'))]).drop_duplicates(['timestamp', 'original'])
v = v[(v.target == 'dickssportinggoods.jobs/job/') & (v.statuscode == '200')]
v['req'] = v.original.str.extract(r'/(20\d{7})/?')[0]
v['st'] = v.original.str.extract(r'-([A-Z]{2})/20\d{7}')[0]
v = v[v.req.notna() & v.st.isin(PAYST)]
v = v[~v.original.str.contains(r'engineer|analyst|intern|manager-of|director|accountant|designer|warehouse|shift|distribution|truck', case=False)]
v = v.sort_values('timestamp').drop_duplicates('req')
v['ryr'] = v.req.str[:4]
sample = pd.concat([g.sample(min(CAP, len(g)), random_state=7) for _, g in v.groupby('ryr')])
# always include all leadership titles (lead / assistant store manager / store manager)
lead = v[v.original.str.contains(r'lead|assistant-store-manager|store-manager|key-holder', case=False)]
sample = pd.concat([sample, lead]).drop_duplicates('req')
out = os.path.join(RAW, 'L3_radancy_pay.jsonl')
done = set()
if os.path.exists(out):
    for l in open(out, encoding='utf-8'):
        try:
            done.add(json.loads(l)['req'])
        except Exception:
            pass
print('candidates', len(v), 'sample', len(sample), 'by yr', sample.ryr.value_counts().to_dict(), 'done', len(done), flush=True)
s = requests.Session()
with open(out, 'a', encoding='utf-8') as fh:
    for i, r in enumerate(sample.itertuples()):
        if r.req in done:
            continue
        rec = {'req': r.req, 'timestamp': r.timestamp, 'original': r.original, 'st': r.st}
        for a in range(6):
            try:
                x = s.get(f'https://web.archive.org/web/{r.timestamp}id_/{r.original}', headers=H, timeout=90)
                if x.status_code == 200:
                    t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', x.text))
                    m = re.search(r'Targeted Pay Range:\s*\$([\d,]+(?:\.\d+)?)\s*-\s*\$([\d,]+(?:\.\d+)?)', t)
                    tt = re.search(r'<title>([^<]+)</title>', x.text)
                    ft = re.search(r'(Full[- ]time|Part[- ]time)', t, re.I)
                    rec.update({'lo': m.group(1) if m else None, 'hi': m.group(2) if m else None, 'page_title': tt.group(1).strip() if tt else None,
                                'timeType': ft.group(1) if ft else None})
                    break
                rec['status'] = x.status_code
                if x.status_code in (404, 403):
                    break
            except Exception as e:
                rec['err'] = str(e)[:80]
            time.sleep(min(60, 6 * (a + 1)))
        fh.write(json.dumps(rec) + '\n'); fh.flush()
        if i % 25 == 0:
            print(i, r.req, rec.get('lo'), rec.get('page_title'), flush=True)
        time.sleep(1.5)
print('done')
