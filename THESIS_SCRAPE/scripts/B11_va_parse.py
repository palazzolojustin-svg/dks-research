"""B11: parse Virginia quarterly taxable sales xlsx (County + City sheets) into a long panel.
Output raw/B11_VA_panel.csv: year,q,locality,sheet,naics,label,dealers,amount
Rerun: python scripts/B11_va_parse.py (after B11_va_fetch.py)"""
import pandas as pd, re, glob, os, warnings
warnings.filterwarnings('ignore')
rows = []
for f in sorted(glob.glob('raw/B11_cache/va/*q*.xls*')):
    if 'annual' in f: continue
    m = re.search(r'(20\d\d)_?q(\d)', os.path.basename(f).replace('cyq', 'cy').replace('cy', ''))
    if not m:
        m = re.search(r'(20\d\d)\D*q(\d)', os.path.basename(f))
    yr, q = int(m.group(1)), int(m.group(2))
    x = pd.ExcelFile(f)
    for sh in x.sheet_names:
        if sh not in ('County', 'City', 'State'): continue
        d = pd.read_excel(x, sh, header=None, dtype=str)
        loc = 'STATE' if sh == 'State' else None
        for _, r in d.iterrows():
            vals = [v for v in r.tolist() if isinstance(v, str) and v.strip() and v.strip().lower() != 'nan']
            if not vals: continue
            code = None
            for v in vals:
                if re.fullmatch(r'\d{3}', v.strip()): code = v.strip(); break
            if code is None:
                # locality header: single short string, not title text
                if len(vals) == 1 and len(vals[0]) < 40 and not re.search(r'(?i)taxable|deposit|naics|commonwealth|total|page', vals[0]) and sh != 'State':
                    loc = vals[0].strip()
                continue
            nums = []
            for v in vals:
                try: nums.append(float(v.replace(',', '')))
                except: pass
            label = [v for v in vals if not re.fullmatch(r'[\d.,\-]+', v.strip())]
            if len(nums) >= 3:
                dealers, amt = nums[-2], nums[-1]
            elif len(nums) == 2:
                dealers, amt = None, nums[-1]
            else:
                continue
            rows.append(dict(year=yr, q=q, sheet=sh, locality=loc, naics=code, label=label[0] if label else '', dealers=dealers, amount=amt))
    print(f, yr, q, len(rows))
p = pd.DataFrame(rows)
p.to_csv('raw/B11_VA_panel.csv', index=False)
print(p[p.naics.isin(['451', '459'])].groupby(['year', 'q', 'naics']).amount.sum())
