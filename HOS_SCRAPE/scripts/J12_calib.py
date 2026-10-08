import csv
rows=[
# id,store,type,sales_lo,sales_hi,sales_basis,jobs_lo,jobs_hi,jobs_basis,grade
("1","Minnetonka MN HoS (Ridgedale) 115,262sf, opened May-2022","HoS gross",31.197,31.197,"TTM CY2024 reported (CMBS 424H 2025-08-05)",200,200,"PR 2022-03-15 'more than 200 positions' (gross postings)","A/B"),
("1b","Minnetonka MN","HoS gross vs QCEW",31.197,31.197,"same",151,151,"B5 QCEW y1 net county jobs","B"),
("2","Johnson City NY HoS 140K sf, Aug-2023","HoS net increment",8.6,8.6,"H07 NY tax excess vs control, yr1",124,124,"B5 QCEW y1 net","B"),
("2b","Johnson City NY","HoS gross model",35,35,"DKS $35M model (not observed)",200,200,"WNBF 2023-05-30 'about 200 expected hired'","B"),
("3","Novi MI HoS (plan)","HoS gross model",35,35,"DKS model",166,166,"DKS letter to city 2025-04-14 hires","B"),
("3b","Novi MI FTE","HoS gross model",35,35,"DKS model",107,107,"32 FT+12 sal+126PT*0.5","C"),
("4","Tampa Intl Plaza HoS, Oct-2024","HoS gross annualised",40,44,"CMBS 12.3M/first 3 mo /0.28-0.31 (H04 inference)",123,123,"B5 QCEW y1 net","B"),
("5","Live Oak TX HoS net-new, Oct-2025","HoS net-new",25,30,"H07 tax-based yr1 annualised",238,277,"B5 QCEW y1/k-1 Bexar","B"),
("6","Victor NY HoS 2021","HoS net increment",19,28,"H07 Ontario excess",128,128,"B5 QCEW y1","B"),
("7","Scheels Chandler AZ 220K sf, Sep-2023","analog gross",150,150,"Macerich 'over $150M' (Q4-25 call)",400,500,"Macerich PR/news 400+ ; 500+ hired","B"),
("8","Scheels Tulsa (proj)","analog proj",100,100,"Scheels projection to city",400,400,"'more than 400 jobs'","C"),
("9","Scheels Littleton CO (proj)","analog proj",135,135,"city memo via Hoodline",550,550,"550+","C"),
("10","Empire Mall legacy DSG 50.3K sf","legacy gross",12.2,12.2,"CMBS FY24",50,66,"Grand Junction new DSG 50-60 jobs; 1.31/1000sf","C"),
]
out=[]
print("id | store | sales$M | jobs | $K/job (sales_lo/jobs_hi .. sales_hi/jobs_lo)")
for r in rows:
    lo=r[3]*1000/r[7]; hi=r[4]*1000/r[6]
    print(r[0],'|',r[1][:42],'|',r[3],r[4],'|',r[6],r[7],'|',round(lo),'-',round(hi))
    out.append(list(r)+[round(lo),round(hi)])
w=csv.writer(open('data/J12_calibration.csv','w'));w.writerow("id store type sales_lo_M sales_hi_M sales_basis jobs_lo jobs_hi jobs_basis grade k_per_job_lo k_per_job_hi".split());w.writerows(out)
# gross build: jobs 166-200 x 156-211K minus legacy
for j in (166,200):
  for p in (156,211): print('gross',j,p,round(j*p/1000,1))
