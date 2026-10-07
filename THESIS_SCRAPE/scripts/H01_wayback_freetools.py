"""H01: pull Wayback Machine snapshots of Placer.ai free-tool chain pages (DICK'S, DICK'S House of Sport, Academy,
Scheels, Big 5, Hibbett) and parse the 'Top Stores' month + visits, 'experienced a X% change' and state-map lines.
Builds a time series of the free snippets. Output: raw/H01_wayback_freetools.csv
Rerun: python H01_wayback_freetools.py
"""
import requests, re, time, csv, os
from bs4 import BeautifulSoup
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = {'User-Agent': 'Mozilla/5.0 (research; contact via site owner)'}
CHAINS = ['dicks-house-of-sport', 'dicks-sporting-goods', 'academy-sports-outdoors', 'scheels', 'big-5-sporting-goods', 'hibbett-sports']


def get(url, params=None, tries=6):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers=H, timeout=90)
            if r.status_code in (200, 404):
                return r
        except Exception as e:
            pass
        time.sleep(8 * (i + 1))
    return None


rows = []
for c in CHAINS:
    r = get('https://web.archive.org/cdx/search/cdx', {'url': 'placer.ai/free-tools/chains/' + c, 'output': 'json',
                                                       'filter': 'statuscode:200', 'collapse': 'digest'})
    if not r:
        print('cdx fail', c); continue
    snaps = r.json()[1:]
    print(c, len(snaps), 'snapshots')
    for s in snaps:
        ts = s[1]
        rr = get(f'https://web.archive.org/web/{ts}id_/{s[2]}')
        if not rr:
            print('  fail', ts); continue
        soup = BeautifulSoup(rr.text, 'html.parser')
        for t in soup(['style', 'script']):
            t.decompose()
        tx = soup.get_text(' | ', strip=True)
        m = re.search(r'Top Stores \| ([A-Za-z]+ \d{4})', tx)
        month = m.group(1) if m else ''
        stores = re.findall(r'\| / \| (?:[A-Z]{2,4} \| )?([^|]{8,80}?, [A-Z]{2} \d{5}) \| ([\d\.]+K)', tx)
        exp = re.search(r'experienced a \| ([-\d\.]+%) \| change in visits in \| ([A-Za-z]+ \d{4}) \| compared to \| ([A-Za-z]+ \d{4})', tx)
        st = re.search(r'stores in \| ([A-Za-z ]+) \| saw a \| ([-\d\.]+%) \| change in customer visits in \| ([A-Za-z]+ \d{4}) \| compared to \| ([A-Za-z]+ \d{4})', tx)
        cm = re.search(r'Chain Metrics \| ([A-Za-z]+ \d{4}) \| Vs\. \| ([A-Za-z]+ \d{4})(.{0,300})', tx)
        row = {'chain': c, 'snapshot': ts, 'top_month': month,
               'stores': ' ; '.join(f'{a}={b}' for a, b in stores[:10]),
               'experienced': ' '.join(exp.groups()) if exp else '',
               'state_line': ' '.join(st.groups()) if st else '',
               'chain_metrics': (' '.join(cm.groups()) if cm else '')[:300]}
        rows.append(row)
        print('  ', ts, month, row['stores'][:200], '|', row['experienced'], '|', row['state_line'])
        time.sleep(2)

with open(os.path.join(BASE, 'raw', 'H01_wayback_freetools.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ['chain'])
    w.writeheader(); w.writerows(rows)
