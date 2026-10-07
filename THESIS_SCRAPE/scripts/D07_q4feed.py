"""D07: query the Q4 Inc public JSON feed of investors.dicks.com for press releases / Sideline Report blog posts.
Rerun: python THESIS_SCRAPE\\scripts\\D07_q4feed.py <keyword> [year]
Saves THESIS_SCRAPE\\raw\\D07_q4feed_<year>.json; prints headline/date/url for items whose headline/body matches keyword.
"""
import sys, json, re, html, requests
kw = sys.argv[1] if len(sys.argv) > 1 else 'Operating Model'
year = sys.argv[2] if len(sys.argv) > 2 else '2026'
H = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
base = 'https://investors.dicks.com/feed/PressRelease.svc/GetPressReleaseList'
params = dict(LanguageId=1, bodyType=0, pressReleaseDateFilter=3, categoryId='', pageSize=-1, pageNumber=0,
              tagList='', includeTags='true', year=year, excludeSelection=1)
r = requests.get(base, params=params, headers=H, timeout=60)
print(r.status_code, len(r.text))
try:
    d = r.json()
except Exception:
    print(r.text[:500]); sys.exit()
open(rf'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\D07_q4feed_{year}.json', 'w', encoding='utf-8').write(json.dumps(d))
items = d.get('GetPressReleaseListResult', [])
print('items', len(items))
for it in items:
    body = it.get('Body') or ''
    if re.search(kw, (it.get('Headline') or '') + body, re.I):
        print('---', it.get('PressReleaseDate'), it.get('Headline'), it.get('LinkToDetailPage'), it.get('Category'))
        txt = html.unescape(re.sub(r'<[^>]+>', ' ', body))
        print(re.sub(r'\s+', ' ', txt)[:6000])
