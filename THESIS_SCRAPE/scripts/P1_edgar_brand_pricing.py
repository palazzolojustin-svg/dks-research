"""P1: pull every 10-Q/10-K/20-F/6-K/8-K(EX-99) filed 2025-01-01..today by DKS key brand vendors that file with the SEC,
and extract sentences mentioning price increases / pricing actions / tariffs.
Rerun: python P1_edgar_brand_pricing.py  -> raw/P1_edgar_pricing_snippets.csv, raw/P1_edgar_docs/<ticker>_<date>_<form>.txt
Uses data.sec.gov submissions API + Archives (SEC fair-access UA)."""
import requests, re, os, csv, time, html
H = {'User-Agent': 'DKS research palazzolojustin@gmail.com'}
BASE = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
DOCS = os.path.join(BASE, 'P1_edgar_docs'); os.makedirs(DOCS, exist_ok=True)
CIKS = {'NKE': 320187, 'DECK': 910521, 'UAA': 1336917, 'VFC': 103379, 'COLM': 1050797, 'YETI': 1670592,
        'GOLF': 1672013, 'MODG': 837465, 'PTON': 1639825, 'GRMN': 1121788, 'ONON': 1858985, 'LULU': 1397187,
        'AS': 1988894, 'WWW': 110471, 'SKX': 1065837, 'CROX': 1334036, 'ASO': 1817358, 'BBWI': 701985}
FORMS = {'10-Q', '10-K', '20-F', '6-K', '8-K'}
PAT = re.compile(r'(price increase|pricing action|pric(e|ing) (adjustment|change)s?|raise[ds]? (our )?prices|increase[ds]? (our )?prices|'
                 r'higher (average )?selling price|average selling price|ASP|strategic pricing|surgical|targeted price|price realization|'
                 r'pricing (benefit|tailwind|was|contributed)|tariff)', re.I)


def text_of(url):
    r = requests.get(url, headers=H, timeout=60)
    t = r.text
    t = re.sub(r'(?is)<(script|style).*?</\1>', ' ', t)
    t = re.sub(r'(?s)<[^>]+>', ' ', t)
    t = html.unescape(t)
    return re.sub(r'\s+', ' ', t)


def main():
    out = open(os.path.join(BASE, 'P1_edgar_pricing_snippets.csv'), 'w', newline='', encoding='utf-8')
    w = csv.writer(out); w.writerow(['ticker', 'form', 'filed', 'period', 'url', 'snippet'])
    for tk, cik in CIKS.items():
        try:
            s = requests.get(f'https://data.sec.gov/submissions/CIK{cik:010d}.json', headers=H, timeout=60).json()
        except Exception as e:
            print('ERR', tk, e); continue
        rec = s['filings']['recent']
        for i, form in enumerate(rec['form']):
            fd = rec['filingDate'][i]
            if form not in FORMS or fd < '2025-01-01':
                continue
            acc = rec['accessionNumber'][i].replace('-', '')
            prim = rec['primaryDocument'][i]
            urls = []
            if form == '8-K' or form == '6-K':
                # only earnings 8-K / 6-K: look at index for EX-99
                items = rec.get('items', [''] * len(rec['form']))[i]
                if form == '8-K' and '2.02' not in items:
                    continue
                try:
                    idx = requests.get(f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/index.json', headers=H, timeout=60).json()
                    for it in idx['directory']['item']:
                        n = it['name'].lower()
                        if (('ex99' in n or 'ex-99' in n or 'exhibit99' in n or form == '6-K') and n.endswith(('.htm', '.html'))):
                            urls.append(f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{it["name"]}')
                except Exception as e:
                    print('idxERR', tk, fd, e)
                time.sleep(0.15)
            else:
                urls.append(f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{prim}')
            for u in urls[:4]:
                try:
                    t = text_of(u)
                except Exception as e:
                    print('getERR', u, e); continue
                fn = os.path.join(DOCS, f'{tk}_{fd}_{form}_{os.path.basename(u)[:40]}.txt')
                open(fn, 'w', encoding='utf-8').write(t)
                n = 0
                for m in PAT.finditer(t):
                    a = max(0, m.start() - 350); b = min(len(t), m.end() + 350)
                    w.writerow([tk, form, fd, rec['reportDate'][i], u, t[a:b]]); n += 1
                print(tk, form, fd, len(t), 'hits', n)
                time.sleep(0.2)
        out.flush()


if __name__ == '__main__':
    main()
