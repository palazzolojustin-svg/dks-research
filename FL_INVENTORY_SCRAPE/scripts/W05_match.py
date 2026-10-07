import pandas as pd,re
fl=pd.read_csv('raw/W05/fl_brand_rows.csv').drop_duplicates(['sku'])
fl=fl[fl.brand.isin(['Nike','Jordan'])]
o=pd.read_csv('raw/W05/others_rows.csv');nk=o[o.retailer=='nike.com'].drop_duplicates('code')
def norm(s):
    s=re.sub(r"\s*-\s*(Men's|Women's|Boys'.*|Girls'.*)$","",s);s=re.sub(r'[^a-z0-9 ]','',s.lower().replace('nike ','').replace('air jordan','jordan'));return re.sub(' +',' ',s).strip()
fl['k']=fl.name.map(norm);nk=nk.assign(k=nk.name.map(norm))
nkg=nk.groupby('k').agg(nk_price=('price','min'),nk_orig=('orig','max'),nk_n=('code','count')).reset_index()
m=fl.groupby('k').agg(name=('name','first'),brand=('brand','first'),fl_price=('price','min'),fl_orig=('orig','max'),fl_n=('sku','count')).reset_index().merge(nkg,on='k')
m['fl_disc']=1-m.fl_price/m.fl_orig;m['nk_disc']=1-m.nk_price/m.nk_orig
m['retailer_gap']=m.fl_price-m.nk_price
print(len(m));print(m[['name','fl_orig','fl_price','nk_orig','nk_price']].to_string(index=False))
print('FL cheaper',(m.fl_price<m.nk_price).sum(),'same',(m.fl_price==m.nk_price).sum(),'FL dearer',(m.fl_price>m.nk_price).sum())
print('FL on sale',(m.fl_disc>.001).sum(),'Nike on sale',(m.nk_disc>.001).sum(),'mean FL disc',round(m.fl_disc.mean(),3),'mean Nike disc',round(m.nk_disc.mean(),3))
m.to_csv('data/W05_prices.csv',index=False)
