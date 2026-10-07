"""X09: Wikipedia monthly pageviews (user agents only, all-access) for DKS owned-brand pages vs benchmarks.
Open Wikimedia REST API, no key. Rerun: python X09_wikipedia_pageviews.py  -> raw/X09_wiki_pageviews.csv
Note: 'user' agent filter excludes self-identified bots/spiders; automated traffic can still leak in.
"""
import requests, pandas as pd, os, time
H = {'User-Agent': 'DKS-research-X09/1.0 (python requests; contact via repo owner)'}
PAGES = ['Maxfli', 'Top-Flite', 'Dick%27s_Sporting_Goods', 'Golf_Galaxy', 'Titleist', 'Srixon', 'Vice_Golf',
         'Lululemon', 'Vuori', 'Under_Armour', 'Acushnet', 'TaylorMade', 'Kirkland_Signature', 'Academy_Sports_%2B_Outdoors']
END = '2026093000'
rows = {}
for p in PAGES:
    u = f'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{p}/monthly/2021010100/{END}'
    r = requests.get(u, headers=H, timeout=30)
    if r.status_code != 200:
        print('miss', p, r.status_code); continue
    rows[p] = {i['timestamp'][:6]: i['views'] for i in r.json()['items']}
    time.sleep(0.5)
df = pd.DataFrame(rows).sort_index()
out = os.path.join(os.path.dirname(__file__), '..', 'raw', 'X09_wiki_pageviews.csv')
df.to_csv(out)
a26 = df.loc['202604':'202609'].sum(); a25 = df.loc['202504':'202509'].sum(); a24 = df.loc['202404':'202409'].sum()
print(pd.DataFrame({'AprSep24': a24, 'AprSep25': a25, 'AprSep26': a26, 'yoy26%': (a26 / a25 - 1) * 100, 'yoy25%': (a25 / a24 - 1) * 100}).round(1))
print(df.loc['202501':].to_string())
