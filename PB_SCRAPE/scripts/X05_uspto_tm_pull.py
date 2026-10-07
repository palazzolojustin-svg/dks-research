"""X05: Pull every USPTO trademark record owned by DKS entities from the public tmsearch.uspto.gov backend.

How to rerun (weekly):  python X05_uspto_tm_pull.py
Outputs:
  PB_SCRAPE/raw/X05_uspto_dks_marks.csv   (one row per serial number, deduped)
  PB_SCRAPE/raw/X05_uspto_dks_marks.json  (full raw records)
Method: POST Elasticsearch-style query to https://tmsearch.uspto.gov/prod-stage-v1-0-0/tmsearch
(the same JSON endpoint the public tmsearch web app calls; no login, no key).
Owners queried: American Sports Licensing (DKS IP-holding subsidiary, Inc. and LLC), Dick's Sporting Goods, Inc.,
Dick's Clothing and Sporting Goods, Golf Galaxy, Galyan's, Moosejaw (DKS-owned 2019-2024), plus Foot Locker owners
are NOT included (out of scope). Diff the CSV against the previous run to spot new filings (filedDate) each week.
"""
import csv, json, os, time
import requests

U = 'https://tmsearch.uspto.gov/prod-stage-v1-0-0/tmsearch'
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36',
     'Content-Type': 'application/json', 'Origin': 'https://tmsearch.uspto.gov',
     'Referer': 'https://tmsearch.uspto.gov/search/search-results'}
OWNERS = ['"american sports licensing"', '"dick\'s sporting goods"', '"dicks sporting goods"',
          '"dick\'s clothing"', '"golf galaxy"', '"galyan\'s"', '"moosejaw"']
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')


def query(qs, start, size=500):
    body = {"query": {"bool": {"must": [{"bool": {"should": [
        {"query_string": {"query": qs, "default_operator": "AND", "fields": ["ownerName", "ownerFullText"]}}]}}]}},
        "size": size, "from": start, "track_total_hits": True}
    r = requests.post(U, headers=H, data=json.dumps(body), timeout=90)
    r.raise_for_status()
    return r.json()


def main():
    recs = {}
    for o in OWNERS:
        start = 0
        while True:
            j = query(o, start)
            hits = j['hits']['hits']
            tot = j['hits']['totalValue']
            for h in hits:
                s = h['source']
                s['_ownerQuery'] = o
                recs.setdefault(s['id'], s)
            print(o, 'total', tot, 'got', start + len(hits))
            start += len(hits)
            if not hits or start >= tot:
                break
            time.sleep(1)
    with open(os.path.join(BASE, 'X05_uspto_dks_marks.json'), 'w', encoding='utf-8') as f:
        json.dump(list(recs.values()), f)
    cols = ['id', 'wordmark', 'filedDate', 'registrationDate', 'registrationId', 'alive', 'statusDescription',
            'abandonDate', 'cancelDate', 'currentBasis', 'originalBasis', 'internationalClass', 'firstUseAnyDate',
            'firstUseCommerceDate', 'publishForOppositionDate', 'drawingCodeDescription', 'markDescription',
            'ownerName', 'ownerType', 'attorney', 'goodsAndServices', '_ownerQuery']
    with open(os.path.join(BASE, 'X05_uspto_dks_marks.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(cols)
        for s in sorted(recs.values(), key=lambda x: x.get('filedDate') or ''):
            row = []
            for c in cols:
                v = s.get(c)
                if isinstance(v, list):
                    v = ' | '.join(str(x) for x in v)
                row.append(v)
            w.writerow(row)
    print('records', len(recs))


if __name__ == '__main__':
    main()
