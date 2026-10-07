"""B6: crawl vendor sitemaps (Legion and other store-labor/store-tech vendors) and grep every URL for DICK'S mentions;
optionally fetch pages and grep text for 'dick'.
Rerun: python B6_vendor_sitemaps.py <domain> [fetch]   e.g. python B6_vendor_sitemaps.py legion.co fetch
Outputs raw/B6_sitemap_<domain>.txt (all URLs) and raw/B6_sitemap_hits_<domain>.txt
"""
import requests, re, sys, os, time
from bs4 import BeautifulSoup
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36'}
RAW=r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'

def urls_from(sm, depth=0, seen=None):
    seen = seen if seen is not None else set()
    if sm in seen or depth > 3: return []
    seen.add(sm)
    try: r = requests.get(sm, headers=H, timeout=30)
    except Exception as e: print('ERR', sm, e); return []
    locs = re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', r.text)
    out = []
    for l in locs:
        if l.endswith('.xml') or 'sitemap' in l.split('/')[-1]: out += urls_from(l, depth+1, seen)
        else: out.append(l)
    return out

if __name__ == '__main__':
    dom = sys.argv[1]; fetch = len(sys.argv) > 2
    cands = []
    try:
        rb = requests.get(f'https://{dom}/robots.txt', headers=H, timeout=20).text
        cands = re.findall(r'(?im)^sitemap:\s*(\S+)', rb)
    except Exception: pass
    cands += [f'https://{dom}/sitemap.xml', f'https://{dom}/sitemap_index.xml', f'https://{dom}/wp-sitemap.xml']
    allu = []
    for c in dict.fromkeys(cands):
        u = urls_from(c)
        if u: allu += u
    allu = list(dict.fromkeys(allu))
    open(os.path.join(RAW, f'B6_sitemap_{dom}.txt'), 'w', encoding='utf-8').write('\n'.join(allu))
    print(dom, 'urls', len(allu))
    hits = [u for u in allu if re.search(r'dick|dsg|sporting|retail|case|customer|stor', u, re.I)]
    for u in hits[:300]: print('  ', u)
    if fetch:
        out = open(os.path.join(RAW, f'B6_sitemap_hits_{dom}.txt'), 'w', encoding='utf-8')
        targets = allu if sys.argv[2] == 'all' else [u for u in allu if re.search(r'case|customer|stor|retail|success|press|news|blog|podcast|resource|event|webinar', u, re.I)]
        print('fetching', len(targets))
        for u in targets:
            try:
                t = BeautifulSoup(requests.get(u, headers=H, timeout=30).text, 'html.parser').get_text(' ')
            except Exception as e: continue
            for m in re.finditer(r"dick'?s|dick’s|sporting goods", t, re.I):
                s = re.sub(r'\s+', ' ', t[max(0, m.start()-300):m.end()+300])
                out.write(u + ' || ' + s + '\n'); print('HIT', u, '||', s[:300]); break
            time.sleep(0.3)
