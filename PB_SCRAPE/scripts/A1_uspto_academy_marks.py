"""A1: list USPTO trademarks owned by Academy, Ltd. (Academy Sports + Outdoors) to classify ASO private-label brands
on the academy.com Bazaarvoice catalog. Same public tmsearch JSON endpoint as X05 (no login/key).
RERUN: python A1_uspto_academy_marks.py  -> raw/A1_uspto_academy_marks.csv
"""
import csv, json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from X05_uspto_tm_pull import query, BASE

OWNERS = ['"academy, ltd"', '"academy ltd"', '"academy sports"']


def main():
    recs = {}
    for o in OWNERS:
        start = 0
        while True:
            j = query(o, start)
            hits = j['hits']['hits']; tot = j['hits']['totalValue']
            for h in hits:
                recs.setdefault(h['source']['id'], h['source'])
            start += len(hits)
            print(o, tot, start)
            if not hits or start >= tot:
                break
            time.sleep(1)
    cols = ['id', 'wordmark', 'filedDate', 'registrationDate', 'alive', 'statusDescription', 'internationalClass',
            'firstUseCommerceDate', 'ownerName', 'goodsAndServices']
    with open(os.path.join(BASE, 'A1_uspto_academy_marks.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(cols)
        for s in sorted(recs.values(), key=lambda x: x.get('filedDate') or ''):
            w.writerow([' | '.join(map(str, s.get(c))) if isinstance(s.get(c), list) else s.get(c) for c in cols])
    print('records', len(recs))


if __name__ == '__main__':
    main()
