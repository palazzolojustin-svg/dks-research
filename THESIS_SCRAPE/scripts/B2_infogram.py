"""B2: fetch the public Infogram embeds behind Placer.ai Anchor charts and extract the underlying chart data.
Placer articles embed charts as <div class="infogram-embed" data-id="_/XXXX">. The public page
https://e.infogram.com/_/XXXX contains window.infographicData (JSON) with the chart's data tables.
Usage: python B2_infogram.py <infogram_id> [<infogram_id> ...]   (ids like _/72A31xFGvsqPoRdDQY0U)
Writes raw/B2_infogram/<id>.json (full JSON) and prints every data table found.
"""
import requests, re, json, os, sys, time
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'raw', 'B2_infogram')
os.makedirs(OUT, exist_ok=True)
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}


def extract(t):
    m = re.search(r'window\.infographicData\s*=\s*(\{.*?\});\s*</script>', t, re.S)
    if not m:
        return None
    return json.loads(m.group(1))


def tables(obj, path=''):
    """yield (path, data) for every 'data' list-of-lists-of-lists found"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'data' and isinstance(v, list) and v and isinstance(v[0], list):
                yield path + '/' + k, v
            else:
                yield from tables(v, path + '/' + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from tables(v, path + f'[{i}]')


def cell(c):
    if isinstance(c, dict):
        return str(c.get('value', ''))
    return str(c) if c is not None else ''


def fetch(iid):
    iid = iid.strip()
    if not iid.startswith('_/'):
        iid = '_/' + iid
    url = 'https://e.infogram.com/' + iid
    r = requests.get(url, headers=H, timeout=60)
    d = extract(r.text)
    fn = os.path.join(OUT, iid.replace('_/', '') + '.json')
    if d is None:
        print('NO DATA', url, r.status_code, len(r.text))
        open(fn.replace('.json', '.html'), 'w', encoding='utf-8').write(r.text)
        return None
    json.dump(d, open(fn, 'w', encoding='utf-8'), indent=1)
    title = ''
    m = re.search(r'<title>([^<]*)</title>', r.text)
    if m:
        title = m.group(1)
    print('=====', iid, '|', title)
    for p, tb in tables(d):
        for sheet in tb:
            if not isinstance(sheet, list):
                continue
            rows = [[cell(c) for c in row] for row in sheet if isinstance(row, list)]
            rows = [r_ for r_ in rows if any(x for x in r_)]
            if rows:
                print('  --', p)
                for r_ in rows[:80]:
                    print('    ', ' | '.join(r_))
    return d


if __name__ == '__main__':
    for a in sys.argv[1:]:
        try:
            fetch(a)
        except Exception as e:
            print('ERR', a, e)
        time.sleep(1.5)
