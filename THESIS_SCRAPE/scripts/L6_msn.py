"""L6: fetch MSN syndicated article text via the public MSN content JSON (assets.msn.com) and save plain text.
Usage: python L6_msn.py <article_id> [<article_id> ...]   e.g. AA1ZzaXq
Output: THESIS_SCRAPE\\raw\\L6_msn_<id>.txt
"""
import requests, sys, re, html, json
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
for aid in sys.argv[1:]:
    u = f'https://assets.msn.com/content/view/v2/Detail/en-us/{aid}'
    r = requests.get(u, headers=H, timeout=60)
    print(aid, r.status_code)
    if r.status_code != 200:
        continue
    j = r.json()
    body = j.get('body', '')
    txt = html.unescape(re.sub(r'<[^>]+>', '\n', body))
    txt = re.sub(r'\n\s*\n+', '\n', txt)
    meta = f"TITLE: {j.get('title')}\nDATE: {j.get('publishedDateTime')}\nPROVIDER: {(j.get('provider') or {}).get('name')}\nSRC: {j.get('sourceHref')}\n\n"
    open(rf'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\L6_msn_{aid}.txt', 'w', encoding='utf-8').write(meta + txt)
    print(meta + txt[:6000])
