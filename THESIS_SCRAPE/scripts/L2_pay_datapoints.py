"""L2: hand-coded realized pay outcomes for INCUMBENT store leaders under DKS 'Built to Win' (offers 2026-06-22),
from r/DicksSportingGoods posts/comments (raw/L2_reddit_threads.jsonl, raw/L2_reddit_posts.jsonl). Each row = one
self-reported (or clearly attributed) outcome; hearsay rows flagged. Outputs raw/L2_pay_datapoints.csv + summary,
and an ILLUSTRATIVE per-store wage-pool model (INFERENCE) -> raw/L2_btw_savings_model.csv.
Rerun: python scripts/L2_pay_datapoints.py
"""
import csv, os, statistics as st
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, 'raw')

# (date, thread_id, from_role, to_role, unit, change, before, after, hearsay, note)
# unit: 'hr' = $/hour change ; 'yr' = $/year change ; 'pct' = % change
D = [
 ('2026-06-22','1ucukuk','ASM (9 yrs)','demotion + transfer','yr',-11000,None,None,0,'quit instead'),
 ('2026-06-22','1ucukuk','ASM (hardlines mgr)','Loyalty captain','yr',-11000,None,None,0,''),
 ('2026-06-23','1ucukuk','ASM','(not stated)','yr',-20000,None,None,0,''),
 ('2026-06-24','1ucp1ds','ASM (15 yrs)','End Zone & Loyalty captain','yr',-11500,62000,50500,0,'-18.5%'),
 ('2026-06-22','1ucp1ds','ASM (West)','captain (offer)','yr',-5000,60000,55000,0,'West-coast captain offer $55K quoted by another user; pairing is INFERENCE'),
 ('2026-06-22','1ucp1ds','ASM','captain (LA)','yr',-15000,None,None,1,'"i was told it is a $15,000 cut"'),
 ('2026-06-23','1ucukuk','Apparel lead (6 yrs)','PT associate','hr',-4.00,None,None,0,''),
 ('2026-06-22','1uct2h3','PSL','FT teammate','hr',-1.50,17.00,15.50,0,'-8.8%'),
 ('2026-06-24','1ue54bc','Lead (10 yrs)','teammate','hr',-6.50,22.00,15.50,0,'-29.5%; severance offered'),
 ('2026-06-24','1ue54bc','(friend, tenured)','(demoted)','hr',-4.50,None,None,1,'~75% of it merit raises'),
 ('2026-06-24','1ue54bc','hourly (friend)','salaried "promotion"','pct',-10.0,None,None,1,'"over 10% less"'),
 ('2026-06-22','1ucclqu','KC lead (10+ yrs, OH)','captain','hr',+0.20,None,23.9,0,'"less than $24"'),
 ('2026-06-22','1ucclqu','lead (7+ yrs)','captain','hr',+0.20,None,None,0,''),
 ('2026-06-22','1ucclqu','ASM','ASM + on/off-field duties','hr',0.0,None,None,0,'no pay increase'),
 ('2026-06-22','1ucclqu','(8 yrs)','(demoted)','hr',-4.00,None,None,0,'"$4 plus pay cut"'),
 ('2026-06-22','1ucclqu','AA','(demoted)','hr',-5.00,None,None,0,'"less now than what I started at"'),
 ('2026-06-24','1ucclqu','Team-sports key carrier','captain','hr',-3.00,None,None,0,''),
 ('2026-06-24','1ucclqu','Team-sports key carrier','specialist','hr',-3.00,None,None,0,'raised sales/NSPP 30%'),
 ('2026-06-23','1ucclqu','ex-ASM/KC AA (20+ yrs)','Ops captain','hr',+1.27,None,None,0,'severance offer was $17K'),
 ('2026-06-23','1ucclqu','lead','captain (transfer)','hr',+0.50,None,None,0,''),
 ('2026-07-02','1ulws15','lead','captain','hr',+1.00,None,None,0,'"$100 extra a month"'),
 ('2026-07-03','1ulws15','lead','captain','hr',+0.25,None,None,0,''),
 ('2026-07-03','1ulws15','lead','captain','hr',+0.23,None,None,0,''),
 ('2026-07-03','1ulws15','AA (10 yrs)','teammate','hr',-3.00,None,None,0,''),
 ('2026-07-20','1v20sbr','Omni lead','FT teammate','hr',-2.00,None,None,0,'"lost over $2"'),
 ('2026-07-21','1v20sbr','PSL','Ops captain','yr',+5000,None,None,0,''),
 ('2026-07-18','1ug3jjl','25-yr associate','(demotion offer)','hr',-10.00,None,None,0,'took severance'),
 ('2026-06-23','1uct2h3','lead (runs 2 depts)','associate (offer)','hr',-5.00,25.00,20.00,0,'took severance'),
 ('2026-08-14','1vnxig5','(demoted)','(more work)','hr',-1.60,None,None,0,''),
 ('2026-08-14','1vnxig5','(lead)','(offer)','hr',-2.00,None,None,0,'took severance'),
 ('2026-08-15','1vnxig5','(lead)','(demoted)','hr',-4.00,None,None,0,''),
 ('2026-06-29','1ui0v0p','lead','specialist','hr',-0.30,None,None,0,''),
 ('2026-07-01','1ui0v0p','lead','teammate','hr',-2.00,None,None,0,'"lost $80 a week"'),
 ('2026-08-21','1vu3gj6','apparel lead','specialist','hr',0.0,22.44,22.44,0,''),
 ('2026-06-25','1uf83qc','apparel lead','apparel specialist','hr',0.0,None,None,0,''),
 ('2026-06-24','1uelhkv','team sports lead','sports & outdoors specialist','hr',0.0,None,None,0,'"twice the workload"'),
 ('2026-06-25','1uf55ph','apparel lead','apparel specialist','hr',0.0,None,None,0,'"broke even"'),
 ('2026-08-29','1ue54bc','lead (16 yrs)','teammate','hr',-6.87,22.37,15.50,1,'"they did me the same" -> assumes $15.50'),
 ('2026-09-12','1we2cfl','Omni (8 yrs)','(demoted)','hr',-4.00,None,None,0,'"almost $4"; quit'),
 ('2026-09-30','1wtqi8s','lead','captain','hr',+0.10,None,None,0,'"10 cent raise for 2x the responsibility"'),
 ('2026-06-29','1ui0v0p','lead','specialist/captain','hr',0.0,None,None,0,'"didn\'t lose any money"'),
]
cols = ['date','thread','from_role','to_role','unit','change','before','after','hearsay','note']
with open(os.path.join(RAW, 'L2_pay_datapoints.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(cols); [w.writerow(r) for r in D]

hr = [r for r in D if r[4] == 'hr' and not r[8]]
cuts = [r[5] for r in hr if r[5] < 0]; flat = [r for r in hr if r[5] == 0]; ups = [r[5] for r in hr if r[5] > 0]
cap = [r[5] for r in hr if 'captain' in r[3].lower() and 'ASM' not in r[2]]
asm = [r[5] for r in D if r[4] == 'yr' and r[2].startswith('ASM') and not r[8]]
print(f'datapoints total {len(D)} (hearsay {sum(r[8] for r in D)})')
print(f'hourly non-hearsay n={len(hr)}: cuts {len(cuts)} (median {st.median(cuts):.2f}, mean {st.mean(cuts):.2f}), flat {len(flat)}, raises {len(ups)} (median {st.median(ups):.2f})')
print(f'lead/KC -> captain hourly changes n={len(cap)}: {sorted(cap)} median {st.median(cap):.2f}')
print(f'ASM annual changes n={len(asm)}: {asm} median {st.median(asm):.0f}')
allsign = [r[5] for r in D if not r[8]]
print('share of non-hearsay outcomes that are cuts:', round(sum(1 for x in allsign if x < 0)/len(allsign), 2),
      'flat:', round(sum(1 for x in allsign if x == 0)/len(allsign), 2), 'raises:', round(sum(1 for x in allsign if x > 0)/len(allsign), 2))

# ---- ILLUSTRATIVE per-store wage-pool model (INFERENCE; inputs from the threads, ranges explicit) ----
# Restructured stores: DSG 630 + FH 52 + GGG 52 = 734 (as L3); HoS (41) and Golf Galaxy excluded; employees say BTW 'stops at 28 million stores'.
STORES = 734
scen = {
 # asm_lost_per_store, asm_sal, demoted_leads_per_store, cut_per_hr, lead_hours, captains_from_leads, captain_raise_hr, cap_hours,
 # aa_per_store_removed, aa_cost, remote_aa_per_store, extra_captain_OT_hrs_wk, benefits_load
 'bear': dict(asm_lost=0.5, asm_cut=11000, demoted=1.0, cut=2.0, lh=1800, capn=3, capr=0.6, ch=1976, aa=0.5, aac=36000, raa=0.12, ot=2.0, load=1.20),
 'base': dict(asm_lost=1.0, asm_cut=11500, demoted=2.0, cut=3.0, lh=1800, capn=4, capr=0.3, ch=1976, aa=0.8, aac=38000, raa=0.11, ot=1.5, load=1.22),
 'bull': dict(asm_lost=1.5, asm_cut=15000, demoted=3.0, cut=4.0, lh=1800, capn=4, capr=0.2, ch=1976, aa=1.0, aac=40000, raa=0.10, ot=1.0, load=1.25),
}
rows = []
for k, p in scen.items():
    asm_sav = p['asm_lost'] * p['asm_cut']                 # ASM -> captain conversions at lower pay (or seat removed)
    lead_sav = p['demoted'] * p['cut'] * p['lh']            # leads/AAs demoted to teammate at lower rate
    cap_cost = p['capn'] * p['capr'] * p['ch']               # small raises for leads promoted to captain
    aa_sav = p['aa'] * p['aac'] - p['raa'] * 40000           # store AA seats removed, net of ~1 remote AA per district (~$40K)
    ot_cost = p['capn'] * p['ot'] * 52 * 23.5 * 1.5         # captain overtime above 40h (many report 40-48h)
    per_store = (asm_sav + lead_sav - cap_cost + aa_sav - ot_cost) * p['load']
    tot = per_store * STORES / 1e6
    bp = tot / 15203 * 1e4
    rows.append([k, round(asm_sav), round(lead_sav), round(cap_cost), round(aa_sav), round(ot_cost), round(per_store), round(tot, 1), round(bp, 1), round(tot * 0.00814, 3)])
with open(os.path.join(RAW, 'L2_btw_savings_model.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['scenario','asm_sav','lead_demotion_sav','captain_raise_cost','aa_net_sav','captain_OT_cost','per_store_loaded','total_$M','bp_of_FY27E_DSG_sales','$/share'])
    [w.writerow(r) for r in rows]
for r in rows: print(r)
