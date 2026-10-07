"""X14: tag X04's ImportYeti supplier table (consignee DICK'S MERCHANDISING & SUPPLY CHAIN) with DKS's own vertical-brand
factory disclosure lists (Transparency Pledge exports 2023-01/2023-07/2024-07), so import volumes can be split into
officially-disclosed vertical-brand factories vs others.
Inputs: raw/X04_iy_dmsc_suppliers.csv (X04), raw/X14_factory_list_combined.csv (X14)
Output: raw/X14_imports_tagged_vertical.csv + printed Apr-Sep totals.
Rerun after X04 refreshes its supplier CSV.
"""
import pandas as pd, re, os
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
imp = pd.read_csv(os.path.join(RAW, 'X04_iy_dmsc_suppliers.csv'))
fl = pd.read_csv(os.path.join(RAW, 'X14_factory_list_combined.csv'))
STOP = {'co', 'ltd', 'limited', 'company', 'inc', 'corp', 'joint', 'stock', 'the', 'int', 'l', 'intl', 'international', 'hk', 'group',
        'industrial', 'industry', 'mfg', 'manufacturing', 'trading', 'trade', 'sa', 'de', 'cv', 'sporting', 'goods', 'sports', 'garment', 'garments',
        'vietnam', 'viet', 'nam', 'cambodia', 'china', 'branch', 'factory', 'pt', 'jsc', 'llc', 'and', 'export', 'c', 'products', 'enterprise'}
def toks(s):
    return {t for t in re.sub(r'[^a-z0-9 ]', ' ', str(s).lower()).split() if t not in STOP and len(t) > 2}
names = []
for _, r in fl.drop_duplicates(['Factory Name', 'Vendor Name']).iterrows():
    names.append((toks(r['Factory Name']), r['Factory Name'], r['Factory Type'], r['ver']))
    names.append((toks(r['Vendor Name']), r['Vendor Name'] + ' [vendor]', r['Factory Type'], r['ver']))
out = []
for _, r in imp.iterrows():
    st = toks(r['supplier'])
    best = None
    for nt, nm, ty, ver in names:
        if st and nt:
            ov = len(st & nt) / len(st)
            if ov >= 0.99 and (best is None or len(nt) < len(best[0])):
                best = (nt, nm, ty)
    out.append({**r.to_dict(), 'fl_match': best[1] if best else '', 'fl_type': best[2] if best else ''})
o = pd.DataFrame(out)
ALIAS = {'Ha Bac Export Garment Joint Stock C':('Habac Export Garment JSC [alias]','Softline'),'Nan Yang Garment':('Nanyang Garment Co. Ltd. [alias]','Softline'),'Century Miracle Apparel Manufacturi':('Century Miracle Apparel Mfg (Yee Tung) [alias]','Softline'),'Wp Sports Cambodia':('WP Sports (Cambodia) Co., Ltd [alias]','Hardline'),'Century Distribution Systems':('CONSOLIDATOR: BOL names Glory Industrial Semarang (Makalot) [alias]','Softline'),'Century Distribution Systems Ind':('CONSOLIDATOR: BOL names Glory Industrial Semarang (Makalot) [alias]','Softline')}
for k,(m,t) in ALIAS.items():
    o.loc[o.supplier==k,['fl_match','fl_type']]=[m,t]
o.to_csv(os.path.join(RAW, 'X14_imports_tagged_vertical.csv'), index=False)
o['on_list'] = o['fl_match'] != ''
cols = ['AprSep24_ship', 'AprSep25_ship', 'AprSep26_ship', 'AprSep24_teu', 'AprSep25_teu', 'AprSep26_teu']
print(o[['supplier', 'fl_match', 'fl_type'] + cols].to_string())
print(o.groupby('on_list')[cols].sum())
print(o[o.on_list].groupby('fl_type')[cols].sum())
