"""E1: Owned-brand share-of-voice census on DKS / Golf Galaxy homepages (and other promo pages) from Wayback Machine snapshots.

Why: milled.com (DKS email archive) sits behind a Cloudflare JS challenge (HTTP 403 "Just a moment...") for scripts, so the
homepage promo grid (which mirrors the weekly email hero offers: flash sales, "x% off select CALIA", etc.) is used as the
repeatable proxy for "what DKS is marketing and discounting".

Rerun:
    python E1_wayback_promo_census.py                  # default targets, 2024-01 -> today
    python E1_wayback_promo_census.py golfgalaxy.com/  # one target
Weekly human routine: rerun; it only fetches snapshots not already in raw/E1_wb_cache/. Optionally save a fresh
homepage capture first via https://web.archive.org/save/https://www.dickssportinggoods.com/ (manual, in a browser).

Outputs (PB_SCRAPE/raw):
    E1_hp_tiles_<target>.csv     one row per promo tile per snapshot (tile text, owned-brand hits, discount %)
    E1_hp_snapshots_<target>.csv one row per snapshot (counts, owned-brand tile share, nav 'Brands We Love' owned count)
    E1_hp_monthly_<target>.csv   monthly aggregates
"""
import requests, time, re, os, sys, csv, hashlib, statistics
from collections import defaultdict
from bs4 import BeautifulSoup

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
CACHE = os.path.join(BASE, 'E1_wb_cache')
os.makedirs(CACHE, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (research; E1 wayback census)'}

# owned-brand patterns (case-sensitive where the token is also an English word)
OWNED = [
    ('CALIA', re.compile(r'\bCALIA\b|\bCalia\b')),
    ('VRST', re.compile(r'\bVRST\b')),
    ('DSG', re.compile(r'\bDSG\b')),
    ('Maxfli', re.compile(r'\bMaxfli\b|\bMAXFLI\b', re.I)),
    ('Walter Hagen', re.compile(r'\bWalter Hagen\b', re.I)),
    ('Top Flite', re.compile(r'\bTop[- ]?Flite\b', re.I)),
    ('Tommy Armour', re.compile(r'\bTommy Armour\b', re.I)),
    ('Alpine Design', re.compile(r'\bAlpine Design\b', re.I)),
    ('ETHOS', re.compile(r'\bETHOS\b')),
    ('Fitness Gear', re.compile(r'\bFitness Gear\b', re.I)),
    ('Nishiki', re.compile(r'\bNishiki\b', re.I)),
    ('Quest', re.compile(r'\bQuest\b')),
    ('Slazenger', re.compile(r'\bSlazenger\b', re.I)),
    ('TourTrek', re.compile(r'\bTour ?Trek\b', re.I)),
    ('PRIMED', re.compile(r'\bPRIMED\b')),
    ('P-TEX', re.compile(r'\bP-TEX\b', re.I)),
    ('DBX', re.compile(r'\bDBX\b')),
    ('Jawbone', re.compile(r'\bJawbone\b')),
    ('Field & Stream', re.compile(r'\bField (&|and) Stream\b', re.I)),
    ('Exclusive Brands', re.compile(r'\b(exclusive|vertical|our own|our) brands\b', re.I)),
]
NATIONAL = re.compile(r'\b(Nike|Jordan|adidas|Under Armour|UA|New Balance|HOKA|On|YETI|The North Face|TaylorMade|Callaway|Titleist|BIRKENSTOCK|Vuori|Carhartt|Stanley)\b')
DISC = re.compile(r'(?:up to |extra |save )?(\d{1,2})% off|\$(\d{2,4}) off', re.I)
CTA = re.compile(r"\b(Shop Now|SHOP NOW|Learn More|LEARN MORE|Explore Now|Preorder Now|Download Now|Shop Deals|SHOP DEALS|Shop Clearance|SHOP CLEARANCE|Shop All[\w' &]*?(?= )|Shop Gifts|SHOP GIFTS)\b")
FOOTER = ['Elevate Your Game with Expert Advice', 'Get It Fast!', 'Best Price Guarantee If You Find', 'CONNECT WITH US', 'Need More Help?', 'Download the DICK\'S App']
DEFAULT_TARGETS = ['dickssportinggoods.com/', 'golfgalaxy.com/']


def get(url, params=None, tries=8, timeout=120):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=timeout)
            if 'Temporarily Offline' in r.text[:3000] or r.status_code in (429, 502, 503, 504):
                raise Exception('IA offline/%s' % r.status_code)
            return r
        except Exception as e:
            time.sleep(min(60, 8 * (i + 1)))
    return None


