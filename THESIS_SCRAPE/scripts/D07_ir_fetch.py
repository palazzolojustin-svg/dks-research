"""D07: fetch DKS investor-relations (Q4 platform) news/blog content via public JSON feed endpoints.
Rerun: python THESIS_SCRAPE\\scripts\\D07_ir_fetch.py [url]
Saves raw page to THESIS_SCRAPE\\raw\\D07_ir_page.html and prints API-like references found.
"""
import re, sys, requests
U = sys.argv[1] if len(sys.argv) > 1 else 'https://investors.dicks.com/news/sideline-report/blog-story-details/2026/Empowering-Teammates-Elevating-Experience-Inside-DICKS-Sporting-Goods-New-Transformative-Store-Operating-Model/default.aspx'
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36'}
r = requests.get(U, headers=H, timeout=30)
print(r.status_code, len(r.text))
open(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\D07_ir_page.html', 'w', encoding='utf-8').write(r.text)
seen = set()
for m in re.finditer(r'(?:feed|Services|api)[A-Za-z0-9_/\.\-\?=&]{0,150}', r.text):
    s = m.group(0)
    if s not in seen:
        seen.add(s); print(s)
