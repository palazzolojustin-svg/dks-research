"""L4: for each peer retailer (CIK), use EDGAR full-text search to find 10-K/10-Q/8-K documents (2017-2026) that mention
store-labor phrases, fetch each document once (cache raw/L4_edgar_cache), and keep every SENTENCE that mentions a labor phrase
AND carries a number (bps, %, $, million, hours). Duplicate sentences across filings are collapsed (dates listed).
Rerun: python L4_peer_sentences.py <group>   (group = a|b|c|all; see PEERS)  -> raw/L4_sent_<name>.txt
"""
import sys, re, json, os, time, hashlib, requests, warnings
import lxml
from bs4 import BeautifulSoup
warnings.filterwarnings('ignore')
H = {'User-Agent': 'DKS research palazzolojustin@gmail.com', 'Accept': 'application/json'}
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
CACHE = os.path.join(RAW, 'L4_edgar_cache2'); os.makedirs(CACHE, exist_ok=True)
PEERS = {
 'a': [('Target', '27419'), ('Walmart', '104169'), ('HomeDepot', '354950'), ('Lowes', '60667'), ('BestBuy', '764478'),
       ('Kohls', '885639'), ('DollarGeneral', '29534'), ('Academy', '1817358'), ('Ulta', '1403568')],
 'b': [('AEO', '919012'), ('Michaels', '1593936'), ('BedBath', '886158'), ('BarnesNoble', '890491'), ('BigLots', '768835'),
       ('DesignerBrands', '1319947'), ('Petco', '1826470'), ('Gap', '39911'), ('BathBody', '701985')],
 'c': [('FootLocker', '850209'), ('Big5', '1156388'), ('Hibbett', '1017480'), ('TractorSupply', '916365'),
       ('ChildrensPlace', '1041859'), ('Signet', '832988'), ('Macys', '794367'), ('VictoriasSecret', '1856437'),
       ('Leslies', '1821806'), ('DollarTree', '935703'), ('BJs', '1531152'), ('Burlington', '1579298')],
}
PHRASES = ['labor model', 'store payroll', 'store labor', 'store operating model', 'store leadership', 'store staffing',
           'store structure', 'field structure', 'labor hours', 'payroll hours', 'store management']
LAB = re.compile(r'labor model|store payroll|store labor|operating model|store leadership|staffing|store structure|field structure|labor hours|payroll hours|store management|store manager|team lead|labor productivity|labor efficienc|store team|payroll', re.I)
NUM = re.compile(r'\d+\s*(basis points|bps)|\$\s?\d|\d(\.\d+)?\s*%|\d+ ?million|billion|\d[\d,]* (hours|positions|roles|employees|associates|jobs)', re.I)

def fts(q, cik):
    out, start = [], 0
    while True:
        p = {'q': f'"{q}"', 'forms': '10-K,10-Q,8-K', 'dateRange': 'custom', 'startdt': '2017-01-01', 'enddt': '2026-10-07',
             'ciks': cik.zfill(10), 'from': start}
        for k in range(3):
            try:
                d = requests.get('https://efts.sec.gov/LATEST/search-index', params=p, headers=H, timeout=60).json(); break
            except Exception:
                time.sleep(3)
        else:
            return out
        hh = d.get('hits', {}).get('hits', [])
        if not hh: break
        for x in hh:
            s = x['_source']; out.append((x['_id'], s.get('file_date'), s.get('form'), s.get('ciks')[0]))
        start += len(hh)
        if start >= d['hits']['total']['value'] or start >= 300: break
        time.sleep(0.15)
    return out

def get_text(cik, adsh, fn):
    key = hashlib.md5(f'{adsh}{fn}'.encode()).hexdigest(); p = os.path.join(CACHE, key + '.txt')
    if os.path.exists(p): return open(p, encoding='utf-8').read()
    url = f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace("-", "")}/{fn}'
    for k in range(4):
        try:
            r = requests.get(url, headers={'User-Agent': H['User-Agent']}, timeout=90); break
        except Exception:
            time.sleep(3 * (k + 1))
    else:
        return url + '\n'
    t = re.sub(r'\s+', ' ', BeautifulSoup(r.content, 'lxml').get_text(' ', strip=True))
    open(p, 'w', encoding='utf-8').write(url + '\n' + t); time.sleep(0.12)
    return url + '\n' + t

def run(name, cik):
    docs = {}
    for ph in PHRASES:
        for did, date, form, c in fts(ph, cik):
            docs[did] = (date, form, c)
    sents = {}
    for did, (date, form, c) in sorted(docs.items(), key=lambda kv: kv[1][0]):
        adsh, fn = did.split(':')
        t = get_text(c, adsh, fn); url = t.split('\n', 1)[0]
        for s in re.split(r'(?<=[.;])\s+(?=[A-Z•])', t):
            if len(s) > 1500 or not LAB.search(s) or not NUM.search(s):
                continue
            k = re.sub(r'\W+', '', s.lower())[:400]
            if k in sents: sents[k][1].append(f'{date} {form}')
            else: sents[k] = [s, [f'{date} {form}'], url]
    with open(os.path.join(RAW, f'L4_sent_{name}.txt'), 'w', encoding='utf-8') as f:
        f.write(f'# {name} CIK {cik}: {len(docs)} docs, {len(sents)} unique labor+number sentences\n')
        for s, dates, url in sents.values():
            f.write(f'\n[{dates[0]}{" +" + str(len(dates)-1) if len(dates) > 1 else ""}] {url}\n{s}\n')
    print(name, len(docs), len(sents), flush=True)

if __name__ == '__main__':
    g = sys.argv[1] if len(sys.argv) > 1 else 'a'
    for grp in (PEERS if g == 'all' else {g: PEERS[g]}):
        for name, cik in PEERS[grp]:
            if len(sys.argv) > 2 and name not in sys.argv[2:]: continue
            run(name, cik)