def cdx(target, frm='2024', to='2026'):
    fn = os.path.join(BASE, 'E1_cdx_' + re.sub(r'\W+', '_', target).strip('_') + '.txt')
    rows = []
    for attempt in range(6):
        r = get('https://web.archive.org/cdx/search/cdx', {'url': target, 'from': frm, 'to': to, 'output': 'txt',
                'fl': 'timestamp,statuscode,length', 'collapse': 'timestamp:8', 'filter': 'statuscode:200'}, timeout=180)
        if r is not None:
            rows = [l.split() for l in r.text.strip().splitlines() if l and l[0].isdigit()]
            if rows:
                open(fn, 'w').write(r.text)
                return rows
        time.sleep(30)
    if os.path.exists(fn):   # fall back to last saved CDX listing
        return [l.split() for l in open(fn).read().strip().splitlines() if l and l[0].isdigit()]
    return rows


def snap(target, ts):
    fn = os.path.join(CACHE, hashlib.md5((target + ts).encode()).hexdigest() + '.html')
    if os.path.exists(fn):
        return open(fn, encoding='utf-8', errors='ignore').read()
    if os.environ.get('E1_CACHE_ONLY'):
        return None
    r = get(f'https://web.archive.org/web/{ts}id_/https://www.{target}')
    if r is None:
        return None
    open(fn, 'w', encoding='utf-8').write(r.text)
    time.sleep(1.5)
    return r.text


def text_of(html):
    s = BeautifulSoup(html, 'html.parser')
    for t in s(['script', 'style', 'noscript']):
        t.decompose()
    return s.get_text(' ', strip=True)


def split_nav_body(txt):
    # nav = mega menu; body starts after the first ' Close ' following the menu (DKS) else after 'Brands We Love'
    start = 0
    for mk in ['Brands We Love', 'Featured Shops', 'Shop by Brand']:
        i = txt.find(mk)
        if i >= 0:
            j = txt.find(' Close ', i)
            start = j + 7 if j >= 0 else i
            break
    end = len(txt)
    for f in FOOTER:
        k = txt.find(f, start)
        if k >= 0:
            end = min(end, k)
    return txt[:start], txt[start:end]


def brands_we_love(nav):
    i = nav.find('Brands We Love')
    if i < 0:
        return ''
    seg = nav[i + 14:i + 600]
    for stop in [' The ', ' Close', ' Featured', ' Shop ']:
        k = seg.find(stop)
        if k > 0:
            seg = seg[:k]
    return seg


def owned_hits(s):
    return [n for n, rx in OWNED if rx.search(s)]


