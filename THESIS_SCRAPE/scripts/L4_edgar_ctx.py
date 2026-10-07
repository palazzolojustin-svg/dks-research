"""L4: pull context windows from EDGAR filings found by L4_edgar_fts.py.
Usage: python L4_edgar_ctx.py "<filer name substring>" "<regex of phrases>" [window_chars] [max_docs]
 - reads raw/L4_edgar_fts_hits.json, takes every hit whose filer name contains the substring,
 - fetches each document once (cached in raw/L4_edgar_cache/), prints and appends windows around the regex
   to raw/L4_ctx_<filer>.txt
"""
import sys, re, json, os, time, hashlib, requests, warnings
import lxml
from bs4 import BeautifulSoup
warnings.filterwarnings('ignore')
H = {'User-Agent': 'DKS research palazzolojustin@gmail.com'}
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
CACHE = os.path.join(RAW, 'L4_edgar_cache')
os.makedirs(CACHE, exist_ok=True)

def get_text(cik, adsh, fn):
    key = hashlib.md5(f'{adsh}{fn}'.encode()).hexdigest()
    p = os.path.join(CACHE, key + '.txt')
    if os.path.exists(p):
        return open(p, encoding='utf-8').read()
    url = f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace("-", "")}/{fn}'
    for k in range(4):
        try:
            r = requests.get(url, headers=H, timeout=90); break
        except Exception as e:
            print('retry', k, e); time.sleep(3 * (k + 1))
    else:
        return url + '\n'
    t = BeautifulSoup(r.text, 'lxml').get_text(' ', strip=True)
    t = re.sub(r'\s+', ' ', t)
    open(p, 'w', encoding='utf-8').write(url + '\n' + t)
    time.sleep(0.15)
    return url + '\n' + t

if __name__ == '__main__':
    filer = sys.argv[1]; rx = sys.argv[2]
    win = int(sys.argv[3]) if len(sys.argv) > 3 else 700
    maxd = int(sys.argv[4]) if len(sys.argv) > 4 else 40
    hits = json.load(open(os.path.join(RAW, 'L4_edgar_fts_hits.json')))
    docs = {}
    for ph, hh in hits.items():
        for h in hh:
            if filer.lower() in h['name'].lower():
                docs[h['id']] = h
    docs = sorted(docs.values(), key=lambda h: h['date'])[:maxd]
    out = open(os.path.join(RAW, f'L4_ctx_{re.sub(r"[^A-Za-z]", "", filer)[:20]}.txt'), 'a', encoding='utf-8')
    for h in docs:
        adsh, fn = h['id'].split(':')
        t = get_text(h['ciks'][0], adsh, fn)
        url = t.split('\n', 1)[0]
        hdr = f"\n######## {h['name'][:40]} | {h['form']} | filed {h['date']} | period {h['period']} | {url}"
        print(hdr); out.write(hdr + '\n')
        last = -10**9
        for m in re.finditer(rx, t, re.I):
            if m.start() - last < win:
                continue
            last = m.start()
            s = '--- ' + t[max(0, m.start() - win): m.end() + win]
            print(s); out.write(s + '\n')
    out.close()
