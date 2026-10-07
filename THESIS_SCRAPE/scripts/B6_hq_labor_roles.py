"""B6: find HQ/field roles that own store labor / workforce management / store productivity / store tech in the DKS
Workday postings (live 2026-10-07 census from H06 + archived 2025 CXS from L3). Prints title, date and responsibilities.
Rerun: python B6_hq_labor_roles.py > raw/B6_hq_labor_roles.txt
"""
import json, re
BASE = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
TIT = re.compile(r'labor|workforce|productiv|store operations|store ops|retail technology|store technology|store systems|operations excellence|process optim|store experience|field operations|scheduling|planning analyst.*store|store readiness|retail operations|operating model|change management|store communication|frontline', re.I)
def rows():
    for l in open(BASE + r'\H06_workday_details_2026-10-07.jsonl', encoding='utf-8'):
        d = json.loads(l); yield '2026live', d['title'], d['location'], d['startDate'], d.get('desc') or ''
    for l in open(BASE + r'\L3_archived_cxs.jsonl', encoding='utf-8'):
        try: d = json.loads(l)
        except: continue
        yield '2025arch', d.get('title') or '', d.get('location'), d.get('startDate'), re.sub('<[^>]+>', ' ', d.get('desc') or '')
seen = set()
for src, t, loc, sd, desc in rows():
    if not t or not TIT.search(t): continue
    if re.search(r'^Store\d|Teammate|Specialist|Team Captain|Assistant Store Manager|Store Manager', t) and 'Store' in (loc or '') : continue
    k = (t, src)
    if k in seen: continue
    seen.add(k)
    i = desc.find('OVERVIEW')
    print('########', src, '|', t, '|', loc, '|', sd)
    print(re.sub(r'\s+', ' ', desc[i if i >= 0 else 0:][:3500]))
    print()
