"""H02: build the HoS/FH census and proximity analysis.
Inputs : raw/H02_store_pages.json (locator scrape), raw/H02_pipeline_input.csv (hand-built pipeline list)
Outputs: raw/H02_census.csv (open HoS from locator + pipeline sites, with nearest legacy DSG store and distance)
         raw/H02_geocode_cache.json
Method : pipeline sites geocoded with OSM Nominatim (public API, 1 req/s, custom UA); haversine distance to every
         DICK'S Sporting Goods-branded locator page (excludes HoS pages, GGG outlets, pre-open pages).
Rerun  : python H02_census_distance.py
"""
import json, csv, math, os, time, requests

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, 'raw')
R = json.load(open(os.path.join(RAW, 'H02_store_pages.json'), encoding='utf8'))
cache_p = os.path.join(RAW, 'H02_geocode_cache.json')
cache = json.load(open(cache_p, encoding='utf8')) if os.path.exists(cache_p) else {}


def hav(a, b, c, d):
    a, b, c, d = map(math.radians, (a, b, c, d))
    h = math.sin((c - a) / 2) ** 2 + math.cos(a) * math.cos(c) * math.sin((d - b) / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(h))


def geocode(q):
    if q in cache:
        return cache[q]
    r = requests.get('https://nominatim.openstreetmap.org/search', params={'q': q, 'format': 'json', 'limit': 1, 'countrycodes': 'us'},
                     headers={'User-Agent': 'DKS-research-H02/1.0 (personal research)'}, timeout=30)
    time.sleep(1.2)
    js = r.json() if r.status_code == 200 else []
    cache[q] = [float(js[0]['lat']), float(js[0]['lon']), js[0].get('display_name', '')] if js else None
    json.dump(cache, open(cache_p, 'w', encoding='utf8'), indent=1)
    return cache[q]


legacy = [r for r in R if r.get('latitude') and "Sporting Goods" in (r.get('ld_name') or '') and 'GOING' not in (r.get('title') or '')]
hos = [r for r in R if 'House of Sport' in (r.get('ld_name') or '')]
print('legacy DSG pages', len(legacy), 'HoS pages', len(hos))


def nearest(lat, lon, exclude=None):
    best = []
    for s in legacy:
        if exclude and s['storeno'] == exclude:
            continue
        d = hav(lat, lon, float(s['latitude']), float(s['longitude']))
        best.append((d, s))
    best.sort(key=lambda x: x[0])
    return best[:2]


rows = []
for h in hos:
    lat, lon = float(h['latitude']), float(h['longitude'])
    nb = nearest(lat, lon)
    rows.append({'site_id': 'OPEN-' + h['storeno'], 'format': 'HoS', 'status': 'open (locator 2026-10-07)', 'center': '', 'city': h['city'], 'state': h['state'],
                 'storeno': h['storeno'], 'lat': lat, 'lon': lon, 'expected_open': '', 'fy_bucket': '',
                 'nearest_dsg': f"#{nb[0][1]['storeno']} {nb[0][1]['city']}", 'nearest_dsg_mi': round(nb[0][0], 1),
                 'second_dsg': f"#{nb[1][1]['storeno']} {nb[1][1]['city']}", 'second_dsg_mi': round(nb[1][0], 1)})
for p in csv.DictReader(open(os.path.join(RAW, 'H02_pipeline_input.csv'), encoding='utf8')):
    g = geocode(p['geocode_query'])
    rec = {'site_id': p['site_id'], 'format': p['format'], 'status': p['status_2026_10_07'], 'center': p['center'], 'city': p['city'],
           'state': p['state'], 'storeno': '', 'expected_open': p['expected_open_reported'], 'fy_bucket': p['fy_bucket'],
           'same_center_dsg': p['existing_dsg_storeno_same_center']}
    if g:
        rec['lat'], rec['lon'] = g[0], g[1]
        nb = nearest(g[0], g[1])
        rec.update({'nearest_dsg': f"#{nb[0][1]['storeno']} {nb[0][1]['city']}", 'nearest_dsg_mi': round(nb[0][0], 1),
                    'second_dsg': f"#{nb[1][1]['storeno']} {nb[1][1]['city']}", 'second_dsg_mi': round(nb[1][0], 1), 'geocoded_as': g[2][:80]})
    rows.append(rec)
keys = ['site_id', 'format', 'status', 'center', 'city', 'state', 'storeno', 'expected_open', 'fy_bucket', 'same_center_dsg',
        'nearest_dsg', 'nearest_dsg_mi', 'second_dsg', 'second_dsg_mi', 'lat', 'lon', 'geocoded_as']
with open(os.path.join(RAW, 'H02_census.csv'), 'w', newline='', encoding='utf8') as f:
    w = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
    w.writeheader()
    w.writerows(rows)
print('rows', len(rows))
