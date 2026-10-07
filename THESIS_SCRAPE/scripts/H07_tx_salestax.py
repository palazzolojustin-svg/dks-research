"""H07: Texas Comptroller open data (data.texas.gov Socrata) pulls for cities where DKS opened House of Sport
stores (permit first-sales dates from 'Active Sales Tax Permit Holders' jrea-zgmq).
- 7z4d-yf2c Quarterly Sales Tax Historical Data (gross/taxable/outlets by city x NAICS sector)
- vfba-b57j Sales Tax Allocation, City (monthly payments to cities)
- tmhs-ahbh Sales Tax Allocation, Tax Rates
Rerun: python H07_tx_salestax.py CITY1 CITY2 ...  -> writes raw/H07_TX_<city>_quarterly.csv and _alloc.csv
"""
import requests, csv, sys, os
B = 'https://data.texas.gov/resource/'
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
cities = sys.argv[1:] or ['Live Oak', 'Selma', 'Universal City', 'Converse', 'Schertz', 'Windcrest']
for c in cities:
    q = requests.get(B + '7z4d-yf2c.json', params={'$where': f"upper(name)='{c.upper()}' and type='City' and industry in('Retail Trade','All Industries')", '$limit': 1000, '$order': 'year,qtr'}, timeout=300).json()
    a = requests.get(B + 'vfba-b57j.json', params={'$where': f"upper(city)='{c.upper()}'", '$limit': 1000}, timeout=300).json()
    tag = c.replace(' ', '_')
    for name, rows in [('quarterly', q), ('alloc', a)]:
        if not rows: print(c, name, 'EMPTY'); continue
        keys = sorted({k for r in rows for k in r})
        with open(os.path.join(RAW, f'H07_TX_{tag}_{name}.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
        print(c, name, len(rows))
