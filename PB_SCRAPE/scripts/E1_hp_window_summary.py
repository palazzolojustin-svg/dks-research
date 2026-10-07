"""E1: per-snapshot owned-brand share-of-voice on the dicks.com homepage (Wayback cache), summarised by comparable windows.
Per snapshot: owned FEATURE mentions (owned brand named outside any discount phrase), owned DISCOUNT phrases, all discount
phrases, national-brand mentions, distinct owned brands named. Averages per snapshot by window.

Rerun: python E1_hp_window_summary.py   (after E1_wayback_promo_census.py)
Output: raw/E1_hp_per_snapshot_<tag>.csv, raw/E1_hp_window_summary_<tag>.csv
"""
import os, re, sys, csv, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import E1_wayback_promo_census as E
import E1_hp_offer_phrases as P

NAT = re.compile(r"\b(Nike|Jordan|adidas|Under Armour|New Balance|HOKA|On Cloud\w*|YETI|The North Face|TaylorMade|Callaway|Titleist|BIRKENSTOCK|Vuori|Carhartt|Stanley|Brooks|UGG|Crocs|Patagonia|Columbia)\b")
WINDOWS = [('2024 Feb-Jun', '2024-02', '2024-06'), ('2026 Feb-Jun', '2026-02', '2026-06'),
           ('2024 Jan-Jul (all 2024)', '2024-01', '2024-07'), ('2025 Jul-Dec', '2025-07', '2025-12'),
           ('2026 Jan-Jun', '2026-01', '2026-06')]


def main(target='dickssportinggoods.com/'):
    tag = re.sub(r'\W+', '_', target).strip('_')
    rows = [l.split() for l in open(os.path.join(E.BASE, f'E1_cdx_{tag}.txt')).read().strip().splitlines() if l and l[0].isdigit()]
    out = []
    for row in rows:
        ts = row[0]
        cf = os.path.join(E.CACHE, hashlib.md5((target + ts).encode()).hexdigest() + '.html')
        if not os.path.exists(cf) or os.path.getsize(cf) < 15000:
            continue
        body = P.body_of(E.text_of(open(cf, encoding='utf-8', errors='ignore').read()))
        if len(body) < 500:
            continue
        ph = P.phrases(body)
        feats = [o for o in ph if o['kind'] == 'feature']
        disc = [o for o in ph if o['kind'] == 'discount']
        odisc = [o for o in ph if o['kind'] in ('discount', 'pricepoint') and o['owned']]
        brands = set(x for o in ph for x in o['owned'].split('|') if x and x != 'Exclusive Brands')
        out.append({'ts': ts, 'month': f'{ts[:4]}-{ts[4:6]}', 'body_chars': len(body), 'owned_feature_mentions': len(feats),
                    'owned_discount_phrases': len(odisc), 'all_discount_phrases': len(disc),
                    'national_mentions': len(NAT.findall(body)), 'distinct_owned_brands': len(brands),
                    'owned_brands': '|'.join(sorted(brands))})
    with open(os.path.join(E.BASE, f'E1_hp_per_snapshot_{tag}.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    summ = []
    for name, a, b in WINDOWS:
        s = [r for r in out if a <= r['month'] <= b]
        if not s:
            continue
        n = len(s)
        avg = lambda k: round(sum(r[k] for r in s) / n, 2)
        tot_feat = sum(r['owned_feature_mentions'] for r in s)
        tot_nat = sum(r['national_mentions'] for r in s)
        summ.append({'window': name, 'snapshots': n, 'avg_owned_feature_mentions': avg('owned_feature_mentions'),
                     'avg_owned_discount_phrases': avg('owned_discount_phrases'), 'avg_all_discount_phrases': avg('all_discount_phrases'),
                     'owned_share_of_discount_phrases': round(sum(r['owned_discount_phrases'] for r in s) / max(1, sum(r['all_discount_phrases'] for r in s)), 3),
                     'avg_national_mentions': avg('national_mentions'),
                     'owned_feature_per_100_national': round(100 * tot_feat / max(1, tot_nat), 1),
                     'avg_distinct_owned_brands': avg('distinct_owned_brands'),
                     'pct_snapshots_with_owned_feature': round(sum(1 for r in s if r['owned_feature_mentions']) / n, 2),
                     'pct_snapshots_with_owned_discount': round(sum(1 for r in s if r['owned_discount_phrases']) / n, 2),
                     'avg_body_chars': avg('body_chars')})
    with open(os.path.join(E.BASE, f'E1_hp_window_summary_{tag}.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(summ[0].keys())); w.writeheader(); w.writerows(summ)
    for r in summ:
        print(r)


if __name__ == '__main__':
    main(*(sys.argv[1:] or []))

