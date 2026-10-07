"""X12: Slickdeals deal-post time series for DKS owned brands (consumer deal-seeking / markdown proxy).

How to rerun (weekly):  python X12_slickdeals_owned_brand_deals.py
- Uses Slickdeals' public search RSS (newsearch.php?...&rss=1&page=N), 25 items per page, no login.
- For each query it pages until no items or MAX_PAGES. Keeps item date, title, price in title,
  thumb score, retailer (from the 'data-store-slug' in content), link.
- Output: PB_SCRAPE/raw/X12_slickdeals_deals.csv (one row per deal post) and a monthly pivot printed.
Notes: a deal post = a consumer finding a markdown worth sharing. Rising counts of owned-brand
posts at Dick's = deeper/more frequent owned-brand markdowns (AGAINST margin thesis) and/or
rising consumer interest (thumb scores). Compare vs benchmark national brands at Dick's.
"""
import re, time, html, csv, sys, requests
from datetime import datetime

H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
OUT = r'C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw\X12_slickdeals_deals.csv'
MAX_PAGES = 40
QUERIES = {
    # owned brands
    'VRST': 'vrst', 'CALIA': 'calia', 'DSG': 'dsg', 'MAXFLI': 'maxfli', 'WALTER HAGEN': 'walter hagen',
    'ALPINE DESIGN': 'alpine design', 'FITNESS GEAR': 'fitness gear', 'TOP-FLITE': 'top flite',
    'TOMMY ARMOUR': 'tommy armour', 'ETHOS': 'ethos', 'NISHIKI': 'nishiki', 'QUEST': 'quest',
    # benchmark denominator: ALL deal posts whose text links dickssportinggoods.com (searchin=all), deep paging
    'BENCH_DKS_ALL': ('dickssportinggoods.com', 'all', 320),
    # control retailer: is the rise in DKS deal posts DKS-specific or Slickdeals-wide?
    'BENCH_ASO_ALL': ('academy.com', 'all', 320),
}
# NOTE (2026-10-07 run): search pagination ends after ~65 pages (~1,600 posts), i.e. ~17 months
# of DKS posts. Run weekly and append to keep a longer history.


def fetch(q, page, searchin='first'):
    url = 'https://slickdeals.net/newsearch.php'
    p = {'q': q, 'searcharea': 'deals', 'searchin': searchin, 'rss': 1, 'page': page}
    for attempt in range(5):
        try:
            r = requests.get(url, params=p, headers=H, timeout=40)
            if r.status_code == 200 and '<rss' in r.text:
                return r.text
        except Exception as e:
            print('err', q, page, type(e).__name__, file=sys.stderr)
        time.sleep(4 * (attempt + 1))
    return None  # persistent failure (distinct from a valid empty page)


def parse(xml):
    rows = []
    for it in re.findall(r'<item>(.*?)</item>', xml, re.S):
        g = lambda pat: (re.search(pat, it, re.S).group(1) if re.search(pat, it, re.S) else '')
        title = html.unescape(g(r'<title><!\[CDATA\[(.*?)\]\]></title>'))
        d = g(r'<pubDate>(.*?)</pubDate>')
        try:
            dt = datetime.strptime(d.strip(), '%a, %d %b %Y %H:%M:%S %z')
        except Exception:
            continue
        store = g(r'data-store-slug="([^"]+)"')
        thumb = g(r'Thumb Score:\s*([+-]?\d+)')
        price = re.search(r'\$(\d[\d,]*\.?\d*)', title)
        rows.append({'date': dt.strftime('%Y-%m-%d'), 'title': title, 'store': store,
                     'thumb': thumb, 'price': price.group(1).replace(',', '') if price else '',
                     'link': g(r'<link>(.*?)</link>').split('?')[0]})
    return rows


def main():
    only = set(sys.argv[1:])  # optional: run only these QUERIES keys
    allrows = []
    for key, q in QUERIES.items():
        if only and key not in only:
            continue
        q, searchin, maxp = (q, 'first', MAX_PAGES) if isinstance(q, str) else q
        seen = set()
        fails = 0
        for page in range(1, maxp + 1):
            xml = fetch(q, page, searchin)
            if xml is None:
                fails += 1
                if fails >= 3:
                    print('GAVE UP', key, 'page', page, file=sys.stderr)
                    break
                continue
            rows = parse(xml)
            new = [r for r in rows if r['link'] not in seen]
            if not new:
                break
            for r in new:
                seen.add(r['link'])
                r['query'] = key
                allrows.append(r)
            time.sleep(1.5)
        print(key, len(seen), file=sys.stderr)
    out = OUT if not only else OUT.replace('.csv', '_' + '_'.join(sorted(k.replace(' ', '') for k in only)) + '.csv')
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['query', 'date', 'store', 'thumb', 'price', 'title', 'link'])
        w.writeheader(); w.writerows(allrows)
    print('wrote', len(allrows), out)


if __name__ == '__main__':
    main()
