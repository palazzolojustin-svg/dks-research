"""R2: print QCEW sporting-goods (451110/459110) quarterly estabs/jobs/wages for NY counties.
Usage: python R2_qcew_county.py 36071 36113 ...   (reads raw/H07_qcew_sporting_allcounties.csv)
"""
import pandas as pd, sys
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
d = pd.read_csv(R + 'H07_qcew_sporting_allcounties.csv', dtype={'area_fips': str})
for f in sys.argv[1:]:
    x = d[d.area_fips == f].sort_values(['year', 'qtr'])
    x = x[x.year >= 2021].copy()
    x['wages_$M'] = (x.total_qtrly_wages / 1e6).round(2)
    print('==', f)
    print(x[['year', 'qtr', 'industry_code', 'qtrly_estabs', 'month3_emplvl', 'wages_$M', 'disclosure_code']].to_string(index=False))
