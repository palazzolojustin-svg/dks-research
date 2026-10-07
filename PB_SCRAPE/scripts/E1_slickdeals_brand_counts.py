"""E1: Slickdeals community deal-post counts for DKS owned brands (store = Dick's Sporting Goods, id 389; Golf Galaxy 5073).

Slickdeals is a public crowd-sourced deal site: a post means a shopper found the item at a notable discount. Counts per
date window (past 30/90/365/1095 days, all time) are read from the server-rendered store facet on the public search page,
so no pagination is used (robots.txt disallows *page=*). The newest-25 RSS feed gives exact dated items.

Rerun:  python E1_slickdeals_brand_counts.py
Weekly routine: rerun every Monday; append the output CSV to a running log and track the 30d and 90d counts per brand
(a rising 90d count vs the 365d/4 run-rate = more owned-brand deal activity; read together with the price level of posts).
Output: PB_SCRAPE/raw/E1_slickdeals_counts_<YYYYMMDD>.csv, E1_slickdeals_rss_<brand>.xml
"""
import requests, re, time, csv, os, datetime, html

H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'}
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
QUERIES = ['calia', 'vrst', 'dsg', 'maxfli', 'walter hagen', 'alpine design', 'nishiki', 'fitness gear', 'top flite',
           'tommy armour', 'ethos', 'quest', 'slazenger',
           # national-brand controls at the same store
           'nike', 'under armour', 'adidas', 'new balance', 'hoka', 'yeti', 'callaway', 'taylormade', 'lululemon']
WINDOWS = ['30', '90', '365', '1095', '-1']
STORES = {'389': "Dick's Sporting Goods", '5073': 'Golf Galaxy'}


def facet_counts(q, window):
    url = 'https://slickdeals.net/newsearch.php'
    params = {'q': q, 'searcharea': 'deals', 'searchin': 'first', 'filters[date][]': window}
    for i in range(4):
        try:
            r = requests.get(url, params=params, headers=H, timeout=60)
            if r.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(5 * (i + 1))
    else:
        return {}
    out = {}
    for sid in STORES:
        m = re.search(r'name="filters\[store\]\[\]" value="%s"[^>]*><span[^>]*>[^<]*<span[^>]*>\((\d+)\)' % sid, r.text)
        out[sid] = int(m.group(1)) if m else 0
    return out


def rss(q):
    r = requests.get('https://slickdeals.net/newsearch.php', params={'q': q, 'searcharea': 'deals', 'searchin': 'first', 'rss': '1'},
                     headers=H, timeout=60)
    open(os.path.join(BASE, 'E1_slickdeals_rss_%s.xml' % q.replace(' ', '_')), 'w', encoding='utf-8').write(r.text)
    items = re.findall(r'<item>.*?<title>(.*?)</title>.*?<pubDate>(.*?)</pubDate>', r.text, re.S)
    return [(html.unescape(t), d) for t, d in items]


def main():
    today = datetime.date.today().strftime('%Y%m%d')
    rows = []
    for q in QUERIES:
        row = {'query': q, 'run_date': today}
        for w in WINDOWS:
            c = facet_counts(q, w)
            row['dks_' + w] = c.get('389', '')
            row['gg_' + w] = c.get('5073', '')
            time.sleep(2)
        print(row)
        rows.append(row)
    keys = ['query', 'run_date'] + ['dks_' + w for w in WINDOWS] + ['gg_' + w for w in WINDOWS]
    with open(os.path.join(BASE, 'E1_slickdeals_counts_%s.csv' % today), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    for q in ['calia', 'vrst', 'dsg', 'maxfli', 'walter hagen', 'alpine design']:
        items = rss(q)
        print(q, len(items), items[:3], items[-1:] if items else '')
        time.sleep(2)


if __name__ == '__main__':
    main()
