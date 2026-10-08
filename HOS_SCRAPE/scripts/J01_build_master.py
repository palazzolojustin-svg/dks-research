import csv,json
ev=list(csv.DictReader(open('/home/user/dks-research/THESIS_SCRAPE/raw/B5_hos_events.csv',encoding='utf-8-sig')))
summ={r['city']:r for r in csv.DictReader(open('/home/user/dks-research/THESIS_SCRAPE/raw/B5_event_summary.csv',encoding='utf-8-sig'))}
loc={x['storeno']:x for x in json.load(open('/home/user/dks-research/HOS_SCRAPE/raw/J01/store_pages.json'))}
repl={'1500':'prior DSG in plaza across Rt 96 (store # n/a)','1546':'Vestal NY DSG 47K sf (opened 1992; store # n/a)','1587+1586':'DSG #5415 (Gulf Fwy, closed 2023-06-30) + Field&Stream outlet converted (Katy)','1666':'DSG + Public Lands (2-into-1)','1664':'ex-Public Lands store reopened as HoS','1661':'DSG at 4601 First Ave NE (store # n/a), relocated','1634':'in-place conversion of existing DSG (Rio Lakefront)','1548':'none: 50K DSG <1 mi stays','1536':'none: net-new'}
rows=[]
def q(d): y,m=d[:4],int(d[5:7]); return f"{y}Q{(m-1)//3+1}"
for e in ev:
    st=e['store']; c=e['city'].split('(')[0]
    key=e['city']
    s=summ.get(key); 
    flag=''
    if s: flag='in_B5_summary; '+s['group']+f"; n_post_q={s['n_post_q']}"
    r=dict(status='open',store_no=st,center_or_note=e['notes'][:70],city=e['city'],state=e['state'],county=e['county'],fips=e['fips'],open_date=e['open_date'],open_q=e['open_q'],date_conf=e['date_conf'],type=e['type'],replaced_store=repl.get(st,''),qcew_event=flag or 'NO',in_locator_HoS='Y' if (st in loc and 'house of sport' in (loc[st]['title']+loc[st]['name']).lower()) or st=='1587+1586' else 'N',source=e['date_source'][:80])
    rows.append(r)
new=[('1563','Gilbert','AZ','Maricopa','04013','','NOT confirmed open: locator shows HoS page; Dec-2025 press said under construction; opening date not found','SanTan Village; planned 166 employees (126 PT/31 FT)','open?'),
('1612','Arlington (Parks Mall)','TX','Tarrant','48439','2026-06-17','H','first sale per TX permits (H07); ex-Sears 120K sf; net-new to city','open'),
('1610','Thornton (Larkridge)','CO','Adams','08001','2026-08-14','M','first HoS in Colorado; opening ~8/14-15 (9News 8/14, CBS 8/15)','open'),
('1661','Cedar Rapids (Lindale Mall)','IA','Linn','19113','2026-06-03','H','soft open 6/3, grand open 6/12-14; ex-Sears 120K sf; ~200 employees','open'),
('1634','Gaithersburg (Rio Lakefront)','MD','Montgomery','24031','2026-06-05','H','in-place conversion $10.2M (mocoshow 2026-06-04)','open'),
('1660','Schaumburg (Streets of Woodfield area, 601 N Martingale)','IL','Cook','17031','2026-07-24','H','opens July 24 (Youth Sports Business 2026-07-21)','open'),
('1617','Greensburg (Westmoreland Mall)','PA','Westmoreland','42129','2026-08-07','H','soft open ~7/30, grand open 8/7 (Hoodline/TribLIVE); ex-Sears','open'),
('1648','Annapolis Mall','MD','Anne Arundel','24003','2026-08-14','H','ex-JCPenney; acquired by Macerich/Brookfield deal; grand open 8/14 (Baltimore Sun)','open')]
for st,city,s,cty,f,d,dc,note,status in new:
    if status=='open?': dc='L'
    rows.append(dict(status=status if status=='open?' else 'open',store_no=st,center_or_note=note[:110],city=city,state=s,county=cty,fips=f,open_date=d,open_q=q(d) if d else '',date_conf=dc if len(dc)==1 else 'L',type='unknown' if st!='1634' else 'in-place conversion',replaced_store=repl.get(st,''),qcew_event='NO (after 2026Q1)' if d else 'NO (not in B5; undated)',in_locator_HoS='Y',source='J01 google-news 2026-10-08 / locator'))
