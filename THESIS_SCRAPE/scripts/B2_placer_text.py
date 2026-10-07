"""B2: fetch Placer Anchor article(s), save visible text (title/date/key takeaways/body) and any inline chart data
(the 2026 'placer-claude-embed-charts' format keeps data in data-* attributes / inline JSON; older ones use Infogram ids).
Usage: python B2_placer_text.py <slug-or-url> [...]   -> raw/B2_placer_text/<slug>.txt
"""
import requests, re, os, sys, html, json, time
from bs4 import BeautifulSoup
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'raw', 'B2_placer_text'); os.makedirs(OUT, exist_ok=True)
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
for a in sys.argv[1:]:
    u = a if a.startswith('http') else 'https://www.placer.ai/anchor/articles/' + a
    slug = u.rstrip('/').rsplit('/', 1)[-1]
    t = requests.get(u, headers=H, timeout=60).text
    s = BeautifulSoup(t, 'html.parser')
    out = [f'URL: {u}', 'TITLE: ' + (s.title.get_text(strip=True) if s.title else '')]
    m = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, 20\d\d', t)
    out.append('DATE: ' + (m.group(0) if m else ''))
    for c in ['key-takeaway-richtext', 'post-body']:
        el = s.find(class_=c)
        if el:
            for sc in el.find_all(['style', 'script', 'form']):
                sc.decompose()
            out.append('== ' + c)
            out.append(re.sub(r'\s+', ' ', el.get_text(' ', strip=True)))
    # inline chart data: any element with data-* attribute holding JSON or long numeric lists
    i = t.find('post-body')
    body = t[i:]
    for mm in re.finditer(r'(data-[a-z0-9-]+)=(["\'])(.{30,}?)\2', body[:300000]):
        v = html.unescape(mm.group(3))
        if re.search(r'-?\d+\.\d', v) and ('[' in v or '{' in v or ',' in v):
            out.append(f'DATAATTR {mm.group(1)}: {v[:3000]}')
    for mm in re.finditer(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', body[:300000], re.S):
        out.append('JSON: ' + mm.group(1)[:5000])
    for mm in re.finditer(r'class="infogram-embed"\s+data-id="([^"]+)"[^>]*?data-title="([^"]*)"', t):
        out.append(f'INFOGRAM {mm.group(1)} | {html.unescape(html.unescape(mm.group(2)))}')
    for mm in set(re.findall(r'datawrapper\.dwcdn\.net/([A-Za-z0-9]{5})/', t)):
        out.append(f'DATAWRAPPER {mm}')
    txt = '\n'.join(out)
    open(os.path.join(OUT, slug + '.txt'), 'w', encoding='utf-8').write(txt)
    print(txt[:6000]); print('-' * 80)
    time.sleep(2)
