"""B1: list document links (pdf/doc/drive/packet) on one or more pages.
Rerun: python B1_links.py URL [URL ...] [--grep regex]   (prints page-text hits for regex, then doc links)
"""
import sys, re, requests
from bs4 import BeautifulSoup
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36'}
args = sys.argv[1:]
pat = None
if '--grep' in args:
    i = args.index('--grep'); pat = args[i + 1]; args = args[:i] + args[i + 2:]
for u in args:
    try:
        r = requests.get(u, headers=H, timeout=90)
    except Exception as e:
        print('ERR', u, e); continue
    print('##', u, r.status_code, len(r.content))
    if pat:
        txt = BeautifulSoup(r.text, 'html.parser').get_text(' ', strip=True)
        for m in list(re.finditer(pat, txt, re.I))[:5]:
            print('   TXT ..', txt[max(0, m.start() - 250): m.start() + 250])
    seen = set()
    for m in re.findall(r'https?://[^"\'\s<>]+', r.text):
        if re.search(r'\.(pdf|docx?|pptx?)(\?|$)|drive\.google|DocumentCenter/View|/files/|packet|Attachment', m, re.I) and m not in seen:
            seen.add(m); print('   ', m[:220])
    for m in re.findall(r'href="(/[^"]+)"', r.text):
        if re.search(r'\.(pdf|docx?)|DocumentCenter/View|AgendaCenter/ViewFile|Attachment|LinkClick', m, re.I) and m not in seen:
            seen.add(m); print('   REL', m[:220])
