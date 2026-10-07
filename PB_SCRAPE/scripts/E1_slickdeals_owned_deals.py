"""E1: Dated owned-brand deal posts at DICK'S / Golf Galaxy from Slickdeals public search pages (first page per query only;
robots.txt disallows *page=* so no pagination). Each card gives: thread id, title, post timestamp, final price, list price,
% off, store, vote count. Many narrow queries (brand x product word) are unioned to widen coverage.

Rerun:  python E1_slickdeals_owned_deals.py          (≈2 s per query; ~150 queries ≈ 6-8 min)
Weekly routine: rerun; the union file is de-duplicated on thread id, so it accumulates history across runs.
Outputs: PB_SCRAPE/raw/E1_slickdeals_owned_deals.csv (cumulative), E1_slickdeals_monthly.csv
"""
import requests, re, time, csv, os, html, datetime
from collections import defaultdict

H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'}
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
OUT = os.path.join(BASE, 'E1_slickdeals_owned_deals.csv')
BRANDS = {
    'CALIA': ['calia', 'calia legging', 'calia leggings', 'calia skort', 'calia jogger', 'calia joggers', 'calia pants', 'calia jacket',
              'calia bra', 'calia hoodie', 'calia shorts', 'calia swim', 'calia tank', 'calia shirt', 'calia dress', 'calia golf',
              'calia fleece', 'calia pullover', 'calia bag', 'calia hat', 'calia women', 'calia sweater', 'calia vest', 'calia carrie underwood',
              'calia new balance', 'calia stanley', 'calia tee', 'calia quarter zip', 'calia skirt', 'calia crop'],
    'VRST': ['vrst', 'vrst shorts', 'vrst pants', 'vrst jogger', 'vrst hoodie', 'vrst shirt', 'vrst jacket', 'vrst polo', 'vrst men',
             'vrst tee', 'vrst limitless', 'vrst quarter zip', 'vrst fleece'],
    'DSG': ['dsg', 'dsg shorts', 'dsg pants', 'dsg jogger', 'dsg hoodie', 'dsg shirt', 'dsg jacket', 'dsg kids', 'dsg women', 'dsg men',
            'dsg fleece', 'dsg tee', 'dsg chair', 'dsg cleats', 'dsg bag', 'dsg softball', 'dsg baseball', 'dsg glove', 'dsg soccer',
            'dsg legging', 'dsg puffer', 'dsg cooler', 'dsg sweatshirt'],
    'Maxfli': ['maxfli', 'maxfli golf balls', 'maxfli tour', 'maxfli softfli', 'maxfli straightfli', 'maxfli tour x', 'maxfli bag'],
    'Walter Hagen': ['walter hagen', 'walter hagen polo', 'walter hagen shorts', 'walter hagen pants', 'walter hagen golf'],
    'Alpine Design': ['alpine design', 'alpine design jacket', 'alpine design tent', 'alpine design fleece', 'alpine design puffer'],
    'Top Flite': ['top flite', 'top flite golf', 'top flite golf balls', 'top flite set'],
    'Tommy Armour': ['tommy armour', 'tommy armour golf', 'tommy armour putter', 'tommy armour driver'],
    'Nishiki': ['nishiki', 'nishiki bike'],
    'Fitness Gear': ['fitness gear', 'fitness gear dumbbell', 'fitness gear bench', 'fitness gear weight'],
    'ETHOS': ['ethos', 'ethos dumbbell', 'ethos bench', 'ethos kettlebell', 'ethos rack', 'ethos treadmill'],
    'Quest': ['quest canopy', 'quest tent', 'quest chair', 'quest kayak'],
    'Field & Stream': ['field & stream', 'field and stream'],
}
CARD = re.compile(r'data-threadid="(\d+)" data-store-id="(\d*)".*?data-qa="deal-card-title" title="([^"]*)".*?'
                  r'data-qa="deal-card-timestamp"[^>]*>([^<]+)<(.*?)(?=data-qa="deal-card-list"|$)', re.S)


def parse(page):
    out = []
    for tid, store, title, ts, rest in CARD.findall(page):
        fp = re.search(r'data-qa="deal-card-price" title="([^"]*)"', rest)
        lp = re.search(r'data-qa="deal-card-original-price" title="([^"]*)"', rest)
        sv = re.search(r'data-qa="deal-card-savings"[^>]*>([^<]*)<', rest)
        st = re.search(r'data-qa="deal-card-store"[^>]*>([^<]*)<', rest)
        vc = re.search(r'data-qa="deal-card-vote-count"[^>]*>([^<]*)<', rest)
        out.append({'thread_id': tid, 'store_id': store, 'store': html.unescape(st.group(1)) if st else '',
                    'title': html.unescape(title), 'posted': ts.strip(),
                    'final_price': fp.group(1) if fp else '', 'list_price': lp.group(1) if lp else '',
                    'savings': sv.group(1).strip() if sv else '', 'votes': vc.group(1).strip() if vc else ''})
    return out


def to_date(s):
    for fmt in ('%b %d, %Y %I:%M %p', '%b %d, %Y'):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def main():
    seen = {}
    if os.path.exists(OUT):
        for r in csv.DictReader(open(OUT, encoding='utf-8')):
            seen[r['thread_id']] = r
    for brand, qs in BRANDS.items():
        for q in qs:
            cards = []
            for attempt in range(5):
                try:
                    r = requests.get('https://slickdeals.net/newsearch.php', params={'q': q, 'searcharea': 'deals', 'searchin': 'first'},
                                     headers=H, timeout=60)
                    cards = parse(r.text)
                    break
                except Exception as e:
                    print('retry', q, str(e)[:60]); time.sleep(6 * (attempt + 1))
            n_new = 0
            bl = brand.lower().replace(' & ', ' ').split()[0]
            for c in cards:
                if bl not in c['title'].lower().replace('&', ''):   # keep only titles that name the brand
                    continue
                c['brand'] = brand; c['query'] = q
                if c['thread_id'] not in seen:
                    n_new += 1
                seen[c['thread_id']] = c
            print(brand, q, len(cards), 'new', n_new)
            time.sleep(2)
    keys = ['thread_id', 'brand', 'query', 'store_id', 'store', 'title', 'posted', 'final_price', 'list_price', 'savings', 'votes']
    rows = sorted(seen.values(), key=lambda x: (to_date(x['posted']) or datetime.date(1900, 1, 1)))
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore'); w.writeheader(); w.writerows(rows)
    print('total unique', len(rows))


if __name__ == '__main__':
    main()
