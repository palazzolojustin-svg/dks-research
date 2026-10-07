"""Parse footlocker/champs release-dates HTML (server-rendered redux state) -> list of products."""
import re, json, sys, csv
def extract_state(s):
    # find "releaseCalendar":{ ... } balanced braces
    k=s.find('"releaseCalendar":{"appliedFilters"')
    if k<0:
        k=s.find('"releaseCalendar":{')
        # skip feature flag "releaseCalendar":true
        while k>=0 and not s[k+len('"releaseCalendar":')]=='{': k=s.find('"releaseCalendar":{',k+1)
        if k<0: return None
    i=s.find('{',k)
    depth=0; instr=False; esc=False
    for j in range(i,len(s)):
        c=s[j]
        if instr:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c=='"': instr=False
        else:
            if c=='"': instr=True
            elif c=='{': depth+=1
            elif c=='}':
                depth-=1
                if depth==0:
                    txt=s[i:j+1]
                    try: return json.loads(txt)
                    except Exception as e:
                        try: return json.loads(txt.encode().decode('unicode_escape'))
                        except Exception: return None
    return None
def rows(path, site, snap):
    s=open(path,encoding='utf-8',errors='replace').read()
    st=extract_state(s)
    out=[]
    if not st: return out
    for p in st.get('products',[]) or []:
        r=p.get('reservation') or {}
        pr=(r.get('prices') or {}).get('us')
        out.append(dict(site=site,snapshot=snap,id=p.get('id'),brand=p.get('brandName'),name=p.get('name'),
            launch=p.get('skuLaunchDate'),heat=p.get('heatLevel'),inStock=p.get('inStock'),gender=p.get('gender'),
            style=p.get('style'),price=pr,status=r.get('status'),storeOnly=(r.get('flags') or {}).get('storeOnly'),
            webOnly=(r.get('flags') or {}).get('webOnly')))
    return out
if __name__=='__main__':
    site,snap,path=sys.argv[1:4]
    rs=rows(path,site,snap)
    w=csv.DictWriter(sys.stdout,fieldnames=list(rs[0].keys()) if rs else ['none'])
    w.writeheader(); [w.writerow(r) for r in rs]
