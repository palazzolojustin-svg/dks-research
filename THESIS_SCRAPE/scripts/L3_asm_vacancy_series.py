"""L3: ASM / Lead / Team Captain open postings over time for legacy DSG-type stores (excludes House of Sport, Golf Galaxy titles).
Inputs: wave-1 H06 Wayback job sitemaps raw/H06_sitemap_<ts>.txt (2024-06 .. 2026-05) + live Workday census raw/H06_details.pkl (2026-10-07).
Rerun: python L3_asm_vacancy_series.py -> raw/L3_asm_vacancy_series.csv
"""
import pandas as pd, re, os, glob, urllib.parse
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')


def cls(t):
    t = t.lower()
    if 'house of sport' in t or 'golf galaxy' in t or 'ggxy' in t or 'public lands' in t:
        return 'excluded (HoS/GG/PL title)'
    if 'assistant store manager' in t or re.search(r'\basm\b', t): return 'ASM'
    if 'team captain' in t: return 'Team Captain'
    if re.search(r'\bstore manager\b', t): return 'Store Mgr'
    if t.startswith('specialist'): return 'Specialist (new)'
    if re.search(r'\blead\b|leader|key holder|keyholder', t): return 'Hourly Lead (old)'
    return 'other'


rows = []
for f in sorted(glob.glob(os.path.join(RAW, 'H06_sitemap_2*.txt'))):
    ts = re.search(r'(\d{14})', f).group(1)
    urls = [u for u in open(f, encoding='utf-8').read().split('\n') if '/job/' in u]
    titles = []
    for u in urls:
        u2 = urllib.parse.unquote_plus(u)
        m = re.search(r'/job/(\d+-)?([a-z0-9\-]+)/', u2)
        if m and not u2.split('/job/')[1].startswith('?'):
            titles.append(m.group(2).replace('-', ' '))
        else:
            m = re.search(r'/job/\?(.+)-j-\d+', u2)
            if m:
                titles.append(' '.join(m.group(1).split('-')[:-2]))
    c = pd.Series([cls(t) for t in titles]).value_counts().to_dict()
    c.update({'date': ts[:8], 'total': len(titles), 'source': 'Wayback jobs-sitemap'})
    rows.append(c)
d = pd.read_pickle(os.path.join(RAW, 'H06_details.pkl'))
s = d[d.location.str.match(r'Store\d{4}', na=False) & d.location_type.isin(["DICK'S Sporting Goods", "DICK'S Sporting Goods (DSG + GG)", 'Going Going Gone!'])]
c = s.title.apply(cls).value_counts().to_dict(); c.update({'date': '20261007', 'total': len(s), 'source': 'Workday live (DSG/GGG location types)'})
rows.append(c)
o = pd.DataFrame(rows).fillna(0)
cols = ['date', 'source', 'total', 'ASM', 'Store Mgr', 'Team Captain', 'Hourly Lead (old)', 'Specialist (new)', 'excluded (HoS/GG/PL title)', 'other']
o = o[[c for c in cols if c in o.columns]]
o.to_csv(os.path.join(RAW, 'L3_asm_vacancy_series.csv'), index=False)
print(o.to_string())
