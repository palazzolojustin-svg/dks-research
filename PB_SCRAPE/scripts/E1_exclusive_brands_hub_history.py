"""E1: History of the dicks.com "DICK'S Exclusive Brands" hub (/c/dicks-exclusive-brands) and related owned-brand landing pages
from Wayback snapshots: which brands are listed, which promo copy (e.g. "% off") sits on the hub, per capture date.

Rerun: python E1_exclusive_brands_hub_history.py
Output: PB_SCRAPE/raw/E1_exclusive_brands_hub_history.csv (+ cached HTML in raw/E1_wb_cache)
"""
import os, re, csv, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import E1_wayback_promo_census as E

PAGES = ['dickssportinggoods.com/c/dicks-exclusive-brands', 'dickssportinggoods.com/f/dicks-exclusive-brands-gifts',
         'dickssportinggoods.com/f/dicks-exclusive-fitness-brands', 'dickssportinggoods.com/c/this-weeks-deals']


def cdx_all(target):
    r = E.get('https://web.archive.org/cdx/search/cdx', {'url': target, 'output': 'txt', 'fl': 'timestamp,statuscode,length',
              'collapse': 'timestamp:8', 'from': '2022'}, timeout=180)
    if r is None:
        return []
    return [l.split() for l in r.text.strip().splitlines() if l and l[0].isdigit()]


def main():
    out = []
    for p in PAGES:
        rows = cdx_all(p)
        print(p, len(rows))
        for row in rows:
            ts, sc = row[0], row[1]
            if sc != '200':
                continue
            fn = os.path.join(E.CACHE, hashlib.md5((p + ts).encode()).hexdigest() + '.html')
            if os.path.exists(fn):
                h = open(fn, encoding='utf-8', errors='ignore').read()
            else:
                r = E.get(f'https://web.archive.org/web/{ts}id_/https://www.{p}')
                if r is None:
                    continue
                h = r.text
                open(fn, 'w', encoding='utf-8').write(h)
            txt = E.text_of(h)
            nav, body = E.split_nav_body(txt)
            owned = E.owned_hits(body)
            disc = sorted(set(m.group(0) for m in E.DISC.finditer(body)))
            out.append({'page': p, 'ts': ts, 'date': f'{ts[:4]}-{ts[4:6]}-{ts[6:8]}', 'n_owned_brands_named': len(owned),
                        'owned_brands': '|'.join(owned), 'discount_phrases': '|'.join(disc[:15]), 'body_excerpt': body[:1500]})
            print(ts, len(owned), owned)
    with open(os.path.join(E.BASE, 'E1_exclusive_brands_hub_history.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()) if out else ['page']); w.writeheader(); w.writerows(out)


if __name__ == '__main__':
    main()
