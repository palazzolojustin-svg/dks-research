"""B8 v3 filter: keep DICK'S rows that look like table rows carrying sales data. Rerun after B8_extract_rows.py:
python B8_filter_rows.py -> raw/B8_rows_tables.txt"""
import csv,re,os
RAW=r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
r=list(csv.DictReader(open(os.path.join(RAW,'B8_rows_raw.tsv'),encoding='utf-8'),delimiter='\t'))
def txt(k):
    for d in ['H04_edgar_cache','B8_cache']:
        p=os.path.join(RAW,d,k)
        if os.path.exists(p): return open(p,encoding='utf-8',errors='ignore').read()
TT=re.compile(r"(Sales History|Tenant Sales|Sales and Occupancy|Sales Summary|Tenant Summary|Major Tenant|Top Tenant|Anchor Tenant|Sales PSF|Occupancy Cost)",re.I)
cache={}
out=[];seen=set()
for x in r:
    row=x['row']
    head=row[:170]
    if re.search(r"square feet;|SF;|Founded|founded|miles|Sale Price|NAP NAP|tenant at the|has been|lease|options|Total 20\d\d maturities|BBB / Baa",head): continue
    nd=len(re.findall(r"\$\s?[\d,]+(?:\.\d+)?",head))
    np_=len(re.findall(r"\d+\.\d\s?%",head))
    if nd<1: continue
    k=x['doc']
    if k not in cache: cache={k:txt(k)}
    t=cache[k]; i=t.find(row[:80])
    back=t[max(0,i-4000):i] if i>=0 else ''
    tm=list(TT.finditer(back))
    hdr=back[tm[-1].start():] if tm else ''
    j=hdr.find('$'); hdr=hdr[:j] if j>0 else hdr
    hdr=re.sub(r'\s+',' ',hdr)[:350]
    prop=x['prop_no'] or x['prop_the']
    key=(prop.lower(),re.sub(r'\W','',head[:90]))
    if key in seen: continue
    seen.add(key)
    out.append((prop,x['file_date'],x['form'],x['doc'],hdr,head))
out.sort(key=lambda z:(z[0].lower(),z[1]))
with open(os.path.join(RAW,'B8_rows_tables.txt'),'w',encoding='utf-8') as f:
    for o in out: f.write(f"## {o[0]} | {o[1]} {o[2]} {o[3][:55]}\nH: {o[4]}\nR: {o[5]}\n")
print(len(out))