def main(targets):
    for target in targets:
        tag = re.sub(r'\W+', '_', target).strip('_')
        rows = cdx(target)
        cap = int(os.environ.get('E1_PER_MONTH', '0'))   # optional: max snapshots per month (evenly spaced)
        if cap:
            bym = defaultdict(list)
            for row in rows:
                if int(row[-1]) >= 15000:
                    bym[row[0][:6]].append(row)
            rows = []
            for k in sorted(bym):
                v = bym[k]
                step = max(1, len(v) // cap)
                rows += v[::step][:cap]
        print(target, 'snapshots', len(rows))
        tiles_out, snaps_out = [], []
        for row in rows:
            ts, ln = row[0], row[-1]
            if int(ln) < 15000:   # tiny captures = bot-wall / error pages
                snaps_out.append({'ts': ts, 'date': f'{ts[:4]}-{ts[4:6]}-{ts[6:8]}', 'status': 'tiny_capture'})
                continue
            h = snap(target, ts)
            if not h:
                snaps_out.append({'ts': ts, 'date': f'{ts[:4]}-{ts[4:6]}-{ts[6:8]}', 'status': 'fetch_fail'})
                continue
            txt = text_of(h)
            nav, body = split_nav_body(txt)
            parts = [p.strip() for p in CTA.split(body)]
            tiles = [p for p in parts if p and not CTA.fullmatch(p) and len(p) > 12]
            n_owned = n_owned_disc = n_disc = n_nat = 0
            depths = []
            for t in tiles:
                oh = owned_hits(t)
                dm = [int(a or 0) for a, b in DISC.findall(t)]
                pct = max(dm) if dm and max(dm) > 0 else None
                is_disc = bool(DISC.search(t))
                n_disc += is_disc
                n_nat += bool(NATIONAL.search(t))
                if oh:
                    n_owned += 1
                    if is_disc:
                        n_owned_disc += 1
                        if pct:
                            depths.append(pct)
                tiles_out.append({'ts': ts, 'date': f'{ts[:4]}-{ts[4:6]}-{ts[6:8]}', 'owned': '|'.join(oh),
                                  'discount': is_disc, 'max_pct': pct or '', 'national': bool(NATIONAL.search(t)), 'tile': t[:400]})
            bwl = brands_we_love(nav)
            snaps_out.append({'ts': ts, 'date': f'{ts[:4]}-{ts[4:6]}-{ts[6:8]}', 'status': 'ok', 'n_tiles': len(tiles),
                              'n_owned_tiles': n_owned, 'n_disc_tiles': n_disc, 'n_owned_disc_tiles': n_owned_disc,
                              'n_national_tiles': n_nat, 'owned_disc_depths': '|'.join(map(str, depths)),
                              'owned_in_body': '|'.join(owned_hits(body)), 'owned_in_nav': '|'.join(owned_hits(nav)),
                              'brands_we_love': bwl, 'bwl_owned': '|'.join(owned_hits(bwl)),
                              'body_owned_mentions': sum(len(rx.findall(body)) for _, rx in OWNED),
                              'body_len': len(body)})
            print(ts, len(tiles), n_owned, n_owned_disc)
        with open(os.path.join(BASE, f'E1_hp_tiles_{tag}.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=['ts', 'date', 'owned', 'discount', 'max_pct', 'national', 'tile'])
            w.writeheader(); w.writerows(tiles_out)
        keys = ['ts', 'date', 'status', 'n_tiles', 'n_owned_tiles', 'n_disc_tiles', 'n_owned_disc_tiles', 'n_national_tiles',
                'owned_disc_depths', 'owned_in_body', 'owned_in_nav', 'brands_we_love', 'bwl_owned', 'body_owned_mentions', 'body_len']
        with open(os.path.join(BASE, f'E1_hp_snapshots_{tag}.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(snaps_out)
        # monthly
        m = defaultdict(lambda: defaultdict(float))
        for s in snaps_out:
            if s.get('status') != 'ok':
                continue
            k = s['date'][:7]
            m[k]['snaps'] += 1
            for c in ['n_tiles', 'n_owned_tiles', 'n_disc_tiles', 'n_owned_disc_tiles', 'n_national_tiles']:
                m[k][c] += s[c]
            m[k]['bwl_owned_n'] += len([x for x in s['bwl_owned'].split('|') if x])
        with open(os.path.join(BASE, f'E1_hp_monthly_{tag}.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['month', 'snaps', 'tiles', 'owned_tiles', 'owned_tile_share', 'disc_tiles', 'owned_disc_tiles',
                        'owned_share_of_disc_tiles', 'national_tiles', 'avg_bwl_owned'])
            for k in sorted(m):
                d = m[k]
                w.writerow([k, int(d['snaps']), int(d['n_tiles']), int(d['n_owned_tiles']),
                            round(d['n_owned_tiles'] / d['n_tiles'], 3) if d['n_tiles'] else '', int(d['n_disc_tiles']),
                            int(d['n_owned_disc_tiles']),
                            round(d['n_owned_disc_tiles'] / d['n_disc_tiles'], 3) if d['n_disc_tiles'] else '',
                            int(d['n_national_tiles']), round(d['bwl_owned_n'] / d['snaps'], 2)])


if __name__ == '__main__':
    main(sys.argv[1:] or DEFAULT_TARGETS)
