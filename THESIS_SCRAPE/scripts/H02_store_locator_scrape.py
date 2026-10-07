"""H02: scrape every store page on stores.dickssportinggoods.com (SOCi/W2GI locator).

Rerun:  python H02_store_locator_scrape.py
Output: THESIS_SCRAPE/raw/H02_store_pages.json (one record per store page, with format flags)
        THESIS_SCRAPE/raw/H02_store_pages_html/<storeno>.html is NOT saved (too large); only parsed fields.
Method: read sitemap_0.xml (via sitemap_index.xml), keep URLs of depth /state/city/storeno/, GET each
with 6 threads, parse <title>, ld+json name, the W2GI poi[0] block, hours, image/logo paths and keyword hits.
"""
import re, json, time, os, concurrent.futures as cf
import requests

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'raw', 'H02_store_pages.json')
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36'}
KEYS = ['House of Sport', 'Field House', 'Coming Soon', 'coming soon', 'Grand Opening', 'grand opening', 'Now Open',
        'Opening', 'climbing', 'Climbing', 'batting', 'Batting', 'TrackMan', 'turf', 'Turf', 'golf simulator',
        'Golf Simulator', 'Hitting', 'Golf Lessons', 'Pickleball', 'pickleball', 'Running Track', 'track', 'Recovery',
        'Hyrox', 'Studio', 'Scoreboard', 'Trading Card', 'Gymshark', 'Field House Experience']


def sitemap_urls():
    idx = requests.get('https://stores.dickssportinggoods.com/sitemap_index.xml', headers=H, timeout=30).text
    urls, lastmod = [], {}
    for sm in re.findall(r'<loc>(.*?)</loc>', idx):
        s = requests.get(sm, headers=H, timeout=60).text
        for block in re.findall(r'<url>(.*?)</url>', s, re.S):
            loc = re.search(r'<loc>(.*?)</loc>', block).group(1)
            lm = re.search(r'<lastmod>(.*?)</lastmod>', block)
            if re.match(r'https://stores\.dickssportinggoods\.com/[a-z]{2}/[^/]+/\d+/$', loc):
                urls.append(loc)
                lastmod[loc] = lm.group(1) if lm else ''
    return urls, lastmod


def parse(url, html):
    rec = {'url': url, 'storeno': url.rstrip('/').split('/')[-1], 'len': len(html)}
    m = re.search(r'<title>(.*?)</title>', html, re.S)
    rec['title'] = m.group(1).strip() if m else ''
    i = html.find('W2GI.collection.poi')
    blk = html[i:i + 2500] if i >= 0 else ''
    for f in ['name', 'icon', 'address1', 'address2', 'city', 'state', 'postalcode', 'latitude', 'longitude', 'phone',
              'clientkey', 'specialhours']:
        mm = re.search(r'\b' + f + r"\s*:\s*'(.*?)'", blk)
        rec[f] = mm.group(1).replace('&#x27;', "'") if mm else ''
    mm = re.search(r'"@type":"SportingGoodsStore".*?"name":\s*"(.*?)"', html, re.S)
    rec['ld_name'] = mm.group(1).replace('&#8217;', "'") if mm else ''
    rec['logo'] = ';'.join(sorted(set(re.findall(r'"logo"\s*:\s*"(.*?)"', html))))
    rec['image'] = ';'.join(sorted(set(re.findall(r'"image"\s*:\s*"(.*?)"', html))))
    rec['hours_n'] = html.count('OpeningHoursSpecification') - 1
    rec['opens'] = ';'.join(re.findall(r'"opens":"(.*?)"', html)[:7])
    rec['h1'] = re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', (re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S) or [None, ''])[1] if re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S) else '')).strip()
    rec['kw'] = {k: html.count(k) for k in KEYS if html.count(k)}
    # any visible text near "open" with a date
    txt = re.sub(r'<script.*?</script>', ' ', html, flags=re.S)
    txt = re.sub(r'<style.*?</style>', ' ', txt, flags=re.S)
    txt = re.sub(r'<!--.*?-->', ' ', txt, flags=re.S)
    txt = re.sub(r'<[^>]+>', ' ', txt)
    txt = re.sub(r'\s+', ' ', txt)
    dates = re.findall(r'(?:[A-Z][a-z]+day,? )?(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}(?:st|nd|rd|th)?,? ?(?:20\d\d)?', txt)
    rec['dates'] = sorted(set(dates))[:15]
    snips = []
    for k in ['Coming Soon', 'coming soon', 'Grand Opening', 'grand opening', 'Now Open', 'NOW OPEN', 'COMING SOON', 'GRAND OPENING', 'opening soon', 'Opening Soon', 'relocat', 'Relocat', 'new location', 'New Location', 'moved']:
        for mm in re.finditer(k, txt):
            snips.append(txt[max(0, mm.start() - 150): mm.start() + 200])
    rec['snips'] = snips[:6]
    imgs = sorted(set(re.findall(r'llp-assets\.meetsoci\.com/live/assets/dickssportinggoods/[^"\'\s)]+', html)))
    rec['asset_dirs'] = sorted(set('/'.join(x.split('/')[4:-1]) for x in imgs))
    return rec


def fetch(url):
    for a in range(3):
        try:
            r = requests.get(url, headers=H, timeout=40)
            if r.status_code == 200:
                return parse(url, r.text)
            time.sleep(2)
        except Exception as e:
            time.sleep(3)
    return {'url': url, 'error': True}


if __name__ == '__main__':
    urls, lastmod = sitemap_urls()
    print(len(urls), 'store urls')
    recs = []
    with cf.ThreadPoolExecutor(6) as ex:
        for i, rec in enumerate(ex.map(fetch, urls)):
            rec['lastmod'] = lastmod.get(rec['url'], '')
            recs.append(rec)
            if i % 100 == 0:
                print(i)
    json.dump(recs, open(OUT, 'w', encoding='utf8'), indent=1)
    print('saved', OUT, len(recs))
