"""B6: grep DKS Workday job descriptions (live 2026-10-07 census from H06, archived 2025 CXS JSON from L3)
for named store-labor / store-tech vendors and tools.
Rerun: python B6_jobs_vendor_grep.py  -> raw/B6_jobs_vendor_hits.csv and prints counts + context snippets.
"""
import json, re, csv, collections, os
BASE = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE"
TERMS = [
 'UKG','Kronos','Legion','Reflexis','Zebra','WorkJam','Quinyx','Blue Yonder','JDA','Workday Scheduling','Workforce Management','WFM',
 'Logile','Axonify','Beekeeper','RFID','Avery','Checkpoint','Nedap','SML','electronic shelf','ESL','self-checkout','self checkout',
 'Simbe','Zippedi','handheld','hand-held','mobile POS','mPOS','TC5','TC2','MC9','Honeywell','scheduling','labor model','labor forecast',
 'forecasting','task management','Manhattan','Oracle','SAP','Salesforce','Tulip','NewStore','Mobile device','iPhone','Android','Teams','Slack',
 'Workplace','Microsoft','Google','Gemini','OpenAI','ChatGPT','AI','machine learning','computer vision','store operations technology',
 'store systems','point of sale','POS','Aptos','NCR','Toshiba','Verifone','Adyen','Stripe','Instacart','DoorDash','ship-from-store','BOPIS',
 'curbside','Coach','labor budget','payroll budget','hours','Infor','Shiftboard','HotSchedules','Fourth','7shifts','Deputy','Ceridian','Dayforce','ADP',
 'Medallia','Qualtrics','YOOBIC','Zipline','Theatro','Relex','o9','Kinaxis','Snowflake','Databricks','Vertex AI','Azure','AWS','GCP','BigQuery','Looker','Tableau',
 'Power BI','Anaplan','Inmar','Cin7','Square','SOTI','MobileIron','Intune','Jamf','Ivanti','Samsung','Apple']

def load():
    rows=[]
    p1=os.path.join(BASE,'raw','H06_workday_details_2026-10-07.jsonl')
    for l in open(p1,encoding='utf-8'):
        d=json.loads(l); rows.append(('2026-10-07',d.get('location_type'),d.get('title'),d.get('location'),d.get('startDate'),d.get('desc') or ''))
    p2=os.path.join(BASE,'raw','L3_archived_cxs.jsonl')
    if os.path.exists(p2):
        for l in open(p2,encoding='utf-8'):
            try: d=json.loads(l)
            except: continue
            ji=d.get('jobPostingInfo',d)
            desc=ji.get('jobDescription') or ji.get('desc') or ''
            desc=re.sub('<[^>]+>',' ',desc)
            rows.append(('2025-arch',ji.get('location_type',''),ji.get('title'),ji.get('location'),ji.get('startDate'),desc))
    return rows

if __name__=='__main__':
    rows=load(); print('rows',len(rows))
    cnt=collections.Counter(); hits=[]
    for src,lt,t,loc,sd,desc in rows:
        for term in TERMS:
            pat=r'\b'+re.escape(term)+r'\b'
            flags=0 if term in ('AI','SML','ESL','POS','SAP','WFM','JDA','Teams','Square','Apple','Coach','Fourth','Gemini') else re.I
            for m in re.finditer(pat,desc,flags):
                cnt[(src,term)]+=1
                hits.append((src,term,t,loc,sd,desc[max(0,m.start()-200):m.end()+200].replace('\n',' ')))
                break
    for k,v in sorted(cnt.items(),key=lambda x:-x[1]): print(k,v)
    with open(os.path.join(BASE,'raw','B6_jobs_vendor_hits.csv'),'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['src','term','title','location','startDate','context']); w.writerows(hits)