pipe="""1608|Raleigh (Crabtree Valley)|NC|Wake|37183|2026-10-09|FY26Q3-4|net-new infill 6 mi from DSG; ex-Sears >100K sf; grand opening 10/9
1677|Frisco (Stonebriar)|TX|Collin|48085|2026-10-23|FY26Q3-4|relocation (DSG #421 next door); ex-Sears 142K sf; TABS $16.0M
|Cherry Hill Mall|NJ|Camden|34007||FY26Q3-4|relocation (DSG #260 1.5 mi); 'Opening in 2026'
|Novi (Twelve Oaks area)|MI|Oakland|26125||FY26Q3-4|relocation (DSG #432 0.8 mi); hiring under way
|Sioux Falls|SD|Minnehaha|46099||FY26Q3-4|relocation (DSG #1124 0.1 mi); hiring under way
|Peabody (Northshore)|MA|Essex|25009||2027|DSG Danvers #435 0.8 mi; CMBS says Feb-2027, mall says fall 2027
|King of Prussia|PA|Montgomery|42091||2027|relocation (DSG #1110)
|Tysons Corner Center|VA|Fairfax|51059||2027|incremental infill
|Springfield MO (Battlefield)|MO|Greene|29077||2027|first-in-market (nearest DSG 76 mi)
|St. Louis Galleria|MO|St. Louis Co.|29189||2027|incremental infill
|San Diego Mission Valley|CA|San Diego|06073||2027|incremental infill
|Joliet (Rock Run)|IL|Will|17197||2027|likely relocation (#1239); city $37M GO bonds
|Washington Square (Tigard)|OR|Washington|41067||2027|DSG #342 may stay (month-to-month)
|Barton Creek (Austin)|TX|Travis|48453||2027|incremental infill
|Arden Fair (Sacramento)|CA|Sacramento|06067||2027|incremental infill
|Rockaway Townsquare|NJ|Morris|34027||2027?|relocation (DSG #196)
|Sarasota UTC|FL|Sarasota|12115||2027?|relocation (#1348)
|Lubbock|TX|Lubbock|48303||2027?|first-in-market (105 mi)
|Poughkeepsie Galleria|NY|Dutchess|36027||2027?|relocation (#16)
|Hollywood (Oakwood Plaza)|FL|Broward|12011||2027?|incremental
|Broomfield (FlatIron)|CO|Broomfield|08014||2027?|relocation (#423)
|Braintree (South Shore Plaza)|MA|Norfolk|25021||2027?|incremental
|Springfield Town Center|VA|Fairfax|51059||FY27-28|relocation (#1141)
|San Jose|CA|Santa Clara|06085||FY27-28|relocation (#1409)
|Short Pump|VA|Henrico|51087||FY27-28|relocation (#128)
|Holyoke|MA|Hampden|25013||FY27-28|incremental
|Mentor|OH|Lake|39085||FY27-28|relocation (#1118)
|Fresno|CA|Fresno|06019||late2027/early2028|demolition Jul-26
|Franklin (CoolSprings)|TN|Williamson|47187||early 2028|relocation (#285)
|Los Cerritos|CA|Los Angeles|06037||2028|relocation (#1195); slipped from late 2027
|Eugene|OR|Lane|41039||spring 2028|incremental
|Lowell AR|AR|Benton|05007||Mar 2028|first-in-market (65 mi)
|Palm Beach Gardens|FL|Palm Beach|12099||spring 2028|incremental
|Boardman|OH|Mahoning|39099||2028|approval Aug-Sep 2026
|Corpus Christi (La Palmera)|TX|Nueces|48355||2028|relocation (#1113); DKS projects ~$20M -> $40M, staff 72 -> 147
|Maple Grove|MN|Hennepin|27053||2028|approval Sep 2026
|Costa Mesa|CA|Orange|06059||2028|incremental; approval Sep 2026
|Orland Park|IL|Cook|17031||2029|existing store stays
|Christiana Mall|DE|New Castle|10003||?|format unknown; Nordstrom bldg bought Jul-26"""
for l in pipe.split('\n'):
    p=l.split('|'); st,city,s,cty,f,d,t,n=p
    rows.append(dict(status='pipeline',store_no=st,center_or_note=n[:110],city=city,state=s,county=cty,fips=f,open_date=d,open_q=t,date_conf='',type='see note',replaced_store='',qcew_event='NO (not open)',in_locator_HoS='pre-open page' if st in('1608','1677') else 'N',source='THESIS_SCRAPE H02/H03/H04 notes (FIPS = J01 general knowledge)'))
w=csv.DictWriter(open('data/J01_hos_master.csv','w',newline=''),fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
import collections;print(len(rows),collections.Counter(r['status'] for r in rows))
# cross-check locator HoS not in rows
have={r['store_no'] for r in rows}|{'1586','1587'}
print([k for k,x in loc.items() if 'house of sport' in (x['title']+x['name']).lower() and k not in have])
