"""L1: pull DKS IR Q4 JSON press-release feed for 2023-2026, save each year, list headlines.
Rerun: python THESIS_SCRAPE\scripts\L1_irfeed.py
Outputs THESIS_SCRAPE\raw\L1_irfeed_<year>.json and L1_irfeed_headlines.csv
"""
import json, requests, csv, re, html
H = {'User-Agent': 'Mozilla/5.0 (research; palazzolojustin@gmail.com)', 'Accept': 'application/json'}
base = 'https://investors.dicks.com/feed/PressRelease.svc/GetPressReleaseList'
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
rows = []
for year in ['2022','2023','2024','2025','2026']:
    params = dict(LanguageId=1, bodyType=2, pressReleaseDateFilter=3, categoryId='', pageSize=-1, pageNumber=0,
                  tagList='', includeTags='true', year=year, excludeSelection=1)
    r = requests.get(base, params=params, headers=H, timeout=60)
    d = r.json()
    open(rf'{R}\L1_irfeed_{year}.json', 'w', encoding='utf-8').write(json.dumps(d))
    for it in d.get('GetPressReleaseListResult', []):
        rows.append([it.get('PressReleaseDate'), it.get('Headline'), it.get('Category'), it.get('LinkToDetailPage'), len(it.get('Body') or '')])
with open(rf'{R}\L1_irfeed_headlines.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['date','headline','category','url','bodylen']); w.writerows(rows)
for x in rows: print(x[0][:10], '|', x[1], '|', x[2], '|', x[4])
