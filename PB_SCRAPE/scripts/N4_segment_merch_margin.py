"""N4: DICK'S-segment 'merchandise & services margin' (net sales less cost of merchandise & services sold, from ASU 2023-07 segment notes)
Inputs hard-coded from 10-Q/10-K segment notes (WORKING_NOTES W01 L697-698, L1054-1055; W04 L105, L286, L531-532, L809-810, L1088-1089).
Rerun: python PB_SCRAPE/scripts/N4_segment_merch_margin.py ; add new quarters to Q dict each 10-Q."""
import csv
Q={ # period: (DICK'S net sales $000, cost of merch & services $000, source)
 'Q1FY24':(3018383,1501409,'10-Q Q1FY25 seg note (PY col)'),
 'Q2FY24':(3473635,1755464,'10-Q Q2FY25 seg note (PY col)'),
 'Q3FY24':(3057181,1525800,'10-Q Q3FY25 seg note (PY col)'),
 'Q1FY25':(3174677,1567248,'10-Q Q1FY25'),
 'Q2FY25':(3646616,1836326,'10-Q Q2FY25'),
 'Q3FY25':(3236860,1613894,'10-Q Q3FY25'),
 'Q1FY26':(3377440,1677274,'10-Q Q1FY26'),
 'Q2FY26':(3849887,1885917,'10-Q Q2FY26 (incl ~$19-21M current-yr IEEPA refunds in COGS)'),
}
A={'FY22':(12368198,6267266),'FY23':(12984399,6664212),'FY24':(13442849,6813682),'FY25':(14108943,7100929)}
# derive Q4
for fy in ('FY24','FY25'):
    s=A[fy][0]-sum(Q[f'Q{i}{fy}'][0] for i in (1,2,3)); c=A[fy][1]-sum(Q[f'Q{i}{fy}'][1] for i in (1,2,3))
    Q[f'Q4{fy}']=(s,c,'derived: 10-K FY less 39w')
rows=[]
order=['Q1FY24','Q2FY24','Q3FY24','Q4FY24','Q1FY25','Q2FY25','Q3FY25','Q4FY25','Q1FY26','Q2FY26']
for p in order:
    s,c,src=Q[p]; m=1-c/s
    py=p[:2]+'FY'+str(int(p[4:])-1); 
    d=(m-(1-Q[py][1]/Q[py][0]))*1e4 if py in Q else None
    rows.append([p,s,c,round(m*100,2),None if d is None else round(d),src])
# Q2FY26 ex current-year IEEPA (~$20M)
s,c,_=Q['Q2FY26']; mx=1-(c+20000)/s; base=1-Q['Q2FY25'][1]/Q['Q2FY25'][0]
rows.append(['Q2FY26_exIEEPA20M',s,c+20000,round(mx*100,2),round((mx-base)*1e4),'INFERENCE adj +$20M COGS'])
for fy,(s,c) in A.items(): rows.append([fy,s,c,round((1-c/s)*100,2),None,'10-K seg note'])
for k in ('1H',):
    for fy in ('FY25','FY26'):
        s=Q['Q1'+fy][0]+Q['Q2'+fy][0]; c=Q['Q1'+fy][1]+Q['Q2'+fy][1]; rows.append(['1H'+fy,s,c,round((1-c/s)*100,2),None,'sum'])
out=r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw\N4_dicks_segment_merch_margin.csv"
with open(out,'w',newline='') as f:
    w=csv.writer(f); w.writerow(['period','dicks_net_sales_k','cost_merch_services_k','merch_services_margin_pct','yoy_bps','source']); w.writerows(rows)
for r in rows: print(r)
