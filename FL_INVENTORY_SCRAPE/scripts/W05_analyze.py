import pandas as pd,re,json
fl=pd.read_csv('raw/W05/fl_brand_rows.csv').drop_duplicates(['brand','slice','sku'])
fa=fl[fl.slice=='all'].copy(); fa['disc']=1-fa.price/fa.orig; fa['onsale']=fa.disc>0.001
print('FL all-slice sample (top-48 relevance per brand):');g=fa.groupby('brand').agg(n=('sku','count'),on_sale=('onsale','mean'),avg_disc_onsale=('disc',lambda x:x[x>0.001].mean()),avg_price=('price','mean'));print(g.round(3))
print('FL overall sample',len(fa),fa.onsale.mean())
o=pd.read_csv('raw/W05/others_rows.csv')
o['code']=o['code'].astype(str)
nk=o[o.retailer=='nike.com'].drop_duplicates('code').copy();nk['disc']=1-nk.price/nk.orig
print('Nike.com sampled',len(nk),'share discounted',(nk.disc>0.001).mean(),'avg disc on sale',nk.disc[nk.disc>0.001].mean())
for sl,gg in o[o.retailer=='nike.com'].drop_duplicates(['slice','code']).groupby('slice'):
    d=1-gg.price/gg.orig;print(' ',sl,len(gg),'on sale',round((d>0.001).mean(),3),'avg disc',round(d[d>0.001].mean(),3))
zp=o[o.retailer=='zappos'].drop_duplicates(['slice','code','name','price','orig']).copy();zp['disc']=1-zp.price/zp.orig
zp['brand']=zp.code
print('Zappos', len(zp),(zp.disc>0.001).mean());print(zp.groupby('brand').agg(n=('name','count'),on_sale=('disc',lambda x:(x>0.001).mean()),avg=('disc',lambda x:x[x>0.001].mean())).query('n>=8').round(3).sort_values('n',ascending=False).head(14))
# match FL to Nike by style code
fa['code']=fa.sku.str[:6]
nk['c6']=nk.code.str.replace('-','').str[:6]
nkm=nk.set_index('c6')
rows=[]
allfl=pd.concat([fl[['brand','slice','sku','name','orig','price']]]).drop_duplicates('sku')
allfl['c6']=allfl.sku.str[:6]
m=allfl.merge(nk[['c6','name','price','orig']].drop_duplicates('c6'),on='c6',suffixes=('_fl','_nike'))
m['fl_disc']=1-m.price_fl/m.orig_fl;m['nk_disc']=1-m.price_nike/m.orig_nike
print('matched FL-Nike styles',len(m));print(m[['name_fl','orig_fl','price_fl','orig_nike','price_nike']].head(25).to_string())
m.to_csv('data/W05_prices.csv',index=False)
print('matched: FL cheaper',(m.price_fl<m.price_nike).sum(),'equal',(m.price_fl==m.price_nike).sum(),'dearer',(m.price_fl>m.price_nike).sum())
print('FL disc>0',(m.fl_disc>.001).sum(),'Nike disc>0',(m.nk_disc>.001).sum())
json.dump(1,open('/dev/null','w'))
