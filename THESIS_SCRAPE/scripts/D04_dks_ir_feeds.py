"""D04: pull DKS investor-site press releases + 'Sideline Report' blog stories via the public Q4 JSON feed
(the same endpoint the investors.dicks.com page calls). Rerun: python D04_dks_ir_feeds.py
Outputs: THESIS_SCRAPE/raw/D04_dks_ir_press_list.json, D04_dks_sideline_list.json, D04_dks_sideline_bodies.txt
"""
import requests, json, datetime, re, time
from bs4 import BeautifulSoup
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36',
     'Accept': 'application/json'}
base = 'https://investors.dicks.com/feed/PressRelease.svc/GetPressReleaseList'
side = requests.get(base, params={'LanguageId': 1, 'bodyType': 3, 'pressReleaseDateFilter': 3,
                                  'categoryId': '6aaabeee-3f59-4251-98de-0a953da6b0ae', 'pageSize': -1,
                                  'pageNumber': 0, 'tagList': '', 'includeTags': 'true', 'year': -1,
                                  'excludeSelection': 1}, headers=h, timeout=60).json()['GetPressReleaseListResult']
json.dump(side, open(RAW + r'\D04_dks_sideline_list.json', 'w'), indent=0)
out = []
for x in side:
    dt = datetime.datetime.strptime(x['PressReleaseDate'], '%m/%d/%Y %H:%M:%S')
    body = BeautifulSoup(x.get('Body') or '', 'html.parser').get_text(' ', strip=True)
    out.append((dt, x['Headline'], x.get('LinkToDetailPage'), body))
out.sort()
with open(RAW + r'\D04_dks_sideline_bodies.txt', 'w', encoding='utf8') as f:
    for dt, hd, link, body in out:
        f.write(f'### {dt.date()} | {hd} | {link}\n{body}\n\n')
print(len(out))
for dt, hd, link, body in out:
    if dt.year >= 2024:
        print(dt.date(), '|', hd, '|', len(body))
