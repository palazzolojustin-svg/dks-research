import json,time,sys
sys.path.insert(0,r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\scripts")
import X04_dmsc_suppliers as M
p=r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw\X04_dmsc_supplier_pages_2026-10-07.json"
d=json.load(open(p,encoding="utf-8"))
for u,v in d.items():
    if v.get("recent_bols"): continue
    for attempt in range(3):
        time.sleep(15)
        try:
            det=M.supplier_detail(u)
        except Exception as e:
            det={"error":str(e)}
        if det.get("recent_bols"):
            d[u]=dict(name=v["name"],desc=v.get("desc",""),**det); print(u,"ok",flush=True); break
        else:
            print(u,"empty",attempt,flush=True); time.sleep(45)
    json.dump(d,open(p,"w",encoding="utf-8"),indent=1)
