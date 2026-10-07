"""S1: pull Academy (ASO, CIK 1817358) 8-K exhibits (press releases, earnings decks, analyst-day decks) + DEF 14A from 2025-03 onward
and grep owned/private-brand sentences. 10-Q/10-K are covered by N3/X13.
Rerun: python S1_aso_edgar_2026.py  -> raw/S1_aso_2026_pl_sentences.txt (cache in raw/S1_aso_cache)"""
import requests, re, os, time, html
H={'User-Agent':'research palazzolojustin@gmail.com'}
OUT=r'C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw\S1_aso_cache'
os.makedirs(OUT,exist_ok=True)
CIK='1817358'
r=requests.get('https://data.sec.gov/submissions/CIK0001817358.json',headers=H,timeout=30).json()['filings']['recent']
accs=[(r['form'][i],r['filingDate'][i],r['accessionNumber'][i]) for i in range(len(r['form'])) if r['filingDate'][i]>='2025-03-01' and r['form'][i] in ('8-K','DEF 14A')]
pat=re.compile(r'(private[- ]label|private brand|owned brand|exclusive brand|Freely|R\.O\.W|Magellan|\bBCG\b|Mosaic|Game Winner|Brava|Outdoor Gourmet|Hi-Tec|Redfield|vertical|better.{0,10}best)',re.I)
def strip(t):
    t=re.sub(r'(?is)<(script|style).*?</\1>',' ',t); t=re.sub(r'<[^>]+>',' ',t); return re.sub(r'\s+',' ',html.unescape(t))
res=open(os.path.join(os.path.dirname(OUT),'S1_aso_2026_pl_sentences.txt'),'w',encoding='utf-8')
for form,date,acc in accs:
    a=acc.replace('-','')
    idx=requests.get(f'https://www.sec.gov/Archives/edgar/data/{CIK}/{a}/index.json',headers=H,timeout=30).json()
    for it in idx['directory']['item']:
        n=it['name']
        if not n.lower().endswith(('.htm','.html','.txt')) or re.match(r'R\d+\.htm',n) or 'index' in n or n.startswith(acc): continue
        fp=os.path.join(OUT,f'{date}_{form}_{n}'.replace(' ','_'))
        if not os.path.exists(fp):
            t=requests.get(f'https://www.sec.gov/Archives/edgar/data/{CIK}/{a}/{n}',headers=H,timeout=60).text
            open(fp,'w',encoding='utf-8').write(t); time.sleep(0.15)
        txt=strip(open(fp,encoding='utf-8').read())
        sents=re.split(r'(?<=[.!?])\s+',txt)
        hits=[s for s in sents if pat.search(s) and len(s)<1500]
        res.write(f'\n===== {date} {form} {n} ({len(hits)} hits, {len(txt)} chars)\n')
        for s in hits: res.write('- '+s.strip()+'\n')
        res.flush()
res.close()
print('done')
