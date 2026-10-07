"""X06: parse Wayback job-URL list (from X06_wayback_jobs.py) into unique requisitions with title/location,
flag corporate (CSC/remote) postings and vertical-brand (VB) product-org postings, and tabulate by year/half.

Rerun: python X06_wayback_parse.py   (after X06_wayback_jobs.py)
Output: PB_SCRAPE/raw/X06_wayback_reqs.csv and printed tables.
Caveat: Wayback captures are a crawler SAMPLE; use VB share of corporate postings, not raw counts.
"""
import csv, re, os, collections, urllib.parse

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
rows = list(csv.DictReader(open(os.path.join(RAW, 'X06_wayback_joburls.csv'), encoding='utf8')))


def parse(url):
    u = urllib.parse.unquote_plus(url)
    if 'myworkdayjobs' in u:
        tail = u.split('/job/', 1)[-1].split('?')[0]
        tail = re.sub(r'/(apply.*|login.*)$', '', tail)
        parts = tail.split('/')
        m = re.search(r'_(\d{9})(-\d+)?$', parts[-1])
        if not m:
            return None
        title = parts[-1][:m.start()].replace('-', ' ')
        loc = parts[0] if len(parts) > 1 else ''
        return title, loc, m.group(1)
    if '/job/?' in u:
        m = re.search(r'/job/\?(.*)-j-(\d{9})', u)
        if m:
            t = m.group(1)
            # Title-City-ST
            mm = re.match(r'(.*)-([^-]+)-([A-Z]{2})$', t)
            if mm:
                return mm.group(1), mm.group(2) + '-' + mm.group(3), m.group(2)
            return t, '', m.group(2)
        return None
    m = re.search(r'/job/([^/]+)/([^/]+)/(\d{9})', u)
    if m:
        return m.group(1).replace('-', ' '), m.group(2), m.group(3)
    return None


CORP_LOC = re.compile(r'coraopolis|customer.support.center|^remote|new.york|csc', re.I)
STORE_T = re.compile(r'\b(sales associate|cashier|teammate|team captain|specialist|lead|store|seasonal|retail|stocking|'
                     r'warehouse|distribution|dc |maintenance|janitor|quality control|loss prevention|golf professional|'
                     r'fitter|stringer|technician|operations associate|merchandising associate|sales leader|key holder)\b', re.I)
VB = re.compile(r'vertical brand|\bcalia\b|\bvrst\b|maxfli|walter hagen|alpine design|top.?flite|tommy armour|fitness gear|'
                r'sourcing (and|&) (pd|product)|sourcing & pd|sourcing pd|business development|product development|'
                r'product regulatory|technical design|tech design|print and textile|'
                r'print textile|textile|apparel design|apparel color|color specialist|industrial design|^designer|design admin|'
                r'fit (tech|engineer)|raw material|\bmaterials\b|quality assurance|product integrity|'
                r'director of design|men.s golf|women.s design', re.I)
VB_EXCL = re.compile(r'ux|mobile|omni|loyalty|store (design|apps|fulfillment)|in.store comm|learning|project designer|'
                     r'fixture|architecture|store designer|tech.*ecommerce|strategic sourcing|category sourcing manager tech|'
                     r'corporate functions|secured athlete|graphic designer', re.I)

reqs = {}
for r in rows:
    p = parse(r['url'])
    if not p:
        continue
    title, loc, req = p
    title = re.sub(r'\s+', ' ', title).strip()
    if req not in reqs or r['first_capture'] < reqs[req]['first_capture']:
        prev = reqs.get(req, {})
        reqs[req] = {'req': req, 'req_year': req[:4], 'first_capture': r['first_capture'], 'title': title or prev.get('title', ''),
                     'loc': loc or prev.get('loc', '')}
    else:
        if not reqs[req]['loc'] and loc:
            reqs[req]['loc'] = loc
out = []
for q in reqs.values():
    t, l = q['title'], q['loc']
    corp = bool(CORP_LOC.search(l)) or (not l and not STORE_T.search(t))
    if STORE_T.search(t) and not CORP_LOC.search(l):
        corp = False
    if re.search(r'^(retail|seasonal|golf sales|team sports sales|the north face brand|\d+ retail)', t, re.I) and 'pittsburgh' in l.lower():
        corp = False
    if re.search(r'pittsburgh', l, re.I) and not re.search(r'manager|analyst|director|engineer|counsel|designer', t, re.I):
        corp = False
    vb = bool(VB.search(t)) and not VB_EXCL.search(t)
    q['corporate'] = corp
    q['vb'] = vb and corp
    out.append(q)
with open(os.path.join(RAW, 'X06_wayback_reqs.csv'), 'w', newline='', encoding='utf8') as f:
    w = csv.DictWriter(f, fieldnames=['req', 'req_year', 'first_capture', 'title', 'loc', 'corporate', 'vb'])
    w.writeheader()
    w.writerows(sorted(out, key=lambda x: x['req']))


def half(q):
    return q['req_year'] + ('H1' if int(q['req'][4:]) < 9000 else 'H2')  # crude; replaced below by capture date


tab = collections.defaultdict(lambda: [0, 0, 0])
for q in out:
    k = q['first_capture'][:4] + ('H1' if q['first_capture'][4:6] <= '06' else 'H2')
    tab[k][0] += 1
    tab[k][1] += q['corporate']
    tab[k][2] += q['vb']
print('capture-half | all reqs | corporate | VB | VB % of corporate')
for k in sorted(tab):
    a, c, v = tab[k]
    print(k, a, c, v, '%.1f%%' % (100 * v / c) if c else '-')
tab2 = collections.defaultdict(lambda: [0, 0, 0])
for q in out:
    tab2[q['req_year']][0] += 1
    tab2[q['req_year']][1] += q['corporate']
    tab2[q['req_year']][2] += q['vb']
print('req-year | all | corporate | VB | VB%')
for k in sorted(tab2):
    a, c, v = tab2[k]
    print(k, a, c, v, '%.1f%%' % (100 * v / c) if c else '-')
print('\nVB list:')
for q in sorted(out, key=lambda x: x['req']):
    if q['vb']:
        print(q['req'], q['first_capture'], q['title'], '|', q['loc'])
