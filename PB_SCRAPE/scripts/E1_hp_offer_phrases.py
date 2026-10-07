"""E1: Offer-phrase analysis of cached Wayback homepage snapshots (run E1_wayback_promo_census.py first to fill the cache).

For each snapshot: strip the mega-menu (nav) and footer, then
  * discount offers  = every "N% Off ..." / "$N Off ..." phrase (offer + next 90 chars, cut at the next offer);
    owned if an owned brand is named inside the phrase
  * owned features   = owned-brand mentions (±70 chars) that are NOT inside a discount phrase (launches, collections,
    "Only at DICK'S", collabs)
Phrases are de-duplicated within each calendar month (a promo that stays up for 10 days counts once).

Rerun: python E1_hp_offer_phrases.py [target=dickssportinggoods.com/]
Outputs: raw/E1_hp_offers_<tag>.csv (distinct phrases by month) and raw/E1_hp_offers_monthly_<tag>.csv
"""
import os, re, sys, csv, hashlib
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import E1_wayback_promo_census as E

OFFER = re.compile(r"(?:Up to |Extra |Save |Plus,? |Plus up to )?(?:\d{1,2}% Off|\$\d{1,4} Off|BOGO|Buy One,? Get One)", re.I)
PRICEPT = re.compile(r"\$\d{1,3}\.\d{2}")   # promo price points like "$9.98 DSG Men's Rec Short"


def body_of(txt):
    i = txt.find('Get the Latest Launches')
    if i >= 0:
        j = txt.rfind(' Close ', 0, i)
        start = j + 7 if j >= 0 else i
    else:
        j = txt.find(' Close ')
        start = j + 7 if 0 <= j < 0.7 * len(txt) else 0
    end = len(txt)
    for f in E.FOOTER:
        k = txt.find(f, start)
        if k >= 0:
            end = min(end, k)
    return txt[start:end]


def phrases(body):
    offers = []
    ms = list(OFFER.finditer(body))
    spans = []
    for n, m in enumerate(ms):
        st = max(0, m.start() - 25)
        en = min(len(body), m.end() + 90)
        if n + 1 < len(ms):
            en = min(en, ms[n + 1].start())
        ph = body[st:en]
        spans.append((st, en))
        pct = re.search(r"(\d{1,2})%", m.group(0))
        offers.append({'kind': 'discount', 'text': ph.strip(), 'owned': '|'.join(E.owned_hits(ph)),
                       'pct': int(pct.group(1)) if pct else ''})
    # promo price points ("$9.98 DSG Men's Rec Short") -> discount-type if owned brand within 40 chars after
    for m in PRICEPT.finditer(body):
        ph = body[m.start():m.end() + 45]
        if any(a <= m.start() < b for a, b in spans):
            continue
        oh = E.owned_hits(ph)
        if oh:
            offers.append({'kind': 'pricepoint', 'text': ph.strip(), 'owned': '|'.join(oh), 'pct': ''})
            spans.append((m.start(), m.end() + 45))
    for name, rx in E.OWNED:
        if name == 'Exclusive Brands':
            continue
        for m in rx.finditer(body):
            if any(a <= m.start() < b for a, b in spans):
                continue
            ph = body[max(0, m.start() - 70):m.end() + 70]
            offers.append({'kind': 'feature', 'text': ph.strip(), 'owned': name, 'pct': ''})
    return offers


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"\d{1,2}/\d{1,2}(/\d{2,4})?", "", s.lower()))[:120]


def main(target='dickssportinggoods.com/'):
    tag = re.sub(r'\W+', '_', target).strip('_')
    fn = os.path.join(E.BASE, f'E1_cdx_{tag}.txt')
    rows = [l.split() for l in open(fn).read().strip().splitlines() if l and l[0].isdigit()]
    month = defaultdict(dict)
    snaps = defaultdict(int)
    for row in rows:
        ts = row[0]
        cf = os.path.join(E.CACHE, hashlib.md5((target + ts).encode()).hexdigest() + '.html')
        if not os.path.exists(cf) or os.path.getsize(cf) < 15000:
            continue
        body = body_of(E.text_of(open(cf, encoding='utf-8', errors='ignore').read()))
        if len(body) < 500:
            continue
        mk = f'{ts[:4]}-{ts[4:6]}'
        snaps[mk] += 1
        for o in phrases(body):
            k = (o['kind'], norm(o['text']))
            if k not in month[mk]:
                o['first_seen'] = f'{ts[:4]}-{ts[4:6]}-{ts[6:8]}'
                month[mk][k] = o
    out = []
    for mk in sorted(month):
        for o in month[mk].values():
            out.append(dict(month=mk, **o))
    with open(os.path.join(E.BASE, f'E1_hp_offers_{tag}.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['month', 'first_seen', 'kind', 'owned', 'pct', 'text']); w.writeheader(); w.writerows(out)
    with open(os.path.join(E.BASE, f'E1_hp_offers_monthly_{tag}.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['month', 'snapshots', 'distinct_discount_offers', 'owned_discount_offers', 'owned_share_of_discount_offers',
                    'owned_disc_avg_pct', 'all_disc_avg_pct', 'owned_feature_mentions', 'owned_brands_featured'])
        for mk in sorted(month):
            v = list(month[mk].values())
            d = [o for o in v if o['kind'] == 'discount']
            od = [o for o in v if o['kind'] in ('discount', 'pricepoint') and o['owned']]
            fe = [o for o in v if o['kind'] == 'feature']
            op = [o['pct'] for o in od if o['pct'] != '']
            ap = [o['pct'] for o in d if o['pct'] != '']
            w.writerow([mk, snaps[mk], len(d), len(od), round(len(od) / max(1, len(d) + len([o for o in od if o['kind'] == 'pricepoint'])), 3),
                        round(sum(op) / len(op), 1) if op else '', round(sum(ap) / len(ap), 1) if ap else '', len(fe),
                        '|'.join(sorted(set(x for o in fe for x in o['owned'].split('|') if x)))])
    print('months', len(month))


if __name__ == '__main__':
    main(*(sys.argv[1:] or []))
