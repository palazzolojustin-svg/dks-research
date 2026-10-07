"""X06: LinkedIn cohort analysis of current DKS employees in the vertical-brands org.

Data: Apify actor harvestapi/linkedin-profile-search (Full mode), searchQuery '"vertical brands"' (and others),
currentCompanies=DICK'S Sporting Goods. Rerun the actor in the Apify console (cost ~ $0.10/25-profile page +
$0.004/profile) and pass the dataset id(s) here:
    python X06_linkedin_cohort.py <datasetId> [<datasetId> ...]
Output: PB_SCRAPE/raw/X06_linkedin_cohort.csv (NO names stored: only title, DKS start month, DKS tenure-start,
prior employer of the person's previous role) + printed tables of DKS-start-year and current-role-start-year.
Interpretation: a survivorship-biased cohort (only people still there and on LinkedIn), so recent years are
over-represented by construction; compare against a control query (e.g. all DKS corporate merchants).
"""
import requests, sys, os, csv, collections, re

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
MONTHS = {m: i for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 1)}


def ym(d):
    if not d or not d.get('year'):
        return None
    return '%04d-%02d' % (int(d['year']), MONTHS.get(d.get('month') or 'Jan', 1))


rows = []
seen = set()
import json
for ds in sys.argv[1:]:
    if os.path.exists(ds):  # local JSON export (Apify console download, or MCP get-dataset-items dump)
        d = json.load(open(ds, encoding='utf8'))
        items = d['items'] if isinstance(d, dict) else d
    else:  # needs APIFY_TOKEN env var for private datasets
        tok = os.environ.get('APIFY_TOKEN', '')
        items = requests.get('https://api.apify.com/v2/datasets/%s/items?format=json&clean=1&token=%s' % (ds, tok), timeout=120).json()
    for it in items:
        pid = it.get('id') or it.get('publicIdentifier') or json.dumps(it.get('experience', ''))[:400]
        if pid in seen:
            continue
        seen.add(pid)
        exp = it.get('experience') or []
        dks = [e for e in exp if 'dick' in (e.get('companyName') or '').lower()]
        cur = (it.get('currentPosition') or [{}])[0]
        if not dks:
            continue
        starts = [ym(e.get('startDate')) for e in dks if ym(e.get('startDate'))]
        first_dks = min(starts) if starts else None
        cur_start = ym(cur.get('startDate')) if 'dick' in (cur.get('companyName') or '').lower() else None
        non_dks = [e for e in exp if 'dick' not in (e.get('companyName') or '').lower() and ym(e.get('startDate'))]
        prior = ''
        if first_dks:
            before = [e for e in non_dks if ym(e.get('startDate')) <= first_dks]
            if before:
                prior = sorted(before, key=lambda e: ym(e.get('startDate')))[-1].get('companyName') or ''
        ttl = (cur.get('position') or '') + ' ' + (it.get('headline') or '') + ' ' + (cur.get('description') or '')
        vb_org = bool(re.search(r'vertical|calia|vrst|maxfli|walter hagen|alpine design|top.?flite|tommy armour|private (brand|label)|'
                                r'technical design|tech design|product develop|sourcing|fabric|textile|industrial design|'
                                r'\bdesigner\b|testing manager|quality assurance|business development', ttl, re.I)) and not re.search(
                                r'software|engineer|ux|product designer ii|data|media|store design|space plan|hr ', cur.get('position') or '', re.I)
        k2 = (cur.get('position'), cur_start, first_dks, prior)
        if k2 in seen:
            continue
        seen.add(k2)
        rows.append({'dataset': os.path.basename(ds)[-12:], 'current_title': cur.get('position') or it.get('headline'), 'vb_org': vb_org,
                     'cur_desc': (cur.get('description') or '')[:600].replace('\n', ' '),
                     'dks_first_start': first_dks, 'current_role_start': cur_start, 'prior_employer': prior,
                     'vb_in_title': bool(re.search(r'vertical|calia|vrst|maxfli|private brand|\bdsg\b', (cur.get('position') or '') + ' ' + (it.get('headline') or ''), re.I))})
os.makedirs(RAW, exist_ok=True)
with open(os.path.join(RAW, 'X06_linkedin_cohort.csv'), 'w', newline='', encoding='utf8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print('profiles with DKS experience', len(rows), 'VB-in-title', sum(r['vb_in_title'] for r in rows))
for key in ['dks_first_start', 'current_role_start']:
    for flt in [False, True]:
        c = collections.Counter((r[key] or '')[:4] for r in rows if (not flt or r['vb_in_title']))
        print(key, 'VB-title-only' if flt else 'all', sorted(c.items()))
# half-year buckets of DKS joiners with VB title
c = collections.Counter()
for r in rows:
    if r['vb_in_title'] and r['dks_first_start']:
        y, m = r['dks_first_start'].split('-')
        c[y + ('H1' if int(m) <= 6 else 'H2')] += 1
print('VB-title joiners by half', sorted(c.items()))
c = collections.Counter()
for r in rows:
    if r['vb_in_title'] and r['current_role_start']:
        y, m = r['current_role_start'].split('-')
        c[y + ('H1' if int(m) <= 6 else 'H2')] += 1
print('VB-title current-role starts by half', sorted(c.items()))
for lab, flt in [('VB-ORG', True), ('NON-VB (control)', False)]:
    cj, cr = collections.Counter(), collections.Counter()
    for r in rows:
        if r['vb_org'] != flt:
            continue
        for key, c in [('dks_first_start', cj), ('current_role_start', cr)]:
            if r[key]:
                y, m = r[key].split('-')
                c[y + ('H1' if int(m) <= 6 else 'H2')] += 1
    print(lab, 'n=%d' % sum(1 for r in rows if r['vb_org'] == flt))
    print('  DKS joiners by half      ', sorted((k, v) for k, v in cj.items() if k >= '2022'))
    print('  current-role starts by half', sorted((k, v) for k, v in cr.items() if k >= '2022'))
print('prior employers of VB-org external joiners since 2024:')
print(collections.Counter(r['prior_employer'] for r in rows if r['vb_org'] and (r['dks_first_start'] or '') >= '2024').most_common(40))
print('prior employers (external joiners since 2024):')
print(collections.Counter(r['prior_employer'] for r in rows if (r['dks_first_start'] or '') >= '2024').most_common(40))
for r in sorted(rows, key=lambda r: r['current_role_start'] or ''):
    if r['vb_org']:
        print(r['current_role_start'], r['dks_first_start'], '|', r['current_title'], '| prior:', r['prior_employer'],
              '| DESC:', r['cur_desc'][:300] if r['cur_desc'] else '')
