"""X04: owned-brand vs national-brand split of DKS direct imports (consignee Dick's Merchandising & Supply Chain).
Union of supplier panels from the live ImportYeti page (raw/X04_iy_company_dick-s-merchandising-and-supply-cha.txt, from X04_importyeti.py)
and the 2025-09-06 Wayback snapshot (raw/X04_wayback_dmsc_20250906_rsc.txt). Suppliers classified by BOL product text
(NAT = national-brand FOB e.g. Sole/Dyaco, GCI/Goleader, Kijaro/Denovo, Lifetime, Bowflex, Bestway; AMB = ambiguous; APP = owned apparel; OWN = other owned).
Output: raw/X04_dmsc_owned_vs_national_quarterly.csv (calendar quarters). Rerun after refreshing the live page; extend the class sets when new suppliers appear.
"""
import re,json,csv
from collections import defaultdict
def vt(p):
    big=open(p,encoding="utf-8").read()
    out={}
    for m in re.finditer(r'\{"shipments_12m":(\d+),"vendor_name":"([^"]*)".*?"url":"/supplier/([^"]*)".*?"product_descriptions":"([^"]*)","vendor_time_series":(\{.*?\}\}),',big):
        out[m.group(3)]=dict(name=m.group(2),desc=m.group(4),ts=json.loads(m.group(5)))
    return out
old=vt(r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw\X04_wayback_dmsc_20250906_rsc.txt")
new=vt(r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw\X04_iy_company_dick-s-merchandising-and-supply-cha.txt")
print(len(old),len(new),len(set(old)|set(new)))
NAT={"goleader-industries-zhejiang","goleader-viet-nam-recreation","goleader-vietnam-recreation-limit","dyaco-international","zhejiang-arcana-power-sports-tech","lifetime-hong-kong","johnson-health-tech","intex-development","sportspower","bestway-hong-kong-international-l-imited","fugang-technology","denovo-hk"}
AMB={"tangshan-laiyuan-household-goods","djm-footwear","pinghu-huayang-outdoor-goods-lt","lanxi-trueyach-industrial","huizhou-double-star-sports-goods","shinehome-industrial","hydrodynamic-industrial","dong-guan-her-cheng-sporting-goods","dongguan-dongcheng-shen-rui-hand"}
APP={"century-distribution-systems","century-distribution-systems-ind","century-miracle-apparel-manufacturi","uni-gears","makalot-garments-cambodia","makalot-garments-vietnam","ha-bac-export-garment-joint-stock-c","habac-export-garment-joint-stock-c","celebrity-fashion-vina","glory-industrial-semarang","hansae-tn","leader-garment-vietnam","top-form-brassiere-maesot","haianhtex-joint-stock","great-global-international","nan-yang-garment","new-wide-apparel","eins-vina","twhq-garments","twhq-garments-national-ro","thuyen-nguyen-trade-import-export","xiamen-kingland","king-success","moha-garments","horizon-outdoor-cambodia","apl-logistics","phi-logistics","decor-su-zhou","southern-textile-network-s-a"}
def qkey(k): return f"{k[6:]}-{k[3:5]}"
agg=defaultdict(lambda:defaultdict(lambda:[0,0]))
for slug in set(old)|set(new):
    g="NAT" if slug in NAT else "AMB" if slug in AMB else ("APP" if slug in APP else "OWN")
    qs=set()
    tso={qkey(k):v for k,v in old.get(slug,{}).get("ts",{}).items()}
    tsn={qkey(k):v for k,v in new.get(slug,{}).get("ts",{}).items()}
    for q in set(tso)|set(tsn):
        v = tsn.get(q) if (q>="2025-07" or q not in tso) else (tsn.get(q) if (tsn.get(q,{"weight":0})["weight"]>=tso[q]["weight"]) else tso[q])
        if v is None: v=tso[q]
        agg[g][q][0]+=v["shipments"]; agg[g][q][1]+=v["weight"]
ent=defaultdict(lambda:[0,0])
for r in csv.DictReader(open(r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw\X04_dmsc_monthly_2026-10-07.csv")):
    y,m=r["month"].split("-"); q=f"{y}-{(int(m)-1)//3*3+1:02d}"
    ent[q][0]+=int(r["shipments"]); ent[q][1]+=int(r["weight_kg"])
rows=[]
for q in sorted(ent):
    if q<"2023-01" or q>"2026-07": continue
    p_=agg["APP"][q]; o=[agg["OWN"][q][0]+p_[0],agg["OWN"][q][1]+p_[1]]; n,a=agg["NAT"][q],agg["AMB"][q]; cov=o[1]+n[1]+a[1]
    rows.append([q,ent[q][0],ent[q][1],o[0],o[1],n[0],n[1],a[0],a[1],round(cov/ent[q][1],3),round(o[1]/(o[1]+n[1]) if o[1]+n[1] else 0,3),round(o[0]/(o[0]+n[0]) if o[0]+n[0] else 0,3),p_[0],p_[1]])
    print(rows[-1])
with open(r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw\X04_dmsc_owned_vs_national_quarterly.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["cal_quarter_start","entity_ship","entity_kg","owned_ship","owned_kg","national_ship","national_kg","ambig_ship","ambig_kg","coverage_kg","owned_share_kg_of_classified","owned_share_ship_of_classified","owned_apparel_ship","owned_apparel_kg"]); w.writerows(rows)

