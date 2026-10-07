"""H02: query public WordPress REST search endpoints (wp-json/wp/v2/posts?search=) on news sites that cover
store openings (WhatNow, SGB Media, Hoodline...). Saves posts with date, link, plain text.
Rerun: python H02_wp_search.py <site_base> "<search terms>" <out.json>
"""
import sys, json, re, html, requests

H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36'}
base, q, outp = sys.argv[1].rstrip('/'), sys.argv[2], sys.argv[3]
posts = []
for page in range(1, 11):
    r = requests.get(f'{base}/wp-json/wp/v2/posts', params={'search': q, 'per_page': 100, 'page': page,
                     '_fields': 'id,date,link,title,content'}, headers=H, timeout=60)
    if r.status_code != 200:
        print('status', r.status_code, r.text[:200]); break
    js = r.json()
    if not js:
        break
    for p in js:
        txt = re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', p['content']['rendered'])))
        posts.append({'id': p['id'], 'date': p['date'], 'link': p['link'],
                      'title': html.unescape(p['title']['rendered']), 'text': txt})
    if len(js) < 100:
        break
json.dump(posts, open(outp, 'w', encoding='utf8'), indent=1)
print(len(posts))
for p in sorted(posts, key=lambda x: x['date'], reverse=True):
    print(p['date'][:10], '|', p['title'][:120], '|', p['link'])
